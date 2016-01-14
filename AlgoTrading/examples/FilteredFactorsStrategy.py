# -*- coding: utf-8 -*-
u"""
Created on 2015-9-22

@author: cheng.li
"""

import datetime as dt

from AlgoTrading.api import Strategy
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import set_universe
from AlgoTrading.api import DataSource
from PyFin.api import MA
from PyFin.api import nthWeekDay
from PyFin.api import advanceDateByCalendar


class MovingAverageCrossStrategy(Strategy):

    def __init__(self):

        short_sma = MA(10, 'close')
        long_sma = MA(60, 'close')
        self.signal = short_sma - long_sma

    def handle_data(self):

        for s in self.tradableAssets:
            if s[:2] != 'if':
                if self.signal[s] > 0 and self.secPos[s] == 0:
                    self.order(s, 1, 200)
                elif self.signal[s] < 0 and self.secPos[s] != 0:
                    self.order(s, -1, 200)

        # 找到需要使用的主力合约
        current_time = self.current_datetime

        year = current_time.year
        month = current_time.month

        delDay = nthWeekDay(3, 6, month, year)
        changeContractDay = advanceDateByCalendar('China.SSE', delDay, '-1b')

        contract_month = month
        if current_time.date() >= changeContractDay:
            contract_month = month + 1

        ifc = 'if15%02d.cffex' % contract_month
        ifcOld = 'if15%02d.cffex' % month

        if month < contract_month and self.secPos[ifcOld] != 0:
            # 需要移仓， 平掉旧合约
            self.order_to(ifcOld, 1, 0)

        self.order_to(ifc, -1, 1)


def run_example():
    stocks = set_universe('000300.zicn')
    futures = ['if15%02d.cffex' % i for i in range(1, 13)]

    universes = stocks + futures

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   symbolList=universes,
                   startDate=dt.datetime(2015, 1, 1),
                   endDate=dt.datetime(2015, 12, 5),
                   logLevel='info',
                   saveFile=False,
                   plot=False,
                   dataSource=DataSource.DataYes,
                   benchmark='000300.zicn',)


if __name__ == "__main__":
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))

