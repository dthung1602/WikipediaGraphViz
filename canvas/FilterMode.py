from .Mode import Mode

FILTER_VERTEX_OPTIONS = [
    ['Pagerank (relative)', 'pagerankRelative'],
    ['Pagerank', 'pagerank'],
    ['Closeness (relative)', 'closenessRelative'],
    ['Closeness', 'closeness'],
    ['Betweenness (relative)', 'betweennessRelative'],
    ['Betweenness', 'betweenness'],

    ['Out degree', 'outdegree'],
    ['In degree', 'indegree'],

    ['Reference count', 'refCount'],
    ['Image count', 'imgCount'],
    ['Category count', 'catCount'],
]


class FilterMode(Mode):
    priority = 3

    def __init__(self, canvas):
        super().__init__(canvas)
        self.min = float('-inf')
        self.max = float('inf')
        self.attr = 'pagerank'

    def onUpdateViewRect(self):
        if self.attr in ['outdegree', 'indegree']:
            shouldBeDrawn = lambda v: self.min <= getattr(v, self.attr)() <= self.max
        else:
            shouldBeDrawn = lambda v: False if v[self.attr] is None else self.min <= v[self.attr] <= self.max
        canvas = self.canvas
        toDraw = []
        toHide = set()
        for v in canvas.g.vs:
            if shouldBeDrawn(v):
                toDraw.append(v)
            else:
                toHide.add(v.index)
        canvas.verticesToDraw = toDraw
        toDraw = []
        for e in canvas.g.es:
            if not (e.source in toHide or e.target in toHide):
                toDraw.append(e)
        canvas.edgesToDraw = toDraw

    def setFilter(self, attr, minValue, maxValue):
        self.attr = attr
        self.min = minValue
        self.max = maxValue
