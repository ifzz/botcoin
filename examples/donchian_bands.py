import numpy as np
import botcoin

class DonchianStrategy(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2013'
        self.DATE_TO = '2014'

        self.upper = self.get_arg(0, 100)
        self.lower = self.get_arg(1, 25)

    def close(self, s):
        upband = max(self.market.past_bars(s, self.upper).high)
        lwband = min(self.market.past_bars(s, self.lower).low)

        today = self.market.today(s)

        if today.high > upband:
            self.buy(s, upband)
        if today.low < lwband:
            self.sell(s, lwband)

a = []
for i in np.arange(10,200,20):
    for j in np.arange(5,50,5):
        a.append((i,j))
strategies = [DonchianStrategy(i,j) for i,j in a]
