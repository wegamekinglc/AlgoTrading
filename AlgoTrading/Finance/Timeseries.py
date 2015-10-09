# -*- coding: utf-8 -*-
u"""
Created on 2015-10-9

@author: cheng.li
"""

import pandas as pd
import datetime as dt
from math import sqrt
from PyFin.Math.Accumulators import MovingDrawDown

APPROX_BDAYS_PER_YEAR = 252.


def cumReturn(returns):

    dfCum = returns.cumsum()
    return dfCum


def aggregateReturns(returns, convert='daily'):

    def cumulateReturns(x):
        return cumReturn(x)[-1]

    if convert == 'daily':
        return returns.groupby(
            lambda x: dt.datetime(x.year, x.month, x.day)).apply(cumulateReturns)
    else:
        ValueError('convert must be daily, weekly, monthly or yearly')


def drawDown(returns):

    ddCal = MovingDrawDown(len(returns), 'ret')
    ddSeries = [0.0] * len(returns)
    for i, value in enumerate(returns):
        ddCal.push({'ret': value})
        ddSeries[i] = ddCal.value[0]

    return pd.Series(ddSeries, returns.index)


def annualReturn(returns):
    return returns.mean() * APPROX_BDAYS_PER_YEAR


def annualVolatility(returns):
    return returns.std() * sqrt(APPROX_BDAYS_PER_YEAR)


def sortinoRatio(returns):
    annualRet = annualReturn(returns)
    annualNegativeVol = annualVolatility(returns[returns < 0.0])
    return annualRet / annualNegativeVol


def sharpRatio(returns):
    annualRet = annualReturn(returns)
    annualVol = annualVolatility(returns)
    return annualRet / annualVol



