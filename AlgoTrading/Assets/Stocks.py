# -*- coding: utf-8 -*-
u"""
Created on 2015-9-25

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue


class XSHEStock(Asset):
    u"""

    深圳证券交易所股票

    """
    lag = 1
    exchange = "XSHE"
    commission = PerValue(buyCost=0.0, sellCost=0.0)
    multiplier = 1.
    margin = 1.
    settle = 1.
    minimum = 1
    short = False
    price_limit = 0.1


class XSHGStock(Asset):
    u"""

    上海证券交易所股票

    """
    lag = 1
    exchange = "XSHG"
    commission = PerValue(buyCost=0.0, sellCost=0.0)
    multiplier = 1.
    margin = 1.
    settle = 1.
    minimum = 1
    short = False
    price_limit = 0.1


class USStock(Asset):
    lag = 0
    exchange = "XSHG"
    commission = PerValue(buyCost=0.0, sellCost=0.0)
    multiplier = 1.
    margin = 1.
    settle = 1.
    minimum = 1
    short = True
    price_limit = 9999.
