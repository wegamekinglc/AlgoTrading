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


def categorizeSymbols(symbolList):

    lowSymbols = [s.lower() for s in symbolList]

    stocks = []
    futures = []
    indexes = []

    for s in lowSymbols:
        if s.endswith('xshg') or s.endswith('xshe'):
            stocks.append(s)
        elif s.endswith('zicn'):
            indexes.append(s)
        elif s[0].isalpha():
            futures.append(s)
        else:
            raise ValueError("Unknown securitie name {0}".format(s))

    return {'stocks': stocks, 'futures': futures, 'indexes': indexes}


class DataHandler(object):

    __metaclass__ = ABCMeta

    def __init__(self, logger, symbolList):
        self.logger = logger
        self.symbolList = [s.lower() for s in symbolList]
        self.category = categorizeSymbols(self.symbolList)

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

    @property
    def tradableAssets(self):
        return list(set(self.category['stocks'] + self.category['futures']))


class DataFrameDataHandler(DataHandler):

    def __init__(self, logger, symbolList):
        super(DataFrameDataHandler, self).__init__(logger=logger, symbolList=symbolList)
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
        tradableAssets = set(self.category['stocks'] + self.category['futures'])

        try:
            currentTimeIndex = self.dateIndex[self.start]
            self.start += 1
        except IndexError:
            self.continueBacktest = False
            return None, None
        for s in self.symbolList:
            try:
                bar = self._getNewBar(s, currentTimeIndex)
            except KeyError:
                noDataCount += 1
                availableSymbol.remove(s)
                if s in tradableAssets:
                    tradableAssets.remove(s)
            else:
                if bar is not None:
                    self.latestSymbolData[s] = (currentTimeIndex, bar)

        if noDataCount == len(self.symbolList):
            self.continueBacktest = False
            return None, None
        self.events.put(MarketEvent())
        self.currentTimeIndex = currentTimeIndex
        return availableSymbol, tradableAssets

    def _getNewBar(self, symbol, timeIndex):
        return self.symbolData[symbol][timeIndex]
