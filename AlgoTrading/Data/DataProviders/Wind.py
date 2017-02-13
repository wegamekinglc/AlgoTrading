# -*- coding: utf-8 -*-

# ref: http://wenku.baidu.com/view/1327f45bba1aa8114531d94f.html
# ref: http://wenku.baidu.com/link?url=Z4CIfS1TD5vFdC9e17pQB5AgfcqF1qRK_VyFtnNeq9L6x1cSm3lth1tPreu37KByHJr7B7iqAhPlwsakN9VB2vhaNPF_qssgVHFfH2Z9DAC
import pandas as pd
import numpy as np
from enum import Enum
from enum import unique
from AlgoTrading.Data.Data import DataFrameDataHandler
from AlgoTrading.Utilities import transfromDFtoDict
from AlgoTrading.Utilities.functions import convert2WindSymbol
from WindPy import w


class StrEnum(str, Enum):
    pass


@unique
class FreqType(StrEnum):
    MIN1 = 'min1'
    MIN5 = 'min5'
    MIN10 = 'min10'
    EOD = 'D'
    EOW = 'W'
    EOM = 'M'
    EOQ = 'Q'
    EOSY = 'S'
    EOY = 'Y'

@unique
class PriceAdjType(StrEnum):
    NoAdj = '0'
    Forward = 'F'   # 前复权
    Backward = 'B'  # 后复权


class WindMarketDataHandler(DataFrameDataHandler):

    _req_args = ['symbolList', 'startDate', 'endDate', 'freq', 'benchmark','priceAdj']

    def __init__(self, **kwargs):
        super(WindMarketDataHandler, self).__init__(kwargs['logger'], kwargs['symbolList'])
        if not w.isconnected():
            w.start()
        self.startDate = kwargs['startDate'].strftime("%Y%m%d")
        self.endDate = kwargs['endDate'].strftime("%Y%m%d")
        self._freq = kwargs['freq']
        self.priceAdj = kwargs['priceAdj']
        self._getDatas()
        if kwargs['benchmark']:
            self._getBenchmarkData(kwargs['benchmark'], self.startDate, self.endDate, self._freq, self.priceAdj)

    def _getDatas(self):
        self.logger.info("Start loading bars from Wind source...")
        combIndex = None
        result = {}

        for s in self.symbolList:
            result[s] = getOneSymbolData((s, self.startDate, self.endDate, self._freq, self.priceAdj))
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

    def _getBenchmarkData(self, indexID, startDate, endDate, freq, priceAdj):
        self.logger.info("Start loading benchmark {0:s} data from Wind source...".format(indexID))

        indexData = getOneSymbolData((indexID, startDate, endDate, freq, priceAdj))
        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData

        self.logger.info("Benchmark data loading finished!")

    def updateInternalDate(self):
        return False


def getOneSymbolData(params):
    s = convert2WindSymbol(params[0])
    start = params[1]
    end = params[2]
    freq = params[3]
    priceAdj = params[4]
    if freq == FreqType.EOD or freq == FreqType.EOW or freq == FreqType.EOM or freq == FreqType.EOQ or freq == FreqType.EOSY \
            or freq == FreqType.EOSY or freq == FreqType.EOY:
        rawData = w.wsd(s,
                     'open,high,low,close,volume',
                     start,
                     end,
                     'PriceAdj='+priceAdj, 'Period='+freq)
    else:
        rawData = w.wsi(s,
                        'open,high,low,close,volume',
                        start,
                        end,
                        'Barsize='+freq[3:])

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
        data['tradeDate'] = pd.to_datetime(data['tradeDate'])
    data = data.set_index('tradeDate')
    data.sort_index(inplace=True)
    return data


