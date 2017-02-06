# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
import datetime as dt
from AlgoTrading.Events import MarketEvent
from AlgoTrading.Events import DayBeginEvent
from AlgoTrading.Env import Settings
from AlgoTrading.Enums import DataSource
from AlgoTrading.Utilities.functions import categorizeSymbols


def set_universe(code, refDate=None):
    if Settings.data_source == DataSource.WIND:
        from WindPy import w
        if not w.isconnected():
            w.start()
        if not refDate:
            rawData = w.wset('IndexConstituent', 'windcode='+code)
        else:
            rawData = w.wset('IndexConstituent', 'date='+refDate, 'windcode='+code)
        if len(rawData.Data) == 0:
            return
        return rawData.Data[0]
    elif Settings.data_source != DataSource.DXDataCenter:
        import os
        import tushare as ts

        try:
            ts.set_token(os.environ['DATAYES_TOKEN'])
        except KeyError:
            raise
        idx = ts.Idx()
        return list(idx.IdxCons(secID=code, field='consID')['consID'])
    else:
        from DataAPI import api
        data = api.GetIndexConstitutionInfo(code, refDate=refDate).sort_values('conSecurityID')
        return list(data.conSecurityID)


class DataHandler(object):

    __metaclass__ = ABCMeta

    def __init__(self, logger, symbolList):
        self.logger = logger
        self.symbolList = [s.lower() for s in symbolList]

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
    def getPreviousDayValue(self, symbol, valType):
        raise NotImplementedError()

    @abstractmethod
    def updateBars(self):
        raise NotImplementedError()

    def setEvents(self, events):
        self.events = events

    @property
    def tradableAssets(self):
        return self.symbolList


class DataFrameDataHandler(DataHandler):

    def __init__(self, logger, symbolList):
        super(DataFrameDataHandler, self).__init__(logger=logger, symbolList=symbolList)
        self.symbolData = {}
        self.latestSymbolData = {}
        self.continueBacktest = True
        self.currentTimeIndex = dt.datetime(1970, 1, 1)
        self.previousSymbolData = None
        self.priceLimitHit = set()
        self.whole_symbols = self.symbolList[:]

    def category(self, symbols):
        return categorizeSymbols(symbols)

    @property
    def tradableAssets(self):
        category = self.category(self.symbolList)
        return list(set(category['stocks'] + category['futures'] + category['indexes'] + category['futures_con']))

    @property
    def allTradableAssets(self):
        category = self.category(self.whole_symbols)
        return list(set(category['stocks'] + category['futures'] + category['indexes'] + category['futures_con']))

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

    def getPreviousDayValue(self, symbol, valType):
        try:
            barsList = self.previousSymbolData[symbol]
        except KeyError:
            raise KeyError("the symbol {0:s} is not available in the previous day data set".format(symbol))
        else:
            return barsList[1][valType]

    def checkingDayBegin(self):
        try:
            currentTimeIndex = self.dateIndex[self.start]
        except IndexError:
            return None
        previousTimeIndex = self.currentTimeIndex
        if currentTimeIndex.date() > previousTimeIndex.date():
            self.events.put(DayBeginEvent(currentTimeIndex))
            self.previousSymbolData = self.latestSymbolData

    def updateBars(self):
        noDataCount = 0
        availableSymbol = set(self.symbolList)
        tradableAssets = set(self.tradableAssets)

        try:
            currentTimeIndex = self.dateIndex[self.start]
            self.start += 1
        except IndexError:
            flag = self.updateInternalDate()
            if not flag:
                self.continueBacktest = False
                return None, None
            else:
                return self.updateBars()
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
        self.events.put(MarketEvent(currentTimeIndex))
        self.currentTimeIndex = currentTimeIndex

        availableSymbol = list(availableSymbol)
        availableSymbol.sort()

        tradableAssets = list(tradableAssets)
        tradableAssets.sort()

        return availableSymbol, tradableAssets

    def _getNewBar(self, symbol, timeIndex):
        return self.symbolData[symbol][timeIndex]
