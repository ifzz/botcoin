import numpy as np
import botcoin

class DonchianStrategy(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = ['AMP','ANZ','BHP','BXB','CBA','CSL','IAG','MQG','NAB','ORG','QBE','RIO','SCG','SUN','TLS','WBC','WES','WFD','WOW','WPL']
        self.YAHOO_SUFFIX = '.AX'

        self.DATE_FROM = '2010'
        self.DATE_TO = '2014'

        self.MAX_SHORT_POSITIONS = 3
        self.MAX_LONG_POSITIONS = 0
        self.ROUND_LOT_SIZE = 100
        self.MAX_SLIPPAGE = 0.0005

        self.upper = self.get_arg(0, 5)
        self.lower = self.get_arg(1, 5)

    def before_open(self):
        for s in self.SYMBOL_LIST:
            try:
                y = self.market.yesterday(s)
                assert(y.datetime < self.market.updated_at)
                if y.close < 2:
                    self.unsubscribe(s)
            except botcoin.BarValidationError as e:
                pass


    def close(self, s):
        upband = max(self.market.past_bars(s, self.upper).high)
        lwband = min(self.market.past_bars(s, self.lower).low)

        today = self.market.today(s)

        if today.open < upband and today.high > upband:
            self.short(s, upband)
        if today.open > lwband and today.low < lwband:
            self.cover(s, lwband)

strategies = [DonchianStrategy(2,i) for i in botcoin.optimize((5,20,10))]
