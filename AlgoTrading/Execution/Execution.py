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
from AlgoTrading.Env import Settings


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

    def _search_suitable_quantity(self, transPrice, start_quantity, assetType, direction, max_quantity):
        multiplier = assetType.multiplier
        minimum = assetType.minimum
        settle = assetType.settle

        cash = max(self.portfolio.currentHoldings['cash'], 1e-5)
        if direction == 1 and settle != 0. and cash != np.inf:
            best_amount = floor(cash / transPrice / settle / minimum / multiplier) * minimum

            best_amount = min(best_amount, int(max_quantity / minimum) * minimum)
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

    def executeOrder(self, order, asset_type, order_book, portfolio):
        transVolume = self.bars.getLatestBarValue(order.symbol, 'volume')
        if transVolume == 0:
            self.logger.warning("{0}: Order ID: {1}  for {2} can't be filled in market frozen status."
                                .format(order.timeIndex,
                                        order.orderID,
                                        order.symbol))
            return None
        transPrice = self.bars.getLatestBarValue(order.symbol, 'close')
        timeIndex = self.bars.getLatestBarDatetime(order.symbol)

        quantity = self._search_suitable_quantity(transPrice,
                                                  order.quantity - order.filled,
                                                  asset_type,
                                                  order.direction,
                                                  int(transVolume * Settings.market_volume_cap))

        if quantity != 0:
            trans = Transaction(transPrice * asset_type.multiplier,
                                quantity,
                                order.direction)
            fillCost = transPrice * quantity * order.direction * asset_type.settle * asset_type.multiplier
            nominal = transPrice * quantity * order.direction * asset_type.multiplier

            commission = asset_type.commission.calculate(trans)
            fill_event = FillEvent(order.orderID,
                                   timeIndex,
                                   order.symbol,
                                   quantity,
                                   order.direction,
                                   fillCost,
                                   commission,
                                   nominal)

            self.logger.info("{0}: Order ID: {1} filled at price: ${2} with quantity {3} direction {4}. "
                             "original order quantity is {5}"
                             .format(timeIndex,
                                     order.orderID,
                                     transPrice,
                                     quantity,
                                     order.direction,
                                     order.quantity))

            order_book.updateFromFillEvent(fill_event)
            portfolio.updateFill(fill_event)


