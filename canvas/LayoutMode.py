from .Mode import Mode

LAYOUT_OPTIONS = [
    ['Auto', 'auto'],
    ['Circle', 'layout_circle'],
    ['Distributed Recursive', 'layout_drl'],
    ['Fruchterman-Reingold', 'layout_fruchterman_reingold'],
    ['Graphopt', 'layout_graphopt'],
    ['Grid', 'layout_grid'],
    ['Kamada-Kawai', 'layout_kamada_kawai'],
    ['Large Graph', 'layout_lgl'],
    ['MDS', 'layout_mds'],
    ['Random', 'layout_random'],
    ['Reingold-Tilford', 'layout_reingold_tilford'],
    ['Reingold-Tilford Circular', 'layout_reingold_tilford_circular'],
    ['Star', 'layout_star']
]


class LayoutMode(Mode):
    priority = 2

    def __init__(self, gui):
        super().__init__(gui)
        self.layoutName = 'auto'
        self.initXY = None

    def onSetGraph(self):
        g = self.canvas.g
        vsAttributes = g.vs.attributes()

        # if xy not in graph data, use default layout
        if 'x' not in vsAttributes or 'y' not in vsAttributes:
            layout = g.layout_reingold_tilford_circular()
            for c, v in zip(layout.coords, g.vs):
                v['x'] = c[0]
                v['y'] = c[1]

        # fit coordinates to screen
        self.onResetViewRect()

        # backup
        self.initXY = {v: (v['x'], v['y']) for v in self.canvas.g.vs}

        self.applyLayout()

    def onResetViewRect(self):
        g = self.canvas.g

        # scale coordinates to screen
        mx = min(g.vs['x']) - 1
        my = min(g.vs['y']) - 1
        g.vs['x'] = [x - mx for x in g.vs['x']]
        g.vs['y'] = [y - my for y in g.vs['y']]

        mx = max(g.vs['x'])
        my = max(g.vs['y'])
        if mx / my > self.canvas.WIDTH / self.canvas.HEIGHT:
            scale = self.canvas.WIDTH / mx
        else:
            scale = self.canvas.HEIGHT / my

        g.vs['x'] = [x * scale for x in g.vs['x']]
        g.vs['y'] = [y * scale for y in g.vs['y']]

    def applyLayout(self):
        if self.layoutName == 'auto':
            for v in self.canvas.g.vs:
                coor = self.initXY.get(v)
                if coor:
                    v['x'] = coor[0]
                    v['y'] = coor[1]
                else:
                    v['x'] = self.canvas.toAbsoluteX(self.canvas.WIDTH / 2)
                    v['y'] = self.canvas.toAbsoluteY(self.canvas.HEIGHT / 2)
                    self.initXY[v] = (v['x'], v['y'])
        else:
            layout = getattr(self.canvas.g, self.layoutName)()
            for c, v in zip(layout.coords, self.canvas.g.vs):
                v['x'] = c[0]
                v['y'] = c[1]
        self.canvas.resetViewRect()

    def setLayout(self, layoutName):
        self.layoutName = layoutName
        self.applyLayout()
