# -*- coding: utf-8 -*-
u"""
Created on 2016-2-4

@author: cheng.li
"""


from AlgoTrading.Events import OrderDirection


def sign(x):
    if x > 0.:
        return 1
    elif x < 0.:
        return -1
    else:
        return 0


def equityCodeToSecurityID(code):
    if code.startswith('6'):
        return code + '.xshg'
    else:
        return code + '.xshe'


def convertDirection(direction):
    if direction == OrderDirection.BUY or direction == OrderDirection.BUY_BACK or direction == 1:
        return 1
    elif direction == OrderDirection.SELL or direction == OrderDirection.SELL_SHORT or direction == -1:
        return -1
    else:
        raise ValueError("unknown direction type: {0}".format(direction))


def categorizeSymbols(symbolList):

    lowSymbols = [s.lower() for s in symbolList]

    stocks = []
    futures = []
    indexes = []
    futures_con = []

    for s in lowSymbols:
        if s.endswith('xshg') or s.endswith('xshe'):
            stocks.append(s)
        elif s.endswith('zicn'):
            indexes.append(s)
        else:
            s_com = s.split('.')
            if len(s_com) < 2:
                raise ValueError("Unknown securitie name {0}. Security names without"
                                 " exchange suffix is not allowed in AlgoTrading".format(s))

            if len(s_com[0]) <= 2:
                futures_con.append(s)
            else:
                futures.append(s)
    return {'stocks': stocks, 'futures': futures, 'indexes': indexes, 'futures_con': futures_con}
