import os, sys
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
sys.path.append(path) #FOR C++ TO WORK!

from . import read_root
from . import read_root_gui
from . import read_root_gui_v2

reader = read_root._root_reader
gui = read_root_gui.GUI
guiv2 = read_root_gui_v2.GUIv2