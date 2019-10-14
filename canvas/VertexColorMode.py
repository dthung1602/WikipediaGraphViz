from igraph import VertexDendrogram

from .Mode import Mode
from .ViewMode import ViewMode
from .utils import randomColor, arrayToSpectrum

COLOR_VERTEX_OPTIONS = [
    ['Pagerank', 'pagerank'],
    ['Closeness', 'closeness'],
    ['Betweenness', 'betweenness'],
    ['Eigenvector', 'evcent'],
    ['Cluster', 'cluster'],
    ['Out degree', 'outdegree'],
    ['In degree', 'indegree'],
    ['Reference', 'reference'],
    ['Image', 'image'],
]

CLUSTERING_ALGO_OPTIONS = [
    ['Fast Greedy', 'community_fastgreedy'],
    ['Info Map', 'community_infomap'],
    ['Leading eigenvector', 'community_leading_eigenvector'],
    ['Label Propagation', 'community_label_propagation'],
    ['Multilevel', 'community_multilevel'],
    ['Edge Betweenness', 'community_edge_betweenness'],
    ['Walktrap', 'community_walktrap']
]


class VertexColorMode(Mode):
    priority = 3

    def __init__(self, gui):
        super().__init__(gui)
        self.enable = True
        self.relative = True
        self.method = 'pagerank'
        self.clusterAlgo = 'community_fastgreedy'

    def onSet(self):
        if self.canvas.g:
            self.applyColor()

    def onUnset(self):
        g = self.canvas.g
        for mode in self.canvas.modes:
            if isinstance(mode, ViewMode):
                g.vs['color'] = [mode.foregroundColor] * g.vcount()

    def onSetGraph(self):
        self.applyColor()

    def onNewVertexAdded(self, vertex):
        self.applyColor()

    def applyColor(self):
        g = self.canvas.g
        if self.method == 'cluster':
            clusters = getattr(g, self.clusterAlgo)()
            if isinstance(clusters, VertexDendrogram):
                clusters = clusters.as_clustering()
            clusters = clusters.subgraphs()

            def getClusterId(vertex):
                for cluster in clusters:
                    if vertex['pageid'] in cluster.vs['pageid']:
                        return str(id(cluster))

            clusterToColor = {str(id(cl)): randomColor() for cl in clusters}
            g.vs['cluster'] = [getClusterId(v) for v in g.vs]
            g.vs['color'] = [clusterToColor[v['cluster']] for v in g.vs]
        else:
            centrality = getattr(self.canvas.g, self.method)()
            g.vs['color'] = arrayToSpectrum(centrality, self.relative)
            g.vs['cluster'] = [color.name() for color in g.vs['color']]

    def setColorMethod(self, method, clusterAlgo, relative):
        self.method = method
        self.clusterAlgo = clusterAlgo
        self.relative = relative
        self.applyColor()
