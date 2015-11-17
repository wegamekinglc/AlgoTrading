# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

import datetime as dt
from AlgoTrading.Strategy.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Backtest import DataSource
from PyFin.API import MA
from PyFin.API import MAX
from PyFin.API import MIN


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):
        short_sma = MA(10, 'close')
        long_sma = MA(30, 'close')
        filter = (MAX(10, 'close') / MIN(10, 'close')) > 1.02
        self.signal = (short_sma - long_sma)[filter]

    def handle_data(self):
        for s in self.universe:
            if self.signal[s] > 0:
                self.order(s, 1, quantity=100)
            elif self.signal[s] < 0 and self.secPos[s] != 0:
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
                   saveFile=False,
                   plot=True)


if __name__ == "__main__":

    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))
