# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

import datetime as dt

from AlgoTrading.Strategy.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Backtest import DataSource
from PyFin.api import MA


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):
        self.short_sma = MA(10, 'close')
        self.long_sma = MA(120, 'close')

    def handle_data(self):
        for s in self.universe:
            if self.short_sma[s] > self.long_sma[s] and self.secPos[s] == 0:
                self.order(s, 1, quantity=1000)
            elif self.short_sma[s] < self.long_sma[s] and self.secPos[s] != 0:
                self.order(s, -1, quantity=1000)


def run_example():
    universe = ['aapl', 'msft', 'ibm']
    initialCapital = 100000.0
    startDate = dt.datetime(1990, 1, 1)
    endDate = dt.datetime(2015, 9, 15)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.YAHOO,
                   saveFile=False)


if __name__ == "__main__":
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))
