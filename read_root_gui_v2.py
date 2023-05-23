#----------------------------------------------------------------------------
# Created by : Chloé Legué
# Current version date : 2023/05
# Version = 1.1
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
root_reader = read_root._root_reader
from . import XML_Parser
InfoParser = XML_Parser.InfoParser
XMLParser = XML_Parser.XMLParser
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
from PyQt5 import QtGui, QtWidgets
import time
from scipy.optimize import curve_fit as cf
from . import ErrorPropagation as ep
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm

g = egg.gui

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


class GUIv2(root_reader):
    def __init__(self, name="GUI", window_size=[1000,500], show=True, block=True, ratio=None):
        self.ratio = int(ct.windll.shcore.GetScaleFactorForDevice(0)/100) if ratio is None else ratio #This is used to scale the GUI on different screen resolutions. Note that this will only work on Windows.
        self.dark_theme_on = dd.isDark()
        width, height = self.get_screen_resolution()
        width = int(window_size[0]/1680*width)
        height = int(window_size[1]/1050*height)

        primary, secondary, accent = self.create_colors()

        window = g.Window(name, size=[width, height], autosettings_path=name+"_window.txt")
        window._window.setWindowIcon(QtGui.QIcon("Images/CoMPASS/icon64x64.ico"))

        self.TopGrid = window.place_object(g.GridLayout(True)).set_height(50*self.ratio)#.set_width(1273*self.ratio)
        window.new_autorow()
        self.BotGrid = window.place_object(g.GridLayout(True), alignment=0)
        
        #Change the top grid's color.
        self.TopGrid._widget.setAutoFillBackground(True)
        temp_palette = self.TopGrid._widget.palette()
        temp_palette.setColor(self.TopGrid._widget.backgroundRole(), accent)
        self.TopGrid._widget.setPalette(temp_palette)
        self.TopGrid.set_column_stretch(1,1)

        #Generate the top grid
        self.generate_top_grid()
        #Change the color and icons of tree dictionary for the ROOT type
        temp_widget = self.root_dict._widget
        dark_tree = """
            QTreeView {
                background-color: rgb(23, 35, 38);
                selection-background-color: rgb(32, 81, 96);
            }
        """
        light_tree = """
            QTreeView {
                background-color: rgb(24, 132, 165);
                selection-background-color: rgb(32, 81, 96);
            }
        """
        temp_widget.setStyleSheet(dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(light_tree)

        a = self.root_dict.get_widget("ROOT Types")
        a.setIcon(0,QtGui.QIcon("Images/file_config.png"))

        #Generate the bot grid
        self.generate_bot_grid()

        #Change the color and icons of tree dictionary for the run info
        temp_widget = self.run_dict._widget
        temp_widget.setStyleSheet(dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(light_tree)

        a = self.run_dict.get_widget("Run Info")
        a.setIcon(0,QtGui.QIcon("Images/info.png"))

        #Change the color and icons of tree dictionaries for the board info
        temp_widget = self.board_dict_1._widget
        temp_widget.setStyleSheet(dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(light_tree)

        a = self.board_dict_1.get_widget("Board Info")
        a.setIcon(0,QtGui.QIcon("Images/info.png"))

        temp_widget = self.board_dict_2._widget
        temp_widget.setStyleSheet(dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(light_tree)

        temp_widget = self.board_dict_3._widget
        temp_widget.setStyleSheet(dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(light_tree)

        #Change the color and icons of tree dictionary for the plot settings
        temp_widget = self.plot_settings_dict._widget
        temp_widget.setStyleSheet(dark_tree) if self.dark_theme_on else temp_widget.setStyleSheet(light_tree)

        a = self.plot_settings_dict.get_widget("General Settings")
        a.setIcon(0,QtGui.QIcon("Images/settings.png"))
        
        a = self.plot_settings_dict.get_widget("Axis")
        a.setIcon(0,QtGui.QIcon("Images/axis.png"))

        a = self.plot_settings_dict.get_widget("Grid")
        a.setIcon(0,QtGui.QIcon("Images/grid.png"))

        a = self.plot_settings_dict.get_widget("Line")
        a.setIcon(0,QtGui.QIcon("Images/line.png"))

        #Make the grid layout for the plot buttons another color:
        self.inner_left._widget.setAutoFillBackground(True)
        temp_palette = self.inner_left._widget.palette()
        temp_palette.setColor(self.inner_left._widget.backgroundRole(), accent)
        self.inner_left._widget.setPalette(temp_palette)

        s.settings["dark_theme_qt"] = self.dark_theme_on

        if show: window.show(block)
    
    def get_screen_resolution(self):
        user32 = ct.windll.user32
        user32.SetProcessDPIAware()
        return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))

    def generate_top_grid(self):
        #Search folder button
        search_folder_btn = self.TopGrid.place_object(g.Button(" ",tip="Search a folder!")).set_width(45*self.ratio).set_height(45*self.ratio)
        search_folder_btn.set_style_unchecked(style="image: url(Images/OpenFolder.png)")
        search_folder_btn.signal_clicked.connect(self.search_folder)

        #File type (Raw, unfiltered, filtered)
        self.root_dict = self.TopGrid.place_object(g.TreeDictionary(), alignment=0).set_width(245*self.ratio).set_height(40*self.ratio)
        self.root_dict.add_parameter("ROOT Types/Type chosen",values=["RAW","UNFILTERED","FILTERED"])#.set_width(150*self.ratio)

        #Label to show what file was selected
        self.folder_label = self.TopGrid.place_object(g.Label("No file selected!"))

        #Channel Buttons
        ch0_btn = self.TopGrid.place_object(g.Button(" ", True,tip="Channel 0")).set_width(45*self.ratio).set_height(45*self.ratio)
        ch0_btn.set_style_unchecked(style="image: url(Images/Off0.png)")
        ch0_btn.set_style_checked(style="image: url(Images/On0.png); border: 2px solid rgb(1,196,255); background: rgb(54,54,54)") if self.dark_theme_on else ch0_btn.set_style_checked(style="image: url(Images/On0.png); border: 2px solid rgb(1,196,255); background: rgb(220,220,220)")

        ch1_btn = self.TopGrid.place_object(g.Button(" ", True,tip="Channel 1")).set_width(45*self.ratio).set_height(45*self.ratio)
        ch1_btn.set_style_unchecked(style="image: url(Images/Off1.png)")
        ch1_btn.set_style_checked(style="image: url(Images/On1.png); border: 2px solid rgb(1,196,255); background: rgb(54,54,54)") if self.dark_theme_on else ch1_btn.set_style_checked(style="image: url(Images/On1.png); border: 2px solid rgb(1,196,255); background: rgb(220,220,220)")

        ch2_btn = self.TopGrid.place_object(g.Button(" ", True,tip="Channel 2")).set_width(45*self.ratio).set_height(45*self.ratio)
        ch2_btn.set_style_unchecked(style="image: url(Images/Off2.png)")
        ch2_btn.set_style_checked(style="image: url(Images/On2.png); border: 2px solid rgb(1,196,255); background: rgb(54,54,54)") if self.dark_theme_on else ch2_btn.set_style_checked(style="image: url(Images/On2.png); border: 2px solid rgb(1,196,255); background: rgb(220,220,220)")

        ch3_btn = self.TopGrid.place_object(g.Button(" ", True,tip="Channel 3")).set_width(45*self.ratio).set_height(45*self.ratio)
        ch3_btn.set_style_unchecked(style="image: url(Images/Off3.png)")
        ch3_btn.set_style_checked(style="image: url(Images/On3.png); border: 2px solid rgb(1,196,255); background: rgb(54,54,54)") if self.dark_theme_on else ch3_btn.set_style_checked(style="image: url(Images/On3.png); border: 2px solid rgb(1,196,255); background: rgb(220,220,220)")

        self.TopGrid.place_object(g.GridLayout()).set_width(680*self.ratio)

    def generate_bot_grid(self):
        main_tab_area = self.BotGrid.place_object(g.TabArea(), alignment=0)
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

    def generate_graph_tab(self):
        grid_left = self.graph_tab.place_object(g.GridLayout(False), alignment=0)
        grid_right = self.graph_tab.place_object(g.GridLayout(False), alignment=0).set_width(300*self.ratio)

        #Make some grids inside the right side grid.
        grid_top = grid_right.place_object(g.GridLayout(False),1,1).set_height(50*self.ratio)
        grid_bot = grid_right.place_object(g.GridLayout(False),1,2)

        #Make the line selection center:
        self.line_selector = grid_top.place_object(g.ComboBox(items=["No lines for now."])).set_width(195*self.ratio).set_height(45*self.ratio)
        self.line_selector._widget.setStyleSheet("background-color: rgb(32, 81, 96)")
        
        save_btn = grid_top.place_object(g.Button(" ")).set_height(45*self.ratio).set_width(45*self.ratio)
        save_btn.set_style_unchecked(style="image: url(Images/save.png)")

        delete_btn = grid_top.place_object(g.Button(" ")).set_height(45*self.ratio).set_width(45*self.ratio)
        delete_btn.set_style_unchecked(style="image: url(Images/delete.png)")

        self.plot_settings_dict = grid_bot.place_object(g.TreeDictionary(),alignment=0).set_width(295*self.ratio)
        self.plot_settings_dict._widget.setHeaderLabels(["Parameters long","Value"])
        self.plot_settings_dict.add_parameter("General Settings/Title", value=" ")
        
        self.plot_settings_dict.add_parameter("Line/Name",value=" ")
        add_color(self.plot_settings_dict, "Line/Pen Color",True)
        add_color(self.plot_settings_dict, "Line/Brush Color",True)

        self.plot_settings_dict.add_parameter("Grid/X Axis",value=True)
        self.plot_settings_dict.add_parameter("Grid/Y Axis",value=True)

        self.plot_settings_dict.add_parameter("Axis/X Label", value=" ")
        self.plot_settings_dict.add_parameter("Axis/Y Label", value=" ")
        self.plot_settings_dict.add_parameter("Axis/X Log Scale", value=False)
        self.plot_settings_dict.add_parameter("Axis/Y Log Scale", value=False)
        self.plot_settings_dict.add_parameter("Axis/Min X",value=0)
        self.plot_settings_dict.add_parameter("Axis/Max X",value=100)
        self.plot_settings_dict.add_parameter("Axis/Min Y",value=0)
        self.plot_settings_dict.add_parameter("Axis/Max Y",value=100)

        #Make the plotting region
        self.inner_left = grid_left.place_object(g.GridLayout(False), alignment=0).set_width(40*self.ratio)
        inner_right = grid_left.place_object(g.GridLayout(False), alignment=0)
        
        #Add the buttons for the different plots:
        self.energy_btn = self.make_comp_btn(self.inner_left, "Plot the energy histogram", "Images/EnergyHist.png", column=1, row=1)
                
        self.psd_btn = self.make_comp_btn(self.inner_left, "Plot the PSD histogram", "Images/PSDHist.png", column=1, row=2)
        
        self.time_btn = self.make_comp_btn(self.inner_left, "Plot the time histogram", "Images/TimeHist.png", column=1, row=3)

        self.tof_btn = self.make_comp_btn(self.inner_left, "Plot the TOF (time of flight) histogram", "Images/TOFHist.png", column=1, row=4)

        self.psdvse_btn = self.make_comp_btn(self.inner_left, "Show the PSD vs Energy Histogram", "Images/PSDvsEnergyHist.png", column=1, row=5)

        self.mcs_btn = self.make_comp_btn(self.inner_left, "Plot the MCS graph", "Images/MCS Graph.png", column=1, row=6)


        #Adding the databox and the plot
        self.databox = inner_right.place_object(g.DataboxSaveLoad(file_type='.txt'), alignment=0)
        self.databox.enable_save()
        inner_right.new_autorow()
        plot_region = inner_right.place_object(pg.PlotWidget(), alignment=0)
        plot_region.setBackground("black") if self.dark_theme_on else plot_region.setBackground("white")
        self.plot = plot_region.getPlotItem()

    def make_comp_btn(self, parent, tip_text, url_image, **kwargs):
        btn = parent.place_object(g.Button(" ", checkable=True, tip=tip_text), alignment=0, **kwargs).set_height(35*self.ratio).set_width(35*self.ratio)
        btn.set_style_checked(style=f"image: url({url_image}); border: 2px solid rgb(1,196,255); background: rgb(54,54,54)") if self.dark_theme_on else btn.set_style_checked(style=f"image: url({url_image}); border: 2px solid rgb(1,196,255); background: rgb(220,220,220)") 
        btn.set_style_unchecked(style=f"image: url({url_image})")
        return btn

    def create_colors(self):
        primary_color = QtGui.QColor("#01c4ff")
        secondary_color = QtGui.QColor("#0baada")
        accent_color = QtGui.QColor("#205160")
        return primary_color, secondary_color, accent_color

    def search_folder(self):
        tkinter_result = fd.askdirectory()
        self.complete_path = os.path.realpath(tkinter_result)
        self.folder_label.set_text(self.complete_path.split('\\')[-1])
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

        xml_parser = XMLParser(xml_file_path)
        board_properties = xml_parser.get_board_properties()

        for index, board_prop_number in enumerate([0,3,6,8]):
            keys = list(self.board_dict_1.get_keys())
            self.board_dict_1[keys[index]] = board_properties[board_prop_number]

        for index, board_prop_number in enumerate([1,4,7]):
            keys = list(self.board_dict_2.get_keys())
            self.board_dict_2[keys[index]] = board_properties[board_prop_number] 

        for index, board_prop_number in enumerate([2,5,9]):
            keys = list(self.board_dict_3.get_keys())
            self.board_dict_3[keys[index]] = board_properties[board_prop_number]

        