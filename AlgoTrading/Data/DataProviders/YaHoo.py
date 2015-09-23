# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

import pandas.io.data as web
from AlgoTrading.Data.Data import DataFrameDataHandler


class YaHooDataProvider(DataFrameDataHandler):

    def __init__(self,
                 symbolList,
                 startDate,
                 endDate):
        super(YaHooDataProvider, self).__init__()
        self.symbolList = [s.lower() for s in symbolList]
        self.startDate = startDate
        self.endDate = endDate
        self._getDatas()

    def _getDatas(self):
        combIndex = None
        for s in self.symbolList:
            self.symbolData[s] = web.get_data_yahoo(s,
                                                    start=self.startDate.strftime("%Y%m%d"),
                                                    end=self.endDate.strftime("%Y%m%d"))
            self.symbolData[s].columns = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
            del self.symbolData[s]['close']
            self.symbolData[s].columns = ['open', 'high', 'low', 'volume', 'close']

            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

            self.latestSymbolData[s] = []

        for s in self.symbolList:
            self.symbolData[s] = self.symbolData[s].reindex(index=combIndex, method='pad').iterrows()
        self.dateIndex = combIndex


if __name__ == "__main__":
    pass