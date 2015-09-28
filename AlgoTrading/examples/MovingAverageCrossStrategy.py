# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

from AlgoTrading.Strategy.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Backtest import DataSource
from PyFin.API import MA


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):
        self.short_sma = MA(10, 'close')
        self.long_sma = MA(120, 'close')
        pass

    def handle_data(self):
        short_sma = self.short_sma.value
        long_sma = self.long_sma.value
        for s in self.universe:
            if short_sma[s] > long_sma[s] and self.secPos[s] == 0:
                self.order(s, 1, quantity=1000)
            elif short_sma[s] < long_sma[s] and self.secPos[s] != 0:
                self.order(s, -1, quantity=1000)


def run_example():
    csvDir = "data"
    universe = ['aapl', 'msft', 'ibm']
    initialCapital = 100000.0

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   dataSource=DataSource.CSV,
                   csvDir=csvDir)


if __name__ == "__main__":
    run_example()
