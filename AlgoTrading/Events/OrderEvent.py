# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

from AlgoTrading.Events.Event import Event


class OrderEvent(Event):

    _orderID = 1

    def __init__(self, timeIndex, symbol, orderType, quantity, direction):
        self.type = 'ORDER'
        self.timeIndex = timeIndex
        self.symbol = symbol
        self.orderType = orderType
        self.quantity = quantity
        self.direction = direction
        self.orderID = OrderEvent._orderID
        OrderEvent._orderID += 1

    def __str__(self):
        return "ID: {0:d}, " \
               "Order: Symbol = {1:s}, " \
               "Type = {2:s}, " \
               "Quantity = {3:s}, " \
               "Direction = {4:s}".format(self.orderID, self.symbol, self.orderType, self.quantity, self.direction)
