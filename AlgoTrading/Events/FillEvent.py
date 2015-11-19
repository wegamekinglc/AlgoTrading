# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

from AlgoTrading.Events.Event import Event


class FillEvent(Event):

    def __init__(self, orderID, timeindex, symbol, quantity, direction, fillCost, commission, nominal):
        self.type = 'FILL'
        self.orderID = orderID
        self.timeindex = timeindex
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.fillCost = fillCost
        self.commission = commission
        self.nominal = nominal
