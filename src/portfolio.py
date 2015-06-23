#!/usr/bin/env python

class OnePositionPortfolio(object):

    def __init__(self, initial_capital=100000.0):
        self.initial_capital = initial_capital
        
        self.results = []
        self.buy_price = 0
        self.sell_price = 0

    def generate_orders(self, event, bars):
        if event.signal_type == 'LONG':
            self.buy_price = bars.close()[0]

        elif event.signal_type == 'EXIT':
            self.sell_price = bars.close()[0]
            self.results.append(self.sell_price-self.buy_price)

    def performance(self):
        return sum(self.results)