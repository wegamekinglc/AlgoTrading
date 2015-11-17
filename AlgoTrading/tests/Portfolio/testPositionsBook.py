# -*- coding: utf-8 -*-
u"""
Created on 2015-11-16

@author: cheng.li
"""

import unittest
import datetime as dt
from AlgoTrading.Portfolio.PositionsBook import StocksPositionsBook
from AlgoTrading.Assets import XSHGStock
from AlgoTrading.Assets import IndexFutures


class TestPositionsBook(unittest.TestCase):

    def setUp(self):
        assets = {'600000': XSHGStock,
                  'IF1501': IndexFutures}
        self.positionsBook = StocksPositionsBook(assets)

    def testUpdatedFromOrder(self):
        self.positionsBook.updatePositionsByOrder('600000', dt.date(2015, 11, 16), 100, 1)
        self.assertEqual(self.positionsBook._allPositions, {})

    def testUpdatedFromFillEvent(self):
        self.positionsBook.updatePositionsByFill('600000', dt.date(2015, 11, 16), 100, 1)
        self.assertEqual(self.positionsBook._allPositions['600000'], ([dt.date(2015, 11, 16)],
                                                                      [100],
                                                                      [0],
                                                                      [1]))

    def testUpdatedFromOrderWithNonEmptyPositionBook(self):
        self.positionsBook.updatePositionsByFill('600000', dt.date(2015, 11, 13), 300, 1)
        self.assertEqual(self.positionsBook.avaliableForTrade('600000', dt.date(2015, 11, 16)), (300, 0))

        self.positionsBook.updatePositionsByOrder('600000', dt.date(2015, 11, 16), 100, -1)
        self.assertEqual(self.positionsBook._allPositions['600000'],  ([dt.date(2015, 11, 13)],
                                                                       [300],
                                                                       [100],
                                                                       [1]))
        self.assertEqual(self.positionsBook.avaliableForTrade('600000', dt.date(2015, 11, 16)), (200, 0))

    def testUpdatedSellShortOrderWithShortForbiddenAsset(self):
        with self.assertRaises(ValueError):
            self.positionsBook.updatePositionsByOrder('600000', dt.date(2015, 11, 16), 100, -1)

    def testUpdatedSellShortOrderWithShortAllowedAsset(self):
        self.positionsBook.updatePositionsByOrder('IF1501', dt.date(2015, 11, 16), 100, -1)

    def testUpdatedFromFillWithBothLongAndShot(self):
        self.positionsBook.updatePositionsByOrder('IF1501', dt.date(2015, 11, 13), 1, -1)
        self.positionsBook.updatePositionsByFill('IF1501', dt.date(2015, 11, 13), 1, -1)
        self.assertEqual(self.positionsBook.avaliableForTrade('IF1501', dt.date(2015, 11, 13)), (0, 1))
        self.positionsBook.updatePositionsByOrder('IF1501', dt.date(2015, 11, 16), 2, 1)
        self.positionsBook.updatePositionsByFill('IF1501', dt.date(2015, 11, 16), 1, 1)
        self.positionsBook.updatePositionsByFill('IF1501', dt.date(2015, 11, 16), 1, 1)
        self.assertEqual(self.positionsBook._allPositions['IF1501'], ([dt.date(2015, 11, 16)],
                                                                       [1],
                                                                       [0],
                                                                       [1]))
