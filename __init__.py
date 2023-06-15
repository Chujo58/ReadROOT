import os, sys, matplotlib, json, difflib
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
sys.path.append(path) #FOR C++ TO WORK!

from . import read_root
from . import read_root_gui
from . import read_root_gui_v2
from . import IOClasses
from . import QtClasses

reader = read_root._root_reader
reader_v2 = read_root.root_reader_v2
gui = read_root_gui.GUI
guiv2 = read_root_gui_v2.GUIv2
config = IOClasses.Configuration
setup = IOClasses.SetUpCpp

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



with open("config.json", "r") as f:
    info = json.load(f)

def do_config():
    print(f"{QtClasses.bcolors.BOLD}Available configurations: {QtClasses.bcolors.ENDC}")
    keys_to_print = [key for key in info.keys() if key != "LoadConfig"]
    for index, key in enumerate(keys_to_print):
        print(key, end=", ") if index != len(keys_to_print)-1 else print(key, end=".\n")
        
    user_input = input(f"{QtClasses.bcolors.UNDERLINE}What configuration do you want to use?{QtClasses.bcolors.ENDC} ")
    output = difflib.get_close_matches(user_input, keys_to_print, 1)[0]
    configuration = config(output, "config.json")
    setup("funcs.hpp").load_configuration(configuration)
    setup("wrap.cpp").load_pybind11(configuration)

    print(f"{QtClasses.bcolors.BOLD}Configuration set!{QtClasses.bcolors.ENDC}")
    configuration.config_done()

if info.get("LoadConfig"):
    do_config()
    