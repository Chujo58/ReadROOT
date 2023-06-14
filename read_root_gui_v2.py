#----------------------------------------------------------------------------
# Created by : Chloé Legué
# Current version date : 2023/05
# Version = 2.0
#----------------------------------------------------------------------------
"""
This code was made for the coincidence experiment at McGill University. 

The code allows the user to choose a folder containing the results saved from the CoMPASS software from CAEN. This code should be used with the CAEN DT5751, or any other digitizer from CAEN that work in the same way.

This code is able to reproduce the important graphs that the CoMPASS software makes like MCS Graph, Energy Histogram and TOF Histogram. Other graphs can be added if needed.
"""
#----------------------------------------------------------------------------
# Imports
import os as os
import sys as sys
#----------------------------------------------------------------------------
# Other imports 
from . import read_root
root_reader_v1 = read_root._root_reader
root_reader = read_root.root_reader_v2
from . import XML_Parser
InfoParser = XML_Parser.InfoParser
XMLParser = XML_Parser.XMLParser
from . import icon_label
IconLabel = icon_label.IconLabel
new_size = IconLabel.new_icon_size(35)
IconLabel.IconSize = new_size
import spinmob as s
import spinmob.egg as egg
import numpy as np
import uproot as ur
import pandas as pd
import tkinter.filedialog as fd
import pyqtgraph as pg
import ctypes as ct
import pyqtgraph.exporters as export
import darkdetect as dd
import re
from PyQt5 import QtGui, QtWidgets, QtCore
import time
from scipy.optimize import curve_fit as cf
from . import ErrorPropagation as ep
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm
import superqt, time

g = egg.gui

Horizontal = QtCore.Qt.Orientation.Horizontal
Vertical = QtCore.Qt.Orientation.Vertical

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

#Making a custom colormap using matplotlib
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
# cm.register_cmap('white_turbo', white_turbo)

parameters_xml_aliases = {"INPUT":{"Enable":"SRV_PARAM_CH_ENABLED",
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

parameters_types = {"INPUT":{"Enable":'bool',
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
                                        "E low cut":'str',
                                        "E high cut":'str',
                                        "E cut enable":'bool',
                                        "PSD low cut":'str',
                                        "PSD high cut":'str',
                                        "PSD cut enable":'bool',
                                        "Time intervals low cut":'str',
                                        "Time intervals high cut":'str',
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
                                
parameters_units = {"INPUT":{"Record length":'s',
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

def add_color(tree_dict:g.TreeDictionary, name, parent):
    if not parent:
        widget = tree_dict._widget
        param = pg.parametertree.Parameter.create(name=name,type="color")
        widget.addParameters(param)
        tree_dict.connect_any_signal_changed(tree_dict.autosave)
    else:
        s = name.split('/')
        name = s.pop(-1)
        branch = tree_dict._find_parameter(s, create_missing=True)
        param = pg.parametertree.Parameter.create(name=name, type="color")
        branch.addChild(param)

def removeItem(combo_box: g.ComboBox, name: str):
    index_to_remove = combo_box.get_index(name)
    combo_box.remove_item(index_to_remove)

class GUIv2():
    def __init__(self, name="GUIv2", window_size=[1000,500], show: bool = True, block: bool = False, ratio:int = None, full_screen: bool = True):
        self.ratio = int(ct.windll.shcore.GetScaleFactorForDevice(0)/100) if ratio is None else ratio #This is used to scale the GUI on different screen resolutions. Note that this will only work on Windows.
        self.dark_theme_on = not dd.isDark()
        self.margins = int(10/3*self.ratio)
        width, height = self.get_screen_resolution()
        width = int(window_size[0]/1680*width)
        height = int(window_size[1]/1050*height)

        primary, secondary, accent = self.create_colors()

        window = g.Window(name, size=[width, height], autosettings_path=name+"_window.txt")
        window._window.setWindowIcon(QtGui.QIcon("Images/CoMPASS/icon64x64.png"))

        myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
        ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.TopGrid = window.place_object(g.GridLayout(True)).set_height(52*self.ratio)#.set_width(1273*self.ratio)
        window.new_autorow()
        self.BotGrid = window.place_object(g.GridLayout(True), alignment=0)
        
        #Change the top grid's color.
        self.TopGrid._widget.setAutoFillBackground(True)
        temp_palette = self.TopGrid._widget.palette()
        temp_palette.setColor(self.TopGrid._widget.backgroundRole(), accent)
        self.TopGrid._widget.setPalette(temp_palette)
        self.TopGrid.set_column_stretch(1,1)

        #Set the margins for the top and bottom grid.
        self.TopGrid.set_margins(self.margins)
        self.BotGrid.set_margins(self.margins)

        #This is for the lines, pens, brushes, graph types and root data.
        self.lines = {"No lines for now.":None}
        self.pens = {}
        self.brushes = {}
        self.graph_info = {}
        self.previous_line = None
        self.data = {}

        #Generate the top grid
        self.generate_top_grid()

        #Qt Style sheets for changing the TreeDictionary colors
        self.dark_tree = """
            QTreeView {
                background-color: rgb(23, 35, 38);
                selection-background-color: rgb(32, 81, 96);
            }
            QTreeView::disabled{
                background-color: rgb(29,29,29);
                selection-background-color: rgb(72,72,72);
            }
        """
        self.light_tree = """
            QTreeView {
                background-color: rgb(208, 244, 254);
                selection-background-color: rgb(165, 230, 248);
                alternate-background-color: white;
            }
            QTreeView::disabled{
                background-color: rgb(185,185,185);
                selection-background-color: rgb(175,175,175);
                alternate-background-color: white;
            }
        """

        #Qt Style sheets for changing the ComboBox colors
        self.dark_combo = "background-color: rgb(32, 81, 96); selection-background-color: rgb(24, 132, 165)"
        self.light_combo = "background-color: rgb(61, 145, 169); selection-background-color: rgb(111, 205, 231)"

        #Qt Style sheets for sliders:
        self.QSS_dark = """
            QSlider::groove:horizontal{
                height:20px;
            }

            QRangeSlider{
                qproperty-barColor: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(120,225,252), stop:1 #77a);
            }

            QSlider::handle{
                background-color: rgb(61,61,61);
                border: 2px solid rgb(40,40,40);
                border-radius: 22px;
            }

            QSlider::handle:horizontal:hover{
                border-radius: 10px;
            }
        """
        self.QSS_light = """
            QSlider::groove:horizontal{
                height:20px;
            }

            QRangeSlider{
                qproperty-barColor: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(120,225,252), stop:1 #77a);
            }

            QSlider::handle{
                background-color: white;
                border: 2px solid rgb(193,193,193);
                border-radius: 22px;
            }

            QSlider::handle:horizontal:hover{
                border-radius: 10px;
            }
        """

        #Change the color and icons of tree dictionary for the ROOT type
        temp_widget = self.root_dict._widget

        temp_widget.setStyleSheet(self.dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(self.light_tree)

        a = self.root_dict.get_widget("ROOT Types")
        a.setIcon(0,QtGui.QIcon("Images/file_config.png"))

        #Generate the bot grid
        self.generate_bot_grid()

        #Change the color and icons of tree dictionary for the run info
        temp_widget = self.run_dict._widget
        temp_widget.setStyleSheet(self.dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(self.light_tree)

        a = self.run_dict.get_widget("Run Info")
        a.setIcon(0,QtGui.QIcon("Images/info.png"))

        #Change the color and icons of tree dictionaries for the board info
        temp_widget = self.board_dict_1._widget
        temp_widget.setStyleSheet(self.dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(self.light_tree)

        a = self.board_dict_1.get_widget("Board Info")
        a.setIcon(0,QtGui.QIcon("Images/info.png"))

        temp_widget = self.board_dict_2._widget
        temp_widget.setStyleSheet(self.dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(self.light_tree)

        temp_widget = self.board_dict_3._widget
        temp_widget.setStyleSheet(self.dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(self.light_tree)

        #Change the color and icons of tree dictionary for the plot settings
        temp_widget = self.plot_settings_dict._widget
        temp_widget.setStyleSheet(self.dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(self.light_tree)

        a = self.plot_settings_dict.get_widget("General Settings")
        a.setIcon(0,QtGui.QIcon("Images/settings.png"))
        
        a = self.plot_settings_dict.get_widget("Axis")
        a.setIcon(0,QtGui.QIcon("Images/axis.png"))

        a = self.plot_settings_dict.get_widget("Grid")
        a.setIcon(0,QtGui.QIcon("Images/grid.png"))

        a = self.plot_settings_dict.get_widget("Line")
        a.setIcon(0,QtGui.QIcon("Images/line.png"))

        a = self.plot_settings_dict.get_widget("Histogram")
        a.setIcon(0,QtGui.QIcon("Images/histogram.png"))

        #Make the grid layout for the plot buttons another color:
        self.inner_left._widget.setAutoFillBackground(True)
        temp_palette = self.inner_left._widget.palette()
        temp_palette.setColor(self.inner_left._widget.backgroundRole(), accent)
        self.inner_left._widget.setPalette(temp_palette)

        #Load all the settings for the graphs:
        self.load_graph_options()

        s.settings["dark_theme_qt"] = self.dark_theme_on

        if full_screen: window._window.showMaximized()
        if show: window.show(block)
    
    def get_screen_resolution(self):
        #Works only for windows
        user32 = ct.windll.user32
        user32.SetProcessDPIAware()
        return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))

    def generate_top_grid(self):
        #For the channel buttons:
        self.previous_btn = None
        #Search folder button
        search_folder_btn = self.TopGrid.place_object(g.Button(" ",tip="Search a folder!")).set_width(45*self.ratio).set_height(45*self.ratio)
        search_folder_btn.set_style_unchecked(style="image: url(Images/OpenFolder.png)")
        search_folder_btn.signal_clicked.connect(self.search_folder)

        #File type (Raw, unfiltered, filtered)
        self.root_dict = self.TopGrid.place_object(g.TreeDictionary(), alignment=0).set_width(245*self.ratio).set_height(40*self.ratio)
        self.root_dict.add_parameter("ROOT Types/Type chosen",values=["RAW","UNFILTERED","FILTERED"])#.set_width(150*self.ratio)
        self.root_dict.connect_signal_changed("ROOT Types/Type chosen", self.changing_tree)
        self.root_dict._widget.setHeaderLabels(["Parameters long","Value"])

        #Label to show what file was selected
        self.folder_label = self.TopGrid.place_object(g.Label("No folder selected!"))

        #Channel Buttons
        self.ch0_btn = self.make_channel_btn(self.TopGrid, "0", 45, self.channel_toggling)
        self.ch1_btn = self.make_channel_btn(self.TopGrid, "1", 45, self.channel_toggling)
        self.ch2_btn = self.make_channel_btn(self.TopGrid, "2", 45, self.channel_toggling)
        self.ch3_btn = self.make_channel_btn(self.TopGrid, "3", 45, self.channel_toggling)

        self.TopGrid.place_object(g.GridLayout()).set_width(680*self.ratio)

    def generate_bot_grid(self):
        main_tab_area = self.BotGrid.place_object(g.TabArea(), alignment=0)
        main_tab_area._widget.setTabsClosable(False) #To not pop out the tabs by accident. This removes the icons if done.
        self.compass_tab = main_tab_area.add_tab("CoMPASS")
        self.graph_tab = main_tab_area.add_tab("GRAPH")

        #Add the icons
        main_tab_area._widget.setTabIcon(0, QtGui.QIcon("Images/CoMPASS/icon64x64.ico"))
        main_tab_area._widget.setTabIcon(1, QtGui.QIcon("Images/CoMPASS/OpenGraph.png"))

        self.generate_compass_tab()
        self.generate_graph_tab()

        main_tab_area.set_current_tab(0)

    def generate_compass_tab(self):
        self.run_dict = self.compass_tab.place_object(g.TreeDictionary(),alignment=0,column_span=3).set_height(100*self.ratio)
        self.run_dict._widget.setHeaderLabels(["Parameters long","Value"])
        self.run_dict.add_parameter("Run Info/Run ID", value=" ", readonly=True,tip="Run ID name set in CoMPASS/Folder name in which files are saved.")
        self.run_dict.add_parameter("Run Info/Start Time", value=" ", readonly=True, tip="Time at which the acquisition started.")
        self.run_dict.add_parameter("Run Info/Stop Time", value=" ", readonly=True, tip="Time at which the acquisition stopped.")
        self.run_dict.add_parameter("Run Info/Run Time", value=" ", readonly=True, tip="Amount of time the acquisition ran for.")

        self.compass_tab.new_autorow()

        self.board_dict_1 = self.compass_tab.place_object(g.TreeDictionary(),alignment=0).set_height(100*self.ratio)
        self.board_dict_1.add_parameter("Board Info/Name", value=" ", readonly=True, tip="Name of the digitizer in use.")
        self.board_dict_1.add_parameter("Board Info/ADC bits", value=" ", readonly=True, tip="Number of binary digits used to represent digital data from the digitizer.")
        self.board_dict_1.add_parameter("Board Info/ROC firmware", value=" ", readonly=True)
        self.board_dict_1.add_parameter("Board Info/Link", value=" ", readonly=True)

        self.board_dict_2 = self.compass_tab.place_object(g.TreeDictionary(),alignment=0).set_height(100*self.ratio)
        self.board_dict_2.add_parameter(" /ID", value=" ", readonly=True)
        self.board_dict_2.add_parameter(" /Sampling rate", value=None, type="float", readonly=True, suffix="S/s", siPrefix=True)
        self.board_dict_2.add_parameter(" /AMC firware", value=" ", readonly=True)

        self.board_dict_3 = self.compass_tab.place_object(g.TreeDictionary(),alignment=0).set_height(100*self.ratio)
        self.board_dict_3._widget.setHeaderLabels(["Parameters Long","Value"])
        self.board_dict_3.add_parameter(" /Model", value=" ", readonly=True, tip="Model of the digitizer in use.")
        self.board_dict_3.add_parameter(" /DPP type", value=" ", readonly=True)
        self.board_dict_3.add_parameter(" /Enable", value=False, readonly=True,tip="Whether the digitizer can be used or not.")

        self.compass_tab.new_autorow()

        embed_compass_tab_area = self.compass_tab.place_object(g.TabArea(),alignment=0,column_span=3)
        embed_compass_tab_area._widget.setTabsClosable(False) #Same as before if they pop out the icons are gone.
        #Create the new tabs
        input_tab = embed_compass_tab_area.add_tab("INPUT")
        disc_tab = embed_compass_tab_area.add_tab("DISCRIMINATOR")
        qdc_tab = embed_compass_tab_area.add_tab("QDC")
        spectra_tab = embed_compass_tab_area.add_tab("SPECTRA")
        rejection_tab = embed_compass_tab_area.add_tab("REJECTIONS")
        energy_tab = embed_compass_tab_area.add_tab("ENERGY CALIBRATION")
        sync_tab = embed_compass_tab_area.add_tab("SYNC/TRG")
        coincidence_tab = embed_compass_tab_area.add_tab("ONBOARD COINCIDENCES")
        misc_tab = embed_compass_tab_area.add_tab("MISCELLANEOUS")

        #Add the icons of those tabs
        input_icon = QtGui.QIcon('Images/CoMPASS/Input.png')
        disc_icon = QtGui.QIcon('Images/CoMPASS/Discriminator.png')
        qdc_icon = QtGui.QIcon('Images/CoMPASS/QDC.png')
        spectra_icon = QtGui.QIcon('Images/CoMPASS/Spectra.png')
        rejection_icon = QtGui.QIcon('Images/CoMPASS/Rejections.png')
        energy_icon = QtGui.QIcon('Images/CoMPASS/EnergyCalibration.png')
        sync_icon = QtGui.QIcon('Images/CoMPASS/Sync.png')
        coinc_icon = QtGui.QIcon('Images/CoMPASS/Coincidence.png')
        misc_icon = QtGui.QIcon('Images/CoMPASS/Misc.png')

        icon_list = [input_icon, disc_icon, qdc_icon, spectra_icon, rejection_icon, energy_icon, sync_icon, coinc_icon, misc_icon]

        _w = embed_compass_tab_area._widget
        [_w.setTabIcon(index, item) for index, item in enumerate(icon_list)]

        embed_compass_tab_area.set_current_tab(0)

        #Make the settings tab:
        self.input_channel, self.input_dict = self.make_comp_settings_tab(input_tab, "INPUT")
        self.disc_channel, self.disc_dict = self.make_comp_settings_tab(disc_tab, "DISCRIMINATOR")
        self.qdc_channel, self.qdc_dict = self.make_comp_settings_tab(qdc_tab, "QDC")
        self.spectra_channel, self.spectra_dict = self.make_comp_settings_tab(spectra_tab, "SPECTRA")
        self.reject_channel, self.reject_dict = self.make_comp_settings_tab(rejection_tab, "REJECTIONS")
        self.energy_channel, self.energy_dict = self.make_comp_settings_tab(energy_tab, "ENERGY CALIBRATION")
        self.sync_channel, self.sync_dict = self.make_comp_settings_tab(sync_tab, "SYNC")
        self.coinc_channel, self.coinc_dict = self.make_comp_settings_tab(coincidence_tab, "ONBOARD COINCIDENCES")
        self.misc_channel, self.misc_dict = self.make_comp_settings_tab(misc_tab, "MISC")

        [channel.signal_changed.connect(self.reload_channels) for channel in [self.input_channel, self.disc_channel, self.qdc_channel, self.spectra_channel, self.reject_channel, self.energy_channel, self.sync_channel, self.misc_channel]]

    def generate_graph_tab(self):
        grid_left = self.graph_tab.place_object(g.GridLayout(False), alignment=0)
        grid_right = self.graph_tab.place_object(g.GridLayout(False), alignment=0).set_width(300*self.ratio)

        #Make some grids inside the right side grid.
        grid_top = grid_right.place_object(g.GridLayout(False),1,1).set_height(50*self.ratio)
        grid_bot = grid_right.place_object(g.GridLayout(False),1,2)

        #Make the line selection center:
        self.line_selector = grid_top.place_object(g.ComboBox(items=list(self.lines.keys()))).set_width(195*self.ratio).set_height(45*self.ratio)
        self.line_selector._widget.setStyleSheet(self.dark_combo) if self.dark_theme_on else self.line_selector._widget.setStyleSheet(self.light_combo)
        self.line_selector.signal_changed.connect(self.change_line_highlight)
        
        save_btn = grid_top.place_object(g.Button(" ")).set_height(45*self.ratio).set_width(45*self.ratio)
        save_btn.set_style_unchecked(style="image: url(Images/save.png)")
        save_btn.signal_clicked.connect(self.save_changes)

        delete_btn = grid_top.place_object(g.Button(" ")).set_height(45*self.ratio).set_width(45*self.ratio)
        delete_btn.set_style_unchecked(style="image: url(Images/delete.png)")
        delete_btn.signal_clicked.connect(self.delete)

        #Make a collapsible zone for the plot settings
        plot_collapsible = grid_bot.place_object(superqt.QCollapsible("Plot Settings",expandedIcon=QtGui.QIcon("Images/expanded.png"),collapsedIcon=QtGui.QIcon("Images/collapsed.png")))
        self.make_plot_settings(plot_collapsible)

        #Make a collapsible zone
        grid_bot.new_autorow()
        collapsible = grid_bot.place_object(superqt.QCollapsible("TOF Settings", expandedIcon=QtGui.QIcon("Images/expanded.png"),collapsedIcon=QtGui.QIcon("Images/collapsed.png")))
        self.make_collapsible_section(collapsible)


        #Make the plotting region
        self.inner_left = grid_left.place_object(g.GridLayout(False), alignment=0).set_width(40*self.ratio)
        inner_right = grid_left.place_object(g.GridLayout(False), alignment=0)
        
        #Add the buttons for the different plots:
        self.energy_btn = self.make_comp_btn(self.inner_left, "New Energy Histogram", "Images/EnergyHist.png", column=1, row=1)
        self.energy_btn.signal_toggled.connect(self.plot_graphs)

        self.psd_btn = self.make_comp_btn(self.inner_left, "New PSD Histogram", "Images/PSDHist.png", column=1, row=2)
        self.psd_btn.signal_toggled.connect(self.plot_graphs)
        
        self.time_btn = self.make_comp_btn(self.inner_left, "New Time Histogram", "Images/TimeHist.png", column=1, row=3)
        self.time_btn.signal_toggled.connect(self.plot_graphs)

        self.tof_btn = self.make_comp_btn(self.inner_left, "New TOF (Time of flight) Histogram", "Images/TOFHist.png", column=1, row=4)
        self.tof_btn.signal_toggled.connect(self.plot_graphs)

        self.psdvse_btn = self.make_comp_btn(self.inner_left, "New PSD vs Energy Histogram", "Images/PSDvsEnergyHist.png", column=1, row=5)

        self.evse_btn = self.make_comp_btn(self.inner_left, "New Energy vs Energy Histogram", "Images/EnergyvsEnergyHist.png", column=1, row=6)

        self.tofvse_btn = self.make_comp_btn(self.inner_left," New TOF (Time of flight) vs Energy Histogram", "Images/TOFvsEnergyHist.png", column=1, row=7)

        self.mcs_btn = self.make_comp_btn(self.inner_left, "New MCS Graph", "Images/MCS Graph.png", column=1, row=8)
        self.mcs_btn.signal_toggled.connect(self.plot_graphs)

        self.clear_btn = self.make_comp_btn(self.inner_left, "Clear plot", "Images/CompClear.png", column=1, row=9)
        self.clear_btn.signal_toggled.connect(self.clear)

        #Adding the databox and the plot
        self.databox = inner_right.place_object(g.DataboxSaveLoad(file_type='.txt'), alignment=0)
        self.databox.enable_save()
        inner_right.new_autorow()
        plot_region = inner_right.place_object(pg.PlotWidget(), alignment=0)
        plot_region.setBackground("black") if self.dark_theme_on else plot_region.setBackground("white")
        self.plot = plot_region.getPlotItem()

    def make_plot_settings(self, parent):
        collapsible_grid_layout = g.GridLayout(False)

        self.plot_settings_dict = collapsible_grid_layout.place_object(g.TreeDictionary(autosettings_path="GUIv2_plot_dict.txt"),alignment=0).set_width(275*self.ratio)
        self.plot_settings_dict._widget.setHeaderLabels(["Parameters slight long","Value"])

        self.plot_settings_dict.add_parameter("General Settings/Title", value=" ")
        self.plot_settings_dict.connect_signal_changed("General Settings/Title", self.change_title)
        self.plot_settings_dict.add_parameter("General Settings/Legend", value=False)
        self.plot_settings_dict.connect_signal_changed("General Settings/Legend", self.change_legend)
        
        self.plot_settings_dict.add_parameter("Line/Name",value=" ")
        add_color(self.plot_settings_dict, "Line/Pen Color",True)
        add_color(self.plot_settings_dict, "Line/Brush Color",True)

        self.plot_settings_dict.add_parameter("Grid/X Axis",value=True)
        self.plot_settings_dict.connect_signal_changed("Grid/X Axis", self.change_grid)
        self.plot_settings_dict.add_parameter("Grid/Y Axis",value=True)
        self.plot_settings_dict.connect_signal_changed("Grid/Y Axis", self.change_grid)

        self.plot_settings_dict.add_parameter("Axis/X Label", value=" ")
        self.plot_settings_dict.connect_signal_changed("Axis/X Label", self.change_labels)
        self.plot_settings_dict.add_parameter("Axis/Y Label", value=" ")
        self.plot_settings_dict.connect_signal_changed("Axis/Y Label", self.change_labels)

        self.plot_settings_dict.add_parameter("Axis/X Log Scale", value=False)
        self.plot_settings_dict.connect_signal_changed("Axis/X Log Scale", self.change_log)
        self.plot_settings_dict.add_parameter("Axis/Y Log Scale", value=False)
        self.plot_settings_dict.connect_signal_changed("Axis/Y Log Scale", self.change_log)

        self.plot_settings_dict.add_parameter("Axis/Min X",value=0)
        self.plot_settings_dict.connect_signal_changed("Axis/Min X", self.change_min_max)
        self.plot_settings_dict.add_parameter("Axis/Max X",value=100)
        self.plot_settings_dict.connect_signal_changed("Axis/Max X", self.change_min_max)
        self.plot_settings_dict.add_parameter("Axis/Min Y",value=0)
        self.plot_settings_dict.connect_signal_changed("Axis/Min Y", self.change_min_max)
        self.plot_settings_dict.add_parameter("Axis/Max Y",value=100)
        self.plot_settings_dict.connect_signal_changed("Axis/Max Y", self.change_min_max)

        self.plot_settings_dict.add_parameter("Histogram/Number of bins", value=100)
        self.plot_settings_dict.connect_signal_changed("Histogram/Number of bins", self.change_bin_number)
        self.plot_settings_dict.add_parameter("Histogram/2D-Histogram bins", value=1024)
        self.plot_settings_dict.add_parameter("Histogram/Fill Level", value=0)
        self.plot_settings_dict.add_parameter("Histogram/Minimum bin", value=0, tip="For TOF and Time histograms")
        self.plot_settings_dict.add_parameter("Histogram/Maximum bin", value=100, tip="For TOF and time histograms")

        parent.addWidget(collapsible_grid_layout._widget)
        parent.expand()

    def make_collapsible_section(self, parent):
        collapse_grid_layout = g.GridLayout(False)
        self.old_stop_range = 500

        self.previous_start_btn = None
        self.previous_stop_btn = None
        
        light_theme = """
            QPushButton{
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(120,225,252), stop:1 rgb(119,119,170));
            }
            QPushButton:checked {
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(61,145,169), stop:1 rgb(78,78,128));
                color: white;
            }
            QPushButton:hover{
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(111,205,231), stop:1 rgb(104,104,161));
            }
        """

        button_grid = collapse_grid_layout.place_object(g.GridLayout(False), alignment=0, column_span=2)

        self.cpp_tof_btn = button_grid.place_object(g.Button("Use C++ TOF functions", checkable=True)).set_width(240*self.ratio)
        self.cpp_tof_btn._widget.setStyleSheet(light_theme)
        self.roi_btn = self.make_channel_btn(button_grid, "SelectROI", 30, self.show_roi, tip="Show region selected by sliders")
        collapse_grid_layout.new_autorow()

        # collapse_grid_layout.place_object(QtGui.QIcon("Images/start.png"))
        label_start = collapse_grid_layout.place_object(IconLabel("Images/start.png","Start channel range: "))
        # label_start._widget.setPicture
        collapse_grid_layout.new_autorow()

        self.start_range_hslider = collapse_grid_layout.place_object(superqt.QLabeledRangeSlider(Horizontal))
        self.start_range_hslider.setMinimumWidth(275*self.ratio)
        self.start_range_hslider.setMinimumHeight(40*self.ratio)
        self.start_range_hslider.setStyleSheet(self.QSS_dark) if self.dark_theme_on else self.start_range_hslider.setStyleSheet(self.QSS_light)
        self.start_range_hslider.setValue((0,80))
        self.start_range_hslider.setRange(0,self.old_stop_range)
        self.start_range_hslider.show()
        self.start_range_hslider.valueChanged.connect(self.update_roi)

        collapse_grid_layout.new_autorow()

        label_stop = collapse_grid_layout.place_object(IconLabel("Images/stop.png","Stop channel range: "))
        collapse_grid_layout.new_autorow()

        self.stop_range_hslider = collapse_grid_layout.place_object(superqt.QLabeledRangeSlider(Horizontal))
        self.stop_range_hslider.setMinimumWidth(275*self.ratio)
        self.stop_range_hslider.setMinimumHeight(40*self.ratio)
        self.stop_range_hslider.setStyleSheet(self.QSS_dark) if self.dark_theme_on else self.stop_range_hslider.setStyleSheet(self.QSS_light)
        self.stop_range_hslider.setValue((0,80))
        self.stop_range_hslider.setRange(0,self.old_stop_range)
        self.stop_range_hslider.show()
        self.stop_range_hslider.valueChanged.connect(self.update_roi)

        collapse_grid_layout.new_autorow()

        window_label = collapse_grid_layout.place_object(g.Label("Window time: ")).set_width(75*self.ratio)
        # collapse_grid_layout.new_autorow()

        self.time_range = collapse_grid_layout.place_object(superqt.QQuantity("10us"))
        self.time_range.setDecimals(2)
        self.time_range.show()

        collapse_grid_layout.new_autorow()

        start_button_grid = collapse_grid_layout.place_object(g.GridLayout(False), alignment=0,column_span=2)
        # start_button_grid.place_object(g.Label("Start channel: ")).set_width(75*self.ratio)
        start_button_grid.place_object(IconLabel("Images/start.png","Start channel: "))

        self.ch0_start_btn = self.make_channel_btn(start_button_grid, "0", 30, self.start_channel_toggling)
        self.ch1_start_btn = self.make_channel_btn(start_button_grid, "1", 30, self.start_channel_toggling)
        self.ch2_start_btn = self.make_channel_btn(start_button_grid, "2", 30, self.start_channel_toggling)
        self.ch3_start_btn = self.make_channel_btn(start_button_grid, "3", 30, self.start_channel_toggling)

        collapse_grid_layout.new_autorow()
        line = QtWidgets.QFrame()
        line.setMinimumWidth(275*self.ratio)
        line.setFixedHeight(1)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("border:5px solid black")
        collapse_grid_layout.place_object(line)
        collapse_grid_layout.new_autorow()

        stop_button_grid = collapse_grid_layout.place_object(g.GridLayout(False), alignment=0, column_span=2)
        stop_button_grid.place_object(IconLabel("Images/stop.png","Stop channel: "))

        self.ch0_stop_btn = self.make_channel_btn(stop_button_grid, "0", 30, self.stop_channel_toggling)
        self.ch1_stop_btn = self.make_channel_btn(stop_button_grid, "1", 30, self.stop_channel_toggling)
        self.ch2_stop_btn = self.make_channel_btn(stop_button_grid, "2", 30, self.stop_channel_toggling)
        self.ch3_stop_btn = self.make_channel_btn(stop_button_grid, "3", 30, self.stop_channel_toggling)
        
        #List of the buttons:
        self.buttons_list = [self.ch0_btn, self.ch1_btn, self.ch2_btn, self.ch3_btn]
        self.start_buttons_list = [self.ch0_start_btn, self.ch1_start_btn, self.ch2_start_btn, self.ch3_start_btn]
        self.stop_buttons_list = [self.ch0_stop_btn, self.ch1_stop_btn, self.ch2_stop_btn, self.ch3_stop_btn]
 
        self.start_roi = pg.LinearRegionItem(self.start_range_hslider.value(),brush=pg.mkBrush((5,255,0,50)),pen=pg.mkPen((31,88,37)),movable=False)
        self.stop_roi = pg.LinearRegionItem(self.stop_range_hslider.value(),brush=pg.mkBrush((255,0,0,50)),pen=pg.mkPen((88,31,31)),movable=False)


        parent.addWidget(collapse_grid_layout._widget)

    def make_comp_btn(self, parent, tip_text, url_image, **kwargs):
        btn = parent.place_object(g.Button(" ", checkable=True, tip=tip_text), alignment=0, **kwargs).set_height(35*self.ratio).set_width(35*self.ratio)
        btn.set_style_checked(style=f"image: url({url_image}); border: 2px solid rgb(1,196,255); background: rgb(54,54,54)") if self.dark_theme_on else btn.set_style_checked(style=f"image: url({url_image}); border: 2px solid rgb(1,196,255); background: rgb(220,220,220)") 
        btn.set_style_unchecked(style=f"image: url({url_image})")
        return btn

    def make_channel_btn(self, parent, channel_number, size, function, tip: str=None, off: str=None, on:str=None, disabled:str=None):
        tip = f"Channel {channel_number}" if tip is None else tip
        button = parent.place_object(g.Button(" ", True, tip=tip)).set_width(size*self.ratio).set_height(size*self.ratio)
        # QSS_Light = "QPushButton: {" + f"image: url(Images/Off{channel_number}.png);" + "}" + "QPushButton::pressed{" + f"image: url(Images/On{channel_number}.png); border: 2px solid rgb(1,196,255); background: {'(54,54,54)' if self.dark_theme_on else '(220,220,220)'}" + "}"  

        off = "Off" if off is None else off
        on = "On" if on is None else on
        disabled = "Disabled" if disabled is None else disabled

        QSS = """
            QPushButton {
        """ + f"image: url(Images/{off}{channel_number}.png);" + """
            }

            QPushButton::checked{
        """ + f"image: url(Images/{on}{channel_number}.png);" + """
            border: 2px solid rgb(1,196,255);
        """ + f"background: {'rgb(54,54,54)' if self.dark_theme_on else 'rgb(220,220,220)'};" + """
            }

            QPushButton::disabled{
        """ + f"image: url(Images/{disabled}{channel_number}.png);" + """
        """ + f"background: {'rgb(54,54,54)' if self.dark_theme_on else 'rgb(220,220,220)'};" + """
            }
        """

        button.signal_toggled.connect(function)        
        button._widget.setStyleSheet(QSS)
        return button


    def create_colors(self):
        if self.dark_theme_on:
            primary_color = QtGui.QColor("#01c4ff")
            secondary_color = QtGui.QColor("#0baada")
            accent_color = QtGui.QColor("#205160")
        else:
            primary_color = QtGui.QColor("#d0f4fe")
            secondary_color = QtGui.QColor("#a5e6f8")
            accent_color = QtGui.QColor("#3d91a9")
        return primary_color, secondary_color, accent_color

    def make_comp_settings_tab(self, parent_tab, tab_type):
        parent_tab.place_object(g.Label("Channel :"))
        channel_selector = parent_tab.place_object(g.ComboBox(items=["BOARD","CH0","CH1","CH2","CH3"])).set_width(1200*self.ratio)
        channel_selector._widget.setStyleSheet(self.dark_combo) if self.dark_theme_on else channel_selector._widget.setStyleSheet(self.light_combo)
        parent_tab.new_autorow()
        tree_dict = parent_tab.place_object(g.TreeDictionary(), alignment=0, column_span=2)
        tree_dict._widget.setHeaderLabels(["Parameters are very long so here","Values"])
        tree_dict._widget.setStyleSheet(self.dark_tree) if self.dark_theme_on else tree_dict._widget.setStyleSheet(self.light_tree)

        for param in list(parameters_xml_aliases[tab_type].keys()):
            embed_dict = parameters_units.get(tab_type)
            units = embed_dict.get(param) if embed_dict is not None else None
            suffixOn = False if units is None else True
            type_value = parameters_types[tab_type].get(param)
            if tab_type in ["REJECTIONS","ENERGY CALIBRATION","SYNC","MISC"]:
                tree_dict.add_parameter(key=param, value=None, type=type_value, readonly=True)
            else:
                tree_dict.add_parameter(key=param, value=None, type=type_value, suffix=units, siPrefix=suffixOn, readonly=True)

        return channel_selector, tree_dict
   
    def search_folder(self):
        tkinter_result = fd.askdirectory()
        self.complete_path = os.path.realpath(tkinter_result)
        self.folder_label.set_text("Folder selected!")
        for file in os.listdir(self.complete_path):
            if file.endswith(".xml"):
                self.xml_file = file
            if file.endswith(".info"):
                self.info_file = file

        self.load_info_xml()
        
    def load_info_xml(self):
        xml_file_path = self.complete_path + "\\" + self.xml_file
        info_file_path = self.complete_path + "\\" + self.info_file

        info_parser = InfoParser(info_file_path)
        run_information = info_parser.get_run_info()

        run_dict_keys = list(self.run_dict.get_keys())
        for index, key in enumerate(run_dict_keys):
            self.run_dict[key] = run_information[index]

        self.xml_parser = XMLParser(xml_file_path)
        board_properties = self.xml_parser.get_board_properties()

        for index, board_prop_number in enumerate([0,3,6,8]):
            keys = list(self.board_dict_1.get_keys())
            self.board_dict_1[keys[index]] = board_properties[board_prop_number]

        for index, board_prop_number in enumerate([1,4,7]):
            keys = list(self.board_dict_2.get_keys())
            self.board_dict_2[keys[index]] = board_properties[board_prop_number] 

        for index, board_prop_number in enumerate([2,5,9]):
            keys = list(self.board_dict_3.get_keys())
            self.board_dict_3[keys[index]] = board_properties[board_prop_number]
        
        self.reload_channels()
        self.changing_tree()
       
    def load_channel_settings(self, xml_obj, combo_box: g.ComboBox, tree_dict: g.TreeDictionary, key: str, *a):
        xml_key = key
        if key == "ENERGY CALIBRATION":
            xml_key = "ENERGY_CALIBRATION"
        if key == "ONBOARD COINCIDENCES":
            xml_key = "HARDWARE_COINCIDENCE"
        if key == "SPECTRA":
            tree_dict_keys = tree_dict.keys()
            if combo_box.get_text() == "BOARD":
                information = xml_obj.get_parameters()
            elif combo_box.get_text().startswith("CH"):
                number = int(combo_box.get_text()[-1])
                information = xml_obj.get_chn_parameters(number)
            
            for param in tree_dict_keys:
                if parameters_types[key][param] == "str":
                    tree_dict[param] = information[key][parameters_xml_aliases[xml_key][param]][0:-2]
                else:
                    tree_dict[param] = information[key][parameters_xml_aliases[xml_key][param]]
            return
        
        tree_dict_keys = tree_dict.keys()
        if combo_box.get_text() == "BOARD":
            information = xml_obj.get_parameters()
        elif combo_box.get_text().startswith("CH"):
            number = int(combo_box.get_text()[-1])
            information = xml_obj.get_chn_parameters(number)
        
        for param in tree_dict_keys:
            tree_dict[param] = information[xml_key][parameters_xml_aliases[key][param]]
    
    def reload_channels(self, *a):
        self.load_channel_settings(self.xml_parser, self.input_channel, self.input_dict, "INPUT")
        self.load_channel_settings(self.xml_parser, self.disc_channel, self.disc_dict, "DISCRIMINATOR")
        self.load_channel_settings(self.xml_parser, self.qdc_channel, self.qdc_dict, "QDC")
        self.load_channel_settings(self.xml_parser, self.spectra_channel, self.spectra_dict, "SPECTRA")
        self.load_channel_settings(self.xml_parser, self.reject_channel, self.reject_dict, "REJECTIONS")
        self.load_channel_settings(self.xml_parser, self.energy_channel, self.energy_dict, "ENERGY CALIBRATION")
        self.load_channel_settings(self.xml_parser, self.sync_channel, self.sync_dict, "SYNC")
        self.load_channel_settings(self.xml_parser, self.misc_channel, self.misc_dict, "MISC")

    def changing_tree(self, *a):
        folder_to_look_in = self.complete_path + "\\" + self.root_dict["ROOT Types/Type chosen"]
        self.files = [file for file in os.listdir(folder_to_look_in) if file.endswith(".root")]
        match self.root_dict["ROOT Types/Type chosen"]:
            case "FILTERED":
                self.tree = "Data_F"
            case "UNFILTERED":
                self.tree = "Data"
            case "RAW":
                self.tree = "Data_R"
        self.channel_buttons()

    def channel_buttons(self, *a):
        ch0_on = self.ch0_btn.is_checked()
        ch1_on = self.ch1_btn.is_checked()
        ch2_on = self.ch2_btn.is_checked()
        ch3_on = self.ch3_btn.is_checked()

        # xml_labels = [self.xml_parser.get_ch_label(i) for i in range(0,4)]
        xml_labels = {self.xml_parser.get_ch_label(i)[0]:self.xml_parser.get_ch_label(i)[1] if self.xml_parser.get_ch_label(i)[1] != "CH" else f"CH{self.xml_parser.get_ch_label(i)[0]}" for i in range(0,4)}

        self.buttons_files = {}
        
        for file in self.files:
            for index, (key, label) in enumerate(xml_labels.items()):
                if label in file:
                    self.buttons_files[key] = file

    def toggle_others_out(self, selected_button, buttons_list):
        for button in buttons_list:
            if button is selected_button:
                continue
            button.set_checked(False)

    def find_checked_button(self, buttons_list, previous_btn):
        for button in buttons_list:
            if button.is_checked() and button is not previous_btn:
                return button

    def channel_toggling(self, *a):
        # #General channel buttons:
        checked_btn = self.find_checked_button(self.buttons_list, self.previous_btn)
        if checked_btn is not self.previous_btn:
            self.toggle_others_out(checked_btn, self.buttons_list)
            self.previous_btn = checked_btn

    def start_channel_toggling(self, *a):
        #TOF start channel buttons:
        checked_start_btn = self.find_checked_button(self.start_buttons_list, self.previous_start_btn)
        if checked_start_btn is not self.previous_start_btn:
            self.toggle_others_out(checked_start_btn, self.start_buttons_list)
            self.previous_start_btn = checked_start_btn

    def stop_channel_toggling(self, *a):
        #TOF stop channel buttons:
        checked_stop_btn = self.find_checked_button(self.stop_buttons_list, self.previous_stop_btn)
        if checked_stop_btn is not self.previous_stop_btn:
            self.toggle_others_out(checked_stop_btn, self.stop_buttons_list)
            self.previous_stop_btn = checked_stop_btn

    def load_graph_options(self):
        self.change_title()
        self.change_legend()
        self.change_grid()
        self.change_labels()
        self.change_log()
        self.change_min_max()
        self.change_bin_number()
                
    def change_title(self, *a):
        self.plot.setLabels(title=self.plot_settings_dict["General Settings/Title"])
        
    def change_legend(self, *a):
        if self.plot_settings_dict["General Settings/Legend"]:
            self.legend = self.plot.addLegend()
        else:
            self.plot.removeItem(self.legend)
    
    def change_grid(self, *a):
        self.plot.showGrid(x=self.plot_settings_dict["Grid/X Axis"], y=self.plot_settings_dict["Grid/Y Axis"])

    def change_labels(self, *a):
        self.plot.setLabel(axis="bottom",text=self.plot_settings_dict["Axis/X Label"])
        self.plot.setLabel(axis="left",text=self.plot_settings_dict["Axis/Y Label"])

    def change_log(self, *a):
        self.plot.setLogMode(self.plot_settings_dict["Axis/X Log Scale"], self.plot_settings_dict["Axis/Y Log Scale"])

    def change_min_max(self, *a):
        self.plot.setXRange(self.plot_settings_dict["Axis/Min X"], self.plot_settings_dict["Axis/Max X"])
        self.plot.setYRange(self.plot_settings_dict["Axis/Min Y"], self.plot_settings_dict["Axis/Max Y"])

    def change_bin_number(self, *a):
        #Get the old values
        old_start_values = np.array(self.start_range_hslider.value())
        old_stop_values = np.array(self.stop_range_hslider.value())
        new_stop_range = self.plot_settings_dict["Histogram/Number of bins"]
        
        ratio = new_stop_range/self.old_stop_range

        #Calculate the new values
        new_start_values = tuple(old_start_values*ratio)
        new_stop_values = tuple(old_stop_values*ratio)

        self.start_range_hslider.setRange(0, new_stop_range)
        self.start_range_hslider.setValue(new_start_values)
        self.stop_range_hslider.setRange(0, self.plot_settings_dict["Histogram/Number of bins"])
        self.stop_range_hslider.setValue(new_stop_values)
        self.old_stop_range = new_stop_range

        self.start_roi.setRegion(self.start_range_hslider.value())
        self.stop_roi.setRegion(self.stop_range_hslider.value())

    def show_roi(self, *a):
        self.plot.addItem(self.start_roi) if self.roi_btn.is_checked() else self.plot.removeItem(self.start_roi)
        self.plot.addItem(self.stop_roi) if self.roi_btn.is_checked() else self.plot.removeItem(self.stop_roi)

    def update_roi(self, *a):
        self.start_roi.setRegion(self.start_range_hslider.value())
        self.stop_roi.setRegion(self.stop_range_hslider.value())

    def change_line_highlight(self, *a):
        line_selected = self.line_selector.get_text()
        
        for line in self.lines:
            if line_selected == "No lines for now.":
                break
            if self.previous_line is None:
                break
            
            if line == line_selected:
                pen_data = self.pens[line].copy()
                brush_data = self.brushes[line].copy()
                pen_data[3] = 255
                pen = pg.mkPen(pen_data)
                brush = pg.mkBrush(brush_data)

                self.lines[line].setPen(pen)
                self.lines[line].setBrush(brush)
            else:
                pen_data = self.pens[line].copy()
                brush_data = self.brushes[line].copy()
                pen_data[3] = 128
                brush_data[3] = brush_data[3]/2
                pen = pg.mkPen(pen_data)
                brush = pg.mkBrush(brush_data)

                self.lines[line].setPen(pen)
                self.lines[line].setBrush(brush)

        self.previous_line = line_selected

    def get_bin_range(self, graph_type):
        match graph_type:
            case "PSD":
                return (0,1)
            case "TIME" | "TOF":
                return (self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"])
            case _:
                return

    def save_changes(self, *a):
        line_selected = self.line_selector.get_text()
        ranged_hist = ["PSD","TIME","TOF"]
        #Check for a No lines for now:
        if "No lines for now." in self.line_selector.get_all_items():
            index = self.line_selector.get_index("No lines for now.")
            self.line_selector.remove_item(index)

        #Get the data for the line:
        x_data, y_data = self.lines[line_selected].getData()
        raw_data = self.data[line_selected]
        #Get the type and style of line we plot:
        style = self.graph_info[line_selected].get("style")
        type_ = self.graph_info[line_selected].get("type")
        #Get the number of bins in use:
        bins = self.plot_settings_dict["Histogram/Number of bins"]

        #Remove the line:
        self.plot.removeItem(self.lines[line_selected])
        self.lines.pop(line_selected)
        self.pens.pop(line_selected)
        self.brushes.pop(line_selected)
        self.graph_info.pop(line_selected)
        line_index = self.line_selector.get_index(line_selected)
        self.line_selector.remove_item(line_index)

        #Make the pen and brush:
        pen_data = list(self.plot_settings_dict["Line/Pen Color"].getRgb())
        pen = pg.mkPen(pen_data)
        brush_data = list(self.plot_settings_dict["Line/Brush Color"].getRgb())
        brush = pg.mkBrush(brush_data)

        #Plot the line again:
        if style == "HIST":
            bin_range = (0,bins)
            if type_ in ranged_hist:
                bin_range = self.get_bin_range(type_)

            hist = np.histogram(raw_data, bins=bins, range=bin_range)
            x = hist[1]
            y = hist[0]
            line = self.plot.plot(x, y, stepMode="center", fillLevel=self.plot_settings_dict["Histogram/Fill Level"], brush=brush, pen=pen, name=self.plot_settings_dict["Line/Name"])
            
            self.graph_info[line.name()] = {"style":"HIST","fill":self.plot_settings_dict["Histogram/Fill Level"],"type":type_}

        else:
            line = self.plot.plot(x_data, y_data, pen=pen, name=self.plot_settings_dict["Line/Name"])

            self.graph_info[line.name()] = {"style":"GRAPH","fill":None,"type":type_}

        self.lines[line.name()] = line
        self.pens[line.name()] = pen_data
        self.brushes[line.name()] = brush_data

        self.line_selector.add_item(line.name())
        index = self.line_selector.get_index(line.name())
        self.line_selector.set_index(index)

    def delete(self, *a):
        line_selected = self.line_selector.get_text()
        self.plot.removeItem(self.lines[line_selected])
        # self.plot.legend.removeItem(self.lines[line_selected])
        self.lines.pop(line_selected)
        self.pens.pop(line_selected)
        self.brushes.pop(line_selected)
        self.graph_info.pop(line_selected)
        plotted_items_names = [item.name() for item in self.plot.listDataItems()]
        self.line_selector.clear()
        [self.line_selector.add_item(item) for item in plotted_items_names]

    def clear(self, *a):
        self.plot.clear()
        self.lines.clear()
        self.pens.clear()
        self.brushes.clear()
        self.graph_info.clear()
        self.line_selector.clear()
        self.clear_btn.set_checked(False)
        
    def what_btn_is_checked(self, button_list, *a):
        states = [button.is_checked() for button in button_list]
        for index, state in enumerate(states):
            if state:
                return index
        else:
            return None
    
    def plot_data(self, data, type_: str, button: str):
        pen_data = list(self.plot_settings_dict["Line/Pen Color"].getRgb())
        brush_data = list(self.plot_settings_dict["Line/Brush Color"].getRgb())
        fill_level = self.plot_settings_dict["Histogram/Fill Level"]
        step = "center"
        
        #Set the data in the databox
        self.databox["x"], self.databox["y"], root_data = data

        if "No lines for now." in self.line_selector.get_all_items():
            pen = pg.mkPen(pen_data)
            brush = pg.mkBrush(brush_data)
            if type_ != "HIST": 
                fill_level = None
                step = None
            line = self.plot.plot(data[0], data[1], stepMode=step, fillLevel=fill_level, brush=brush, pen=pen, name=self.plot_settings_dict["Line/Name"])

            
            #Add pen and brush to the selected dictionaries
            self.lines.pop("No lines for now.")
            self.lines[line.name()] = line
            self.pens[line.name()] = pen_data
            self.brushes[line.name()] = brush_data
            self.graph_info[line.name()] = {"style":type_,"fill":fill_level,"type":button}
            self.data[line.name()] = root_data

        elif self.line_selector.get_text() != self.plot_settings_dict["Line/Name"]:
            temp_pen_data = pen_data.copy()
            temp_brush_data = brush_data.copy()
            temp_pen_data[3] = 128
            temp_brush_data[3] /= 2

            pen = pg.mkPen(temp_pen_data)
            brush = pg.mkBrush(temp_brush_data)
            if type_ != "HIST": 
                fill_level = None
                step = None
            line = self.plot.plot(data[0], data[1], stepMode=step, fillLevel=fill_level, brush=brush, pen=pen, name=self.plot_settings_dict["Line/Name"])

            self.lines[line.name()] = line
            self.pens[line.name()] = pen_data
            self.brushes[line.name()] = brush_data
            self.graph_info[line.name()] = {"style":type_,"fill":fill_level,"type":button}
            self.data[line.name()] = root_data

    def plot_2dhist(self, data, button: str):
        pen_data = None
        brush_data = None
        fill_level = None
        type_ = "2D-HIST"

        if button == "PSDvsE":
            transform = QtGui.QTransform()
            transform.scale(1, 1)

        image = pg.ImageItem(image=data)

    def disable_buttons(self, buttons_list, buttons_states):
        for index, button in enumerate(buttons_list):
            button.enable(value=buttons_states[index])

    def start_TOF(self, *a):
        states = [True if os.stat(os.path.join(self.complete_path,self.root_dict["ROOT Types/Type chosen"], file)).st_size > 7*1024 else False for file in list(self.buttons_files.values())]
        two_files_pass = True if states.count(True) >= 2 else False
        self.disable_buttons(self.start_buttons_list,states)
        self.disable_buttons(self.stop_buttons_list,states)
        start_btn = self.what_btn_is_checked(self.start_buttons_list)
        stop_btn = self.what_btn_is_checked(self.stop_buttons_list)
        
        if self.root_dict["ROOT Types/Type chosen"] == "FILTERED" and two_files_pass:
            self.root_dict.disable()
            start_file = os.path.join(self.complete_path,self.root_dict["ROOT Types/Type chosen"],self.buttons_files.get(str(start_btn)))
            stop_file = os.path.join(self.complete_path,self.root_dict["ROOT Types/Type chosen"],self.buttons_files.get(str(stop_btn)))

            data = root_reader(start_file, self.tree).get_tof_hist(stop_file, self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"], self.plot_settings_dict["Histogram/Number of bins"])
            
            self.plot_data(data, "HIST","TOF")

    def clean_TOF(self, *a):
        for button in self.start_buttons_list:
            button.enable()
        for button in self.stop_buttons_list:
            button.enable()

        self.root_dict.enable()

        

    def plot_graphs(self, *a):
        btn_checked = self.what_btn_is_checked(self.buttons_list)
        file_to_use = self.buttons_files.get(str(btn_checked))
        path_to_use = os.path.join(self.complete_path, self.root_dict["ROOT Types/Type chosen"], file_to_use)

        if self.energy_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"Energy Histogram - CH{btn_checked}"
            
            data = root_reader(path_to_use, self.tree).get_energy_hist(bins=self.plot_settings_dict["Histogram/Number of bins"])

            self.plot_data(data, "HIST","ENERGY")
            self.energy_btn.set_checked(False)     
            return   


        if self.psd_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"PSD Histogram - CH{btn_checked}"

            data = root_reader(path_to_use, self.tree).get_psd_hist(bins=self.plot_settings_dict["Histogram/Number of bins"])
            
            self.plot_data(data, "HIST","PSD")
            self.psd_btn.set_checked(False)
            return

        if self.time_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"Time Histogram - CH{btn_checked}"

            data = root_reader(path_to_use, self.tree).get_time_hist(self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"], bins=self.plot_settings_dict["Histogram/Number of bins"])

            self.plot_data(data, "HIST","TIME")
            self.time_btn.set_checked(False)
            return

        if self.tof_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"TOF Histogram"
            self.start_TOF()
            self.clean_TOF()
            self.tof_btn.set_checked(False)
            return

        if self.psdvse_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"PSD vs Energy Histogram - CH{btn_checked}"

            file_to_use = self.buttons_files.get(str(btn_checked))
            # data = self.__PSDvsE__(os.path.join(self.complete_path,self.root_dict["ROOT Types/Type chosen"], file_to_use), self.plot_settings_dict)
            return
        
        if self.mcs_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"MCS Graph - CH{btn_checked}"

            data = root_reader(path_to_use, self.tree).get_mcs_graph()

            self.plot_data(data, "GRAPH","MCS")
            self.mcs_btn.set_checked(False)
            return

        plotted_items_names = [item.name() for item in self.plot.listDataItems()]
        self.line_selector.block_signals()
        self.line_selector.clear()
        [self.line_selector.add_item(item) for item in plotted_items_names]
        self.line_selector.unblock_signals()
