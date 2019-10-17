from math import sin, pi
from random import choice

from PyQt5.QtGui import *


def randomColor():
    return QColor(choice(range(0, 256)), choice(range(0, 256)), choice(range(0, 256)))


def createColors(n):
    def g(i):
        return 255 * (i + 1) / 2.0

    def f(start, stop, N):
        interval = (stop - start) / N
        for i in range(N):
            coefficient = start + interval * i
            yield int(g(sin(coefficient * pi)))

    red = f(0.5, 1.5, n)
    green = f(1.5, 3.5, n)
    blue = f(1.5, 2.5, n)
    return [('#%02x%02x%02x' % rgb) for rgb in zip(red, green, blue)]


def arrayToSpectrum(arr, relative):
    if relative:
        uniqueValues = set(arr)
        rgbs = createColors(len(uniqueValues))
        temp = sorted(uniqueValues, reverse=True)
        dictColor = {central: color for central, color in zip(temp, rgbs)}
        return [QColor(dictColor[i]) for i in arr]
    else:
        rgbs = createColors(101)
        minValue = min(arr)
        maxValue = max(arr)
        if maxValue == minValue:
            return [QColor(255, 0, 0)] * len(arr)
        step = (maxValue - minValue) / 100.0
        return [QColor(rgbs[100 - int((value - minValue) / step)]) for value in arr]
