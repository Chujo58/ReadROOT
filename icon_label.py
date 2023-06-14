from PyQt5 import QtCore, QtWidgets, QtGui

class IconLabel(QtWidgets.QWidget):
    IconSize = QtCore.QSize(16,16)
    HorizontalSpacing = 2

    def __init__(self, icon_url: str, text: str, final_stretch=True):
        super(QtWidgets.QWidget, self).__init__()

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        icon = QtWidgets.QLabel()
        icon.setPixmap(QtGui.QIcon(icon_url).pixmap(self.IconSize))

        layout.addWidget(icon)
        layout.addSpacing(self.HorizontalSpacing)
        layout.addWidget(QtWidgets.QLabel(text))

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