import numpy as np
import botcoin

class DonchianStrategy(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.YAHOO_SYMBOL_APPENDIX = '.AX'
        self.DATE_FROM = '2013'
        self.DATE_TO = '2014'
        self.MAX_LONG_POSITIONS = 5

        self.upper = self.get_arg(0, 50)
        self.lower = self.get_arg(1, 5)

    def close(self, s):
        upband = max(self.market.past_bars(s, self.upper).high)
        lwband = min(self.market.past_bars(s, self.lower).low)

        today = self.market.today(s)

        if today.open < upband and today.high > upband and today.open > 2:
            self.buy(s, upband)
        if today.open > lwband and today.low < lwband:
            self.sell(s, lwband)
