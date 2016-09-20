# -*- coding: utf-8 -*-
u"""
Created on 2016-9-20

@author: cheng.li
"""

import datetime as dt
import unittest
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import Strategy
from AlgoTrading.api import DataSource
from PyFin.api import CLOSE


class SimpleStrategy(Strategy):

    def __init__(self):
        self.count = 0
        self.close = CLOSE()

    def handle_data(self):
        if self.count <= 2:
            self.keep('close', -self.close['000905.zicn'])
            self.order('000905.zicn', 1, 1)
        elif 3 <= self.count <= 5:
            self.keep('close', self.close['000905.zicn'])
            self.order('000905.zicn', -1, 1)
        self.count += 1


def run_example(freq):
    universe = ['000905.zicn']
    startDate = dt.datetime(2016, 1, 8)
    endDate = dt.datetime(2016, 1, 31)

    return strategyRunner(userStrategy=SimpleStrategy,
                          symbolList=universe,
                          startDate=startDate,
                          endDate=endDate,
                          dataSource=DataSource.DXDataCenter,
                          freq=freq,
                          logLevel="warning",
                          saveFile=False,
                          plot=False)


class TestSimpleStrategy(unittest.TestCase):

    def testPortfolioSettlementsEOD(self):
        res = run_example(0)
        expected_total_pnl = res['user_info'].close.sum()
        calculated_total_pnl = res['equity_curve'].pnl[-1]
        self.assertAlmostEqual(expected_total_pnl, calculated_total_pnl)

    def testPortfolioSettlementsMin5(self):
        res = run_example(5)
        expected_total_pnl = res['user_info'].close.sum()
        calculated_total_pnl = res['equity_curve'].pnl[-1]
        self.assertAlmostEqual(expected_total_pnl, calculated_total_pnl)