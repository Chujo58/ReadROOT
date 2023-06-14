import os, sys, matplotlib
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
sys.path.append(path) #FOR C++ TO WORK!

from . import read_root
from . import read_root_gui
from . import read_root_gui_v2

reader = read_root._root_reader
reader_v2 = read_root.root_reader_v2
gui = read_root_gui.GUI
guiv2 = read_root_gui_v2.GUIv2

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