import numpy as np
import botcoin 

class MovingAverage(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200
        self.DATE_FROM = '2015'
        self.DATE_TO = '2015'

        self.fast = self.get_arg(0, 50)
        self.slow = self.get_arg(1, 70)

    def close(self, context, symbol):
        # for symbol in context.market.symbol_list:
        slow_prices = context.market.bars(symbol, self.slow)
        fast_prices = context.market.bars(symbol, self.fast)
        fast = np.round(np.mean(fast_prices.close),botcoin.settings.ROUND_DECIMALS)
        slow = np.round(np.mean(slow_prices.close),botcoin.settings.ROUND_DECIMALS)

        if context.positions[symbol] > 0:
            if fast <= slow:
                self.sell(symbol, context.market.today(symbol).close)
        else:
            if fast >= slow:
                self.buy(symbol, context.market.today(symbol).close)