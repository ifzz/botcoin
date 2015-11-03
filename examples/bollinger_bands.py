import numpy as np
import botcoin 

class BollingerBands(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2015'
        self.DATE_TO = '2015'

        self.length = self.get_arg(0, 30)
        self.k = self.get_arg(1, 3)

    def close(self, context, s):
        average, upband, lwband = context.market.past_bars(s, self.length).bollingerbands(self.k)
        today = context.market.today(s)

        if today.low <= lwband:
            self.buy(s, lwband)
        if today.high >= average:
            self.sell(s, average)