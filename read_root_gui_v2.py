#----------------------------------------------------------------------------
# Created by : Chloé Legué
# Current version date : 2024/04/12
# Version = 2.5.12
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
# Other imports from ReadROOT
# Import the root reader API:
from . import read_root
root_reader = read_root.root_reader_v2
# Import the XML file parsing and info parsing (used for the CoMPASS tab):
from . import XML_Parser
InfoParser = XML_Parser.InfoParser
XMLParser = XML_Parser.XMLParser
# Import QtClasses for extra widgets (used for the GUI):
from . import QtClasses
IconLabel = QtClasses.IconLabel
Seperator = QtClasses.Seperator
SelectionBox = QtClasses.SelectionBox
Selecter = QtClasses.Selecter
Logger = QtClasses.Logger
bcolors = QtClasses.bcolors
TableDictionary = QtClasses.TableDictionary
# Import the Merger (Fast TOF calculations):
from . import merge
Merger = merge.Merger
Merger.unfilter_data = True
Converter = merge.Converter
#----------------------------------------------------------------------------
# General libraries imports
import spinmob as s #type: ignore
import spinmob.egg as egg #type: ignore
import numpy as np
# import tkinter.filedialog as fd
import pyqtgraph as pg #type: ignore
import ctypes as ct
import pyqtgraph.exporters as export #type: ignore
import darkdetect as dd #type: ignore
from PyQt5 import QtGui, QtCore, QtWidgets
import superqt, datetime
import pyautogui as p
import typing
#----------------------------------------------------------------------------

g = egg.gui

Horizontal = QtCore.Qt.Orientation.Horizontal
Vertical = QtCore.Qt.Orientation.Vertical

ENABLE_OLD = False


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

def add_color(tree_dict:g.TreeDictionary, name: str, parent: bool, default: QtGui.QColor = None):
    """Adds a color picker item to the selected `TreeDictionary`

    Parameters
    ----------
    tree_dict : g.TreeDictionary
        The `TreeDictionary` to which we want to add a color picker
    name : str
        The name of the variable for the color picker
    parent : bool
        Whether the color picker will have a parent or not.
    default : tuple
        RGBA default value given to the color picker
    """
    if not parent:
        widget = tree_dict._widget
        param = pg.parametertree.Parameter.create(name=name,type="color",default=default, value=default) if default is not None else pg.parametertree.Parameter.create(name=name,type="color", value=default)
        widget.addParameters(param)
        tree_dict.connect_any_signal_changed(tree_dict.autosave)
    else:
        s = name.split('/')
        name = s.pop(-1)
        branch = tree_dict._find_parameter(s, create_missing=True)
        param = pg.parametertree.Parameter.create(name=name, type="color",default=default, value=default) if default is not None else pg.parametertree.Parameter.create(name=name,type="color", value=default)
        branch.addChild(param)

def removeItem(combo_box: g.ComboBox, name: str):
    """Removes an item from a `ComboBox`

    Parameters
    ----------
    combo_box : g.ComboBox
        Selected `ComboBox`
    name : str
        Item to remove
    """
    index_to_remove = combo_box.get_index(name)
    combo_box.remove_item(index_to_remove)

class GUIv2():
    """Class `GUIv2` : Creates a GUIv2 instance that the user can interact with.

    Parameters
    ----------
    name : str, optional
        Name of the window, by default `"GUIv2"`
    window_size : list, optional
        Default window size, by default `[1000,500]`
    show : bool, optional
        Shows the GUI to the user, by default `True`
    block : bool, optional
        Blocks the command line, by default `False`
    ratio : float, optional
        Scale factor of the GUI, by default `None` and will be fetched if possible (defaults to 1 otherwise)
    full_screen : bool, optional
        Shows the GUI in fullscreen, by default `True`
    dark_theme : bool, optional
        Forces the GUI into its dark mode or light mode (if `False`), by default `None` and will be fetched to match the user's default theme.
    compress : bool, optional
        Chooses the compression type of the `.csv` files saved by the GUI, by default `True` which turns on `bz2` compression.
    """
    def __init__(self, name="GUIv2", window_size=[1000,500], show: bool = True, block: bool = False, ratio: float = None, full_screen: bool = True, dark_theme: bool = None, compress: bool = True):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.ratio = self.get_scale_factor() if ratio is None else ratio #This is used to scale the GUI on different screen resolutions. Note that this will only work on Windows.
        self.dark_theme_on = dd.isDark() if dark_theme is None else dark_theme
        Converter.compress = compress
        self.colormap = pg.colormap.getFromMatplotlib("black_turbo") if self.dark_theme_on else pg.colormap.getFromMatplotlib("white_turbo")
        self.margins = int(10/3*self.ratio)
        width, height = self.get_screen_resolution()
        width = int(window_size[0]/1680*width)
        height = int(window_size[1]/1050*height)

        IconLabel.IconSize = IconLabel.new_icon_size(int(35/3*self.ratio))

        primary, secondary, accent = self.create_colors()

        window = g.Window(name, size=[width, height], autosettings_path=name+"_window.txt")
        window._window.setWindowIcon(QtGui.QIcon("Images/CoMPASS/icon64x64.png"))

        if sys.platform.startswith("win"): #This will set the icon to the taskbar. Will only work on windows, I have no idea how this should be done on MacOs.
            myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
            ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.TopGrid = window.place_object(g.GridLayout(True)).set_height(int(52*self.ratio))#.set_width(1273*self.ratio)
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
        self.lines = {"No lines for now.":None} # This is to show the lines in the graph tab.
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

        #Qt Style sheets for changing the custom TableDictionary colors
        self.dark_table = """
            QTableView {
                background-color: rgb(23, 35, 38);
                selection-background-color: rgb(32, 81, 96);
            }
            QTableView::disabled{
                background-color: rgb(29,29,29);
                selection-background-color: rgb(72,72,72);
            }
        """

        self.light_table = """
            QTableView {
                background-color: rgb(208, 244, 254);
                selection-background-color: rgb(165, 230, 248);
                alternate-background-color: white;
            }
            QTableView::disabled{
                background-color: rgb(185,185,185);
                selection-background-color: rgb(175,175,175);
                alternate-background-color: white;
            }
        """

        #Qt Style sheets for changing the ComboBox colors
        self.dark_combo = """
            QComboBox {
                background-color: rgb(32, 81, 96); 
                selection-background-color: rgb(24, 132, 165);
            }
            QComboBox::disabled {
                background-color: rgb(72,72,72);
                selection-background-color: rgb(111,111,111);
            }
        """
        self.light_combo = """
            QComboBox {
                background-color: rgb(61, 145, 169);
                selection-background-color: rgb(111, 205, 231);
            }
            QComboBox::disabled {
                background-color: rgb(121,121,121);
                selection-background-color: rgb(158,158,158);
            }
        """

        #Qt Style sheets for sliders:
        self.QSS_dark = """
            QSlider::groove:horizontal{
            """ + f"height:{int(20/3*self.ratio)}px;" + """
            }

            QRangeSlider{
                qproperty-barColor: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(120,225,252), stop:1 #77a);
            }

            QSlider::handle{
                background-color: rgb(61,61,61);
                border: 2px solid rgb(40,40,40);
            """ + f"border-radius: {int(22/3*self.ratio)}px;" + """
            }

            QSlider::handle:horizontal:hover{
            """ + f"border-radius: {int(10/3*self.ratio)}px;" + """
            }
        """
        self.QSS_light = """
            QSlider::groove:horizontal{
            """ + f"height:{int(20/3*self.ratio)}px;" + """
            }

            QRangeSlider{
                qproperty-barColor: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(120,225,252), stop:1 #77a);
            }

            QSlider::handle{
                background-color: white;
                border: 2px solid rgb(193,193,193);
            """ + f"border-radius: {int(22/3*self.ratio)}px;" + """
            }

            QSlider::handle:horizontal:hover{
            """ + f"border-radius: {int(10/3*self.ratio)}px;" + """
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
    
    def get_screen_resolution(self) -> tuple[int, int]:
        """Gets the resolution of a screen

        Returns
        -------
        tuple[int, int]
            Output tuple containing the width and height of the screen.
        """
        screen_size = p.size()
        return (screen_size.width, screen_size.height)

    def get_scale_factor(self) -> float:
        """Gets the scale factor of your screen. This will only work on Windows machines.

        Returns
        -------
        scale_factor : float
            Scale factor of your device.
        """
        if sys.platform.startswith("win"):
            #Works only for Windows since we are working with dll.
            return float(ct.windll.shcore.GetScaleFactorForDevice(0)/100)
        else:
            return 1

    def generate_top_grid(self):
        """Generates the top grid with the buttons of the GUI"""
        #For the channel buttons:
        self.previous_btn = None
        #Search folder button
        search_folder_btn = self.TopGrid.place_object(g.Button(" ",tip="Search a folder!")).set_width(int(45*self.ratio)).set_height(int(45*self.ratio))
        search_folder_btn.set_style_unchecked(style="image: url(Images/OpenFolder.png)")
        search_folder_btn.signal_clicked.connect(self.search_folder)

        #File type (Raw, unfiltered, filtered)
        self.root_dict = self.TopGrid.place_object(g.TreeDictionary(), alignment=0).set_width(int(245*self.ratio)).set_height(int(40*self.ratio))
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

        self.TopGrid.place_object(g.GridLayout()).set_width(int(680*self.ratio))

    def generate_bot_grid(self):
        """Generates the bottom grid of the GUI. This contains most of the GUI, like the CoMPASS and Graph tabs,"""
        main_tab_area = self.BotGrid.place_object(g.TabArea(), alignment=0)
        main_tab_area._widget.setTabsClosable(False) #To not pop out the tabs by accident. This removes the icons if done.
        self.compass_tab = main_tab_area.add_tab("CoMPASS")
        self.graph_tab = main_tab_area.add_tab("GRAPH")

        #Add the icons
        main_tab_area._widget.setTabIcon(0, QtGui.QIcon("Images/CoMPASS/icon64x64.ico"))
        main_tab_area._widget.setTabIcon(1, QtGui.QIcon("Images/CoMPASS/OpenGraph.png"))

        self.generate_compass_tab()
        self.generate_graph_tab()
        Logger.text_width = int(1265*self.ratio)
        self.logs = Logger(main_tab_area)

        main_tab_area.set_current_tab(0)

    def generate_compass_tab(self):
        """Generates the CoMPASS tab with all of the `TreeDictionary` containing the information of the `.xml` file saved by CoMPASS. All the run settings will also be loaded such that the user can read and note the values used for a specific run."""
        self.run_dict = self.compass_tab.place_object(g.TreeDictionary(),alignment=0,column_span=3).set_height(int(100*self.ratio))
        self.run_dict._widget.setHeaderLabels(["Parameters long","Value"])
        self.run_dict.add_parameter("Run Info/Run ID", value=" ", readonly=True,tip="Run ID name set in CoMPASS/Folder name in which files are saved.")
        self.run_dict.add_parameter("Run Info/Start Time", value=" ", readonly=True, tip="Time at which the acquisition started.")
        self.run_dict.add_parameter("Run Info/Stop Time", value=" ", readonly=True, tip="Time at which the acquisition stopped.")
        self.run_dict.add_parameter("Run Info/Run Time", value=" ", readonly=True, tip="Amount of time the acquisition ran for.")

        self.compass_tab.new_autorow()

        self.board_dict_1 = self.compass_tab.place_object(g.TreeDictionary(),alignment=0).set_height(int(100*self.ratio))
        self.board_dict_1._widget.setHeaderLabels(["Parameters Long","Value"])
        self.board_dict_1.add_parameter("Board Info/Name", value=" ", readonly=True, tip="Name of the digitizer in use.")
        self.board_dict_1.add_parameter("Board Info/ADC bits", value=" ", readonly=True, tip="Number of binary digits used to represent digital data from the digitizer.")
        self.board_dict_1.add_parameter("Board Info/ROC firmware", value=" ", readonly=True)
        self.board_dict_1.add_parameter("Board Info/Link", value=" ", readonly=True)

        self.board_dict_2 = self.compass_tab.place_object(g.TreeDictionary(),alignment=0).set_height(int(100*self.ratio))
        self.board_dict_2._widget.setHeaderLabels(["Parameters Long","Value"])
        self.board_dict_2.add_parameter(" /ID", value=" ", readonly=True)
        self.board_dict_2.add_parameter(" /Sampling rate", value=None, type="float", readonly=True, suffix="S/s", siPrefix=True)
        self.board_dict_2.add_parameter(" /AMC firware", value=" ", readonly=True)

        self.board_dict_3 = self.compass_tab.place_object(g.TreeDictionary(),alignment=0).set_height(int(100*self.ratio))
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
        if ENABLE_OLD:
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

        self.input_dict = self.make_comp_settings_tab(input_tab, "INPUT")
        self.disc_dict = self.make_comp_settings_tab(disc_tab, "DISCRIMINATOR")
        self.qdc_dict = self.make_comp_settings_tab(qdc_tab, "QDC")
        self.spectra_dict = self.make_comp_settings_tab(spectra_tab, "SPECTRA")
        self.reject_dict = self.make_comp_settings_tab(rejection_tab, "REJECTIONS")
        self.energy_dict = self.make_comp_settings_tab(energy_tab, "ENERGY CALIBRATION")
        self.sync_dict = self.make_comp_settings_tab(sync_tab, "SYNC")
        self.coinc_dict = self.make_comp_settings_tab(coincidence_tab, "ONBOARD COINCIDENCES")
        self.misc_dict = self.make_comp_settings_tab(misc_tab, "MISC")
        
    def generate_graph_tab(self):
        """Generates the Graph tab which contains the plot zone and all of the different histogram buttons and settings."""
        grid_left = self.graph_tab.place_object(g.GridLayout(False), alignment=0)
        grid_right = self.graph_tab.place_object(g.GridLayout(False), alignment=0).set_width(int(300*self.ratio))

        #Make some grids inside the right side grid.
        grid_top = grid_right.place_object(g.GridLayout(False),1,1).set_height(int(50*self.ratio))
        grid_bot = grid_right.place_object(g.GridLayout(False),1,2)

        #Make the line selection center:
        self.line_selector = grid_top.place_object(g.ComboBox(items=list(self.lines.keys()))).set_width(int(195*self.ratio)).set_height(int(45*self.ratio))
        self.line_selector._widget.setStyleSheet(self.dark_combo) if self.dark_theme_on else self.line_selector._widget.setStyleSheet(self.light_combo)
        self.line_selector.signal_changed.connect(self.change_line_highlight)
        
        save_btn = grid_top.place_object(g.Button(" ")).set_height(int(45*self.ratio)).set_width(int(45*self.ratio))
        save_btn.set_style_unchecked(style="image: url(Images/save.png)")
        save_btn.signal_clicked.connect(self.save_changes)

        delete_btn = grid_top.place_object(g.Button(" ")).set_height(int(45*self.ratio)).set_width(int(45*self.ratio))
        delete_btn.set_style_unchecked(style="image: url(Images/delete.png)")
        delete_btn.signal_clicked.connect(self.delete)

        #Make a collapsible zone for the plot settings
        plot_collapsible = grid_bot.place_object(superqt.QCollapsible("Plot Settings",expandedIcon=QtGui.QIcon("Images/expanded.png"),collapsedIcon=QtGui.QIcon("Images/collapsed.png")))
        self.make_plot_settings(plot_collapsible)

        #Make a collapsible zone
        grid_bot.new_autorow()
        self.collapsible = grid_bot.place_object(superqt.QCollapsible("TOF Settings", expandedIcon=QtGui.QIcon("Images/expanded.png"),collapsedIcon=QtGui.QIcon("Images/collapsed.png")))
        self.make_collapsible_section(self.collapsible)


        #Make the plotting region
        self.inner_left = grid_left.place_object(g.GridLayout(False), alignment=0).set_width(int(40*self.ratio))
        inner_right = grid_left.place_object(g.GridLayout(False), alignment=0)
        
        #Add the buttons for the different plots:
        self.previous_graph_btn = None #To keep track of what was the last graph button selected.

        self.energy_btn = self.make_comp_btn(self.inner_left, "New Energy Histogram", "Images/EnergyHist.png", column=1, row=1)
        self.energy_btn.signal_toggled.connect(self.plot_selection)

        self.psd_btn = self.make_comp_btn(self.inner_left, "New PSD Histogram", "Images/PSDHist.png", column=1, row=2)
        self.psd_btn.signal_toggled.connect(self.plot_selection)
        
        self.time_btn = self.make_comp_btn(self.inner_left, "New Time Histogram", "Images/TimeHist.png", column=1, row=3)
        self.time_btn.signal_toggled.connect(self.plot_selection)

        self.tof_btn = self.make_comp_btn(self.inner_left, "New TOF (Time of flight) Histogram", "Images/TOFHist.png", column=1, row=4)
        self.tof_btn.signal_toggled.connect(self.tof_selection)

        self.psdvse_btn = self.make_comp_btn(self.inner_left, "New PSD vs Energy Histogram", "Images/PSDvsEnergyHist.png", column=1, row=5)
        self.psdvse_btn.signal_toggled.connect(self.plot_selection)

        self.evse_btn = self.make_comp_btn(self.inner_left, "New Energy vs Energy Histogram", "Images/EnergyvsEnergyHist.png", column=1, row=6)
        self.evse_btn.signal_toggled.connect(self.tof_selection)

        self.tofvse_btn = self.make_comp_btn(self.inner_left," New TOF (Time of flight) vs Energy Histogram", "Images/TOFvsEnergyHist.png", column=1, row=7)
        self.tofvse_btn.signal_toggled.connect(self.tof_selection)

        self.mcs_btn = self.make_comp_btn(self.inner_left, "New MCS Graph", "Images/MCS Graph.png", column=1, row=8)
        self.mcs_btn.signal_toggled.connect(self.plot_selection)

        self.snapshot_btn = self.inner_left.place_object(g.Button(" ", tip="Snapshot"), alignment=0, column=1, row=9).set_height(int(35*self.ratio)).set_width(int(35*self.ratio))
        self.snapshot_btn.set_style_unchecked(style="image: url(Images/SaveCompass.png)")
        self.snapshot_btn.signal_clicked.connect(self.save_snapshot)

        self.plot_btn = self.inner_left.place_object(g.Button(" ", tip="Plot the graph/histogram selected above"), alignment=0, column=1, row=10).set_height(int(35*self.ratio)).set_width(int(35*self.ratio))
        self.plot_btn.set_style_unchecked(style="image: url(Images/PlotCompass.png)")
        self.plot_btn.signal_clicked.connect(self.plot_graphs)

        self.clear_btn = self.make_comp_btn(self.inner_left, "Clear plot", "Images/CompClear.png", column=1, row=11)
        self.clear_btn.signal_toggled.connect(self.clear)

        self.graph_buttons = [self.energy_btn, self.psd_btn, self.time_btn, self.tof_btn, self.psdvse_btn, self.evse_btn, self.tofvse_btn, self.mcs_btn]

        #Adding the databox and the plot
        # inner_right.new_autorow()
        plot_region = inner_right.place_object(pg.PlotWidget(), alignment=0)
        plot_region.setBackground("black") if self.dark_theme_on else plot_region.setBackground("white")
        self.plot = plot_region.getPlotItem()

    def make_plot_settings(self, parent):
        """Generates the plot settings inside of a collapsible zone"""
        collapsible_grid_layout = g.GridLayout(False)

        self.plot_settings_dict = collapsible_grid_layout.place_object(g.TreeDictionary(autosettings_path="GUIv2_plot_dict.txt"),alignment=0).set_width(int(275*self.ratio))
        self.plot_settings_dict._widget.setHeaderLabels(["Parameters slight long","Value"])

        self.plot_settings_dict.add_parameter("General Settings/Title", value=" ", tip="Title of the graph")
        self.plot_settings_dict.connect_signal_changed("General Settings/Title", self.change_title)
        self.plot_settings_dict.add_parameter("General Settings/Legend", value=False, tip="Shows the legend of the graph")
        self.plot_settings_dict.connect_signal_changed("General Settings/Legend", self.change_legend)
        
        self.plot_settings_dict.add_parameter("Line/Name",value=" ", tip="Name of the line")
        add_color(self.plot_settings_dict, "Line/Pen Color",True, QtGui.QColor(67, 230, 110, 255))
        add_color(self.plot_settings_dict, "Line/Brush Color",True, QtGui.QColor(67, 194, 230, 255))

        self.plot_settings_dict.add_parameter("Grid/X Axis",value=True, tip="Shows the X-axis grid")
        self.plot_settings_dict.connect_signal_changed("Grid/X Axis", self.change_grid)
        self.plot_settings_dict.add_parameter("Grid/Y Axis",value=True, tip="Shows the Y-axis grid")
        self.plot_settings_dict.connect_signal_changed("Grid/Y Axis", self.change_grid)

        self.plot_settings_dict.add_parameter("Axis/X Label", value=" ", tip="Label of the X-axis")
        self.plot_settings_dict.connect_signal_changed("Axis/X Label", self.change_labels)
        self.plot_settings_dict.add_parameter("Axis/Y Label", value=" ", tip="Label of the Y-axis")
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

        self.plot_settings_dict.add_parameter("Histogram/X Axis bins", value=100, tip="X-axis bins")
        self.plot_settings_dict.add_parameter("Histogram/Y Axis bins", value=1024, tip="Y-axis bins (for 2D histograms only)")
        self.plot_settings_dict.add_parameter("Histogram/Fill Level", value=0)
        self.plot_settings_dict.add_parameter("Histogram/Minimum bin", value=0, tip="For TOF and Time histograms")
        self.plot_settings_dict.add_parameter("Histogram/Maximum bin", value=100, tip="For TOF and time histograms")

        parent.addWidget(collapsible_grid_layout._widget)
        parent.expand()

    def make_collapsible_section(self, parent):
        """Generates the TOF options inside of a collapsible zone"""
        collapse_grid_layout = g.GridLayout(False)
        self.old_range = 500
        self.old_min = 0

        self.previous_start_btn = None #To keep track of what was the last start channel button selected
        self.previous_stop_btn = None #To keep track of what was the last stop channel buttons selected.
        
        # Calculate TOF button theme:
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
            QPushButton:hover:!pressed{
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(111,205,231), stop:1 rgb(104,104,161));
            }
            QPushButton:hover:checked {
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgb(111,205,231), stop:1 rgb(91,91,144))
                color: white;
            }
            QPushButton:disabled{
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgb(159,159,159), stop:1 rgb(110,110,110));
                color: white;
            }
        """

        dark_theme = """
            QPushButton{
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(120,225,252), stop:1 rgb(119,119,170));
                color: black;
            }
            QPushButton:checked {
                border: 2px solid rgb(30,30,30);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(61,145,169), stop:1 rgb(78,78,128));
                color: white;
            }
            QPushButton:hover:!pressed{
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2: 1, y2: 1, stop:0 rgb(111,205,231), stop:1 rgb(104,104,161));
            }
            QPushButton:hover:checked {
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgb(111,205,231), stop:1 rgb(91,91,144))
                color: white;
            }
            QPushButton:disabled{
                border: 2px solid rgb(193,193,193);
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgb(159,159,159), stop:1 rgb(110,110,110));
                color: white;
            }
        """

        button_grid = collapse_grid_layout.place_object(g.GridLayout(False), alignment=0, column_span=2)

        self.cpp_tof_btn = button_grid.place_object(g.Button("Calculate TOF", checkable=True)).set_width(int(240*self.ratio))
        self.cpp_tof_btn._widget.setStyleSheet(dark_theme) if self.dark_theme_on else self.cpp_tof_btn._widget.setStyleSheet(light_theme)
        self.roi_btn = self.make_channel_btn(button_grid, "SelectROI", 30, self.show_roi, tip="Show region selected by sliders")
        collapse_grid_layout.new_autorow()

        #MAKE SOMETHING FOR THE FILE SELECTION!
        temp_grid = collapse_grid_layout.place_object(g.GridLayout(False), alignment=0, column_span=2)
        self.selection = Selecter("No CSV files for now.", parent=temp_grid)
        self.selection.change_button("Images/OnSelect.png","Images/OffSelect.png","Images/DisabledSelect.png",(1,196,255))
        self.selection.change_combo(self.dark_combo) if self.dark_theme_on else self.selection.change_combo(self.light_combo)
        self.selection.show()
        
        self.selection.set_height(int(30*self.ratio))
        self.selection.set_width(int(240*self.ratio))
        collapse_grid_layout.new_autorow()

        #Start label
        collapse_grid_layout.place_object(IconLabel("Images/start.png","Start channel range: ", int(125*self.ratio)))
        collapse_grid_layout.new_autorow()

        self.start_range_hslider = collapse_grid_layout.place_object(superqt.QLabeledDoubleRangeSlider(Horizontal))
        self.start_range_hslider.setMinimumWidth(int(275*self.ratio))
        self.start_range_hslider.setMinimumHeight(int(40*self.ratio))
        self.start_range_hslider.setStyleSheet(self.QSS_dark) if self.dark_theme_on else self.start_range_hslider.setStyleSheet(self.QSS_light)
        self.start_range_hslider.setValue((0,80))
        self.start_range_hslider.setRange(self.old_min,self.old_range)
        self.start_range_hslider.show()
        self.start_range_hslider.valueChanged.connect(self.update_roi)

        collapse_grid_layout.new_autorow()

        #Stop label
        collapse_grid_layout.place_object(IconLabel("Images/stop.png","Stop channel range: ", int(125*self.ratio)))
        collapse_grid_layout.new_autorow()

        self.stop_range_hslider = collapse_grid_layout.place_object(superqt.QLabeledDoubleRangeSlider(Horizontal))
        self.stop_range_hslider.setMinimumWidth(int(275*self.ratio))
        self.stop_range_hslider.setMinimumHeight(int(40*self.ratio))
        self.stop_range_hslider.setStyleSheet(self.QSS_dark) if self.dark_theme_on else self.stop_range_hslider.setStyleSheet(self.QSS_light)
        self.stop_range_hslider.setValue((0,80))
        self.stop_range_hslider.setRange(self.old_min,self.old_range)
        self.stop_range_hslider.show()
        self.stop_range_hslider.valueChanged.connect(self.update_roi)

        collapse_grid_layout.new_autorow()

        #Window label
        collapse_grid_layout.place_object(IconLabel("Images/time.png","Window time: ",int(75*self.ratio)))

        self.time_range = collapse_grid_layout.place_object(superqt.QQuantity("10us"))
        self.time_range.setDecimals(2)
        self.time_range.show()

        collapse_grid_layout.new_autorow()

        start_button_grid = collapse_grid_layout.place_object(g.GridLayout(False), alignment=0,column_span=2)
        start_button_grid.place_object(IconLabel("Images/start.png","Start channel: ", int(75*self.ratio)))

        self.ch0_start_btn = self.make_channel_btn(start_button_grid, "0", 30, self.start_channel_toggling)
        self.ch1_start_btn = self.make_channel_btn(start_button_grid, "1", 30, self.start_channel_toggling)
        self.ch2_start_btn = self.make_channel_btn(start_button_grid, "2", 30, self.start_channel_toggling)
        self.ch3_start_btn = self.make_channel_btn(start_button_grid, "3", 30, self.start_channel_toggling)

        collapse_grid_layout.new_autorow()
        collapse_grid_layout.place_object(Seperator(int(125*self.ratio), int(100*self.ratio), left=int(113*self.ratio), right=int(37*self.ratio)),column_span=2)
        collapse_grid_layout.new_autorow()

        stop_button_grid = collapse_grid_layout.place_object(g.GridLayout(False), alignment=0, column_span=2)
        stop_button_grid.place_object(IconLabel("Images/stop.png","Stop channel:  ", int(75*self.ratio)))

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

    def reload_csv_files(self):
        """Reloads the `.csv` files shown in the TOF options's Selecter"""
        self.selection.clear()
        if os.path.isdir(os.path.join(self.complete_path,"TOF Data")):
            items_to_add = list(os.listdir(os.path.join(self.complete_path,"TOF Data")))
            for item in items_to_add:
                if item.endswith(".csv"):
                    split_item = item.split("_")[1:]
                    to_add = "_".join(split_item)
                    self.selection.add_item(to_add)
        

    def make_comp_btn(self, parent, tip_text: str, url_image: str, **kwargs):
        """Makes a button with the proper disabled and pressed style sheets."""
        btn = parent.place_object(g.Button(" ", checkable=True, tip=tip_text), alignment=0, **kwargs).set_height(int(35*self.ratio)).set_width(int(35*self.ratio))
        btn.set_style_checked(style=f"image: url({url_image}); border: 2px solid rgb(1,196,255); background: rgb(54,54,54)") if self.dark_theme_on else btn.set_style_checked(style=f"image: url({url_image}); border: 2px solid rgb(1,196,255); background: rgb(220,220,220)") 
        btn.set_style_unchecked(style=f"image: url({url_image})")
        return btn

    def make_channel_btn(self, parent, channel_number: int, size: int, function: callable, tip: str=None, off: str=None, on:str=None, disabled:str=None):
        """Makes a channel button with the proper disabled and pressed style sheets."""
        tip = f"Channel {channel_number}" if tip is None else tip
        button = parent.place_object(g.Button(" ", True, tip=tip)).set_width(int(size*self.ratio)).set_height(int(size*self.ratio))

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
        """Returns some colors used for the GUI"""
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
        
        """Makes a CoMPASS setting tab with the specific `TreeDictionary` entries."""
        grid = parent_tab.place_object(g.GridLayout(False), alignment=0)
        

        if ENABLE_OLD:
            #OLD CODE TO REPLACE
            grid.place_object(g.Label("Channel :"))
            channel_selector = grid.place_object(g.ComboBox(items=["BOARD","CH0","CH1","CH2","CH3"])).set_width(int(1200*self.ratio))
            channel_selector._widget.setStyleSheet(self.dark_combo) if self.dark_theme_on else channel_selector._widget.setStyleSheet(self.light_combo)
            grid.new_autorow()
            tree_dict = grid.place_object(g.TreeDictionary(), alignment=0, column_span=2)
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

        table_dict: TableDictionary = grid.place_object(TableDictionary(6, False))
        table_dict.set_columns_size(int(1248/table_dict.dtsize*self.ratio))
        table_dict.set_width(int(1250*self.ratio))
        table_dict.header(['PARAMETER','BOARD','CH0','CH1','CH2','CH3'])
        table_dict._widget.setStyleSheet(self.dark_table) if self.dark_theme_on else table_dict._widget.setStyleSheet(self.light_table)

        tab_units = parameters_units.get(tab_type)
        for param in list(parameters_xml_aliases[tab_type].keys()):
            unit = tab_units.get(param) if tab_units is not None else None
            type_ = parameters_types[tab_type].get(param)

            table_dict.add(param, [0]*5, [unit]*5, type_)

        return table_dict  
   
    def search_folder(self):
        """Function that asks the user to look for a CoMPASS folder and loads the files and data."""
        # tkinter_result = fd.askdirectory()
        tkinter_result = QtWidgets.QFileDialog.getExistingDirectory()
        self.complete_path = os.path.realpath(tkinter_result)
        for file in os.listdir(self.complete_path):
            if file.endswith(".xml"):
                self.xml_file = file
            if file.endswith(".info"):
                self.info_file = file

        if not hasattr(self, "xml_file") and not hasattr(self, "info_file"):
            self.logs.add_log("The folder searching was cancelled. Please reload a folder before using any of the GUI's functions.")
            return 
        
        self.folder_label.set_text("Folder selected!")
        self.reload_csv_files()
        self.load_info_xml()
        
    def load_info_xml(self):
        """Loads the information from the `.xml` and `.info` files into the CoMPASS settings and run information."""
        xml_file_path = self.complete_path + "\\" + self.xml_file
        info_file_path = self.complete_path + "\\" + self.info_file

        info_parser = InfoParser(info_file_path)
        run_information = info_parser.get_run_info()

        run_dict_keys = list(self.run_dict.get_keys())
        for index, key in enumerate(run_dict_keys):
            self.run_dict[key] = run_information[index]

        self.plot_settings_dict["General Settings/Title"] = run_information[0]
        self.run_id = run_information[0]

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

    def load_compass_settings(self, board_data, channels_data, table_dict: TableDictionary, key: str, *a):
        xml_key = key
        table_keys = table_dict.keys
        tab_units = parameters_units.get(key)

        if key == "ENERGY CALIBRATION":
            xml_key = "ENERGY_CALIBRATION"
        if key == "ONBOARD COINCIDENCES":
            xml_key = "HARDWARE_COINCIDENCE"
        if key == "SPECTRA":
            for index, param in enumerate(table_keys):
                if index == 0: continue
                unit = tab_units.get(param) if tab_units is not None else None
                type_ = parameters_types[key].get(param)

                if type_ == 'str':
                    data = [board_data[xml_key][parameters_xml_aliases[key][param]][0:-2], *[channels_data[i][xml_key][parameters_xml_aliases[key][param]][0:-2] for i in range(4)]]
                    table_dict.set_item(param, data, [unit]*5, type_)
                    continue

                data = [board_data[xml_key][parameters_xml_aliases[key][param]], *[channels_data[i][xml_key][parameters_xml_aliases[key][param]] for i in range(4)]]
                table_dict.set_item(param, data, [unit]*5, type_)
            return        
        
        for index, param in enumerate(table_keys):
            if index == 0: continue
            unit = tab_units.get(param) if tab_units is not None else None
            type_ = parameters_types[key].get(param)

            data = [board_data[xml_key][parameters_xml_aliases[key][param]], *[channels_data[i][xml_key][parameters_xml_aliases[key][param]] for i in range(4)]]
            # if key == "QDC":
            #     # print(board_data[xml_key][parameters_xml_aliases[key][param]])
            #     print(f"{param} :\t{data}") #FOR DEBUG
            table_dict.set_item(param, data, [unit]*5, type_)
 

    def load_channel_settings(self, xml_obj, combo_box: g.ComboBox, tree_dict: g.TreeDictionary, key: str, *a):
        """Load the data for a specified channel and setting group."""
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
        """Reloads the data shown in the CoMPASS settings if the channel selected is changed."""
        if hasattr(self, "xml_parser") and ENABLE_OLD:
            self.load_channel_settings(self.xml_parser, self.input_channel, self.input_dict, "INPUT")
            self.load_channel_settings(self.xml_parser, self.disc_channel, self.disc_dict, "DISCRIMINATOR")
            self.load_channel_settings(self.xml_parser, self.qdc_channel, self.qdc_dict, "QDC")
            self.load_channel_settings(self.xml_parser, self.spectra_channel, self.spectra_dict, "SPECTRA")
            self.load_channel_settings(self.xml_parser, self.reject_channel, self.reject_dict, "REJECTIONS")
            self.load_channel_settings(self.xml_parser, self.energy_channel, self.energy_dict, "ENERGY CALIBRATION")
            self.load_channel_settings(self.xml_parser, self.sync_channel, self.sync_dict, "SYNC")
            self.load_channel_settings(self.xml_parser, self.misc_channel, self.misc_dict, "MISC")

        if hasattr(self, "xml_parser"):
            board_data = self.xml_parser.get_parameters()
            channels_data = [self.xml_parser.get_chn_parameters(i) for i in range(4)]

            self.load_compass_settings(board_data, channels_data, self.input_dict, "INPUT")
            self.load_compass_settings(board_data, channels_data, self.disc_dict, "DISCRIMINATOR")
            self.load_compass_settings(board_data, channels_data, self.qdc_dict, "QDC")
            self.load_compass_settings(board_data, channels_data, self.spectra_dict, "SPECTRA")
            self.load_compass_settings(board_data, channels_data, self.reject_dict, "REJECTIONS")
            self.load_compass_settings(board_data, channels_data, self.energy_dict, "ENERGY CALIBRATION")
            self.load_compass_settings(board_data, channels_data, self.sync_dict, "SYNC")
            self.load_compass_settings(board_data, channels_data, self.misc_dict, "MISC")

    def changing_tree(self, *a):
        """Reloads the `.root` files inside of the project folder."""
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
        """Finds which buttons corresponds to which channel if the channels were renamed."""
        self.load_states = True
        self.rerun_tof = True
        self.states = [None, None, None, None]
        # xml_labels = [self.xml_parser.get_ch_label(i) for i in range(0,4)]
        xml_labels = {self.xml_parser.get_ch_label(i)[0]:self.xml_parser.get_ch_label(i)[1] if self.xml_parser.get_ch_label(i)[1] != "CH" else f"CH{self.xml_parser.get_ch_label(i)[0]}" for i in range(0,4)}

        self.buttons_files = {}
        
        for file in self.files:
            for index, (key, label) in enumerate(xml_labels.items()):
                if label in file:
                    self.buttons_files[key] = file

    def toggle_others_out(self, selected_button: g.Button, buttons_list: list):
        """Toggles out every button in a list of buttons aside the selected one."""
        for button in buttons_list:
            if button is selected_button:
                continue
            button.set_checked(False)

    def find_checked_button(self, buttons_list: list, previous_btn: g.Button):
        """Finds which button is checked within a list of buttons"""
        for button in buttons_list:
            if button.is_checked() and button is not previous_btn:
                return button

    def channel_toggling(self, *a):
        """Toggles the channel buttons in the top grid"""
        # #General channel buttons:
        checked_btn = self.find_checked_button(self.buttons_list, self.previous_btn)
        if checked_btn is not self.previous_btn:
            self.toggle_others_out(checked_btn, self.buttons_list)
            self.previous_btn = checked_btn

    def start_channel_toggling(self, *a):
        """Toggles the start channel buttons in the TOF options"""
        #TOF start channel buttons:
        checked_start_btn = self.find_checked_button(self.start_buttons_list, self.previous_start_btn)
        if checked_start_btn is not self.previous_start_btn:
            self.toggle_others_out(checked_start_btn, self.start_buttons_list)
            self.previous_start_btn = checked_start_btn

    def stop_channel_toggling(self, *a):
        """Toggles the stop channel buttons in the TOF options"""
        #TOF stop channel buttons:
        checked_stop_btn = self.find_checked_button(self.stop_buttons_list, self.previous_stop_btn)
        if checked_stop_btn is not self.previous_stop_btn:
            self.toggle_others_out(checked_stop_btn, self.stop_buttons_list)
            self.previous_stop_btn = checked_stop_btn

    def graph_button_toggling(self, *a):
        """Toggles the histogram buttons on the left side of the plot zone"""
        #Graph buttons:
        checked_graph_btn = self.find_checked_button(self.graph_buttons, self.previous_graph_btn)
        if checked_graph_btn is not self.previous_graph_btn:
            self.toggle_others_out(checked_graph_btn, self.graph_buttons)
            self.previous_graph_btn = checked_graph_btn

    def load_graph_options(self):
        """Loads the default values of the graph options so that they will correctly apply when doing the first graph."""
        self.change_title()
        self.change_legend()
        self.change_grid()
        self.change_labels()
        self.change_log()
                
    def change_title(self, *a):
        """Changes the title of the graph"""
        self.plot.setLabels(title=self.plot_settings_dict["General Settings/Title"])
        
    def change_legend(self, *a):
        """Shows the legend"""
        if self.plot_settings_dict["General Settings/Legend"]:
            self.legend = self.plot.addLegend()
        else:
            try:
                self.plot.removeItem(self.legend)
            except:
                self.logs.add_log("Could not remove an non-existing legend!")
    
    def change_grid(self, *a):
        """Shows the X and Y axis grids"""
        self.plot.showGrid(x=self.plot_settings_dict["Grid/X Axis"], y=self.plot_settings_dict["Grid/Y Axis"])

    def change_labels(self, *a):
        """Changes the X axis and Y axis labels"""
        self.plot.setLabel(axis="bottom",text=self.plot_settings_dict["Axis/X Label"])
        self.plot.setLabel(axis="left",text=self.plot_settings_dict["Axis/Y Label"])

    def change_log(self, *a):
        """Turns on the log scale for the X and Y axis"""
        self.plot.setLogMode(self.plot_settings_dict["Axis/X Log Scale"], self.plot_settings_dict["Axis/Y Log Scale"])

    def change_min_max(self, *a):
        """Changes the X and Y axis range"""
        self.plot.setXRange(self.plot_settings_dict["Axis/Min X"], self.plot_settings_dict["Axis/Max X"])
        self.plot.setYRange(self.plot_settings_dict["Axis/Min Y"], self.plot_settings_dict["Axis/Max Y"])

    def change_bin_number(self, new_min, new_max, *a):
        """Changes the number of bins for the histograms. Will also update the range of the sliders in the TOF options."""
        #Get the old values
        start_values = np.array(self.start_range_hslider.value())
        stop_values = np.array(self.stop_range_hslider.value())
        
        new_range = new_max - new_min
        if new_range < 0: return

        start_positions = (start_values - self.old_min)/float(self.old_range)
        stop_positions = (stop_values - self.old_min)/float(self.old_range)

        new_start_values = start_positions * new_range + new_min
        new_stop_values = stop_positions * new_range + new_min


        self.start_range_hslider.setRange(new_min, new_max)
        self.start_range_hslider.setValue(tuple(new_start_values))
        self.stop_range_hslider.setRange(new_min, new_max)
        self.stop_range_hslider.setValue(tuple(new_stop_values))
        self.old_range = new_range
        self.old_min = new_min

        self.start_roi.setRegion(self.start_range_hslider.value())
        self.stop_roi.setRegion(self.stop_range_hslider.value())

    def show_roi(self, *a):
        """Shows the region of interest for both sliders. The one in green is for the start, the one in red is for the stop."""
        self.plot.addItem(self.start_roi) if self.roi_btn.is_checked() else self.plot.removeItem(self.start_roi)
        self.plot.addItem(self.stop_roi) if self.roi_btn.is_checked() else self.plot.removeItem(self.stop_roi)
        Merger.cuts_enabled = self.roi_btn.is_checked()

    def update_roi(self, *a):
        """Changes the region of interest based on the sliders positions."""
        self.start_roi.setRegion(self.start_range_hslider.value())
        self.stop_roi.setRegion(self.stop_range_hslider.value())

    def change_line_highlight(self, *a):
        """Changes the highlighted line"""
        line_selected = self.line_selector.get_text()
        
        for line in self.lines:
            if line_selected == "No lines for now.":
                break
            if self.previous_line is None:
                break
            
            if line == line_selected:
                if self.graph_info[line]["style"] != "2D-HIST":
                    pen_data = self.pens[line].copy()
                    brush_data = self.brushes[line].copy()
                    pen_data[3] = 255
                    pen = pg.mkPen(pen_data)
                    brush = pg.mkBrush(brush_data)

                    self.lines[line].setPen(pen)
                    self.lines[line].setBrush(brush)
                    continue
                
                self.lines[line].setOpts(opacity=1)
                
            else:
                if self.graph_info[line]["style"] != "2D-HIST":
                    pen_data = self.pens[line].copy()
                    brush_data = self.brushes[line].copy()
                    pen_data[3] = 128
                    brush_data[3] = brush_data[3]/2
                    pen = pg.mkPen(pen_data)
                    brush = pg.mkBrush(brush_data)

                    self.lines[line].setPen(pen)
                    self.lines[line].setBrush(brush)
                    continue

                self.lines[line].setOpts(opacity=0.25)
                

        self.previous_line = line_selected

    def get_bin_range(self, graph_type):
        """Fetches the bin range for different graphs"""
        match graph_type:
            case "PSD":
                return (0,1)
            case "TIME" | "TOF":
                return (self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"])
            case _:
                return

    def save_changes(self, *a):
        """Saves the changes made to the graph options and applies them to the selected graph"""
        line_selected = self.line_selector.get_text()
        file_selected = self.selection.get_text()
        cuts_on = False
        if len(file_selected.split("_")) > 3:
            cuts_on = True

        ranged_hist = ["PSD","TIME","TOF"]
        ranged_2dhist = ["TOFvsE","PSDvsE"]
        #Check for a No lines for now:
        if "No lines for now." in self.line_selector.get_all_items():
            index = self.line_selector.get_index("No lines for now.")
            self.line_selector.remove_item(index)

        #Get the type and style of line we plot:
        style = self.graph_info[line_selected].get("style")
        type_ = self.graph_info[line_selected].get("type")
        #Get the number of bins in use:
        bins = self.plot_settings_dict["Histogram/X Axis bins"]
        #Get the data for the line:
        if style != "2D-HIST":
            x_data, y_data = self.lines[line_selected].getData()
            raw_data = self.data[line_selected]
        else:
            raw_data = self.data[line_selected]

        

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
        name = self.plot_settings_dict["Line/Name"]

        #Plot the line again:
        if style == "2D-HIST":
            y_bins = self.plot_settings_dict["Histogram/Y Axis bins"]
            x_range = None
            y_range = None
            if type_ in ranged_2dhist:
                y_range = self.get_bin_range(type_.split("vs")[0])
                min_e = min(raw_data[0])
                max_e = max(raw_data[0])
                x_range = (min_e, max_e)

            density = np.histogram2d(*raw_data, bins=[bins, y_bins], range=(x_range, y_range))[0]

            transform = QtGui.QTransform()
            transform.scale(1,1)

            if type_ == "EvsE":
                old_y, old_x = density.shape
                x_scale = y_scale = int(self.spectra_dict["Energy N channels"])
                transform.scale(x_scale/old_x, y_scale/old_y)
                if cuts_on:
                    transform = QtGui.QTransform()
                    string_to_edit = file_selected.split("_")[-1][1:-5].split(",")
                    start_channel_cut = [float(item) for item in string_to_edit[0][1:-1].split("-")]
                    stop_channel_cut = [float(item) for item in string_to_edit[1][2:-1].split("-")]
                    if len(start_channel_cut) != 2:
                        self.logs.add_log("Did you properly name your `.csv` file?")
                        return
                    if len(stop_channel_cut) != 2:
                        self.logs.add_log("Did you properly name your `.csv` file?")
                        return
                    x_scale = (start_channel_cut[1] - start_channel_cut[0])/old_x
                    y_scale = (stop_channel_cut[1] - stop_channel_cut[0])/old_y

                    transform.scale(x_scale, y_scale)     
                    transform.translate(start_channel_cut[0]/x_scale, stop_channel_cut[0]/y_scale)
            if type_ == "PSDvsE":
                transform.scale(1, 1/self.plot_settings_dict["Histogram/Y Axis bins"])
            if type_ == "TOFvsE":
                _, old_x = density.shape
                x_scale = int(self.spectra_dict["Energy N channels"])
                scale_factor = (self.plot_settings_dict["Histogram/Maximum bin"]-self.plot_settings_dict["Histogram/Minimum bin"])/self.plot_settings_dict["Histogram/Y Axis bins"]
                transform.scale(x_scale/old_x, scale_factor)
                transform.translate(0,self.plot_settings_dict["Histogram/Minimum bin"]*scale_factor)

            image = pg.ImageItem(image=density)
            image.setTransform(transform)
            image.setColorMap(self.colormap)

            if "No lines for now." in self.line_selector.get_all_items() or len(self.line_selector.get_all_items()) == 0:
                opacity = 1
                image.setOpts(opacity=opacity)

                self.plot.addItem(image)

                self.lines.pop("No lines for now.") if "No lines for now." in self.line_selector.get_all_items() else None

            elif self.line_selector.get_text() != name:
                opacity = 0.25
                image.setOpts(opacity=opacity)

                self.plot.addItem(image)

            self.lines[name] = image
            self.pens[name] = pen_data
            self.brushes[name] = brush_data
            self.graph_info[name] = {"style":style,"fill":None,"type":type_}
            self.data[name] = raw_data
            self.clean_up()
            return

        if style == "HIST":
            bin_range = None
            if type_ in ranged_hist:
                bin_range = self.get_bin_range(type_)

            hist = np.histogram(raw_data, bins=bins, range=bin_range)
            x = hist[1]
            y = hist[0]
            line = self.plot.plot(x, y, stepMode="center", fillLevel=self.plot_settings_dict["Histogram/Fill Level"], brush=brush, pen=pen, name=name)
            
            self.graph_info[name] = {"style":"HIST","fill":self.plot_settings_dict["Histogram/Fill Level"],"type":type_}

        if style != "HIST" and style != "2D-HIST":
            line = self.plot.plot(x_data, y_data, pen=pen, name=self.plot_settings_dict["Line/Name"])

            self.graph_info[name] = {"style":"GRAPH","fill":None,"type":type_}

        self.lines[name] = line
        self.pens[name] = pen_data
        self.brushes[name] = brush_data

        self.line_selector.add_item(name)
        index = self.line_selector.get_index(name)
        self.line_selector.set_index(index)
        self.clean_up()

    def delete(self, *a):
        """Deletes the selected line/image"""
        line_selected = self.line_selector.get_text()
        self.plot.removeItem(self.lines[line_selected])
        # self.plot.legend.removeItem(self.lines[line_selected])
        self.lines.pop(line_selected)
        self.pens.pop(line_selected)
        self.brushes.pop(line_selected)
        self.graph_info.pop(line_selected)
        self.data.pop(line_selected)
        
        plotted_items_names = self.lines.keys()
        self.line_selector.block_signals()
        self.line_selector.clear()
        [self.line_selector.add_item(item) for item in plotted_items_names]
        self.line_selector.unblock_signals()


    def save_snapshot(self, *a):
        """Saves a screenshot of the graph inside of the screenshots folder generated by CoMPASS"""
        exporter = export.ImageExporter(self.plot)
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        path_to_save = os.path.join(self.complete_path, "SCREENSHOTS", f"{self.plot_settings_dict['General Settings/Title']}_{current_date}.png")
        exporter.export(path_to_save)

    def clear(self, *a):
        """Clears the plot zone"""
        self.plot.clear()
        self.lines.clear()
        self.pens.clear()
        self.brushes.clear()
        self.graph_info.clear()
        self.line_selector.clear()
        self.clear_btn.set_checked(False)
        self.roi_btn.set_checked(False)
        
    def what_btn_is_checked(self, button_list, *a):
        """Returns the index of the pressed/checked button in a list of buttons."""
        states = [button.is_checked() for button in button_list]
        for index, state in enumerate(states):
            if state:
                return index
        else:
            return None
    
    def plot_data(self, data: tuple, type_: str, button: str):
        """Plot the histograms (1D)

        Parameters
        ----------
        data : tuple
            X bins, Y bins and raw histogram data
        type_ : str
            Type of histogram (depending on the type some histogram ranges might change)
        button : str
            Button pressed for the histogram.
        """
        pen_data = list(self.plot_settings_dict["Line/Pen Color"].getRgb())
        brush_data = list(self.plot_settings_dict["Line/Brush Color"].getRgb())
        fill_level = self.plot_settings_dict["Histogram/Fill Level"]
        step = "center"
        
        #Set the data in the databox
        x, y, root_data = data
        min_value = min(root_data)
        max_value = max(root_data)
        if button == "PSD":
            min_value = 0
            max_value = 1

        if "No lines for now." in self.line_selector.get_all_items():
            pen = pg.mkPen(pen_data)
            brush = pg.mkBrush(brush_data)
            if type_ != "HIST": 
                fill_level = None
                step = None
            line = self.plot.plot(data[0], data[1], stepMode=step, fillLevel=fill_level, brush=brush, pen=pen, name=self.plot_settings_dict["Line/Name"])
            
            #Add pen and brush to the selected dictionaries
            self.lines.pop("No lines for now.")

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

        self.change_bin_number(min_value, max_value)

    def plot_2dhist(self, data: tuple, button: str):
        """Plot the histograms (2D)

        Parameters
        ----------
        data : tuple
            X bins, Y bins and raw histogram data
        button : str
            Button pressed for the histogram.
        """
        file_selected = self.selection.get_text()
        cuts_on = False
        if len(file_selected.split("_")) > 3:
            cuts_on = True
        pen_data = None
        brush_data = None
        fill_level = None
        type_ = "2D-HIST"
        name = self.plot_settings_dict["Line/Name"]

        x, y, density_data, original_data = data
        
        transform = QtGui.QTransform()
        transform.scale(1,1)

        if button == "EvsE":
            old_y, old_x = density_data.shape
            x_scale = y_scale = int(self.spectra_dict["Energy N channels"])
            transform.scale(x_scale/old_x, y_scale/old_y)
            if cuts_on:
                transform = QtGui.QTransform()
                string_to_edit = file_selected.split("_")[-1][1:-5].split(",")
                start_channel_cut = [float(item) for item in string_to_edit[0][1:-1].split("-")]
                stop_channel_cut = [float(item) for item in string_to_edit[1][2:-1].split("-")]
                if len(start_channel_cut) != 2:
                    self.logs.add_log("Did you properly name your `.csv` file?")
                    return
                if len(stop_channel_cut) != 2:
                    self.logs.add_log("Did you properly name your `.csv` file?")
                    return
                x_scale = (start_channel_cut[1] - start_channel_cut[0])/old_x
                y_scale = (stop_channel_cut[1] - stop_channel_cut[0])/old_y

                transform.scale(x_scale, y_scale)     
                transform.translate(start_channel_cut[0]/x_scale, stop_channel_cut[0]/y_scale)
                
        if button == "PSDvsE":
            transform.scale(1, 1/self.plot_settings_dict["Histogram/Y Axis bins"])
        if button == "TOFvsE":
            scale_factor = (self.plot_settings_dict["Histogram/Maximum bin"]-self.plot_settings_dict["Histogram/Minimum bin"])/self.plot_settings_dict["Histogram/Y Axis bins"]
            transform.scale(1, scale_factor)
            transform.translate(0,self.plot_settings_dict["Histogram/Minimum bin"]*scale_factor)

        image = pg.ImageItem(image=density_data)
        image.setTransform(transform)
        image.setColorMap(self.colormap)
    
        if "No lines for now." in self.line_selector.get_all_items() or len(self.line_selector.get_all_items()) == 0:
            opacity = 1
            image.setOpts(opacity=opacity)

            self.plot.addItem(image)

            self.lines.pop("No lines for now.") if "No lines for now." in self.line_selector.get_all_items() else None

        elif self.line_selector.get_text() != name:
            opacity = 0.25
            image.setOpts(opacity=opacity)

            self.plot.addItem(image)

        self.lines[name] = image
        self.pens[name] = pen_data
        self.brushes[name] = brush_data
        self.graph_info[name] = {"style":type_,"fill":fill_level,"type":button}
        self.data[name] = original_data
            
        
    def enable_buttons(self, buttons_list):
        """Enables all buttons inside of a list of buttons"""
        for button in buttons_list:
            button.enable()

    def enable_all_buttons(self):
        """Enables all the buttons that can be disabled in the GUI"""
        self.enable_buttons(self.buttons_list)
        self.enable_buttons(self.start_buttons_list)
        self.enable_buttons(self.stop_buttons_list)

    def disable_buttons(self, buttons_list, buttons_states):
        """Disables the buttons corresponding to their states they should have"""
        for index, button in enumerate(buttons_list):
            button.enable(value=buttons_states[index])

    def disable_all_buttons(self, buttons_states):
        """Disables all buttons based on given staets"""
        self.disable_buttons(self.buttons_list, buttons_states)
        self.disable_buttons(self.start_buttons_list, buttons_states)
        self.disable_buttons(self.stop_buttons_list, buttons_states)

    def start_TOF(self, button, *a):
        """Run the TOF analysis based on different sets of parameters"""
        two_files_pass = True if self.states.count(True) >= 2 else False
        if not self.selection.is_checked():
            start_btn = self.what_btn_is_checked(self.start_buttons_list)
            stop_btn = self.what_btn_is_checked(self.stop_buttons_list)
            if start_btn is None:
                self.logs.add_log("Did you select a start channel for the TOF?")
                return
            if stop_btn is None:
                self.logs.add_log("Did you select a stop channel for the TOF?")
                return
            
            time_window_magnitude = int(self.time_range.value().to("picosecond").magnitude)
            time_window_quantity = self.time_range.value()

            start_file = os.path.join(self.complete_path,self.root_dict["ROOT Types/Type chosen"],self.buttons_files.get(str(start_btn)))
            stop_file = os.path.join(self.complete_path,self.root_dict["ROOT Types/Type chosen"],self.buttons_files.get(str(stop_btn)))

        
        if self.root_dict["ROOT Types/Type chosen"] == "FILTERED" and two_files_pass:
            self.root_dict.disable()

            if button == "TOF":
                data = root_reader(start_file, self.tree).get_tof_hist(stop_file, self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"], self.plot_settings_dict["Histogram/X Axis bins"])
                self.plot_data(data, "HIST", button) if data is not None else None
                self.tof_btn.set_checked(False)

            if button == "EvsE":
                data = root_reader(start_file, self.tree).get_evse_hist(stop_file, self.plot_settings_dict["Histogram/X Axis bins"],self.plot_settings_dict["Histogram/Y Axis bins"])
                self.plot_2dhist(data, button) if data is not None else None
                self.evse_btn.set_checked(False)

            if button == "TOFvsE":
                data = root_reader(start_file, self.tree).get_tofvse_hist(stop_file, self.plot_settings_dict["Histogram/Minimum bin"],self.plot_settings_dict["Histogram/Maximum bin"],self.plot_settings_dict["Histogram/X Axis bins"],self.plot_settings_dict["Histogram/Y Axis bins"])
                self.plot_2dhist(data, button) if data is not None else None
                self.tofvse_btn.set_checked(False)
            
            self.clean_up()

        if self.root_dict["ROOT Types/Type chosen"] == "RAW" and two_files_pass and (self.cpp_tof_btn.is_checked()):
            self.csv_name = read_root.generate_csv_name(start_file, start_btn, stop_btn, time_window_quantity)
            if Merger.cuts_enabled:
                starts = np.array(self.start_range_hslider.value()).astype(int)
                stops = np.array(self.stop_range_hslider.value()).astype(int)
                start_string = f"{starts[0]}-{starts[1]}"
                stop_string = f"{stops[0]}-{stops[1]}"
                self.csv_name = read_root.generate_csv_name(start_file, start_btn, stop_btn, time_window_quantity, True, (start_string, stop_string))
                
            
            self.root_dict.disable()
            self.cpp_tof_btn.disable()
            self.roi_btn.disable()
            self.selection.disable()

            self.tof_thread = QtCore.QThread()
            self.merger = Merger(stop_file, start_file, window=time_window_magnitude)
            self.merger.select_cuts(*self.start_range_hslider.value(),1)
            self.merger.select_cuts(*self.stop_range_hslider.value(),0)

            self.merger.moveToThread(self.tof_thread)
            self.tof_thread.started.connect(self.merger.merge)

            self.merger.finished.connect(self.tof_thread.quit)
            self.merger.finished.connect(lambda x: Converter(x).save(self.csv_name))
            self.tof_thread.finished.connect(self.tof_thread.deleteLater)
            self.merger.finished.connect(self.merger.deleteLater)
            
            if button == "TOF":
                self.merger.finished.connect(lambda: self.plot_data(read_root.get_cpp_tof_hist(self.csv_name, self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"], self.plot_settings_dict["Histogram/X Axis bins"],compress=Converter.compress), "HIST", "TOF"))
                self.merger.finished.connect(lambda: self.tof_btn.set_checked(False))
            
            if button == "EvsE":
                self.merger.finished.connect(lambda: self.plot_2dhist(read_root.get_cpp_evse_hist(self.csv_name, self.plot_settings_dict["Histogram/X Axis bins"], self.plot_settings_dict["Histogram/Y Axis bins"],compress=Converter.compress), button))
                self.merger.finished.connect(lambda: self.evse_btn.set_checked(False))
            
            if button == "TOFvsE":
                self.merger.finished.connect(lambda: self.plot_2dhist(read_root.get_cpp_tofvse_hist(self.csv_name, self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"], self.plot_settings_dict["Histogram/X Axis bins"], self.plot_settings_dict["Histogram/Y Axis bins"],compress=Converter.compress), button))
                self.merger.finished.connect(lambda: self.tofvse_btn.set_checked(False))
            
            self.merger.finished.connect(self.clean_up)
            self.merger.finished.connect(self.reload_csv_files)
            
            self.tof_thread.start()
            self.rerun_tof = False

        if two_files_pass and self.selection.is_checked():
            csv_to_use = os.path.join(self.complete_path, "TOF Data",f"{self.run_id}_{self.selection.get_text()}")

            self.root_dict.disable()
            self.cpp_tof_btn.disable()
            self.roi_btn.disable()
            self.selection.disable()

            if button == "TOF":
                self.plot_data(read_root.get_cpp_tof_hist(csv_to_use, self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"], self.plot_settings_dict["Histogram/X Axis bins"],compress=Converter.compress), "HIST", "TOF")
                self.tof_btn.set_checked(False)

            if button == "EvsE":
                self.plot_2dhist(read_root.get_cpp_evse_hist(csv_to_use, self.plot_settings_dict["Histogram/X Axis bins"], self.plot_settings_dict["Histogram/Y Axis bins"],compress=Converter.compress), button)
                self.evse_btn.set_checked(False)

            if button == "TOFvsE":
                self.plot_2dhist(read_root.get_cpp_tofvse_hist(csv_to_use, self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"], self.plot_settings_dict["Histogram/X Axis bins"], self.plot_settings_dict["Histogram/Y Axis bins"],compress=Converter.compress), button)
                self.tofvse_btn.set_checked(False)

            self.clean_up()
            self.selection.set_checked(False)
            


    def clean_up(self, *a):
        """Cleans up the buttons after the TOF"""
        self.root_dict.enable()
        self.cpp_tof_btn.enable()
        self.cpp_tof_btn.set_checked(False)
        self.roi_btn.enable()
        self.roi_btn.set_checked(False)
        self.selection.enable()

        # Enables all the buttons
        self.enable_all_buttons()

        # Toggle all the buttons out
        self.toggle_others_out(None, self.buttons_list)
        self.toggle_others_out(None, self.start_buttons_list)
        self.toggle_others_out(None, self.stop_buttons_list)

        plotted_items_names = self.lines.keys()
        self.line_selector.block_signals()
        self.line_selector.clear()
        [self.line_selector.add_item(item) for item in plotted_items_names]
        self.line_selector.unblock_signals()

        

    def plot_graphs(self, *a):
        """Plots the graph corresponding to the selected button"""
        btn_checked = self.what_btn_is_checked(self.buttons_list)
        if btn_checked is not None:
            file_to_use = self.buttons_files.get(str(btn_checked))
            path_to_use = os.path.join(self.complete_path, self.root_dict["ROOT Types/Type chosen"], file_to_use)

        if self.energy_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"Energy Histogram - CH{btn_checked}"
            self.plot_settings_dict["Axis/X Label"] = "Energy bins"
            self.plot_settings_dict["Axis/Y Label"] = "Counts"
            
            data = root_reader(path_to_use, self.tree).get_energy_hist(bins=self.plot_settings_dict["Histogram/X Axis bins"])

            self.plot_data(data, "HIST","ENERGY")
            self.energy_btn.set_checked(False)
            self.clean_up()

        if self.psd_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"PSD Histogram - CH{btn_checked}"
            self.plot_settings_dict["Axis/X Label"] = "PSD bins"
            self.plot_settings_dict["Axis/Y Label"] = "Counts"

            data = root_reader(path_to_use, self.tree).get_psd_hist(bins=self.plot_settings_dict["Histogram/X Axis bins"])
            
            self.plot_data(data, "HIST","PSD")
            self.psd_btn.set_checked(False)
            self.clean_up()

        if self.time_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"Time Histogram - CH{btn_checked}"
            self.plot_settings_dict["Axis/X Label"] = "Time bins"
            self.plot_settings_dict["Axis/Y Label"] = "Counts"

            data = root_reader(path_to_use, self.tree).get_time_hist(self.plot_settings_dict["Histogram/Minimum bin"], self.plot_settings_dict["Histogram/Maximum bin"], bins=self.plot_settings_dict["Histogram/X Axis bins"])

            self.plot_data(data, "HIST","TIME")
            self.time_btn.set_checked(False)
            self.clean_up()

        if self.tof_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"TOF Histogram"
            self.plot_settings_dict["Axis/X Label"] = "TOF bins"
            self.plot_settings_dict["Axis/Y Label"] = "Counts"

            self.start_TOF("TOF")

        if self.psdvse_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"PSD vs Energy Histogram - CH{btn_checked}"
            self.plot_settings_dict["Axis/X Label"] = "Energy bins"
            self.plot_settings_dict["Axis/Y Label"] = "PSD bins"            
            
            data = root_reader(path_to_use, self.tree).get_psdvse_hist(self.plot_settings_dict["Histogram/X Axis bins"],self.plot_settings_dict["Histogram/Y Axis bins"])

            self.plot_2dhist(data, "PSDvsE")
            self.psdvse_btn.set_checked(False)
            self.clean_up()

        if self.evse_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"E vs E Histogram"
            self.plot_settings_dict["Axis/X Label"] = "Energy (start) bins"            
            self.plot_settings_dict["Axis/Y Label"] = "Energy (stop) bins"            

            self.start_TOF("EvsE")

        if self.tofvse_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"TOF vs E Histogram"
            self.plot_settings_dict["Axis/X Label"] = "Energy (stop) bins"
            self.plot_settings_dict["Axis/Y Label"] = "TOF bins"

            self.start_TOF("TOFvsE")
        
        if self.mcs_btn.is_checked():
            self.plot_settings_dict["Line/Name"] = f"MCS Graph - CH{btn_checked}"
            self.plot_settings_dict["Axis/X Label"] = "Time"
            self.plot_settings_dict["Axis/Y Label"] = "Events"

            data = root_reader(path_to_use, self.tree).get_mcs_graph()

            self.plot_data(data, "GRAPH","MCS")
            self.mcs_btn.set_checked(False)
            self.clean_up()

    def tof_selection(self, *a):
        """Collapses or expands the TOF zone if a TOF"""
        if a[0]:
            self.collapsible.expand()
        else:
            self.collapsible.collapse()

        self.plot_selection(*a)


    def plot_selection(self, *a):
        """Disable the buttons that have a file that contains no data."""
        if hasattr(self, "load_states") and self.load_states:
            self.check_thread = QtCore.QThread()
            self.worker = QtClasses.CheckFiles()
            QtClasses.CheckFiles.gen_path = [self.complete_path, self.root_dict["ROOT Types/Type chosen"]]
            QtClasses.CheckFiles.files = self.buttons_files.items()
            QtClasses.CheckFiles.tree = self.tree

            self.worker.moveToThread(self.check_thread)
            self.check_thread.started.connect(self.worker.start)

            self.worker.finished.connect(self.check_thread.quit)
            self.check_thread.finished.connect(self.check_thread.deleteLater)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.progress.connect(self.update_states)

            self.check_thread.start()
            self.worker.finished.connect(lambda: self.disable_all_buttons(self.states))
            self.load_states = False

        if not hasattr(self, "load_states") and a[0]:
            self.logs.add_log("Did you properly load your folder?")
            self.graph_button_toggling()

        if a[0]:
            try: 
                self.disable_all_buttons(self.states)
                self.graph_button_toggling()
            except: pass
        else:
            self.enable_all_buttons()


    def update_states(self, *a):
        """Updates the states of the buttons"""
        self.states[a[0][0]] = a[0][1]
