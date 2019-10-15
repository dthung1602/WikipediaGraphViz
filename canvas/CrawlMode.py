from collections import deque
from datetime import timedelta
from random import randrange
from threading import Thread, Lock
from time import time, sleep

import wikipedia
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from igraph import Graph
from wikipedia.exceptions import WikipediaException

from .Mode import Mode


class CrawlMode(Mode, QObject):
    priority = 99

    statusUpdatedSignal = pyqtSignal(object)
    crawlDoneSignal = pyqtSignal(object)

    def __init__(self, gui):
        QObject.__init__(self)
        Mode.__init__(self, gui)

        self.terminate = False
        self.crawlThread = self.pauseLock = None
        self.language = 'en'
        self.searchAlgo = 'RAND'
        self.delay = 1
        self.startPage = None
        self.reachPage = self.maxPage = self.maxDepth = self.timeLimit = None
        self.toCrawl = deque()

        self._timeElapsed = 0
        self._status = 'stopped'  # stopped, paused, running, done

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.statusUpdatedSignal.emit(value)

    @property
    def timeElapsed(self):
        return self._timeElapsed

    @timeElapsed.setter
    def timeElapsed(self, value):
        self._timeElapsed = value
        self.statusUpdatedSignal.emit(value)

    def timeElapsedText(self):
        return str(timedelta(seconds=int(self.timeElapsed)))

    def onClose(self):
        self.stop()

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
        if self.timeLimit is not None and self.timeElapsed > self.timeLimit:
            return True
        return False

    def start(self):
        if self.startPage is None:
            self.startPage = wikipedia.random()
        self.toCrawl = deque([self.startPage])
        wikipedia.set_lang(self.language)

        self.status = 'running'
        self.timeElapsed = 0
        self.terminate = False
        self.pauseLock = Lock()
        self.canvas.setGraph(Graph(directed=True))
        self.crawlThread = Thread(target=self.crawl, daemon=False)
        self.crawlThread.start()

    def stop(self):
        self.status = 'stopped'
        self.terminate = True
        if self.pauseLock.locked():
            self.pauseLock.release()
        self.crawlThread.join()

    def pause(self):
        self.status = 'paused'
        self.pauseLock.acquire()

    def resume(self):
        self.status = 'running'
        self.pauseLock.release()

    def crawl(self):
        g = self.canvas.g

        while not self.terminate:
            startTime = time()

            # get page to crawl
            page = None
            while page is None:
                if len(self.toCrawl) == 0:
                    self.terminate = True
                    break
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

            # crawling usually take a long time
            # -> terminate signal may come
            # -> terminate for smooth behaviour
            if self.terminate:
                break

            # add vertex and edge
            g.add_vertex(
                page=page,
                x=self.canvas.WIDTH / 2,
                y=self.canvas.HEIGHT / 2,
                color=Qt.white
            )
            newVertexIndex = g.vcount() - 1
            for v in g.vs:
                if v.index != newVertexIndex and page.title in v['links']:
                    g.add_edge(v.index, newVertexIndex, color=Qt.white)
            for v in g.vs:
                if v.index != newVertexIndex and v['title'] in page.links:
                    g.add_edge(newVertexIndex, v.index, color=Qt.white)

            # add to crawl
            if self.searchAlgo == 'DFS':
                self.toCrawl.extendleft(page.links[::-1])
            else:
                self.toCrawl.extend(page.links)
                if self.searchAlgo == 'RAND':
                    # randomly swap 1st element to somewhere
                    i = randrange(0, len(self.toCrawl))
                    self.toCrawl[i], self.toCrawl[0] = self.toCrawl[0], self.toCrawl[i]

            # stuff
            self.terminate = self.terminate or self.checkStopConditions() or len(self.toCrawl) == 0
            sleep(self.delay)
            self.timeElapsed += time() - startTime

            # handle pause / resume
            self.pauseLock.acquire()
            self.pauseLock.release()

            # update canvas after handle pause / resume for smoother behavior
            startTime = time()
            self.canvas.notifyNewVertex()
            self.timeElapsed += time() - startTime

        self.status = 'done'
        self.crawlDoneSignal.emit('done')
