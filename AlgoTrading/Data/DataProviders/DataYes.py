# -*- coding: utf-8 -*-
u"""
Created on 2015-9-21

@author: cheng.li
"""

import tushare as ts
import numpy as np
import pandas as pd
from AlgoTrading.Data.Data import DataFrameDataHandler


class DataYesMarketDataHandler(DataFrameDataHandler):

    _req_args = ['token', 'symbolList', 'startDate', 'endDate', 'benchmark']

    def __init__(self, **kwargs):
        super(DataYesMarketDataHandler, self).__init__()
        ts.set_token(kwargs['token'])
        self.mt = ts.Market()
        self.idx = ts.Idx()
        self.symbolList = [s.lower() for s in kwargs['symbolList']]
        self.startDate = kwargs['startDate'].strftime("%Y%m%d")
        self.endDate = kwargs['endDate'].strftime("%Y%m%d")
        self._getDatas()
        if kwargs['benchmark']:
            self._getBenchmarkData(kwargs['benchmark'], self.startDate, self.endDate)

    def _getDatas(self):
        combIndex = None
        for s in self.symbolList:
            self.symbolData[s] = self.mt.MktEqud(secID=s,
                                                 beginDate=self.startDate,
                                                 endDate=self.endDate,
                                                 field='tradeDate,openPrice,highestPrice,lowestPrice,turnoverVol,closePrice')
            self.symbolData[s].index = pd.to_datetime(self.symbolData[s]['tradeDate'], format="%Y-%m-%d")
            self.symbolData[s].sort_index(inplace=True)
            self.symbolData[s].columns = ['tradeDate', 'open', 'high', 'low', 'volume', 'close']
            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

            self.latestSymbolData[s] = []
            self.symbolData[s] = self.symbolData[s].T.to_dict()

        self.dateIndex = combIndex
        self.start = 0
        for i, s in enumerate(self.symbolList):
            if s not in self.symbolData:
                del self.symbolList[i]

    def _getBenchmarkData(self, indexID, startTimeStamp, endTimeStamp):
        indexData = self.mt.MktIdxd(indexID=indexID, beginDate=startTimeStamp, endDate=endTimeStamp, field='tradeDate,closeIndex')
        indexData['tradeDate'] = pd.to_datetime(indexData['tradeDate'], format="%Y-%m-%d")
        indexData.set_index('tradeDate', inplace=True)
        indexData.columns = ['close']
        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData
