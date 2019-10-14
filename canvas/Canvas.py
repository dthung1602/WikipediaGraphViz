from math import sqrt
from typing import Union
import igraph
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from igraph import Graph

from .Mode import Mode
from .utils import *


def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the
    instance as the first argument, i.e. "self".
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method


def wrapGraph(graph):
    def reference(self):
        return self.vs['ref']

    def image(self):
        return self.vs['image']

    for func in [reference, image]:
        bind(graph, func)

    graph['category'] = set()
    graph['title'] = set()
    graph['pageid'] = set()
    return graph


class Canvas(QWidget):
    POINT_RADIUS = 8
    SELECTED_POINT_RADIUS = 12
    LINE_DISTANCE = 2
    CURVE_SELECT_SQUARE_SIZE = 10

    def __init__(self, width: int, height: int):
        super().__init__(None)

        self.WIDTH = width
        self.HEIGHT = height
        self.SCREEN_RECT = QRectF(0, 0, width, height)
        self.SCREEN_RECT_LINE = [
            QLineF(0, 0, width, 0),
            QLineF(width, 0, width, height),
            QLineF(width, height, 0, height),
            QLineF(0, height, 0, 0)
        ]

        self.center = self.zoom = None
        self.selectedEdges = self.selectedVertices = []
        self.viewRect = self.verticesToDraw = self.edgesToDraw = None

        self.g = None
        self.modes = []

    def toScaledXY(self, x, y):
        return self.toScaledX(x), self.toScaledY(y)

    def toScaledX(self, x):
        return float((x - self.viewRect.x()) * self.zoom)

    def toScaledY(self, y):
        return float((y - self.viewRect.y()) * self.zoom)

    def toAbsoluteXY(self, x, y):
        return self.toAbsoluteX(x), self.toAbsoluteY(y)

    def toAbsoluteX(self, x):
        return float(x / self.zoom + self.viewRect.x())

    def toAbsoluteY(self, y):
        return float(y / self.zoom + self.viewRect.y())

    def setGraph(self, g: Union[str, Graph]):
        if isinstance(g, str):
            g = igraph.read(g)
        self.g = wrapGraph(g)

        for mode in self.modes:
            if mode.onSetGraph():
                break
        self.resetViewRect()
        self.update()

    def notifyNewVertex(self, ):
        vertex = self.g.vs[self.g.vcount() - 1]
        for mode in self.modes:
            if mode.onNewVertexAdded(vertex):
                break
        self.update()

    def saveGraph(self, fileName):
        g = self.g.copy()
        # TODO preprocess
        g.write_graphml(fileName)

    def addMode(self, mode: Mode):
        if mode in self.modes:
            mode.onUnset()
            mode.onSet()
            self.update()
            return

        def isConflict(m: Mode):
            if m.__class__.__name__ in mode.conflict_modes:
                return True
            return False

        mode.canvas = self
        mode.onSet()
        modes = []
        for m in self.modes:
            if isConflict(m):
                m.onUnset()
            else:
                modes.append(m)
        self.modes = sorted(modes + [mode], key=lambda m: m.priority)
        self.update()

    def removeMode(self, mode: Mode):
        if mode in self.modes:
            self.modes.remove(mode)
            mode.onUnset()
            self.update()
            return True
        self.update()
        return False

    def toggleMode(self, mode: Mode):
        if mode in self.modes:
            self.removeMode(mode)
        else:
            self.addMode(mode)

    def resetViewRect(self):
        for mode in self.modes:
            if mode.onResetViewRect():
                break

        self.center = QPointF(self.WIDTH / 2, self.HEIGHT / 2)
        self.zoom = 1
        self.selectedEdges = self.selectedVertices = []

        self.updateViewRect()

    def updateViewRect(self):
        viewRectWidth = self.WIDTH / self.zoom
        viewRectHeight = self.HEIGHT / self.zoom
        viewRectX = self.center.x() - viewRectWidth / 2
        viewRectY = self.center.y() - viewRectHeight / 2
        self.viewRect = QRectF(viewRectX, viewRectY, viewRectWidth, viewRectHeight)

        def intersectWithViewRect(line):
            if isinstance(line, QLineF):
                return any([line.intersect(vrl, QPointF()) == 1 for vrl in self.SCREEN_RECT_LINE])
            return line.intersects(self.SCREEN_RECT)

        def inScreen(edge):
            return self.SCREEN_RECT.contains(self.g.vs[edge.source]['pos']) \
                   or self.SCREEN_RECT.contains(self.g.vs[edge.target]['pos'])

        self.g.vs['pos'] = [QPointF(
            self.toScaledX(v['x']),
            self.toScaledY(v['y'])
        ) for v in self.g.vs]

        multipleEdge = {}
        for e in self.g.es:
            count = e.count_multiple()
            key = (e.source, e.target)
            if count > 1 and key not in multipleEdge:
                p1 = self.g.vs[e.source]['pos']
                p2 = self.g.vs[e.target]['pos']
                midPoint = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
                normalVector = QVector2D(p1.y() - p2.y(), p2.x() - p1.x())
                startVector = QVector2D(midPoint.x() - normalVector.x() / 2, midPoint.y() - normalVector.y() / 2)
                incVector = normalVector / (count - 1)
                multipleEdge[key] = [(p1, p2, (startVector + incVector * i).toPointF())
                                     for i in range(count)]

        def createLine(edge):
            result = multipleEdge.get((edge.source, edge.target))
            if result:
                pos1, pos2, controlPoint = result.pop()
                path = QPainterPath(pos1)
                path.quadTo(controlPoint, pos2)
                path.quadTo(controlPoint, pos1)
                return path
            return QLineF(
                self.g.vs[edge.source]['pos'],
                self.g.vs[edge.target]['pos'],
            )

        self.g.es['line'] = [createLine(e) for e in self.g.es]

        self.verticesToDraw = [v for v in self.g.vs if self.viewRect.contains(v['x'], v['y'])]

        linesInScreen = {e for e in self.g.es if inScreen(e)}
        linesIntersectScreen = {e for e in self.g.es if intersectWithViewRect(e['line'])}
        self.edgesToDraw = list(linesInScreen.union(linesIntersectScreen))

        for mode in self.modes:
            if mode.onUpdateViewRect():
                break

    def paintEvent(self, event):
        self.updateViewRect()
        painter = QPainter()
        painter.begin(self)
        self.paint(painter)
        painter.end()

    def paint(self, painter):
        for mode in self.modes:
            if mode.onPaintBegin(painter):
                break

        for mode in self.modes:
            if mode.beforePaintEdges(painter):
                break
        for edge in self.edgesToDraw:
            painter.setPen(edge['color'])
            line = edge['line']
            if isinstance(line, QLineF):
                painter.drawLine(line)
            else:
                painter.drawPath(line)

        for mode in self.modes:
            if mode.beforePaintVertices(painter):
                break
        for vertex in self.verticesToDraw:
            painter.setBrush(vertex['color'])
            painter.drawEllipse(
                int(vertex['pos'].x() - self.POINT_RADIUS / 2.0),
                int(vertex['pos'].y() - self.POINT_RADIUS / 2.0),
                self.POINT_RADIUS, self.POINT_RADIUS
            )

        for mode in self.modes:
            if mode.beforePaintSelectedEdges(painter):
                break
        for edge in self.selectedEdges:
            line = edge['line']
            if isinstance(line, QLineF):
                painter.drawLine(line)
            else:
                painter.drawPath(line)

        for mode in self.modes:
            if mode.beforePaintSelectedVertices(painter):
                break
        for vertex in self.selectedVertices:
            painter.setBrush(vertex['color'])
            painter.drawEllipse(
                int(vertex['pos'].x() - self.POINT_RADIUS / 2.0),
                int(vertex['pos'].y() - self.POINT_RADIUS / 2.0),
                self.POINT_RADIUS, self.POINT_RADIUS
            )

    def zoomIn(self):
        self.zoom *= 1.2
        self.update()

    def zoomOut(self):
        self.zoom /= 1.2
        self.update()

    def zoomReset(self):
        self.zoom = 1
        self.center = QPointF(self.WIDTH / 2, self.HEIGHT / 2)
        self.update()

    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y() / 120 * 0.05
        self.update()

    def mousePressEvent(self, event):
        pos = event.pos()

        clickedSquare = QPainterPath(pos)
        clickedSquare.addRect(QRectF(
            pos.x() - self.CURVE_SELECT_SQUARE_SIZE / 2,
            pos.y() - self.CURVE_SELECT_SQUARE_SIZE / 2,
            self.CURVE_SELECT_SQUARE_SIZE,
            self.CURVE_SELECT_SQUARE_SIZE
        ))

        def clickToLine(line):
            if isinstance(line, QLineF):
                try:
                    d = abs((line.x2() - line.x1()) * (line.y1() - pos.y()) - (line.x1() - pos.x()) *
                            (line.y2() - line.y1())) / sqrt((line.x2() - line.x1()) ** 2 + (line.y2() - line.y1()) ** 2)
                except ZeroDivisionError:
                    return False
                return d < self.LINE_DISTANCE and min(line.x1(), line.x2()) < pos.x() < max(line.x1(), line.x2())

            return line.intersects(clickedSquare)

        def clickedToPoint(point):
            return self.POINT_RADIUS ** 2 >= (point.x() - pos.x()) ** 2 + (point.y() - pos.y()) ** 2

        for v in self.verticesToDraw:
            if clickedToPoint(v['pos']):
                for mode in self.modes:
                    if mode.onSelectVertex(v, event):
                        break
                self.update()
                return

        for e in self.edgesToDraw:
            if clickToLine(e['line']):
                for mode in self.modes:
                    if mode.onSelectEdge(e, event):
                        break
                self.update()
                return

        for mode in self.modes:
            if mode.onSelectBackground(event):
                return

        self.update()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        for mode in self.modes:
            if mode.onMouseMove(event):
                break
        self.update()

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        for mode in self.modes:
            if mode.onMouseRelease(event):
                break
        self.update()
