import xml.etree.ElementTree as ET
from datetime import datetime
import tkinter.filedialog as fd
from bs4 import BeautifulSoup

class XMLParser:
    def __init__(self, file: str):
        self.file = file
        self.parameters = {'INPUT':{},
                        'DISCRIMINATOR':{},
                        'QDC':{},
                        'SPECTRA':{},
                        'REJECTIONS':{},
                        'ENERGY_CALIBRATION':{},
                        'SYNC':{},
                        'HARDWARE_COINCIDENCE':{},
                        'MISC':{}}
        self.groups = list(self.parameters.keys())
        self.reformatted = ['SRV_PARAM_CH_POLARITY','SRV_PARAM_CH_BLINE_NSMEAN','HARDWARE_COINCIDENCE','SRV_PARAM_START_MODE','SRV_PARAM_CH_SPECTRUM_NBINS','SRV_PARAM_CH_INDYN','SRV_PARAM_CH_CFD_FRACTION','SRV_PARAM_CH_DISCR_MODE','SRV_PARAM_CH_ENERGY_COARSE_GAIN','SRV_PARAM_TRGOUT_MODE']
        self.reformatted_keys = ['polarity', 'baseline', 'coincidence', 'start', 'ebins', 'input_range', 'cfd', 'discriminator', 'coarse_gain', 'trig_out']
        self.formatted = 0
        self.board_formatted = False

    def get_board_properties(self):
        root = ET.parse(self.file).getroot()
        name = root.find('board/label').text
        id = root.find('board/id').text
        model = root.find('board/modelName').text
        adc_bits = root.find('board/adcBitCount').text
        sample_rate = int(root.find('board/sampleTime').text)*10**6
        dpp_type = root.find('board/dppType').text
        roc = root.find('board/rocFirmware/major').text + '.' + root.find('board/rocFirmware/minor').text + ' build ' + str(hex(int(root.find('board/rocFirmware/build').text))).split('0x')[-1].zfill(4)
        amc = root.find('board/amcFirmware/major').text + '.' + root.find('board/amcFirmware/minor').text + ' build ' + str(hex(int(root.find('board/amcFirmware/build').text))).split('0x')[-1].zfill(4)
        link = root.find('board/connectionType').text + ' link #' + root.find('board/address').text
        status = root.find('board/active').text
        if status == 'true':
            status = True
        if status == 'false':
            status = False
        return name, id, model, adc_bits, sample_rate, dpp_type, roc, amc, link, status
    
    def reformat(self, list_of_params):
        """
        Reformats the values of the XML file.

        Args:
            list_of_params (list): Contains `polarity`, `baseline`, `coincidence`, `start`, `ebins`, `input_range`, `cfd`, `discriminator`, `coarse_gain`, 'trig_out`.
        """
        if 'all' in list_of_params:
            list_of_params.clear()
            list_of_params = ['polarity', 'baseline', 'coincidence', 'start', 'ebins', 'input_range', 'cfd', 'discriminator', 'coarse_gain', 'trig_out']

        #Formatting of the text values
        if 'polarity' in list_of_params:
            pol = self.parameters['INPUT']['SRV_PARAM_CH_POLARITY']
            real_pol = pol.split('_')[-1]
            self.parameters['INPUT']['SRV_PARAM_CH_POLARITY'] = real_pol

        if 'baseline' in list_of_params:
            bline = self.parameters['INPUT']['SRV_PARAM_CH_BLINE_NSMEAN']
            real_bline = bline.split('_')[-1]
            self.parameters['INPUT']['SRV_PARAM_CH_BLINE_NSMEAN'] = real_bline

        if 'coincidence' in list_of_params:
            coinc_mode = self.parameters['HARDWARE_COINCIDENCE']['SRV_PARAM_COINC_MODE']
            real_coinc_mode = coinc_mode[11:]
            self.parameters['HARDWARE_COINCIDENCE']['SRV_PARAM_COINC_MODE'] = real_coinc_mode

        if 'start' in list_of_params:
            start_mode = self.parameters['SYNC']['SRV_PARAM_START_MODE']
            real_start_mode = start_mode[11:]
            self.parameters['SYNC']['SRV_PARAM_START_MODE'] = real_start_mode
        
        if 'ebins' in list_of_params:
            energy_bins = self.parameters['SPECTRA']['SRV_PARAM_CH_SPECTRUM_NBINS']
            real_energy_bins = energy_bins[5:] +'.0'
            self.parameters['SPECTRA']['SRV_PARAM_CH_SPECTRUM_NBINS'] = real_energy_bins
        
        if 'input_range' in list_of_params:
            input_range = self.parameters['INPUT']['SRV_PARAM_CH_INDYN']
            input_range = input_range.split('_')[1:]
            real_input_range = input_range[0] + '.' + input_range[1]
            self.parameters['INPUT']['SRV_PARAM_CH_INDYN'] = real_input_range
        
        if 'cfd' in list_of_params:
            cfd_frac = self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_CFD_FRACTION']
            real_cfd_frac = cfd_frac.split('_')[-1]
            self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_CFD_FRACTION'] = real_cfd_frac
        
        if 'discriminator' in list_of_params:
            disc_mode = self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_DISCR_MODE']
            disc_mode = disc_mode.split('_')[-1]
            if disc_mode == "LED":
                real_disc_mode = "Leading Edge Discriminator"
            if disc_mode == "CFD":
                real_disc_mode = "Constant Fraction Discriminator"
            self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_DISCR_MODE'] = real_disc_mode

        if 'coarse_gain' in list_of_params:
            coarse_gain = self.parameters['QDC']['SRV_PARAM_CH_ENERGY_COARSE_GAIN']
            self.parameters['QDC']['SRV_PARAM_CH_ENERGY_COARSE_GAIN'] = coarse_gain.split('_')[1]

        if 'trig_out' in list_of_params:
            trig_out = self.parameters['SYNC']['SRV_PARAM_TRGOUT_MODE'].split('_')[2:]
            real_trig_out =""
            for elem in trig_out:
                real_trig_out += elem + ' '
            self.parameters['SYNC']['SRV_PARAM_TRGOUT_MODE'] = real_trig_out

        #FIXING THE VALUES THAT ARE IN NANOSECONDS TO SECONDS FOR SPINMOB AUTOSCALING
        if self.formatted == 0:
            self.parameters['INPUT']['SRV_PARAM_RECLEN'] = float(self.parameters['INPUT']['SRV_PARAM_RECLEN'])*10**(-9)
            self.parameters['INPUT']['SRV_PARAM_CH_PRETRG'] = float(self.parameters['INPUT']['SRV_PARAM_CH_PRETRG'])*10**(-9)
            self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_TRG_HOLDOFF'] = float(self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_TRG_HOLDOFF'])*10**(-9)
            self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_CFD_DELAY'] = float(self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_CFD_DELAY'])*10**(-9)
            self.parameters['QDC']['SRV_PARAM_CH_GATE'] = float(self.parameters['QDC']['SRV_PARAM_CH_GATE'])*10**(-9)
            self.parameters['QDC']['SRV_PARAM_CH_GATESHORT'] = float(self.parameters['QDC']['SRV_PARAM_CH_GATESHORT'])*10**(-9)
            self.parameters['QDC']['SRV_PARAM_CH_GATEPRE'] = float(self.parameters['QDC']['SRV_PARAM_CH_GATEPRE'])*10**(-9)
            self.parameters['SPECTRA']['SW_PARAMETER_TIME_DISTRIBUTION_CH_T0'] = float(self.parameters['SPECTRA']['SW_PARAMETER_TIME_DISTRIBUTION_CH_T0'])*10**(-9)
            self.parameters['SPECTRA']['SW_PARAMETER_TIME_DISTRIBUTION_CH_T1'] = float(self.parameters['SPECTRA']['SW_PARAMETER_TIME_DISTRIBUTION_CH_T1'])*10**(-9)
            self.parameters['SPECTRA']['SW_PARAMETER_TIME_DIFFERENCE_CH_T0'] = float(self.parameters['SPECTRA']['SW_PARAMETER_TIME_DIFFERENCE_CH_T0'])*10**(-9)
            self.parameters['SPECTRA']['SW_PARAMETER_TIME_DIFFERENCE_CH_T1'] = float(self.parameters['SPECTRA']['SW_PARAMETER_TIME_DIFFERENCE_CH_T1'])*10**(-9)
            self.parameters['HARDWARE_COINCIDENCE']['SRV_PARAM_COINC_TRGOUT'] = float(self.parameters['HARDWARE_COINCIDENCE']['SRV_PARAM_COINC_TRGOUT'])*10**(-9)
            self.parameters['REJECTIONS']['SW_PARAMETER_CH_ENERGYCUTENABLE'] = (True if self.parameters['REJECTIONS']['SW_PARAMETER_CH_ENERGYCUTENABLE'] == 'true' else False)
        self.formatted += 1
    
    def get_parameters(self):
        """
        Gets the board parameters (shared parameters for all channels).
        """
        root = ET.parse(self.file).getroot()
        board_parameters = root.find('board/parameters')
        for entry in board_parameters:
            key = entry.find('key').text
            value = entry.find('value/value').text
            group = entry.find('value/descriptor/group').text
            
            if value == 'true':
                value = True
            if value == 'false':
                value = False
                
            for tab in self.groups:
                if group == tab:
                    #if units is None:
                    self.parameters[tab][key] = value
                    #else:
                        #self.parameters[tab][key] = [value, units]
        self.formatted = 0
        self.reformat(['all'])
        
        return self.parameters

    def get_chn_parameters(self, chn_number: str):
        root = ET.parse(self.file).getroot()
        channels = root.findall('board/channel')
        channel_in_use = channels[chn_number]
        # keys = channel_in_use.findall('values/entry/key')
        # values = channel_in_use.findall('values/entry/value')
        entries = channel_in_use.findall('values/entry')
        entries_with_vals = []
        for index, entry in enumerate(entries):
            if entry.find('value') is not None:
                entries_with_vals.append(entries[index])

        keys = []
        values = []
        for entry in entries_with_vals:
            keys.append(entry.find('key'))
            values.append(entry.find('value'))

        list_format = []
        for key in keys:
            if key.text in self.reformatted:
                list_format.append(self.reformatted_keys[self.reformatted.index(key.text)])
        
        for group in self.parameters:
            for index, key in enumerate(keys):
                if key.text in self.parameters[group]:
                    if 'true' in values[index].text or 'false' in values[index].text:
                        values[index].text = (True if values[index].text == 'true' else False)
                    else:
                        self.parameters[group][key.text] = values[index].text
        
        # self.formatted = 0
        # self.reformat(list_format)
        return self.parameters

    def get_ch_label(self, chn_number: str):
        root = ET.parse(self.file).getroot()
        channels = root.findall('board/channel')
        channel_to_check = channels[chn_number]
        index = channel_to_check.find('index').text
        entries = channel_to_check.findall('values/entry')
        for entry in entries:
            if entry.find('key').text == "SW_PARAMETER_CH_LABEL":
                label = entry.find('value').text
                break
        else: # I'm a genius. Don't mind me using disgusting functions in python.
            label = "CH" #This is executed if the loop ends normally (so without encountering the break above.)
        return (index, label)


class InfoParser:
    def __init__(self, file: str):
        self.file = file       

    def get_run_info(self):
        with open(self.file) as f:
            informations = f.readlines()[0:4]
        self.id = informations[0].split('=')[-1][:-1]
        self.time_start = datetime.strptime(informations[1].split('=')[-1].split('.')[0], "%Y/%m/%d %H:%M:%S")
        self.time_stop = datetime.strptime(informations[2].split('=')[-1].split('.')[0], "%Y/%m/%d %H:%M:%S")
        self.time_real = self.time_stop - self.time_start
        return self.id, self.time_start, self.time_stop, self.time_real

if __name__ == '__main__':
    file = "C:\\Users\\chloe\\OneDrive - McGill University\\Coincidence Testing\\Co60 Spectrums with different settings\\DAQ\\4096Chns-20lsb(LE)-80Gain-(300.80.50)-150s\\settings.xml"
    test = XMLParser(file)
    test.get_parameters()
    print(test.get_ch_label(2))