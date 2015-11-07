# -*- coding: utf-8 -*-
u"""
Created on 2015-11-7

@author: cheng.li
"""


def transfromDFtoDict(df):

    index = df.index.to_pydatetime()
    columns = df.columns
    data = df.as_matrix()
    result = {}
    for i, k in enumerate(index):
        result[k] = {}
        for j, c in enumerate(columns):
            result[k][c] = data[i][j]
    return result
