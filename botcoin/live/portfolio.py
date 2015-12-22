from botcoin.common.portfolio import Portfolio

class LivePortfolio(Portfolio):

    def check_signal_consistency(self, symbol, exec_price, direction):
        if exec_price < 0:
            logging.critical(NegativeExecutionPriceError(self.strategy, self.market.updated_at, symbol, exec_price))
