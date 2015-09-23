# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

from AlgoTrading.Events.Event import Event


class MarketEvent(Event):

    def __init__(self):
        self.type = 'MARKET'
