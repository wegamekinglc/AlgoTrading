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
from PyFin.api import MMAX
from PyFin.api import MMIN


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):
        filtering = (MMAX(10, 'close') / MMIN(10, 'close')) >= 1.00
        indicator = MA(10, 'close') - MA(120, 'close')
        self.signal = indicator[filtering]

    def handle_data(self):
        print(self.current_datetime)
        for s in self.universe:
            amount = self.avaliableForSale(s)
            if self.signal[s] > 0. and self.secPos[s] == 0:
                self.order(s, 1, quantity=200)
            if self.signal[s] < 0. and amount != 0:
                self.order(s, -1, quantity=200)


def run_example():
    universe = set_universe('000300.zicn')[:10]
    startDate = dt.datetime(2001, 1, 1)
    endDate = dt.datetime(2017, 1, 1)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   freq=0,
                   dataSource=DataSource.DataYes,
                   logLevel='info',
                   saveFile=True,
                   plot=True)


if __name__ == "__main__":
    from VisualPortfolio.Env import Settings
    from AlgoTrading.Env import Settings
    Settings.set_source(DataSource.DataYes)
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))
