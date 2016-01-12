# -*- coding: utf-8 -*-
u"""
Created on 2015-11-30

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
        filtering = (MAX(10, 'close') / MIN(10, 'close')) >= 1.02
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
    universe = set_universe('000300.zicn')
    startDate = dt.datetime(2012, 1, 1)
    endDate = dt.datetime(2015, 10, 1)

    return strategyRunner(userStrategy=MovingAverageCrossStrategy,
                          symbolList=universe,
                          startDate=startDate,
                          endDate=endDate,
                          dataSource=DataSource.DXDataCenter,
                          benchmark='000300.zicn',
                          saveFile=False,
                          logLevel='critical',
                          plot=False)


if __name__ == "__main__":
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    res = run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))
