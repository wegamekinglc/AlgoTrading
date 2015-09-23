# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

import pandas.io.data as web
from AlgoTrading.Data.Data import DataFrameDataHandler


class YaHooDataProvider(DataFrameDataHandler):

    _req_args = ['symbolList', 'startDate', 'endDate']

    def __init__(self, **kwargs):
        super(YaHooDataProvider, self).__init__()
        self.symbolList = [s.lower() for s in kwargs['symbolList']]
        self.startDate = kwargs['startDate']
        self.endDate = kwargs['endDate']
        self._getDatas()

    def _getDatas(self):
        combIndex = None
        for s in self.symbolList:
            self.symbolData[s] = web.get_data_yahoo(s,
                                                    start=self.startDate.strftime("%Y%m%d"),
                                                    end=self.endDate.strftime("%Y%m%d"),
                                                    adjust_price=True).sort()
            del self.symbolData[s]['Adj_Ratio']
            self.symbolData[s].columns = ['open', 'high', 'low', 'close', 'volume']

            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

            self.latestSymbolData[s] = []

        for s in self.symbolList:
            self.symbolData[s] = self.symbolData[s].reindex(index=combIndex, method='pad').iterrows()
        self.dateIndex = combIndex
