from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class AboutUsDialog(QDialog):
    def __init__(self):
        super().__init__()

        loadUi('resource/gui/AboutUsDialog.ui', self)
        self.setWindowIcon(QIcon('resource/gui/image/wiki-logo.png'))
        self.setWindowTitle("About Us")
