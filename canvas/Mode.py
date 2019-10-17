class Mode:
    conflict_modes = []
    priority = None

    def __init__(self, canvas):
        self.canvas = canvas

    def onSet(self):
        pass

    def onUnset(self):
        pass

    def onSetGraph(self):
        pass

    def onNewVerticesAdded(self):
        pass

    def onResetViewRect(self):
        pass

    def onUpdateViewRect(self):
        pass

    def onPaintBegin(self, painter):
        pass

    def beforePaintEdges(self, painter):
        pass

    def beforePaintVertices(self, painter):
        pass

    def beforePaintSelectedEdges(self, painter):
        pass

    def beforePaintSelectedVertices(self, painter):
        pass

    def onSelectVertex(self, vertex, event):
        pass

    def onSelectEdge(self, edge, event):
        pass

    def onSelectBackground(self, event):
        pass

    def onMouseMove(self, event):
        pass

    def onMouseRelease(self, event):
        pass

    def onClose(self):
        pass
