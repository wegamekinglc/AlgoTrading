# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

from abc import ABCMeta, abstractmethod
from math import floor
import numpy as np
from AlgoTrading.Finance import Transaction
from AlgoTrading.Events import OrderDirection
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

        portfolio_value = self.portfolio.currentHoldings['total']
        cash = self.portfolio.currentHoldings['cash']
        current_margin = self.portfolio.currentHoldings['margin']

        global_leverage_cap = Settings.strategy_leverage_cap
        margin_usable = portfolio_value * global_leverage_cap - current_margin

        cash_usable = min(cash - current_margin, margin_usable)

        if (direction == OrderDirection.BUY or direction == OrderDirection.BUY_BACK) and settle != 0. and margin_usable != np.inf:
            if direction == OrderDirection.BUY:
                best_amount = floor(cash_usable / transPrice / settle / minimum / multiplier) * minimum
                best_amount = min(best_amount, int(max_quantity / minimum) * minimum)
            else:
                best_amount = int(max_quantity / minimum) * minimum
        elif direction == OrderDirection.SELL:
            best_amount = int(max_quantity / minimum) * minimum
        elif margin_usable != np.inf:
            if margin_usable <= 0:
                best_amount = 0
            else:
                # check the short amount
                market_amount = min(int(max_quantity / minimum) * minimum, np.inf)
                margin_amount = floor(margin_usable / transPrice / minimum / multiplier) * minimum
                best_amount = min(market_amount, margin_amount)
        else:
            best_amount = int(max_quantity / minimum) * minimum

        if best_amount < assetType.minimum:
            return 0.0
        else:
            try_amount = min(best_amount, start_quantity)
            if direction == OrderDirection.BUY:
                while True:
                    fillCost = transPrice * try_amount * settle * multiplier
                    if fillCost < cash:
                        return try_amount
                    elif try_amount < minimum:
                        return 0.0
                    else:
                        try_amount -= minimum
            return try_amount

    def executeOrder(self, order, asset_type, order_book, portfolio):
        transVolume = self.bars.getLatestBarValue(order.symbol, 'volume')
        timeIndex = self.bars.getLatestBarDatetime(order.symbol)
        if transVolume == 0 or np.isnan(transVolume):
            self.logger.warning("{0}: Order ID: {1} sent at {2} for {3} can't be filled in market frozen status."
                                .format(timeIndex,
                                        order.orderID,
                                        order.timeIndex,
                                        order.symbol))
            return None
        transPrice = self.bars.getLatestBarValue(order.symbol, 'close')

        quantity = self._search_suitable_quantity(transPrice,
                                                  order.quantity - order.filled,
                                                  asset_type,
                                                  order.direction,
                                                  int(transVolume * Settings.market_volume_cap))

        if quantity != 0:
            trans = Transaction(transPrice * asset_type.multiplier,
                                quantity,
                                order.direction)
            if order.direction == OrderDirection.BUY or order.direction == OrderDirection.BUY_BACK:
                fillCost = transPrice * quantity * asset_type.settle * asset_type.multiplier
                nominal = transPrice * quantity * asset_type.multiplier
            else:
                fillCost = -transPrice * quantity * asset_type.settle * asset_type.multiplier
                nominal = -transPrice * quantity * asset_type.multiplier

            commission = asset_type.commission.calculate(trans)
            fill_event = FillEvent(order.orderID,
                                   timeIndex,
                                   order.symbol,
                                   quantity,
                                   order.direction,
                                   fillCost,
                                   commission,
                                   nominal)

            self.events.put(fill_event)

            self.logger.info("{0}: Order ID: {1} sent at {2} filled at price: ${3} with quantity {4} direction {5}. "
                             "original order quantity is {6}"
                             .format(timeIndex,
                                     order.orderID,
                                     order.timeIndex,
                                     transPrice,
                                     quantity,
                                     order.direction,
                                     order.quantity))

            order_book.updateFromFillEvent(fill_event)
            portfolio.updateFill(fill_event)


