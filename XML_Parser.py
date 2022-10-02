import xml.etree.ElementTree as ET

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
            for tab in self.groups:
                if group == tab:
                    self.parameters[tab][key] = value

        return self.parameters
                
