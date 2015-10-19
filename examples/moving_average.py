import numpy as np
import botcoin 

class TradingStrategy(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2010'
        self.DATE_TO = '2015'

        self.fast = self.args[0] if 0 in self.args else 10
        self.slow = self.args[1] if 1 in self.args else 200

    def logic(self, context):
        for s in context.market.symbol_list:
            slow_prices = context.market.bars(s, self.slow).close
            fast_prices = context.market.bars(s, self.fast).close
            if len(slow_prices) == self.slow and len(fast_prices) == self.fast:
                fast = np.round(np.mean(fast_prices),botcoin.settings.ROUND_DECIMALS)
                slow = np.round(np.mean(slow_prices),botcoin.settings.ROUND_DECIMALS)

                if context.positions[s] > 0:
                    if fast <= slow:
                        self.sell(s)
                else:
                    if fast >= slow:
                        self.buy(s)

strategies = [TradingStrategy(10,250)]