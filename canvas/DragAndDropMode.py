from PyQt5.QtCore import QPointF, Qt

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

    def onSelectVertex(self, vertex, event):
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

    def onSelectBackground(self, event):
        if event.button() == Qt.LeftButton:
            self.canvas.selectedVertices = []
            self.gui.setPageInfoVisible(False)
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
