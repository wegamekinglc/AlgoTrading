# -*- coding: utf-8 -*-
u"""
Created on 2015-11-20

@author: cheng.li
"""

from PyFin.Patterns.Singleton import Singleton


class SettingsFactory(Singleton):

    def __init__(self, forcedBuild=False):
        self._usingCache = False

    @property
    def usingCache(self):
        return self._usingCache

    def enableCache(self):
        self._usingCache = True

    def disableCache(self):
        self._usingCache = False


Settings = SettingsFactory()
