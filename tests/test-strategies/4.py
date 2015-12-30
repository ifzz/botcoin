import botcoin

class MovingAverage(botcoin.Strategy):
    def initialize(self):
        self.SYMBOL_LIST = ['AMP','ANZ','BHP','BXB','CBA','CSL','IAG','MQG','NAB','ORG','QBE','RIO','SCG','SUN','TLS','WBC','WES','WFD','WOW','WPL']

        self.DATE_FROM = '2014'
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
            except botcoin.BarValidationError as e:
                pass
