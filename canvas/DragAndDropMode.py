from PyQt5.QtCore import QPointF
from igraph import IN, OUT

from .Mode import Mode


class DragAndDropMode(Mode):
    conflict_modes = []
    priority = 1

    def __init__(self, gui):
        super().__init__(gui)
        self.backgroundDragging = None

    def onSetGraph(self):
        self.canvas.selectedVertices = []
        self.canvas.selectedEdges = []

    def onSelectVertex(self, vertex, pos):
        # page = vertex['page']
        # self.gui.displayInfo({
        #     'pageTitle': page.title,
        #     'pageRank': str(vertex['pagerankRelative']),
        #     'pageID': str(page.pageid),
        #     'pageInLinkCount': str(vertex.indegree()),
        #     'pageOutLinkCount': str(vertex.outdegree()),
        #     'pageRefCount': str(len(page.reference)),
        #     'pageImgCount': str(len(page.image)),
        #     'pageWordCount': str(vertex['wordCount']),
        #     'pageCatCount': str(len(page.category)),
        #     'pageSummary': page.summary,
        # })
        self.canvas.selectedVertices = [vertex]
        self.gui.setPageInfoVisible(True)
        self.canvas.selectedEdges = []

    def onSelectBackground(self, pos):
        self.canvas.selectedVertices = []
        self.gui.setPageInfoVisible(False)
        self.backgroundDragging = pos

    def onMouseMove(self, pos):
        if len(self.canvas.selectedVertices) > 0:
            vertex = self.canvas.selectedVertices[0]
            vertex['x'] = self.canvas.toAbsoluteX(pos.x())
            vertex['y'] = self.canvas.toAbsoluteY(pos.y())
        elif self.backgroundDragging is not None:
            center = self.canvas.center
            zoom = self.canvas.zoom
            self.canvas.center = QPointF(
                center.x() + (self.backgroundDragging.x() - pos.x()) / zoom,
                center.y() + (self.backgroundDragging.y() - pos.y()) / zoom,
            )
            self.backgroundDragging = pos

    def onMouseRelease(self, pos):
        self.backgroundDragging = None
