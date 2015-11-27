# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue

_test_cost = 0.00015

IFFutures = Asset(lag=0,
                  exchange='CFFEX',
                  commission=PerValue(buyCost=_test_cost, sellCost=_test_cost),
                  multiplier=6,
                  margin=0.,
                  settle=0.,
                  minimum=1,
                  short=True)

IHFutures = Asset(lag=0,
                  exchange='CFFEX',
                  commission=PerValue(buyCost=_test_cost, sellCost=_test_cost),
                  multiplier=8,
                  margin=0.,
                  settle=0.,
                  minimum=1,
                  short=True)

ICFutures = Asset(lag=0,
                  exchange='CFFEX',
                  commission=PerValue(buyCost=_test_cost, sellCost=_test_cost),
                  multiplier=3,
                  margin=0.,
                  settle=0.,
                  minimum=1,
                  short=True)

