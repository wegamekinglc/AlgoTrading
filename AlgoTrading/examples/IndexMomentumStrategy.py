# -*- coding: utf-8 -*-
u"""
Created on 2016-2-3

@author: cheng.li
"""

import datetime as dt
from AlgoTrading.api import Strategy
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import DataSource
from PyFin.api import MMAX
from PyFin.api import MMIN
from PyFin.api import CLOSE


class IndexMomentumStrategy(Strategy):

    def __init__(self):
        self.preMax = MMAX(10, 'close').shift(1)
        self.preMin = MMIN(10, 'close').shift(1)
        self.maxOI = MMAX(10, 'openInterest')
        self.current = CLOSE()
        self.count = 0

    def handle_data(self):
        self.count += 1
        for secID in self.tradableAssets:
            if self.count > 10:
                if self.current[secID] > self.preMax[secID]:
                    self.order_to(secID, 1, 1)
                elif self.current[secID] < self.preMin[secID]:
                    self.order_to(secID, -1, 1)
                else:
                    self.order_to(secID, 1, 0)

            self.keep('close_' + secID, self.current[secID])
            self.keep('max10_' + secID, self.preMax[secID])
            self.keep('min10_' + secID, self.preMin[secID])


def run_example():
    universe = ['if1701.ccfx']

    startDate = dt.datetime(2016, 10, 7)
    endDate = dt.datetime(2016, 12, 4)

    strategyRunner(userStrategy=IndexMomentumStrategy,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DXDataCenter,
                   benchmark='000001.zicn',
                   freq=5,
                   logLevel='info',
                   plot=True,
                   saveFile=False)


if __name__ == "__main__":
    run_example()

