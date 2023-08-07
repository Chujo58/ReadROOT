import typing
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget
from spinmob.egg import gui as g
import datetime, os, superqt
import read_root
from playsound import playsound

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
            path = os.path.join(*self.gen_path, file)
            root = read_root.root_reader_v2(path, self.tree)
            if os.stat(path).st_size/(1024*1024) >= 20:
                self.progress.emit([int(key),True])
                continue
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

#New version of the SelectionBox class!
class Selecter(QtCore.QObject):
    keep = QtCore.pyqtSignal(str)
    On = QtCore.pyqtSignal(bool)
    dark_theme = True
    def __init__(self, default_text: str = None, parent = None) -> None:
        super(QtCore.QObject, self).__init__()
        self.grid = g.GridLayout(False)
        self.parent = parent

        default = [] if default_text is None else [default_text]
        self.combo = self.grid.place_object(g.ComboBox(default))
        self.button = self.grid.place_object(g.Button(" ", True))
        self.button.signal_clicked.connect(self.__emit_changes)

    def show(self):
        if self.parent is not None:
            self.parent.place_object(self.grid)

    def __emit_changes(self):
        if self.button.is_checked():
            self.keep.emit(self.combo.get_text())
        self.On.emit(self.button.is_checked())

    def is_checked(self):
        return self.button.is_checked()
    
    def set_checked(self, state: bool):
        self.button.set_checked(state)
    
    def change_combo(self, style_sheet):
        self.combo._widget.setStyleSheet(style_sheet)

    def change_button(self, button_icon_on: str, button_icon_off: str, button_icon_disabled: str, button_highlight_color: tuple):
        list_color = [str(i) for i in button_highlight_color]
        string_color = ",".join(list_color)
        QSS = """
            QPushButton {
        """ + f"image: url({button_icon_off});" + """
            }

            QPushButton::checked{
        """ + f"image: url({button_icon_on});" + """
        """ + f"border: 2px solid rgb({string_color});" + """
        """ + f"background: {'rgb(54,54,54)' if Selecter.dark_theme else 'rgb(220,220,220)'};" + """
            }

            QPushButton::disabled{
        """ + f"image: url({button_icon_disabled});" + """
        """ + f"background: {'rgb(54,54,54)' if Selecter.dark_theme else 'rgb(220,220,220)'};" + """
            }
        """
        self.button._widget.setStyleSheet(QSS)

    def set_width(self, width):
        self.combo.set_width(width)
   
    def set_height(self, height):
        self.combo.set_height(height)
        self.button.set_height(height).set_width(height)

    def add_items(self, items):
        for item in items:
            self.combo.add_item(item)

    def add_item(self, item):
        self.add_items([item])

    def clear(self):
        self.combo.clear()

    def disable(self):
        self.combo.disable()
        self.button.disable()

    def enable(self):
        self.combo.enable()
        self.button.enable()

    def get_text(self):
        return self.combo.get_text()

    
class TextBox(QtWidgets.QWidget):
    text_modified = QtCore.pyqtSignal(int) # Plain text 0, HTML 1 and MD 2.
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.text_zone = QtWidgets.QTextEdit()
        self.text_zone.setReadOnly(True)

        layout.addWidget(self.text_zone)

    def set_width(self, width: int):
        self.text_zone.setMinimumWidth(width)

    def add_text(self, text: str):
        self.text_zone.append(text)
        self.text_modified.emit(0)

    def add_html(self, html: str):
        self.text_zone.insertHtml(html)
        self.text_modified.emit(1)

    def add_md(self, md: str):
        self.text_zone.setMarkdown(md)
        self.text_modified.emit(2)

    def clear(self):
        self.text_zone.clear()

class Logger(QtCore.QObject):
    start_tab = 0
    text_width = 500
    def __init__(self, parent: g.TabArea) -> None:
        super(QtCore.QObject, self).__init__()

        self._parent = parent
        self.log_tab = self._parent.add_tab("Logs")

        self.index = self._parent.objects.index(self.log_tab)
        self.new_logs = 0
        self.change_icon()
        
        self.text = self.log_tab.place_object(TextBox())
        self.text.set_width(self.text_width)

        self.text.text_modified.connect(self.change_icon)
        self._parent.signal_switched.connect(self.changed_tab)

        self.previous_tab = self.start_tab

    def change_icon(self):
        if hasattr(self, "new_logs") and self.new_logs <= 9:
            self._parent._widget.setTabIcon(self.index, QtGui.QIcon(f"Images/Log/{self.new_logs}.png"))
        elif self.new_logs >= 9:
            self._parent._widget.setTabIcon(self.index, QtGui.QIcon("Images/Log/9+.png"))

    def changed_tab(self):
        current_tab = self._parent.get_current_tab()
        if current_tab == self.index and self.previous_tab != self.index:
            self.new_logs = 0
            self.change_icon()
        self.previous_tab = current_tab

    def add_log(self, log_message: str, log_type: str = None) -> None:
        current_time = datetime.datetime.now()
        formatted_log_message = f"{current_time.strftime('%Y-%m-%d %H:%M')} - {log_message}\n"
        self.new_logs += 1
        if log_type == "HTML":
            self.text.add_html(formatted_log_message)
        if log_type == "Plain":
            self.text.add_text(formatted_log_message)
        if log_type == "MarkDown":
            self.text.add_md(formatted_log_message)
        if log_type == None:
            self.text.add_text(formatted_log_message)

        playsound("discord.mp3")



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