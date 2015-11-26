# -*- coding: utf-8 -*-
u"""
Created on 2015-11-25

@author: cheng.li
"""

import datetime as dt
import pandas as pd

from AlgoTrading.Strategy.Strategy import Strategy
from AlgoTrading.Backtest import strategyRunner
from AlgoTrading.Enums import DataSource
from AlgoTrading.Enums import PortfolioType
from PyFin.api import CLOSE
from PyFin.api import OPEN
from PyFin.api import LOW
from PyFin.api import HIGH
from PyFin.api import nthWeekDay
from PyFin.api import advanceDateByCalendar


def sign(x):
    if x > 0:
        return 1
    else:
        return -1


class MovingAverageCrossStrategy(Strategy):
    def __init__(self):

        self.closes = CLOSE()
        self.preCloses = CLOSE().shift(1)
        self.openes = OPEN()
        self.lowes = LOW()
        self.highes = HIGH()

        # 计算指数的备用指标
        self.closeDLastClose = self.closes / self.preCloses - 1.
        self.closeDOpen = self.closes / self.openes - 1.
        self.closeDLow = self.closes / self.lowes - 1.
        self.highDClose = 1. - self.highes / self.closes

        # 定义指数的权重
        self.indexWeights = pd.Series([1., -2., 1.], index=['000016.zicn', '000300.zicn', '000905.zicn'])

    def handle_data(self):

        # 计算指数指标得分
        closeDLastCloseScore = self.closeDLastClose['000016.zicn', '000300.zicn', '000905.zicn'].dot(self.indexWeights)
        closeDOpenScore = self.closeDOpen['000016.zicn', '000300.zicn', '000905.zicn'].dot(self.indexWeights)
        closeDLowScore = self.closeDLow['000016.zicn', '000300.zicn', '000905.zicn'].dot(self.indexWeights)
        highDCloseScore = self.highDClose['000016.zicn', '000300.zicn', '000905.zicn'].dot(self.indexWeights)

        # 找到需要使用的主力合约
        current_time = self.current_datetime

        year = current_time.year
        month = current_time.month

        delDay = nthWeekDay(3, 6, month, year)
        changeContractDay = advanceDateByCalendar('China.SSE', delDay, '-1b')

        contract_month = month
        if current_time.date() >= changeContractDay:
            contract_month = month + 1

        ihc, ifc, icc = 'ih15%02d' % contract_month, 'if15%02d' % contract_month, 'ic15%02d' % contract_month
        ihcOld, ifcOld, iccOld = 'ih15%02d' % month, 'if15%02d' % month, 'ic15%02d' % month

        if month < contract_month and self.secPos[ihcOld] != 0:
            # 需要移仓， 平掉旧合约
            self.order_to(ihcOld, 1, 0)
            self.order_to(ifcOld, 1, 0)
            self.order_to(iccOld, 1, 0)

        # 定义基差
        ihBasis = self.closes[ihc] / self.closes['000016.zicn'] - 1.
        ihPreBasis = self.preCloses[ihc] / self.preCloses['000016.zicn'] - 1.

        ifBasis = self.closes[ifc] / self.closes['000300.zicn'] - 1.
        ifPreBasis = self.preCloses[ifc] / self.preCloses['000300.zicn'] - 1.

        icBasis = self.closes[icc] / self.closes['000905.zicn'] - 1.
        icPreBasis = self.preCloses[icc] / self.preCloses['000905.zicn'] - 1.

        # 计算基差得分
        ihBasisDiff = ihPreBasis - ihBasis
        ifBasisDiff = ifPreBasis - ifBasis
        icBasisDiff = icPreBasis - icBasis

        basis = ihBasis - 2. * ifBasis + icBasis
        basisScore = ihBasisDiff - 2. * ifBasisDiff + icBasisDiff

        # 5个信号合并产生开平仓信号
        elects = 0
        for signal in [closeDLastCloseScore, closeDOpenScore, closeDLowScore, highDCloseScore, basisScore]:
            if basis < 0. < signal:
                elects += 1
            elif signal < 0. < basis:
                elects -= 1

        # 开平仓逻辑

        if elects > 0:
            # 多头信号
            self.order_to(ihc, 1, 1)
            self.order_to(ifc, -1, 2)
            self.order_to(icc, 1, 1)
        elif elects < 0:
            # 空头信号
            self.order_to(ihc, -1, 1)
            self.order_to(ifc, 1, 2)
            self.order_to(icc, -1, 1)
        else:
            # 平仓信号
            self.order_to(ihc, 1, 0)
            self.order_to(ifc, 1, 0)
            self.order_to(icc, 1, 0)

        # 记录必要的信息，供回测后查看

        # 指数价格信息
        self.keep("000016.zicn_open", self.openes['000016.zicn'])
        self.keep("000016.zicn_high", self.highes['000016.zicn'])
        self.keep("000016.zicn_low", self.lowes['000016.zicn'])
        self.keep("000016.zicn_close", self.closes['000016.zicn'])

        self.keep("000300.zicn_open", self.openes['000300.zicn'])
        self.keep("000300.zicn_high", self.highes['000300.zicn'])
        self.keep("000300.zicn_low", self.lowes['000300.zicn'])
        self.keep("000300.zicn_close", self.closes['000300.zicn'])

        self.keep("000905.zicn_open", self.openes['000905.zicn'])
        self.keep("000905.zicn_high", self.highes['000905.zicn'])
        self.keep("000905.zicn_low", self.lowes['000905.zicn'])
        self.keep("000905.zicn_close", self.closes['000905.zicn'])

        # 期货价格信息
        self.keep("IH_ID", ihc)
        self.keep("IH_CLOSER", self.closes[ihc])
        self.keep("IF_ID", ifc)
        self.keep("IF_CLOSER", self.closes[ifc])
        self.keep("IC_ID", icc)
        self.keep("IC_CLOSER", self.closes[icc])

        # 因子信息
        self.keep("C/LC-1", closeDLastCloseScore)
        self.keep("C/O-1", closeDOpenScore)
        self.keep("C/L-1", closeDLowScore)
        self.keep("1-H/C", highDCloseScore)

        # 基差信息
        self.keep("BASIS_DIFF", basisScore)
        self.keep("BASIS", basis)

        # 开平仓方向信号
        self.keep("POSITION_SIGNAL", elects)
        self.keep("Released_PnL", self.realizedHoldings['pnl'])
        self.keep("PnL", self.holdings['pnl'])


def run_example():
    indexes = ['000016.zicn', '000300.zicn', '000905.zicn']

    # futures to trade
    ihs = ['ih15%02d' % i for i in range(4, 13)]
    ifs = ['if15%02d' % i for i in range(4, 13)]
    ics = ['ic15%02d' % i for i in range(4, 13)]

    futures = ihs + ifs + ics

    universe = indexes + futures
    initialCapital = 75000.0
    startDate = dt.datetime(2015, 4, 22)
    endDate = dt.datetime(2015, 11, 19)

    strategyRunner(userStrategy=MovingAverageCrossStrategy,
                   initialCapital=initialCapital,
                   symbolList=universe,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DataYes,
                   saveFile=True,
                   plot=True,
                   benchmark='000300.zicn',
                   portfolioType=PortfolioType.FullNotional)


if __name__ == "__main__":
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))
