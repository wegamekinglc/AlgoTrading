# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

from AlgoTrading.Events.Event import Event


class FillEvent(Event):

    def __init__(self, orderID, timeindex, symbol, exchange, quantity, direction, fillCost, commission=None):
        self.type = 'FILL'
        self.orderID = orderID
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fillCost = fillCost

        # calculate commission
        if commission is None:
            self.commission = self._calculateIbCommission()
        else:
            self.commission = commission

    def _calculateIbCommission(self):
        if self.quantity <= 500:
            fullCost = max(1.3, 0.013 * self.quantity)
        else:
            fullCost = max(1.3, 0.008 * self.quantity)
        return fullCost
