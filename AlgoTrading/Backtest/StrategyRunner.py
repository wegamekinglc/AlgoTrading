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
from AlgoTrading.Env import Settings


def strategyRunner(userStrategy,
                   strategyParameters=(),
                   initialCapital=100000,
                   symbolList=['600000.XSHG'],
                   startDate=dt.datetime(2015, 9, 1),
                   endDate=dt.datetime(2015, 9, 15),
                   benchmark=None,
                   refreshRate=1,
                   saveFile=False,
                   plot=True,
                   logLevel='critical',
                   portfolioType=PortfolioType.FullNotional,
                   **kwargs):
    u"""

    回测用运行器

    :param userStrategy: 用户自定义策略
    :param strategyParameters: 用户自定义策略所用参数，默认为None
    :param initialCapital: 初始资金，默认为100000
    :param symbolList: 证券代码，默认为600000.xshg
    :param startDate: 回测起始日，默认为2015年9月1日
    :param endDate: 回测结束日，默认为2015年9月15日
    :param dataSource: 行情数据源，默认为DataSource.DXDataCenter
    :param benchmark: 比较基准，比如指数。默认为None
    :param refreshRate: bar的调用频率，默认为0
    :param saveFile: 是否保存表现的数据为本地文件，默认为False
    :param plot: 是否绘制表现图，默认为True
    :param logLevel: 日志的等级
    :param portfolioType: 收益计算的方法
    :param kwargs: 其他需要的关键字参数
    :return: dict
    """

    logger = CustomLogger(logLevel)


    try:
        dataSource = kwargs['dataSource']
        Settings.set_source(dataSource)
    except KeyError:
        dataSource = Settings.data_source

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
            logger.info("No `freq` keyword arguments found. using default value as freq=0")
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
