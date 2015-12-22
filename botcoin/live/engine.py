import logging
import time

from swigibpy import EPosixClientSocket

from botcoin import settings
from botcoin.live.data import LiveMarketData
from botcoin.live.execution import LiveExecution
from botcoin.common.portfolio import settings, Portfolio
from botcoin.interfaces.ib import IbHandler

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
        self.strategy = strategy
        self.execution = LiveExecution()
        self.portfolio.set_modules(self.market, strategy, self.execution)

        # Connect to IB tws (edemo/demouser)
        self.ib_handler = IbHandler(self.market, self.strategy, self.execution)
        self.ib_client = EPosixClientSocket(self.ib_handler, reconnect_auto=True)
        self.ib_client.eConnect("", 7497, 0)
        while not self.ib_client.isConnected():
            logging.critical("Failed to connect to tws. Trying again in 5 seconds.")
            time.sleep(5)
            self.ib_client.eConnect("", 7497, 0)
        self.ib_client.reqCurrentTime()

        self.market.ib_client = self.ib_client

        logging.info("Live execution with strategy {}.".format(self.portfolio.strategy))
        time.sleep(1)

    def start(self):
        self.portfolio.market_opened()
        self.strategy.market_opened()

        for s in self.market.symbol_list:
            self.market._subscribe(s.split('.')[0])

        while True:
            self.portfolio.run_cycle()

    def stop(self):
        self.market._stop()
