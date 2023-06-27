from PyQt5 import QtCore, QtWidgets, QtGui
from spinmob.egg import gui as g
import time, os, superqt
import read_root

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

class IconLabel(QtWidgets.QWidget):
    IconSize = QtCore.QSize(16,16)
    HorizontalSpacing = 2

    def __init__(self, icon_url: str, text: str, width: int, final_stretch=True):
        """Makes a QLabel with an icon attached to it's left.

        Parameters
        ----------
        icon_url : str
            The image to use for the icon
        text : str
            The text to use for the label
        width : int
            Size of the widget
        final_stretch : bool, optional
            If we stretch the final widget, by default True
        """
        super(QtWidgets.QWidget, self).__init__()

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        icon = QtWidgets.QLabel()
        icon.setPixmap(QtGui.QIcon(icon_url).pixmap(self.IconSize))

        text_widget = QtWidgets.QLabel(text)
        text_widget.setFixedWidth(width)

        layout.addWidget(icon)
        layout.addSpacing(self.HorizontalSpacing)
        layout.addWidget(text_widget)

        if final_stretch:
            layout.addStretch()
    
    @staticmethod
    def new_icon_size(size: int):
        return QtCore.QSize(size, size)

class Seperator(QtWidgets.QWidget):
    def __init__(self, size: int, space_size: int, left: int=None, right: int=None):
        super(QtWidgets.QWidget, self).__init__()

        left = space_size if left is None else left
        right = space_size if right is None else right

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        left_grid = QtWidgets.QWidget()
        left_grid.setFixedWidth(left)

        line = QtWidgets.QFrame()
        line.setMinimumWidth(size)
        line.setFixedHeight(1)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("border: 5px solid black")

        right_grid = QtWidgets.QWidget()
        right_grid.setFixedWidth(right)

        layout.addWidget(left_grid)
        layout.addWidget(line)
        layout.addWidget(right_grid)

class CheckFiles(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(list)
    gen_path = []
    files = []
    tree = ""

    def start(self):
        for index, (key, file) in enumerate(self.files):
            root = read_root.root_reader_v2(os.path.join(*self.gen_path, file), self.tree)
            data = root.open()
            if data is None:
                self.progress.emit([int(key),False])
                continue
            self.progress.emit([int(key),True])
        self.finished.emit()
            
class SelectionBox(QtCore.QObject):
    on_save = QtCore.pyqtSignal(str)
    def __init__(self, default_text: str = None):
        super(QtCore.QObject, self).__init__()
        self.grid = g.GridLayout(False)
        default = [] if default_text is None else [default_text]
        self._searchable_combo = self.grid.place_object(g.ComboBox(default))
    
    def add_button(self, button=None):
        self._save_btn = self.grid.place_object(g.Button(" ")) if button is None else button
        self._save_btn.signal_clicked.connect(self._save_btn_clicked)

    def add_items(self, items):
        for item in items:
            self._searchable_combo.add_item(item)        

    def clear(self):
        self._searchable_combo.clear()

    def _save_btn_clicked(self, *a):
        self.on_save.emit(self._searchable_combo.get_text())

    def set_height(self, value):
        self._searchable_combo.set_height(value)
        # self._save_btn.set_height(value).set_width(value)

    def set_width(self, value):
        self._searchable_combo.set_width(value)

    def setStyleSheet(self, style_sheet):
        self._searchable_combo._widget.setStyleSheet(style_sheet)

    def get_text(self):
        return self._searchable_combo.get_text()

    def disable(self):
        self._searchable_combo.disable()
        self._save_btn.disable()

    def enable(self):
        self._searchable_combo.enable()
        self._save_btn.enable()

    



if __name__ == "__main__":
    w = g.Window()
    obj = SelectionBox()
    obj.change_icon("SelectDark.png")
    obj.set_height(75)
    t = w.place_object(obj.grid)
    to_add = list(os.listdir("Images"))
    obj.add_items(to_add)
    obj.on_save.connect(lambda x: print(x))
    w.show(True)