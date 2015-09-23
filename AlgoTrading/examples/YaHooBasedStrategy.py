# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

import datetime as dt

from AlgoTrading.Strategy.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Backtest import DataSource
from PyFin.API import MA


class MovingAverageCrossStrategy(Strategy):

    def __init__(self):
        self.short_sma = MA(10, 'close')
        self.long_sma = MA(30, 'close')

    def calculateSignals(self):
        short_sma = self.short_sma.value
        long_sma = self.long_sma.value
        for s in self.symbolList:
            currDt = self.bars.getLatestBarDatetime(s)
            if short_sma[s] > long_sma[s] and self.secPos[s] == 0:
                print("{0}: BUY {1}".format(currDt, s))
                sigDir = 'LONG'
                self.order(s, sigDir, quantity=100)
            if short_sma[s] < long_sma[s] and self.secPos[s] != 0:
                print("{0}: SELL {1}".format(currDt, s))
                sigDir = 'EXIT'
                self.order(s, sigDir, quantity=100)


def run_example():
    symbolList = ['aapl', 'msft', 'ibm']
    initialCapital = 100000.0
    startDate = dt.datetime(2015, 1, 1)
    endDate = dt.datetime(2015, 9, 15)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   initialCapital=initialCapital,
                   symbolList=symbolList,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.YAHOO)

if __name__ == "__main__":
    run_example()
