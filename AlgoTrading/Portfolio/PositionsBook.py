# -*- coding: utf-8 -*-
u"""
Created on 2015-9-25

@author: cheng.li
"""

import datetime as dt
import bisect
from PyFin.api import bizDatesList


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
        lag = self._lags[symbol]
        if symbol not in self._allPositions:
            avaliableForSell = 0
            avaliableForBuy = 0
        elif lag == 0:
            _, positions, locked, existDirections, _ = self._allPositions[symbol]
            avaliableForSell = 0
            avaliableForBuy = 0
            for i, direction in enumerate(existDirections):
                if direction == 1:
                    avaliableForSell += positions[i] - locked[i]
                else:
                    avaliableForBuy += positions[i] - locked[i]
        else:
            dates, positions, locked, existDirections, _ = self._allPositions[symbol]
            i = len(dates) - 1
            date = dates[i]

            while date > currDT:
                i -= 1
                if i < 0:
                    break
                date = dates[i]

            while i >= 0:
                startPos = bisect.bisect_left(StocksPositionsBook._bizDatesList, date)
                endPos = bisect.bisect_left(StocksPositionsBook._bizDatesList, currDT)
                bizDates = endPos - startPos + 1
                if StocksPositionsBook._bizDatesList[endPos] == currDT:
                    bizDates -= 1
                else:
                    bizDates -= 2
                if bizDates >= lag:
                    break
                i -= 1
                if i < 0:
                    break
                date = dates[i]

            avaliableForSell = 0
            avaliableForBuy = 0
            if i >= 0:
                for k in range(i+1):
                    if existDirections[k] == 1:
                        avaliableForSell += positions[k] - locked[k]
                    else:
                        avaliableForBuy += positions[k] - locked[k]
        self._cachedSaleAmount[symbol] = {'date': currDT, 'amount': (avaliableForSell, avaliableForBuy)}
        return avaliableForSell, avaliableForBuy

    def updatePositionsByOrder(self, symbol, currDT, quantity, direction):
        if symbol not in self._allPositions:
            if not self._shortable[symbol] and direction == -1:
                raise ValueError("Short sell is not allowed for {0}".format(symbol))
        else:
            dates, positions, locked, existDirections, _ = self._allPositions[symbol]

            toFinish = quantity
            i = 0
            while toFinish != 0 and i != len(dates):
                if existDirections[i] != direction:
                    amount = positions[i] - locked[i]
                    if amount >= toFinish:
                        locked[i] += toFinish
                        toFinish = 0
                        break
                    else:
                        locked[i] = positions[i]
                        i += 1
                        toFinish -= amount
                else:
                    i += 1

            if toFinish > 0 and direction == -1 and not self._shortable[symbol]:
                raise ValueError("Existing amount is not enough to cover sell order. Short sell is not allowed for {0}".format(symbol))

        self._avaliableForTrade(symbol, currDT)

    def updatePositionsByFill(self, fill_evevt):
        posClosed = 0
        posOpened = 0
        pnl = 0.
        symbol = fill_evevt.symbol
        currDT = fill_evevt.timeindex.date()
        quantity = fill_evevt.quantity
        direction = fill_evevt.direction
        value = fill_evevt.nominal / quantity / direction
        if symbol not in self._allPositions:
            self._allPositions[symbol] = [currDT], [quantity], [0], [direction], [value]
            posOpened = quantity
        else:
            dates, positions, locked, existDirections, existValues = self._allPositions[symbol]
            toFinish = quantity
            for i, d in enumerate(existDirections):
                if d != direction:
                    amount = positions[i]
                    if amount >= toFinish:
                        positions[i] -= toFinish
                        locked[i] -= toFinish
                        posClosed += toFinish
                        pnl += (value - existValues[i]) * d * toFinish
                        toFinish = 0
                        break
                    else:
                        toFinish -= amount
                        positions[i] = 0
                        locked[i] = 0
                        posClosed += amount
                        pnl += (value - existValues[i]) * d * amount
            if toFinish != 0:
                dates.append(currDT)
                positions.append(toFinish)
                locked.append(0)
                existDirections.append(direction)
                existValues.append(value)
                posOpened = toFinish

            for k in range(i+1):
                if positions[k] == 0:
                    del dates[k]
                    del positions[k]
                    del locked[k]
                    del existDirections[k]
                    del existValues[k]

            if not dates:
                del self._allPositions[symbol]

        self._avaliableForTrade(symbol, currDT)
        return - posClosed * direction, posOpened * direction, pnl

    def getBookValueAndBookPnL(self, symbol, currentPrice):

        if symbol not in self._allPositions:
            return 0., 0.
        else:
            bookValue = 0.
            bookPnL = 0.
            _, positions, _, existDirections, existCosts = self._allPositions[symbol]
            for p, d, c in zip(positions, existDirections, existCosts):
                bookValue += p * d * currentPrice
                bookPnL += p * d * (currentPrice - c)
            return bookValue, bookPnL


if __name__ == "__main__":

    from AlgoTrading.Assets import XSHEStock
    from AlgoTrading.Assets import IndexFutures
    pb = StocksPositionsBook({'s': XSHEStock})
    pb.updatePositionsByOrder('s', dt.date(2015, 9, 23), 300, 1)
    print(pb._allPositions)
    pb.updatePositionsByOrder('s', dt.date(2015, 9, 23), 500, -1)
    print(pb._allPositions)



