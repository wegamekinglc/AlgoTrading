# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
import datetime as dt
from AlgoTrading.Events import OrderEvent
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder


class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_data(self):
        raise NotImplementedError()

    def _subscribe(self):
        self._subscribed = []
        self._pNames = {}
        for k, v in self.__dict__.items():
            if isinstance(v, SecurityValueHolder):
                self._subscribed.append(v)
                if not self._pNames:
                    for name in v.dependency:
                        self._pNames[name] = set(v.dependency[name])
                else:
                    for name in self._pNames:
                        self._pNames[name] = self._pNames[name].union(set(v.dependency[name]))

    def _updateSubscribing(self):

        self._current_datetime = None
        values = dict()
        if self._pNames:
            for s in self._pNames:
                securityValue = {}
                fields = self._pNames[s]

                for f in fields:
                    try:
                        value = self.bars.getLatestBarValue(s, f)
                        if not self.current_datetime:
                            self._current_datetime = self.bars.getLatestBarDatetime(s)
                        securityValue[f] = value
                    except:
                        pass

                if securityValue:
                    values[s] = securityValue

            for subscriber in self._subscribed:
                subscriber.push(values)

    @property
    def universe(self):
        return self.symbolList

    def monitoring(self):
        pass

    @property
    def current_datetime(self):
        return self._current_datetime

    def order(self, symbol, direction, quantity):
        currDTTime = self.bars.getLatestBarDatetime(symbol)
        currDT = currDTTime.date()
        currValue = self.bars.getLatestBarValue(symbol, 'close')
        if direction == -1:
            amount = self._posBook.avaliableForSale(symbol, currDT)
            if amount < quantity:
                #print("{0} quantity need to be sold {1} is less then the available for sell amount {2}"
                #      .format(symbol, quantity, amount))
                return
        elif direction == 1:
            if quantity * currValue > self._port.currentHoldings['cash']:
                #print("cash needed to buy the quantity {0} of {1} is less than available cash {2}"
                #      .format(quantity, symbol,  self._port.currentHoldings['cash']))
                return
        else:
            raise ValueError("Unrecognized direction %d" % direction)

        self._posBook.updatePositionsByOrder(symbol, currDT, quantity, direction)
        signal = OrderEvent(currDTTime, symbol, "MKT", quantity, direction)
        self.events.put(signal)
        return signal.orderID

    @property
    def secPos(self):
        return self._port.currentPosition
