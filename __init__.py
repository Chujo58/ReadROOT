import os, sys
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
from . import read_root
from . import read_root_gui

reader = read_root._root_reader
gui = read_root_gui.GUI