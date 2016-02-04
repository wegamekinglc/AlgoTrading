# -*- coding: utf-8 -*-
u"""
Created on 2015-11-20

@author: cheng.li
"""

from PyFin.Patterns.Singleton import Singleton
from AlgoTrading.Enums import DataSource


class SettingsFactory(Singleton):

    def __init__(self, forcedBuild=False):
        self._usingCache = False
        self._data_source = DataSource.DXDataCenter

    @property
    def usingCache(self):
        u"""

        获取DataAPI缓存功能是否开启的标识

        :return: bool
        """
        return self._usingCache

    def enableCache(self):
        u"""

        开启使用DataAPI的缓存功能

        :return: None
        """
        self._usingCache = True

    def disableCache(self):
        u"""

        禁止使用DataAPI的缓存功能

        :return:
        """
        self._usingCache = False

    def set_source(self, data_source):
        u"""

        设置全局数据源

        :param data_source: 数据源枚举类型
        :return: None
        """
        self._data_source = data_source

    @property
    def data_source(self):
        u"""

        返回当前全局数据源

        :return: DataSource
        """
        return self._data_source


Settings = SettingsFactory()
