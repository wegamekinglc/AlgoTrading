# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

import datetime as dt

from AlgoTrading.api import Strategy
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import DataSource
from AlgoTrading.api import set_universe
from PyFin.api import MA
from PyFin.api import MAX
from PyFin.api import MIN


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):
        filtering = (MAX(10, 'close') / MIN(10, 'close')) >= 1.00
        indicator = MA(10, 'close') - MA(120, 'close')
        self.signal = indicator[filtering]

    def handle_data(self):
        for s in self.universe:
            amount = self.avaliableForSale(s)
            if self.signal[s] > 0. and self.secPos[s] == 0:
                self.order(s, 1, quantity=200)
            if self.signal[s] < 0. and amount != 0:
                self.order(s, -1, quantity=200)


def run_example():
    universe = set_universe('000300.zicn')[:10]
    startDate = dt.datetime(2007, 1, 1)
    endDate = dt.datetime(2015, 10, 1)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   freq=0,
                   benchmark='000300.zicn',
                   logLevel='info',
                   saveFile=True,
                   plot=True)


if __name__ == "__main__":
    # from VisualPortfolio.Env import Settings
    # from AlgoTrading.Env import Settings
    # Settings.set_source(DataSource.DataYes)
    # Settings.set_source(DataSource.DataYes)
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))
