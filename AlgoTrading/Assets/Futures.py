# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue

IFFutures = Asset(lag=0,
                  exchange='CFFEX',
                  commission=PerValue(buyCost=0.00, sellCost=0.00),
                  multiplier=300,
                  margin=0.,
                  settle=0.,
                  minimum=1,
                  short=True)

IHFutures = Asset(lag=0,
                  exchange='CFFEX',
                  commission=PerValue(buyCost=0.00, sellCost=0.00),
                  multiplier=300,
                  margin=0.,
                  settle=0.,
                  minimum=1,
                  short=True)

ICFutures = Asset(lag=0,
                  exchange='CFFEX',
                  commission=PerValue(buyCost=0.00, sellCost=0.00),
                  multiplier=200,
                  margin=0.,
                  settle=0.,
                  minimum=1,
                  short=True)

