# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
from AlgoTrading.Events import OrderEvent
from AlgoTrading.Utilities import logger
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
        criticalFields = set(['open', 'high', 'low', 'close'])
        if self._pNames:
            for s in self._pNames:
                securityValue = {}
                fields = self._pNames[s]

                for f in fields:
                    try:
                        value = self.bars.getLatestBarValue(s, f)
                        if not self.current_datetime:
                            self._current_datetime = self.bars.getLatestBarDatetime(s)
                        if f not in criticalFields or value != 0.0:
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

    @property
    def cash(self):
        return self._port.currentHoldings['cash']

    def avaliableForSale(self, symbol):
        currDTTime = self.current_datetime
        currDT = currDTTime.date()
        amount = self._posBook.avaliableForSale(symbol, currDT)
        return amount

    def order(self, symbol, direction, quantity):
        currDTTime = self.current_datetime
        currDT = currDTTime.date()
        currValue = self.bars.getLatestBarValue(symbol, 'close')
        if direction == -1:
            amount = self._posBook.avaliableForSale(symbol, currDT)
            if amount < quantity:
                logger.warning("{0}: {1} quantity need to be sold {2} is less then the available for sell amount {3}"
                               .format(currDTTime, symbol, quantity, amount))
                return
        elif direction == 1:
            if quantity * currValue > self._port.currentHoldings['cash']:
                logger.warning("{0}: ${1} cash needed to buy the quantity {2} of {3} is less than available cash ${4}"
                               .format(currDTTime, quantity * currValue, quantity, symbol,  self._port.currentHoldings['cash']))
                return
        else:
            raise ValueError("Unrecognized direction %d" % direction)

        self._posBook.updatePositionsByOrder(symbol, currDT, quantity, direction)
        signal = OrderEvent(currDTTime, symbol, "MKT", quantity, direction)

        logger.info("{0}: {1} Order ID: {2} is sent with quantity {3} and direction {4} on symbol {5}"
                    .format(signal.timeIndex, signal.orderType, signal.orderID, signal.quantity, signal.direction, symbol))

        self.events.put(signal)
        return signal.orderID

    @property
    def secPos(self):
        return self._port.currentPosition
