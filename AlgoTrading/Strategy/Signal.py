# -*- coding: utf-8 -*-
u"""
Created on 2015-11-30

@author: cheng.li
"""

from abc import ABCMeta
from abc import abstractmethod
from AlgoTrading.Strategy.Strategy import Strategy


class Signal(Strategy):

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_data(self,):
        raise NotImplementedError()

    def _handle_data(self):
        self._orderRecords = []
        signals = self.handle_data()
        self._generateOrders(signals)
        self._processOrders()

    def _generateOrders(self, signals):
        pass
