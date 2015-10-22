# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from AlgoTrading.Events import OrderEvent
from AlgoTrading.Finance import aggregateReturns
from AlgoTrading.Finance import drawDown
from AlgoTrading.Finance import annualReturn
from AlgoTrading.Finance import annualVolatility
from AlgoTrading.Finance import sortinoRatio
from AlgoTrading.Finance import sharpRatio
from AlgoTrading.Portfolio.Plottings import plottingRollingReturn
from AlgoTrading.Portfolio.Plottings import plottingDrawdownPeriods
from AlgoTrading.Portfolio.Plottings import plottingUnderwater
from AlgoTrading.Portfolio.Plottings import plotting_context
from AlgoTrading.Portfolio.Plottings import plottingMonthlyReturnsHeapmap
from AlgoTrading.Portfolio.Plottings import plottingAnnualReturns
from AlgoTrading.Portfolio.Plottings import plottingMonthlyRetDist


class Portfolio(object):

    def __init__(self, bars, events, startDate, initialCapital=100000.0):
        self.bars = bars
        self.events = events
        self.symbolList = self.bars.symbolList
        self.startDate = startDate
        self.initialCapital = initialCapital

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
        d['commission'] = 0.0
        d['total'] = self.initialCapital
        return [d]

    def constructCurrentHoldings(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        d['datetime'] = self.startDate
        d['cash'] = self.initialCapital
        d['commission'] = 0.0
        d['total'] = self.initialCapital
        return d

    def updateTimeindex(self):
        latestDatetime = self.bars.currentTimeIndex

        dh = dict((s, 0) for s in self.symbolList)
        dh['datetime'] = latestDatetime
        dh['cash'] = self.currentHoldings['cash']
        dh['commission'] = self.currentHoldings['commission']
        dh['total'] = self.currentHoldings['cash']

        for s in self.symbolList:
            marketValue = 0.0
            if self.currentPosition[s] != 0:
                marketValue = self.currentPosition[s] * self.bars.getLatestBarValue(s, 'close')
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

    def outputSummaryStats(self, curve):
        returns = curve['return']
        aggregateDaily = aggregateReturns(returns)
        drawDownDaily = drawDown(aggregateDaily)
        annualRet = annualReturn(aggregateDaily)
        annualVol = annualVolatility(aggregateDaily)
        sortino = sortinoRatio(aggregateDaily)
        sharp = sharpRatio(aggregateDaily)
        maxDrawDown = np.min(drawDownDaily['draw_down'])
        winningDays = np.sum(aggregateDaily > 0.)
        lossingDays = np.sum(aggregateDaily < 0.)

        perf_df = pd.DataFrame(index=aggregateDaily.index)
        perf_df['daily_return'] = aggregateDaily
        perf_df['daily_cum_return'] = np.exp(aggregateDaily.cumsum()) - 1.0
        perf_df['daily_draw_down'] = drawDownDaily['draw_down']

        perf_metric = pd.DataFrame([annualRet, annualVol, sortino, sharp, maxDrawDown, winningDays, lossingDays],
                                   index=['annual_return', 'annual_volatiltiy', 'sortino_ratio', 'sharp_ratio', 'max_draw_down', 'winning_days', 'lossing_days'],
                                   columns=['metrics'])
        self._createPerfSheet(curve, perf_df, drawDownDaily)
        return perf_metric, perf_df

    @plotting_context
    def _createPerfSheet(self, curve, perf_df, drawDownDaily):
        returns = curve['return']
        verticalSections = 4
        fig = plt.figure(figsize=(16, 7 * verticalSections))
        gs = gridspec.GridSpec(verticalSections, 3, wspace=0.5, hspace=0.5)

        axRollingReturns = plt.subplot(gs[0, :])
        axDrawDown = plt.subplot(gs[1, :], sharex=axRollingReturns)
        axUnderwater = plt.subplot(gs[2, :], sharex=axDrawDown)
        axMonthlyHeatmap = plt.subplot(gs[3, 0])
        axAnnualReturns = plt.subplot(gs[3, 1])
        axMonthlyDist = plt.subplot(gs[3, 2])

        plottingRollingReturn(perf_df['daily_cum_return'], axRollingReturns)
        plottingDrawdownPeriods(perf_df['daily_cum_return'], drawDownDaily, 5, axDrawDown)
        plottingUnderwater(drawDownDaily['draw_down'], axUnderwater)
        plottingMonthlyReturnsHeapmap(returns, axMonthlyHeatmap)
        plottingAnnualReturns(returns, axAnnualReturns)
        plottingMonthlyRetDist(returns, axMonthlyDist)

        plt.show()
        return fig

