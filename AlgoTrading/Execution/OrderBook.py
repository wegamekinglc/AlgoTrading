# -*- coding: utf-8 -*-
u"""
Created on 2015-9-24

@author: cheng.li
"""

import pandas as pd


class OrderBook(object):

    def __init__(self):
        self._allOrders = {'type': {},
                           'time': {},
                           'symbol': {},
                           'quantity': {},
                           'filled': {},
                           'direction': {}}

    def updateFromOrderEvent(self, event):
        self._allOrders['type'][event.orderID] = event.orderType
        self._allOrders['time'][event.orderID] = event.timeIndex
        self._allOrders['symbol'][event.orderID] = event.symbol
        self._allOrders['quantity'][event.orderID] = event.quantity
        self._allOrders['filled'][event.orderID] = 0
        self._allOrders['direction'][event.orderID] = event.direction

    def orderTime(self, orderID):
        return self._allOrders['time'][orderID]

    def updateFromFillEvent(self, event):
        self._allOrders['filled'][event.orderID] += event.quantity

    def view(self):
        data = pd.DataFrame(self._allOrders)
        data.index.name = 'orderID'
        return data
