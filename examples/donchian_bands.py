import numpy as np
import botcoin 

class DonchianStrategy(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2015'
        self.DATE_TO = '2015'

        self.upper = self.get_arg(0, 100)
        self.lower = self.get_arg(1, 25)

    def close(self, context, s):
        upband = max(context.market.past_bars(s, self.upper).high)
        lwband = min(context.market.past_bars(s, self.lower).low)
        
        today = context.market.today(s)

        if today.high > upband:
            self.buy(s, upband)
        if today.low < lwband:
            self.sell(s, lwband)

