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
                 token,
                 symbolList,
                 startDate,
                 endDate):
        ts.set_token(token)
        self.mt = ts.Market()
        self.symbolList = symbolList
        self.startDate = startDate.strftime("%Y%m%d")
        self.endDate = endDate.strftime("%Y%m%d")
        self.symbolData = {}
        self.latestSymbolData = {}
        self.continueBacktest = True
        self._getDatas()

    def _getDatas(self):
        combIndex = None
        for s in self.symbolList:
            self.symbolData[s] = self.mt.MktEqud(secID=s,
                                                 beginDate=self.startDate,
                                                 endDate=self.endDate,
                                                 field='tradeDate,openPrice,highestPrice,lowestPrice,turnoverVol,closePrice')
            self.symbolData[s].index = pd.to_datetime(self.symbolData[s]['tradeDate'], format="%Y-%m-%d")
            self.symbolData[s].columns = ['tradeDate', 'open', 'high', 'low', 'volume', 'close']
            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

                self.latestSymbolData[s] = []

            self.latestSymbolData[s] = []

        for s in self.symbolList:
            self.symbolData[s] = self.symbolData[s].reindex(index=combIndex, method='pad').iterrows()
        self.dateIndex = combIndex
