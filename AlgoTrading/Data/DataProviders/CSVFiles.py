# -*- coding: utf-8 -*-
u"""
Created on 2015-9-21

@author: cheng.li
"""

import os
import pandas.io as io
from AlgoTrading.Data.Data import DataFrameDataHandler


class HistoricalCSVDataHandler(DataFrameDataHandler):

    _req_args = ['csvDir', 'symbolList']

    def __init__(self, **kwargs):
        super(HistoricalCSVDataHandler, self).__init__()
        self.csvDir = kwargs['csvDir']
        self.symbolList = [s.lower() for s in kwargs['symbolList']]
        self._openConvertCSVFiles()

    def _openConvertCSVFiles(self):
        combIndex = None
        for s in self.symbolList:
            filePath = os.path.join(self.csvDir, "{0:s}.csv".format(s))
            self.symbolData[s] = io.parsers.read_csv(filePath,
                                                     header=0,
                                                     index_col=0,
                                                     parse_dates=True,
                                                     usecols=['datetime', 'open', 'high', 'low', 'close', 'volume']).sort()

            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

            self.latestSymbolData[s] = []

        for s in self.symbolList:
            self.symbolData[s] = self.symbolData[s].reindex(index=combIndex, method='pad').iterrows()
        self.dateIndex = combIndex
