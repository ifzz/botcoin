import logging

from botcoin import settings
from botcoin.live.data import LiveMarketData
from botcoin.live.execution import LiveExecution
from botcoin.portfolio import settings, Portfolio

class LiveEngine(object):
    def __init__(self, strategy, data_dir):

        # Single market object will be used for all backtesting instances
        self.market = LiveMarketData(
            data_dir or settings.DATA_DIR, #should come from script loader
            getattr(strategy, 'SYMBOL_LIST', []),
            normalize_prices = getattr(strategy, 'NORMALIZE_PRICES', settings.NORMALIZE_PRICES),
            normalize_volume = getattr(strategy, 'NORMALIZE_VOLUME', settings.NORMALIZE_VOLUME),
            round_decimals = getattr(strategy, 'ROUND_DECIMALS', settings.ROUND_DECIMALS),
        )

        self.portfolio = Portfolio()
        self.portfolio.set_modules(self.market, strategy, LiveExecution())
        self.strategy = strategy



        # print(self.market.past_bars('CBA.AX', 5).bollingerbands(2))

    def start(self):
        logging.info("Live execution with strategy {}.".format(self.portfolio.strategy))

        # while True:
        self.portfolio.run_cycle
