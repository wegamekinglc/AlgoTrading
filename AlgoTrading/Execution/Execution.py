# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

from abc import ABCMeta, abstractmethod
from math import floor
from AlgoTrading.Finance import Transaction
from AlgoTrading.Events import FillEvent


class ExecutionHanlder(object):

    __metaclass__ = ABCMeta

    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    def executeOrder(self, event):
        raise NotImplementedError()


class SimulatedExecutionHandler(ExecutionHanlder):

    def __init__(self, events, assets, bars, portfolio, logger):
        super(SimulatedExecutionHandler, self).__init__(logger=logger)
        self.events = events
        self.assets = assets
        self.portfolio = portfolio
        self.bars = bars

    def _search_suitable_quantity(self, transPrice, start_quantity, commission_calc):
        cash = self.portfolio.currentHoldings['cash']
        best_amount = floor(cash / transPrice / 100.0) * 100.0
        if best_amount < 100.0:
            return 0.0
        else:
            try_amount = min(best_amount, start_quantity)
            while True:
                fillCost = transPrice * try_amount
                trans = Transaction(transPrice,
                                    try_amount,
                                    1)
                commission = commission_calc.calculate(trans)
                if (fillCost + commission) < cash:
                    return try_amount
                elif try_amount < 100.0:
                    return 0.0
                else:
                    try_amount -= 100.0

    def executeOrder(self, event):
        if event.type == 'ORDER':
            exchange = event.symbol.split('.')[-1]
            transPrice = self.bars.getLatestBarValue(event.symbol, 'close')
            comCals = self.assets[event.symbol].commission

            if event.direction == 1:
                quantity = self._search_suitable_quantity(transPrice, event.quantity, comCals)
            elif event.direction == -1:
                quantity = event.quantity
            else:
                raise ValueError("Unknow direction: {0}".format(event.direction))

            trans = Transaction(transPrice,
                                quantity,
                                event.direction)
            fillCost = transPrice * quantity * event.direction

            commission = comCals.calculate(trans)
            fill_event = FillEvent(event.orderID,
                                   event.timeIndex,
                                   event.symbol,
                                   exchange,
                                   quantity,
                                   event.direction,
                                   fillCost,
                                   commission)

            self.logger.info("{0}: Order ID: {1} filled at price: ${2} with quantity {3} direction {4}. "
                        "original order quantity is {5}"
                        .format(event.timeIndex, event.orderID, transPrice, quantity, event.direction, event.quantity))

            return fill_event


