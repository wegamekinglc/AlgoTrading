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
from AlgoTrading.Utilities import logger
try:
    from AlgoTrading.Data.DataProviders import DXDataCenter
except ImportError:
    pass
from AlgoTrading.Data.DataProviders import YaHooDataProvider
from AlgoTrading.Execution.Execution import SimulatedExecutionHandler
from AlgoTrading.Execution.OrderBook import OrderBook
from AlgoTrading.Execution.FilledBook import FilledBook
from AlgoTrading.Portfolio.Portfolio import Portfolio
from AlgoTrading.Portfolio.PositionsBook import StocksPositionsBook
from AlgoTrading.Assets import XSHGStock


class Backtest(object):

    def __init__(self,
                 initial_capital,
                 heartbeat,
                 data_handler,
                 execution_handler,
                 portfolio,
                 strategy,
                 benchmark=None,
                 refreshRate=1,
                 plot=False):
        self.initialCapital = initial_capital
        self.heartbeat = heartbeat
        self.dataHandler = data_handler
        self.executionHanlderCls = execution_handler
        self.portfolioCls = portfolio
        self.strategyCls = strategy
        self.symbolList = self.dataHandler.symbolList
        self.assets = {s: XSHGStock for s in self.symbolList}
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
                                           self.initialCapital,
                                           self.benchmark)
        self.executionHanlder = self.executionHanlderCls(self.events, self.assets, self.dataHandler, self.portfolio)
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
                self.strategy.symbolList = self.dataHandler.updateBars()
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
                        if self.counter % self.refreshRate == 0:
                            self.strategy.handle_data()
                        self.portfolio.updateTimeindex()
                    elif event.type == 'SIGNAL':
                        self.signals += 1
                        self.portfolio.updateSignal(event)
                    elif event.type == 'ORDER':
                        self.orders += 1
                        self.orderBook.updateFromOrderEvent(event)
                        fill_event = self.executionHanlder.executeOrder(event)
                        self.fills += 1
                        self.orderBook.updateFromFillEvent(fill_event)
                        self.portfolio.updateFill(fill_event)
                        self.filledBook.updateFromFillEvent(fill_event)
                        orderTime = self.orderBook.orderTime(fill_event.orderID)
                        self.stocksPositionsBook.updatePositionsByFill(fill_event.symbol,
                                                                       orderTime.date(),
                                                                       fill_event.quantity,
                                                                       fill_event.direction)

            time.sleep(self.heartbeat)

    def _outputPerformance(self):
        print("Orders : {0:d}".format(self.orders))
        print("Fills  : {0:d}".format(self.fills))

        self.portfolio.createEquityCurveDataframe()
        perf_metric, perf_df = self.portfolio.outputSummaryStats(self.portfolio.equityCurve, self.plot)
        return self.portfolio.equityCurve, self.orderBook.view(), self.filledBook.view(), perf_metric, perf_df

    def simulateTrading(self):
        logger.info("Start backtesting...")
        self.strategy._subscribe()
        self._runBacktest()
        logger.info("Backesting finished!")
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
                   benchmark=None,
                   refreshRate=1,
                   saveFile=False,
                   plot=False,
                   **kwargs):

    if dataSource == DataSource.CSV:
        dataHandler = HistoricalCSVDataHandler(csvDir=kwargs['csvDir'],
                                               symbolList=symbolList)
    elif dataSource == DataSource.DataYes:
        dataHandler = DataYesMarketDataHandler(token=kwargs['token'],
                                               symbolList=symbolList,
                                               startDate=startDate,
                                               endDate=endDate,
                                               benchmark=benchmark)
    elif dataSource == DataSource.DXDataCenter:
        dataHandler = DXDataCenter(symbolList=symbolList,
                                   startDate=startDate,
                                   endDate=endDate,
                                   freq=kwargs['freq'],
                                   benchmark=benchmark)
    elif dataSource == DataSource.YAHOO:
        dataHandler = YaHooDataProvider(symbolList=symbolList,
                                        startDate=startDate,
                                        endDate=endDate)

    backtest = Backtest(initialCapital,
                        0.0,
                        dataHandler,
                        SimulatedExecutionHandler,
                        Portfolio,
                        userStrategy,
                        benchmark,
                        refreshRate,
                        plot=plot)

    equityCurve, orderBook, filledBook, perf_metric, perf_df = backtest.simulateTrading()

    # save to a excel file
    if saveFile:
        print(u"策略表现数据写入excel文件，请稍等...")
        perf_metric.to_csv('perf/perf_metrics.csv', float_format='%.4f')
        perf_df.to_csv('perf/perf_series.csv', float_format='%.4f')
        equityCurve.to_csv('perf/equity_curve.csv', float_format='%.4f')
        orderBook.to_csv('perf/order_book.csv', float_format='%.4f')
        filledBook.to_csv('perf/filled_book.csv', float_format='%.4f')
        print(u"写入完成！")

    return {'equity_curve': equityCurve,
             'order_book': orderBook,
             'filled_book': filledBook,
             'perf_metric': perf_metric,
             'perf_series': perf_df}
