# -*- coding: utf-8 -*-
u"""
Created on 2016-2-4

@author: cheng.li
"""

import re
from AlgoTrading.Events import OrderDirection



_windIndexSuffixDict = {'000[0-9]*': 'sh', # 上证指数、中证指数
                          '399[0-9]*': 'sz', # 深证指数、国证规模指数
                          '899[0-9]*': 'csi', # 三板指数
                        '80[0-9]*': 'si', # 申万行业指数
                        'CI[0-9]*': 'wi'} # 中信行业指数


_windExchangeDict = {'xshg': 'sh',
                 'xshe': 'sz',
                 'ccfx': 'cfe',# 中国金融期货交易所
                 'xsge': 'shf', # 上海期货交易所
                 'xzce': 'czc', # 郑州商品交易所
                 'xdce':'dce'} # 大连期货交易所



def convert2WindSymbol(symbol):
    symbolComp = symbol.split('.')
    if symbolComp[1] == 'zicn':
        for patterns in _windIndexSuffixDict:
            if re.match(patterns, symbolComp[0]):
                return symbolComp[0] + '.'+ _windIndexSuffixDict[patterns]
        raise ValueError('{0} and {1} pair is not recognized'.format(symbolComp[0], symbolComp[1]))
    else:
        return symbolComp[0] + '.' + _windExchangeDict[symbolComp[1]]


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
