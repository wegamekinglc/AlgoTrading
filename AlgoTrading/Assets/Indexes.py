# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue


class EXIndex(Asset):
    u"""

    交易所指数

    """
    lag = 0
    exchange = "SE"
    commission = PerValue(buyCost=0.0, sellCost=0.0)
    multiplier = 1.
    margin = 1.
    settle = 1.
    minimum = 1
    short = True
    price_limit = 0.1
