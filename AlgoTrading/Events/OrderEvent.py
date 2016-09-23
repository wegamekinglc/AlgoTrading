# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

from enum import Enum
from enum import unique
from AlgoTrading.Events.Event import Event

@unique
class OrderDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    SELL_SHORT = "SELL_SHORT"
    BUY_BACK = "BUY_BACK"


class Order:

    def __init__(self, orderID, timeIndex, symbol, orderType, quantity, filled, direction):
        self.orderID = orderID
        self.timeIndex = timeIndex
        self.symbol = symbol
        self.orderType = orderType
        self.quantity = quantity
        self.filled = filled
        self.direction = direction


class OrderEvent(Event):

    _orderID = 1

    def __init__(self, timeIndex, symbol, orderType, quantity, direction):
        self.type = 'ORDER'
        self.timeIndex = timeIndex
        self.symbol = symbol
        self.orderType = orderType
        self.quantity = quantity
        self.filled = 0
        self.direction = direction
        self.orderID = OrderEvent._orderID
        OrderEvent._orderID += 1

    def __str__(self):
        return "ID: {0}, " \
               "Order: Symbol = {1}, " \
               "Type = {2}, " \
               "Quantity = {3}, " \
               "filled = {4}, " \
               "Direction = {5}".format(self.orderID,
                                         self.symbol,
                                         self.orderType,
                                         self.quantity,
                                         self.filled,
                                         self.direction)

    def to_order(self):
        return Order(self.orderID,
                     self.timeIndex,
                     self.symbol,
                     self.orderType,
                     self.quantity,
                     self.filled,
                     self.direction)
