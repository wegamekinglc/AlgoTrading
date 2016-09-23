# -*- coding: utf-8 -*-
u"""
Created on 2016-9-14

@author: cheng.li
"""

import glob
import datetime as dt
import pandas as pd
import numpy as np
from PyFin.api import CLOSE
from AlgoTrading.api import strategyRunner
from AlgoTrading.api import Strategy
from AlgoTrading.api import DataSource
from AlgoTrading.api import PortfolioType


def data_loader():
    data_folder = r'\\10.63.6.71\sharespace\personal\朱蓓佳\data'
    files = sorted(glob.glob(data_folder + r'\*.csv'))
    dfs = []
    for file in files:
        seps = file.split('-')
        date = seps[1].split('.')[0]
        df = pd.read_csv(file, header=0, names=['timestamp', 'factor'], usecols=[0, 1])
        df['date'] = dt.datetime.strptime(date, '%Y%m%d')

        # 忽略夜盘数据
        df = df[df['timestamp'] >= 0]
        seconds = (df['timestamp'] / 1000000).astype('int64')
        milliseconds = (df['timestamp'] - 1000000 * seconds) / 1000

        seconds = list(seconds.values)
        milliseconds = list(milliseconds.values)

        timedeltas = np.array(
            list(map(lambda x: pd.Timedelta(seconds=x[0], milliseconds=x[1]), zip(seconds, milliseconds))))
        complete_timestamp = df['date'] + timedeltas
        df.index = complete_timestamp
        del df['date']
        dfs.append(df)
        print('{0} is finished'.format(date))

    table = pd.concat(dfs, axis=0)
    table.to_csv('d:/ru_data.csv')


class HighFrequencyRU(Strategy):

    def __init__(self):
        df = pd.read_csv('d:/ru_data.csv', header=0, index_col=0, parse_dates=True)
        self.signals = df.resample('5min').sum().dropna()
        self.date_index = self.signals.index
        self.close = CLOSE()

    def handle_data(self):
        current_time = self.current_datetime
        try:
            location = self.date_index.get_loc(current_time)
        except KeyError:
            return

        if location >= 99:
            histories = self.signals.factor[location-99:location]
            current_level = histories[-1]
            upper = np.percentile(histories, 95)
            lower = np.percentile(histories, 5)

            mid_upper = np.percentile(histories, 75)
            mid_lower = np.percentile(histories, 25)

            if current_level > upper:
                self.order_to('ru.cffex', 1, 1)
            elif current_level < lower:
                self.order_to('ru.cffex', -1, 1)
            #elif mid_lower < current_level < mid_upper:
            #    self.order_to('ru.cffex', 1, 0)

            self.keep('factor', current_level)
            self.keep('factor (95%)', upper)
            self.keep('factor (5%)', lower)
            self.keep('factor (75%)', mid_upper)
            self.keep('factor (25%)', mid_lower)
            self.keep('ru.cffex', self.close['ru.cffex'])
        else:
            return


def run_example():
    universe = ['ru.xsge']

    startDate = dt.datetime(2016, 7, 1)
    endDate = dt.datetime(2016, 8, 31)

    strategyRunner(userStrategy=HighFrequencyRU,
                   symbolList=universe,
                   initialCapital=50000.,
                   startDate=startDate,
                   endDate=endDate,
                   dataSource=DataSource.DXDataCenter,
                   freq=5,
                   saveFile=True,
                   plot=True,
                   portfolioType=PortfolioType.CashManageable,
                   logLevel='info')


if __name__ == "__main__":
    startTime = dt.datetime.now()
    print("Start: %s" % startTime)
    run_example()
    endTime = dt.datetime.now()
    print("End : %s" % endTime)
    print("Elapsed: %s" % (endTime - startTime))

    df = pd.read_csv('d:/ru_data.csv', header=0, index_col=0, parse_dates=True)
    df = df.resample('5min').sum().dropna()
    print(df)




