import numpy as np
import botcoin

class DonchianStrategy(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = ['AMP','ANZ','BHP','BXB','CBA','CSL','IAG','MQG','NAB','ORG']
        self.YAHOO_SUFFIX = '.AX'

        self.DATE_FROM = '2005'
        self.DATE_TO = '2014'

        self.MAX_SHORT_POSITIONS = 3
        self.MAX_LONG_POSITIONS = 1
        self.MAX_SLIPPAGE = 0.0008

        self.upper = self.get_arg(0, 50)
        self.lower = self.get_arg(1, 5)

    def close(self, s):
        upband = max(self.market.past_bars(s, self.upper).high)
        lwband = min(self.market.past_bars(s, self.lower).low)

        today = self.market.today(s)

        if today.open < upband and today.high > upband and today.open > 2:
            self.short(s, upband)
        if today.open > lwband and today.low < lwband:
            self.cover(s, lwband)
