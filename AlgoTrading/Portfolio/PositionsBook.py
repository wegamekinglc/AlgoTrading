# -*- coding: utf-8 -*-
u"""
Created on 2015-9-25

@author: cheng.li
"""

import datetime as dt
import bisect
from PyFin.API import bizDatesList


class StocksPositionsBook(object):

    _bizDatesList = bizDatesList("China.SSE", dt.datetime(1993, 1, 1), dt.datetime(2025, 12, 31))

    def __init__(self, lags):

        self._allPositions = {}
        self._lags = lags
        self._cachedSaleAmount = {}

    def avaliableForSale(self, symbol, currDT):
        if symbol in self._cachedSaleAmount:
            record = self._cachedSaleAmount[symbol]
            if record['date'] < currDT:
                return self._avaliableForSale(symbol, currDT)
            else:
                return record['amount']
        else:
            return self._avaliableForSale(symbol, currDT)

    def _avaliableForSale(self, symbol, currDT):
        lag = self._lags[symbol]
        if symbol not in self._allPositions:
            amount = 0
        elif lag == 0:
            avalPos = self._allPositions[symbol]
            amount = sum(avalPos[1])
        else:
            dates, positions, locked = self._allPositions[symbol]
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

            if i < 0:
                amount = 0
            else:
                amount = sum(positions[:i+1]) - sum(locked[:i+1])
        self._cachedSaleAmount[symbol] = {'date': currDT, 'amount': amount}
        return amount

    def updatePositionsByOrder(self, symbol, currDT, quantity, direction):
        if symbol not in self._allPositions:
            if direction == 1:
                self._allPositions[symbol] = ([currDT], [quantity], [quantity])
            else:
                raise ValueError("Short sell is currently not allowed")
        else:
            dates, positions, locked = self._allPositions[symbol]
            if direction == 1:
                if dates[-1] == currDT:
                    positions[-1] += quantity
                    locked[-1] += quantity
                else:
                    self._allPositions[symbol][0].append(currDT)
                    self._allPositions[symbol][1].append(quantity)
                    self._allPositions[symbol][2].append(quantity)
            elif direction == -1:
                i = 0
                toSell = quantity
                while toSell != 0:
                    amount = positions[i] - locked[i]
                    if amount >= toSell:
                        locked[i] += toSell
                        break
                    else:
                        locked[i] = positions[i]
                        i += 1
                        toSell -= amount
            else:
                raise ValueError("Unrecognized direction %d" % direction)
        self._avaliableForSale(symbol, currDT)

    def updatePositionsByFill(self, symbol, currDT, quantity, direction):
        dates, positions, locked = self._allPositions[symbol]
        if direction == 1:
            i = 0
            while dates[i] != currDT:
                i += 1
            locked[i] -= quantity
        elif direction == -1:
            i = 0
            toSell = quantity
            while toSell != 0:
                amount = positions[i]
                if amount >= toSell:
                    positions[i] -= toSell
                    locked[i] -= toSell
                    break
                else:
                    i += 1
                    toSell -= amount
            if positions[i] == 0:
                i += 1
            if i != 0:
                del dates[:i]
                del positions[:i]
                del locked[:i]

            if not dates:
                del self._allPositions[symbol]

        else:
            raise ValueError("Unrecognized direction %d" % direction)
        self._avaliableForSale(symbol, currDT)

if __name__ == "__main__":

    import datetime as dt

    pb = StocksPositionsBook({'s':1})
    pb.updatePositionsByOrder('s', dt.datetime(2015, 9, 23), 300, 1)
    pb.updatePositionsByFill('s', dt.datetime(2015, 9, 23), 50, 1)
    pb.updatePositionsByOrder('s', dt.datetime(2015, 9, 24), 100, 1)
    pb.updatePositionsByOrder('s', dt.datetime(2015, 9, 25), 200, 1)
    pb.updatePositionsByFill('s', dt.datetime(2015, 9, 24), 50, 1)
    pb.updatePositionsByFill('s', dt.datetime(2015, 9, 25), 50, 1)
    print(pb._allPositions['s'])
    print(pb.avaliableForSale('s', dt.datetime(2015, 9, 25)))
    print(pb.avaliableForSale('s', dt.datetime(2015, 9, 25)))
    pb.updatePositionsByOrder('s', dt.datetime(2015, 9, 25), 75, -1)
    print(pb.avaliableForSale('s', dt.datetime(2015, 9, 25)))
    pb.updatePositionsByOrder('s', dt.datetime(2015, 9, 25), 250, -1)
    print(pb.avaliableForSale('s', dt.datetime(2015, 9, 25)))
    pb.updatePositionsByFill('s', dt.datetime(2015, 9, 25), 250, -1)
    print(pb._allPositions['s'])
    pb.updatePositionsByFill('s', dt.datetime(2015, 9, 25), 100, -1)
    print(pb._allPositions['s'])



