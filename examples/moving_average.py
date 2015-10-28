import numpy as np
import botcoin 

class MovingAverage(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2010'
        self.DATE_TO = '2015'

        self.fast = self.args[0]
        self.slow = self.args[1]

    def close(self, context):
        for s in context.market.symbol_list:
            slow_prices = context.market.bars(s, self.slow)
            fast_prices = context.market.bars(s, self.fast)
            if len(slow_prices) == self.slow and len(fast_prices) == self.fast:
                fast = np.round(np.mean(fast_prices.close),botcoin.settings.ROUND_DECIMALS)
                slow = np.round(np.mean(slow_prices.close),botcoin.settings.ROUND_DECIMALS)

                if context.positions[s] > 0:
                    if fast <= slow:
                        self.sell(s, context.market.today(s).close)
                else:
                    if fast >= slow:
                        self.buy(s, context.market.today(s).close)

strategies = [MovingAverage(10,250)]