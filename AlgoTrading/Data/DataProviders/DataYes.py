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
from AlgoTrading.Utilities import transfromDFtoDict


class DataYesMarketDataHandler(DataFrameDataHandler):

    _req_args = ['token', 'symbolList', 'startDate', 'endDate', 'benchmark']

    def __init__(self, **kwargs):
        super(DataYesMarketDataHandler, self).__init__(kwargs['logger'], kwargs['symbolList'])
        if kwargs['token']:
            ts.set_token(kwargs['token'])
        else:
            try:
                token = os.environ['DATAYES_TOKEN']
                ts.set_token(token)
            except KeyError:
                raise ValueError("Please input token or set up DATAYES_TOKEN in the envirement.")

        self.idx = ts.Idx()
        self.mt = ts.Market()
        self.startDate = kwargs['startDate'].strftime("%Y%m%d")
        self.endDate = kwargs['endDate'].strftime("%Y%m%d")
        self._getDatas()
        if kwargs['benchmark']:
            self._getBenchmarkData(kwargs['benchmark'], self.startDate, self.endDate)

    def _getDatas(self):

        self.logger.info("Start loading bars from DataYes source...")

        combIndex = None

        result = {}

        category = self.category(self.symbolList)

        if category['stocks']:
            for s in category['stocks']:
                result[s] = getOneSymbolData((self.mt, s, self.startDate, self.endDate))
                self.logger.info("Symbol {0:s} is ready for back testing.".format(s))

        if category['indexes']:
            for s in category['indexes']:
                result[s] = getOneSymbolIndexData((self.mt, s, self.startDate, self.endDate))
                self.logger.info("Symbol {0:s} is ready for back testing.".format(s))

        if category['futures']:
            for s in category['futures']:
                result[s] = getOneSymbolFutureData((self.mt, s, self.startDate, self.endDate))
                self.logger.info("Symbol {0:s} is ready for back testing.".format(s))

        if category['futures_con']:
            for s in category['futures_con']:
                result[s] = getOneSymbolFutureContinuesData((self.mt, s, self.startDate, self.endDate))
                self.logger.info("Symbol {0:s} is ready for back testing.".format(s))

        for s in result:
            if not result[s].empty:
                self.symbolData[s] = result[s]
                if combIndex is None:
                    combIndex = self.symbolData[s].index
                else:
                    combIndex = combIndex.union(self.symbolData[s].index)

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

        indexIDComp = indexID.split('.')

        if indexIDComp[1] == 'zicn':
            indexData = getOneSymbolIndexData((self.mt, indexID, startTimeStamp, endTimeStamp))
        elif (indexIDComp[1] == 'ccfx' or indexIDComp[1] == 'xzce' or indexIDComp[1] == 'xdce' or indexIDComp[1] == 'xsge') and len(indexIDComp[0]) >= 3:
            indexData = getOneSymbolFutureData((self.mt, indexID, startTimeStamp, endTimeStamp))
        elif (indexIDComp[1] == 'ccfx' or indexIDComp[1] == 'xzce' or indexIDComp[1] == 'xdce' or indexIDComp[1] == 'xsge') and len(indexIDComp[0]) < 3:
            indexData = getOneSymbolFutureContinuesData((self.mt, indexID, startTimeStamp, endTimeStamp))
        elif indexIDComp[1] == 'xshg' or indexIDComp[1] == 'xshe':
            indexData = getOneSymbolData((self.mt, indexID, startTimeStamp, endTimeStamp))

        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData

        self.logger.info("Benchmark data loading finished!")

    def updateInternalDate(self):
        return False


def getOneSymbolData(params):
    mt = params[0]
    s = params[1]
    start = params[2]
    end = params[3]
    data = mt.MktEqud(secID=s,
                      beginDate=start,
                      endDate=end,
                      field='tradeDate,openPrice,highestPrice,lowestPrice,turnoverVol,closePrice')
    if data.empty:
        return
    data.index = pd.to_datetime(data['tradeDate'], format="%Y-%m-%d")
    data.sort_index(inplace=True)
    data.columns = ['tradeDate', 'open', 'high', 'low', 'volume', 'close']
    return data


def getOneSymbolIndexData(params):
    mt = params[0]
    s = params[1]
    start = params[2]
    end = params[3]
    data = mt.MktIdxd(indexID=s,
                      beginDate=start,
                      endDate=end,
                      field='tradeDate,openIndex,highestIndex,lowestIndex,turnoverVol,closeIndex')
    if data.empty:
        return
    data.index = pd.to_datetime(data['tradeDate'], format="%Y-%m-%d")
    data.sort_index(inplace=True)
    data.columns = ['tradeDate', 'open', 'high', 'low', 'volume', 'close']
    return data


def getOneSymbolFutureData(params):
    mt = params[0]
    s = params[1]
    start = params[2]
    end = params[3]
    data = mt.MktFutd(ticker=s[:6],
                      beginDate=start,
                      endDate=end,
                      field='tradeDate,openPrice,highestPrice,lowestPrice,turnoverVol,closePrice')
    if data.empty:
        return
    data.index = pd.to_datetime(data['tradeDate'], format="%Y-%m-%d")
    data.sort_index(inplace=True)
    data.columns = ['tradeDate', 'open', 'high', 'low', 'volume', 'close']
    return data


def getOneSymbolFutureContinuesData(params):
    mt = params[0]
    s = params[1]
    product = s.split('.')[0]
    start = params[2]
    end = params[3]
    data = mt.MktMFutd(contractObject=product,
                       mainCon=1,
                       startDate=start,
                       endDate=end,
                       field='tradeDate,openPrice,highestPrice,lowestPrice,turnoverVol,closePrice')
    if data.empty:
        return
    data.index = pd.to_datetime(data['tradeDate'], format="%Y-%m-%d")
    data.sort_index(inplace=True)
    data.columns = ['tradeDate', 'open', 'high', 'low', 'volume', 'close']
    return data
