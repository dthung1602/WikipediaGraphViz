from math import isnan

from PyQt5.QtCore import pyqtSignal, QObject
from igraph._igraph import InternalError
from numpy import argsort, mean

from .Mode import Mode


def formatFloat(f):
    if isnan(f):
        return '0'
    s = str(float(f))
    if 'e' in s:
        return s[:5] + s[s.index('e'):]
    return s[:s.index('.') + 5]


class UpdateInfoMode(Mode, QObject):
    priority = 0

    updateSummarySignal = pyqtSignal(object)

    def __init__(self, canvas):
        QObject.__init__(self)
        Mode.__init__(self, canvas)

    def onSetGraph(self):
        self.recalculate()

    def onNewVerticesAdded(self):
        self.recalculate()

    def recalculate(self):
        # recalculate
        g = self.canvas.g
        for prop in ['pagerank', 'closeness', 'betweenness']:
            try:
                value = getattr(g, prop)()
            except InternalError as e:
                value = 0
                print(e)
            g.vs[prop] = value
            g.vs[prop + 'Relative'] = argsort(value)

        # update info
        info = {
            'pageCount': str(g.vcount()),
            'linkCount': str(g.ecount()),
            'catCount': str(len(g['category'])),
            'diameter': str(g.diameter()),
            'radius': str(int(0 if isnan(g.radius()) else g.radius())),
            'density': formatFloat(g.density()),
            'avgOutDeg': formatFloat(mean(g.outdegree())),
            'avgInDeg': formatFloat(mean(g.indegree()))
        }
        if len(self.canvas.selectedVertices) > 0:
            vertex = self.canvas.selectedVertices[-1]
            info.update({
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
        self.updateSummarySignal.emit(info)
