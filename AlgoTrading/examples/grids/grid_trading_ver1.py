# -*- coding: utf-8 -*-
u"""
Created on 2016-2-5

@author: cheng.li
"""

import datetime as dt
import numpy as np
import bisect
import pandas as pd
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import Strategy
from AlgoTrading.api import DataSource
from AlgoTrading.api import PortfolioType
from PyFin.api import VARIANCE
from PyFin.api import MAX
from PyFin.api import MIN
from PyFin.api import CLOSE


class GridTradingStrategy(Strategy):

    def __init__(self, batches, pack):
        self.var = VARIANCE(120, 'close')
        self.max = MAX(120, 'high')
        self.min = MIN(120, 'low')
        self.close = CLOSE()
        self.batches = batches
        self.interval = {}
        self.bought_grid = {}
        self.bought_price = {}
        self.bought_amount = {}
        self.sold_grid = {}
        self.sold_price = {}
        self.sold_amount = {}
        self.count = 0
        self.pack = pack

    def handle_data(self):
        # 按照每120天，重新定义网格
        self.count += 1
        var = pd.Series()
        if self.count == 120:
            self.count = 0
            var = self.var.value
            for secID in self.universe:
                self.interval[secID] = []
                max = self.max[secID]
                min = self.min[secID]
                step = (max - min) / (self.batches - 1)
                if step != 0.:
                    self.interval[secID] = np.arange(min, max + 0.1, step)
                else:
                    del self.interval[secID]

        for secID in self.tradableAssets:
            if secID not in self.bought_grid:
                self.bought_grid[secID] = []
                self.bought_price[secID] = []
                self.bought_amount[secID] = []
            if secID not in self.sold_grid:
                self.sold_grid[secID] = []
                self.sold_price[secID] = []
                self.sold_amount[secID] = []
            try:
                interval = self.interval[secID]
            except KeyError:
                continue

            close = self.close[secID]
            grid = bisect.bisect_left(interval, close)

            # 开仓指令
            if True or (len(var) > 0 and var[secID] > 0.02):
                if grid < (self.batches + 1) / 2:
                    if grid not in self.bought_grid[secID]:
                        amount = self.pack
                        self.order(secID, 1, amount)
                        self.bought_grid[secID].append(grid)
                        self.bought_price[secID].append(close)
                        self.bought_amount[secID].append(amount)
                elif (self.batches + 1) / 2 < grid < self.batches:
                    if grid not in self.sold_grid[secID]:
                        amount = self.pack
                        self.order(secID, -1, amount)
                        self.sold_grid[secID].append(grid)
                        self.sold_price[secID].append(close)
                        self.sold_amount[secID].append(amount)

            # 获利平仓指令
            del_index = []
            for i, level in enumerate(self.bought_grid[secID]):
                if close > self.interval[secID][level + 1]:
                    amount = self.bought_amount[secID][i]
                    self.order(secID, -1, amount)
                    del_index.append(i)

            del_count = 0
            for i in del_index:
                del self.bought_grid[secID][i - del_count]
                del self.bought_price[secID][i - del_count]
                del self.bought_amount[secID][i - del_count]
                del_count += 1

            del_index = []
            for i, level in enumerate(self.sold_grid[secID]):
                if close < self.interval[secID][level - 1]:
                    amount = self.sold_amount[secID][i]
                    self.order(secID, 1, amount)
                    del_index.append(i)

            del_count = 0
            for i in del_index:
                del self.sold_grid[secID][i - del_count]
                del self.sold_price[secID][i - del_count]
                del self.sold_amount[secID][i - del_count]
                del_count += 1


def run_example():
    universe = ['000905.zicn']
    startDate = dt.datetime(2016, 1, 1)
    endDate = dt.datetime(2016, 9, 5)
    initialCapital = 10000000.
    batches = 10
    pack = 100

    strategyRunner(userStrategy=GridTradingStrategy,
                   initialCapital=initialCapital,
                   strategyParameters=(batches, pack),
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DXDataCenter,
                   portfolioType=PortfolioType.CashManageable,
                   freq=5,
                   logLevel="info",
                   saveFile=True,
                   plot=True)


if __name__ == "__main__":
    #Settings.enableCache()
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))



