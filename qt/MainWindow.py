from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from canvas import *
from .AboutUsDialog import AboutUsDialog
from .CrawlDialog import CrawlDialog
from .StatDialog import StatDialog

DEFAULT_GRAPH = 'resource/graph/UsCarrier.graphml'


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('resource/gui/GUI.ui', self)

        self.setWindowIcon(QIcon('resource/gui/icon.ico'))
        self.setWindowTitle("Wikipedia Graph Viz")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.canvas = Canvas(1080, 650)
        self.findChild(QVBoxLayout, 'canvasBox').addWidget(self.canvas)

        # Modes
        # 0
        self.darkMode = DarkViewMode(self)
        self.grayMode = GrayViewMode(self)
        self.lightMode = LightViewMode(self)
        self.updateInfoMode = UpdateInfoMode(self)
        # 1
        self.shortestPathMode = ShortestPathMode(self)
        self.dragAndDropMode = DragAndDropMode(self)
        # 2
        self.layoutMode = LayoutMode(self)
        # 3
        self.vertexAttrColorMode = VertexColorMode(self)
        self.filterMode = FilterMode(self)
        # 99
        self.crawlMode = CrawlMode(self)

        defaultModes = [
            self.darkMode,
            self.updateInfoMode,
            self.dragAndDropMode,
            self.layoutMode,
            self.crawlMode
        ]
        for m in defaultModes:
            self.canvas.addMode(m)
        self.canvas.setGraph(DEFAULT_GRAPH)

        self.statDialog = self.crawlSettingDialog = None
        self.startBtn = self.stopBtn = self.pauseBtn = self.resumeBtn = None
        self.fromLineEdit = self.toLineEdit = None
        self.absoluteRadio = self.relativeRadio = self.clusterLabel = self.pageInfo = self.pageSummary = None
        self.clusterComboBox = self.colorVertexComboBox = self.filterVertexComboBox = self.layoutComboBox = None

        self.labels = [
            'clusterLabel', 'timeElapsed'
                            'pageTitle', 'pageRank', 'pageID', 'pageInLinkCount', 'pageOutLinkCount',
            'pageRefCount', 'pageImgCount', 'pageWordCount', 'pageCatCount',
            'pageCount', 'linkCount', 'catCount', 'diameter', 'radius',
            'density', 'avgOutDeg', 'avgInDeg', 'avgShortestPath'
        ]

        self.bindMenuActions()
        self.bindButtonActions()
        self.initComboBoxes()
        self.findLabels()
        self.stuff()

    def bindMenuActions(self):
        # ------------- Menu ---------------- #
        # File
        self.findChild(QAction, 'actionNew').triggered.connect(self.handleNew)
        self.findChild(QAction, 'actionOpen').triggered.connect(self.handleOpenFile)
        self.findChild(QAction, 'actionSave').triggered.connect(self.handleSave)
        self.findChild(QAction, 'actionSaveImage').triggered.connect(self.handleSaveImage)
        self.findChild(QAction, 'actionClose').triggered.connect(self.close)
        # View
        self.findChild(QAction, 'actionZoomIn').triggered.connect(self.handleZoomIn)
        self.findChild(QAction, 'actionZoomOut').triggered.connect(self.handleZoomOut)
        self.findChild(QAction, 'actionResetZoom').triggered.connect(self.handleResetZoom)
        self.findChild(QAction, 'actionLightMode').triggered.connect(self.changeViewModeTo(LightViewMode))
        self.findChild(QAction, 'actionGrayMode').triggered.connect(self.changeViewModeTo(GrayViewMode))
        self.findChild(QAction, 'actionDarkMode').triggered.connect(self.changeViewModeTo(DarkViewMode))
        # Crawl
        # self.findChild(QAction, 'actionStartCrawling').triggered.connect(self.handleStartCrawling)
        # self.findChild(QAction, 'actionStopCrawling').triggered.connect(self.handleStartStop)
        # self.findChild(QAction, 'actionPauseCrawling').triggered.connect(self.handlePauseResume)
        # self.findChild(QAction, 'actionResumeCrawling').triggered.connect(self.handleResumeCrawling)
        # self.findChild(QAction, 'actionCrawlSetting').triggered.connect(self.handleCrawlSetting)
        # Tools
        self.findChild(QAction, 'actionFindShortestPath').triggered.connect(self.handleFindShortestPath)
        self.findChild(QAction, 'actionSearch').triggered.connect(self.handleSearch)
        self.findChild(QAction, 'actionShowCharts').triggered.connect(self.handleShowCharts)
        # About Us
        self.findChild(QAction, 'actionAboutUs').triggered.connect(self.handleAboutUs)

    def bindButtonActions(self):
        # -------------Toolbar---------------- #
        self.findChild(QToolButton, 'zoomInBtn').pressed.connect(self.handleZoomIn)
        self.findChild(QToolButton, 'zoomOutBtn').pressed.connect(self.handleZoomOut)
        self.findChild(QToolButton, 'zoomResetBtn').pressed.connect(self.handleResetZoom)

        self.pauseBtn = self.findChild(QToolButton, 'pauseBtn')
        self.pauseBtn.pressed.connect(self.handlePause)
        self.resumeBtn = self.findChild(QToolButton, 'resumeBtn')
        self.resumeBtn.pressed.connect(self.handleResume)
        self.startBtn = self.findChild(QToolButton, 'startBtn')
        self.startBtn.pressed.connect(self.handleStart)
        self.stopBtn = self.findChild(QToolButton, 'stopBtn')
        self.stopBtn.pressed.connect(self.handleStop)
        self.findChild(QToolButton, 'crawlSettingBtn').pressed.connect(self.handleCrawlSetting)

        self.findChild(QToolButton, 'showChartsBtn').pressed.connect(self.handleShowCharts)
        self.findChild(QToolButton, 'findShortestPathBtn').pressed.connect(self.handleFindShortestPath)
        self.findChild(QToolButton, 'searchBtn').pressed.connect(self.handleSearch)

        # ------------ Tabs ------------#
        self.findChild(QPushButton, 'cancelColorBtn').pressed.connect(self.handleCancelColor)
        self.findChild(QPushButton, 'applyColorBtn').pressed.connect(self.handleApplyColor)
        self.findChild(QPushButton, 'cancelFilterBtn').pressed.connect(self.handleCancelFilter)
        self.findChild(QPushButton, 'applyFilterBtn').pressed.connect(self.handleApplyFilter)
        self.findChild(QPushButton, 'applyLayoutBtn').pressed.connect(self.handleApplyLayout)

        self.absoluteRadio = self.findChild(QRadioButton, 'absoluteRadio')
        self.absoluteRadio.clicked.connect(self.handleAbsoluteRadioChange)
        self.relativeRadio = self.findChild(QRadioButton, 'relativeRadio')
        self.relativeRadio.clicked.connect(self.handleRelativeRadioChange)

    def initComboBoxes(self):
        self.colorVertexComboBox = self.findChild(QComboBox, 'colorVertexComboBox')
        self.colorVertexComboBox.addItems([opt[0] for opt in COLOR_VERTEX_OPTIONS])
        self.colorVertexComboBox.currentIndexChanged.connect(self.handleColorVertexOptionChange)

        self.filterVertexComboBox = self.findChild(QComboBox, 'filterVertexComboBox')
        self.filterVertexComboBox.addItems([opt[0] for opt in FILTER_VERTEX_OPTIONS])

        self.clusterComboBox = self.findChild(QComboBox, 'clusterComboBox')
        self.clusterComboBox.addItems([opt[0] for opt in CLUSTERING_ALGO_OPTIONS])

        self.layoutComboBox = self.findChild(QComboBox, 'layoutComboBox')
        self.layoutComboBox.addItems([opt[0] for opt in LAYOUT_OPTIONS])

    def findLabels(self):
        for label in self.labels:
            setattr(self, label, self.findChild(QLabel, label))

    def stuff(self):
        self.clusterLabel.setVisible(False)
        self.clusterComboBox.setVisible(False)
        self.pageInfo = self.findChild(QWidget, 'pageInfo')
        self.pageSummary = self.findChild(QPlainTextEdit)
        self.fromLineEdit = self.findChild(QLineEdit, 'fromLineEdit')
        self.toLineEdit = self.findChild(QLineEdit, 'toLineEdit')
        self.pauseBtn.setVisible(False)
        self.resumeBtn.setVisible(False)
        self.stopBtn.setVisible(False)
        self.pageInfo.setVisible(False)

    def handleNew(self):
        pass

    def handleOpenFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open", "./resource/graph",
            "GraphML Files (*.graphml)", options=options
        )
        if fileName:
            self.canvas.setGraph(fileName)

    def handleSave(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save As", "",
            "GraphML Files (*.graphml)", options=options
        )

        if fileName:
            self.canvas.saveGraph(fileName)

    def handleSaveImage(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save As Image", "",
            "All Files (*);;JPG Files (*.jpg)"
        )
        if fileName != '':
            img = QPixmap(self.canvas.size())
            painter = QPainter(img)
            self.canvas.paint(painter)
            painter.end()
            img.save(fileName)

    def changeViewModeTo(self, viewModeClass):
        def func():
            self.canvas.addMode(viewModeClass(self))
            self.canvas.resetViewRect()
            self.canvas.update()

        return func

    def handleZoomIn(self):
        self.canvas.zoomIn()

    def handleZoomOut(self):
        self.canvas.zoomOut()

    def handleResetZoom(self):
        self.canvas.zoomReset()

    def handlePause(self):
        self.pauseBtn.setVisible(False)
        self.resumeBtn.setVisible(True)
        self.crawlMode.pause()

    def handleResume(self):
        self.pauseBtn.setVisible(True)
        self.resumeBtn.setVisible(False)
        self.crawlMode.resume()

    def handleStart(self):
        self.pauseBtn.setVisible(True)
        self.resumeBtn.setVisible(False)
        self.startBtn.setVisible(False)
        self.stopBtn.setVisible(True)
        self.crawlMode.start()

    def handleStop(self):
        self.pauseBtn.setVisible(False)
        self.resumeBtn.setVisible(False)
        self.startBtn.setVisible(True)
        self.stopBtn.setVisible(False)
        self.crawlMode.stop()

    def handleCrawlSetting(self):
        self.crawlSettingDialog = CrawlDialog(self.canvas, self.crawlMode)
        self.crawlSettingDialog.show()

    def handleFindShortestPath(self):
        self.canvas.toggleMode(self.shortestPathMode)

    def handleSearch(self):
        pass

    def handleShowCharts(self):
        self.statDialog = StatDialog(self.canvas)
        self.statDialog.show()

    def handleColorVertexOptionChange(self, opt):
        opt = COLOR_VERTEX_OPTIONS[opt][1]
        visible = opt == 'cluster'
        self.clusterLabel.setVisible(visible)
        self.clusterComboBox.setVisible(visible)
        self.absoluteRadio.setVisible(not visible)
        self.relativeRadio.setVisible(not visible)

    def handleCancelColor(self):
        self.canvas.removeMode(self.vertexAttrColorMode)

    def handleApplyColor(self):
        method = COLOR_VERTEX_OPTIONS[self.colorVertexComboBox.currentIndex()][1]
        relative = self.relativeRadio.isChecked()
        clusterAlgo = CLUSTERING_ALGO_OPTIONS[self.clusterComboBox.currentIndex()][1]
        self.vertexAttrColorMode.setColorMethod(method, clusterAlgo, relative)
        self.canvas.addMode(self.vertexAttrColorMode)

    def handleCancelFilter(self):
        self.canvas.removeMode(self.filterMode)

    def handleApplyFilter(self):
        attr = FILTER_VERTEX_OPTIONS[self.filterVertexComboBox.currentIndex()][1]
        try:
            minValue = float(self.fromLineEdit.text())
        except ValueError:
            minValue = float('-inf')
        try:
            maxValue = float(self.toLineEdit.text())
        except ValueError:
            maxValue = float('inf')
        self.filterMode.setFilter(attr, minValue, maxValue)
        self.canvas.addMode(self.filterMode)

    def handleApplyLayout(self):
        layout = LAYOUT_OPTIONS[self.layoutComboBox.currentIndex()][1]
        self.layoutMode.setLayout(layout)
        self.canvas.update()

    def handleAbsoluteRadioChange(self, selected):
        self.absoluteRadio.setChecked(selected)
        self.relativeRadio.setChecked(not selected)

    def handleRelativeRadioChange(self, selected):
        self.absoluteRadio.setChecked(not selected)
        self.relativeRadio.setChecked(selected)

    @staticmethod
    def handleAboutUs():
        aboutUsWindow = AboutUsDialog()
        aboutUsWindow.exec()

    def displayInfo(self, info: dict):
        for key, value in info.items():
            if key == 'pageSummary':
                self.pageSummary.clear()
                self.pageSummary.insertPlainText(value)
            else:
                getattr(self, key).setText(value)

    def setPageInfoVisible(self, vis):
        self.pageInfo.setVisible(vis)

    def closeEvent(self, event):
        self.crawlSettingDialog.close()
        self.statDialog.close()
        super().closeEvent(event)

    def notifyCrawlDone(self):
        # TODO something
        if self.crawlSettingDialog:
            self.crawlSettingDialog.notifyCrawlDone()
