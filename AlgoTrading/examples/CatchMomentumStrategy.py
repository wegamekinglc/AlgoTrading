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
                if s in self.tradableAssets:
                    self.order_to(s, 1, 0)
            for s in self.universe:
                self.today_close_list[s] = []
                self.today_close_list[s].append(self.hist[s][0])
        elif self.current_time == '14:55:00':
            for s in self.universe:
                if s in self.pre_last_price:
                    self.pre_last_price[s].append(self.hist[s][0])
                else:
                    self.pre_last_price[s] = [self.hist[s][0]]
        elif '10:30:00' < self.current_time < '14:55:00':
            buy_list = []
            for s in self.universe:
                self.today_close_list[s].append(self.hist[s][0])
            if '000905.zicn' in self.pre_last_price:
                pre_last_10day_index_high = max(self.pre_last_price['000905.zicn'][-10:])
                last_index = self.today_close_list['000905.zicn'][-1]
            for s in self.tradableAssets:
                if s in self.pre_last_price:
                    first_price = self.today_close_list[s][0]
                    last_price = self.today_close_list[s][-1]
                    high_price = max(self.today_close_list[s])
                    pre_last = self.pre_last_price[s][-1]
                    if last_price > high_price * 0.98\
                            and first_price > pre_last \
                            and last_price > 1.07 * pre_last \
                            and last_index > pre_last_10day_index_high \
                            and s not in self.today_bought_list \
                            and self.secPos[s] == 0:
                        buy_list.append(s)
                        self.today_bought_list.append(s)

            if len(buy_list) > 0:
                unit = 0.50 / len(self.today_bought_list)
                for s in buy_list:
                    self.order_to_pct(s, 1, unit)
        else:
            for s in self.universe:
                self.today_close_list[s].append(self.hist[s][0])


def run_example():
    universe = set_universe('000905.zicn') + ['000905.zicn']
    startDate = dt.datetime(2014, 1, 1)
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
                          benchmark='000905.zicn',
                          logLevel="warning",
                          saveFile=True,
                          plot=True)


if __name__ == "__main__":
    Settings.enableCache()
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))