# -*- coding: utf-8 -*-

import datetime as dt
from AlgoTrading.api import Strategy
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import DataSource
from PyFin.api import MACD
from PyFin.api import RSI
from PyFin.api import EMA


class MovingAverageCrossStrategy(Strategy):
    def __init__(self, fast, slow, MACDLength, RSILength):
        MACDValue = MACD(fast, slow, 'close')
        AvgMACD = EMA(MACDLength, MACDValue)
        self.MACDDiff = MACDValue - AvgMACD
        self.RSI = RSI(RSILength, 'close')

    def handle_data(self):

        if self.MACDDiff['000300.zicn'] > 2. \
                and self.RSI['000300.zicn'] > 51. \
                and self.secPos['000300.zicn'] != 1:
            self.order_to('000300.zicn', 1, 1)
        elif self.MACDDiff['000300.zicn'] < -2. \
                and self.RSI['000300.zicn'] < 49 \
                and self.secPos['000300.zicn'] != -1:
            self.order_to('000300.zicn', -1, 1)
            
        self.keep('macd_diff', self.MACDDiff['000300.zicn'])
        self.keep('rsi', self.MACDDiff['000300.zicn'])


def run_example():
    universe = ['000300.zicn']
    startDate = dt.datetime(2012, 1, 1)
    endDate = dt.datetime(2016, 1, 12)

    return strategyRunner(userStrategy=MovingAverageCrossStrategy,
                          strategyParameters=(36, 78, 27, 42),
                          symbolList=universe,
                          startDate=startDate,
                          endDate=endDate,
                          dataSource=DataSource.DXDataCenter,
                          freq=5,
                          logLevel='critical',
                          plot=True)


if __name__ == "__main__":
    
    import pickle
    res = run_example()
    
    with open('data/data.dat', 'wb') as f:
        pickle.dump(res, f)