from math import sqrt, atan2, cos
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
        return self.vs['refCount']

    def image(self):
        return self.vs['imgCount']

    for func in [reference, image]:
        bind(graph, func)

    graph['category'] = set()
    graph['title'] = dict()
    graph['pageid'] = dict()
    graph['loadDetails'] = True

    return graph


class Canvas(QWidget):
    POINT_RADIUS = 10
    ARROW_SIZE = 8
    SELECTED_ARROW_SIZE = 12
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

        self.liveUpdate = self.showUnvisited = True
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

    def close(self):
        for mode in self.modes:
            if mode.onClose():
                break
        super().close()

    def setGraph(self, g: Union[str, Graph]):
        if isinstance(g, str):
            g = igraph.read(g)
        self.g = wrapGraph(g)

        for mode in self.modes:
            if mode.onSetGraph():
                break
        self.resetViewRect()
        self.update()

    def notifyNewVertices(self):
        if self.liveUpdate:
            for mode in self.modes:
                if mode.onNewVerticesAdded():
                    break
        self.update()

    def saveGraph(self, fileName, saveDetails=False):
        g = self.g.copy()
        del g['title']
        del g['category']
        del g['pageid']
        del g.vs['pos']
        del g.es['line']
        if not saveDetails:
            del g.es['color']
            del g.vs['color']
            del g.vs['x']
            del g.vs['y']
            del g.vs['pagerank']
            del g.vs['pagerankRelative']
            del g.vs['closeness']
            del g.vs['closenessRelative']
            del g.vs['betweenness']
            del g.vs['betweennessRelative']
        else:
            g.vs['color'] = [c.name() for c in g.vs['color']]
            g.es['color'] = [c.name() for c in g.es['color']]
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

        self.updateViewRect()

    def createArrow(self, start, end, big=False):
        arrowSize = self.SELECTED_ARROW_SIZE if big else self.ARROW_SIZE
        xStart = start.x()
        yStart = start.y()
        xEnd = end.x()
        yEnd = end.y()

        baseVector = QVector2D(-xEnd + xStart, -yEnd + yStart)
        unitVector = baseVector / baseVector.length()
        baseVector = unitVector * arrowSize
        a = atan2(baseVector.y(), baseVector.x())
        p = pi / 6
        xb = arrowSize * cos(a - p)
        yb = arrowSize * sin(a - p)
        xc = arrowSize * cos(a + p)
        yc = arrowSize * sin(a + p)

        xEnd += unitVector.x() * self.POINT_RADIUS / 2
        yEnd += unitVector.y() * self.POINT_RADIUS / 2

        path = QPainterPath(QPointF(xStart, yStart))
        path.lineTo(xEnd, yEnd)
        path.lineTo(xEnd + xb, yEnd + yb)
        path.lineTo(xEnd + xc, yEnd + yc)
        path.lineTo(xEnd, yEnd)

        return path

    def updateViewRect(self):
        viewRectWidth = self.WIDTH / self.zoom
        viewRectHeight = self.HEIGHT / self.zoom
        viewRectX = self.center.x() - viewRectWidth / 2
        viewRectY = self.center.y() - viewRectHeight / 2
        self.viewRect = QRectF(viewRectX, viewRectY, viewRectWidth, viewRectHeight)

        self.g.vs['pos'] = [QPointF(
            self.toScaledX(v['x']),
            self.toScaledY(v['y'])
        ) for v in self.g.vs]

        self.g.es['line'] = [self.createArrow(
            self.g.vs[e.source]['pos'],
            self.g.vs[e.target]['pos'],
        ) for e in self.g.es]

        def shouldDrawVertex(v):
            if not self.showUnvisited and not v['visited']:
                return False
            return self.viewRect.contains(v['x'], v['y'])

        self.verticesToDraw = [v for v in self.g.vs if shouldDrawVertex(v)]

        index = set(v.index for v in self.verticesToDraw)

        def shouldDrawEdge(e):
            s, t, vs = e.source, e.target, self.g.vs
            if not (s in index or t in index):
                return False
            if not self.showUnvisited and not vs[t]['visited']:
                return False
            return True

        self.edgesToDraw = [e for e in self.g.es if shouldDrawEdge(e)]

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
            painter.drawPath(edge['line'])

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
            painter.drawPath(edge['line'])

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
