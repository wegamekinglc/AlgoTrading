# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
import datetime as dt
from AlgoTrading.Events import SignalEvent
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder


class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculateSignals(self):
        raise NotImplementedError()

    def _subscribe(self):
        self._subscribed = []
        self._pNames = tuple()
        for k, v in self.__dict__.items():
            if isinstance(v, SecurityValueHolder):
                self._subscribed.append(v)
                self._pNames = self._pNames + (v.dependency,)

    def _updateSubscribing(self):

        values = dict()
        for s in self._pNames[0]:
            securityValue = {}
            fields = self._pNames[0][s]
            try:
                value = self.bars.getLatestBarValue(s, fields)
                securityValue[fields] = value
            except:
                 pass
            values[s] = securityValue

        for subscriber in self._subscribed:
            subscriber.push(values)

    @property
    def universe(self):
        return self.symbolList

    def monitoring(self):
        pass

    def order(self, symbol, signalDirection, quantity):
        currentDT = dt.datetime.utcnow()
        signal = SignalEvent(1, symbol, currentDT, signalDirection, 1.0, quantity)
        self.events.put(signal)

    @property
    def secPos(self):
        return self._port.currentPosition
