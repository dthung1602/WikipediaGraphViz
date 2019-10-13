from abc import ABC


class Mode(ABC):
    conflict_modes = []
    priority = None

    def __init__(self, gui):
        self.gui = gui
        self.canvas = gui.canvas

    def onSet(self):
        pass

    def onUnset(self):
        pass

    def onSetGraph(self):
        pass

    def onNewVertexAdded(self, vertex):
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

    def onSelectVertex(self, vertex, pos):
        pass

    def onSelectEdge(self, edge, pos):
        pass

    def onSelectBackground(self, pos):
        pass

    def onMouseMove(self, pos):
        pass

    def onMouseRelease(self, pos):
        pass
