# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
from AlgoTrading.Events import OrderEvent
from AlgoTrading.Strategy.InfoKeeper import InfoKepper
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder


class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_data(self,):
        raise NotImplementedError()

    def _subscribe(self):
        self._infoKeeper = InfoKepper()
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
                        if name in v.dependency:
                            self._pNames[name] = self._pNames[name].union(set(v.dependency[name]))

    def _updateSubscribing(self):

        self._current_datetime = None
        values = dict()
        criticalFields = set(['open', 'high', 'low', 'close'])
        if self._pNames:
            for s in self.symbolList:
                if s in self._pNames:
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
        self._orderRecords = []
        self.handle_data()
        self._processOrders()

    @property
    def universe(self):
        return self.symbolList

    @property
    def tradableAssets(self):
        return self.assets

    @tradableAssets.setter
    def tradableAssets(self, value):
        self.assets = value

    def monitoring(self):
        pass

    @property
    def current_datetime(self):
        return self._current_datetime

    def keep(self, label, value, time=None):
        if not time:
            time = self.current_datetime
        self._infoKeeper.attach(time, label, value)

    def infoView(self):
        return self._infoKeeper.view()

    @property
    def cash(self):
        return self._port.currentHoldings['cash']

    def avaliableForSale(self, symbol):
        return self.avaliableForTrade(symbol)[0]

    def avaliableForBuyBack(self, symbol):
        return self.avaliableForBuyBack(symbol)[1]

    def avaliableForTrade(self, symbol):
        currDTTime = self.current_datetime
        currDT = currDTTime.date()
        return self._posBook.avaliableForTrade(symbol, currDT)

    def _processOrders(self):

        signals = []

        cashAmount = max(self._port.currentHoldings['cash'], 1e-5)
        for order in self._orderRecords:
            symbol = order['symbol']
            quantity = order['quantity']
            direction = order['direction']
            currDTTime = self.bars.getLatestBarDatetime(symbol)
            currDT = currDTTime.date()
            currValue = self.bars.getLatestBarValue(symbol, 'close')

            multiplier = self._port.assets[symbol].multiplier
            settle = self._port.assets[symbol].settle
            margin = self._port.assets[symbol].margin
            shortable = self._port.assets[symbol].short

            # amount available for buy back or sell
            if direction == 1:
                amount = self._posBook.avaliableForTrade(symbol, currDT)[1]
            elif direction == -1:
                amount = self._posBook.avaliableForTrade(symbol, currDT)[0]

            fill_cost = quantity * currValue * multiplier * settle * direction

            margin_cost = max(quantity - amount, 0) * currValue * multiplier * margin
            maximumCashCost = max(fill_cost, margin_cost)

            if maximumCashCost <= cashAmount and (direction == 1 or (quantity <= amount or shortable)):
                signal = OrderEvent(currDTTime, symbol, "MKT", quantity, direction)
                self._posBook.updatePositionsByOrder(symbol, currDT, quantity, direction)
                signals.append(signal)
                cashAmount -= maximumCashCost
            elif maximumCashCost > cashAmount:
                if direction == 1:
                    self.logger.warning("{0}: ${1} cash needed to buy the quantity {2} of {3} "
                                        "is less than available cash ${4}"
                                        .format(currDTTime, maximumCashCost, quantity, symbol, cashAmount))
                else:
                    self.logger.warning("{0}: ${1} cash needed to sell the quantity {2} of {3} "
                                        "is less than available cash ${4}"
                                        .format(currDTTime, maximumCashCost, quantity, symbol, cashAmount))
            else:
                self.logger.warning("{0}: short disabled {1} quantity need to be sold {2} "
                                    "is less then the available for sell amount {3}"
                                    .format(currDTTime, symbol, quantity, amount))

        # log the signal informations
        for signal in signals:
            self.logger.info("{0}: {1} Order ID: {2} is sent with quantity {3} and direction {4} on symbol {5}"
                    .format(signal.timeIndex,
                            signal.orderType,
                            signal.orderID,
                            signal.quantity,
                            signal.direction,
                            signal.symbol))
            self.events.put(signal)

    def order_to(self, symbol, direction, quantity):
        currentPos = self.secPos[symbol]
        if direction == 1:
            posNeedToBuy = quantity - currentPos
            if posNeedToBuy > 0:
                self.order(symbol, 1, posNeedToBuy)
            elif posNeedToBuy < 0:
                self.order(symbol, -1, -posNeedToBuy)
        elif direction == -1:
            posNeedToSell = quantity + currentPos
            if posNeedToSell > 0:
                self.order(symbol, -1, posNeedToSell)
            elif posNeedToSell < 0:
                self.order(symbol, 1, -posNeedToSell)

    def order(self, symbol, direction, quantity):

        if symbol not in self.tradableAssets:
            self.logger.warning("Order for {0} with amount {1} and direction as {2} is rejected since {0}"
                                " is not a tradable asset!".format(symbol, quantity, direction))
            return

        if quantity % self._port.assets[symbol].minimum != 0:
            self.logger.warning("Order for {0} with amount {1} and direction as {2} is not consistent "
                                "with minimum bucket amount seeting. "
                                "Order is discarded!".format(symbol, quantity, direction))
            return

        if quantity > 0:
            self._orderRecords.append({'symbol': symbol, 'quantity': quantity, 'direction': direction})
        elif quantity == 0 and abs(direction) == 1:
            pass
        else:
            raise ValueError("Unrecognized direction %d" % direction)

    @property
    def secPos(self):
        return self._port.currentPosition

    @property
    def holdings(self):
        return self._port.allHoldings[-1]

    @property
    def realizedHoldings(self):
        return self._port.currentHoldings
