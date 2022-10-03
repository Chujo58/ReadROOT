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
import spinmob as _s
import spinmob.egg as _egg
import numpy as _np
import uproot as _ur
import pandas as _pd
import tkinter.filedialog as _fd
import pyqtgraph as _pq
import ctypes as _ct
import pyqtgraph.exporters as _export
import darkdetect as _dd
import re as _re

_g = _egg.gui

class GUI(_root_reader):
    def __init__(self, name='GUI', window_size=[1000,500], show=True, block=True):
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
                                        "Analog Traces Fin Resolution":"SRV_PARAM_ANALOGTR_FINERES_ENABLE"},
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
                                           "Start/stop Δt N channels":"SW_PARAMETER_DIFFERENCE_BINCOUNT",
                                           "Start/stop Δt Tmin":"SW_PARAMETER_TIME_DIFFERENCE_CH_T0",
                                           "Start/stop Δt Tmax":"SW_PARAMETER_TIME_DIFFERENCE_CH_T1",
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
                                                      "Calibration units":"SW_PARAMETER_CH_ENERGY_CALIBRATION_UDM"},
                                "SYNC":{"External clock source":"SRV_PARAM_DT_EXT_CLOCK",
                                        "Start mode":"SRV_PARAM_START_MODE",
                                        "TRG OUT/GPO mode":"SRV_PARAM_TRGOUT_MODE",
                                        "Start delay":"SRV_PARAM_START_DELAY",
                                        "Channel time offset":"SRV_PARAM_CH_TIME_OFFSET"},
                                "ONBOARD COINCIDENCES":{"Coincidence Mode":"SRV_PARAM_COINC_MODE",
                                                        "Coincidence window":"SRV_PARAM_COINC_TRGOUT"},
                                "MISC":{"Label":"SW_PARAMETER_CH_LABEL",
                                        "FPIO type":"SRV_PARAM_IOLEVEL",
                                        "Rate optimization":"SRV_PARAM_EVENTAGGR"}}

        screen_width, screen_height = self.__get_screen_resolution__()
        window_width = int(window_size[0]/1680*screen_width)
        window_height = int(window_size[1]/1050*screen_height)
        scaleFactor = _ct.windll.shcore.GetScaleFactorForDevice(0)/100

        #self.ratio = int(window_width/window_size[0])
        self.ratio = int(scaleFactor)
        
        self.window = _g.Window(name, size=[window_width, window_height], autosettings_path=name+'_window.txt')
        self.window._window
        self.grid_top = self.window.place_object(_g.GridLayout(False)).set_height(50*self.ratio)
        self.window.new_autorow()
        self.grid_bot = self.window.place_object(_g.GridLayout(False), alignment=0)
        self.grid_top.set_column_stretch(1,1)

        #Buttons
        self.button_folder = self.grid_top.place_object(_g.Button('Search\nfolder')).set_width(50*self.ratio).set_height(45*self.ratio)
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
        self.ch0 = self.grid_top.place_object(_g.Button('CH0', True).set_width(50*self.ratio)).set_height(45*self.ratio)
        self.ch1 = self.grid_top.place_object(_g.Button('CH1', True).set_width(50*self.ratio)).set_height(45*self.ratio)
        self.ch2 = self.grid_top.place_object(_g.Button('CH2', True).set_width(50*self.ratio)).set_height(45*self.ratio)
        self.ch3 = self.grid_top.place_object(_g.Button('CH3', True).set_width(50*self.ratio)).set_height(45*self.ratio)

        self.ch0.signal_toggled.connect(self.__channel_buttons__)
        self.ch1.signal_toggled.connect(self.__channel_buttons__)
        self.ch2.signal_toggled.connect(self.__channel_buttons__)
        self.ch3.signal_toggled.connect(self.__channel_buttons__)

        #Plot button
        self.plot = self.grid_top.place_object(_g.Button('Plot').set_width(55*self.ratio)).set_height(45*self.ratio)
        self.plot.signal_clicked.connect(self.__plot__)
        #Clear button
        self.clear = self.grid_top.place_object(_g.Button('Clear').set_width(55*self.ratio)).set_height(45*self.ratio)
        self.clear.signal_clicked.connect(self.__clear__)
        #Save plot button
        self.save = self.grid_top.place_object(_g.Button('Save Plot Image')).set_width(90*self.ratio).set_height(45*self.ratio)
        self.save.signal_clicked.connect(self.__save_image__)

        self.calculate = self.grid_top.place_object(_g.Button('Calculate Results')).set_height(45*self.ratio)
        self.calculate.signal_clicked.connect(self.__calculate__)
        
        #General tab area containing the graph and COMPASS sections
        self.GeneralTabArea = self.grid_bot.place_object(_g.TabArea(name+'_gen_tabs_settings.txt'), alignment=0)
        self.COMPASS = self.GeneralTabArea.add_tab('COMPASS')
        self.GRAPH = self.GeneralTabArea.add_tab('GRAPH')

        #COMPASS
        

        #Tab Area for the plotting settings and the file transformation settings
        self.TabArea = self.GRAPH.place_object(_g.TabArea(name+'_tabs_settings.txt'), alignment=0).set_width(300*self.ratio)

        #Plot settings tab
        self.TabSettings = self.TabArea.add_tab('Plot Settings')
        self.settings = self.TabSettings.place_object(_g.TreeDictionary(name+'_settings.txt', name), 0, 0, alignment=0).set_width(275*self.ratio)

        #Specific Graph settings
        self.GraphSettingsTab = self.TabArea.add_tab('Graph Settings')
        self.graphsettings = self.GraphSettingsTab.place_object(_g.TreeDictionary(name+'_graph_settings.txt', name), 0, 0, alignment=0).set_width(275*self.ratio)
        self.graphsettings.add_parameter(key='Energy Histogram/Energy bins', value = 4096, values=[256, 512, 1024, 2048, 4096, 8192, 16384], suffix='channels', siPrefix=True, tip='How many bins are used for the energy histogram.')
        self.graphsettings.add_parameter(key='Energy Histogram/File selected', value='No file selected', tip='Path of the selected file', readonly=True)
        self.graphsettings.add_parameter(key='Energy Histogram/File name', value='No file selected', tip='Name of the selected file', readonly=True)

        self.graphsettings.add_parameter(key='TOF Histogram/ΔT min', value=-1000, default=-1000, step=1, suffix='ns', siPrefix=True, tip='Smallest value counted for the bins.')
        self.graphsettings.add_parameter(key='TOF Histogram/ΔT max', value=1000, default=1000, step=1, suffix='ns', siPrefix=True, tip='Biggest value counted for the bins.')
        self.graphsettings.add_parameter(key='TOF Histogram/ΔT bins', value=8192, values=[256, 512, 1024, 2048, 4096, 8192], default=8192, suffix='channels', siPrefix=True, tip='How many bins are used for the TOF histogram.')
        self.graphsettings.add_parameter(key='TOF Histogram/File #1', value='No file selected', tip='Start channel path', readonly=True)
        self.graphsettings.add_parameter(key='TOF Histogram/File #2', value='No file selected', tip='Stop channel path', readonly=True)
        self.graphsettings.add_parameter(key='TOF Histogram/File name #1', value='No file selected', tip='Start channel', readonly=True)
        self.graphsettings.add_parameter(key='TOF Histogram/File name #2', value='No file selected', tip='Stop channel', readonly=True)
        
        self.graphsettings.add_parameter(key='MCS Graph/File selected', value='No file selected', tip='Path of the selected file', readonly=True)
        self.graphsettings.add_parameter(key='MCS Graph/File name', value='No file selected', tip='Name of the selected file', readonly=True)


        #Graph type
        self.settings.add_parameter(key='Choose plot/Energy Histogram', value=False)
        self.settings.connect_signal_changed('Choose plot/Energy Histogram', self.__change_graph__)
        self.settings.add_parameter(key='Choose plot/TOF Histogram', value=False)
        self.settings.connect_signal_changed('Choose plot/TOF Histogram', self.__change_graph__)
        self.settings.add_parameter(key='Choose plot/MCS Graph', value=False)        
        self.settings.connect_signal_changed('Choose plot/MCS Graph', self.__change_graph__)

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
        self.TabAreaData = self.GRAPH.place_object(_g.TabArea(name+'_tabs_data.txt'), 1, 0, alignment=0)#.set_width(700*self.ratio)
        self.TabData = self.TabAreaData.add_tab('Data')
        self.data = self.TabData.place_object(_g.DataboxSaveLoad(file_type='.txt', autosettings_path=name+'_data.txt'), alignment=0).set_width(700*self.ratio)
        self.data.enable_save()
        self.TabData.new_autorow()
        self.PlotArea = self.TabData.place_object(_pq.PlotWidget(), alignment=0)
        self.PLT = self.PlotArea.getPlotItem()
        
        self.TabResults = self.TabAreaData.add_tab('Results')
        self.results = self.TabResults.place_object(_g.TreeDictionary(name+'_results.txt', name), 0, 0, alignment=0)
        
        #Range for the calculation
        self.results.add_parameter('Range for calculation/Minimum', float(self.settings['Plot Settings/Axes limits/x min']))
        self.results.add_parameter('Range for calculation/Maximum', float(self.settings['Plot Settings/Axes limits/x max']))

        #Average, standard deviation and median from the data set (READ ONLY)
        self.results.add_parameter(key='Results/Average', value=0.0, readonly=True)
        self.results.add_parameter(key='Results/Median', value=0.0, readonly=True)
        self.results.add_parameter(key='Results/Standard deviation', value=0.0, readonly=True)
        

        
        #Set the default tab opened to the file settings tab:
        self.TabArea.set_current_tab(0)
        #self.filesetlabel = self.TabFileSettings.place_object(_g.Label('Select a folder please.'))

        self.__linecolor__()#Loads the line color for the first time.
        self.__fillcolor__()#Loads the fill color for the first time.

        _s.settings['dark_theme_qt'] = _dd.isDark()
        self.PlotArea.setBackground('white') if _dd.isLight() else self.PlotArea.setBackground('black')
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

    def __change_graph__(self, *a):
        if self.settings['Choose plot/Energy Histogram']:
            self.settings['Plot Settings/Title'] = 'Energy Histogram'
            self.__title__()
            self.settings['Plot Settings/Axes limits/x min'] = 0
            self.settings['Plot Settings/Axes limits/x max'] = self.graphsettings['Energy Histogram/Energy bins']
            self.settings['Plot Settings/Axes limits/y min'] = 0
            self.settings['Plot Settings/Axes limits/y max'] = 5000
            self.__xlim__()
            self.__ylim__()
            self.settings['Plot Settings/Axes label/x'] = 'ADC bins'
            self.settings['Plot Settings/Axes label/y'] = 'Counts'
            self.__ax_labels__()

        if self.settings['Choose plot/TOF Histogram']:
            self.settings['Plot Settings/Title'] = 'TOF Histogram'
            self.__title__()
            self.settings['Plot Settings/Axes limits/x min'] = self.graphsettings['TOF Histogram/ΔT min']
            self.settings['Plot Settings/Axes limits/x max'] = self.graphsettings['TOF Histogram/ΔT max']
            self.settings['Plot Settings/Axes limits/y min'] = 0.5
            self.settings['Plot Settings/Axes limits/y max'] = 5000
            self.__xlim__()
            self.__ylim__()
            self.settings['Plot Settings/Axes label/x'] = 'ΔT (ns)'
            self.settings['Plot Settings/Axes label/y'] = 'Counts'
            self.__ax_labels__()

        if self.settings['Choose plot/MCS Graph']:
            data = _root_reader.__MCSgraph__(self, self.graphsettings['MCS Graph/File selected'])

            self.data['x'] = data[0]
            self.data['y'] = data[1]
            self.settings['Plot Settings/Title'] = 'MCS Graph'
            self.__title__()
            self.settings['Plot Settings/Axes limits/x min'] = 0
            self.settings['Plot Settings/Axes limits/x max'] = self.data['x'][-1]
            self.settings['Plot Settings/Axes limits/y min'] = 0
            self.settings['Plot Settings/Axes limits/y max'] = 100
            self.settings['Plot Settings/Axes label/x'] = 'Time (s)'
            self.settings['Plot Settings/Axes label/y'] = 'Event rate'
            self.__ax_labels__()

    def __plot__(self, *a):
        if self.settings['Choose plot/Energy Histogram']:
            data = _root_reader.__energyhist__(self, self.graphsettings['Energy Histogram/File selected'], int(self.graphsettings['Energy Histogram/Energy bins']), tree=self.tree)

            self.data['x'] = data[0]
            self.data['y'] = data[1]

            self.__load_all__()
            curve_name = self.settings['Plot Settings/Title'] + '-' + self.file_settings['Files Settings/Folder']

            curve = _pq.PlotCurveItem(self.data['x'], self.data['y'], stepMode='left', fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)

            self.PLT.addItem(curve)

        elif self.settings['Choose plot/TOF Histogram']:
            data = _root_reader.__tofhist__(self, self.graphsettings['TOF Histogram/File #1'], self.graphsettings['TOF Histogram/File #2'], self.graphsettings['TOF Histogram/ΔT min'], self.graphsettings['TOF Histogram/ΔT max'], int(self.graphsettings['TOF Histogram/ΔT bins']), tree=self.tree)
            self.results['Results/Average'] = self.average(data[2])
            self.results['Results/Median'] = self.median(data[2])
            self.results['Results/Standard deviation'] = self.standard_deviation(data[2])

            self.data['x'] = data[0]
            self.data['y'] = data[1]

            self.__load_all__()
            curve_name = self.settings['Plot Settings/Title'] + '-' + self.file_settings['Files Settings/Folder']
            #if self.settings['Plot Settings/Log scale/y']:
                #self.data['y'] = _np.where(self.data['y'] == 0, _np.nan, self.data['y'])
                #print(self.data['y'])
            curve = _pq.PlotCurveItem(self.data['x'], self.data['y'], stepMode=True, fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)

            #self.PLT.addItem(curve)
            self.PLT.plot(self.data['x'], self.data['y'], stepMode=True, fillLevel=0.5, brush=self.brush, pen=self.pen, name=curve_name)
            #PlotItem = self.PLT.getPlotItem()
            #PlotItem.plot(self.data['x'], self.data['y'], stepMode=True, fillLevel=0, brush=self.brush, pen=self.pen)

        elif self.settings['Choose plot/MCS Graph']:
            data = _root_reader.__MCSgraph__(self, self.graphsettings['MCS Graph/File selected'], tree=self.tree)

            self.data['x'] = data[0]
            self.data['y'] = data[1]

            self.__load_all__()
            curve_name = self.settings['Plot Settings/Title'] + '-' + self.file_settings['Files Settings/Folder']

            curve = _pq.PlotCurveItem(self.data['x'], self.data['y'], fillLevel=0, brush=self.brush, pen=self.pen, name=curve_name)

            self.PLT.addItem(curve)
    
    def __clear__(self, *a):
        """
        Clears the graph.
        """
        self.PLT.clear()

    def __save_image__(self, *a):
        """
        Saves an image of the graph in the SCREENSHOTS folder.
        """
        exporter = _export.ImageExporter(self.PlotArea.plotItem)
        exporter.export(self.folder_path+'\SCREENSHOTS\\' + self.settings['Plot Settings/Title'] +'.png')
    
    def __calculate__(self, *a):
        if self.settings['Choose plot/Energy Histogram']:
            data = _root_reader.__energyhist__(self, self.graphsettings['Energy Histogram/File selected'], int(self.graphsettings['Energy Histogram/Energy bins']), tree=self.tree)

            values_kept = []

            for value in data[2]:
                if self.results['Range for calculation/Minimum'] <= value <= self.results['Range for calculation/Maximum']:
                    values_kept.append(value)

            self.results['Results/Average'] = self.average(values_kept)
            self.results['Results/Median'] = self.median(values_kept)
            self.results['Results/Standard deviation'] = self.standard_deviation(values_kept)

        elif self.settings['Choose plot/TOF Histogram']:
            data = _root_reader.__tofhist__(self, self.graphsettings['TOF Histogram/File #1'], self.graphsettings['TOF Histogram/File #2'], self.graphsettings['TOF Histogram/ΔT min'], self.graphsettings['TOF Histogram/ΔT max'], int(self.graphsettings['TOF Histogram/ΔT bins']), tree=self.tree)

            values_kept = []

            for value in data[2]:
                if self.results['Range for calculation/Minimum'] <= value <= self.results['Range for calculation/Maximum']:
                    values_kept.append(value)

            self.results['Results/Average'] = self.average(values_kept)
            self.results['Results/Median'] = self.median(values_kept)
            self.results['Results/Standard deviation'] = self.standard_deviation(values_kept)

        elif self.settings['Choose plot/MCS Graph']:
            data = _root_reader.__MCSgraph__(self, self.graphsettings['MCS Graph/File selected'], tree=self.tree)

            values_kept = []

            for value in data[2]:
                if self.results['Range for calculation/Minimum'] <= value <= self.results['Range for calculation/Maximum']:
                    values_kept.append(value)

            self.results['Results/Average'] = self.average(values_kept)
            self.results['Results/Median'] = self.median(values_kept)
            self.results['Results/Standard deviation'] = self.standard_deviation(values_kept)

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

    def __grid__(self, *a):
        """
        Shows the grid of the graph for both axis.
        """
        self.PLT.showGrid(x=self.settings['Plot Settings/Grid/x'], y=self.settings['Plot Settings/Grid/y'])

    def __ax_labels__(self, *a):
        """
        Sets the labels of the axes of the graph.
        """
        self.PLT.setLabel(axis='left', text=self.settings['Plot Settings/Axes label/y'])
        self.PLT.setLabel(axis='bottom', text=self.settings['Plot Settings/Axes label/x'])

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
        self.pen = _pq.mkPen(self.settings['Plot Settings/Line Color/Red'], self.settings['Plot Settings/Line Color/Green'], self.settings['Plot Settings/Line Color/Blue'], self.settings['Plot Settings/Line Color/Alpha'])

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
                self.run_info = file
        
        self.__settings_folder_changed__()#Loads the files for the first time.
        

    def __getfiles__(self, folder_path):
        allfiles = _os.listdir(folder_path)
        root_files = []
        for file in allfiles:
            if file.endswith(".root"):
                root_files.append(file)

        return root_files
        
    def __settings_folder_changed__(self, *a):
        """
        Reloads the files from the chosen folder.
        """
        self.folder_containing_root = self.folder_path + '\\' + self.file_settings['Files Settings/Folder']
        self.files = self.__getfiles__(self.folder_containing_root)
        if self.file_settings['Files Settings/Folder'] == 'FILTERED':
            self.tree = 'Data_F'
        elif self.file_settings['Files Settings/Folder'] == 'UNFILTERED':
            self.tree = 'Data'
        elif self.file_settings['Files Settings/Folder'] == 'RAW':
            self.tree = 'Data_R'

        self.__channel_buttons__
                        
    def __channel_buttons__(self, *a): 
        ch0_state = self.ch0.is_checked()
        ch1_state = self.ch1.is_checked()
        ch2_state = self.ch2.is_checked()
        ch3_state = self.ch3.is_checked()
     
        ch0_filepath = self.folder_containing_root + '\\' + self.files[0]
        ch1_filepath = self.folder_containing_root + '\\' + self.files[1]
        ch2_filepath = self.folder_containing_root + '\\' + self.files[2]
        ch3_filepath = self.folder_containing_root + '\\' + self.files[3]            

        if ch0_state:
            self.file_label.set_text('CH0')
            self.graphsettings['Energy Histogram/File selected'] = ch0_filepath
            self.graphsettings['Energy Histogram/File name'] = 'CH0'
            self.graphsettings['MCS Graph/File selected'] = ch0_filepath
            self.graphsettings['MCS Graph/File name'] = 'CH0'

            if ch1_state:
                self.file_label.set_text('CH0&CH1')
                self.graphsettings['TOF Histogram/File #1'] = ch0_filepath
                self.graphsettings['TOF Histogram/File name #1'] = 'CH0'
                self.graphsettings['TOF Histogram/File #2'] = ch1_filepath
                self.graphsettings['TOF Histogram/File name #2'] = 'CH1'
                
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
                    self.graphsettings['TOF Histogram/File #1'] = ch0_filepath
                    self.graphsettings['TOF Histogram/File name #1'] = 'CH0'
                    self.graphsettings['TOF Histogram/File #2'] = ch2_filepath
                    self.graphsettings['TOF Histogram/File name #2'] = 'CH2'
                    if ch3_state:
                        self.file_label.set_text('CH0&CH2&CH3')
                else:
                    if ch3_state:
                        self.file_label.set_text('CH0&CH3')
                        self.graphsettings['TOF Histogram/File #1'] = ch0_filepath
                        self.graphsettings['TOF Histogram/File name #1'] = 'CH0'
                        self.graphsettings['TOF Histogram/File #2'] = ch3_filepath
                        self.graphsettings['TOF Histogram/File name #2'] = 'CH3'
        else:
            if ch1_state:
                self.file_label.set_text('CH1')
                self.graphsettings['Energy Histogram/File selected'] = ch1_filepath
                self.graphsettings['Energy Histogram/File name'] = 'CH1'
                self.graphsettings['MCS Graph/File selected'] = ch1_filepath
                self.graphsettings['MCS Graph/File name'] = 'CH1'
                if ch2_state:
                    self.file_label.set_text('CH1&CH2')
                    self.graphsettings['TOF Histogram/File #1'] = ch1_filepath
                    self.graphsettings['TOF Histogram/File name #1'] = 'CH1'
                    self.graphsettings['TOF Histogram/File #2'] = ch2_filepath
                    self.graphsettings['TOF Histogram/File name #2'] = 'CH2'
                    if ch3_state:
                        self.file_label.set_text('CH1&CH2&CH3')
                else:
                    if ch3_state:
                        self.file_label.set_text('CH1&CH3')
                        self.graphsettings['TOF Histogram/File #1'] = ch1_filepath
                        self.graphsettings['TOF Histogram/File name #1'] = 'CH1'
                        self.graphsettings['TOF Histogram/File #2'] = ch3_filepath
                        self.graphsettings['TOF Histogram/File name #2'] = 'CH3'
            else:
                if ch2_state:
                    self.file_label.set_text('CH2')
                    self.graphsettings['Energy Histogram/File selected'] = ch2_filepath
                    self.graphsettings['Energy Histogram/File name'] = 'CH2'
                    self.graphsettings['MCS Graph/File selected'] = ch2_filepath
                    self.graphsettings['MCS Graph/File name'] = 'CH2'
                    if ch3_state:
                        self.file_label.set_text('CH2&CH3')
                        self.graphsettings['TOF Histogram/File #1'] = ch2_filepath
                        self.graphsettings['TOF Histogram/File name #1'] = 'CH2'
                        self.graphsettings['TOF Histogram/File #2'] = ch3_filepath
                        self.graphsettings['TOF Histogram/File name #2'] = 'CH3'
                else:
                    if ch3_state:
                        self.file_label.set_text('CH3')
                        self.graphsettings['Energy Histogram/File selected'] = ch3_filepath
                        self.graphsettings['Energy Histogram/File name'] = 'CH3'
                        self.graphsettings['MCS Graph/File selected'] = ch3_filepath
                        self.graphsettings['MCS Graph/File name'] = 'CH3'
                    else:
                        self.file_label.set_text('No file selected')
                        self.graphsettings['Energy Histogram/File selected'] = 'No file selected'
                        self.graphsettings['Energy Histogram/File name'] = 'No file selected'
                        self.graphsettings['TOF Histogram/File #1'] = 'No file selected'
                        self.graphsettings['TOF Histogram/File #2'] = 'No file selected'
                        self.graphsettings['TOF Histogram/File name #1'] = 'No file selected'
                        self.graphsettings['TOF Histogram/File name #2'] = 'No file selected'


if __name__ == '__main__':
    self = GUI()