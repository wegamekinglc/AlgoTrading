# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

from abc import ABCMeta, abstractmethod
from math import floor
import numpy as np
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

    def __init__(self, events, bars, portfolio, logger):
        super(SimulatedExecutionHandler, self).__init__(logger=logger)
        self.events = events
        self.portfolio = portfolio
        self.bars = bars

    def _search_suitable_quantity(self, transPrice, start_quantity, assetType, direction):
        multiplier = assetType.multiplier
        minimum = assetType.minimum
        settle = assetType.settle

        cash = max(self.portfolio.currentHoldings['cash'], 1e-5)
        if direction == 1 and settle != 0. and cash != np.inf:
            best_amount = floor(cash / transPrice / settle / minimum / multiplier) * minimum
        else:
            best_amount = np.inf

        if best_amount < assetType.minimum:
            return 0.0
        else:
            try_amount = min(best_amount, start_quantity)
            while True:
                fillCost = transPrice * try_amount * settle * multiplier * direction
                if fillCost < cash:
                    return try_amount
                elif try_amount < minimum:
                    return 0.0
                else:
                    try_amount -= minimum

    def executeOrder(self, event):
        if event.type == 'ORDER':
            transPrice = self.bars.getLatestBarValue(event.symbol, 'close')

            quantity = self._search_suitable_quantity(transPrice, event.quantity, event.assetType, event.direction)

            if quantity != 0:
                trans = Transaction(transPrice * event.assetType.multiplier,
                                    quantity,
                                    event.direction)
                fillCost = transPrice * quantity * event.direction * event.assetType.settle * event.assetType.multiplier
                nominal = transPrice * quantity * event.direction * event.assetType.multiplier

                commission = event.assetType.commission.calculate(trans)
                fill_event = FillEvent(event.orderID,
                                       event.timeIndex,
                                       event.symbol,
                                       quantity,
                                       event.direction,
                                       fillCost,
                                       commission,
                                       nominal)

                self.logger.info("{0}: Order ID: {1} filled at price: ${2} with quantity {3} direction {4}. "
                                 "original order quantity is {5}"
                                 .format(event.timeIndex,
                                         event.orderID,
                                         transPrice,
                                         quantity,
                                         event.direction,
                                         event.quantity))

                return fill_event


