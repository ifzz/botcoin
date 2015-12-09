import logging

from botcoin import settings
from botcoin.data import MarketData
from botcoin.live.execution import LiveExecution
from botcoin.portfolio import settings, Portfolio

class LiveEngine(object):
    def __init__(self, strategy, data_dir):
        self.portfolio = Portfolio()
        self.portfolio.set_modules(self.market, strategy, LiveExecution())

        # Single market object will be used for all backtesting instances
        self.market = MarketData(
            data_dir or settings.DATA_DIR, #should come from script loader
            getattr(strategy, 'SYMBOL_LIST', []),
            normalize_prices = getattr(strategies[0], 'NORMALIZE_PRICES', settings.NORMALIZE_PRICES),
            normalize_volume = getattr(strategies[0], 'NORMALIZE_VOLUME', settings.NORMALIZE_VOLUME),
            round_decimals = getattr(strategies[0], 'ROUND_DECIMALS', settings.ROUND_DECIMALS),
        )

        # print(self.market.symbol_data['CBA.AX']['df'][-1])
        self.strategy = strategy


    def start(self):
        logging.info("Live execution with strategy {}.".format(self.portfolio.strategy))

        # while True:
        self.portfolio.run_cycle
