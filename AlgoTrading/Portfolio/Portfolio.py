# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from AlgoTrading.Events import OrderEvent
from VisualPortfolio.Tears import createPerformanceTearSheet
from VisualPortfolio.Tears import createPostionTearSheet
from VisualPortfolio.Tears import createTranscationTearSheet


def extractTransactionFromFilledBook(filledBook):
    interestedColumns = filledBook[['time', 'symbol', 'quantity', 'fillCost']]
    interestedColumns.set_index('time', inplace=True)
    interestedColumns = interestedColumns.rename(columns={'quantity': 'turnover_volume', 'fillCost': 'turnover_value'})
    return interestedColumns


class Portfolio(object):

    def __init__(self, dataHandler, events, startDate, assets, initialCapital=100000.0, benchmark=None):
        self.dataHandler = dataHandler
        self.events = events
        self.symbolList = self.dataHandler.symbolList
        self.startDate = startDate
        self.initialCapital = initialCapital
        self.benchmark = benchmark
        self.assets = assets

        self.allPositions = self.constructAllPositions()
        self.currentPosition = dict((s, 0) for s in self.symbolList)

        self.allHoldings = []
        self.currentHoldings = self.constructCurrentHoldings()

    def constructAllPositions(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        d['datetime'] = self.startDate
        return [d]

    def constructAllHoldings(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        d['datetime'] = self.startDate
        d['cash'] = self.initialCapital
        d['margin'] = 0.0
        d['commission'] = 0.0
        d['total'] = self.initialCapital
        return [d]

    def constructCurrentHoldings(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        d['datetime'] = self.startDate
        d['cash'] = self.initialCapital
        d['margin'] = 0.0
        d['commission'] = 0.0
        d['total'] = self.initialCapital
        return d

    def updateTimeindex(self):
        latestDatetime = self.dataHandler.currentTimeIndex

        dh = dict((s, 0) for s in self.symbolList)
        dh['datetime'] = latestDatetime
        dh['cash'] = self.currentHoldings['cash']
        dh['commission'] = self.currentHoldings['commission']
        dh['total'] = self.currentHoldings['cash']

        for s in self.symbolList:
            marketValue = 0.0
            if self.currentPosition[s] != 0:
                marketValue = self.currentPosition[s] \
                              * self.dataHandler.getLatestBarValue(s, 'close') \
                              * self.assets[s].multiplier * self.assets[s].settle
            dh[s] = marketValue
            dh['total'] += marketValue

        self.allHoldings.append(dh)

    def updatePositionFromFill(self, fill):
        fillDir = fill.direction
        self.currentPosition[fill.symbol] += fillDir * fill.quantity

    def updateHoldingsFromFill(self, fill):
        self.currentHoldings[fill.symbol] += fill.fillCost
        self.currentHoldings['commission'] += fill.commission
        self.currentHoldings['cash'] -= (fill.fillCost + fill.commission)
        self.currentHoldings['total'] -= (fill.fillCost + fill.commission)

    def updateFill(self, event):
        if event.type == 'FILL':
            self.updatePositionFromFill(event)
            self.updateHoldingsFromFill(event)

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

    def createEquityCurveDataframe(self):
        curve = pd.DataFrame(self.allHoldings)
        curve.set_index('datetime', inplace=True)
        curve['return'] = np.log(curve['total'] / curve['total'].shift(1))
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

        positons = curve.drop(['commission', 'total', 'return', 'equity_curve'], axis=1)
        aggregated_positons = createPostionTearSheet(positons, plot=plot)

        transactions = extractTransactionFromFilledBook(self.filledBook.view())
        turnover_rate = createTranscationTearSheet(transactions, positons, plot=plot)

        if plot:
            plt.show()

        return perf_metric, perf_df, rollingRisk, aggregated_positons, transactions, turnover_rate
