import numpy as np
import botcoin

class MovingAverage(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = ['^GSPC']

        self.DATE_FROM = '2010'
        self.DATE_TO = '2014'

        self.INITIAL_CAPITAL = 100000.00
        self.MAX_LONG_POSITIONS = 1
        self.ROUND_LOT_SIZE = 1
        self.COMMISSION_FIXED = 0.0
        self.COMMISSION_MIN = 0.0

        self.fast = self.get_arg(0, 5)
        self.slow = self.get_arg(1, 15)

    def after_close(self):
        for symbol in self.SYMBOL_LIST:
            try:
                slow = self.market.bars(symbol, self.slow).mavg('close')
                fast = self.market.bars(symbol, self.fast).mavg('close')

                if fast > slow:
                    self.buy(symbol)
                if fast < slow:
                    self.sell(symbol)
            except botcoin.BarError as e:
                pass
