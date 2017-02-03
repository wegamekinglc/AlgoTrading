# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from enum import IntEnum
from AlgoTrading.Data.Data import DataFrameDataHandler
from AlgoTrading.Utilities import transfromDFtoDict
from WindPy import w


_windExchangeMap = {'xshg': 'sh',
                 'xshe': 'sz',
                 'ccfx': 'cfe',# 中国金融期货交易所
                 'xsge': 'shf', # 上海期货交易所
                 'xzce': 'czc', # 郑州商品交易所
                 'xdce':'dce'} # 大连期货交易所

@unique
class FreqType(IntEnum):
    MIN1 = 1
    MIN5 = 5
    EOD = 0


class WindMarketDataHandler(DataFrameDataHandler):

    _req_args = ['symbolList', 'startDate', 'endDate', 'freq', 'benchmark']

    def __init__(self, **kwargs):
        super(WindMarketDataHandler, self).__init__(kwargs['logger'], kwargs['symbolList'])
        self.symbolList = [s.replace('xshg', 'sh') for s in self.symbolList]
        self.symbolList = [s.replace('xshe', 'sz') for s in self.symbolList]
        self.startDate = kwargs['startDate'].strftime("%Y%m%d")
        self.endDate = kwargs['endDate'].strftime("%Y%m%d")
        self._freq = kwargs['freq']
        self._getDatas()
        if kwargs['benchmark']:
            self._getBenchmarkData(kwargs['benchmark'], self.startDate, self.endDate)


    def _getDatas(self):
        self.logger.info("Start loading bars from Wind source...")
        combIndex = None
        result = {}

        for s in self.symbolList:
            result[s] = getOneSymbolData((s, self.startDate, self.endDate))
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

    def _getBenchmarkData(self, indexID, startDate, endDate):
        self.logger.info("Start loading benchmark {0:s} data from Wind source...".format(indexID))

        indexData = getOneSymbolData((indexID, startDate, endDate))
        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData

        self.logger.info("Benchmark data loading finished!")

    def updateInternalDate(self):
        return False


def getOneSymbolData(params):
    s = params[0]
    start = params[1]
    end = params[2]
    freq = params[3]
    if freq == FreqType.EOD:
        rawData = w.wsd(s,
                     'open,high,low,close,volums',
                     start,
                     end,
                     'Fill=Previous')
    else:
        rawData = w.wsi(s,
                        'open,high,low,close,volums',
                        start,
                        end,
                        'Fill=Previous,Barsize='+str(freq))

    if len(rawData.Data) == 0:
        return rawData
    else:
        output={'tradeDate':rawData.Times,
                'open':rawData.Data[0],
                'high':rawData.Data[1],
                'low':rawData.Data[2],
                'close':rawData.Data[3],
                'volume':rawData.Data[4]}
    data = pd.DataFrame(output)
    if freq == FreqType.EOD:
        data['tradeDate'] = data['tradeDate'].apply(lambda x: x.strftime('%Y-%m-%d'))
    data = data.reset_index('tradeDate')
    data.sort_index(inplace=True)
    data.columns = ['open', 'high', 'low', 'close', 'volume']
    return data
