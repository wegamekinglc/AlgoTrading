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

    def _handle_data(self):
        self._buyOrderRecords = []
        self._sellOrderRecords = []
        self.handle_data()
        self._processOrders()

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

    def _processOrders(self):

        signals = []

        # buy orders
        cashAmount = self._port.currentHoldings['cash']
        for order in self._buyOrderRecords:
            symbol = order['symbol']
            quantity = order['quantity']
            currDTTime = self.bars.getLatestBarDatetime(symbol)
            currValue = self.bars.getLatestBarValue(symbol, 'close')
            currDT = currDTTime.date()
            if (quantity * currValue) < cashAmount:
                signal = OrderEvent(currDTTime, symbol, "MKT", quantity, 1)
                self._posBook.updatePositionsByOrder(symbol, currDT, quantity, 1)
                signals.append(signal)
                cashAmount -= quantity * currValue
            else:
                logger.warning("{0}: ${1} cash needed to buy the quantity {2} of {3} is less than available cash ${4}"
                               .format(currDTTime, quantity * currValue, quantity, symbol, cashAmount))

        # sell orders
        for order in self._sellOrderRecords:
            symbol = order['symbol']
            quantity = order['quantity']
            currDTTime = self.bars.getLatestBarDatetime(symbol)
            currDT = currDTTime.date()
            amount = self._posBook.avaliableForSale(symbol, currDT)
            if amount >= quantity:
                signal = OrderEvent(currDTTime, symbol, "MKT", quantity, -1)
                self._posBook.updatePositionsByOrder(symbol, currDT, quantity, -1)
                signals.append(signal)
            else:
                logger.warning("{0}: {1} quantity need to be sold {2} is less then the available for sell amount {3}"
                               .format(currDTTime, symbol, quantity, amount))

        # log the signal informations
        for signal in signals:
            logger.info("{0}: {1} Order ID: {2} is sent with quantity {3} and direction {4} on symbol {5}"
                    .format(signal.timeIndex,
                            signal.orderType,
                            signal.orderID,
                            signal.quantity,
                            signal.direction,
                            signal.symbol))
            self.events.put(signal)

    def order(self, symbol, direction, quantity):
        if direction == 1:
            self._buyOrderRecords.append({'symbol': symbol, 'quantity': quantity})
        elif direction == -1:
            self._sellOrderRecords.append({'symbol': symbol, 'quantity': quantity})
        else:
            raise ValueError("Unrecognized direction %d" % direction)

    @property
    def secPos(self):
        return self._port.currentPosition
