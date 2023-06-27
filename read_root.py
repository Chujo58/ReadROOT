import numpy
import sys
import matplotlib.pyplot as _plt
import uproot as _ur
import pandas
import tkinter.filedialog as _fd
from scipy.optimize import curve_fit
import pint

import os as _os

# import cppimport
# try:
#     lib = cppimport.imp("wrap")
# except:
#     lib = cppimport.imp_from_filepath("wrap.cpp")


def define_cut(start: int, stop: int, data_set: pandas.DataFrame) -> numpy.array:
    """Finds the indexes that are within a given cut

    Parameters
    ----------
    start : U16
        Start of the cut (minimum value)
    stop : U16
        Stop of the cut (maximum value)
    data_set : pandas.DataFrame
        Data set on which we perform a cut.

    Returns
    -------
    output : numpy.array
        Array containing the indexes that match the cut.
    """
    return numpy.where((start <= data_set) & (data_set <= stop))[0]


def get_unfiltered(data: pandas.DataFrame) -> pandas.DataFrame:
    """Removes the pileup and saturation events from the selected dataset

    Parameters
    ----------
    data : pandas.DataFrame
        Dataset from which we remove the pileup and saturation events

    Returns
    -------
    unfiltered_data : pandas.DataFrame
        Unfiltered dataset
    """
    indexes = numpy.where(data["Flags"] == 16384)[0]
    temp_dict = {}
    for key in data.keys():
        temp_dict[key] = data[key][indexes]

    return pandas.DataFrame(temp_dict)    


def generate_csv_name(file_path, start: int, stop: int, window: pint.Quantity, cutsOn: bool = None, cuts: tuple = None) -> str:
    """Generates the csv file path where the C++ TOF will save its data.

    Parameters
    ----------
    start : int
        Start channel number
    stop : int
        Stop channel number
    window : pint.Quantity
        Time window for the TOF

    Returns
    -------
    file_path : str
        File path for the csv
    """
    list_output = file_path.split("/")
    if len(list_output) == 1:
        list_output = file_path.split("\\")

    list_output[0] = f"{list_output[0]}\\"
    where_to_save = _os.path.join(*list_output[0:-3])
    run_folder = list_output[-3]
    tree_folder = list_output[-2]
    
    cuts_string = ""
    if cutsOn:
        cuts_string = f"_{cuts}"


    csv_name = f"{run_folder}_{tree_folder}_CH{start}-CH{stop}_{window:.2e~P}" + cuts_string + ".csv"

    directory = _os.path.join(where_to_save, run_folder, "TOF Data")
    if not _os.path.exists(directory):
        _os.mkdir(directory)

    return _os.path.join(directory, csv_name)

def get_cpp_tof_hist(file_path: str, min_: int, max_: int, default_bins=8192):
    df = pandas.read_csv(file_path, compression="bz2")
    delta_time = (numpy.array(df["Stop Time"]) - numpy.array(df["Start Time"]))*1e-3

    hist = numpy.histogram(delta_time, default_bins, range=(min_, max_))
    y, x = hist
    return (x, y, delta_time)

def get_cpp_evse_hist(file_path: str, xbins: int, ybins: int) -> tuple[numpy.array, numpy.array, numpy.ndarray]:
    """Generates the Energy vs Energy 2D histogram

    Parameters
    ----------
    file_path : str
        Path to the csv file containing the time and energy information
    xbins : int
        Number of bins on the x-axis
    ybins : int
        Number of bins on the y-axis

    Returns
    -------
    output: tuple[numpy.array, numpy.array, numpy.ndarray]
        Tuple containing the x bins, y bins and the density (z axis counts) calculated the histogram.
    """
    df = pandas.read_csv(file_path, compression="bz2")

    density, xedge, yedge = numpy.histogram2d(df["Start Energy"], df["Stop Energy"], (xbins, ybins))
    return (xedge, yedge, density, (df["Start Energy"], df["Stop Energy"]))

def get_cpp_tofvse_hist(file_path: str, min_: int, max_: int, default_energy_bins=4096, default_tof_bins=8192) -> tuple[numpy.array, numpy.array, numpy.ndarray]:
    """Generates the TOF vs Energy 2D histogram

    Parameters
    ----------
    file_path : str
        Path to the csv file containing the time and energy information
    min_ : int
        Minimum time for the TOF bins
    max_ : int
        Maximum time for the TOF bins
    default_energy_bins : int, optional
        Number of bins to use for the X axis, by default 4096
    default_tof_bins : int, optional
        Number of bins to use for the Y axis, by default 8192

    Returns
    -------
    output: tuple[numpy.array, numpy.array, numpy.ndarray]
        Tuple containing the x bins, y bins and the density (z axis counts) calculated the histogram.
    """
    df = pandas.read_csv(file_path, compression="bz2")
    min_e = min(df["Stop Energy"])
    max_e = max(df["Stop Energy"])
    
    tof_data = get_cpp_tof_hist(file_path, min_, max_, default_tof_bins)[2] #Grab only the time differences
    density, xedge, yedge = numpy.histogram2d(df["Stop Energy"], tof_data, [default_energy_bins, default_tof_bins], ((min_e,max_e),(min_,max_)))
    return (xedge, yedge, density, (df["Stop Energy"], tof_data))


class _root_reader():
    """
    A file reader capable of getting information from a `.root` file format and returning the information in a more understandable format.

    Parameters
    ----------
    `Default_directory`: String containing the path of a `.root` file.

    `Warning`: Boolean that lets the code tell you wheter the `.root` file was properly read.
    """
    def __init__(self, Default_directory = '/', Warning=False, askfile=False):
        if askfile:
            self.def_dir = Default_directory
            self.file_path = _fd.askopenfilename(initialdir=self.def_dir, title='Select a file', filetypes=(('ROOT file', '*.root'), ('All files', '*.*')))
            """
            String containing the path of the chosen file.
            """
            self.file_name = self.file_path.split('/')[-1].split('.')[0]
            """
            String containing the name of the chosen file.
            """
        self.warnings = Warning
        """
        Wheter you want to get a warning saying that the file was properly read.
        """

    @staticmethod
    def median(data_set):
        return numpy.median(data_set)

    @staticmethod
    def average(data_set):
        """
        Returns the average of a data set.
        """
        return numpy.average(data_set)

    @staticmethod
    def standard_deviation(data_set):
        """
        Returns the standard deviation of a data set.
        """
        return numpy.std(data_set)

    @staticmethod
    def PSD(energylong, energyshort):
        """
        Tries to calculate the PSD value for given E_long and E_short. If E_long is zero, the PSD value will be set to 0.
        """
        try:
            value = (energylong-energyshort)/energylong
        except:
            value = 0
        return value


    def calc_psd(self, data):
        psd_func = numpy.vectorize(self.PSD)
        PSD_values = psd_func(data['Energy'], data['EnergyShort'])
        data.insert(2, 'PSD', PSD_values)
        

    @staticmethod
    def get_unfiltered(data_raw):
        indexes = numpy.where(data_raw['Flags'] == 16384)[0]
        temp_dict = {}
        for key in data_raw.keys():
            temp_dict[key] = data_raw[key][indexes]
        return pandas.DataFrame(temp_dict)

    @staticmethod
    def data_in_range(data_unfiltered, start, stop):
        return numpy.where((start <= data_unfiltered) & (data_unfiltered <= stop))

    def __getdata__(self, filepath:str, tree='Data_F', raw=False):
        """
        Reads the data from the file selected and returns it into a readable format.

        Parameters
        ----------
        `filepath`: String containing the path of a `.root` file.

        Returns
        ------
        `pandas.DataFrame` containing the data of the `.root` file.
        """
        root_file = _ur.open(filepath)
        tree = root_file[tree]
        keys = ['Channel', 'Timestamp', 'Board', 'Energy', 'EnergyShort', 'Flags']
        filtered_data = tree.arrays(keys, library='np')
        
        filtered_DF = pandas.DataFrame(filtered_data)
        if not raw:
            timestamps = filtered_DF['Timestamp']
            formatted_timestamps = pandas.to_numeric(timestamps, downcast='integer')
            filtered_DF = filtered_DF.drop('Timestamp', axis=1)
            filtered_DF.insert(1, 'Timestamp', formatted_timestamps)
        
        self.calc_psd(filtered_DF)
        
        return filtered_DF

    def __energyhist__(self, filepath, default_bins=4096, tree='Data_F'):
        """
        Computes the counts for the different energy bins.

        Parameters
        ----------
        `filepath`: String containing the path of a `.root` file.

        `default_bins`: The number of energy bins used by the CoMPASS software for the acquisition. By default `4096`.

        Returns
        ------
        `tuple` containing the bins and the counts for the histogram.
        """
        data = self.__getdata__(filepath, tree)
        hist = numpy.histogram(data['Energy'], bins=default_bins, range=(0,default_bins))
        x = hist[1]#[1:]
        y = hist[0]
        return (x, y, data['Energy'])

    def __psdhist__(self, filepath, default_bins=4096, tree='Data_F'):
        data = self.__getdata__(filepath, tree)
        hist = numpy.histogram(data['PSD'], bins=default_bins, range=(0,1))
        x = hist[1]#[1:]
        y = hist[0]
        return (x, y, data['PSD'])
        
    def __timehist__(self, filepath, min_bin, max_bin, default_bins=4096, tree='Data_F'):
        data = self.__getdata__(filepath, tree)
        time_difference = numpy.ediff1d(data['Timestamp']/1000)

        hist = numpy.histogram(time_difference, bins=default_bins, range=(min_bin, max_bin))
        x = hist[1]#[1:]
        y = hist[0]
        return (x, y, time_difference)

    def __tofhist__(self, file1, file2, min_bin, max_bin, default_bins=8192, default_bin_size = 0.045, tree='Data_F'):
        """
        Computes the counts for the different time difference bins.

        Parameters
        ----------
        `file1`: File path of the start channel

        `file2`: File path of the second channel

        `min_bin`: Integer of the smallest value counted for the bins.

        `max_bin`: Integer of the biggest value counted for the bins. This value might be changed in order to fit the smallest bin size of 45 ps.

        `default_bin`: Integer containing the default amount of bins used. Must match the value used with the CoMPASS software at Start/Stop ΔT channels.

        `default_bin_size`: Smallest bin size used by the CoMPASS software for the ΔT histogram. DO NOT CHANGE THIS VALUE!

        `tree`: Type of root file opened. Can either be `DATA_F`, `DATA_R` or `DATA`

        Output
        ------
        `tuple` containing the bins and counts for the histogram.
        """

        #Data from the first file path.
        ch0_data = self.__getdata__(file1, tree)
        #Data from the second file path
        ch1_data = self.__getdata__(file2, tree)

        #Calculation of the ΔT
        delta_time = (numpy.array(ch1_data["Timestamp"]) - numpy.array(ch0_data["Timestamp"]))*1e-3
        # for index in range(0, len(ch0_data)):
        #     delta_time.append((ch1_data['Timestamp'][index] - ch0_data['Timestamp'][index])/10**3) #Timestamp are in ps so we transform the result to ns.

        #Modification of the upper value for the histogram bins.
        bin_range = max_bin - min_bin
        bin_size = round(bin_range/default_bins, 3)
        if bin_size < default_bin_size:
            max_bin = min_bin + default_bins * default_bin_size
            bin_size = default_bin_size
            bin_range = max_bin - min_bin

        
        hist = numpy.histogram(delta_time, default_bins, range=(min_bin, max_bin))
        x = hist[1]#[1:]
        y = hist[0]
        # print(x.shape, y.shape)
        return (x, y, delta_time)

    def __CPPTOF__(self, file1, file2, low_cut_0, high_cut_0, low_cut_1, high_cut_1, window, min_bin, max_bin, default_bins=8192, default_bin_size=0.045, tree="Data_R"):
        ch0_data = self.__getdata__(file1, tree, True)
        ch1_data = self.__getdata__(file2, tree, True)

        ch0_unfiltered = self.get_unfiltered(ch0_data)
        ch1_unfiltered = self.get_unfiltered(ch1_data)

        range_0 = list(self.data_in_range(ch0_unfiltered['Energy'], low_cut_0, high_cut_0)[0])
        range_1 = list(self.data_in_range(ch1_unfiltered['Energy'], low_cut_1, high_cut_1)[0])

        first_line = numpy.array(ch0_unfiltered['Timestamp'].iloc[range_0]).astype(numpy.int64)
        second_line = numpy.array(ch1_unfiltered['Timestamp'].iloc[range_1]).astype(numpy.int64)

        start, stop = lib.TOF(first_line, second_line, window)

        bin_range = max_bin - min_bin
        bin_size = round(bin_range/default_bins, 3)
        if bin_size < default_bin_size:
            max_bin = min_bin + default_bins * default_bin_size
            bin_size = default_bin_size
            bin_range = max_bin - min_bin

        diffs = (stop-start)*10**(-3)
        hist = numpy.histogram(diffs, bins=default_bins, range=(min_bin, max_bin))
        x = hist[1]
        y = hist[0]
        return (x, y, diffs)        


    def __PSDvsE__(self, filepath, min_e, max_e, default_energy_bins=4096, default_psd_bins=4096, tree='Data_F'):
        data = self.__getdata__(filepath, tree)
        hist = numpy.histogram2d(data['Energy'], data['PSD'], [default_energy_bins, default_psd_bins], range=((min_e,max_e),(0,1)))
        return hist[0]
        


    def __MCSgraph__(self, filepath, tree='Data_F'):
        """
        Computes the counts for the different rate bins.
        
        Output
        ------
        `tuple` containing the bins and counts for the histogram.
        """
        data = self.__getdata__(filepath, tree)
        t0 = 0 #seconds
        t1 = int(data['Timestamp'][len(data)-1]/10**12) #seconds
        n_bins = t1-t0
        hist = numpy.histogram(data['Timestamp']/10**12, bins=n_bins, range=(t0,t1))
        x = hist[1][1:]
        y = hist[0]
        return (x, y, data['Timestamp']/10**12)

    def __getfilepath__(self):
        return _fd.askopenfilename(initialdir='/', title='Select a file', filetypes=(('ROOT file', '*.root'), ('All files', '*.*')))

    def __transform_root_to_excel__(self, filepath, tree='Data_F'):
        """
        Transforms the root file to an excel file.

        Parameters
        ----------
        `filepath`: String containing the file path.

        `tree`: Optional value that can be changed depending on the root file used.
        """
        data = self.__getdata__(filepath, tree)
        data.rename(columns={'Channel': 'Channel', 'Timestamp': 'Timestamp [ps]', 'Board':'Board', 'Energy':'Energy', 'Flags':'Flags'}, inplace=True)

        timestamps_in_seconds = []
        for value in data['Timestamp [ps]']:
            timestamps_in_seconds.append(value/10**12)

        data.insert(5, 'Timestamp [s]', timestamps_in_seconds)
        data.to_csv(filepath.split('.')[0]+'.csv', index=False)

class root_reader_v2():
    """
    A file reader capable of getting information from a `.root` file.

    Parameters
    ----------
    file_path : str
        Path of the file we want to read
    tree : str
        Key for the TTree inside the root file
    """
    def __init__(self, file_path: str, tree: str):
        self.file_path = file_path
        self.tree = tree

    @staticmethod
    def PSD(energy_long: int, energy_short: int) -> float:
        """Calculates the PSD value for given energies.

        Parameters
        ----------
        energy_long : int
            Long gate energy
        energy_short : int
            Short gate energy

        Returns
        -------
        psd : float
            PSD value
        """
        try:
            value = (energy_long-energy_short)/energy_long
        except:
            value = 0

        return value

    def calculate_PSD(self, data: pandas.DataFrame):
        """Calculates the PSD values for a dataset.

        Parameters
        ----------
        data : pandas.DataFrame
            Dataset used to calculate the PSD values
        """
        psd_func = numpy.vectorize(self.PSD)
        psd_values = psd_func(data["Energy"], data["EnergyShort"])
        data.insert(2, "PSD", psd_values)



    def open(self, raw=False, check_flags=False) -> pandas.DataFrame:
        """Opens the selected file

        .. note::
        Can return `None` if the file doesn't contain any data.

        Parameters
        ----------
        raw : bool, optional
            Whether we downcast the timestamps to integers or keep them as unsigned integers, by default False
        check_flags : bool, optional
            Whether we print out the different flags found in the selected file, by default False

        Returns
        -------
        filtered_data : pandas.DataFrame
            Downcasted timestamp data with all the rest of the file's data.
        """
        try:
            root = _ur.open(self.file_path)
        except:
            return

        tree = root[self.tree]
        keys = ["Channel", "Timestamp", "Board", "Energy", "EnergyShort", "Flags"]
        data = tree.arrays(keys, library="np")

        if len(data["Channel"]) == 0:
            return

        filtered_dataframe = pandas.DataFrame(data)

        if not raw:
            timestamps = data["Timestamp"]
            formatted_timestamps = pandas.to_numeric(timestamps, downcast="integer")
            filtered_dataframe = filtered_dataframe.drop("Timestamp", axis=1)
            filtered_dataframe.insert(1, "Timestamp", formatted_timestamps)

        self.calculate_PSD(filtered_dataframe)

        if check_flags:
            flags = set(filtered_dataframe["Flags"])
            for flag in flags:
                print(list(filtered_dataframe["Flags"]).count(flag), flag)
            #  print(list(filtered_dataframe["Flags"]).count(16512))

        root.close()

        return filtered_dataframe

    def len(self) -> int:
        data = self.open()
        return len(data)

    def get_energy_hist(self, default_bins=4096, **kwargs) -> tuple[numpy.array, numpy.array, pandas.Series]:
        """Generates the energy histogram's data

        Parameters
        ----------
        default_bins : int, optional
            Number of bins used by the histogram, by default 4096

        Returns
        -------
        output_tuple : tuple[numpy.array, numpy.array, pandas.Series]
            Tuple containing the x data, y data and raw data used to create the histogram.
        """
        default_bins = default_bins if kwargs.get("bins") is None else kwargs.get("bins")
        data = self.open()
        hist = numpy.histogram(data["Energy"], bins=default_bins)
        y, x = hist
        return (x, y, data["Energy"])

    def get_psd_hist(self, default_bins=4096, **kwargs) -> tuple[numpy.array, numpy.array, pandas.Series]:
        """Generates the PSD histogram's data

        Parameters
        ----------
        default_bins : int, optional
            Number of bins used by the histogram, by default 4096

        Returns
        -------
        output_tuple : tuple[numpy.array, numpy.array, pandas.Series]
            Tuple containing the x data, y data and raw data used to create the histogram.
        """
        default_bins = default_bins if kwargs.get("bins") is None else kwargs.get("bins")
        data = self.open()
        hist = numpy.histogram(data["PSD"], bins=default_bins, range=(0,1))
        y, x = hist
        return (x, y, data["PSD"])

    def get_time_hist(self, min_: int, max_: int, default_bins=4096, **kwargs) -> tuple[numpy.array, numpy.array, numpy.array]:
        """Generates the time histogram's data

        Parameters
        ----------
        min_ : int
            Minimum time for the histogram's range
        max_ : int
            Maximum time for the histogram's range
        default_bins : int, optional
            Number of bins used by the histogram, by default 4096

        Returns
        -------
        output_tuple : tuple[numpy.array, numpy.array, numpy.array]
            Tuple containing the x data, the y data and the raw data used to create the histogram.
        """
        default_bins = default_bins if kwargs.get("bins") is None else kwargs.get("bins")
        data = self.open()
        time_difference = numpy.ediff1d(data["Timestamp"]/1000)
        hist = numpy.histogram(time_difference, bins=default_bins, range=(min_,max_))
        y, x = hist
        return (x, y, time_difference)

    def get_tof_hist(self, stop_file: str, min_: int, max_: int, default_bins=8192) -> tuple[numpy.array, numpy.array, numpy.array]:
        """Generates the TOF histogram's data from a file with the TTree key `Data_F`

        .. note::
            Requires two files to be used.

        Parameters
        ----------
        stop_file : str
            Path to the stop channel's root file
        min_ : int
            Minimum time for the histogram's range
        max_ : int
            Maximum time for the histogram's range
        default_bins : int, optional
            Number of bins used by the histogram, by default 8192

        Returns
        -------
        output_tuple : tuple[numpy.array, numpy.array, numpy.array]
            Tuple containing the x data, the y data and the raw data used to create the histogram.
        """
        data_start = self.open()
        data_stop = root_reader_v2(stop_file, self.tree).open()
        # print(len(data_stop))
        
        try:
            delta_time = (numpy.array(data_stop["Timestamp"]) - numpy.array(data_start["Timestamp"]))*1e-3
        except:
            return

        hist = numpy.histogram(delta_time, default_bins, range=(min_, max_))
        y, x = hist
        return (x, y, delta_time)

    def get_evse_hist(self, stop_file: str, xbins: int, ybins: int) -> tuple[numpy.array, numpy.array, numpy.ndarray]:
        """Generates the Energy vs Energy 2D histogram's data from a file with the TTree key `Data_F`

        .. note::
            Requires two files to be used.

        Parameters
        ----------
        stop_file : str
            Path to the stop channel's root file
        xbins : int
            Number of bins used by the histogram for the x axis
        ybins : int
            Number of bins used by the histogram for the y axis

        Returns
        -------
        output_tuple: tuple[numpy.array, numpy.array, numpy.ndarray]
            Tuple containing the x bins, y bins and the density (z axis counts) calculated the the histogram.
        """
        data_start = self.open()
        data_stop = root_reader_v2(stop_file, self.tree).open()
        
        try:
            density, xedge, yedge = numpy.histogram2d(data_start["Energy"], data_stop["Energy"], (xbins, ybins))
        except:
            return

        return (xedge, yedge, density, (data_start["Energy"], data_stop["Energy"]))

    def get_tofvse_hist(self, stop_file: str, min_: int, max_: int, default_energy_bins=4096, default_tof_bins=8192) -> tuple[numpy.array, numpy.array, numpy.array]:
        """Generates the TOF vs Energy 2D histogram's data from a file with the TTree key `Data_F`

        .. note::
            Requires two files to be used.

        Parameters
        ----------
        stop_file : str
            Path to the stop channel's root file
        min_ : int
            Minimum time for the histogram's range
        max_ : int
            Maximum time for the histogram's range
        default_energy_bins : int, optional
            Number of bins used by the histogram for the energy axis, by default 4096
        default_tof_bins : int, optional
            Number of bins used by the histogram for the TOF axis, by default 8192

        Returns
        -------
        output_tuple : tuple[numpy.array, numpy.array, numpy.array]
            Tuple containing the x bins, y bins and the density (z axis counts) calculated by the histogram.
        """
        tof_data = self.get_tof_hist(stop_file,min_,max_, default_tof_bins)[2]
        stop_data = root_reader_v2(stop_file, self.tree).open()
        min_e = min(stop_data["Energy"])
        max_e = max(stop_data["Energy"])
        try:
            density, xedge, yedge = numpy.histogram2d(stop_data["Energy"], tof_data, [default_energy_bins, default_tof_bins], ((min_e,max_e),(min_,max_)))
        except:
            return
        return (xedge, yedge, density, (stop_data["Energy"], tof_data))

    def get_psdvse_hist(self, default_energy_bins=4096, default_psd_bins=4096) -> tuple[numpy.array, numpy.array, numpy.array]:
        """Generates the PSD vs Energy 2D histogram's data

        Parameters
        ----------
        default_energy_bins : int, optional
            Number of bins used by the histogram for the energy axis, by default 4096
        default_psd_bins : int, optional
            Number of bins used by the histogram for the PSD axis, by default 4096

        Returns
        -------
        output_tuple : tuple[numpy.array, numpy.array, numpy.array]
            Tuple containing the x bins, y bins and the density (z axis counts) calculated by the histogram.
        """
        data = self.open()
        min_e = min(data["Energy"])
        max_e = max(data["Energy"])
        density, xedge, yedge = numpy.histogram2d(data["Energy"], data["PSD"], [default_energy_bins, default_psd_bins], range=((min_e,max_e),(0,1)))
        return (xedge, yedge, density, (data["Energy"], data["PSD"]))

    def get_mcs_graph(self) -> tuple[numpy.array, numpy.array, pandas.Series]:
        """Generates the MCS graph's data

        Returns
        -------
        output_tuple : tuple[numpy.array, numpy.array, pandas.Series]
            Tuple containing the x data, y data and the raw data used for the graph.
        """
        data = self.open()
        t0 = 0 #seconds
        t1 = int(data['Timestamp'][len(data)-1]/10**12) #seconds
        n_bins = t1-t0
        hist = numpy.histogram(data['Timestamp']/10**12, bins=n_bins, range=(t0,t1))
        x = hist[1][1:]
        y = hist[0]
        return (x, y, data['Timestamp']/10**12)

    def run_cpp_tof(self, stop_file: str, window: int, start: int, stop: int):
        csv_file_path = self.generate_csv_name(start, stop, window)
        # CODE THIS PART WHEN THE C++ CODE IS DONE.
        pass

    

    
    
    

class RootPlotter(_root_reader):
    """
    Used to produce plots containing the data from `.root` file.

    Parameters
    ----------
    `grid`: Boolean for whether the graph should have a grid or not.

    `show`: Boolean for whether the graph should be shown or not.

    `label`: Shows the average, median and standard deviation
    """
    def __init__(self, grid=False, show=False, label=False):
        _root_reader.__init__(self, askfile=True)
        self.grid = grid
        self.show = show
        self.label = label
        

    


    def PlotEnergyHistogram(self, title='Energy Histogram', x_label='ADC bins', y_label='Counts'):
        """
        Plots the counts of energy in a histogram.
        """
        x_values, y_values = self.__energyhist__(self.file_path)
        _plt.plot(x_values, y_values, drawstyle='steps')
        _plt.xlim(0, None)
        _plt.yscale('log')
        _plt.title(title)
        _plt.grid(self.grid)
        _plt.xlabel(x_label)
        _plt.ylabel(y_label)
        if self.show:    _plt.show()

    def PlotTOFHistogram(self, min_bin, max_bin, title='TOF Histogram', x_label='ΔT (ns)', y_label='Counts', default_bin = 8192):
        """
        Plots the time difference between two channels in a histogram.
        """
        file1 = self.__getfilepath__()
        file2 = self.__getfilepath__()
        x_values, y_values, delta_t = self.__tofhist__(file1, file2, min_bin, max_bin, default_bin)
        mean = self.average(delta_t)
        stdev = self.standard_deviation(delta_t)
        median = self.median(delta_t)       

        fig ,ax = _plt.subplots()

        ax.plot(x_values, y_values, drawstyle='steps-mid')
        if self.label:  ax.lines[-1].set_label(f'Data, mean={round(mean,3)}, stdev={round(stdev,3)}, median={round(median,3)}')
        ax.set_xlim(min_bin, None)
        ax.set_ylim(0.1, None)
        ax.set_title(title)
        ax.grid(self.grid)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.legend()
        ax.set_yscale('log')
        if self.show:    _plt.show()

    def PlotMCS(self, title='MCS Graph', x_label='Elapsed time (s)', y_label='Event rate (cps)'):
        """
        Plots the rate of events in function of elapsed time.
        """
        x_values, y_values = self.__MCSgraph__()
        _plt.plot(x_values, y_values)
        _plt.title(title)
        _plt.xlim(0,None)
        _plt.grid(self.grid)
        _plt.xlabel(x_label)
        _plt.ylabel(y_label)
        if self.show:    _plt.show()

if __name__ == '__main__':
    # test = root_reader_v2("C:\\Users\\chloe\\OneDrive - McGill University\\Coincidence Testing\\Summer 2023 - CoMPASS\\DAQ\\Co60-1000V-Coinc\\RAW\\DataR_eq2611@DT5751_1989_Co60-1000V-Coinc.root", "Data_R")
    # test.open()
    # print(len(test.open()))
    # test.get_tof_hist("C:\\Users\\chloe\\OneDrive - McGill University\\Coincidence Testing\\Summer 2023 - CoMPASS\\DAQ\\Co60-1000V-Coinc (1.33MeV)\\FILTERED\\DataF_eq2432@DT5751_1989_Co60-1000V-Coinc (1.33MeV).root", -100, 100)
    test2 = root_reader_v2("C:\\Users\\chloe\\OneDrive - McGill University\\Coincidence Testing\\Summer 2023 - CoMPASS\\DAQ\\Co60-1000V-Coinc - 10us\\RAW\\DataR_eq2611@DT5751_1989_Co60-1000V-Coinc - 10us.root", "Data_R")
    test2.open()