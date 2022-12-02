#----------------------------------------------------------------------------
# Created by : Chloé Legué
# Current version date : 2022/08/10
# Version = 1.0
#----------------------------------------------------------------------------
"""
This code was made for the coincidence experiment at McGill University. 

The code allows the user to choose a folder containing the results saved from the CoMPASS software from CAEN. This code should be used with the CAEN DT5751, or any other digitizer from CAEN that work in the same way.

This code is able to reproduce the important graphs that the CoMPASS software makes like MCS Graph, Energy Histogram and TOF Histogram. Other graphs can be added if needed.
"""
#----------------------------------------------------------------------------
# Imports
import os as _os
#----------------------------------------------------------------------------
# Other imports 
from ReadROOT import _root_reader
from XML_Parser import InfoParser, XMLParser
import spinmob as _s
import spinmob.egg as _egg
import numpy as _np
import uproot as _ur
import pandas as _pd
import tkinter.filedialog as _fd
import pyqtgraph as _pg
import ctypes as _ct
import pyqtgraph.exporters as _export
import darkdetect as _dd
import re as _re
from PyQt5 import QtGui, QtWidgets
import time
from scipy.optimize import curve_fit as _cf
from ErrorPropagation import UFloat as _uf
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm

_g = _egg.gui

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

running_from_main = False

def gaussian(x, centroid, sigma, amplitude):
    return amplitude*_np.exp(-(x-centroid)**2/(2*sigma**2))

def fit(x: float, center: float, spread: float, log_amp: float) -> float:
    """
    Function used for the `scipy.optimize.curve_fit`.

    Args:
        x (float): Data used for the fit.
        center (float): Center of the gaussian.
        spread (float): Spread of the gaussian.
        log_amp (float): Natural logarithm of the amplitude of the gaussian.

    Returns:
        float: Value after going through the fit.
    """
    return (2*log_amp*spread**2-(x-center)**2)/(2*spread**2)

def complementary(color: tuple) -> tuple:
    r,g,b,a = color
    return (255-r,255-g,255-b,a)

def FWAP(x_data, center: _uf, spread: _uf, amp: _uf, percent: float):
    y_data = gaussian(x_data, center._value, spread._value, amp._value)
    half_max = percent*max(y_data)
    x_1 = center-(spread**2*(-2)*(amp**(-1)*half_max).evalf(_np.log)).evalf(_np.sqrt)
    x_2 = center+(spread**2*(-2)*(amp**(-1)*half_max).evalf(_np.log)).evalf(_np.sqrt)
    return x_2-x_1


def chi_sqr(expected, obtained):
    if len(expected) != len(obtained):
        raise ValueError("Both arrays should have the same size for the calculation of χ2.")
    else:
        sum = 0
        for i in range(0, len(expected)):
            sum += (obtained[i]-expected[i])**2/expected[i]
    return sum

white_turbo_list = [
    (0, '#ffffff'),
    (1e-20, '#30123b'),
    (0.1, '#4458cb'),
    (0.2, '#3e9bfe'),
    (0.4, '#46f783'),
    (0.5, '#a4fc3b'),
    (0.6, '#e1dc37'),
    (0.7, '#fda330'),
    (0.8, '#ef5a11'),
    (0.9, '#c32402'),
    (1, '#311542')
]

white_turbo = LinearSegmentedColormap.from_list('white_turbo', white_turbo_list, N=256)

cm.register_cmap('white_turbo', white_turbo)


class GUI(_root_reader):
    def __init__(self, name='GUI', window_size=[1000,500], show=True, block=True):
        self.PSDvsE_BEFORE = False
        self.name = name
        self.folder_path = ''
        self.folder_containing_root =''
        self.filepath1 = ''
        self.filepath2 = ''
        self.xml_parameters = {"INPUT":{"Enable":"SRV_PARAM_CH_ENABLED",
                                        "Record length":"SRV_PARAM_RECLEN",
                                        "Pre-trigger":"SRV_PARAM_CH_PRETRG",
                                        "Polarity":"SRV_PARAM_CH_POLARITY",
                                        "N samples baseline":"SRV_PARAM_CH_BLINE_NSMEAN",
                                        "Fixed baseline value":"SRV_PARAM_CH_BLINE_FIXED",
                                        "DC Offset":"SRV_PARAM_CH_BLINE_DCOFFSET",
                                        "Calibrate ADC":"SRV_PARAM_ADCCALIB_ONSTART_ENABLE",
                                        "Input dynamic":"SRV_PARAM_CH_INDYN",
                                        "Analog Traces Fine Resolution":"SRV_PARAM_ANALOGTR_FINERES_ENABLE"},
                                "DISCRIMINATOR":{"Discriminator mode":"SRV_PARAM_CH_DISCR_MODE",
                                                 "Threshold":"SRV_PARAM_CH_THRESHOLD",
                                                 "Trigger holdoff":"SRV_PARAM_CH_TRG_HOLDOFF",
                                                 "CFD delay":"SRV_PARAM_CH_CFD_DELAY",
                                                 "CFD fraction":"SRV_PARAM_CH_CFD_FRACTION"},
                                "QDC":{"Energy coarse gain":"SRV_PARAM_CH_ENERGY_COARSE_GAIN",
                                       "Gate":"SRV_PARAM_CH_GATE",
                                       "Short gate":"SRV_PARAM_CH_GATESHORT",
                                       "Pre-gate":"SRV_PARAM_CH_GATEPRE",
                                       "Charge pedestal":"SRV_PARAM_CH_PEDESTAL_EN"},
                                "SPECTRA":{"Energy N channels":"SRV_PARAM_CH_SPECTRUM_NBINS",
                                           "PSD N channels":"SW_PARAMETER_PSDBINCOUNT",
                                           "Time intervals N channels":"SW_PARAMETER_DISTRIBUTION_BINCOUNT",
                                           "Time intervals Tmin":"SW_PARAMETER_TIME_DISTRIBUTION_CH_T0",
                                           "Time intervals Tmax":"SW_PARAMETER_TIME_DISTRIBUTION_CH_T1",
                                           "Start-stop Δt N channels":"SW_PARAMETER_DIFFERENCE_BINCOUNT",
                                           "Start-stop Δt Tmin":"SW_PARAMETER_TIME_DIFFERENCE_CH_T0",
                                           "Start-stop Δt Tmax":"SW_PARAMETER_TIME_DIFFERENCE_CH_T1",
                                           "2D Energy N channels":"SW_PARAMETER_E2D_BINCOUNT",
                                           "2D PSD N channels":"SW_PARAMETER_PSD2D_BINCOUNT",
                                           "2D Δt N channels":"SW_PARAMETER_TOF2D_BINCOUNT"},
                                "REJECTIONS":{"Saturation rejection":"SW_PARAM_CH_SATURATION_REJECTION_ENABLE",
                                              "Pileup rejection":"SW_PARAM_CH_PUR_ENABLE",
                                              "E low cut":"SW_PARAMETER_CH_ENERGYLOWCUT",
                                              "E high cut":"SW_PARAMETER_CH_ENERGYHIGHCUT",
                                              "E cut enable":"SW_PARAMETER_CH_ENERGYCUTENABLE",
                                              "PSD low cut":"SW_PARAMETER_CH_PSDLOWCUT",
                                              "PSD high cut":"SW_PARAMETER_CH_PSDHIGHCUT",
                                              "PSD cut enable":"SW_PARAMETER_CH_PSDCUTENABLE",
                                              "Time intervals low cut":"SW_PARAMETER_CH_TIMELOWCUT",
                                              "Time intervals high cut":"SW_PARAMETER_CH_TIMEHIGHCUT",
                                              "Time intervals cut enable":"SW_PARAMETER_CH_TIMECUTENABLE"},
                                "ENERGY CALIBRATION":{"C0":"SW_PARAMETER_CH_ENERGY_CALIBRATION_P0",
                                                      "C1":"SW_PARAMETER_CH_ENERGY_CALIBRATION_P1",
                                                      "C2":"SW_PARAMETER_CH_ENERGY_CALIBRATION_P2",
                                                      "Units":"SW_PARAMETER_CH_ENERGY_CALIBRATION_UDM"},
                                "SYNC":{"External clock source":"SRV_PARAM_DT_EXT_CLOCK",
                                        "Start mode":"SRV_PARAM_START_MODE",
                                        "TRG OUT-GPO mode":"SRV_PARAM_TRGOUT_MODE",
                                        "Start delay":"SRV_PARAM_START_DELAY",
                                        "Channel time offset":"SRV_PARAM_CH_TIME_OFFSET"},
                                "ONBOARD COINCIDENCES":{"Coincidence mode":"SRV_PARAM_COINC_MODE",
                                                        "Coincidence window":"SRV_PARAM_COINC_TRGOUT"},
                                "MISC":{"Label":"SW_PARAMETER_CH_LABEL",
                                        "FPIO type":"SRV_PARAM_IOLEVEL",
                                        "Rate optimization":"SRV_PARAM_EVENTAGGR"}}

        self.xml_types = {"INPUT":{"Enable":'bool',
                                   "Record length":'float',
                                   "Pre-trigger":'float',
                                   "Polarity":'str',
                                   "N samples baseline":'str',
                                   "Fixed baseline value":'str',
                                   "DC Offset":'float',
                                   "Calibrate ADC":'bool',
                                   "Input dynamic":'float',
                                   "Analog Traces Fine Resolution":'bool'},
                          "DISCRIMINATOR":{"Discriminator mode":'str',
                                           "Threshold":'float',
                                           "Trigger holdoff":'float',
                                           "CFD delay":'float',
                                           "CFD fraction":'float'},
                          "QDC":{"Energy coarse gain":'str',
                                 "Gate":'float',
                                 "Short gate":'float',
                                 "Pre-gate":'float',
                                 "Charge pedestal":'bool'},
                          "SPECTRA":{"Energy N channels":'str',
                                     "PSD N channels":'str',
                                     "Time intervals N channels":'str',
                                     "Time intervals Tmin":'float',
                                     "Time intervals Tmax":'float',
                                     "Start-stop Δt N channels":'str',
                                     "Start-stop Δt Tmin":'float',
                                     "Start-stop Δt Tmax":'float',
                                     "2D Energy N channels":'str',
                                     "2D PSD N channels":'str',
                                     "2D Δt N channels":'str'},
                          "REJECTIONS":{"Saturation rejection":'bool',
                                        "Pileup rejection":'bool',
                                        "E low cut":'float',
                                        "E high cut":'float',
                                        "E cut enable":'bool',
                                        "PSD low cut":'float',
                                        "PSD high cut":'float',
                                        "PSD cut enable":'bool',
                                        "Time intervals low cut":'float',
                                        "Time intervals high cut":'float',
                                        "Time intervals cut enable":'bool'},
                          "ENERGY CALIBRATION":{"C0":'float',
                                                "C1":'float',
                                                "C2":'float',
                                                "Units":'str'},
                          "SYNC":{"External clock source":'bool',
                                  "Start mode":'str',
                                  "TRG OUT-GPO mode":'str',
                                  "Start delay":'float',
                                  "Channel time offset":'float'},
                          "ONBOARD COINCIDENCES":{"Coincidence mode":'str',
                                                  "Coincidence window":'float'},
                          "MISC":{"Label":'str',
                                  "FPIO type":'str',
                                  "Rate optimization":'float'}}

        self.xml_units = {"INPUT":{"Record length":'s',
                                   "Pre-trigger":'s',
                                   "DC Offset":'%',
                                   "Input dynamic":'Vpp'},
                          "DISCRIMINATOR":{"Threshold":'lsb',
                                           "Trigger holdoff":'s',
                                           "CFD delay":'s',
                                           "CFD fraction":'%'},
                          "QDC":{"Gate":'s',
                                 "Short gate":'s',
                                 "Pre-gate":'s'},
                          "SPECTRA":{"Time intervals Tmin":'s',
                                     "Time intervals Tmax":'s',
                                     "Start-stop Δt Tmin":'s',
                                     "Start-stop Δt Tmax":'s'},
                          "ONBOARD COINCIDENCES":{"Coincidence window":'s'}}

        if not running_from_main:
            module_list = ['cppimport', 'pybind11', 'uproot', 'pyqtgraph=0.12.4', 'darkdetect', 'numpy', 'pandas','PyQt5']
            print(bcolors.WARNING + "Please make sure that the following modules are installed on your machine." + bcolors.ENDC)
            for module in module_list:
                if module != module_list[-1]:
                    print(module, end=', ')
                else:
                    print(module)
            print(bcolors.WARNING + "Also note that you can use raw ROOT files directly to calculate the TOF." + bcolors.ENDC)
 
        screen_width, screen_height = self.__get_screen_resolution__()
        window_width = int(window_size[0]/1680*screen_width)
        window_height = int(window_size[1]/1050*screen_height)
        scaleFactor = _ct.windll.shcore.GetScaleFactorForDevice(0)/100

        #self.ratio = int(window_width/window_size[0])
        self.ratio = int(scaleFactor)
        
        self.window = _g.Window(name, size=[window_width, window_height], autosettings_path=name+'_window.txt')
        self.window._window.setWindowIcon(QtGui.QIcon('Images/CoMPASS/icon64x64.ico'))
        self.grid_top = self.window.place_object(_g.GridLayout(False)).set_height(50*self.ratio)
        self.window.new_autorow()
        self.grid_bot = self.window.place_object(_g.GridLayout(False), alignment=0)
        self.grid_top.set_column_stretch(1,1)



        #Buttons
        self.button_folder = self.grid_top.place_object(_g.Button(' ', tip='Search folder')).set_width(45*self.ratio).set_height(45*self.ratio)
        self.button_folder.set_style_unchecked(style='image: url(Images/OpenFolder.png)')
        #self.button_transform = self.grid_top.place_object(_g.Button('Transform selected file'))
        #self.folder_label = self.grid_top.place_object(_g.Label('No folder selected'))

        #File settings tab
        self.file_settings = self.grid_top.place_object(_g.TreeDictionary(name+'_file_settings.txt', name), alignment=0).set_width(245*self.ratio).set_height(40*self.ratio)

        self.file_settings.add_parameter(key='Files Settings/Folder', type='list', values=['FILTERED', 'UNFILTERED', 'RAW'])
        self.file_settings.connect_signal_changed('Files Settings/Folder', self.__settings_folder_changed__)

        self.file_label = self.grid_top.place_object(_g.Label('No file selected'))

        self.button_folder.signal_clicked.connect(self.__search_folder__)
        #self.button_transform.signal_clicked.connect(self.__transform__)



        #Channels button
        self.ch0 = self.grid_top.place_object(_g.Button(' ', True, tip='CH0').set_width(45*self.ratio)).set_height(45*self.ratio)
        self.ch0.set_style_unchecked(style='image: url(Images/Off0.png)')
        self.ch0.set_style_checked(style='image: url(Images/On0.png)')
        
        self.ch1 = self.grid_top.place_object(_g.Button(' ', True, tip='CH1').set_width(45*self.ratio)).set_height(45*self.ratio)
        self.ch1.set_style_unchecked(style='image: url(Images/Off1.png)')
        self.ch1.set_style_checked(style='image: url(Images/On1.png)')

        self.ch2 = self.grid_top.place_object(_g.Button(' ', True, tip='CH2').set_width(45*self.ratio)).set_height(45*self.ratio)
        self.ch2.set_style_unchecked(style='image: url(Images/Off2.png)')
        self.ch2.set_style_checked(style='image: url(Images/On2.png)')
        
        self.ch3 = self.grid_top.place_object(_g.Button(' ', True, tip='CH3').set_width(45*self.ratio)).set_height(45*self.ratio)
        self.ch3.set_style_unchecked(style='image: url(Images/Off3.png)')
        self.ch3.set_style_checked(style='image: url(Images/On3.png)')

        self.ch0.signal_toggled.connect(self.__channel_buttons__)
        self.ch1.signal_toggled.connect(self.__channel_buttons__)
        self.ch2.signal_toggled.connect(self.__channel_buttons__)
        self.ch3.signal_toggled.connect(self.__channel_buttons__)

        #Plot button
        self.plot = self.grid_top.place_object(_g.Button(' ', tip='Plot').set_width(45*self.ratio)).set_height(45*self.ratio)
        self.plot.set_style_unchecked(style='image: url(Images/Plot.png)')
        self.plot.signal_clicked.connect(self.__plot__)

        #Clear button
        self.clear = self.grid_top.place_object(_g.Button(' ', tip='Clear').set_width(45*self.ratio)).set_height(45*self.ratio)
        self.clear.set_style_unchecked(style='image: url(Images/Clear.png)')
        self.clear.signal_clicked.connect(self.__clear__)

        #Save plot button
        self.save = self.grid_top.place_object(_g.Button(' ', tip='Save Plot Image')).set_width(45*self.ratio).set_height(45*self.ratio)
        self.save.set_style_unchecked(style='image: url(Images/SaveImage.png)')
        self.save.signal_clicked.connect(self.__save_image__)

        self.select = self.grid_top.place_object(_g.Button(' ', tip='Select ROI',checkable=True)).set_width(45*self.ratio).set_height(45*self.ratio)
        self.select.set_style_unchecked(style='image: url(Images/SelectROI.png)')
        self.select.set_style_checked(style='image: url(Images/SelectROIOn.png)')
        self.select.signal_toggled.connect(self.__select_ROI__)

                
        #General tab area containing the graph and COMPASS sections
        self.GeneralTabArea = self.grid_bot.place_object(_g.TabArea(name+'_gen_tabs_settings.txt'), alignment=0)
        self.COMPASS = self.GeneralTabArea.add_tab('CoMPASS')
        self.GRAPH = self.GeneralTabArea.add_tab('GRAPH')

        comp_icon = QtGui.QIcon('Images/CoMPASS/icon64x64.ico')
        graph_icon = QtGui.QIcon('Images/CoMPASS/OpenGraph.png')
        self.GeneralTabArea._widget.setTabIcon(0, comp_icon)
        self.GeneralTabArea._widget.setTabIcon(1, graph_icon)


        #COMPASS
        self.run_info = self.COMPASS.place_object(_g.TreeDictionary(), alignment=0).set_height(85*self.ratio)
        self.run_info.add_parameter(key="Run ID", value=" ", readonly=True, tip="Run ID name set in CoMPASS/Folder name in which files are saved.")
        self.run_info.add_parameter(key="Start Time", value=" ", readonly=True, tip="Time at which the acquisition started.")
        self.run_info.add_parameter(key="Stop Time", value=" ", readonly=True, tip="Time at which the acquisition stopped.")
        self.run_info.add_parameter(key="Run Time", value=" ", readonly=True, tip="Amount of time the acquisition ran for.")
        
        self.COMPASS.new_autorow()
        self.BOARD = self.COMPASS.place_object(_g.TabArea(), alignment=0)
        self.board_properties = self.BOARD.add_tab('Board Properties')
        self.board_1 = self.board_properties.place_object(_g.TreeDictionary(), alignment=0).set_height(85*self.ratio)
        self.board_2 = self.board_properties.place_object(_g.TreeDictionary(), alignment=0).set_height(85*self.ratio)
        self.board_3 = self.board_properties.place_object(_g.TreeDictionary(), alignment=0).set_height(85*self.ratio)
        
        self.board_properties.new_autorow()
        self.COMPASS_settings = self.board_properties.place_object(_g.TabArea(), alignment=0, column_span=3)

        #Board properties
        self.board_1.add_parameter(key="Name", value=" ", readonly=True, tip="Name of the digitizer in use.")
        self.board_1.add_parameter(key="ADC bits", value=" ", readonly=True, tip="Number of binary digits used to represent the digital numbers.")
        self.board_1.add_parameter(key="ROC firmware", value=" ", readonly=True)
        self.board_1.add_parameter(key="Link", value=" ", readonly=True)

        self.board_2.add_parameter(key="ID", value=" ", readonly=True)
        self.board_2.add_parameter(key="Sampling rate  ", value=None, type='float', readonly=True, suffix="S/s", siPrefix=True)
        self.board_2.add_parameter(key="AMC firmware", value=" ", readonly=True)
        
        self.board_3.add_parameter(key="Model", value=" ", readonly=True)
        self.board_3.add_parameter(key="DPP type", value=" ", readonly=True)
        self.board_3.add_parameter(key="Enable", value=False, readonly=True)

        #CoMPASS Icons/Icons for the settings tree dictionary.
        input_icon = QtGui.QIcon('Images/CoMPASS/Input.png')
        disc_icon = QtGui.QIcon('Images/CoMPASS/Discriminator.png')
        qdc_icon = QtGui.QIcon('Images/CoMPASS/QDC.png')
        spectra_icon = QtGui.QIcon('Images/CoMPASS/Spectra.png')
        rejection_icon = QtGui.QIcon('Images/CoMPASS/Rejections.png')
        energy_icon = QtGui.QIcon('Images/CoMPASS/EnergyCalibration.png')
        sync_icon = QtGui.QIcon('Images/CoMPASS/Sync.png')
        coinc_icon = QtGui.QIcon('Images/CoMPASS/Coincidence.png')
        misc_icon = QtGui.QIcon('Images/CoMPASS/Misc.png')

        #CoMPASS Settings
        self.INPUT = self.COMPASS_settings.add_tab("INPUT")
        self.COMPASS_settings._widget.setTabIcon(0, input_icon)

        self.DISCRIMINATOR = self.COMPASS_settings.add_tab("DISCRIMINATOR")
        self.COMPASS_settings._widget.setTabIcon(1, disc_icon)

        self.QDC = self.COMPASS_settings.add_tab("QDC")
        self.COMPASS_settings._widget.setTabIcon(2, qdc_icon)

        self.SPECTRA = self.COMPASS_settings.add_tab("SPECTRA")
        self.COMPASS_settings._widget.setTabIcon(3, spectra_icon)

        self.REJECTIONS = self.COMPASS_settings.add_tab("REJECTIONS")
        self.COMPASS_settings._widget.setTabIcon(4, rejection_icon)

        self.ENERGYCAL = self.COMPASS_settings.add_tab("ENERGY CALIBRATION")
        self.COMPASS_settings._widget.setTabIcon(5, energy_icon)

        self.SYNC = self.COMPASS_settings.add_tab("SYNC/TRG")
        self.COMPASS_settings._widget.setTabIcon(6, sync_icon)

        self.COINCIDENCE = self.COMPASS_settings.add_tab("ONBOARD COINCIDENCES")
        self.COMPASS_settings._widget.setTabIcon(7, coinc_icon)

        self.MISC = self.COMPASS_settings.add_tab("MISCELLANEOUS")
        self.COMPASS_settings._widget.setTabIcon(8, misc_icon)

        #Tree dictionaries for each CoMPASS settings
        self.input_ch = self.INPUT.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.input_ch.add_parameter(key="Channel", type='list', values=['BOARD','CH0','CH1','CH2','CH3'])
        self.INPUT.new_autorow()
        self.input_tree = self.INPUT.place_object(_g.TreeDictionary(), alignment=0)
        self.input_ch.connect_signal_changed('Channel', self.__reload_channels__)

        self.disc_ch = self.DISCRIMINATOR.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.disc_ch.add_parameter(key="Channel", type='list', values=['BOARD','CH0','CH1','CH2','CH3'])
        self.DISCRIMINATOR.new_autorow()
        self.disc_tree = self.DISCRIMINATOR.place_object(_g.TreeDictionary(), alignment=0)
        self.disc_ch.connect_signal_changed('Channel', self.__reload_channels__)

        self.qdc_ch = self.QDC.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.qdc_ch.add_parameter(key="Channel", type='list', values=['BOARD','CH0','CH1','CH2','CH3'])
        self.QDC.new_autorow()
        self.qdc_tree = self.QDC.place_object(_g.TreeDictionary(), alignment=0)
        self.qdc_ch.connect_signal_changed('Channel', self.__reload_channels__)

        self.spectra_ch = self.SPECTRA.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.spectra_ch.add_parameter(key="Channel", type='list', values=['BOARD','CH0','CH1','CH2','CH3'])
        self.SPECTRA.new_autorow()
        self.spectra_tree = self.SPECTRA.place_object(_g.TreeDictionary(), alignment=0)
        self.spectra_ch.connect_signal_changed('Channel', self.__reload_channels__)
        
        self.rejection_ch = self.REJECTIONS.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.rejection_ch.add_parameter(key="Channel", type='list', values=['BOARD','CH0','CH1','CH2','CH3'])
        self.REJECTIONS.new_autorow()
        self.rejection_tree = self.REJECTIONS.place_object(_g.TreeDictionary(), alignment=0)
        self.rejection_ch.connect_signal_changed('Channel', self.__reload_channels__)
        
        self.energy_ch = self.ENERGYCAL.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.energy_ch.add_parameter(key="Channel", type='list', values=['BOARD','CH0','CH1','CH2','CH3'])
        self.ENERGYCAL.new_autorow()
        self.energy_tree = self.ENERGYCAL.place_object(_g.TreeDictionary(), alignment=0)
        self.energy_ch.connect_signal_changed('Channel', self.__reload_channels__)
        
        self.sync_ch = self.SYNC.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.sync_ch.add_parameter(key="Channel", type='list', values=['BOARD','CH0','CH1','CH2','CH3'])
        self.SYNC.new_autorow()
        self.sync_tree = self.SYNC.place_object(_g.TreeDictionary(), alignment=0)
        self.sync_ch.connect_signal_changed('Channel', self.__reload_channels__)
        
        self.coinc_ch = self.COINCIDENCE.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.coinc_ch.add_parameter(key="Channel", value="BOARD")
        self.COINCIDENCE.new_autorow()
        self.coinc_tree = self.COINCIDENCE.place_object(_g.TreeDictionary(), alignment=0)
        self.coinc_ch.connect_signal_changed('Channel', self.__reload_channels__)
        
        self.misc_ch = self.MISC.place_object(_g.TreeDictionary(), alignment=0).set_height(25*self.ratio)
        self.misc_ch.add_parameter(key="Channel", type='list', values=['BOARD','CH0','CH1','CH2','CH3'])
        self.MISC.new_autorow()
        self.misc_tree = self.MISC.place_object(_g.TreeDictionary(), alignment=0)
        self.misc_ch.connect_signal_changed('Channel', self.__reload_channels__)

        #INPUT TAB
        input_parameters = list(self.xml_parameters['INPUT'].keys())
        for param in input_parameters:
            try:
                units = self.xml_units['INPUT'][param]
            except:
                units = None
            if units == None:
                suffixOn = False
            else:
                suffixOn = True
            type_value = self.xml_types['INPUT'][param]
            self.input_tree.add_parameter(key=param, value=None, type=type_value, suffix=units, siPrefix=suffixOn, readonly=True)

        #DISCRIMINATOR TAB
        disc_parameters = list(self.xml_parameters['DISCRIMINATOR'].keys())
        for param in disc_parameters:
            try:
                units = self.xml_units['DISCRIMINATOR'][param]
            except:
                units = None
            if units == None:
                suffixOn = False
            else:
                suffixOn = True
            type_value = self.xml_types['DISCRIMINATOR'][param]
            self.disc_tree.add_parameter(key=param, value=None, type=type_value, suffix=units, siPrefix=suffixOn, readonly=True)

        #QDC TAB
        qdc_parameters = list(self.xml_parameters['QDC'].keys())
        for param in qdc_parameters:
            try:
                units = self.xml_units['QDC'][param]
            except:
                units = None
            if units == None:
                suffixOn = False
            else:
                suffixOn = True
            type_value = self.xml_types['QDC'][param]
            self.qdc_tree.add_parameter(key=param, value=None, type=type_value, suffix=units, siPrefix=suffixOn, readonly=True)

        #SPECTRA TAB
        spectra_parameters = list(self.xml_parameters['SPECTRA'].keys())
        for param in spectra_parameters:
            try:
                units = self.xml_units['SPECTRA'][param]
            except:
                units = None
            if units == None:
                suffixOn = False
            else:
                suffixOn = True
            type_value = self.xml_types['SPECTRA'][param]
            self.spectra_tree.add_parameter(key=param, value=None, type=type_value, suffix=units, siPrefix=suffixOn, readonly=True)

        #REJECTIONS TAB
        rej_parameters = list(self.xml_parameters['REJECTIONS'].keys())
        for param in rej_parameters:
            type_value= self.xml_types['REJECTIONS'][param]
            self.rejection_tree.add_parameter(key=param, value=None, type=type_value, readonly=True)

        #ENERGY CALIBRATION TAB
        energy_parameters = list(self.xml_parameters['ENERGY CALIBRATION'].keys())
        for param in energy_parameters:
            type_value = self.xml_types['ENERGY CALIBRATION'][param]
            self.energy_tree.add_parameter(key=param, value=None, type=type_value, readonly=True)

        #SYNC TAB
        sync_parameters = list(self.xml_parameters['SYNC'].keys())
        for param in sync_parameters:
            type_value = self.xml_types['SYNC'][param]
            self.sync_tree.add_parameter(key=param, value=None, type=type_value, readonly=True)
        
        #ONBOARD COINCIDENCES TAB
        coinc_parameters = list(self.xml_parameters['ONBOARD COINCIDENCES'].keys())
        for param in coinc_parameters:
            try:
                units = self.xml_units['ONBOARD COINCIDENCES'][param]
            except:
                units = None
            if units == None:
                suffixOn = False
            else:
                suffixOn = True            
            type_value = self.xml_types['ONBOARD COINCIDENCES'][param]
            self.coinc_tree.add_parameter(key=param, value=None, type=type_value, suffix=units, siPrefix=suffixOn, readonly=True)

        #MISCELLANEOUS TAB
        misc_parameters = list(self.xml_parameters['MISC'].keys())
        for param in misc_parameters:
            type_value = self.xml_types['MISC'][param]
            self.misc_tree.add_parameter(key=param, value=None, type=type_value, readonly=True)
        


        #Tab Area for the plotting settings and the file transformation settings
        self.TabArea = self.GRAPH.place_object(_g.TabArea(name+'_tabs_settings.txt'), alignment=0).set_width(300*self.ratio)

        #Plot settings tab
        self.TabSettings = self.TabArea.add_tab('Plot Settings')
        self.settings = self.TabSettings.place_object(_g.TreeDictionary(name+'_settings.txt', name), 0, 0, alignment=0).set_width(275*self.ratio)

        #Title
        self.settings.add_parameter(key='Plot Settings/Title', value='Graph title', tip='Title of the graph')
        self.settings.connect_signal_changed('Plot Settings/Title', self.__title__)

        #Legend
        self.settings.add_parameter(key='Plot Settings/Legend', value=False, tip='Turns on or off the legend.')
        self.settings.connect_signal_changed('Plot Settings/Legend', self.__legend__)

        #Grid
        self.settings.add_parameter(key='Plot Settings/Grid/x', value=False, tip='Turns on the grid for the x axis.')
        self.settings.add_parameter(key='Plot Settings/Grid/y', value=False, tip='Turns on the grid for the y axis.')
        self.settings.connect_signal_changed('Plot Settings/Grid/x', self.__grid__)
        self.settings.connect_signal_changed('Plot Settings/Grid/y', self.__grid__)

        #Axes label
        self.settings.add_parameter(key='Plot Settings/Axes label/x', value='x', tip='Label of the x axis')
        self.settings.connect_signal_changed('Plot Settings/Axes label/x', self.__ax_labels__)
        self.settings.add_parameter(key='Plot Settings/Axes label/y', value='y', tip='Label of the y axis')
        self.settings.connect_signal_changed('Plot Settings/Axes label/y', self.__ax_labels__)

        #Axes limits
        self.settings.add_parameter(key='Plot Settings/Axes limits/x min', value=0, type='int', step=1, tip='Minimum value for the x axis')
        self.settings.add_parameter(key='Plot Settings/Axes limits/x max', value=10, type='int', step=1, tip='Maximum value for the x axis')
        self.settings.connect_signal_changed('Plot Settings/Axes limits/x min', self.__xlim__)        
        self.settings.connect_signal_changed('Plot Settings/Axes limits/x max', self.__xlim__)        
        self.settings.add_parameter(key='Plot Settings/Axes limits/y min', value=0, type='int', step=1, tip='Minimum value for the y axis')
        self.settings.add_parameter(key='Plot Settings/Axes limits/y max', value=10, type='int', step=1, tip='Maximum value for the y axis')
        self.settings.connect_signal_changed('Plot Settings/Axes limits/y min', self.__ylim__)        
        self.settings.connect_signal_changed('Plot Settings/Axes limits/y max', self.__ylim__)        

        #Log scale
        self.settings.add_parameter(key='Plot Settings/Log scale/x', value=False, tip='Turns on or off the log scale for the x axis.')
        #self.settings.connect_signal_changed('Plot Settings/Log scale/x', self.__log__)
        self.settings.add_parameter(key='Plot Settings/Log scale/y', value=False, tip='Turns on or off the log scale for the y axis.')
        #self.settings.connect_signal_changed('Plot Settings/Log scale/y', self.__log__)

        #Line color and fill color
        self.settings.add_parameter(key='Plot Settings/Line Color/Red', value=0, bounds=(0,255), default=255)
        self.settings.connect_signal_changed('Plot Settings/Line Color/Red', self.__linecolor__)

        self.settings.add_parameter(key='Plot Settings/Line Color/Green', value=0, bounds=(0,255))
        self.settings.connect_signal_changed('Plot Settings/Line Color/Green', self.__linecolor__)

        self.settings.add_parameter(key='Plot Settings/Line Color/Blue', value=0, bounds=(0,255))
        self.settings.connect_signal_changed('Plot Settings/Line Color/Blue', self.__linecolor__)

        self.settings.add_parameter(key='Plot Settings/Line Color/Alpha', value=0, bounds=(0,100), default=100)
        self.settings.connect_signal_changed('Plot Settings/Line Color/Alpha', self.__linecolor__)

        self.settings.add_parameter(key='Plot Settings/Fill Color/Red', value=0, bounds=(0,255))
        self.settings.connect_signal_changed('Plot Settings/Fill Color/Red', self.__fillcolor__)

        self.settings.add_parameter(key='Plot Settings/Fill Color/Green', value=0, bounds=(0,255))
        self.settings.connect_signal_changed('Plot Settings/Fill Color/Green', self.__fillcolor__)

        self.settings.add_parameter(key='Plot Settings/Fill Color/Blue', value=0, bounds=(0,255), default=255)
        self.settings.connect_signal_changed('Plot Settings/Fill Color/Blue', self.__fillcolor__)
        
        self.settings.add_parameter(key='Plot Settings/Fill Color/Alpha', value=0, bounds=(0,100), default=50)
        self.settings.connect_signal_changed('Plot Settings/Fill Color/Alpha', self.__fillcolor__)

        #Color in hex
        self.settings.add_parameter('Plot Settings/Line Color/HEX CODE', value='000000')
        self.settings.connect_signal_changed('Plot Settings/Line Color/HEX CODE', self.__hexline__)
        self.settings.add_parameter('Plot Settings/Fill Color/HEX CODE', value='000000')
        self.settings.connect_signal_changed('Plot Settings/Fill Color/HEX CODE', self.__hexfill__)



        #Graph Area
        self.TabAreaData = self.GRAPH.place_object(_g.TabArea(name+'_tabs_data.txt'), 1, 0, alignment=0)
        self.TabData = self.TabAreaData.add_tab('Data')
        self.TabDataGT = self.TabData.place_object(_g.GridLayout(False)).set_height(35*self.ratio)
        self.TabData.new_autorow()
        self.TabDataBT = self.TabData.place_object(_g.GridLayout(False), alignment=0)

        #Buttons for the different graphs types
        self.EH_btn = self.TabDataGT.place_object(_g.Button(' ', checkable=True, tip='Energy Histogram')).set_width(25*self.ratio).set_height(25*self.ratio)
        self.EH_btn.set_style_unchecked(style='image: url(Images/EnergyHist.png)')
        self.EH_btn.set_style_checked(style='image: url(Images/EnergyHist.png)')
        self.EH_btn.signal_toggled.connect(self.__EH_toggled__)

        self.PSD_btn = self.TabDataGT.place_object(_g.Button(' ', checkable=True, tip='PSD Histogram')).set_width(25*self.ratio).set_height(25*self.ratio)
        self.PSD_btn.set_style_unchecked(style='image: url(Images/PSDHist.png)')
        self.PSD_btn.set_style_checked(style='image: url(Images/PSDHist.png)')
        self.PSD_btn.signal_toggled.connect(self.__PSD_toggled__)

        self.Time_btn = self.TabDataGT.place_object(_g.Button(' ', checkable=True, tip='Time Histogram')).set_width(25*self.ratio).set_height(25*self.ratio)
        self.Time_btn.set_style_unchecked(style='image: url(Images/TimeHist.png)')
        self.Time_btn.set_style_checked(style='image: url(Images/TimeHist.png)')
        self.Time_btn.signal_toggled.connect(self.__Time_toggled__)

        self.TOF_btn = self.TabDataGT.place_object(_g.Button(' ', checkable=True, tip='TOF Histogram')).set_width(25*self.ratio).set_height(25*self.ratio)
        self.TOF_btn.set_style_unchecked(style='image: url(Images/TOFHist.png)')
        self.TOF_btn.set_style_checked(style='image: url(Images/TOFHist.png)')
        self.TOF_btn.signal_toggled.connect(self.__TOF_toggled__)

        self.PSDvsE_btn = self.TabDataGT.place_object(_g.Button(' ', checkable=True, tip='PSD vs Energy Histogram')).set_width(25*self.ratio).set_height(25*self.ratio)
        self.PSDvsE_btn.set_style_unchecked(style='image: url(Images/PSDvsEnergyHist.png)')
        self.PSDvsE_btn.set_style_checked(style='image: url(Images/PSDvsEnergyHist.png)')
        self.PSDvsE_btn.signal_toggled.connect(self.__PSDvsE_toggled__)

        self.MCS_btn = self.TabDataGT.place_object(_g.Button(' ', checkable=True, tip='MCS Graph')).set_width(25*self.ratio).set_height(25*self.ratio)
        self.MCS_btn.set_style_unchecked(style='image: url(Images/MCS Graph.png)')
        self.MCS_btn.set_style_checked(style='image: url(Images/MCS Graph.png)')
        self.MCS_btn.signal_toggled.connect(self.__MSC_toggled__)

        #Graph
        self.data = self.TabDataBT.place_object(_g.DataboxSaveLoad(file_type='.txt', autosettings_path=name+'_data.txt'), alignment=0, column_span=3).set_width(700*self.ratio)
        self.data.enable_save()
        self.TabDataBT.new_autorow()
        self.PlotArea = self.TabDataBT.place_object(_pg.PlotWidget(), alignment=0, column_span=3)
        self.PLT = self.PlotArea.getPlotItem()
        
        self.ROI = _pg.LinearRegionItem([0,10])
        self.ROI.sigRegionChanged.connect(self.__update_ROI__)


        #RESULTS TAB
        self.TabResults = self.TabAreaData.add_tab('Results')
        self.TOP_ROW = self.TabResults.place_object(_g.GridLayout(False)).set_height(50*self.ratio)

        self.calculate = self.TOP_ROW.place_object(_g.Button(' ', tip='Calculate Results'), 0, 0).set_width(45*self.ratio).set_height(45*self.ratio)
        self.calculate.set_style_unchecked(style='image: url(Images/Calculate.png)')
        self.calculate.signal_clicked.connect(self.__calculate__)
        
        self.TabResults.new_autorow()
        self.data_res = self.TOP_ROW.place_object(_g.DataboxSaveLoad(file_type='.txt', autosettings_path=name+'_datares.txt'), 1, 0, alignment=0)#.set_width(665*self.ratio).set_height(45*self.ratio)
        self.data_res.enable_save()
        
        self.PlotAreaResults = self.TabResults.place_object(_pg.PlotWidget(), alignment=0, column_span=2)
        self.PLT_RES = self.PlotAreaResults.getPlotItem()
        self.PLT_RES.sigXRangeChanged.connect(self.__update_plot__)
        self.TabResults.new_autorow()
        self.results = self.TabResults.place_object(_g.TreeDictionary(name+'_results.txt', name), alignment=0, column_span=2)
        
        #Range for the calculation
        # self.results.add_parameter('Range for calculation/Minimum', float(self.settings['Plot Settings/Axes limits/x min']))
        self.results.add_parameter("Begin", round(self.ROI.getRegion()[0], 2), readonly=True)
        self.results.add_parameter("End", round(self.ROI.getRegion()[1], 2), readonly=True)
        self.results.add_parameter("Centroid", type='str', readonly=True, tip="Mean of the gaussian distribution.")
        self.results.add_parameter("Sigma", type='str', readonly=True, tip="Spread of the gaussian distribution.")
        self.results.add_parameter("χ2", type='str', readonly=True, tip="Reduced χ2 from the gaussian fit.")
        self.results.add_parameter("FWHM", type='str', readonly=True, tip="Full width at half maximum.")
        self.results.add_parameter("FWTM", type='str', readonly=True, tip="Full width at tenth of maximum.")
        self.results.add_parameter("Resolution", type='str', readonly=True, tip="Resolution of the peak.")

        
        #Set the default tab opened to the CoMPASS settings tab:
        self.GeneralTabArea.set_current_tab(0)
        self.TabArea.set_current_tab(0)
        self.TabAreaData.set_current_tab(0)
        #self.filesetlabel = self.TabFileSettings.place_object(_g.Label('Select a folder please.'))

        self.__linecolor__()#Loads the line color for the first time.
        self.__fillcolor__()#Loads the fill color for the first time.

        _s.settings['dark_theme_qt'] = _dd.isDark()
        self.PlotArea.setBackground('white') if _dd.isLight() else self.PlotArea.setBackground('black')
        self.PlotAreaResults.setBackground('white') if _dd.isLight() else self.PlotAreaResults.setBackground('black')
        self.__load_all__()
        if show:    self.window.show(block)


    def __get_screen_resolution__(self):
        user32 = _ct.windll.user32
        user32.SetProcessDPIAware()
        return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))

    def __transform__(self, *a):
        ch0_state = self.ch0.is_checked()
        ch1_state = self.ch1.is_checked()
        ch2_state = self.ch2.is_checked()
        ch3_state = self.ch3.is_checked()
     
        ch0_filepath = self.folder_containing_root + '\\' + self.files[0]
        ch1_filepath = self.folder_containing_root + '\\' + self.files[1]
        ch2_filepath = self.folder_containing_root + '\\' + self.files[2]
        ch3_filepath = self.folder_containing_root + '\\' + self.files[3]
        
        if ch0_state:
            self.__transform_root_to_excel__(ch0_filepath, self.tree)
        if ch1_state:
            self.__transform_root_to_excel__(ch1_filepath, self.tree)
        if ch2_state:
            self.__transform_root_to_excel__(ch2_filepath, self.tree)
        if ch3_state:
            self.__transform_root_to_excel__(ch3_filepath, self.tree)

    def __EH_toggled__(self, *a):
        self.PSD_btn.set_checked(False)
        self.Time_btn.set_checked(False)
        self.TOF_btn.set_checked(False)
        self.PSDvsE_btn.set_checked(False)
        self.MCS_btn.set_checked(False)

        self.settings['Plot Settings/Title'] = 'Energy Histogram'
        self.settings['Plot Settings/Axes limits/x min'] = 0
        try:
            self.settings['Plot Settings/Axes limits/x max'] = self.spectra_tree['Energy N channels']
        except:
            self.settings['Plot Settings/Axes limits/x max'] = 4096            
        self.settings['Plot Settings/Axes limits/y min'] = 0
        self.settings['Plot Settings/Axes limits/y max'] = 5000
        self.settings['Plot Settings/Axes label/x'] = 'ADC bins'
        self.settings['Plot Settings/Axes label/y'] = 'Counts'
        self.__load_all__()
    
    def __PSD_toggled__(self, *a):
        self.EH_btn.set_checked(False)
        self.Time_btn.set_checked(False)
        self.TOF_btn.set_checked(False)
        self.PSDvsE_btn.set_checked(False)
        self.MCS_btn.set_checked(False)

        self.settings['Plot Settings/Title'] = 'PSD Histogram'
        self.settings['Plot Settings/Axes limits/x min'] = 0
        self.settings['Plot Settings/Axes limits/x max'] = 1
        
        self.settings['Plot Settings/Axes limits/y min'] = 0
        self.settings['Plot Settings/Axes limits/y max'] = 5000
        self.settings['Plot Settings/Axes label/x'] = 'ADC bins'
        self.settings['Plot Settings/Axes label/y'] = 'Counts'
        self.__load_all__()

    def __Time_toggled__(self, *a):
        self.EH_btn.set_checked(False)
        self.PSD_btn.set_checked(False)
        self.TOF_btn.set_checked(False)
        self.PSDvsE_btn.set_checked(False)
        self.MCS_btn.set_checked(False)

        self.settings['Plot Settings/Title'] = 'Time Histogram'
        self.settings['Plot Settings/Axes limits/x min'] = self.spectra_tree['Time intervals Tmin']
        self.settings['Plot Settings/Axes limits/x max'] = self.spectra_tree['Time intervals Tmax']
        
        self.settings['Plot Settings/Axes limits/y min'] = 0
        self.settings['Plot Settings/Axes limits/y max'] = 5000
        self.settings['Plot Settings/Axes label/x'] = 'Time (s)'
        self.settings['Plot Settings/Axes label/y'] = 'Counts'
        self.__load_all__()

    def __TOF_toggled__(self, *a):
        self.EH_btn.set_checked(False)
        self.PSD_btn.set_checked(False)
        self.Time_btn.set_checked(False)
        self.PSDvsE_btn.set_checked(False)
        self.MCS_btn.set_checked(False)

        self.settings['Plot Settings/Title'] = 'TOF Histogram'
        try:
            self.settings['Plot Settings/Axes limits/x min'] = self.spectra_tree['Start-stop Δt Tmin']
            self.settings['Plot Settings/Axes limits/x max'] = self.spectra_tree['Start-stop Δt Tmax']
        except:
            self.settings['Plot Settings/Axes limits/x min'] = 0
            self.settings['Plot Settings/Axes limits/x max'] = 8192
        self.settings['Plot Settings/Axes limits/y min'] = 0
        self.settings['Plot Settings/Axes limits/y max'] = 5000
        self.settings['Plot Settings/Axes label/x'] = 'Δt (ns)'
        self.settings['Plot Settings/Axes label/y'] = 'Counts'
        self.__load_all__()

    def __PSDvsE_toggled__(self, *a):
        self.EH_btn.set_checked(False)
        self.PSD_btn.set_checked(False)
        self.Time_btn.set_checked(False)
        self.TOF_btn.set_checked(False)
        self.MCS_btn.set_checked(False)

        self.settings['Plot Settings/Title'] = 'PSD vs Energy Histogram'
        self.settings['Plot Settings/Axes limits/x min'] = 0
        try:
            self.settings['Plot Settings/Axes limits/x max'] = self.spectra_tree['Energy N channels']
        except:
            self.settings['Plot Settings/Axes limits/x max'] = 4096
        self.settings['Plot Settings/Axes limits/y min'] = 0
        self.settings['Plot Settings/Axes limits/y max'] = 1
        self.settings['Plot Settings/Axes label/x'] = 'ADC bins'
        self.settings['Plot Settings/Axes label/y'] = 'PSD'
        self.__load_all__()

    def __MSC_toggled__(self, *a):
        self.EH_btn.set_checked(False)
        self.PSD_btn.set_checked(False)
        self.Time_btn.set_checked(False)
        self.TOF_btn.set_checked(False)
        self.PSDvsE_btn.set_checked(False)

        self.settings['Plot Settings/Title'] = 'MCS Graph'
        self.settings['Plot Settings/Axes limits/x min'] = 0
        self.settings['Plot Settings/Axes limits/x max'] = 500
        self.settings['Plot Settings/Axes limits/y min'] = 0
        self.settings['Plot Settings/Axes limits/y max'] = 1
        self.settings['Plot Settings/Axes label/x'] = 'Elapsed time (s)'
        self.settings['Plot Settings/Axes label/y'] = 'Event rate (cps)'
        self.__load_all__()


    def __plot__(self, *a):
        if self.PSDvsE_BEFORE:
            try:
                self.PLT.removeItem(self.image)
                self.bar.close()
            except:
                print('Did not remove any image.')
            
            self.PLT.getViewBox().setLimits(xMin=-_np.Inf, xMax=_np.Inf,    yMin=_np.Inf, yMax=_np.Inf)
            

        if self.EH_btn.is_checked():
            self.PSDvsE_BEFORE = False
            data = _root_reader.__energyhist__(self, self.files_in_use[0], int(self.spectra_tree['Energy N channels']), tree=self.tree)

            self.data['x'], self.data['y'], self.root_data = data

            self.__load_all__()
            curve_name = f"{self.settings['Plot Settings/Title']}-{self.file_settings['Files Settings/Folder']}"

            self.PLT.plot(self.data['x'], self.data['y'], stepMode='center', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)
            self.PLT_RES.plot(self.data['x'], self.data['y'], stepMode='center', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)

        elif self.PSD_btn.is_checked():
            self.PSDvsE_BEFORE = False
            data = _root_reader.__psdhist__(self, self.files_in_use[0], int(self.spectra_tree['PSD N channels']), tree=self.tree)

            self.data['x'], self.data['y'], self.root_data = data

            self.__load_all__()
            
            curve_name = self.settings['Plot Settings/Title'] + '-' + self.file_settings['Files Settings/Folder']

            self.PLT.plot(self.data['x'], self.data['y'], stepMode='center', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)
            self.PLT_RES.plot(self.data['x'], self.data['y'], stepMode='center', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)

        elif self.Time_btn.is_checked():
            self.PSDvsE_BEFORE = False
            data = _root_reader.__timehist__(self, self.files_in_use[0], float(self.settings['Plot Settings/Axes limits/x min']), float(self.settings['Plot Settings/Axes limits/x max']), int(self.spectra_tree['Time intervals N channels']), tree=self.tree)

            self.data['x'], self.data['y'], self.root_data = data
            self.__load_all__()

            curve_name = self.settings['Plot Settings/Title'] + '-' + self.file_settings['Files Settings/Folder']
            
            self.PLT.plot(self.data['x'], self.data['y'], stepMode='center', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)
            self.PLT_RES.plot(self.data['x'], self.data['y'], stepMode='center', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)

        elif self.TOF_btn.is_checked():
            self.PSDvsE_BEFORE = False
            if self.tree == "Data_F":
                data = _root_reader.__tofhist__(self, self.files_in_use[0], self.files_in_use[1], float(self.settings['Plot Settings/Axes limits/x min']), float(self.settings['Plot Settings/Axes limits/x max']), int(self.spectra_tree['Start-stop Δt N channels']), tree=self.tree)

                self.data['x'] = data[0]
                self.data['y'] = data[1]

                self.root_data = data[2]

                self.__load_all__()
                curve_name = self.settings['Plot Settings/Title'] + '-' + self.file_settings['Files Settings/Folder']
            
                self.PLT.plot(self.data['x'], self.data['y'], stepMode='center', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)
                self.PLT_RES.plot(self.data['x'], self.data['y'], stepMode='center', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)

            # if self.tree == "Data_R":
                # data = _root_reader.__CPPTOF__(self, self.files_in_use[0], self.files_in_use[1])
        elif self.PSDvsE_btn.is_checked():
            self.PSDvsE_BEFORE = True
            self.__clear__()
            data = _root_reader.__PSDvsE__(self, self.files_in_use[0], float(self.settings['Plot Settings/Axes limits/x min']), float(self.settings['Plot Settings/Axes limits/x max']), int(self.spectra_tree['Energy N channels']), int(self.spectra_tree['PSD N channels']), tree=self.tree)
            
            tr = QtGui.QTransform()
            tr.scale(1, 1/self.spectra_tree['PSD N channels'])

            self.image = _pg.ImageItem(image=data)
            self.image.setTransform(tr)
            self.PLT.addItem(self.image)
            cm = _pg.colormap.getFromMatplotlib('white_turbo')
            print(_np.sort(data.flatten())[-20:])
            self.bar = _pg.ColorBarItem(values=(0,20),cmap=cm)
            self.bar.setImageItem(self.image,insert_in=self.PLT)
            range_ = self.PLT.getViewBox().viewRange()
            self.PLT.getViewBox().setLimits(xMin=range_[0][0],xMax=range_[0][1], yMin=range_[1][0], yMax=range_[1][1])


        elif self.MCS_btn.is_checked():
            self.PSDvsE_BEFORE = False
            data = _root_reader.__MCSgraph__(self, self.files_in_use[0], tree=self.tree)

            self.data['x'] = data[0]
            self.data['y'] = data[1]

            self.root_data = data[2]

            self.__load_all__()
            curve_name = self.settings['Plot Settings/Title'] + '-' + self.file_settings['Files Settings/Folder']

            # curve = _pg.PlotCurveItem(self.data['x'], self.data['y'], fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)
            # self.PLT.addItem(curve)
            self.PLT.plot(self.data['x'], self.data['y'], brush=self.brush, pen=self.pen, name=curve_name)
            self.PLT_RES.plot(self.data['x'], self.data['y'], stepMode='left', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)
    
    def __clear__(self, *a):
        """
        Clears the graph.
        """
        self.PLT.clear()
        self.PLT_RES.clear()

    def __save_image__(self, *a):
        """
        Saves an image of the graph in the SCREENSHOTS folder.
        """
        exporter = _export.ImageExporter(self.PlotArea.plotItem)
        exporter.export(self.folder_path+'\SCREENSHOTS\\' + self.settings['Plot Settings/Title'] +'.png')
    
    def __select_ROI__(self, *a):
        if self.select.is_checked():
            self.PLT.addItem(self.ROI)
        else:
            self.PLT.removeItem(self.ROI)
        self.ROI.setRegion((0,50))

    def __update_ROI__(self, *a):
        self.lower_bound, self.upper_bound = self.ROI.getRegion()
        self.PLT_RES.setXRange(*self.ROI.getRegion(), padding=0)
        data = _np.array(self.root_data)
        # values = data[(self.lower_bound <= self.data['x']) & (self.data['x'] <= self.upper_bound)]
        indexes = _np.where((self.lower_bound<=self.data['x']) & (self.data['x']<=self.upper_bound))[0]
        if indexes[-1] == self.settings['Plot Settings/Axes limits/x max']:
            indexes = _np.delete(indexes, -1)
        values_range = self.data['y'][indexes]
        min_range = 0
        max_range = max(values_range)
        
        self.data_res['x'] = self.data['x'][indexes]
        self.data_res['y'] = self.data['y'][indexes]

        self.PLT_RES.setYRange(min_range, max_range)

    def __update_plot__(self, *a):
        try:
            indexes = _np.where((self.lower_bound<=self.data['x']) & (self.data['x']<=self.upper_bound))[0]
            self.data_res['x'] = self.data['x'][indexes]
            self.data_res['y'] = self.data['y'][indexes]
        except:
            print("Could not set the data")
        self.ROI.setRegion(self.PLT_RES.getViewBox().viewRange()[0])

    def __calculate__(self, *a):
        self.results['Begin'] = round(self.lower_bound,2)
        self.results['End'] = round(self.upper_bound,2)
        
        if self.EH_btn.is_checked():
            indexes = _np.where((self.lower_bound<=self.data['x']) & (self.data['x']<=self.upper_bound))[0]
            x_values = self.data['x'][indexes]
            y_values = self.data['y'][indexes]
            popt, pcov = _cf(fit, x_values, _np.log(y_values))
            errors = _np.sqrt(_np.diag(pcov))
            centroid = _uf(popt[0], errors[0])
            sigma = _uf(popt[1], errors[1])
            amp = _uf(popt[2], errors[2]).evalf(_np.exp)
            
            y_e = gaussian(x_values, *popt[0:2], amp._value)

            self.results['Centroid'] = str(centroid)
            self.results['Sigma'] = str(sigma)
            self.results["χ2"] = str(chi_sqr(y_values, y_e))
            FWHM = FWAP(x_values, centroid, sigma, amp, 0.5)
            self.results['FWHM'] = str(FWHM)
            self.results['FWTM'] = str(FWAP(x_values, centroid, sigma, amp, 0.1))
            self.results['Resolution'] = str(FWHM/centroid*100)

            curve_name = f"{self.settings['Plot Settings/Title']}-{self.file_settings['Files Settings/Folder']} - Gaussian fit"

            self.PLT_RES.plot(x_values, gaussian(x_values, *popt[0:2], amp._value), pen=self.pen_fit, name=curve_name)


    def __load_all__(self, *a):
        self.__title__()
        self.__legend__()
        self.__grid__()
        self.__ax_labels__()
        self.__xlim__()
        self.__ylim__()
        #self.__log__()
        self.__linecolor__()
        self.__fillcolor__()

    def __title__(self, *a):
        """
        Sets the title of the graph.
        """
        self.PLT.setLabels(title=self.settings['Plot Settings/Title'])

    def __legend__(self, *a):
        """
        Shows the legend of the graph.
        """
        if self.settings['Plot Settings/Legend']:
            self.PLT.addLegend()
            self.PLT_RES.addLegend()

    def __grid__(self, *a):
        """
        Shows the grid of the graph for both axis.
        """
        self.PLT.showGrid(x=self.settings['Plot Settings/Grid/x'], y=self.settings['Plot Settings/Grid/y'])
        self.PLT_RES.showGrid(x=self.settings['Plot Settings/Grid/x'], y=self.settings['Plot Settings/Grid/y'])

    def __ax_labels__(self, *a):
        """
        Sets the labels of the axes of the graph.
        """
        self.PLT.setLabel(axis='left', text=self.settings['Plot Settings/Axes label/y'])
        self.PLT.setLabel(axis='bottom', text=self.settings['Plot Settings/Axes label/x'])
        self.PLT_RES.setLabel(axis='bottom', text=self.settings['Plot Settings/Axes label/x'])
        self.PLT_RES.setLabel(axis='left', text=self.settings['Plot Settings/Axes label/y'])
    
    def __xlim__(self, *a):
        """
        Sets the limits on the x axis of the graph.
        """
        self.PLT.setXRange(self.settings['Plot Settings/Axes limits/x min'], self.settings['Plot Settings/Axes limits/x max'])

    def __ylim__(self, *a):
        """
        Sets the limits on the y axis of the graph.
        """
        self.PLT.setYRange(self.settings['Plot Settings/Axes limits/y min'], self.settings['Plot Settings/Axes limits/y max'])

    def __log__(self, *a):
        """
        Sets the scale to logarithmic scale for the selected axes.
        """
        self.PLT.setLogMode(self.settings['Plot Settings/Log scale/x'], self.settings['Plot Settings/Log scale/y'])
        #PlotItem = self.PLT.getPlotItem()
        #PlotItem.setLogMode(self.settings['Plot Settings/Log scale/x'], self.settings['Plot Settings/Log scale/y'])

    def __linecolor__(self, *a):
        """
        Sets the line color by changing the Red, Green, Blue and Alpha values.
        """
        self.pen = _pg.mkPen(self.settings['Plot Settings/Line Color/Red'], self.settings['Plot Settings/Line Color/Green'], self.settings['Plot Settings/Line Color/Blue'], self.settings['Plot Settings/Line Color/Alpha'])
        # comp = complementary((self.settings['Plot Settings/Line Color/Red'], self.settings['Plot Settings/Line Color/Green'], self.settings['Plot Settings/Line Color/Blue'], self.settings['Plot Settings/Line Color/Alpha']))
        self.pen_fit = _pg.mkPen(0,0,0,100) if _dd.isLight() else _pg.mkPen(255,255,255,100)

    def __fillcolor__(self, *a):
        """
        Sets the fill color by changing the Red, Green, Blue and Alpha values.
        """
        self.brush = (self.settings['Plot Settings/Fill Color/Red'], self.settings['Plot Settings/Fill Color/Green'], self.settings['Plot Settings/Fill Color/Blue'], self.settings['Plot Settings/Fill Color/Alpha'])

    def __hexline__(self, *a):
        hex_code = self.settings['Plot Settings/Line Color/HEX CODE']
        if len(hex_code) > 6:
            hex_code = hex_code[0:6]
        red_string = ''
        green_string = ''
        blue_string = ''

        hex_values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

        red = 0
        green = 0
        blue = 0

        for index in range(0, 6):
            if index < 2:
                red_string += hex_code[index]
            if 2 <= index < 4:
                green_string += hex_code[index]
            if 4 <= index < len(hex_code):
                blue_string += hex_code[index]

        try:
            red = int(red_string, 16)
        except:
            for value in hex_code:
                if value in hex_values:
                    continue
                else:
                    self.settings['Plot Settings/Line Color/HEX CODE'] = hex_code.replace(value, '0')
        hex_code = self.settings['Plot Settings/Line Color/HEX CODE']
        try:
            green = int(green_string, 16)
        except:
            for value in hex_code[2:4]:
                if value in hex_values:
                    continue
                else:
                    self.settings['Plot Settings/Line Color/HEX CODE'] = hex_code.replace(value, '0')
        hex_code = self.settings['Plot Settings/Line Color/HEX CODE']
        try:
            blue = int(blue_string, 16)
        except:
            for value in hex_code[4:6]:
                if value in hex_values:
                    continue
                else:
                    self.settings['Plot Settings/Line Color/HEX CODE'] = hex_code.replace(value, '0')

        self.settings['Plot Settings/Line Color/Red'] = red
        self.settings['Plot Settings/Line Color/Green'] = green
        self.settings['Plot Settings/Line Color/Blue'] = blue

    def __hexfill__(self, *a):
        hex_code = self.settings['Plot Settings/Fill Color/HEX CODE']
        if len(hex_code) > 6:
            hex_code = hex_code[0:6]
        red_string = ''
        green_string = ''
        blue_string = ''

        hex_values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C', 'D', 'E', 'F']

        red = 0
        green = 0
        blue = 0

        for index in range(0, 6):
            if index < 2:
                red_string += hex_code[index]
            if 2 <= index < 4:
                green_string += hex_code[index]
            if 4 <= index < len(hex_code):
                blue_string += hex_code[index]

        try:
            red = int(red_string, 16)
        except:
            for value in hex_code:
                if value in hex_values:
                    continue
                else:
                    self.settings['Plot Settings/Fill Color/HEX CODE'] = hex_code.replace(value, '0')
        hex_code = self.settings['Plot Settings/Fill Color/HEX CODE']
        try:
            green = int(green_string, 16)
        except:
            for value in hex_code[2:4]:
                if value in hex_values:
                    continue
                else:
                    self.settings['Plot Settings/Fill Color/HEX CODE'] = hex_code.replace(value, '0')
        hex_code = self.settings['Plot Settings/Fill Color/HEX CODE']
        try:
            blue = int(blue_string, 16)
        except:
            for value in hex_code[4:6]:
                if value in hex_values:
                    continue
                else:
                    self.settings['Plot Settings/Fill Color/HEX CODE'] = hex_code.replace(value, '0')

        self.settings['Plot Settings/Fill Color/Red'] = red
        self.settings['Plot Settings/Fill Color/Green'] = green
        self.settings['Plot Settings/Fill Color/Blue'] = blue

    def __search_folder__(self, *a):
        folder_path = _fd.askdirectory(initialdir='/')
        path = _os.path.realpath(folder_path)
        folder_name = path.split('\\')[-1]
        #self.folder_label.set_text(folder_name)
        #self.filesetlabel.set_text('')
        self.folder_path = path
        allfiles = _os.listdir(path)
        for file in allfiles:
            if file.endswith(".xml"):
                self.compass_settings = file
            if file.endswith(".info"):
                self.run_info_file = file
        
        self.__settings_folder_changed__()#Loads the files for the first time.
        

    def __getfiles__(self, folder_path):
        allfiles = _os.listdir(folder_path)
        root_files = []
        for file in allfiles:
            if file.endswith(".root"):
                root_files.append(file)

        return root_files


    def __load_channel_settings__(self, tree_dict, param_tree, key, *a):
        key_1 = key
        key_2 = key
        if key == "ENERGY CALIBRATION":
            key_1 = "ENERGY_CALIBRATION"
            key_2 = key
        if key == "ONBOARD COINCIDENCES":
            key_1 = "HARDWARE_COINCIDENCE"
            key_2 = key
        if key == "SPECTRA":
            param_keys = param_tree.keys()
            if tree_dict["Channel"] == "BOARD":
                info = self.board_settings
            if tree_dict["Channel"] == "CH0":
                info = self.xml_info.get_chn_parameters(0)
            if tree_dict["Channel"] == "CH1":
                info = self.xml_info.get_chn_parameters(1)
            if tree_dict["Channel"] == "CH2":
                info = self.xml_info.get_chn_parameters(2)
            if tree_dict["Channel"] == "CH3":
                info = self.xml_info.get_chn_parameters(3)
            for param in param_keys:
                if self.xml_types[key_1][param] == 'str':
                    param_tree[param] = info[key_2][self.xml_parameters[key_1][param]][0:-2]
                else:
                    param_tree[param] = info[key_2][self.xml_parameters[key_1][param]]
 
        else:
            param_keys = param_tree.keys()
            if tree_dict["Channel"] == "BOARD":
                info = self.board_settings
            if tree_dict["Channel"] == "CH0":
                info = self.xml_info.get_chn_parameters(0)
            if tree_dict["Channel"] == "CH1":
                info = self.xml_info.get_chn_parameters(1)
            if tree_dict["Channel"] == "CH2":
                info = self.xml_info.get_chn_parameters(2)
            if tree_dict["Channel"] == "CH3":
                info = self.xml_info.get_chn_parameters(3)
            for param in param_keys:
                param_tree[param] = info[key_1][self.xml_parameters[key_2][param]]
            

    def __settings_folder_changed__(self, *a):
        """
        Reloads the files from the chosen folder.
        """
        self.folder_containing_root = self.folder_path + '\\' + self.file_settings['Files Settings/Folder']
        
        #XML AND INFO FILES
        self.path_compass_settings = self.folder_path + '\\' + self.compass_settings
        self.path_run_info_file = self.folder_path + '\\' + self.run_info_file
        info = InfoParser(self.path_run_info_file)
        self.run_info_data = info.get_run_info()
        self.xml_info = XMLParser(self.path_compass_settings)
        board_props = self.xml_info.get_board_properties()
        self.board_settings = self.xml_info.get_parameters()
        #RUN INFO
        self.run_info["Run ID"] = self.run_info_data[0]
        self.run_info["Start Time"] = self.run_info_data[1]
        self.run_info["Stop Time"] = self.run_info_data[2]
        self.run_info["Run Time"] = self.run_info_data[3]

        #BOARD INFO
        self.board_1['Name'] = board_props[0]
        self.board_1['ADC bits'] = board_props[3]
        self.board_1['ROC firmware'] = board_props[6]
        self.board_1['Link'] = board_props[8]

        self.board_2['ID'] = board_props[1]
        self.board_2['Sampling rate  '] = board_props[4]
        self.board_2['AMC firmware'] = board_props[7]

        self.board_3['Model'] = board_props[2]
        self.board_3['DPP type'] = board_props[5]
        self.board_3['Enable'] = board_props[9]

        #SETTINGS INFO
        #INPUT TAB
        self.__load_channel_settings__(self.input_ch, self.input_tree, "INPUT")

        #DISCRIMINATOR TAB
        self.__load_channel_settings__(self.disc_ch, self.disc_tree, "DISCRIMINATOR")

        #QDC TAB
        self.__load_channel_settings__(self.qdc_ch, self.qdc_tree, "QDC")

        #SPECTRA TAB
        self.__load_channel_settings__(self.spectra_ch, self.spectra_tree, "SPECTRA")

        #REJECTIONS TAB
        self.__load_channel_settings__(self.rejection_ch, self.rejection_tree, "REJECTIONS")

        #ENERGY CALIBRATION TAB
        self.__load_channel_settings__(self.energy_ch, self.energy_tree, "ENERGY CALIBRATION")

        #SYNC TAB
        self.__load_channel_settings__(self.sync_ch, self.sync_tree, "SYNC")

        #ONBOARD COINCIDENCE TAB
        self.__load_channel_settings__(self.coinc_ch, self.coinc_tree, "ONBOARD COINCIDENCES")

        #MISCELLANEOUS TAB
        self.__load_channel_settings__(self.misc_ch, self.misc_tree, "MISC")

        self.files = self.__getfiles__(self.folder_containing_root)
        # print(self.files)
        if self.file_settings['Files Settings/Folder'] == 'FILTERED':
            self.tree = 'Data_F'
        elif self.file_settings['Files Settings/Folder'] == 'UNFILTERED':
            self.tree = 'Data'
        elif self.file_settings['Files Settings/Folder'] == 'RAW':
            self.tree = 'Data_R'

        self.__channel_buttons__()

    def __reload_channels__(self, *a):
        self.__load_channel_settings__(self.input_ch, self.input_tree, "INPUT")
        self.__load_channel_settings__(self.disc_ch, self.disc_tree, "DISCRIMINATOR")
        self.__load_channel_settings__(self.qdc_ch, self.qdc_tree, "QDC")
        self.__load_channel_settings__(self.spectra_ch, self.spectra_tree, "SPECTRA")
        self.__load_channel_settings__(self.rejection_ch, self.rejection_tree, "REJECTIONS")
        self.__load_channel_settings__(self.energy_ch, self.energy_tree, "ENERGY CALIBRATION")
        self.__load_channel_settings__(self.sync_ch, self.sync_tree, "SYNC")
        self.__load_channel_settings__(self.coinc_ch, self.coinc_tree, "ONBOARD COINCIDENCES")
        self.__load_channel_settings__(self.misc_ch, self.misc_tree, "MISC")
                        
    def __channel_buttons__(self, *a): 
        ch0_state = self.ch0.is_checked()
        ch1_state = self.ch1.is_checked()
        ch2_state = self.ch2.is_checked()
        ch3_state = self.ch3.is_checked()
     
        states = [ch0_state, ch1_state, ch2_state, ch3_state]
        all_labels = [self.xml_info.get_ch_label(i) for i in range(0,4)]
        labels = []
        for label in all_labels:
            if label[1] == "CH":
                labels.append(label[1]+label[0])
            else:
                labels.append(label[1])
        chns_labels = {}
        for index, label in enumerate(labels):
            chns_labels[index] = label
        # print(chns_labels)
        buttons_files = {}
        for file in self.files:
            for label in labels:
                if label in file:
                    buttons_files[label] = file
        # print(self.tree)
        # print(buttons_files)

        ch0_filepath = self.folder_containing_root + '\\' + buttons_files[chns_labels[0]]
        ch1_filepath = self.folder_containing_root + '\\' + buttons_files[chns_labels[1]]
        ch2_filepath = self.folder_containing_root + '\\' + buttons_files[chns_labels[2]]
        ch3_filepath = self.folder_containing_root + '\\' + buttons_files[chns_labels[3]]

        paths = [ch0_filepath, ch1_filepath, ch2_filepath, ch3_filepath]

        self.files_in_use = []
        for i in range(4):
            if states[i]:
                self.files_in_use.append(paths[i])

        if ch0_state:
            self.file_label.set_text('CH0')

            if ch1_state:
                self.file_label.set_text('CH0&CH1')
                
                if ch2_state:
                    self.file_label.set_text('CH0&CH1&CH2')
                    if ch3_state:
                        self.file_label.set_text('CH0&CH1&CH2&CH3')
                else:
                    if ch3_state:
                        self.file_label.set_text('CH0&CH1&CH3')
            else:
                if ch2_state:
                    self.file_label.set_text('CH0&CH2')
                    if ch3_state:
                        self.file_label.set_text('CH0&CH2&CH3')
                else:
                    if ch3_state:
                        self.file_label.set_text('CH0&CH3')
        else:
            if ch1_state:
                self.file_label.set_text('CH1')
                if ch2_state:
                    self.file_label.set_text('CH1&CH2')
                    if ch3_state:
                        self.file_label.set_text('CH1&CH2&CH3')
                else:
                    if ch3_state:
                        self.file_label.set_text('CH1&CH3')
            else:
                if ch2_state:
                    self.file_label.set_text('CH2')
                    if ch3_state:
                        self.file_label.set_text('CH2&CH3')
                else:
                    if ch3_state:
                        self.file_label.set_text('CH3')
                    else:
                        self.file_label.set_text('No file selected')


if __name__ == '__main__':
    module_list = ['cppimport', 'pybind11', 'uproot', 'pyqtgraph=0.12.4', 'darkdetect', 'numpy', 'pandas','PyQt5']
    print(bcolors.WARNING + "Please make sure that the following modules are installed on your machine." + bcolors.ENDC)
    for module in module_list:
        if module != module_list[-1]:
            print(module, end=', ')
        else:
            print(module)
    print(bcolors.WARNING + "Also note that you can use raw ROOT files directly to calculate the TOF." + bcolors.ENDC)
    time.sleep(2)
    running_from_main = True
    self = GUI()