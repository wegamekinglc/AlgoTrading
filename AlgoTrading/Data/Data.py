# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
import numpy as np
from AlgoTrading.Events import MarketEvent


class DataHandler(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def getLatestBar(self, symbol):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBars(self, symbol, N=1):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBarDatetime(self, symbol):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBarValue(self, symbol, valType):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBarsValues(self, symbol, valType, N=1):
        raise NotImplementedError()

    @abstractmethod
    def updateBars(self):
        raise NotImplementedError()

    def setEvents(self, events):
        self.events = events


class DataFrameDataHandler(DataHandler):

    def __init__(self):
        self.symbolData = {}
        self.latestSymbolData = {}
        self.continueBacktest = True

    def getStartDate(self):
        return self.dateIndex[0]

    def getLatestBar(self, symbol):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return barsList[-1]

    def getLatestBars(self, symbol, N=1):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return barsList[-N:]

    def getLatestBarDatetime(self, symbol):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return barsList[-1][0]

    def getLatestBarValue(self, symbol, valType):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return getattr(barsList[-1][1], valType)

    def getLatestBarsValues(self, symbol, valType, N=1):
        try:
            barsList = self.getLatestBars(symbol, N)
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return np.array([getattr(b[1], valType) for b in barsList])

    def updateBars(self):
        for s in self.symbolList:
            try:
                bar = next(self._getNewBar(s))
            except StopIteration:
                self.continueBacktest = False
                return
            else:
                if bar is not None:
                    self.latestSymbolData[s].append(bar)
        self.events.put(MarketEvent())

    def _getNewBar(self, symbol):
        for b in self.symbolData[symbol]:
            yield b


