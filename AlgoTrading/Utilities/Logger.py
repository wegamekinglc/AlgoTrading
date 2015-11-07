# -*- coding: utf-8 -*-
u"""
Created on 2015-11-5

@author: cheng.li
"""

import logging


class CustomLogger(object):

    def __init__(self):
        self.logger = logging.getLogger('output')
        self.logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        sh = logging.FileHandler('strategy.log')
        ch.setLevel(logging.INFO)
        sh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        sh.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.addHandler(sh)

    def setLevel(self, type):
        if type.lower() == "info":
            self.logger.setLevel(logging.INFO)
        elif type.lower() == "warning":
            self.logger.setLevel(logging.WARNING)
        elif type.lower() == 'critical':
            self.logger.setLevel(logging.CRITICAL)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

logger = CustomLogger()
