import numpy as np
import botcoin

class MovingAverage(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2015'
        self.DATE_TO = '2015'

        self.fast = self.get_arg(0, 50)
        self.slow = self.get_arg(1, 70)

    def close(self, context, symbol):
        slow = context.market.bars(symbol, self.slow).mavg('close')
        fast = context.market.bars(symbol, self.fast).mavg('close')

        if fast > slow:
            self.buy(symbol)
        else:
            self.sell(symbol)
