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
        self.long_sma = MA(30, 'close')

    def handle_data(self):
        for s in self.universe:
            if self.short_sma[s] > self.long_sma[s]:
                self.order(s, 1, quantity=100)
            elif self.short_sma[s] < self.long_sma[s] and self.secPos[s] != 0:
                self.order(s, -1, quantity=100)


def run_example():
    csvDir = "data"
    universe = ['aapl', 'msft', 'ibm']
    initialCapital = 1000000.0

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   dataSource=DataSource.CSV,
                   csvDir=csvDir,
                   saveFile=True,
                   plot=False)


if __name__ == "__main__":
    run_example()
