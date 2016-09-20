# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue

index_future_cost = 0.0
bond_future_cost = 0.0


class IFFutures(Asset):
    u"""

    中金所沪深300股指期货

    """
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=index_future_cost, sellCost=index_future_cost)
    multiplier = 300
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class IHFutures(Asset):
    u"""

    中金所上证50指数期货

    """
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=index_future_cost, sellCost=index_future_cost)
    multiplier = 300
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class ICFutures(Asset):
    u"""

    中金所中证500指数期货

    """
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=index_future_cost, sellCost=index_future_cost)
    multiplier = 200
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class TFFutures(Asset):
    u"""

    中金所5年期国债期货

    """
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=bond_future_cost, sellCost=bond_future_cost)
    multiplier = 10000
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class TFutures(Asset):
    u"""

    中金所10年期国债期货

    """
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=bond_future_cost, sellCost=bond_future_cost)
    multiplier = 10000
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class RUFutures(Asset):
    lag = 0
    exchange = 'CFFEX'
    commission = PerValue(buyCost=0.002, sellCost=0.002)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1

