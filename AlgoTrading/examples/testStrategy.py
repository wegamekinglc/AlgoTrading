# -*- coding: utf-8 -*-
u"""
Created on 2015-12-08

@author: cheng.li
"""

import datetime as dt
from AlgoTrading.api import Strategy
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import DataSource


class UserStrategy(Strategy):

    def handle_data(self):

        for s in self.tradableAssets:
            self.order(s, 1, 100)

res = strategyRunner(userStrategy=UserStrategy,
                     symbolList=['600000.xshg', 'if.ccfx'],
                     startDate=dt.datetime(2015, 1, 1),
                     endDate=dt.datetime(2016, 9, 19),
                     benchmark='000300.zicn',
                     dataSource=DataSource.DataYes,
                     freq=5,
                     plot=True)