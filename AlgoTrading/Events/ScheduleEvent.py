# -*- coding: utf-8 -*-
u"""
Created on 2016-2-23

@author: cheng.li
"""

from AlgoTrading.Events.Event import Event


class DayBeginEvent(Event):

    def __init__(self, timeIndex):
        self.type = 'DAYBEGIN'
        self.timeIndex = timeIndex
