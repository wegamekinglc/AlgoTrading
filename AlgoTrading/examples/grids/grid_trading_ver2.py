# -*- coding: utf-8 -*-
u"""
Created on 2016-9-20

@author: cheng.li
"""

import bisect
import datetime as dt
import numpy as np
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import Strategy
from AlgoTrading.api import DataSource
from AlgoTrading.api import PortfolioType
from PyFin.api import MAX
from PyFin.api import MIN
from PyFin.api import CLOSE


class GridTradingStrategy(Strategy):

    def __init__(self):
        self.window = 500
        self.max = MAX(self.window, 'close')
        self.min = MIN(self.window, 'close')
        self.close = CLOSE()
        self.interval = {}
        self.count = 0
        self.batches = 10
        self.pack = 1
        self.grid_positions = {}
        self.upper_direction = 1
        self.lower_direction = -1

    def handle_data(self):

        secID = '000905.zicn'

        positions = self.secPosDetail(secID)

        self.count += 1
        if self.count == self.window:
            self.count = 0
            self.interval[secID] = []
            max = self.max[secID]
            min = self.min[secID]
            step = (max - min) / (self.batches - 1)
            if step != 0.:
                self.interval[secID] = np.arange(min, max + 0.1, step)
                self.order_to(secID, 1, 0)
                self.grid_positions[secID] = {}
            else:
                del self.interval[secID]

        try:
            interval = self.interval[secID]
        except KeyError:
            return

        close = self.close[secID]

        self.cut_lose(positions, close)
        self.cut_profit(positions, close)

        grid = bisect.bisect_left(interval, close)
        keys = list(self.grid_positions[secID].keys())

        if (self.batches + 1) / 2 < grid < self.batches - 1:
            if grid in self.grid_positions[secID]:
                return

            self.order(secID, self.upper_direction, self.pack)

            if self.grid_positions[secID] and keys[0] < (self.batches - 1) / 2:
                del self.grid_positions[secID][keys[0]]
            else:
                self.grid_positions[secID][grid] = close

    def cut_lose(self, positions, close):
        for i, row in positions.iterrows():
            pass

    def cut_profit(self, positions, close):
        for i, row in positions.iterrows():
            pass


def run_example():
    universe = ['000905.zicn']
    startDate = dt.datetime(2015, 12, 1)
    endDate = dt.datetime(2016, 9, 5)
    initialCapital = 10000000.

    strategyRunner(userStrategy=GridTradingStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DXDataCenter,
                   portfolioType=PortfolioType.CashManageable,
                   freq=5,
                   #benchmark='000905.zicn',
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