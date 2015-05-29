#!/usr/bin/env python

class OnePositionPortfolio(object):
    def __init__(self, data, initial_capital=100000.0):
        self.data = data
        self.initial_capital = initial_capital