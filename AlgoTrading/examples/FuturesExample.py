# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

import datetime as dt

from AlgoTrading.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Backtest import DataSource
from AlgoTrading.Data import set_universe
from PyFin.api import MA
from PyFin.api import HIST

futures = ['if1412',
           'if1501',
           'if1502',
           'if1503',
           'if1504',
           'if1505',
           'if1506',
           'if1507',
           'if1508',
           'if1509',
           'if1510',
           'if1511']


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):
        indicator = MA(10, 'close') - MA(120, 'close')
        self.signal = indicator
        self.volume = HIST(10, 'volume')
        self.first_time = True

    def handle_data(self):
        global futures
        for s in self.universe:
            amount = self.avaliableForSale(s)
            if self.signal[s] > 0. and self.secPos[s] == 0:
                if s not in futures:
                    self.order(s, 1, quantity=15000)
            if self.signal[s] < 0. and amount != 0:
                if s not in futures:
                    self.order(s, -1, quantity=15000)

        if self.first_time and 'if1412' in self.universe:
            self.order('if1412', -1, quantity=20000)
            self.first_time = False

        current_year = self.current_datetime.year - 2000
        current_month = self.current_datetime.month

        oldContract = 'if%d%02d' % (current_year, current_month)
        if current_month != 12:
            newContract = 'if%d%02d' % (current_year, current_month + 1)
        else:
            newContract = 'if%d%02d' % (current_year + 1, 1)

        oldV = self.volume[oldContract]
        newV = self.volume[newContract]

        if sum(oldV) < sum(newV) and len(newV) == 10:
            if self.secPos[oldContract] != 0 and oldContract in self.universe:
                self.order(oldContract, 1, quantity=-self.secPos[oldContract])
            if self.secPos[newContract] == 0 and newContract in self.universe:
                self.order(newContract, -1, quantity=20000)


def run_example():
    universe = set_universe('000300.zicn')[:1] + futures
    initialCapital = 1e8
    startDate = dt.datetime(2014, 12, 1)
    endDate = dt.datetime(2015, 11, 1)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DXDataCenter,
                   freq=5,
                   benchmark='000300.zicn',
                   logLevel="critical",
                   saveFile=True,
                   plot=True)


startTime = dt.datetime.now()
print("Start: %s" % startTime)
run_example()
endTime = dt.datetime.now()
print("End : %s" % endTime)
print("Elapsed: %s" % (endTime - startTime))