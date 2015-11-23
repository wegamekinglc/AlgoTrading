# -*- coding: utf-8 -*-
u"""
Created on 2015-9-22

@author: cheng.li
"""

import datetime as dt
import pandas as pd

from AlgoTrading.Strategy.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Backtest import DataSource
from PyFin.api import CLOSE
from PyFin.api import OPEN
from PyFin.api import LOW
from PyFin.api import HIGH
from PyFin.api import nthWeekDay
from PyFin.api import advanceDateByCalendar


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):

        indexes = ['000016.zicn', '000300.zicn', '000905.zicn']

        self.closes = CLOSE()
        self.preCloses = CLOSE().shift(1)
        self.openes = OPEN()
        self.lowes = LOW()
        self.highes = HIGH()

        # define indexes signal
        self.closeDLastClose = self.closes / self.preCloses
        self.closeDOpen = self.closes / self.openes
        self.closeDLow = self.closes / self.lowes
        self.oneMinusHigDClose = 1. - self.highes / self.closes

        self.indexSignals = [self.closeDLastClose, self.closeDOpen, self.closeDLow, self.oneMinusHigDClose]

        # index weight to calculate final score
        self.indexWeights = pd.Series([1., -2., 1.], index=['000016.zicn', '000300.zicn', '000905.zicn'])

    def handle_data(self):

        # calculate the index score
        elects = 0
        for signal in self.indexSignals:
            value = signal['000016.zicn', '000300.zicn', '000905.zicn'].dot(self.indexWeights)
            if value > 0.:
                elects += 1

        # find the right contracts to trade
        current_time = self.current_datetime

        year = current_time.year
        month = current_time.month

        delDay = nthWeekDay(3, 6, month, year)
        changeContractDay = advanceDateByCalendar('China.SSE', delDay, '-3b')
        print(u"换仓日:{0} 交割日：{1}".format(changeContractDay, delDay))


def run_example():
    indexes = ['000016.zicn', '000300.zicn', '000905.zicn']

    # futures to trade
    ihs = ['ih15%02d' % i for i in range(6, 12)]
    ifs = ['if15%02d' % i for i in range(6, 12)]
    ics = ['ic15%02d' % i for i in range(6, 12)]

    futures = ihs + ifs + ics

    universe = indexes + futures
    initialCapital = 100000.0
    startDate = dt.datetime(2015, 6, 1)
    endDate = dt.datetime(2015, 11, 1)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DataYes,
                   benchmark='000300.zicn',
                   saveFile=False,
                   plot=False)


if __name__ == "__main__":
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))
