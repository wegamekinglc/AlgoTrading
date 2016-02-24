# -*- coding: utf-8 -*-
u"""
Created on 2015-9-25

@author: cheng.li
"""

import datetime as dt
import bisect
import numpy as np
from PyFin.api import bizDatesList


class SymbolPositionsHistory(object):

    def __init__(self, symbol, lag, short, currDT, quantity, locked, direction, value):
        self.lag = lag
        self.shortable = short
        self.symbol = symbol
        self.dates = [currDT]
        self.positions = [quantity]
        self.locked = [locked]
        self.existDirections = [direction]
        self.existValues = [value]

    def avaliableForTrade(self, currDT, bizDatesList):
        if self.lag == 0:
            avaliableForSell, avaliableForBuy = np.inf, np.inf
        else:
            i = len(self.dates) - 1
            date = self.dates[i]

            while date > currDT:
                i -= 1
                if i < 0:
                    break
                date = self.dates[i]

            while i >= 0:
                startPos = bisect.bisect_left(bizDatesList, date)
                endPos = bisect.bisect_left(bizDatesList, currDT)
                bizDates = endPos - startPos + 1
                if bizDatesList[endPos] == currDT:
                    bizDates -= 1
                else:
                    bizDates -= 2
                if bizDates >= self.lag:
                    break
                i -= 1
                if i < 0:
                    break
                date = self.dates[i]

            avaliableForSell = 0
            avaliableForBuy = 0
            if i >= 0:
                for k in range(i+1):
                    if self.existDirections[k] == 1:
                        avaliableForSell += self.positions[k] - self.locked[k]
                    else:
                        avaliableForBuy += self.positions[k] - self.locked[k]
        return avaliableForSell, avaliableForBuy

    def updatePositionsByOrder(self, currDT, quantity, direction):

        toFinish = quantity
        i = 0
        while toFinish != 0 and i != len(self.dates):
            if self.existDirections[i] != direction:
                amount = self.positions[i] - self.locked[i]
                if amount >= toFinish:
                    self.locked[i] += toFinish
                    toFinish = 0
                    break
                else:
                    self.locked[i] = self.positions[i]
                    i += 1
                    toFinish -= amount
            else:
                i += 1

        if toFinish > 0 and direction == -1 and not self.shortable:
            raise ValueError("Existing amount is not enough to cover sell order. Short sell is not allowed for {0}"
                             .format(self.symbol))

    def updatePositionsByCancelOrder(self, currDt, quantity, direction):
        toFinish = quantity
        i = 0
        while toFinish != 0 and i != len(self.dates):
            if self.existDirections[i] != direction:
                self.locked[i] -= toFinish
                break
            i += 1

    def updatePositionsByFill(self, currDT, quantity, direction, value):
        posClosed = 0
        posOpened = 0
        pnl = 0.
        toFinish = quantity
        for i, d in enumerate(self.existDirections):
            if d != direction:
                amount = self.positions[i]
                if amount >= toFinish:
                    self.positions[i] -= toFinish
                    self.locked[i] -= toFinish
                    posClosed += toFinish
                    pnl += (value - self.existValues[i]) * d * toFinish
                    toFinish = 0
                    break
                else:
                    toFinish -= amount
                    self.positions[i] = 0
                    self.locked[i] = 0
                    posClosed += amount
                    pnl += (value - self.existValues[i]) * d * amount

        if toFinish:
            if len(self.dates) >= 1 and self.existDirections[-1] == direction and self.dates[-1] == currDT:
                self.existValues[-1] = \
                    (self.positions[-1] * self.existValues[-1] + toFinish * value) / (self.positions[-1] + toFinish)
                self.positions[-1] += toFinish
                toFinish = 0

            if toFinish and len(self.dates) >= 2 and self.existDirections[-2] == direction and self.dates[-2] == currDT:
                self.existValues[-2] = \
                    (self.positions[-2] * self.existValues[-2] + toFinish * value) / (self.positions[-2] + toFinish)
                self.positions[-2] += toFinish
                toFinish = 0

            if toFinish:
                self.dates.append(currDT)
                self.positions.append(toFinish)
                self.locked.append(0)
                self.existDirections.append(direction)
                self.existValues.append(value)
                posOpened = toFinish

        deleted = 0
        for k in range(i+1):
            if self.positions[k - deleted] == 0:
                del self.dates[k - deleted]
                del self.positions[k - deleted]
                del self.locked[k - deleted]
                del self.existDirections[k - deleted]
                del self.existValues[k - deleted]
                deleted += 1

        return posClosed, posOpened, pnl

    def bookValueAndBookPnL(self, currentPrice):
        bookValue = 0.
        bookPnL = 0.
        for p, d, c in zip(self.positions, self.existDirections, self.existValues):
            bookValue += p * d * currentPrice
            bookPnL += p * d * (currentPrice - c)
        return bookValue, bookPnL

    def empty(self):
        return len(self.dates) == 0


class StocksPositionsBook(object):

    _bizDatesList = bizDatesList("China.SSE", dt.datetime(1993, 1, 1), dt.datetime(2025, 12, 31))

    def __init__(self, assets):

        self._allPositions = {}
        self.assets = assets
        self._lags = {s: self.assets[s].lag for s in self.assets.keys()}
        self._shortable = {s: self.assets[s].short for s in self.assets.keys()}
        self._cachedSaleAmount = {}
        self._allPositions = {}

    def avaliableForTrade(self, symbol, currDT):
        if symbol in self._cachedSaleAmount:
            record = self._cachedSaleAmount[symbol]
            if record['date'] < currDT:
                return self._avaliableForTrade(symbol, currDT)
            else:
                return record['amount']
        else:
            return self._avaliableForTrade(symbol, currDT)

    def _avaliableForTrade(self, symbol, currDT):
        if symbol not in self._allPositions and not self._shortable[symbol]:
            avaliableForSell = 0
            avaliableForBuy = 0
        elif symbol not in self._allPositions:
            avaliableForSell, avaliableForBuy = np.inf, np.inf
        else:
            symbolPositionsHistory = self._allPositions[symbol]
            avaliableForSell, avaliableForBuy =\
                symbolPositionsHistory.avaliableForTrade(currDT,
                                                         StocksPositionsBook._bizDatesList)
        self._cachedSaleAmount[symbol] = {'date': currDT, 'amount': (avaliableForSell, avaliableForBuy)}
        return avaliableForSell, avaliableForBuy

    def updatePositionsByOrder(self, symbol, currDT, quantity, direction):
        if symbol not in self._allPositions:
            if not self._shortable[symbol] and direction == -1:
                raise ValueError("Short sell is not allowed for {0}".format(symbol))
        else:
            symbolPositionsHistory = self._allPositions[symbol]
            symbolPositionsHistory.updatePositionsByOrder(currDT, quantity, direction)

        # update cache for future usage
        self._avaliableForTrade(symbol, currDT)

    def updatePositionsByCancelOrder(self, symbol, currDT, quantity, direction):
        if symbol in self._allPositions:
            symbolPositionsHistory = self._allPositions[symbol]
            symbolPositionsHistory.updatePositionsByCancelOrder(currDT, quantity, direction)

        # update cache for future usage
        self._avaliableForTrade(symbol, currDT)

    def updatePositionsByFill(self, fill_evevt):
        posClosed = 0
        pnl = 0.
        symbol = fill_evevt.symbol
        currDT = fill_evevt.timeindex.date()
        quantity = fill_evevt.quantity
        direction = fill_evevt.direction
        value = fill_evevt.nominal / quantity / direction
        if symbol not in self._allPositions:
            lag = self._lags[symbol]
            short = self._shortable[symbol]
            self._allPositions[symbol] = SymbolPositionsHistory(symbol,
                                                                lag,
                                                                short,
                                                                currDT,
                                                                quantity,
                                                                0,
                                                                direction,
                                                                value)
            posOpened = quantity
        else:
            symbolPositionsHistory = self._allPositions[symbol]
            posClosed, posOpened, pnl = \
                symbolPositionsHistory.updatePositionsByFill(currDT, quantity, direction, value)

            if symbolPositionsHistory.empty():
                del self._allPositions[symbol]

        self._avaliableForTrade(symbol, currDT)
        return -posClosed * direction, posOpened * direction, pnl

    def getBookValueAndBookPnL(self, symbol, currentPrice):

        if symbol not in self._allPositions:
            return 0., 0.
        else:
            symbolPositionsHistory = self._allPositions[symbol]
            return symbolPositionsHistory.bookValueAndBookPnL(currentPrice)


if __name__ == "__main__":

    from AlgoTrading.Assets import XSHEStock
    from AlgoTrading.Assets import IndexFutures
    pb = StocksPositionsBook({'s': XSHEStock})
    pb.updatePositionsByOrder('s', dt.date(2015, 9, 23), 300, 1)
    print(pb._allPositions)
    pb.updatePositionsByOrder('s', dt.date(2015, 9, 23), 500, -1)
    print(pb._allPositions)



