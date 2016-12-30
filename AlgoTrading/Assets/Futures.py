# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue

future_cost = 0.00015


class ICFutures(Asset):
    u"""

    中金所中证500指数期货

    """
    lag = 0
    exchange = 'CCFX'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class IFFutures(Asset):
    u"""

    中金所沪深300股指期货

    """
    lag = 0
    exchange = 'CCFX'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
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
    exchange = 'CCFX'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
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
    exchange = 'CCFX'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
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
    exchange = 'CCFX'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class CUFutures(Asset):
    u"""

    上期所铜合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class ZNFutures(Asset):
    u"""

    上期所锌合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class AUFutures(Asset):
    u"""

    上期所黄金合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class AGFutures(Asset):
    u"""

    上期所白银合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class NIFutures(Asset):
    u"""

    上期所镍合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class SNFutures(Asset):
    u"""

    上期所锡合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class PBFutures(Asset):
    u"""

    上期所铅合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class HCFutures(Asset):
    u"""

    上期所热轧卷板合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class RBFutures(Asset):
    u"""

    上期所螺纹钢合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class RUFutures(Asset):
    u"""

    上期所天然橡胶合约

    """
    lag = 0
    exchange = 'XSGE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class AFutures(Asset):
    u"""

    大商所一号大豆合约

    """
    lag = 0
    exchange = 'XDCE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class IFutures(Asset):
    u"""

    大商所铁矿石合约

    """
    lag = 0
    exchange = 'XDCE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class JFutures(Asset):
    u"""

    大商所焦炭合约

    """
    lag = 0
    exchange = 'XDCE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class JMFutures(Asset):
    u"""

    大商所焦煤合约

    """
    lag = 0
    exchange = 'XDCE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class YFutures(Asset):
    u"""

    大商所豆油合约

    """
    lag = 0
    exchange = 'XDCE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class TAFutures(Asset):
    u"""

    郑商所PTA合约

    """
    lag = 0
    exchange = 'XZCE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1


class ZCFutures(Asset):
    u"""

    郑商所动力煤合约

    """
    lag = 0
    exchange = 'XZCE'
    commission = PerValue(buyCost=future_cost, sellCost=future_cost)
    multiplier = 1
    margin = 0.
    settle = 0.
    minimum = 1
    short = True
    price_limit = 0.1
