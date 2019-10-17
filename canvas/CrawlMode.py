from collections import deque
from datetime import timedelta
from random import randrange
from threading import Thread, Lock
from time import time, sleep

import wikipedia
from PyQt5.QtCore import pyqtSignal, QObject, QPointF
from PyQt5.QtGui import QColor, QPainterPath
from igraph import Graph
from wikipedia.exceptions import WikipediaException

from .Mode import Mode
from .ViewMode import ViewMode

WHITE = QColor(255, 255, 255)


class CrawlMode(Mode, QObject):
    priority = 99

    statusUpdatedSignal = pyqtSignal(object)
    newVerticesSignal = pyqtSignal(object)
    crawlDoneSignal = pyqtSignal(object)

    startSignal = pyqtSignal(object)
    stopSignal = pyqtSignal(object)
    pauseSignal = pyqtSignal(object)
    resumeSignal = pyqtSignal(object)

    def __init__(self, canvas):
        QObject.__init__(self)
        Mode.__init__(self, canvas)

        self.terminate = False
        self.crawlThread = self.pauseLock = None
        self.language = 'en'
        self.searchAlgo = 'RAND'
        self.delay = 1
        self.loadDetails = True
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
                        loadDetails=True, reachPage=None, maxPage=None, maxDepth=None, timeLimit=None):
        self.language = language
        self.searchAlgo = searchAlgo
        self.delay = delay
        self.startPage = startPage
        self.loadDetails = loadDetails
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

    def createNewGraph(self):
        g = Graph(directed=True)
        self.canvas.setGraph(g)
        g['loadDetails'] = self.loadDetails
        g['title'][self.startPage] = 0
        g.add_vertex(**self.createVertexInitAttr(self.startPage))

    def start(self):
        self.startSignal.emit(None)
        if self.startPage is None:
            self.startPage = wikipedia.random()
        self.toCrawl = deque([0])
        wikipedia.set_lang(self.language)

        self.status = 'running'
        self.timeElapsed = 0
        self.terminate = False
        self.pauseLock = Lock()
        self.createNewGraph()
        self.crawlThread = Thread(target=self.crawl, daemon=False)
        self.crawlThread.start()

    def stop(self):
        self.stopSignal.emit(None)
        self.status = 'stopped'
        self.terminate = True
        if self.pauseLock and self.pauseLock.locked():
            self.pauseLock.release()
        if self.crawlThread:
            self.crawlThread.join()

    def pause(self):
        self.pauseSignal.emit(None)
        self.status = 'paused'
        self.pauseLock.acquire()

    def resume(self):
        self.resumeSignal.emit(None)
        self.status = 'running'
        self.pauseLock.release()

    def getViewMode(self):
        for mode in self.canvas.modes:
            if isinstance(mode, ViewMode):
                return mode

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
                visitedIndex = self.toCrawl.popleft()
                pageTitle = g.vs[visitedIndex]['title']
                print('>> ' + pageTitle)
                try:
                    page = wikipedia.page(pageTitle, preload=self.loadDetails)
                    if page.pageid in g['pageid']:
                        page = None
                except (WikipediaException, KeyError) as e:
                    print(e)

            # crawling usually takes a long time
            # -> terminate signal may come
            # -> terminate for smooth behaviour
            if self.terminate:
                break

            # add vertices and edges
            vertex = g.vs[visitedIndex]
            vertex.update_attributes(**self.createVertexInitAttr(page))
            g['title'][page.title] = visitedIndex
            g['pageid'][page.pageid] = visitedIndex
            g['category'].update(page.categories)

            # add edges from newly visited vertex
            lineColor = self.getViewMode().lineColor
            for link in page.links:
                otherVertexIndex = g['title'].get(link)
                if otherVertexIndex is not None:  # to old vertices
                    g.add_edge(visitedIndex, otherVertexIndex, color=lineColor, line=QPainterPath())
                else:  # to new vertices
                    g.add_vertex(**self.createVertexInitAttr(link))
                    i = g.vcount() - 1
                    g.add_edge(visitedIndex, i, color=lineColor, line=QPainterPath())
                    g['title'][link] = i

            # add to crawl
            if self.searchAlgo == 'BFS':
                self.toCrawl.extend(range(visitedIndex + 1, g.vcount()))
            else:
                self.toCrawl.extendleft(range(g.vcount(), visitedIndex + 1, -1))
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
            self.newVerticesSignal.emit(None)
            startTime = time()
            self.timeElapsed += time() - startTime

        self.status = 'done'
        self.crawlDoneSignal.emit('done')

    def createVertexInitAttr(self, page):
        g = self.canvas.g
        viewMode = self.getViewMode()
        visited = isinstance(page, wikipedia.WikipediaPage)
        attrs = {
            'color': viewMode.visitedPageColor if visited else viewMode.unvisitedPageColor,
            'visited': visited
        }
        if visited:
            attrs.update({
                'title': page.title,
                'pageid': page.pageid,
                'links': page.links
            })
        else:
            attrs.update({
                'title': page,
                'pageid': '--',
                'links': [],
                'x': self.canvas.WIDTH / 2,
                'y': self.canvas.HEIGHT / 2,
                'pos': QPointF(
                    self.canvas.toScaledX(self.canvas.WIDTH / 2),
                    self.canvas.toScaledY(self.canvas.HEIGHT / 2)
                )
            })
        if visited and g['loadDetails']:
            attrs.update({
                'summary': page.summary,
                'wordCount': page.summary.replace('\n', ' ').count(' '),
                'refCount': len(page.references),
                'imgCount': len(page.images),
                'catCount': len(page.categories)
            })
        else:
            attrs.update({
                'summary': 'Summary is not available',
                'wordCount': 0,
                'refCount': 0,
                'imgCount': 0,
                'catCount': 0,
            })
        return attrs
