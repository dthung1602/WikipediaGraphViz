from .Mode import Mode


class SearchMode(Mode):
    priority = 0.9
    conflict_modes = ['ShortestPathMode']

    def reset(self):
        self.canvas.selectedEdges = []
        self.canvas.selectedVertices = []

    def onSet(self):
        self.reset()

    def onUnset(self):
        self.reset()

    def onSetGraph(self):
        self.reset()

    def search(self, searchTerm: str):
        searchTerm = searchTerm.strip().lower()
        if searchTerm != '':
            self.canvas.selectedVertices = [v for v in self.canvas.g.vs if searchTerm in v['title'].lower()]
        self.canvas.update()
