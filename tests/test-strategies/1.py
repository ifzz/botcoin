import numpy as np
import botcoin

class BollingerBands(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = ['AMP','ANZ','BHP','BXB','CBA','CSL','IAG','MQG','NAB','ORG','QBE','RIO','SCG','SUN','TLS','WBC','WES','WFD','WOW','WPL']
        self.YAHOO_SUFFIX = '.AX'

        self.DATE_FROM = '2010'
        self.DATE_TO = '2014'

        self.INITIAL_CAPITAL = 100000.00
        self.MAX_LONG_POSITIONS = 1
        self.ROUND_LOT_SIZE = 1
        self.ROUND_DECIMALS_BELOW_ONE = 2

        self.length = self.get_arg(0, 5)
        self.k = self.get_arg(1, 3)

    def before_open(self):
        [self.subscribe(s) for s in ['QBE','RIO','SCG','SUN','TLS','WBC','WES','WFD','WOW','WPL']]

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
