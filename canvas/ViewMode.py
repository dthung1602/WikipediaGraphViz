from abc import ABC

from PyQt5.QtGui import QPainter, QPen, QColor

from .Mode import Mode

BLACK = QColor(0, 0, 0)
WHITE = QColor(255, 255, 255)
GRAY = QColor(128, 128, 128)
DARK_GRAY = QColor(80, 80, 80)
LIGHTER_GRAY = QColor(180, 180, 180)
DARKER_GRAY = QColor(50, 50, 50)
BLUE = QColor(0, 191, 255)
LIGHT_BLUE = QColor(168, 238, 255)
DARK_BLUE = QColor(0, 0, 102)
YELLOW = QColor(255, 255, 66)


class ViewMode(Mode, ABC):
    priority = 0

    backgroundColor = None
    lineColor = None
    visitedPageColor = None
    unvisitedPageColor = None
    selectedPen = QPen(QColor(255, 0, 0), 2)

    def setVerticesColor(self):
        vs = self.canvas.g.vs
        print(len(vs.select(visited=True)))
        vs['color'] = [self.visitedPageColor if v['visited'] else self.unvisitedPageColor for v in vs]

    def onSet(self):
        g = self.canvas.g
        if g:
            g.es['color'] = [self.lineColor] * g.ecount()
            if len(set([c.name() for c in g.vs['color']])) <= 2:
                self.setVerticesColor()

    def onSetGraph(self):
        g = self.canvas.g
        vsAttributes = g.vs.attributes()
        g.es['color'] = self.lineColor

        if 'color' in vsAttributes:
            if g.vcount() > 0:
                if all([isinstance(v['color'], str) for v in g.vs]):
                    g.vs['cluster'] = g.vs['color']
                    g.vs['color'] = [(QColor(c)) for c in g.vs['color']]
                else:
                    g.vs['cluster'] = '0'
                    self.setVerticesColor()
        else:
            g.vs['color'] = self.visitedPageColor

    def onNewVerticesAdded(self):
        self.canvas.g.es['color'] = self.lineColor
        self.setVerticesColor()

    def onPaintBegin(self, painter: QPainter):
        painter.fillRect(self.canvas.SCREEN_RECT, self.backgroundColor)

    def beforePaintEdges(self, painter):
        painter.setPen(self.lineColor)
        painter.setBrush(self.lineColor)

    def beforePaintVertices(self, painter):
        painter.setPen(self.backgroundColor)

    def beforePaintSelectedEdges(self, painter):
        painter.setPen(self.selectedPen)


class DarkViewMode(ViewMode):
    conflict_modes = ['LightViewMode', 'GrayViewMode']
    backgroundColor = BLACK
    lineColor = DARK_GRAY
    visitedPageColor = YELLOW
    unvisitedPageColor = WHITE


class GrayViewMode(ViewMode):
    conflict_modes = ['LightViewMode', 'DarkViewMode']
    backgroundColor = GRAY
    lineColor = LIGHTER_GRAY
    visitedPageColor = DARKER_GRAY
    unvisitedPageColor = WHITE


class LightViewMode(ViewMode):
    conflict_modes = ['DarkViewMode', 'GrayViewMode']
    backgroundColor = WHITE
    lineColor = LIGHT_BLUE
    visitedPageColor = DARK_BLUE
    unvisitedPageColor = BLUE
