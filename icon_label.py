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