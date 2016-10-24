# -*- coding: utf-8 -*-
u"""
Created on 2016-9-20

@author: cheng.li
"""

import datetime as dt
import pandas as pd
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import Strategy
from AlgoTrading.api import DataSource
from AlgoTrading.api import PortfolioType
from AlgoTrading.Events import OrderDirection
from PyFin.api import MA
from PyFin.api import VARIANCE
from PyFin.api import SQRT
from PyFin.api import CLOSE
from PyFin.api import RETURNSimple


secIDs = ['ta.xzce', 'y.xdce', 'ru.xsge', 'a.xdce', 'ic.ccfx', 'if.ccfx', 'ih.ccfx']


class GridTradingStrategy(Strategy):

    def __init__(self):
        self.window = 20
        self.ma = MA(self.window, 'close')
        self.var = SQRT(VARIANCE(20, RETURNSimple('close')))
        self.close = CLOSE()
        self.pack = {'ta.xzce': 1,
                     'y.xdce': 1,
                     'ru.xsge': 1,
                     'a.xdce': 1,
                     'ic.ccfx': 1,
                     'if.ccfx': 1,
                     'ih.ccfx': 1}
        self.upper_direction = -1
        self.lower_direction = 1
        self.step = 0.005
        self.profit_threshold = 0.005

        self.position_book = {}
        self.order_queue = {}

    def handle_data(self):

        for secID in secIDs:

            if secID not in self.position_book:
                self.position_book[secID] = pd.DataFrame(columns=['date', 'cost', 'direction', 'positions'])
                self.order_queue[secID] = []

            if not self.ma.isFull[secID]:
                continue

            positions = self.position_book[secID]
            close = self.close[secID]
            current_date = self.current_datetime.date()

            if positions.empty:
                if close > (1 + self.step) * self.ma[secID]:
                    self.order(secID, self.upper_direction, self.pack[secID])
                elif close < (1 - self.step) * self.ma[secID]:
                    self.order(secID, self.lower_direction, self.pack[secID])
            else:
                long_positions = positions[positions.direction == 1].sort_values('cost')
                short_positions = positions[positions.direction == -1].sort_values('cost')
                assert (long_positions.empty or short_positions.empty)

                if not long_positions.empty:
                    for i, row in long_positions.iterrows():
                        if close > (1. + self.profit_threshold) * row['cost']:
                            self.order(secID, -self.lower_direction, self.pack[secID])
                            self.log_order(secID, -self.lower_direction, self.pack[secID], row['cost'], row['date'])

                    if current_date not in set(long_positions.date) and close < (1. - self.step) * long_positions['cost'].iloc[0]:
                        self.order(secID, self.lower_direction, self.pack[secID])

                else:
                    for i, row in short_positions.iterrows():
                        if close < (1. - self.profit_threshold) * row['cost']:
                            self.order(secID, -self.upper_direction, self.pack[secID])
                            self.log_order(secID, -self.upper_direction, self.pack[secID], row['cost'], row['date'])

                    if current_date not in set(short_positions.date) and close > (1. + self.step) * short_positions['cost'].iloc[-1]:
                        self.order(secID, self.upper_direction, self.pack[secID])

    def log_order(self, secID, direction, quantity, cost, date):
        self.order_queue[secID].append([self.current_datetime, secID, direction, quantity, 0, cost, date])

    def handle_order(self, event):
        secID = event.symbol
        if event.direction == OrderDirection.SELL or event.direction == OrderDirection.BUY_BACK:
            for order in self.order_queue[secID]:
                if order[3] != order[4]:
                    order[4] += event.quantity
                    break

    def handle_fill(self, event):
        secID = event.symbol
        time_stamp = event.timeindex

        if event.direction == OrderDirection.BUY or event.direction == OrderDirection.BUY_BACK:
            direction = 1
        else:
            direction = -1

        cost = event.nominal / event.quantity / direction
        if event.direction == OrderDirection.BUY or event.direction == OrderDirection.SELL_SHORT:
            self.position_book[secID].loc[time_stamp] = [time_stamp.date(), cost, direction, event.quantity]
        else:
            tmp = self.position_book[secID]
            new_order = None
            for i, order in enumerate(self.order_queue[secID]):
                if order[2] == direction and order[4] != 0:
                    new_order = order
                    del self.order_queue[secID][i]
                    break
            self.position_book[secID] = tmp[tmp.cost.index.date != new_order[6]]


def run_example():
    universe = secIDs
    startDate = dt.datetime(2015, 12, 1)
    endDate = dt.datetime(2016, 9, 22)
    initialCapital = 200000.

    strategyRunner(userStrategy=GridTradingStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DXDataCenter,
                   portfolioType=PortfolioType.CashManageable,
                   freq=0,
                   benchmark=secIDs[0],
                   logLevel="info",
                   saveFile=False,
                   plot=False)


if __name__ == "__main__":
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))