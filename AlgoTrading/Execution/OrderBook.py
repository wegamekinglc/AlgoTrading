# -*- coding: utf-8 -*-
u"""
Created on 2015-9-24

@author: cheng.li
"""

from enum import Enum
from enum import unique
import datetime as dt
import pandas as pd
from AlgoTrading.Events.OrderEvent import Order


@unique
class OrderStatus(str, Enum):
    Live = 'Live'
    Closed = 'Closed'
    Cancelled = 'Cancelled'


class OrderBook(object):

    def __init__(self, logger):
        self._allOrders = {'type': {},
                           'time': {},
                           'symbol': {},
                           'quantity': {},
                           'filled': {},
                           'direction': {},
                           'status': {}}
        self._liveOrders = {'type': {},
                            'time': {},
                            'symbol': {},
                            'quantity': {},
                            'filled': {},
                            'direction': {},
                            'status': {}}
        self.logger = logger

    def updateFromOrderEvent(self, event):
        self._allOrders['type'][event.orderID] = event.orderType
        self._allOrders['time'][event.orderID] = event.timeIndex
        self._allOrders['symbol'][event.orderID] = event.symbol
        self._allOrders['quantity'][event.orderID] = event.quantity
        self._allOrders['filled'][event.orderID] = 0
        self._allOrders['direction'][event.orderID] = event.direction
        self._allOrders['status'][event.orderID] = OrderStatus.Live

        self._liveOrders['type'][event.orderID] = event.orderType
        self._liveOrders['time'][event.orderID] = event.timeIndex
        self._liveOrders['symbol'][event.orderID] = event.symbol
        self._liveOrders['quantity'][event.orderID] = event.quantity
        self._liveOrders['filled'][event.orderID] = 0
        self._liveOrders['direction'][event.orderID] = event.direction
        self._liveOrders['status'][event.orderID] = OrderStatus.Live

    def orderTime(self, orderID):
        return self._allOrders['time'][orderID]

    def _delOrderFromLiveBook(self, orderID):
        del self._liveOrders['type'][orderID]
        del self._liveOrders['time'][orderID]
        del self._liveOrders['symbol'][orderID]
        del self._liveOrders['quantity'][orderID]
        del self._liveOrders['filled'][orderID]
        del self._liveOrders['direction'][orderID]
        del self._liveOrders['status'][orderID]

    def updateFromFillEvent(self, event):
        self._allOrders['filled'][event.orderID] += event.quantity
        self._liveOrders['filled'][event.orderID] += event.quantity
        if self._allOrders['filled'][event.orderID] == self._allOrders['quantity'][event.orderID]:
            self._allOrders['status'][event.orderID] = OrderStatus.Closed
            self._delOrderFromLiveBook(event.orderID)

    def view(self):
        data = pd.DataFrame(self._allOrders)
        data.index.name = 'orderID'
        return data

    def liveOrders(self):
        data = pd.DataFrame(self._liveOrders)
        data.index.name = 'orderID'
        return data

    def cancelOrders(self, timeIndex, posBook):
        for key in self._allOrders['type']:
            if self._allOrders['status'][key] == OrderStatus.Live:
                self._allOrders['status'][key] = OrderStatus.Cancelled
                self._delOrderFromLiveBook(key)
                remainingQuantity = self._allOrders['quantity'][key] - self._allOrders['filled'][key]
                direction = self._allOrders['direction'][key]
                currDTTime = self._allOrders['time'][key]
                currDT = dt.datetime(currDTTime.year, currDTTime.month, currDTTime.day)
                posBook.updatePositionsByCancelOrder(self._allOrders['symbol'][key], currDT, remainingQuantity, direction)
                self.logger.warning("{0}: {1} Legacy Order ID: {2} sent "
                                    "with time {3} and quantity {4} and direction {5} on symbol {6} "
                                    "is cancelled at today's day begin"
                                    .format(timeIndex,
                                            self._allOrders['type'][key],
                                            key,
                                            self._allOrders['time'][key],
                                            self._allOrders['quantity'][key],
                                            self._allOrders['direction'][key],
                                            self._allOrders['symbol'][key]))

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
