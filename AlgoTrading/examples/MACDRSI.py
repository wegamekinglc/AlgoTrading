# -*- coding: utf-8 -*-
u"""
Created on 2016-1-18

@author: cheng.li
"""

import datetime as dt
from AlgoTrading.api import Strategy
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import DataSource
from AlgoTrading.api import set_universe
from AlgoTrading.api import PortfolioType
from PyFin.api import MA
from PyFin.api import MACD
from PyFin.api import RSI
from PyFin.api import EMA


class MovingAverageCrossStrategy(Strategy):
    def __init__(self, fast, slow, MACDLength, RSILength):
        MACDValue = MACD(fast, slow, 'close')
        AvgMACD = EMA(MACDLength, MACDValue)
        self.MACDDiff = MACDValue - AvgMACD
        self.RSI = RSI(RSILength, 'close')
        self.total_length = max(slow + MACDLength, RSILength)
        self.count = 0

    def handle_data(self):

        for secID in self.tradableAssets:
            #if not self.MACDDiff.isFull[secID] or not self.RSI.isFull[secID]:
            #    continue
            if self.MACDDiff[secID] > 2 \
                    and self.RSI[secID] > 51.:
                self.order_to(secID, 1, 1)
            elif self.MACDDiff[secID] < -2 \
                    and self.RSI[secID] < 49.:
                self.order_to(secID, 1, -1)


def run_example():
    universe = ['000905.zicn'] #set_universe('000300.zicn', refDate='2012-06-01')

    startDate = dt.datetime(2013, 1, 1)
    endDate = dt.datetime(2016, 1, 12)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   strategyParameters=(39, 78, 27, 42),
                   #initialCapital=50000.,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DataYes,
                   benchmark='000300.zicn',
                   freq=5,
                   logLevel='info',
                   #portfolioType=PortfolioType.CashManageable,
                   plot=True,
                   saveFile=False)


if __name__ == "__main__":
    res = run_example()