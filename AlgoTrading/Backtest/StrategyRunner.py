# -*- coding: utf-8 -*-
u"""
Created on 2015-11-30

@author: cheng.li
"""

import os
import shutil
import datetime as dt
from AlgoTrading.Enums import DataSource
from AlgoTrading.Enums import PortfolioType
from AlgoTrading.Utilities import CustomLogger
from AlgoTrading.Data.DataProviders import HistoricalCSVDataHandler
from AlgoTrading.Data.DataProviders import DataYesMarketDataHandler
try:
    from AlgoTrading.Data.DataProviders import DXDataCenter
except ImportError:
    pass
from AlgoTrading.Data.DataProviders import YaHooDataProvider
from AlgoTrading.Execution.Execution import SimulatedExecutionHandler
from AlgoTrading.Portfolio.Portfolio import Portfolio
from AlgoTrading.Backtest.Backtest import Backtest


def strategyRunner(userStrategy,
                   strategyParameters=(),
                   initialCapital=100000,
                   symbolList=['600000.XSHG'],
                   startDate=dt.datetime(2015, 9, 1),
                   endDate=dt.datetime(2015, 9, 15),
                   dataSource=DataSource.DXDataCenter,
                   benchmark=None,
                   refreshRate=1,
                   saveFile=False,
                   plot=True,
                   logLevel='critical',
                   portfolioType=PortfolioType.FullNotional,
                   **kwargs):

    logger = CustomLogger(logLevel)

    if dataSource == DataSource.CSV:
        dataHandler = HistoricalCSVDataHandler(csvDir=kwargs['csvDir'],
                                               symbolList=symbolList,
                                               logger=logger)
    elif dataSource == DataSource.DataYes:
        try:
            token = kwargs['token']
        except KeyError:
            token = None
        dataHandler = DataYesMarketDataHandler(token=token,
                                               symbolList=symbolList,
                                               startDate=startDate,
                                               endDate=endDate,
                                               benchmark=benchmark,
                                               logger=logger)
    elif dataSource == DataSource.DXDataCenter:
        try:
            freq = kwargs['freq']
        except KeyError:
            freq = 0
        dataHandler = DXDataCenter(symbolList=symbolList,
                                   startDate=startDate,
                                   endDate=endDate,
                                   freq=freq,
                                   benchmark=benchmark,
                                   logger=logger)
    elif dataSource == DataSource.YAHOO:
        dataHandler = YaHooDataProvider(symbolList=symbolList,
                                        startDate=startDate,
                                        endDate=endDate,
                                        logger=logger)

    backtest = Backtest(initialCapital,
                        0.0,
                        dataHandler,
                        SimulatedExecutionHandler,
                        Portfolio,
                        userStrategy,
                        logger,
                        benchmark,
                        refreshRate,
                        plot=plot,
                        portfolioType=portfolioType,
                        strategyParameters=strategyParameters)

    equityCurve, \
    orderBook, \
    filledBook, \
    perf_metric, \
    perf_df, \
    rollingRisk, \
    aggregated_positions, \
    transactions, \
    turnover_rate, \
    info_view \
        = backtest.simulateTrading()

    # save to a excel file
    if saveFile:
        if os.path.isdir('performance/'):
            shutil.rmtree('performance/')
        os.mkdir('performance/')
        logger.info("Strategy performance is now saving to local files...")
        perf_metric.to_csv('performance/perf_metrics.csv', float_format='%.4f')
        perf_df.to_csv('performance/perf_series.csv', float_format='%.4f')
        if benchmark is not None:
            rollingRisk.to_csv('performance/rollingRisk.csv', float_format='%.4f')
        equityCurve.to_csv('performance/equity_curve.csv', float_format='%.4f')
        orderBook.to_csv('performance/order_book.csv', float_format='%.4f')
        filledBook.to_csv('performance/filled_book.csv', float_format='%.4f')
        aggregated_positions.to_csv('performance/aggregated_positions.csv', float_format='%.4f')
        turnover_rate.to_csv('performance/turnover_rate.csv', float_format='%.4f')
        transactions.to_csv('performance/transactions.csv', float_format='%.4f')
        info_view.to_csv('performance/strategy_info.csv', float_format='%.4f')
        logger.info("Performance saving is finished!")

    return {'equity_curve': equityCurve,
            'order_book': orderBook,
            'filled_book': filledBook,
            'perf_metric': perf_metric,
            'perf_series': perf_df,
            'aggregated_positions': aggregated_positions,
            'transactions': transactions,
            'turnover_rate': turnover_rate,
            'user_info': info_view}
