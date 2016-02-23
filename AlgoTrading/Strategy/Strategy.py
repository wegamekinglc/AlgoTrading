# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""

from __future__ import absolute_import
from abc import ABCMeta
from abc import abstractmethod
import datetime as dt
from AlgoTrading.Events import OrderEvent
from AlgoTrading.Strategy.InfoKeeper import InfoKepper
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder


class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_data(self):
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

    def _updateTime(self):
        self._current_datetime = None
        for s in self.symbolList:
            if not self.current_datetime:
                self._current_datetime = self.bars.getLatestBarDatetime(s)
                break

    def _updateSubscribing(self):

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
        u"""

        获取当前所有代码列表（包括指数等非交易型代码）

        :return: list
        """
        return self.symbolList

    @property
    def tradableAssets(self):
        u"""

        获取当前所有可交易证券代码列表

        :return: list
        """
        return self.assets

    @tradableAssets.setter
    def tradableAssets(self, value):
        self.assets = value

    def monitoring(self):
        pass

    @property
    def current_datetime(self):
        u"""

        获取策略当前运行的bar的时间戳

        :return: datetime.datetime
        """
        return self._current_datetime

    @property
    def current_date(self):
        u"""

        获取当前日期的字符串时间戳，格式为YYYY-MM-DD

        :return: str
        """
        return self._current_datetime.date().__str__()

    @property
    def current_time(self):
        u"""

        获取当前时间的字符串时间戳，格式为HH:MM:SS

        :return: str
        """
        return self._current_datetime.time().__str__()

    def keep(self, label, value, time=None):
        u"""

        将用户需要保留的信息保存到指定的时间戳下，供回测后查看

        :param label: 指定信息的名称
        :param value: 指定信息的值
        :param time: 指定的时间戳，若为None，则使用当前bar的时间戳
        :return: None
        """
        if not time:
            time = self.current_datetime
        self._infoKeeper.attach(time, label, value)

    def infoView(self):
        u"""

        返回当前所保留的全部用户信息

        :return: pandas.DataFrame
        """
        return self._infoKeeper.view()

    @property
    def cash(self):
        u"""

        返回当前账户现金

        :return: float
        """
        return self._port.currentHoldings['cash']

    @property
    def portfolioValue(self):
        u"""

        返回当前账户总净值

        :return: float
        """
        return self._port.allHoldings[-1]['total']

    def avaliableForSale(self, symbol):
        u"""

        返回指定证券当前可卖出数量

        :param symbol: 证券代码
        :return: int
        """
        return self.avaliableForTrade(symbol)[0]

    def avaliableForBuyBack(self, symbol):
        u"""

        返回指定证券当前可买回数量

        :param symbol: 证券代码
        :return: int
        """
        return self.avaliableForBuyBack(symbol)[1]

    def avaliableForTrade(self, symbol):
        u"""

        返回指定证券当前账户可交易数量，返回为一个tuple类型，分别为可卖出数量和可买回数量

        :param symbol: 证券代码
        :return: tuple
        """
        currDTTime = self.current_datetime
        currDT = currDTTime.date()
        return self._posBook.avaliableForTrade(symbol, currDT)

    def _processOrders(self):

        signals = []

        currDTTime = self.current_datetime
        if isinstance(currDTTime, dt.datetime):
            currDT = currDTTime.date()
        else:
            currDT = currDTTime

        cashAmount = max(self._port.currentHoldings['cash'], 1e-5)
        for order in self._orderRecords:
            symbol = order['symbol']
            quantity = order['quantity']
            direction = order['direction']
            currValue = self.bars.getLatestBarValue(symbol, 'close')

            multiplier = self._port.assets[symbol].multiplier
            settle = self._port.assets[symbol].settle
            margin = self._port.assets[symbol].margin

            # amount available for buy back or sell
            if direction == 1:
                amount = self._posBook.avaliableForTrade(symbol, currDT)[1]
            elif direction == -1:
                amount = self._posBook.avaliableForTrade(symbol, currDT)[0]

            fill_cost = quantity * currValue * multiplier * settle * direction

            margin_cost = max(quantity - amount, 0) * currValue * multiplier * margin
            maximumCashCost = max(fill_cost, margin_cost)

            if maximumCashCost <= cashAmount and (direction == 1 or quantity <= amount):
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
        u"""

        交易指定证券至指定要求的仓位

        :param symbol: 证券代码
        :param direction: 方向，1为买入，-1为卖出
        :param quantity: 指定要求的仓位
        :return: None
        """
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
        u"""

        交易指定量的指定证券

        :param symbol: 证券代码
        :param direction: 方向，1为买入，-1为卖出
        :param quantity:交易量
        :return: None
        """

        currDTTime = self.current_datetime

        if symbol not in self.tradableAssets:
            self.logger.warning("{0}: Order for {1} with amount {2} and direction as {3} is rejected since {1}"
                                " is not a tradable asset!".format(currDTTime, symbol, quantity, direction))
            return

        if quantity % self._port.assets[symbol].minimum != 0:
            self.logger.warning("{0}: Order for {1} with amount {2} and direction as {3} is not consistent "
                                "with minimum bucket amount seeting. "
                                "Order is discarded!".format(currDTTime, symbol, quantity, direction))
            return

        if quantity > 0 and abs(direction) == 1:
            self._orderRecords.append({'symbol': symbol, 'quantity': quantity, 'direction': direction})
        elif quantity == 0 and abs(direction) == 1:
            pass
        elif quantity < 0:
            raise ValueError("quantity cant't be negative as {0}".format(quantity))
        else:
            raise ValueError("Unrecognized direction {0}".format(direction))

    def order_pct(self, symbol, direction, pct):
        u"""

        交易占当前资产组合指定比例的证券

        :param symbol: 证券代码
        :param direction: 方向，1为买入，-1为卖出
        :param pct: 比例
        :return: None
        """
        currDTTime = self.current_datetime
        if pct < 0. or pct > 1.0:
            self.logger.warning("{0:}: Percentage order for {1} with percentage {2} and direction {4} is not allowed. "
                                "Percentage should be between 0 and 1".format(currDTTime, symbol, pct, direction))
            return

        portfolio_value = self.portfolioValue
        currValue = self.bars.getLatestBarValue(symbol, 'close')
        rought_amount = int(portfolio_value * pct / currValue)
        actual_amount = rought_amount // self._port.assets[symbol].minimum * self._port.assets[symbol].minimum
        self.order(symbol, direction, actual_amount)

    def order_to_pct(self, symbol, direction, pct):
        u"""

        交易证券至占当前组合指定比例

        :param symbol: 证券代码
        :param direction: 方向，1为买入，-1为卖出
        :param pct: 目标比例
        :return: None
        """
        currDTTime = self.current_datetime
        if pct < 0. or pct > 1.0:
            self.logger.warning("{0:}: Percentage order for {1} with percentage {2} and direction {4} is not allowed. "
                                "Percentage should be between 0 and 1".format(currDTTime, symbol, pct, direction))
            return

        portfolio_value = self.portfolioValue
        currValue = self.bars.getLatestBarValue(symbol, 'close')
        rought_amount = int(portfolio_value * pct / currValue)
        actual_amount = rought_amount // self._port.assets[symbol].minimum * self._port.assets[symbol].minimum
        self.order_to(symbol, direction, actual_amount)


    @property
    def secPos(self):
        u"""

        保存当前证券整体仓位信息(单位，股数）

        :return: int
        """
        return self._port.currentPosition

    @property
    def holdings(self):
        u"""

        保存当前证券仓位信息（单位，元）

        :return: float
        """
        return self._port.allHoldings[-1]

    @property
    def realizedHoldings(self):
        return self._port.currentHoldings
