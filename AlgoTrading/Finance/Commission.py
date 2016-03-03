# -*- coding: utf-8 -*-
u"""
Created on 2015-9-24

@author: cheng.li
"""

from AlgoTrading.Events import OrderDirection


class Transaction:

    def __init__(self, price, quantity, direction):
        self.price = price
        self.quantity = quantity
        self.direction = direction


class PerShare(object):

    def __init__(self, cost=0.03, minTradeCost=None):
        self.cost = float(cost)
        self.minTradeCost = None if minTradeCost is None else float(minTradeCost)

    def calculate(self, transaction):
        commission = transaction.quantity * self.cost
        if self.minTradeCost is None:
            return commission
        else:
            commission = max(commission, self.minTradeCost)
            return commission

    def __str__(self):
        return "{className}(cost={cost}, min trade cost={minTradeCost})"\
            .format(className=self.__class__.__name__,
                    cost=self.cost,
                    minTradeCost=self.minTradeCost)

    def __repr__(self):
        return self.__str__()


class PerTrade(object):

    def __init__(self, cost=5.0):
        self.cost = float(cost)

    def calculate(self, transaction):
        if transaction.quantity == 0:
            return 0.0

        return self.cost

    def __str__(self):
        return "PerTrade(cost={0})".format(self.cost)

    def __repr__(self):
        return self.__str__()


class PerValue(object):

    def __init__(self, buyCost=0.003, sellCost=0.):
        self.buyCost = float(buyCost)
        self.sellCost = float(sellCost)

    def calculate(self, transaction):
        if transaction.direction == OrderDirection.BUY or transaction.direction == OrderDirection.BUY_BACK:
            costPerShare = transaction.price * self.buyCost
        else:
            costPerShare = transaction.price * self.sellCost
        return transaction.quantity * costPerShare

    def __str__(self):
        return "PerValue(buyCost={0}, sellCost={1})".format(self.buyCost, self.sellCost)

    def __repr__(self):
        return self.__str__()