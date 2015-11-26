# -*- coding: utf-8 -*-
u"""
Created on 2015-11-19

@author: cheng.li
"""

import datetime as dt
from AlgoTrading.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Enums import DataSource
from PyFin.api import MA


class MonitoringIndexStrategy(Strategy):

    def __init__(self):
        self.signal = MA(10, 'close')

    def handle_data(self):

        for s in self.universe:
            self.order(s, 1, 100)


def run_example():
    universe = ['600000.xshg', '000300.zicn']
    initialCapital = 1e5
    startDate = dt.datetime(2014, 12, 1)
    endDate = dt.datetime(2015, 11, 1)

    strategyRunner(userStrategy=MonitoringIndexStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DXDataCenter,
                   freq=0,
                   benchmark='000300.zicn',
                   logLevel="warning",
                   saveFile=True,
                   plot=True)


if __name__ == "__main__":
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))