# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

from AlgoTrading.Events.Event import Event


class FillEvent(Event):

    def __init__(self, orderID, timeindex, symbol, exchange, quantity, direction, fillCost, commission):
        self.type = 'FILL'
        self.orderID = orderID
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fillCost = fillCost
        self.commission = commission
