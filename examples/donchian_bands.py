import numpy as np
import botcoin 

class DonchianStrategy(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2010'
        self.DATE_TO = '2015'

        self.upper = self.args[0]
        self.lower = self.args[1]

    def close(self, context):
        for s in context.market.symbol_list:
            upper_bars = context.market.past_bars(s, self.upper)
            lower_bars = context.market.past_bars(s, self.lower)
            today = context.market.today(s)

            if (len(lower_bars) == self.lower and len(upper_bars) == self.upper):

                upband = max(upper_bars.high)
                lwband = min(lower_bars.low)

                if context.positions[s] > 0:
                    if today.low <= lwband:
                        self.sell(s, lwband)

                else:
                    if today.high >= upband:
                            self.buy(s, upband)


strategies = [DonchianStrategy(100,25)]