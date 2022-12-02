import numpy as _np
import matplotlib.pyplot as _plt
import uproot as _ur
import pandas as _pd
import tkinter.filedialog as _fd
from scipy.optimize import curve_fit
import cppimport
funcs = cppimport.imp("wrap")
#from scipy import asarray as ar,exp


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
        return _np.median(data_set)

    @staticmethod
    def average(data_set):
        """
        Returns the average of a data set.
        """
        return _np.average(data_set)

    @staticmethod
    def standard_deviation(data_set):
        """
        Returns the standard deviation of a data set.
        """
        return _np.std(data_set)

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
        psd_func = _np.vectorize(self.PSD)
        PSD_values = psd_func(data['Energy'], data['EnergyShort'])
        data.insert(2, 'PSD', PSD_values)
        

    @staticmethod
    def get_unfiltered(data_raw):
        indexes = _np.where(data_raw['Flags'] == 16384)[0]
        temp_dict = {}
        for key in data_raw.keys():
            temp_dict[key] = data_raw[key][indexes]
        return _pd.DataFrame(temp_dict)

    @staticmethod
    def data_in_range(data_unfiltered, start, stop):
        return _np.where((start <= data_unfiltered) & (data_unfiltered <= stop))

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
        keys = ['Channel', 'Timestamp', 'Board', 'Energy', 'EnergyShort']
        filtered_data = tree.arrays(keys, library='np')
        
        filtered_DF = _pd.DataFrame(filtered_data)
        if not raw:
            timestamps = filtered_DF['Timestamp']
            formatted_timestamps = _pd.to_numeric(timestamps, downcast='integer')
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
        hist = _np.histogram(data['Energy'], bins=default_bins, range=(0,default_bins))
        x = hist[1]#[1:]
        y = hist[0]
        return (x, y, data['Energy'])

    def __psdhist__(self, filepath, default_bins=4096, tree='Data_F'):
        data = self.__getdata__(filepath, tree)
        hist = _np.histogram(data['PSD'], bins=default_bins, range=(0,1))
        x = hist[1]#[1:]
        y = hist[0]
        return (x, y, data['PSD'])
        
    def __timehist__(self, filepath, min_bin, max_bin, default_bins=4096, tree='Data_F'):
        data = self.__getdata__(filepath, tree)
        time_difference = _np.ediff1d(data['Timestamp']/1000)

        hist = _np.histogram(time_difference, bins=default_bins, range=(min_bin, max_bin))
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
        delta_time = []
        for index in range(0, len(ch0_data)):
            delta_time.append((ch1_data['Timestamp'][index] - ch0_data['Timestamp'][index])/10**3) #Timestamp are in ps so we transform the result to ns.

        #Modification of the upper value for the histogram bins.
        bin_range = max_bin - min_bin
        bin_size = round(bin_range/default_bins, 3)
        if bin_size < default_bin_size:
            max_bin = min_bin + default_bins * default_bin_size
            bin_size = default_bin_size
            bin_range = max_bin - min_bin

        
        hist = _np.histogram(delta_time, default_bins, range=(min_bin, max_bin))
        x = hist[1]#[1:]
        y = hist[0]
        print(x.shape, y.shape)
        return (x, y, delta_time)

    def __CPPTOF__(self, file1, file2, low_cut_0, high_cut_0, low_cut_1, high_cut_1, window, min_bin, max_bin, default_bins=8192, default_bin_size=0.045, tree="Data_R"):
        ch0_data = self.__getdata__(file1, tree, True)
        ch1_data = self.__getdata__(file2, tree, True)

        ch0_unfiltered = self.get_unfiltered(ch0_data)
        ch1_unfiltered = self.get_unfiltered(ch1_data)

        first_line = ch0_unfiltered['Timestamp'][self.data_in_range(ch0_unfiltered['Energy'], low_cut_0, high_cut_0)]
        second_line = ch1_unfiltered['Timestamp'][self.data_in_range(ch1_unfiltered['Energy'], low_cut_1, high_cut_1)]

        start, stop = funcs.TOF(first_line, second_line, window)

        bin_range = max_bin - min_bin
        bin_size = round(bin_range/default_bins, 3)
        if bin_size < default_bin_size:
            max_bin = min_bin + default_bins * default_bin_size
            bin_size = default_bin_size
            bin_range = max_bin - min_bin

        diffs = (stop-start)*10**(-3)
        hist = _np.histogram(diffs, bins=default_bins, range=(min_bin, max_bin))
        x = hist[1]
        y = hist[0]
        return (x, y, diffs)        


    def __PSDvsE__(self, filepath, min_e, max_e, default_energy_bins=4096, default_psd_bins=4096, tree='Data_F'):
        data = self.__getdata__(filepath, tree)
        hist = _np.histogram2d(data['Energy'], data['PSD'], [default_energy_bins, default_psd_bins], range=((min_e,max_e),(0,1)))
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
        hist = _np.histogram(data['Timestamp']/10**12, bins=n_bins, range=(t0,t1))
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

# if __name__ == '__main__':
#     test = _root_reader()
#     data = test.__psdhist__("C:\\Users\\clegue4\\OneDrive - McGill University\\Coincidence Testing\\Voltage Bias Setup\\DAQ\\Ba133-EQ2611-1000V\\RAW\\DataR_CH0@DT5751_1989_Ba133-EQ2611-1000V.root", 0, 1000, tree='Data_R')
#     _plt.plot(data[0], data[1], drawstyle='steps-mid')
#     _plt.show()