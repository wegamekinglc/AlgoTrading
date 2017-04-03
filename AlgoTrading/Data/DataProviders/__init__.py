# -*- coding: utf-8 -*-
u"""
Created on 2015-9-21

@author: cheng.li
"""

from AlgoTrading.Data.DataProviders.CSVFiles import HistoricalCSVDataHandler
from AlgoTrading.Data.DataProviders.DataYes import DataYesMarketDataHandler
try:
    from AlgoTrading.Data.DataProviders.Wind import WindMarketDataHandler
except ImportError:
    pass
from AlgoTrading.Data.DataProviders.Tushare import TushareMarketDataHandler
try:
    from AlgoTrading.Data.DataProviders.DongXingDataCenter import DXDataCenter
except ImportError:
    pass
from AlgoTrading.Data.DataProviders.YaHoo import YaHooDataProvider

__all__ = ["HistoricalCSVDataHandler",
           "DataYesMarketDataHandler",
           "DXDataCenter",
           "YaHooDataProvider",
           "WindMarketDataHandler",
           "TushareMarketDataHandler"]
