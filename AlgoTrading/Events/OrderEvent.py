# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

from AlgoTrading.Events.Event import Event


class OrderEvent(Event):

    def __init__(self, symbol, orderType, quantity, direction):
        self.type = 'ORDER'
        self.symbol = symbol
        self.orderType = orderType
        self.quantity = quantity
        self.direction = direction

    def __str__(self):
        return "Order: Symbol = {0:s}, " \
               "Type = {1:s}, " \
               "Quantity = {2:s}, " \
               "Direction = {3:s}".format(self.symbol, self.orderType, self.quantity, self.direction)
