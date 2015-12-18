import numpy as np
import botcoin

class MovingAverage(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.YAHOO_SYMBOL_APPENDIX = '.AX'
        self.DATE_FROM = '2015'
        self.DATE_TO = '2015'

        self.fast = self.get_arg(0, 5)
        self.slow = self.get_arg(1, 15)

    def close(self, symbol):
        slow = self.market.bars(symbol, self.slow).mavg('close')
        fast = self.market.bars(symbol, self.fast).mavg('close')

        if fast > slow:
            self.buy(symbol)
        if fast < slow:
            self.sell(symbol)
