import numpy as np
import botcoin

class BollingerBands(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_50
        self.YAHOO_SYMBOL_APPENDIX = '.AX'
        self.DATE_FROM = '2013'
        self.DATE_TO = '2014'
        self.MAX_LONG_POSITIONS = 5

        self.length = self.get_arg(0, 30)
        self.k = self.get_arg(1, 2)

    def close(self, s):
        average, upband, lwband = self.market.past_bars(s, self.length).bollingerbands(self.k)
        today = self.market.today(s)

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
