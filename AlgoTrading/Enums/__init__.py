# -*- coding: utf-8 -*-
u"""
Created on 2015-11-25

@author: cheng.li
"""

from enum import IntEnum
from enum import unique

@unique
class DataSource(IntEnum):
    CSV = 0
    DataYes = 1
    DXDataCenter = 2
    YAHOO = 3
    WIND = 4
    TUSHARE = 5


@unique
class PortfolioType(IntEnum):
    FullNotional = 0
    CashManageable = 1
