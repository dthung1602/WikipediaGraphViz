from .Mode import Mode


class ShortestPathMode(Mode):
    priority = 0.9

    def __init__(self, gui):
        super().__init__(gui)
        self.src = self.dst = None

    def reset(self):
        self.canvas.selectedVertices = []
        self.canvas.selectedEdges = []
        self.src = self.dst = None

    def onSet(self):
        self.reset()

    def onSetGraph(self):
        self.reset()

    def onUnset(self):
        self.reset()

    def onNewVertexAdded(self, vertex):
        if len(self.canvas.selectedVertices) == 2:
            self.findShortestPath()

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
        canvas = self.canvas
        svl = len(canvas.selectedVertices)
        if svl != 1:
            canvas.selectedVertices = [vertex]
            canvas.selectedEdges = []
        else:
            canvas.selectedVertices.append(vertex)
            self.src, self.dst = canvas.selectedVertices
            self.findShortestPath()
        return True

    def findShortestPath(self):
        canvas = self.canvas
        g = canvas.g
        path = g.get_shortest_paths(
            self.src,
            self.dst,
            output='epath'
        )
        if path[0]:
            canvas.selectedEdges = [g.es[i] for i in path[0]]
            canvas.selectedVertices = [g.vs[e.source] for e in canvas.selectedEdges] + [self.dst]
