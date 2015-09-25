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
import datetime as dt
from enum import IntEnum
from enum import unique
from pandas import ExcelWriter
from PyFin.Env import Settings
from AlgoTrading.Data.DataProviders import HistoricalCSVDataHandler
from AlgoTrading.Data.DataProviders import DataYesMarketDataHandler
from AlgoTrading.Data.DataProviders import DXDataCenter
from AlgoTrading.Data.DataProviders import YaHooDataProvider
from AlgoTrading.Execution.Execution import SimulatedExecutionHandler
from AlgoTrading.Execution.OrderBook import OrderBook
from AlgoTrading.Execution.FilledBook import FilledBook
from AlgoTrading.Portfolio.Portfolio import Portfolio
from AlgoTrading.Portfolio.PositionsBook import StocksPositionsBook
from AlgoTrading.Assets import XSHGStock


class Backtest(object):

    def __init__(self,
                 symbol_list,
                 initial_capital,
                 heartbeat,
                 data_handler,
                 execution_handler,
                 portfolio,
                 strategy):
        self.symbolList = [s.lower() for s in symbol_list]
        self.initialCapital = initial_capital
        self.heartbeat = heartbeat
        self.dataHandler = data_handler
        self.executionHanlderCls = execution_handler
        self.portfolioCls = portfolio
        self.strategyCls = strategy
        self.assets = {s: XSHGStock for s in self.symbolList}
        self.events = queue.Queue()
        self.dataHandler.setEvents(self.events)
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self._generateTradingInstance()

    def _generateTradingInstance(self):
        Settings.defaultSymbolList = self.symbolList
        self.strategy = self.strategyCls()
        self.strategy.events = self.events
        self.strategy.bars = self.dataHandler
        self.strategy.symbolList = self.symbolList
        self.portfolio = self.portfolioCls(self.dataHandler,
                                           self.events,
                                           self.dataHandler.getStartDate(),
                                           self.initialCapital)
        self.executionHanlder = self.executionHanlderCls(self.events, self.assets, self.dataHandler)
        self.orderBook = OrderBook()
        self.filledBook = FilledBook()
        lags = {s: self.assets[s].lag for s in self.symbolList}
        self.stocksPositionsBook = StocksPositionsBook(lags)
        self.strategy._port = self.portfolio
        self.strategy._posBook = self.stocksPositionsBook

    def _runBacktest(self):

        i = 0
        while True:
            i += 1
            if self.dataHandler.continueBacktest:
                self.dataHandler.updateBars()
            else:
                break

            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                if event is not None:
                    if event.type == 'MARKET':
                        self.strategy._updateSubscribing()
                        self.strategy.handle_data()
                        self.portfolio.updateTimeindex()
                    elif event.type == 'SIGNAL':
                        self.signals += 1
                        self.portfolio.updateSignal(event)
                    elif event.type == 'ORDER':
                        self.orders += 1
                        self.orderBook.updateFromOrderEvent(event)
                        self.executionHanlder.executeOrder(event)
                    elif event.type == 'FILL':
                        self.fills += 1
                        self.orderBook.updateFromFillEvent(event)
                        self.portfolio.updateFill(event)
                        self.filledBook.updateFromFillEvent(event)
                        orderTime = self.orderBook.orderTime(event.orderID)
                        self.stocksPositionsBook.updatePositionsByFill(event.symbol,
                                                                       orderTime.date(),
                                                                       event.quantity,
                                                                       event.direction)

            time.sleep(self.heartbeat)

    def _outputPerformance(self):
        print("Signals: {0:d}".format(self.signals))
        print("Orders : {0:d}".format(self.orders))
        print("Fills  : {0:d}".format(self.fills))

        self.portfolio.createEquityCurveDataframe()
        return self.portfolio.equityCurve, self.orderBook.view(), self.filledBook.view()

    def simulateTrading(self):
        self.strategy._subscribe()
        self._runBacktest()
        return self._outputPerformance()


@unique
class DataSource(IntEnum):
    CSV = 0
    DataYes = 1
    DXDataCenter = 2
    YAHOO = 3


def strategyRunner(userStrategy,
                   initialCapital=100000,
                   symbolList=['600000.XSHG'],
                   startDate=dt.datetime(2015, 9, 1),
                   endDate=dt.datetime(2015, 9, 15),
                   dataSource=DataSource.DXDataCenter,
                   **kwargs):

    if dataSource == DataSource.CSV:
        dataHandler = HistoricalCSVDataHandler(csvDir=kwargs['csvDir'],
                                               symbolList=symbolList)
    elif dataSource == DataSource.DataYes:
        dataHandler = DataYesMarketDataHandler(token=kwargs['token'],
                                               symbolList=symbolList,
                                               startDate=startDate,
                                               endDate=endDate)
    elif dataSource == DataSource.DXDataCenter:
        dataHandler = DXDataCenter(symbolList=symbolList,
                                   startDate=startDate,
                                   endDate=endDate,
                                   freq=kwargs['freq'])
    elif dataSource == DataSource.YAHOO:
        dataHandler = YaHooDataProvider(symbolList=symbolList,
                                        startDate=startDate,
                                        endDate=endDate)

    backtest = Backtest(symbolList,
                        initialCapital,
                        0.0,
                        dataHandler,
                        SimulatedExecutionHandler,
                        Portfolio,
                        userStrategy)

    equityCurve, orderBook, filledBook = backtest.simulateTrading()

    # save to a excel file
    writer = ExcelWriter('performance.xlsx')
    equityCurve.to_excel(writer, 'equity_curve', float_format='%.2f')
    orderBook.to_excel(writer, 'order_book', float_format='%.2f')
    filledBook.to_excel(writer, 'filled_book', float_format='%.2f')
    writer.save()
