# -*- coding: utf-8 -*-
u"""
Created on 2015-9-21

@author: cheng.li
"""

import tushare as ts
import pandas as pd
from AlgoTrading.Data.Data import DataFrameDataHandler


class DataYesMarketDataHandler(DataFrameDataHandler):

    _req_args = ['token', 'symbolList', 'startDate', 'endDate']

    def __init__(self, **kwargs):
        super(DataYesMarketDataHandler, self).__init__()
        ts.set_token(kwargs['token'])
        self.mt = ts.Market()
        self.symbolList = [s.lower() for s in kwargs['symbolList']]
        self.startDate = kwargs['startDate'].strftime("%Y%m%d")
        self.endDate = kwargs['endDate'].strftime("%Y%m%d")
        self._getDatas()

    def _getDatas(self):
        combIndex = None
        for s in self.symbolList:
            self.symbolData[s] = self.mt.MktEqud(secID=s,
                                                 beginDate=self.startDate,
                                                 endDate=self.endDate,
                                                 field='tradeDate,openPrice,highestPrice,lowestPrice,turnoverVol,closePrice')
            self.symbolData[s].index = pd.to_datetime(self.symbolData[s]['tradeDate'], format="%Y-%m-%d")
            self.symbolData[s].sort(inplace=True)
            self.symbolData[s].columns = ['tradeDate', 'open', 'high', 'low', 'volume', 'close']
            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

            self.latestSymbolData[s] = []

        for s in self.symbolList:
            self.symbolData[s] = self.symbolData[s].reindex(index=combIndex, method='pad').iterrows()
        self.dateIndex = combIndex
