# -*- coding: utf-8 -*-
u"""
Created on 2015-9-25

@author: cheng.li
"""

class Asset(object):

    @classmethod
    def props(cls):
        return {i: cls.__dict__[i] for i in cls.__dict__.keys() if i[:1] != '_'}

    @classmethod
    def __str__(cls):
        return cls.props().__str__()
