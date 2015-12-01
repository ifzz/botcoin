import numpy as np
import botcoin

class BollingerBands(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2013'
        self.DATE_TO = '2014'
        self.MAX_LONG_POSITIONS = 5

        self.length = self.get_arg(0, 5)
        self.k = self.get_arg(1, 2)
        self.price_cuttoff = self.get_arg(2,2)

    def close(self, s):
        average, upband, lwband = self.market.past_bars(s, self.length).bollingerbands(self.k)
        today = self.market.today(s)
        yesterday = self.market.yesterday(s)

        if yesterday.close > self.price_cuttoff and yesterday.close*yesterday.vol > 1500000:

            if self.is_long(s):
                if today.open > average:
                    self.sell(s, today.open)
                elif today.high >= average:
                    self.sell(s, average)

            if self.is_neutral(s):
                if today.open < lwband:
                    self.buy(s, today.open)
                elif today.low <= lwband:
                    self.buy(s, lwband)

# strategies = [BollingerBands(5,2,i) for i in botcoin.optimize((1,10,1))]
