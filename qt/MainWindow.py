import igraph
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from canvas import *
from .AboutUsDialog import AboutUsDialog

DEFAULT_GRAPH = igraph.Graph()

COLOR_VERTEX_OPTIONS = [
    ['Pagerank', 'pagerank'],
    ['Closeness', 'closeness'],
    ['Betweenness', 'betweenness'],
    ['Eigenvector', 'evcent'],
    ['Out degree', 'outdegree'],
    ['In degree', 'indegree'],
    ['Reference', 'reference'],
    ['Image', 'image'],
]

FILTER_VERTEX_OPTIONS = [
    ['Pagerank', 'pagerank'],
    ['Closeness', 'closeness'],
    ['Betweenness', 'betweenness'],
    ['Eigenvector', 'evcent'],
    ['Out degree', 'outdegree'],
    ['In degree', 'indegree'],
    ['Reference', 'reference'],
    ['Image', 'image'],
]

RELATIVE_FILTERS = [
    'pagerank', 'closeness', 'betweenness'
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('resource/gui/GUI.ui', self)

        self.setWindowIcon(QIcon('resource/gui/icon.ico'))
        self.setWindowTitle("Wikipedia Graph Viz")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.canvas = Canvas(1129, 600)
        # self.findChild(QVBoxLayout, 'canvasBox').addWidget(self.canvas)

        # Modes
        # 0
        self.darkMode = DarkViewMode(self)
        self.grayMode = GrayViewMode(self)
        self.lightMode = LightViewMode(self)
        # 1
        self.editMode = EditMode(self)
        self.shortestPathMode = ShortestPathMode(self)
        # 2
        self.layoutMode = LayoutMode(self)
        # 3
        self.clusterVerticesMode = ClusterVerticesMode(self)
        self.centralityMode = CentralityMode(self)
        self.vertexAttrColorMode = VertexAttrColorMode(self)

        defaultModes = [
            self.darkMode,
            self.editMode,
            self.layoutMode,
            self.clusterVerticesMode,
        ]
        # /for m in defaultModes:
        #     self.canvas.addMode(m)
        # self.canvas.setGraph(DEFAULT_GRAPH)

        self.absoluteRadio = self.relativeRadio = self.colorVertexComboBox = self.filterVertexComboBox = None
        self.labels = [
            'pageTitle', 'pageRank', 'pageID', 'pageInLinkCount', 'pageOutLinkCount',
            'pageRefCount', 'pageImgCount', 'pageWordCount', 'pageCatCount', 'pageSummary',
            'pageCount', 'linkCount', 'catCount', 'diameter', 'radius',
            'density', 'avgOutDeg', 'avgInDeg', 'avgShortestPath'
        ]

        self.bindMenuActions()
        self.bindButtonActions()
        self.initComboBoxes()
        self.findLabels()

    def bindMenuActions(self):
        # ------------- Menu ---------------- #
        # File
        self.findChild(QAction, 'actionNew').triggered.connect(self.handleNew)
        self.findChild(QAction, 'actionOpen').triggered.connect(self.handleOpenFile)
        self.findChild(QAction, 'actionSave').triggered.connect(self.handleSave)
        self.findChild(QAction, 'actionSaveImage').triggered.connect(self.handleSaveImage)
        self.findChild(QAction, 'actionClose').triggered.connect(self.close)
        # View
        self.findChild(QAction, 'actionZoomIn').triggered.connect(self.canvas.zoomInEvent)
        self.findChild(QAction, 'actionZoomOut').triggered.connect(self.canvas.zoomOutEvent)
        self.findChild(QAction, 'actionResetZoom').triggered.connect(self.canvas.zoomResetEvent)
        self.findChild(QAction, 'actionLightMode').triggered.connect(self.changeViewModeTo(LightViewMode))
        self.findChild(QAction, 'actionGrayMode').triggered.connect(self.changeViewModeTo(GrayViewMode))
        self.findChild(QAction, 'actionDarkMode').triggered.connect(self.changeViewModeTo(DarkViewMode))
        # Crawl
        self.findChild(QAction, 'actionCrawlSetting').triggered.connect(self.handleCrawlSetting)
        self.findChild(QAction, 'actionStartCrawling').triggered.connect(self.handleStartCrawling)
        self.findChild(QAction, 'actionPauseCrawling').triggered.connect(self.handlePauseCrawling)
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
        self.findChild(QToolButton, 'startCrawlingBtn').pressed.connect(self.handleStartCrawling)
        self.findChild(QToolButton, 'pauseCrawlingBtn').pressed.connect(self.handlePauseCrawling)
        self.findChild(QToolButton, 'crawlSettingBtn').pressed.connect(self.handleCrawlSetting)
        self.findChild(QToolButton, 'showChartsBtn').pressed.connect(self.handleShowCharts)
        self.findChild(QToolButton, 'findShortestPathBtn').pressed.connect(self.handleFindShortestPath)
        self.findChild(QToolButton, 'searchBtn').pressed.connect(self.handleSearch)

        # ------------ Tabs ------------#
        self.findChild(QPushButton, 'cancelColorBtn').pressed.connect(self.handleCancelColor)
        self.findChild(QPushButton, 'applyColorBtn').pressed.connect(self.handleApplyColor)
        self.findChild(QPushButton, 'cancelFilterBtn').pressed.connect(self.handleCancelFilter)
        self.findChild(QPushButton, 'applyFilterBtn').pressed.connect(self.handleApplyFilter)

        self.absoluteRadio = self.findChild(QRadioButton, 'absoluteRadio')
        self.absoluteRadio.pressed.connect(self.handleAbsoluteRadioChange)
        self.relativeRadio = self.findChild(QRadioButton, 'relativeRadio')
        self.relativeRadio.pressed.connect(self.handleRelativeRadioChange)

    def initComboBoxes(self):
        self.colorVertexComboBox = self.findChild(QComboBox, 'colorVertexComboBox')
        self.colorVertexComboBox.addItems([opt[0] for opt in COLOR_VERTEX_OPTIONS])

        self.filterVertexComboBox = self.findChild(QComboBox, 'filterVertexComboBox')
        self.filterVertexComboBox.addItems([opt[0] for opt in FILTER_VERTEX_OPTIONS])

    def findLabels(self):
        for label in self.labels:
            setattr(self, label, self.findChild(QLabel, label))

    def handleNew(self):
        g = igraph.read('resource/graph/__empty__.graphml')
        self.canvas.setGraph(g)
        self.canvas.center = QPointF(530, 1130)
        self.canvas.zoom = 0.25
        self.canvas.update()

    def handleOpenFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open", "./resource/graph",
            "All Files (*);;Python Files (*.py)", options=options
        )
        if fileName:
            self.canvas.setGraph(fileName)

    def handleSave(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save As", "",
            "All Files (*);;GraphML Files (*.graphml);;GML Files (*.gml)", options=options
        )

        # process graph before saving
        g = self.canvas.g.copy()
        g.vs['color'] = [c.name() if isinstance(c, QColor) else c.color().name() for c in g.vs['color']]
        g.es['color'] = [c.name() if isinstance(c, QColor) else c.color().name() for c in g.es['color']]
        del g.es['line']
        del g.vs['pos']

        if fileName:
            if ".graphml" in fileName:
                g.write_graphml(fileName)
            elif ".gml" in fileName:
                g.write_gml(fileName)

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
        pass

    def handleZoomOut(self):
        pass

    def handleResetZoom(self):
        pass

    def handleCrawlSetting(self):
        pass

    def handleStartCrawling(self):
        pass

    def handlePauseCrawling(self):
        pass

    def handleFindShortestPath(self):
        pass

    def handleSearch(self):
        pass

    def handleShowCharts(self):
        pass

    def handleCancelColor(self):
        pass

    def handleApplyColor(self):
        pass

    def handleCancelFilter(self):
        pass

    def handleApplyFilter(self):
        pass

    def handleAbsoluteRadioChange(self):
        pass

    def handleRelativeRadioChange(self):
        pass

    @staticmethod
    def handleAboutUs():
        aboutUsWindow = AboutUsDialog()
        aboutUsWindow.exec()

    def displayPage(self, page):
        pass
