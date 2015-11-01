# -*- coding: utf-8 -*-
u"""
Created on 2015-9-22

@author: cheng.li
"""

import datetime as dt

from AlgoTrading.Strategy.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Backtest import DataSource
from PyFin.API import MA
from PyFin.API import MAX
from PyFin.API import MIN


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):
        filtering = (MAX(10, 'close') / MIN(10, 'close')) > 1.08
        indicator = MA(10, 'close') - MA(120, 'close')
        self.signal = indicator[filtering]

    def handle_data(self):
        for s in self.universe:
            if self.signal[s] > 0. and self.secPos[s] == 0:
                self.order(s, 1, quantity=5000)
            elif self.signal[s] < 0. and self.secPos[s] != 0:
                self.order(s, -1, quantity=5000)


def run_example():
    universe = ['000001.XSHE', '000002.XSHE', '000004.XSHE', '000005.XSHE', '000006.XSHE', '000007.XSHE', '000008.XSHE']
    initialCapital = 100000.0
    startDate = dt.datetime(2000, 1, 2)
    endDate = dt.datetime(2015, 9, 15)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DataYes,
                   token="2bfc4b3b06efa5d8bba2ab9ef83b5d61f1c3887834de729b60eec9f13e1d4df8",
                   benchmark='000300.zicn',
                   saveFile=False,
                   refreshRate=5,
                   plot=True)


if __name__ == "__main__":
    run_example()

