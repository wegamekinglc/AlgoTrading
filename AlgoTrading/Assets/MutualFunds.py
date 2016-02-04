# -*- coding: utf-8 -*-
u"""
Created on 2016-1-18

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue


class XSHGMutualFund(Asset):
    u"""

    上海证券交易所公募基金

    """
    lag = 1
    exchange = "XSHG"
    commission = PerValue(buyCost=0.0, sellCost=0.001)
    multiplier = 1.
    margin = 0.
    settle = 1.
    minimum = 100
    short = False


class XSHEMutualFund(Asset):
    u"""

    深圳证券交易所公募基金E

    """
    lag = 1
    exchange = "XSH"
    commission = PerValue(buyCost=0.0, sellCost=0.001)
    multiplier = 1.
    margin = 0.
    settle = 1.
    minimum = 100
    short = False



