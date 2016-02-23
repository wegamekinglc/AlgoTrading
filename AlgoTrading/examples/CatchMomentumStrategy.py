# -*- coding: utf-8 -*-
u"""
Created on 2016-2-19

@author: cheng.li
"""

import datetime as dt
from PyFin.api import HIST
from AlgoTrading.api import Strategy
from AlgoTrading.api import DataSource
from AlgoTrading.api import PortfolioType
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import Settings
from AlgoTrading.api import set_universe


class CatchMomentumStrategy(Strategy):

    def __init__(self):
        self.hist = HIST(1, 'close')
        self.today_close_list = {}
        self.pre_last_price = {}
        self.today_bought_list = []

    def handle_data(self):
        if self.current_time == '09:30:00':
            self.today_bought_list = []
            for s in self.secPos:
                self.order_to(s, 1, 0)
            for s in self.universe:
                self.today_close_list[s] = []
                self.today_close_list[s].append(self.hist[s][0])
        elif self.current_time == '14:55:00':
            for s in self.universe:
                self.pre_last_price[s] = self.hist[s][0]
        elif '10:30:00' < self.current_time < '14:55:00':
            buy_list = []
            for s in self.universe:
                self.today_close_list[s].append(self.hist[s][0])
            for s in self.tradableAssets:
                if s in self.pre_last_price:
                    first_price = self.today_close_list[s][0]
                    last_price = self.today_close_list[s][-1]
                    high_price = max(self.today_close_list[s])

                    pre_last = self.pre_last_price[s]
                    if last_price > high_price * 0.98\
                            and first_price > pre_last \
                            and last_price > 1.07 * pre_last \
                            and s not in self.today_bought_list:
                        buy_list.append(s)
                        self.today_bought_list.append(s)

            if len(buy_list) > 0:
                unit = 1.0 / len(self.today_bought_list)
                for s in buy_list:
                    self.order_to_pct(s, 1, unit)
        else:
            for s in self.universe:
                self.today_close_list[s].append(self.hist[s][0])


def run_example():
    universe = ['000999.xshe']#set_universe('000300.zicn')[:100]
    startDate = dt.datetime(2015, 1, 1)
    endDate = dt.datetime(2016, 2, 22)
    initialCapital = 10000000.

    return strategyRunner(userStrategy=CatchMomentumStrategy,
                          initialCapital=initialCapital,
                          symbolList=universe,
                          startDate=startDate,
                          endDate=endDate,
                          dataSource=DataSource.DXDataCenter,
                          portfolioType=PortfolioType.CashManageable,
                          freq=5,
                          benchmark='000300.zicn',
                          logLevel="critical",
                          saveFile=False,
                          plot=False)


if __name__ == "__main__":
    Settings.enableCache()
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))