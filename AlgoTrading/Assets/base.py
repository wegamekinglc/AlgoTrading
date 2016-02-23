# -*- coding: utf-8 -*-
u"""
Created on 2015-9-25

@author: cheng.li
"""

from collections import namedtuple

Asset = namedtuple('Asset', 'lag exchange commission multiplier margin settle minimum short price_limit')


class Asset:

    def __init__(self):
        pass
