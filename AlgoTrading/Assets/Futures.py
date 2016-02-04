# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue

_test_cost = 0.00015


class IFFutures(Asset):
    u"""

    中金所沪深300股指期货

    """
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=_test_cost, sellCost=_test_cost)
    multiplier = 300
    margin = 0.
    settle = 0.
    minimum = 1
    short = True


class IHFutures(Asset):
    u"""

    中金所上证50指数期货

    """
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=_test_cost, sellCost=_test_cost)
    multiplier = 300
    margin = 0.
    settle = 0.
    minimum = 1
    short = True


class ICFutures(Asset):
    u"""

    中金所中证500指数期货

    """
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=_test_cost, sellCost=_test_cost)
    multiplier = 200
    margin = 0.
    settle = 0.
    minimum = 1
    short = True

