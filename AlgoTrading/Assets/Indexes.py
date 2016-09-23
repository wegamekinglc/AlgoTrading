# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue

index_cost = 0.


class EXIndex(Asset):
    u"""

    交易所指数

    """
    lag = 0
    exchange = "ZICN"
    commission = PerValue(buyCost=index_cost, sellCost=index_cost)
    multiplier = 1.
    margin = 1.
    settle = 1.
    minimum = 1
    short = True
    price_limit = 0.1


if __name__ == "__main__":

    s1 = EXIndex()
    s2 = EXIndex()

    s1.lag = 20
    print(s2)