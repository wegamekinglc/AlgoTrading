# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from AlgoTrading.Data.Data import DataFrameDataHandler
from AlgoTrading.Utilities import transfromDFtoDict
from enum import Enum
from enum import unique
import tushare as ts


class StrEnum(str, Enum):
    pass


@unique
class FreqType(StrEnum):
    MIN5 = '5'
    MIN15 = '15'
    MIN30 = '30'
    MIN60 = '60'
    EOD = 'D'
    EOW = 'W'
    EOM = 'M'


@unique
class PriceAdjType(StrEnum):
    NoAdj = None
    Forward = 'qfq'  # 前复权
    Backward = 'hfq'  # 后复权


class TushareMarketDataHandler(DataFrameDataHandler):
    _req_args = ['symbolList', 'startDate', 'endDate', 'freq', 'benchmark', 'priceAdj']

    def __init__(self, **kwargs):
        super(TushareMarketDataHandler, self).__init__(kwargs['logger'], kwargs['symbolList'])
        self.startDate = kwargs['startDate'].strftime("%Y-%m-%d")
        self.endDate = kwargs['endDate'].strftime("%Y-%m-%d")
        self._freq = kwargs['freq']
        self.priceAdj = kwargs['priceAdj']
        self._getDatas()
        if kwargs['benchmark']:
            index = True if kwargs['benchmark'].split('.')[1] == 'zicn' else False
            self._getBenchmarkData(kwargs['benchmark'], self.startDate, self.endDate, self._freq, self.priceAdj,
                                   index=index)

    def _getDatas(self):
        self.logger.info("Start loading bars from Tushare source...")
        combIndex = None
        result = {}

        for s in self.symbolList:
            index = True if s.split('.')[1] == 'zicn' else False
            result[s] = getOneSymbolData((s, self.startDate, self.endDate, self._freq, self.priceAdj, index))
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

    def _getBenchmarkData(self, indexID, startDate, endDate, freq, priceAdj, index):
        self.logger.info("Start loading benchmark {0:s} data from Tushare source...".format(indexID))

        indexData = getOneSymbolData((indexID, startDate, endDate, freq, priceAdj, index))
        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData

        self.logger.info("Benchmark data loading finished!")

    def updateInternalDate(self):
        return False


def getOneSymbolData(params):
    s = params[0].split('.')[0]
    start = params[1]
    end = params[2]
    freq = params[3]
    priceAdj = params[4]
    index = params[5]

    data = ts.get_k_data(code=s, start=start, end=end, ktype=freq, autype=priceAdj, index=index)

    if data.empty:
        return
    data.index = pd.to_datetime(data['date'], format="%Y-%m-%d")
    data.sort_index(inplace=True)
    data = data[['open', 'high', 'low', 'close', 'volume']]
    return data
