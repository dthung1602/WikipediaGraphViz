from numpy import argsort, mean

from .Mode import Mode


class UpdateInfoMode(Mode):
    priority = 0

    def onSetGraph(self):
        self.recalculate()

    def onNewVertexAdded(self, vertex):
        # g = self.canvas.g
        # g['category'].add(vertex.page.category)
        # page = vertex['page']
        # vertex['wordCount'] = page.summary.replace('\n', ' ').count(' ')
        # vertex['refCount'] = len(page.reference)
        # vertex['imgCount'] = len(page.iamge)
        # vertex['catCount'] = len(page.category)
        self.recalculate()

    def recalculate(self):
        # recalculate
        g = self.canvas.g
        for prop in ['pagerank', 'closeness', 'betweenness', 'evcent']:
            value = getattr(g, prop)()
            g.vs[prop] = value
            g.vs[prop + 'Relative'] = argsort(value)

        # update info
        info = {
            'pageCount': str(g.vcount()),
            'linkCount': str(g.ecount()),
            'catCount': str(len(g['category'])),
            'diameter': str(g.diameter()),
            'radius': str(int(g.radius())),
            'density': str(g.density())[:5],
            'avgOutDeg': str(mean(g.outdegree()))[:5],
            'avgInDeg': str(mean(g.indegree()))[:5],
            'avgShortestPath': '0'
        }
        if len(self.canvas.selectedVertices) > 0:
            vertex = self.canvas.selectedVertices[-1]
            page = vertex['page']
            info.update({
                'pageTitle': page.title,
                'pageRank': str(vertex['pagerankRelative']),
                'pageID': str(page.pageid),
                'pageInLinkCount': str(vertex.indegree()),
                'pageOutLinkCount': str(vertex.outdegree()),
                'pageRefCount': str(vertex['refCount']),
                'pageImgCount': str(vertex['imgCount']),
                'pageWordCount': str(vertex['wordCount']),
                'pageCatCount': str(vertex['catCount']),
                'pageSummary': page.summary,
            })
        self.gui.displayInfo(info)
