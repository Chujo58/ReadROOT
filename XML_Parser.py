import xml.etree.ElementTree as ET
from datetime import datetime

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
    
    def get_parameters(self):
        """
        Gets the board parameters (shared parameters for all channels).
        """
        root = ET.parse(self.file).getroot()
        board_parameters = root.find('board/parameters')
        for entry in board_parameters:
            value = entry.find('value/value').text
            group = entry.find('value/descriptor/group').text
            units = entry.find('value/descriptor/udm').text
            if units == "NANOS":
                units = "ns"
            for tab in self.groups:
                if group == tab:
                    self.parameters[tab][key] = value

        return self.parameters

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