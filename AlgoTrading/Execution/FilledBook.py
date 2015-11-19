# -*- coding: utf-8 -*-
u"""
Created on 2015-9-24

@author: cheng.li
"""

import pandas as pd


class FilledBook(object):

    _filledCount = 1

    def __init__(self):
        self._allFills = {'orderID': {},
                          'time': {},
                          'symbol': {},
                          'quantity': {},
                          'direction': {},
                          'fillCost': {},
                          'commission': {},
                          'nominal': {}}

    def updateFromFillEvent(self, event):
        self._allFills['orderID'][FilledBook._filledCount] = event.orderID
        self._allFills['time'][FilledBook._filledCount] = event.timeindex
        self._allFills['symbol'][FilledBook._filledCount] = event.symbol
        self._allFills['quantity'][FilledBook._filledCount] = event.quantity
        self._allFills['direction'][FilledBook._filledCount] = event.direction
        self._allFills['fillCost'][FilledBook._filledCount] = event.fillCost
        self._allFills['commission'][FilledBook._filledCount] = event.commission
        self._allFills['nominal'][FilledBook._filledCount] = event.nominal
        FilledBook._filledCount += 1

    def view(self):
        return pd.DataFrame(self._allFills)




