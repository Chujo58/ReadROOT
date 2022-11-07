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
    
    def reformat(self):
        #Formatting of the text values
        pol = self.parameters['INPUT']['SRV_PARAM_CH_POLARITY']
        real_pol = pol.split('_')[-1]
        self.parameters['INPUT']['SRV_PARAM_CH_POLARITY'] = real_pol

        bline = self.parameters['INPUT']['SRV_PARAM_CH_BLINE_NSMEAN']
        real_bline = bline.split('_')[-1]
        self.parameters['INPUT']['SRV_PARAM_CH_BLINE_NSMEAN'] = real_bline

        coinc_mode = self.parameters['HARDWARE_COINCIDENCE']['SRV_PARAM_COINC_MODE']
        real_coinc_mode = coinc_mode[11:]
        self.parameters['HARDWARE_COINCIDENCE']['SRV_PARAM_COINC_MODE'] = real_coinc_mode

        start_mode = self.parameters['SYNC']['SRV_PARAM_START_MODE']
        real_start_mode = start_mode[11:]
        self.parameters['SYNC']['SRV_PARAM_START_MODE'] = real_start_mode
        
        energy_bins = self.parameters['SPECTRA']['SRV_PARAM_CH_SPECTRUM_NBINS']
        real_energy_bins = energy_bins[5:] +'.0'
        self.parameters['SPECTRA']['SRV_PARAM_CH_SPECTRUM_NBINS'] = real_energy_bins
        
        input_range = self.parameters['INPUT']['SRV_PARAM_CH_INDYN']
        input_range = input_range.split('_')[1:]
        real_input_range = input_range[0] + '.' + input_range[1]
        self.parameters['INPUT']['SRV_PARAM_CH_INDYN'] = real_input_range
        
        cfd_frac = self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_CFD_FRACTION']
        real_cfd_frac = cfd_frac.split('_')[-1]
        self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_CFD_FRACTION'] = real_cfd_frac
        
        disc_mode = self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_DISCR_MODE']
        disc_mode = disc_mode.split('_')[-1]
        if disc_mode == "LED":
            real_disc_mode = "Leading Edge Discriminator"
        if disc_mode == "CFD":
            real_disc_mode = "Constant Fraction Discriminator"
        self.parameters['DISCRIMINATOR']['SRV_PARAM_CH_DISCR_MODE'] = real_disc_mode

        coarse_gain = self.parameters['QDC']['SRV_PARAM_CH_ENERGY_COARSE_GAIN']
        self.parameters['QDC']['SRV_PARAM_CH_ENERGY_COARSE_GAIN'] = coarse_gain.split('_')[1]

        trig_out = self.parameters['SYNC']['SRV_PARAM_TRGOUT_MODE'].split('_')[2:]
        real_trig_out =""
        for elem in trig_out:
             real_trig_out += elem + ' '
        self.parameters['SYNC']['SRV_PARAM_TRGOUT_MODE'] = real_trig_out

        #FIXING THE VALUES THAT ARE IN NANOSECONDS TO SECONDS FOR SPINMOB AUTOSCALING
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
        self.reformat()
        
        return self.parameters

    def get_chn_parameters(self, chn_number: str):
        root = ET.parse(self.file).getroot()
        chns = root.findall('board/channel')
        params = {}
        for chn in chns:
            if chn.find('index').text == chn_number:
                values = chn.find('values')
        for entry in values:
            params[entry.find('key').text] = entry.find('value').text

        return params


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
    file = fd.askopenfilename()
    test = XMLParser(file)
    print(bool(test.get_chn_parameters('0')))