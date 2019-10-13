from abc import ABC

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor

from .Mode import Mode


class ViewMode(Mode, ABC):
    priority = 0

    backgroundBrush = None
    backgroundPen = None
    foregroundBrush = None
    foregroundPen = None
    selectedPen = QPen(QColor(255, 0, 0), 4)

    def onSet(self):
        g = self.canvas.g
        if g:
            g.es['color'] = [self.foregroundPen] * g.ecount()
            g.vs['color'] = [self.foregroundBrush] * g.vcount()

    def onSetGraph(self):
        g = self.canvas.g
        if 'color' not in g.es.attributes():
            g.es['color'] = [self.foregroundPen] * g.ecount()
        override = False
        if 'color' in g.vs.attributes() and g.vcount() > 0 and isinstance(g.vs[0]['color'], str):
            g.vs['cluster'] = g.vs['color']
            g.vs['color'] = [QBrush(QColor(c)) for c in g.vs['color']]
            override = True
        if 'color' in g.es.attributes() and g.ecount() > 0 and isinstance(g.es[0]['color'], str):
            g.es['cluster'] = g.es['color']
            g.es['color'] = [QPen(QColor(c)) for c in g.es['color']]
            override = True
        if override:
            return True
        if 'cluster' not in g.vs.attributes():
            g.vs['color'] = [self.foregroundBrush] * g.vcount()

    def onUpdateGraph(self):
        for e in self.canvas.g.es:
            if not e['color']:
                e['color'] = self.foregroundPen
        for v in self.canvas.g.vs:
            if not v['color']:
                v['color'] = self.foregroundBrush

    def onPaintBegin(self, painter: QPainter):
        painter.fillRect(self.canvas.SCREEN_RECT, self.backgroundBrush)

    def beforePaintEdges(self, painter):
        painter.setPen(self.foregroundPen)

    def beforePaintVertices(self, painter):
        painter.setPen(self.backgroundPen)

    def beforePaintSelectedEdges(self, painter):
        painter.setPen(self.selectedPen)

    def onSelectEdge(self, edge):
        return

    def onSelectVertex(self, vertex):
        return


class DarkViewMode(ViewMode):
    conflict_modes = ['LightViewMode', 'GrayViewMode']
    backgroundBrush = QBrush(Qt.black)
    backgroundPen = QPen(Qt.black)
    foregroundBrush = QBrush(Qt.white)
    foregroundPen = QPen(Qt.white)


class GrayViewMode(ViewMode):
    conflict_modes = ['LightViewMode', 'DarkViewMode']
    backgroundBrush = QBrush(Qt.gray)
    backgroundPen = QPen(Qt.gray)
    foregroundBrush = QBrush(Qt.white)
    foregroundPen = QPen(Qt.white)


class LightViewMode(ViewMode):
    conflict_modes = ['DarkViewMode', 'GrayViewMode']
    backgroundBrush = QBrush(Qt.white)
    backgroundPen = QPen(Qt.white)
    foregroundBrush = QBrush(Qt.darkBlue)
    foregroundPen = QPen(Qt.black)
