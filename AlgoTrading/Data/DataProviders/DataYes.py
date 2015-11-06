# -*- coding: utf-8 -*-
u"""
Created on 2015-9-21

@author: cheng.li
"""

import os
import tushare as ts
import numpy as np
import pandas as pd
from AlgoTrading.Data.Data import DataFrameDataHandler
from AlgoTrading.Utilities import logger


class DataYesMarketDataHandler(DataFrameDataHandler):

    _req_args = ['token', 'symbolList', 'startDate', 'endDate', 'benchmark']

    def __init__(self, **kwargs):
        super(DataYesMarketDataHandler, self).__init__()
        if kwargs['token']:
            ts.set_token(kwargs['token'])
        else:
            try:
                token = os.environ['DATAYES_TOKEN']
                ts.set_token(token)
            except KeyError:
                raise ValueError("Please input token or set up DATAYES_TOKEN in the envirement.")

        self.mt = ts.Market()
        self.idx = ts.Idx()
        self.symbolList = [s.lower() for s in kwargs['symbolList']]
        self.startDate = kwargs['startDate'].strftime("%Y%m%d")
        self.endDate = kwargs['endDate'].strftime("%Y%m%d")
        self._getDatas()
        if kwargs['benchmark']:
            self._getBenchmarkData(kwargs['benchmark'], self.startDate, self.endDate)

    def _getDatas(self):

        logger.info("Start loading bars from DataYes source...")

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
            logger.info("Symbol {0:s} is ready for back testing".format(s))

        self.dateIndex = combIndex
        self.start = 0
        for i, s in enumerate(self.symbolList):
            if s not in self.symbolData:
                del self.symbolList[i]

        logger.info("Bars loading finished!")

    def _getBenchmarkData(self, indexID, startTimeStamp, endTimeStamp):

        logger.info("Start loading benchmark {0:s} data from DataYes source...".format(indexID))

        indexData = self.mt.MktIdxd(indexID=indexID, beginDate=startTimeStamp, endDate=endTimeStamp, field='tradeDate,closeIndex')
        indexData['tradeDate'] = pd.to_datetime(indexData['tradeDate'], format="%Y-%m-%d")
        indexData.set_index('tradeDate', inplace=True)
        indexData.columns = ['close']
        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData

        logger.info("Benchmark data loading finished!")
