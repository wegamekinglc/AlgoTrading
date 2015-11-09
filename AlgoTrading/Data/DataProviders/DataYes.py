# -*- coding: utf-8 -*-
u"""
Created on 2015-9-21

@author: cheng.li
"""

import os
import tushare as ts
from multiprocessing.pool import ThreadPool
import numpy as np
import pandas as pd
from AlgoTrading.Data.Data import DataFrameDataHandler
from AlgoTrading.Utilities import transfromDFtoDict


class DataYesMarketDataHandler(DataFrameDataHandler):

    _req_args = ['token', 'symbolList', 'startDate', 'endDate', 'benchmark']

    def __init__(self, **kwargs):
        super(DataYesMarketDataHandler, self).__init__(kwargs['logger'])
        if kwargs['token']:
            ts.set_token(kwargs['token'])
        else:
            try:
                token = os.environ['DATAYES_TOKEN']
                ts.set_token(token)
            except KeyError:
                raise ValueError("Please input token or set up DATAYES_TOKEN in the envirement.")

        self.idx = ts.Idx()
        self.symbolList = [s.lower() for s in kwargs['symbolList']]
        self.startDate = kwargs['startDate'].strftime("%Y%m%d")
        self.endDate = kwargs['endDate'].strftime("%Y%m%d")
        self._getDatas()
        if kwargs['benchmark']:
            self._getBenchmarkData(kwargs['benchmark'], self.startDate, self.endDate)

    def _getDatas(self):

        self.logger.info("Start loading bars from DataYes source...")

        combIndex = None

        pool = ThreadPool(25)
        result = {}

        def getOneSymbolData(params):
            mt = params[0]
            s = params[1]
            start = params[2]
            end = params[3]
            logger = params[4]
            result = params[5]
            data = mt.MktEqud(secID=s,
                              beginDate=start,
                              endDate=end,
                              field='tradeDate,openPrice,highestPrice,lowestPrice,turnoverVol,closePrice')
            data.index = pd.to_datetime(data['tradeDate'], format="%Y-%m-%d")
            data.sort_index(inplace=True)
            data.columns = ['tradeDate', 'open', 'high', 'low', 'volume', 'close']
            logger.info("Symbol {0:s} is ready for back testing.".format(s))
            result[s] = data

        pool.map(getOneSymbolData, [(ts.Market(), s, self.startDate, self.endDate, self.logger, result) for s in self.symbolList])

        for s in result:
            self.symbolData[s] = result[s]
            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

            self.latestSymbolData[s] = []
            self.symbolData[s] = transfromDFtoDict(self.symbolData[s])

            # transform

        self.dateIndex = combIndex
        self.start = 0
        for i, s in enumerate(self.symbolList):
            if s not in self.symbolData:
                del self.symbolList[i]

        self.logger.info("Bars loading finished!")

    def _getBenchmarkData(self, indexID, startTimeStamp, endTimeStamp):

        self.logger.info("Start loading benchmark {0:s} data from DataYes source...".format(indexID))

        indexData = ts.Market().MktIdxd(indexID=indexID, beginDate=startTimeStamp, endDate=endTimeStamp, field='tradeDate,closeIndex')
        indexData['tradeDate'] = pd.to_datetime(indexData['tradeDate'], format="%Y-%m-%d")
        indexData.set_index('tradeDate', inplace=True)
        indexData.columns = ['close']
        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData

        self.logger.info("Benchmark data loading finished!")







