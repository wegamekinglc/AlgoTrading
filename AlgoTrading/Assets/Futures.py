# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue

IndexFutures = Asset(lag=0,
                     exchange='SFE',
                     commission=PerValue(buyCost=0.0002, sellCost=0.0002),
                     multiplier=300,
                     margin=1.,
                     settle=0.,
                     minimum=1,
                     short=True)

