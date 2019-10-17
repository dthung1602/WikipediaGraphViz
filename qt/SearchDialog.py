from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi


class SearchDialog(QWidget):
    def __init__(self, searchMode):
        super().__init__()
        self.searchMode = searchMode

        loadUi('resource/gui/SearchDialog.ui', self)
        self.setWindowIcon(QIcon('resource/gui/image/wiki-logo.png'))
        self.setWindowTitle("WikipediaGraphViz - Search")

        self.searchBtn = self.findChild(QPushButton, 'searchBtn')
        self.searchTerm = self.findChild(QLineEdit, 'searchTerm')

        self.searchBtn.pressed.connect(self.search)
        self.searchTerm.returnPressed.connect(self.search)

    def search(self):
        text = self.searchTerm.text()
        self.searchMode.search(text)
