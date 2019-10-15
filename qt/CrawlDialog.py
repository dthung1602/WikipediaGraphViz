import wikipedia
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from .Switch import Switch

AVAILABLE_WIKI_LANG = [  # 15 wiki with > 1000000 pages
    ['English', 'en'],
    ['Cebuano', 'ceb'],
    ['Swedish - Svenska', 'sv'],
    ['German - Deutsch', 'de'],
    ['French - Français', 'fr'],
    ['Dutch - Nederlands', 'nl'],
    ['Russian - Pусский', 'ru'],
    ['Italian - Italiano', 'it'],
    ['Spanish - Español', 'es'],
    ['Polish - Polski', 'pl'],
    ['Waray - Winaray', 'war'],
    ['Vietnamese - Tiếng Việt', 'vi'],
    ['Japanese - 日本語', 'ja'],
    ['Chinese - 中文', 'zh'],
    ['Portuguese - Português', 'pt']
]


class CrawlDialog(QMainWindow):
    def __init__(self, canvas, crawlMode):
        super().__init__()
        self.canvas = canvas
        self.crawlMode = crawlMode

        loadUi('resource/gui/CrawlDialog.ui', self)
        self.setWindowIcon(QIcon('resource/gui/image/wiki-logo.png'))
        self.setWindowTitle("WikipediaGraphViz - Crawl")

        self.languageComboBox = self.findChild(QComboBox, 'languageComboBox')
        self.languageComboBox.addItems([lang[0] for lang in AVAILABLE_WIKI_LANG])

        self.delay = self.findChild(QLineEdit, 'delay')
        self.startPage = self.findChild(QLineEdit, 'startPage')
        self.loadDetails = Switch(parent=self.findChild(QLabel, 'switchContainer'))
        self.loadDetails.setChecked(True)

        for lineEditName in ['reachPage', 'maxPage', 'maxDepth', 'timeLimit']:
            setattr(self, lineEditName, self.findChild(QLineEdit, lineEditName))
            getattr(self, lineEditName).setDisabled(True)
            checkBoxName = lineEditName + 'CheckBox'
            setattr(self, checkBoxName, self.findChild(QCheckBox, checkBoxName))
            getattr(self, checkBoxName).stateChanged.connect(self.handleStopConditionCheckBox(lineEditName))

        self.dfsRadio = self.findChild(QRadioButton, 'dfsRadio')
        self.dfsRadio.clicked.connect(self.handleRadioChange('dfsRadio'))
        self.bfsRadio = self.findChild(QRadioButton, 'bfsRadio')
        self.bfsRadio.clicked.connect(self.handleRadioChange('bfsRadio'))
        self.randomRadio = self.findChild(QRadioButton, 'randomRadio')
        self.randomRadio.clicked.connect(self.handleRadioChange('randomRadio'))

        self.findChild(QPushButton, 'randomBtn').pressed.connect(self.handleRandomStartPage)

        self.pauseResumeBtn = self.findChild(QPushButton, 'pauseResumeBtn')
        self.pauseResumeBtn.pressed.connect(self.handlePauseResume)
        self.startStopBtn = self.findChild(QPushButton, 'startStopBtn')
        self.startStopBtn.pressed.connect(self.handleStartStop)

        if crawlMode.status == 'running':
            self.pauseResumeBtn.setDisabled(False)
            self.startStopBtn.setText('Stop')
            self.pauseResumeBtn.setText('Pause')
            self.enableEdit(False)
        elif crawlMode.status in ['stopped', 'done']:
            self.startStopBtn.setText('Start')
            self.pauseResumeBtn.setText('Pause')
            self.pauseResumeBtn.setDisabled(True)
            self.enableEdit(True)
        else:  # paused
            self.startStopBtn.setText('Stop')
            self.pauseResumeBtn.setText('Resume')
            self.pauseResumeBtn.setDisabled(False)
            self.enableEdit(False)

    def handleRadioChange(self, radioName):
        def func(value):
            self.dfsRadio.setChecked(False)
            self.bfsRadio.setChecked(False)
            self.randomRadio.setChecked(False)
            getattr(self, radioName).setChecked(True)

        return func

    def bfsChecked(self, value):
        self.dfsRadio.setChecked(not value)
        self.bfsRadio.setChecked(value)

    def handleStopConditionCheckBox(self, lineEditName):
        def func(value):
            getattr(self, lineEditName).setDisabled(not value)

        return func

    def handleRandomStartPage(self):
        self.startPage.setText(wikipedia.random())

    def handlePauseResume(self):
        if self.crawlMode.status == 'running':
            self.pauseResumeBtn.setText('Resume')
            self.crawlMode.pause()
        else:
            self.pauseResumeBtn.setText('Pause')
            self.crawlMode.resume()

    def floatOrDefault(self, attrName, defaultValue=None):
        value = getattr(self, attrName).text()
        try:
            return float(value)
        except ValueError:
            getattr(self, attrName).setText(str(defaultValue))
            return defaultValue

    def strOrDefault(self, attrName, defaultValue=None):
        value = getattr(self, attrName).text().strip()
        if value == '':
            getattr(self, attrName).setText(str(defaultValue))
            return defaultValue
        return value

    def enableEdit(self, value):
        for attr in []:
            getattr(self, attr).setDisabled(value)

    def handleStartStop(self):
        if self.crawlMode.status in ['stopped', 'done']:
            settings = {
                'language': AVAILABLE_WIKI_LANG[self.languageComboBox.currentIndex()][1],
                'searchAlgo': 'DFS' if self.dfsRadio.isChecked() else 'BFS' if self.bfsRadio.isChecked() else 'RAND',
                'delay': self.floatOrDefault('delay', 1),
                'startPage': self.strOrDefault('startPage', 'Graph theory'),
                'loadDetails': self.loadDetails.isChecked()
            }

            if self.reachPageCheckBox.isChecked():
                settings['reachPage'] = self.strOrDefault('reachPage', 'Network science')
            if self.maxPageCheckBox.isChecked():
                settings['maxPage'] = self.floatOrDefault('maxPage', 10)
            if self.maxDepthCheckBox.isChecked():
                settings['maxDepth'] = self.floatOrDefault('maxDepth', 5)
            if self.timeLimitCheckBox.isChecked():
                settings['timeLimit'] = self.floatOrDefault('timeLimit', 60 * 5)

            self.crawlMode.setCrawlSetting(**settings)
            self.crawlMode.start()
            self.pauseResumeBtn.setDisabled(False)
            self.startStopBtn.setText('Stop')
            self.pauseResumeBtn.setText('Pause')
            self.enableEdit(False)
        else:
            self.startStopBtn.setText('Start')
            self.crawlMode.stop()
            self.pauseResumeBtn.setDisabled(True)
            self.enableEdit(True)

    def notifyCrawlDone(self):
        self.startStopBtn.setText('Start')
        self.pauseResumeBtn.setDisabled(True)
        self.enableEdit(True)
