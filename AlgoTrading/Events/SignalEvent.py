# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

from AlgoTrading.Events.Event import Event


class SignalEvent(Event):

    def __init__(self, strategyId, symbol, datetime, signalType, strength, quantity):
        self.type = 'SIGNAL'
        self.strategyId = strategyId
        self.symbol = symbol
        self.datetime = datetime
        self.signalType = signalType
        self.strength = strength
        self.quantity = quantity
