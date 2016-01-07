import botcoin

class MovingAverage(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = botcoin.settings.ASX_200

        self.DATE_FROM = '2015'
        self.DATE_TO = '2015'

        self.fast = self.get_arg(0, 5)
        self.slow = self.get_arg(1, 15)

    def after_close(self):
        for symbol in self.SYMBOL_LIST:
            try:
                slow = self.market.bars(symbol, self.slow).mavg('close')
                fast = self.market.bars(symbol, self.fast).mavg('close')

                if fast > slow:
                    self.buy(symbol)
                if fast < slow:
                    self.sell(symbol)
            except botcoin.BarError as e:
                pass


# strategies = [MovingAverage(5,i) for i in botcoin.optimize((5,100,5))]
