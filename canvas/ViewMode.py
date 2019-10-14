from abc import ABC
from itertools import chain

from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

from .Mode import Mode

BLACK = QColor(0, 0, 0)
WHITE = QColor(255, 255, 255)
GRAY = QColor(128, 128, 128)
DARK_BLUE = QColor(0, 0, 102)


class ViewMode(Mode, ABC):
    priority = 0

    backgroundColor = None
    foregroundColor = None
    selectedPen = QPen(QColor(255, 0, 0), 2)
    selectedBrush = QBrush(QColor(255, 0, 0))

    def onSet(self):
        g = self.canvas.g
        if g:
            g.es['color'] = [self.foregroundColor] * g.ecount()
            if len(set([c.name() for c in g.vs['color']])) == 1:
                g.vs['color'] = [self.foregroundColor] * g.vcount()

    def onSetGraph(self):
        g = self.canvas.g
        vsAttributes = g.vs.attributes()
        g.es['color'] = [self.foregroundColor] * g.ecount()

        if 'color' in vsAttributes:
            if g.vcount() > 0:
                if all([isinstance(v['color'], str) for v in g.vs]):
                    g.vs['cluster'] = g.vs['color']
                    g.vs['color'] = [(QColor(c)) for c in g.vs['color']]
                else:
                    g.vs['cluster'] = '0'
                    g.vs['color'] = [self.canvas.defaultForegroundColor] * g.vcount()
        else:
            g.vs['color'] = [self.foregroundColor] * g.vcount()

    def onNewVertexAdded(self, vertex):
        es = self.canvas.g.es
        for e in chain(es.select(_source=vertex.index), es.select(_target=vertex.index)):
            e['color'] = self.foregroundColor
        vertex['color'] = self.foregroundColor

    def onPaintBegin(self, painter: QPainter):
        painter.fillRect(self.canvas.SCREEN_RECT, self.backgroundColor)

    def beforePaintEdges(self, painter):
        painter.setPen(self.foregroundColor)
        painter.setBrush(self.foregroundColor)

    def beforePaintVertices(self, painter):
        painter.setPen(self.backgroundColor)

    def beforePaintSelectedEdges(self, painter):
        painter.setPen(self.selectedPen)
        painter.setBrush(self.selectedBrush)


class DarkViewMode(ViewMode):
    conflict_modes = ['LightViewMode', 'GrayViewMode']
    backgroundColor = BLACK
    foregroundColor = WHITE


class GrayViewMode(ViewMode):
    conflict_modes = ['LightViewMode', 'DarkViewMode']
    backgroundColor = GRAY
    foregroundColor = WHITE


class LightViewMode(ViewMode):
    conflict_modes = ['DarkViewMode', 'GrayViewMode']
    backgroundColor = WHITE
    foregroundColor = DARK_BLUE
