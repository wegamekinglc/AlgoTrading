# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
from AlgoTrading.Events import MarketEvent


def set_universe(code):
    import tushare as ts
    ts.set_token('2bfc4b3b06efa5d8bba2ab9ef83b5d61f1c3887834de729b60eec9f13e1d4df8')
    idx = ts.Idx()
    return list(idx.IdxCons(secID=code, field='consID')['consID'])


class DataHandler(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def getLatestBar(self, symbol):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBarDatetime(self, symbol):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBarValue(self, symbol, valType):
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
            return barsList

    def getLatestBarDatetime(self, symbol):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return barsList[0]

    def getLatestBarValue(self, symbol, valType):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return barsList[1][valType]

    def updateBars(self):
        noDataCount = 0
        availableSymbol = set(self.symbolList)
        try:
            currentTimeIndex = self.dateIndex[self.start]
            self.start += 1
        except IndexError:
            self.continueBacktest = False
            return
        for s in self.symbolList:
            try:
                bar = self._getNewBar(s, currentTimeIndex)
            except KeyError:
                noDataCount += 1
                availableSymbol.remove(s)
            else:
                if bar is not None:
                    self.latestSymbolData[s] = (currentTimeIndex, bar)

        if noDataCount == len(self.symbolList):
            self.continueBacktest = False
            return
        self.events.put(MarketEvent())
        self.currentTimeIndex = currentTimeIndex
        return availableSymbol

    def _getNewBar(self, symbol, timeIndex):
        return self.symbolData[symbol][timeIndex]
