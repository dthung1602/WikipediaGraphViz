from PyQt5.QtCore import QPointF, Qt, pyqtSignal, QObject

from .Mode import Mode


class DragAndDropMode(Mode, QObject):
    conflict_modes = []
    priority = 1

    vertexSelectedSignal = pyqtSignal(object)
    backgroundSelectedSignal = pyqtSignal(object)

    def __init__(self, canvas):
        QObject.__init__(self)
        Mode.__init__(self, canvas)
        self.backgroundDragging = None

    def onSetGraph(self):
        self.canvas.selectedVertices = []
        self.canvas.selectedEdges = []

    def onSelectVertex(self, vertex, event):
        self.vertexSelectedSignal.emit({
            'pageTitle': vertex['title'],
            'pageRank': str(vertex['pagerankRelative']),
            'pageID': str(vertex['pageid']),
            'pageInLinkCount': str(vertex.indegree()),
            'pageOutLinkCount': str(vertex.outdegree()),
            'pageRefCount': str(vertex['refCount']),
            'pageImgCount': str(vertex['imgCount']),
            'pageWordCount': str(vertex['wordCount']),
            'pageCatCount': str(vertex['catCount']),
            'pageSummary': vertex['summary'],
        })
        # self.gui.setPageInfoVisible(True)
        self.canvas.selectedVertices = [vertex]
        self.canvas.selectedEdges = []

    def onSelectBackground(self, event):
        if event.button() == Qt.LeftButton:
            self.canvas.selectedVertices = []
            self.backgroundSelectedSignal.emit(None)  # .setPageInfoVisible(False)
        elif event.button() == Qt.RightButton:
            self.backgroundDragging = event.pos()

    def onMouseMove(self, event):
        pos = event.pos()
        if self.backgroundDragging is not None:
            center = self.canvas.center
            zoom = self.canvas.zoom
            self.canvas.center = QPointF(
                center.x() + (self.backgroundDragging.x() - pos.x()) / zoom,
                center.y() + (self.backgroundDragging.y() - pos.y()) / zoom,
            )
            self.backgroundDragging = pos
        elif len(self.canvas.selectedVertices) > 0:
            vertex = self.canvas.selectedVertices[0]
            vertex['x'] = self.canvas.toAbsoluteX(pos.x())
            vertex['y'] = self.canvas.toAbsoluteY(pos.y())

    def onMouseRelease(self, event):
        self.backgroundDragging = None
