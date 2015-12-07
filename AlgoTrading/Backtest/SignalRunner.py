# -*- coding: utf-8 -*-
u"""
Created on 2015-11-30

@author: cheng.li
"""

from AlgoTrading.Enums import DataSource
from AlgoTrading.Enums import PortfolioType
from AlgoTrading.Backtest.StrategyRunner import strategyRunner


def signalRunner(signal,
                 symbolList,
                 startDate,
                 endDate,
                 dataSource=DataSource.DXDataCenter,
                 benchmark=None,
                 refreshRate=1,
                 saveFile=False,
                 plot=False,
                 logLevel='info',
                 **kwargs):

    # signal is a special kind of strategy

    return strategyRunner(userStrategy=signal,
                          initialCapital=1.,
                          symbolList=symbolList,
                          startDate=startDate,
                          endDate=endDate,
                          dataSource=dataSource,
                          benchmark=benchmark,
                          refreshRate=refreshRate,
                          saveFile=saveFile,
                          plot=plot,
                          logLevel=logLevel,
                          portfolioType=PortfolioType.FullNotional,
                          **kwargs)



