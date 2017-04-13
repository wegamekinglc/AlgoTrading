# -*- coding: utf-8 -*-
u"""
Created on 2016-1-18

@author: cheng.li
"""

import datetime as dt
from AlgoTrading.api import Strategy
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import DataSource
from AlgoTrading.api import PortfolioType
from PyFin.api import *


class MovingAverageCrossStrategy(Strategy):
    def __init__(self, fast, slow, MACDLength, RSILength):
        MACDValue = MACD(fast, slow, 'close')
        AvgMACD = EMA(MACDLength, MACDValue)
        self.MACDDiff = MACDValue - AvgMACD
        self.RSI = RSI(RSILength, 'close')
        self.total_length = max(slow + MACDLength, RSILength)
        self.count = 0

        self.test_ret = MSUM(10, RETURNSimple('close'))

    def handle_data(self):

        for secID in self.tradableAssets:
            if self.MACDDiff[secID] > 2 \
                    and self.RSI[secID] > 51.:
                self.order_to(secID, 1, 2)
            elif self.MACDDiff[secID] < -2 \
                    and self.RSI[secID] < 49.:
                self.order_to(secID, 1, -2)
            else:
                self.order_to(secID, 0, 0)


def run_example():
    universe = ['000905.zicn']

    startDate = dt.datetime(2013, 1, 1)
    endDate = dt.datetime(2016, 8, 12)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   strategyParameters=(39, 78, 27, 42),
                   initialCapital=50000.,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DXDataCenter,
                   benchmark='000905.zicn',
                   freq=5,
                   logLevel='info',
                   portfolioType=PortfolioType.CashManageable,
                   plot=True,
                   saveFile=False)


if __name__ == "__main__":
    res = run_example()