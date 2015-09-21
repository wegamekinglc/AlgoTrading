# -*- coding: utf-8 -*-
u"""
Created on 2015-9-21

@author: cheng.li
"""

import tushare as ts
import pandas as pd
import numpy as np
from AlgoTrading.Events.Event import MarketEvent
from AlgoTrading.Data.Data import DataFrameDataHandler


class DataYesMarketDataHandler(DataFrameDataHandler):

    def __init__(self,
                 symbolList,
                 startDate,
                 endDate):
        self.mt = ts.Market()
        self.symbolList = symbolList
        self.starDate = startDate
        self.endDate = endDate

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
            else:
                if bar is not None:
                    self.latestSymbolData[s].append(bar)
        self.events.put(MarketEvent())

    def _getNewBar(self, symbol):
        for b in self.symbolData[symbol]:
            yield b

    def _getDatas(self):
        combIndex = None
        for s in self.symbolList:
            self.symbolData[s] = self.mt.MktEqud(secID=s,
                                                 startDate=self.starDate,
                                                 endDate=self.endDate,
                                                 field='tradeDate,openPrice,highestPrice,lowestPrice,closePrice')
            self.symboData[s].index = pd.to_datetime(self.symbolData[s]['tradeDate'], format="%y-%m-%d")
            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

                self.latestSymbolData[s] = []

            for s in self.symbolList:
                self.symbolData[s] = self.symbolData[s].reindex(index=combIndex, method='pad').iterrows()
