from math import isnan

from numpy import argsort, mean

from .Mode import Mode


class UpdateInfoMode(Mode):
    priority = 0

    def onSetGraph(self):
        self.recalculate()

    def onNewVertexAdded(self, vertex):
        g = self.canvas.g
        page = vertex['page']

        g['pageid'].add(page.pageid)
        g['title'].add(page.title)
        vertex['title'] = page.title
        vertex['pageid'] = page.pageid
        vertex['links'] = page.links

        if g['loadDetails']:
            g['category'].update(page.categories)
            vertex['summary'] = page.summary
            vertex['wordCount'] = page.summary.replace('\n', ' ').count(' ')
            vertex['refCount'] = len(page.references)
            vertex['imgCount'] = len(page.images)
            vertex['catCount'] = len(page.categories)
        else:
            vertex['summary'] = 'Summary is not available'
            vertex['wordCount'] = 0
            vertex['refCount'] = 0
            vertex['imgCount'] = 0
            vertex['catCount'] = 0

        del vertex['page']
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
            'radius': str(int(0 if isnan(g.radius()) else g.radius())),
            'density': str(g.density())[:5],
            'avgOutDeg': str(mean(g.outdegree()))[:5],
            'avgInDeg': str(mean(g.indegree()))[:5],
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
        self.gui.displayInfo(info)
