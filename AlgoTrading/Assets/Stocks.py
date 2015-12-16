# -*- coding: utf-8 -*-
u"""
Created on 2015-9-25

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue


class XSHGStock(Asset):
    lag = 1
    exchange = "XSHG"
    commission = PerValue(buyCost=0.0, sellCost=0.001)
    multiplier = 1.
    margin = 0.
    settle = 1.
    minimum = 100
    short = False


class XSHEStock(Asset):
    lag = 1
    exchange = "XSHE"
    commission = PerValue(buyCost=0.0, sellCost=0.001)
    multiplier = 1.
    margin = 0.
    settle = 1.
    minimum = 100
    short = False



