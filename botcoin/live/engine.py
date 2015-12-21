import logging
import time

from botcoin import settings
from botcoin.live.data import LiveMarketData
from botcoin.live.execution import LiveExecution
from botcoin.common.portfolio import settings, Portfolio

class LiveEngine(object):
    def __init__(self, strategy, data_dir):

        # Single market object will be used for all backtesting instances
        self.market = LiveMarketData(
            data_dir or settings.DATA_DIR, #should come from script loader
            getattr(strategy, 'SYMBOL_LIST', []),
            normalize_prices = getattr(strategy, 'NORMALIZE_PRICES', settings.NORMALIZE_PRICES),
            normalize_volume = getattr(strategy, 'NORMALIZE_VOLUME', settings.NORMALIZE_VOLUME),
            round_decimals = getattr(strategy, 'ROUND_DECIMALS', settings.ROUND_DECIMALS),
            exchange = getattr(strategy, 'EXCHANGE', settings.EXCHANGE),
            sec_type = getattr(strategy, 'SEC_TYPE', settings.SEC_TYPE),
            currency = getattr(strategy, 'CURRENCY', settings.CURRENCY),
        )

        self.portfolio = Portfolio()
        self.portfolio.set_modules(self.market, strategy, LiveExecution())
        self.strategy = strategy

        logging.info("Live execution with strategy {}.".format(self.portfolio.strategy))

    def start(self):
        time.sleep(1)  # a second for first IB requests to come through
        self.portfolio.market_opened()
        while True:
            self.portfolio.run_cycle()

    def stop(self):
        self.market._stop()
