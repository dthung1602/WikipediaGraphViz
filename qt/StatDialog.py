from math import isnan, isinf

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QComboBox, QSizePolicy
from PyQt5.uic import loadUi
from igraph import VertexSeq
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from canvas import Canvas
from .utils import clearLayout


class StatDialog(QWidget):
    def __init__(self, canvas: Canvas):
        super().__init__()
        self.canvas = canvas
        loadUi('resource/gui/StatDialog.ui', self)
        self.setWindowIcon(QIcon('resource/gui/icon.ico'))
        self.setWindowTitle("WikipediaGraphViz - Statistics")

        self.availableAttributes = self.getAvailableAttributes()

        self.simpleAttrGraph = self.findChild(QVBoxLayout, 'simpleAttrGraph')

        self.selectAttr = self.findChild(QComboBox, 'selectAttr')
        self.selectAttr.addItems(self.availableAttributes)
        self.selectAttr.currentIndexChanged.connect(self.changeAttr)

        self.plotStyle = 'bmh'
        self.selectStyle = self.findChild(QComboBox, 'selectStyle')
        self.selectStyle.addItems(plt.style.available)
        self.selectStyle.currentIndexChanged.connect(self.changeStyle)

        self.changeAttr(0)

    def getAvailableAttributes(self):
        vs = self.canvas.g.vs

        def isStrOrFloat(attr):
            return all(isinstance(v[attr], str) for v in vs) or all(isinstance(v[attr], float) for v in vs)

        return list(filter(isStrOrFloat, vs.attributes()))

    def changeAttr(self, opt):
        vs = self.canvas.g.vs
        attr = self.availableAttributes[opt]
        clearLayout(self.simpleAttrGraph)
        w = WidgetPlot(attr, vs[attr], self.plotStyle)
        self.simpleAttrGraph.addWidget(w)

    def changeStyle(self, opt):
        self.plotStyle = plt.style.available[opt]
        i = int(self.selectAttr.currentIndex())
        self.changeAttr(i)


class WidgetPlot(QWidget):
    def __init__(self, attr, values, style):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.plot = Plot(attr, values, style)
        self.toolbar = NavigationToolbar(self.plot, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.plot)


class Plot(FigureCanvas):
    def __init__(self, attrName, values, style):
        with plt.style.context(style):
            # values = list(filter(lambda x: isinstance(x, str) or not (isnan(x) or isinf(x)), values))
            fig, ax = plt.subplots()
            num_bins = 30
            ax.set_title(attrName + ' distribution')
            ax.set_ylabel('Number of wiki page')
            if values and isinstance(values[0], str):
                labels = sorted(list(set(values)))
                ax.set_xticklabels(labels, rotation=90)
                num_bins = len(labels)
            if values and isinstance(values[0], float):
                meanLine = ax.axvline(np.mean(values), color='r', linestyle='--')
                medianLine = ax.axvline(np.median(values), color='b', linestyle='-')
                plt.legend([meanLine, medianLine], ['Mean', 'Median'])
            ax.hist(values, num_bins)

        FigureCanvas.__init__(self, fig)
        self.setParent(None)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
