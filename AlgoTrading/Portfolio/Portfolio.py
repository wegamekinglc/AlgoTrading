# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""

from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyFin.Utilities import isClose
from AlgoTrading.Events import OrderEvent
from AlgoTrading.Enums import PortfolioType
from AlgoTrading.Portfolio.PositionsBook import StocksPositionsBook
from AlgoTrading.Env import Settings
from AlgoTrading.Utilities import sign
from VisualPortfolio.Tears import createPerformanceTearSheet
from VisualPortfolio.Tears import createPostionTearSheet
from VisualPortfolio.Tears import createTranscationTearSheet
from VisualPortfolio.Env import Settings as vp_settings


def extractTransactionFromFilledBook(filledBook):
    interestedColumns = filledBook[['time', 'symbol', 'quantity', 'nominal']]
    interestedColumns.set_index('time', inplace=True)
    interestedColumns = interestedColumns.rename(columns={'quantity': 'turnover_volume', 'nominal': 'turnover_value'})
    return interestedColumns


class Portfolio(object):

    def __init__(self, dataHandler,
                 events,
                 startDate,
                 assets,
                 initialCapital=100000.0,
                 benchmark=None,
                 portfolioType=PortfolioType.CashManageable):
        self.dataHandler = dataHandler
        self.events = events
        self.tradableAssets = self.dataHandler.tradableAssets
        self.startDate = startDate
        self.initialCapital = initialCapital
        self.benchmark = benchmark
        self.assets = assets
        self.positionsBook = StocksPositionsBook(assets)
        self.portfolioType = portfolioType

        self.allPositions = self.constructAllPositions()
        self.currentPosition = defaultdict(int, [(s, 0) for s in self.tradableAssets])

        self.allHoldings = self.constructAllHoldings()
        self.currentHoldings = self.constructCurrentHoldings()

        vp_settings.set_source(Settings.data_source)

    def constructAllPositions(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.tradableAssets])
        d['datetime'] = self.startDate
        return [d]

    def constructAllHoldings(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.tradableAssets])
        d['datetime'] = self.startDate
        d['cash'] = self.initialCapital
        d['margin'] = 0.0
        d['commission'] = 0.0
        d['pnl'] = 0.
        d['total'] = self.initialCapital
        return [d]

    def constructCurrentHoldings(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.tradableAssets])
        d['datetime'] = self.startDate
        d['cash'] = self.initialCapital
        d['margin'] = 0.0
        d['commission'] = 0.0
        d['pnl'] = 0.
        d['total'] = self.initialCapital
        return d

    def updateTimeindex(self):
        latestDatetime = self.dataHandler.currentTimeIndex

        dh = dict((s, 0) for s in self.tradableAssets)
        dh['datetime'] = latestDatetime
        dh['cash'] = self.currentHoldings['cash']
        dh['commission'] = self.currentHoldings['commission']
        dh['margin'] = self.currentHoldings['margin']
        dh['total'] = self.currentHoldings['total']
        dh['pnl'] = self.currentHoldings['pnl']

        for s in self.tradableAssets:
            bookValue = 0.
            bookPnL = 0.
            if self.currentPosition[s]:
                currentCost = self.dataHandler.getLatestBarValue(s, 'close') * self.assets[s].multiplier
                bookValue, bookPnL = self.positionsBook.getBookValueAndBookPnL(s, currentCost)
            dh[s] = bookValue
            dh['pnl'] += bookPnL
            dh['total'] += bookPnL

        self.allHoldings.append(dh)

    def updatePositionFromFill(self, fill):
        fillDir = fill.direction
        self.currentPosition[fill.symbol] += fillDir * fill.quantity

    def updateHoldingsFromFill(self, fill, pnl):
        self.currentHoldings[fill.symbol] += fill.fillCost
        self.currentHoldings['commission'] += fill.commission
        if not isClose(fill.fillCost, 0.):
            self.currentHoldings['cash'] -= (fill.fillCost + fill.commission)
        else:
            self.currentHoldings['cash'] += (pnl - fill.commission)
        self.currentHoldings['pnl'] += pnl - fill.commission
        self.currentHoldings['total'] += pnl - fill.commission

    def updateFill(self, event):
        posClosed, posOpen, pnl = self.positionsBook.updatePositionsByFill(event)
        self.updatePositionFromFill(event)
        self.updateHoldingsFromFill(event, pnl)

        self.filledBook.updateFromFillEvent(event)

    def generateNaiveOrder(self, signal):
        order = None

        symbol = signal.symbol
        direction = signal.signalType

        mktQuantity = signal.quantity
        curQuantity = self.currentPosition[symbol]
        orderType = 'MKT'

        if direction == 'LONG' and curQuantity == 0:
            order = OrderEvent(symbol, orderType, mktQuantity, 1)
        if direction == 'SHORT' and curQuantity == 0:
            order = OrderEvent(symbol, orderType, mktQuantity, -1)

        if direction == 'EXIT' and curQuantity > 0:
            order = OrderEvent(symbol, orderType, abs(curQuantity), -1)
        if direction == 'EXIT' and curQuantity < 0:
            order = OrderEvent(symbol, orderType, abs(curQuantity), 1)

        return order

    def updateSignal(self, event):
        if event.type == 'SIGNAL':
            orderEvent = self.generateNaiveOrder(event)
            self.events.put(orderEvent)

    def _createFullNotionalEquityCurve(self, curve):
        rawpos = curve.drop(['cash', 'commission', 'total', 'margin', 'pnl'], axis=1)
        notionals = rawpos.abs().sum(axis=1).fillna(0)
        notional_directions = rawpos.sum(axis=1).fillna(0).apply(sign)
        pnldiffs = curve['pnl'].diff()
        # to handl the case when pnl is shown in null notional day
        cumPnL = 0.
        returns = []
        for notional, pnldiff, direction in zip(notionals, pnldiffs, notional_directions):
            if not isClose(notional):
                r = direction * np.log(direction * notional / (direction * notional - pnldiff - cumPnL))
                returns.append(r)
                cumPnL = 0.
            elif not np.isnan(pnldiff):
                returns.append(0.)
                cumPnL += pnldiff
            else:
                returns.append(0.)
        curve['return'] = returns
        curve.fillna(0., inplace=True)
        curve['equity_curve'] = np.exp(curve['return'].cumsum())

    def createEquityCurveDataframe(self):
        curve = pd.DataFrame(self.allHoldings)
        curve.set_index('datetime', inplace=True)
        if self.portfolioType == PortfolioType.FullNotional:
            self._createFullNotionalEquityCurve(curve)
        else:
            curve['return'] = np.log(curve['total'] / curve['total'].shift(1))
            curve.dropna(inplace=True)
            curve['equity_curve'] = np.exp(curve['return'].cumsum())
        self.equityCurve = curve.dropna()

    def outputSummaryStats(self, curve, plot):
        returns = curve['return']
        if hasattr(self.dataHandler, "benchmarkData"):
            benchmarkReturns = self.dataHandler.benchmarkData['return']
            benchmarkReturns.name = self.benchmark
        else:
            benchmarkReturns = None
        perf_metric, perf_df, rollingRisk = createPerformanceTearSheet(returns=returns, benchmarkReturns=benchmarkReturns, plot=plot)

        if self.portfolioType == PortfolioType.FullNotional:
            positons = curve.drop(['cash', 'commission', 'total', 'return', 'margin', 'equity_curve', 'pnl'], axis=1)
        else:
            positons = curve.drop(['commission', 'total', 'return', 'margin', 'equity_curve', 'pnl'], axis=1)
        aggregated_positons = createPostionTearSheet(positons, plot=plot)

        transactions = extractTransactionFromFilledBook(self.filledBook.view())
        turnover_rate = createTranscationTearSheet(transactions, positons, plot=plot)

        if plot:
            plt.show()

        return perf_metric, perf_df, rollingRisk, aggregated_positons, transactions, turnover_rate
