# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

from abc import ABCMeta, abstractmethod
from AlgoTrading.Finance import Transaction
from AlgoTrading.Events import FillEvent


class ExecutionHanlder(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def executeOrder(self, event):
        raise NotImplementedError()


class SimulatedExecutionHandler(ExecutionHanlder):

    def __init__(self, events, assets, bars):
        self.events = events
        self.assets = assets
        self.bars = bars

    def executeOrder(self, event):
        if event.type == 'ORDER':
            exchange = event.symbol.split('.')[-1]
            transPrice = self.bars.getLatestBarValue(event.symbol, 'close')
            trans = Transaction(transPrice,
                                event.quantity,
                                event.direction)
            fillCost = transPrice * event.quantity * event.direction
            comCals = self.assets[event.symbol].commission
            commission = comCals.calculate(trans)
            fill_event = FillEvent(event.orderID,
                                   event.timeIndex,
                                   event.symbol,
                                   exchange,
                                   event.quantity,
                                   event.direction,
                                   fillCost,
                                   commission)
            self.events.put(fill_event)


