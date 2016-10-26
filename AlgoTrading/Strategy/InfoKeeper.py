# -*- coding: utf-8 -*-
u"""
Created on 2015-11-25

@author: cheng.li
"""


import pandas as pd


class InfoKepper(object):
    # for user to keep the information he needed
    def __init__(self):
        self.info = {}
        self.labels = []

    def attach(self, time, label, value):
        if label not in self.info:
            self.info[label] = ([], [])
            self.labels.append(label)

        self.info[label][0].append(time)
        self.info[label][1].append(value)

    def view(self):
        seriesList = []
        for s in self.labels:
            series = pd.Series(self.info[s][1], index=self.info[s][0])
            seriesList.append(series)

        if seriesList:
            res = pd.concat(seriesList, axis=1, join='outer')
            res.fillna(method='pad', inplace=True)
            res.set_axis(axis=1, labels=self.labels)
        else:
            res = pd.DataFrame()
        return res


class PlotInfoKeeper(object):

    def __init__(self):
        self.info = {}
        self.labels = []
        self.markers = []
        self.line_styles = []

    def attach(self, time, label, value, marker=None, line_style='solid'):
        if label not in self.info:
            self.info[label] = ([], [])
            self.labels.append(label)
            self.markers.append(marker)
            self.line_styles.append(line_style)

        self.info[label][0].append(time)
        self.info[label][1].append(value)

    def curves(self):
        seriesList = []
        for i, s in enumerate(self.labels):
            series = pd.Series(self.info[s][1], index=self.info[s][0])
            line_style = self.line_styles[i]
            if line_style:
                series.fillna(method='pad', inplace=True)
            seriesList.append(series)

        return (self.markers, self.line_styles, self.labels, seriesList)
