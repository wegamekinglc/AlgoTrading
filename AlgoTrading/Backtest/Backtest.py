# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

try:
    import Queue as queue
except ImportError:
    import queue
import time
import numpy as np
from PyFin.Env import Settings
from AlgoTrading.Enums import PortfolioType
from AlgoTrading.Execution.OrderBook import OrderBook
from AlgoTrading.Execution.FilledBook import FilledBook
from AlgoTrading.Assets import XSHGStock
from AlgoTrading.Assets import IFFutures
from AlgoTrading.Assets import ICFutures
from AlgoTrading.Assets import IHFutures


def setAssetsConfig(symbolList):
    res = {}
    for s in symbolList:
        if s[0].isalpha():
            if s.startswith('if'):
                res[s] = IFFutures
            elif s.startswith('ic'):
                res[s] = ICFutures
            elif s.startswith('ih'):
                res[s] = IHFutures
            else:
                res[s] = XSHGStock
        else:
            res[s] = XSHGStock
    return res


class Backtest(object):

    def __init__(self,
                 initial_capital,
                 heartbeat,
                 data_handler,
                 execution_handler,
                 portfolio,
                 strategy,
                 logger,
                 benchmark=None,
                 refreshRate=1,
                 plot=False,
                 portfolioType=PortfolioType.CashManageable):
        self.initialCapital = initial_capital
        self.heartbeat = heartbeat
        self.dataHandler = data_handler
        self.executionHanlderCls = execution_handler
        self.portfolioCls = portfolio
        self.strategyCls = strategy
        self.symbolList = self.dataHandler.symbolList
        self.tradable = self.dataHandler.tradableAssets
        self.assets = setAssetsConfig(self.tradable)
        self.events = queue.Queue()
        self.dataHandler.setEvents(self.events)
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1
        self.benchmark = benchmark
        self.refreshRate = refreshRate
        self.counter = 0
        self.plot = plot
        self.logger = logger
        self.portfolioType = portfolioType

        if portfolioType == PortfolioType.FullNotional:
            self.initialCapital = np.inf

        self._generateTradingInstance()

    def _generateTradingInstance(self):
        Settings.defaultSymbolList = self.symbolList
        self.strategy = self.strategyCls()
        self.strategy.events = self.events
        self.strategy.bars = self.dataHandler
        self.strategy.symbolList = self.symbolList
        self.strategy.logger = self.logger
        self.portfolio = self.portfolioCls(self.dataHandler,
                                           self.events,
                                           self.dataHandler.getStartDate(),
                                           self.assets,
                                           self.initialCapital,
                                           self.benchmark,
                                           self.portfolioType)
        self.executionHanlder = self.executionHanlderCls(self.events, self.dataHandler, self.portfolio, self.logger)
        self.orderBook = OrderBook()
        self.filledBook = FilledBook()
        self.portfolio.filledBook = self.filledBook
        self.strategy._port = self.portfolio
        self.strategy._posBook = self.portfolio.positionsBook

    def _runBacktest(self):
        i = 0
        while True:
            i += 1
            if self.dataHandler.continueBacktest:
                self.strategy.symbolList, self.strategy.tradableAssets = self.dataHandler.updateBars()
            else:
                break

            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                if event is not None:
                    if event.type == 'MARKET':
                        self.counter += 1
                        self.strategy._updateSubscribing()
                        self.portfolio.updateTimeindex()
                        if self.counter % self.refreshRate == 0:
                            self.strategy._handle_data()
                    elif event.type == 'SIGNAL':
                        self.signals += 1
                        self.portfolio.updateSignal(event)
                    elif event.type == 'ORDER':
                        self.orders += 1
                        event.assetType = self.assets[event.symbol]
                        self.orderBook.updateFromOrderEvent(event)
                        fill_event = self.executionHanlder.executeOrder(event)
                        self.fills += 1
                        if fill_event:
                            self.orderBook.updateFromFillEvent(fill_event)
                            self.portfolio.updateFill(fill_event)

            time.sleep(self.heartbeat)

    def _outputPerformance(self):
        self.logger.info("Orders : {0:d}".format(self.orders))
        self.logger.info("Fills  : {0:d}".format(self.fills))

        self.portfolio.createEquityCurveDataframe()
        perf_metric, perf_df, rollingRisk, aggregated_positions, transactions, turnover_rate = self.portfolio.outputSummaryStats(self.portfolio.equityCurve, self.plot)
        return self.portfolio.equityCurve, \
               self.orderBook.view(), \
               self.filledBook.view(), \
               perf_metric, perf_df, \
               rollingRisk, \
               aggregated_positions, \
               transactions, \
               turnover_rate, \
               self.strategy.infoView()

    def simulateTrading(self):
        self.logger.info("Start backtesting...")
        self.strategy._subscribe()
        self._runBacktest()
        self.logger.info("Backesting finished!")
        return self._outputPerformance()
