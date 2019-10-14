from collections import deque
from random import randrange
from threading import Thread, Lock
from time import time, sleep

import wikipedia
from igraph import Graph
from wikipedia.exceptions import WikipediaException

from .Mode import Mode


class CrawlMode(Mode):
    priority = 99

    def __init__(self, gui):
        super().__init__(gui)
        self.startTime = None
        self.terminate = None
        self.thread = self.pauseLock = None
        self.language = self.searchAlgo = self.delay = self.startPage = None
        self.reachPage = self.maxPage = self.maxDepth = self.timeLimit = None
        self.toCrawl = None
        self.status = 'stopped'  # stopped, paused, running, done

    def setCrawlSetting(self, language='en', searchAlgo='BFS', delay=1, startPage='Graph theory',
                        reachPage=None, maxPage=None, maxDepth=None, timeLimit=None):
        self.language = language
        self.searchAlgo = searchAlgo
        self.delay = delay
        self.startPage = startPage
        self.reachPage = reachPage
        self.maxPage = maxPage
        self.maxDepth = maxDepth
        self.timeLimit = timeLimit

    def checkStopConditions(self):
        g = self.canvas.g
        if self.reachPage is not None and self.reachPage in g['title']:
            return True
        if self.maxPage is not None and g.vcount() >= self.maxPage:
            return True
        if self.maxDepth is not None and len(
                g.get_shortest_paths(0, g.vcount() - 1, output='epath')[0]) > self.maxDepth:
            return True
        if self.timeLimit is not None and self.elapsedTime() > self.timeLimit:
            return True
        return False

    def elapsedTime(self):
        return time() - self.startTime

    def start(self):
        self.toCrawl = deque([self.startPage])
        wikipedia.set_lang(self.language)

        self.status = 'running'
        self.startTime = time()
        self.terminate = False
        self.pauseLock = Lock()
        self.canvas.setGraph(Graph(directed=True))
        self.thread = Thread(target=self.crawl, daemon=False)
        self.thread.start()

    def stop(self):
        self.status = 'stopped'
        self.terminate = True
        if self.pauseLock.locked():
            self.pauseLock.release()
        self.thread.join()

    def pause(self):
        self.status = 'paused'
        self.pauseLock.acquire()

    def resume(self):
        self.status = 'running'
        self.pauseLock.release()

    def crawl(self):
        g = self.canvas.g

        while not self.terminate:
            # handle pause / resume
            self.pauseLock.acquire()
            self.pauseLock.release()

            # get page to crawl
            page = None
            while page is None:
                if len(self.toCrawl) == 0:
                    self.status = 'done'
                    self.gui.notifyCrawlDone()
                    return
                pageTitle = self.toCrawl.popleft()
                print(g['title'])
                while pageTitle in g['title']:
                    pageTitle = self.toCrawl.popleft()
                print('>> ' + pageTitle)
                try:
                    page = wikipedia.page(pageTitle, preload=True)
                    if page.pageid in g['pageid']:
                        page = None
                except (WikipediaException, KeyError) as e:
                    print(e)

            # add vertex and edge
            g.add_vertex(page=page, x=self.canvas.WIDTH / 2, y=self.canvas.HEIGHT / 2)
            newVertexIndex = g.vcount() - 1
            for v in g.vs:
                if v.index != newVertexIndex and page.title in v['links']:
                    g.add_edge(v.index, newVertexIndex)
            for v in g.vs:
                if v.index != newVertexIndex and v['title'] in page.links:
                    g.add_edge(newVertexIndex, v.index)
            self.canvas.notifyNewVertex()

            # add to crawl
            if self.searchAlgo == 'DFS':
                self.toCrawl.extendleft(page.links[::-1])
            else:
                self.toCrawl.extend(page.links)
                if self.searchAlgo == 'RAND':
                    # randomly swap 1st element to somewhere
                    i = randrange(0, len(self.toCrawl))
                    self.toCrawl[i], self.toCrawl[0] = self.toCrawl[0], self.toCrawl[i]

            # sleep
            sleep(self.delay)
            self.terminate = self.terminate or self.checkStopConditions() or len(self.toCrawl) == 0

        self.status = 'done'
        self.gui.notifyCrawlDone()