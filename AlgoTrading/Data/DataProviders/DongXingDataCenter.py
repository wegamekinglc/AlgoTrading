# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

import datetime as dt
import numpy as np
import pandas as pd
from enum import IntEnum
from enum import unique
from DataAPI import api
from PyFin.api import makeSchedule
from PyFin.api import adjustDateByCalendar
from PyFin.api import BizDayConventions
from AlgoTrading.Data.Data import DataFrameDataHandler
from AlgoTrading.Env import Settings
from AlgoTrading.Utilities.functions import categorizeSymbols


@unique
class FreqType(IntEnum):
    MIN1 = 1
    MIN5 = 5
    EOD = 0


def route(freq):
    if freq == FreqType.MIN1:
        equity_api, future_api, index_api, future_api_con = api.GetEquityBarMin1, api.GetFutureBarMin1, api.GetIndexBarMin1, None
    elif freq == FreqType.MIN5:
        equity_api, future_api, index_api, future_api_con = api.GetEquityBarMin5, api.GetFutureBarMin5, api.GetIndexBarMin5, api.GetFutureBarMin5Continuing
    elif freq == FreqType.EOD:
        equity_api, future_api, index_api, future_api_con = api.GetEquityBarEOD, api.GetFutureBarEOD, api.GetIndexBarEOD, api.GetFutureBarEODContinuing
    else:
        raise ValueError("Unknown bar type {0}".format(freq))

    return equity_api, future_api, index_api, future_api_con


class DXDataCenter(DataFrameDataHandler):
    _req_args = ['symbolList', 'startDate', 'endDate', 'freq']

    def __init__(self, **kwargs):
        super(DXDataCenter, self).__init__(kwargs['logger'], kwargs['symbolList'])
        self.fields = ['productID', 'instrumentID', 'tradingDate', 'tradingTime', 'openPrice', 'highPrice', 'lowPrice',
                       'closePrice', 'volume', 'multiplier']
        self.startDate = kwargs['startDate']
        self.endDate = kwargs['endDate']
        self._freq = kwargs['freq']
        self.baseDate = adjustDateByCalendar('China.SSE', self.endDate, BizDayConventions.Preceding)

        if not Settings.usingCache:
            self.forceUpdate = True
        else:
            self.forceUpdate = False

        if self._freq == FreqType.MIN5:
            self.loadSchedule = makeSchedule(self.startDate, self.endDate, '1m')
        elif self._freq == FreqType.MIN1:
            self.loadSchedule = makeSchedule(self.startDate, self.endDate, '7d')
        else:
            self.loadSchedule = [self.startDate, self.endDate]

        self.schCurrEnd = 1

        while True:
            self._getMinutesBars(startDate=self.loadSchedule[self.schCurrEnd - 1].strftime("%Y-%m-%d"),
                                 endDate=self.loadSchedule[self.schCurrEnd].strftime("%Y-%m-%d"),
                                 freq=self._freq)
            if self.symbolList:
                break
            self.logger.warning('There is no any valid data in the back-testing data range ({0} - {1})' \
                                .format(self.loadSchedule[self.schCurrEnd - 1], self.loadSchedule[self.schCurrEnd]))
            if self.schCurrEnd == len(self.loadSchedule) - 1:
                break
            self.schCurrEnd += 1

        if not self.symbolList:
            raise ValueError('There is no any valid data in the back-testing whole data range')

        if kwargs['benchmark']:
            self._getBenchmarkData(kwargs['benchmark'],
                                   self.startDate.strftime("%Y-%m-%d"),
                                   self.endDate.strftime("%Y-%m-%d"))

    def updateInternalDate(self):
        if self.schCurrEnd == len(self.loadSchedule) - 1:
            # get the end of the date series
            return False
        else:
            self.schCurrEnd += 1
            startDate = self.loadSchedule[self.schCurrEnd - 1] + dt.timedelta(days=1)
            endDate = self.loadSchedule[self.schCurrEnd]
            self._getMinutesBars(startDate=startDate.strftime("%Y-%m-%d"),
                                 endDate=endDate.strftime("%Y-%m-%d"),
                                 freq=self._freq)
            if len(self.dateIndex) == 0:
                return self.updateInternalDate()
            return True

    def _getMinutesBars(self, startDate, endDate, freq):

        self.logger.info("Start loading bars from DX source ({0} - {1})...".format(startDate, endDate))

        self.symbolList = self.whole_symbols[:]
        self.symbolData = {}

        equity_api, future_api, index_api, future_api_con = route(freq)

        equity_res = pd.DataFrame()
        future_res = pd.DataFrame()
        future_con_res = pd.DataFrame()
        index_res = pd.DataFrame()

        category = self.category(self.symbolList)

        if category['stocks']:
            equity_res = equity_api([s[:6] for s in category['stocks']],
                                    startDate,
                                    endDate,
                                    self.fields,
                                    baseDate=self.baseDate.strftime("%Y-%m-%d"),
                                    forceUpdate=self.forceUpdate)
        if category['futures']:
            future_res = future_api([f[:6] for f in category['futures']],
                                    startDate,
                                    endDate,
                                    self.fields,
                                    forceUpdate=self.forceUpdate)

        if category['futures_con']:
            cat = [f.split('.')[0] for f in category['futures_con']]
            future_con_res = future_api_con(cat,
                                            startDate,
                                            endDate,
                                            self.fields,
                                            forceUpdate=self.forceUpdate)

        if category['indexes']:
            index_res = index_api([i[:6] for i in category['indexes']],
                                  startDate,
                                  endDate,
                                  self.fields,
                                  forceUpdate=self.forceUpdate)

        res = equity_res.append(future_res)
        res = res.append(index_res)
        res = res.append(future_con_res)

        timeIndexList = []
        dataList = []

        if 'multiplier' in res:
            res = res[['securityID',
                       'tradingDate',
                       'tradingTime',
                       'openPrice',
                       'highPrice',
                       'lowPrice',
                       'closePrice',
                       'volume',
                       'instrumentID',
                       'multiplier']]
        else:
            res = res[['securityID',
                       'tradingDate',
                       'tradingTime',
                       'openPrice',
                       'highPrice',
                       'lowPrice',
                       'closePrice',
                       'volume',
                       'instrumentID']]
        res = res.as_matrix()
        for row in res:
            s = row[0]
            if s not in self.symbolData:
                self.symbolData[s] = {}

            timeIndexList.append(row[1] + " " + row[2][0:8] + "+0000")
            if len(row) >= 10:
                dataList.append((s, {'open': row[3],
                                     'high': row[4],
                                     'low': row[5],
                                     'close': row[6],
                                     'volume': row[7],
                                     'instrumentid': row[8],
                                     'multiplier': row[9]}))
            else:
                dataList.append((s, {'open': row[3],
                                     'high': row[4],
                                     'low': row[5],
                                     'close': row[6],
                                     'volume': row[7],
                                     'instrumentid': row[8]}))

        timeIndexList = np.array(timeIndexList, dtype='datetime64').astype(dt.datetime)
        for timeIndex, data in zip(timeIndexList, dataList):
            self.symbolData[data[0]][timeIndex] = data[1]

        self.dateIndex = np.unique(timeIndexList)
        self.dateIndex.sort()
        self.start = 0
        for i, s in enumerate(self.symbolList):
            if s not in self.symbolData:
                del self.symbolList[i]

        self.logger.info("Loading bars finished.")

    def _getBenchmarkData(self, indexID, startTimeStamp, endTimeStamp):

        self.logger.info("Starting load benchmark {0:s} daily bar data from DX data center...".format(indexID))

        indexIDComp = indexID.split('.')

        if indexIDComp[1] == 'zicn':
            indexData = api.GetIndexBarEOD(indexIDComp[0],
                                           startDate=startTimeStamp,
                                           endDate=endTimeStamp,
                                           forceUpdate=self.forceUpdate)
        elif indexIDComp[1] == 'ccfx' or indexIDComp[1] == 'xzce' or indexIDComp[1] == 'xdce' or indexIDComp[1] == 'xsge':
            indexData = api.GetFutureBarEODContinuing(indexIDComp[0],
                                                      startDate=startTimeStamp,
                                                      endDate=endTimeStamp,
                                                      forceUpdate=self.forceUpdate)
        elif indexIDComp[1] == 'xshg' or indexIDComp[1] == 'xshe':
            indexData = api.GetEquityBarEOD(indexIDComp[0],
                                            startDate=startTimeStamp,
                                            endDate=endTimeStamp,
                                            forceUpdate=self.forceUpdate,
                                            baseDate='end')
        indexData = indexData[['closePrice']]
        indexData.columns = ['close']
        indexData.index = pd.to_datetime(indexData.index.date)
        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData

        self.logger.info("Benchmark data loading finished!")
