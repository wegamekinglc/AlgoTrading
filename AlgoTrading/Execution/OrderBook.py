# -*- coding: utf-8 -*-
u"""
Created on 2015-9-24

@author: cheng.li
"""

from enum import Enum
from enum import unique
import pandas as pd
from AlgoTrading.Events.OrderEvent import Order


@unique
class OrderStatus(str, Enum):
    Live = 'Live'
    Closed = 'Closed'
    Cancelled = 'Cancelled'


class OrderBook(object):

    def __init__(self):
        self._allOrders = {'type': {},
                           'time': {},
                           'symbol': {},
                           'quantity': {},
                           'filled': {},
                           'direction': {},
                           'status': {}}

    def updateFromOrderEvent(self, event):
        self._allOrders['type'][event.orderID] = event.orderType
        self._allOrders['time'][event.orderID] = event.timeIndex
        self._allOrders['symbol'][event.orderID] = event.symbol
        self._allOrders['quantity'][event.orderID] = event.quantity
        self._allOrders['filled'][event.orderID] = 0
        self._allOrders['direction'][event.orderID] = event.direction
        self._allOrders['status'][event.orderID] = OrderStatus.Live

    def orderTime(self, orderID):
        return self._allOrders['time'][orderID]

    def updateFromFillEvent(self, event):
        self._allOrders['filled'][event.orderID] += event.quantity
        if self._allOrders['filled'][event.orderID] == self._allOrders['quantity'][event.orderID]:
            self._allOrders['status'][event.orderID] = OrderStatus.Closed

    def view(self):
        data = pd.DataFrame(self._allOrders)
        data.index.name = 'orderID'
        return data

    def __iter__(self):
        for key in self._allOrders['type']:
            if self._allOrders['status'][key] == OrderStatus.Live:
                yield Order(key,
                            self._allOrders['time'][key],
                            self._allOrders['symbol'][key],
                            self._allOrders['type'][key],
                            self._allOrders['quantity'][key],
                            self._allOrders['filled'][key],
                            self._allOrders['direction'][key])
