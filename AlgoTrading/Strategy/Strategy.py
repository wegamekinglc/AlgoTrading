# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""

from __future__ import absolute_import
from abc import ABCMeta
from abc import abstractmethod
import datetime as dt
import numpy as np
import pandas as pd
from AlgoTrading.Events import OrderEvent
from AlgoTrading.Events import OrderDirection
from AlgoTrading.Strategy.InfoKeeper import InfoKepper
from AlgoTrading.Strategy.InfoKeeper import PlotInfoKeeper
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder


class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_data(self):
        return

    def handle_fill(self, event):
        return

    def handle_order(self, event):
        return

    def day_begin(self):
        return

    def _subscribe(self):
        self._infoKeeper = InfoKepper()
        self._plotKeeper = PlotInfoKeeper()
        self._subscribed = []
        self._pNames = {}
        for k, v in self.__dict__.items():
            if k != '_infoKeeper' and k != '_subscribed' and k != '_pNames':
                self._subscribeOneItem(v)

    def _subscribeOneItem(self, new_item):
        if isinstance(new_item, SecurityValueHolder):
            self._subscribed.append(new_item)
            if not self._pNames:
                for name in new_item.dependency:
                    self._pNames[name] = set(new_item.dependency[name])
            else:
                for name in self._pNames:
                    if name in new_item.dependency:
                        self._pNames[name] = self._pNames[name].union(set(new_item.dependency[name]))
        elif isinstance(new_item, list) or isinstance(new_item, set):
            for v in new_item:
                self._subscribeOneItem(v)
        elif isinstance(new_item, dict):
            for v in new_item.values():
                self._subscribeOneItem(v)

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
        self._posTargets = {}
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

    @current_datetime.setter
    def current_datetime(self, value):
        self._current_datetime = value

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

    def keep(self, name, value, time=None):
        u"""

        将用户需要保留的信息保存到指定的时间戳下，供回测后查看

        :param label: 指定信息的名称
        :param value: 指定信息的值
        :param time: 指定的时间戳，若为None，则使用当前bar的时间戳
        :return: None
        """
        if not time:
            time = self.current_datetime
        self._infoKeeper.attach(time, name, value)

    def plot(self, name, value, marker=None, line_style='solid', time=None):
        u"""

        将用户需要保留的信息保存到指定的时间戳下，供绘图使用

        :param label: 指定信息的名称
        :param value: 指定信息的值
        :param time: 指定的时间戳，若为None，则使用当前bar的时间戳
        :param marker: 数据点类型
        :param line_style: 线型
        :return: None
        """

        if not time:
            time = self.current_datetime
        self._plotKeeper.attach(time, name, value, marker, line_style)

    def infoView(self):
        u"""

        返回当前所保留的全部用户信息

        :return: pandas.DataFrame
        """
        return self._infoKeeper.view()

    def plotCurves(self):
        u"""

        返回当前所保留的全部绘图用信息

        :return: pandas.DataFrame
        """
        return self._plotKeeper.curves()

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
        return self.avaliableForTrade(symbol)[1]

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

        cashAmount = self._port.currentHoldings['cash']
        for order in self._orderRecords:
            cashAmount = max(cashAmount, 1.e-5)
            symbol = order['symbol']
            quantity = order['quantity']
            direction = order['direction']
            currValue = self.bars.getLatestBarValue(symbol, 'close')

            multiplier = self._port.assets[symbol].multiplier
            settle = self._port.assets[symbol].settle
            margin = self._port.assets[symbol].margin

            # amount available for buy back or sell
            if direction == OrderDirection.BUY:
                fill_cost = quantity * currValue * multiplier * settle
                margin_cost = 0.
            elif direction == OrderDirection.BUY_BACK:
                fill_cost = 0.
                margin_cost = 0.
            elif direction == OrderDirection.SELL:
                fill_cost = 0.
                margin_cost = 0.
            elif direction == OrderDirection.SELL_SHORT:
                fill_cost = 0.
                margin_cost = quantity * currValue * multiplier * margin

            maximumCashCost = max(fill_cost, margin_cost)

            if maximumCashCost <= cashAmount:
                signal = OrderEvent(currDTTime, symbol, "MKT", quantity, direction)
                self._posBook.updatePositionsByOrder(symbol, currDT, quantity, direction)
                signals.append(signal)
                cashAmount -= maximumCashCost
            elif maximumCashCost > cashAmount:
                if direction == OrderDirection.BUY:
                    self.logger.warning("{0}: ${1} cash needed to buy the quantity {2} of {3} "
                                        "is less than available cash ${4}"
                                        .format(currDTTime, maximumCashCost, quantity, symbol, cashAmount))
                elif direction == OrderDirection.SELL_SHORT:
                    self.logger.warning("{0}: ${1} cash needed to sell short the quantity {2} of {3} "
                                        "is less than available cash ${4}"
                                        .format(currDTTime, maximumCashCost, quantity, symbol, cashAmount))

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

        if symbol not in self._posTargets:
            currentPos = self.secPos[symbol]
            self._posTargets[symbol] = currentPos
        else:
            currentPos = self._posTargets[symbol]

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

        if symbol in self.priceLimitTable:
            currValue = self.bars.getLatestBarValue(symbol, 'close')
            low_limit, high_limit = self.priceLimitTable[symbol]
            if currValue <= low_limit and direction < 0:
                self.logger.warning("{0}: Order for {1} with amount {2} and direction as {3} is not sent "
                                    "with market is frozen at {4} lower limit price."
                                    .format(currDTTime, symbol, quantity, direction, currValue))
                return
            elif currValue >= high_limit and direction > 0:
                self.logger.warning("{0}: Order for {1} with amount {2} and direction as {3} is not sent "
                                    "with market is frozen at {4} higher limit price."
                                    .format(currDTTime, symbol, quantity, direction, currValue))
                return

        if symbol not in self._posTargets:
            self._posTargets[symbol] = self.secPos[symbol]

        if quantity > 0 and direction == 1:
            self._posTargets[symbol] += quantity
            buyback_amount = self.avaliableForBuyBack(symbol)
            if buyback_amount >= quantity:
                self._orderRecords.append({'symbol': symbol, 'quantity': quantity, 'direction': OrderDirection.BUY_BACK})
            else:
                if buyback_amount != 0:
                    self._orderRecords.append({'symbol': symbol, 'quantity': buyback_amount, 'direction': OrderDirection.BUY_BACK})
                self._orderRecords.append({'symbol': symbol, 'quantity': quantity - buyback_amount, 'direction': OrderDirection.BUY})
        elif quantity > 0 and direction == -1:
            self._posTargets[symbol] -= quantity
            sell_amount = self.avaliableForSale(symbol)
            if sell_amount >= quantity:
                self._orderRecords.append({'symbol': symbol, 'quantity': quantity, 'direction': OrderDirection.SELL})
            else:
                if self._port.assets[symbol].short:
                    if sell_amount != 0:
                        self._orderRecords.append({'symbol': symbol, 'quantity': sell_amount, 'direction': OrderDirection.SELL})
                    self._orderRecords.append({'symbol': symbol, 'quantity': quantity - sell_amount, 'direction': OrderDirection.SELL_SHORT})
                else:
                    self.logger.warning("{0}: short disabled {1} quantity need to be sold {2} "
                                        "is less then the available for sell amount {3}."
                                        .format(currDTTime, symbol, quantity, sell_amount))

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
    def liveOrders(self):
        return self._port.orderBook.liveOrders()

    def secPosDetail(self, secID):
        try:
            return self._port.positionsBook.positions(secID).view()
        except KeyError:
            return pd.DataFrame()

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

    def checkingPriceLimit(self):
        self.priceLimitTable = {}
        # only work for securities close at the same time
        for s in self.tradableAssets:
            try:
                previous_day_close = self.bars.getPreviousDayValue(s, 'close')
            except KeyError:
                previous_day_close = np.nan

            if not np.isnan(previous_day_close):
                price_limit = self._port.assets[s].price_limit
                self.priceLimitTable[s] = (1.005 - price_limit) * previous_day_close, (0.995 + price_limit) * previous_day_close,

