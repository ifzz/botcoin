import numpy as np
import botcoin 

def bbands(prices, k):
    """ returns average, upper band, and lower band"""
    ave = np.mean(prices)
    sd = np.std(prices)
    upband = ave + (sd*k)
    lwband = ave - (sd*k)
    round_dec = botcoin.settings.ROUND_DECIMALS
    return np.round(ave,round_dec), np.round(upband,round_dec), np.round(lwband,round_dec)

class BollingerBands(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2010'
        self.DATE_TO = '2015'

        self.length = self.get_arg(0, 30)
        self.k = self.get_arg(1, 3)

    def close(self, context, s):
        bars = context.market.past_bars(s, self.length)

        if len(bars) >= self.length:
            
            average, upband, lwband = bbands(bars.close, self.k)
            today = context.market.today(s)

            if context.positions[s] > 0:
                if today.high >= average:
                    self.sell(s, average)

            else:
                if today.low <= lwband:
                    self.buy(s, lwband)