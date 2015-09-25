# -*- coding: utf-8 -*-
u"""
Created on 2015-9-25

@author: cheng.li
"""

from AlgoTrading.Assets.base import Asset
from AlgoTrading.Finance.Commission import PerValue

XSHGStock = Asset(lag=1,
                  exchange='XSHG',
                  commission=PerValue(buyCost=0.00, sellCost=0.0))

XSHEStock = Asset(lag=1,
                  exchange='XSHE',
                  commission=PerValue(buyCost=0.00, sellCost=0.0))



