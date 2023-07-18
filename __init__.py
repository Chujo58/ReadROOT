import os, sys, matplotlib, json, difflib
running_directory = os.getcwd() #This is to make the relative import work!
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
sys.path.append(path) #FOR C++ TO WORK!

from . import read_root
from . import read_root_gui
from . import read_root_gui_v2
from . import IOClasses
from . import QtClasses
from . import root_plotter

reader = read_root._root_reader
reader_v2 = read_root.root_reader_v2
gui = read_root_gui.GUI
guiv2 = read_root_gui_v2.GUIv2
fileexp = IOClasses.FileExplorer
config = IOClasses.Configuration
setup = IOClasses.SetUpCpp
plotter = root_plotter.RootPlotter

#Make the colormaps:
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

black_turbo_list = [
    (0, '#000000'),
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

white_turbo = matplotlib.colors.LinearSegmentedColormap.from_list('white_turbo', white_turbo_list, N=256)
black_turbo = matplotlib.colors.LinearSegmentedColormap.from_list('black_turbo', black_turbo_list, N=256)
matplotlib.colormaps.register(white_turbo)
matplotlib.colormaps.register(black_turbo)

from colorama import init
from termcolor import cprint

with open("config.json", "r") as f:
    info = json.load(f)

def do_config():
    os.chdir(path)
    init()
    cprint("Available configurations: ", "cyan", attrs=["bold"])
    keys_to_print = [key for key in info.keys() if key != "LoadConfig"]
    for index, key in enumerate(keys_to_print):
        print(key, end=", ") if index != len(keys_to_print)-1 else print(key, end=".\n")
        
    cprint("What configuration do you want to use? ", "light_grey", attrs=["underline"])
    user_input = input()
    output = difflib.get_close_matches(user_input, keys_to_print, 1)[0]
    configuration = config(output, "config.json")
    setup("funcs.hpp").load_configuration(configuration)
    setup("wrap.cpp").load_pybind11(configuration)

    cprint("Configuration set!", "cyan", attrs=["bold"])
    configuration.config_done()
    os.chdir(running_directory)

if info.get("LoadConfig"):
    do_config()

os.chdir(running_directory)