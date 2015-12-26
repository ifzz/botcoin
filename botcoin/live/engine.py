import datetime
import logging
import time

from botcoin import settings
from botcoin.live.data import LiveMarketData
from botcoin.live.portfolio import LivePortfolio
from botcoin.interfaces.ib import IbHandler, IbSocket

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

        self.portfolio = LivePortfolio()
        self.strategy = strategy
        self.portfolio.set_modules(self.market, strategy)

        # Connect to IB tws (edemo/demouser)
        self.if_handler = IbHandler(self.market, self.portfolio)
        self.if_socket = IbSocket(self.if_handler, reconnect_auto=True)
        self.if_socket.connect()

        self.market.if_socket = self.if_socket

        logging.info("Live execution with strategy {}.".format(self.portfolio.strategy))


    def start(self):
        while not self._initial_status_check():
            time.sleep(1)

        self.if_socket.request_portfolio_data(self.portfolio.account_id)

        self.portfolio.market_opened()
        self.strategy.market_opened()

        self.market._subscribe()

        while True:
            self.portfolio.run_cycle()

    def stop(self):
        self.market._stop()

    def _initial_status_check(self):
        try:
            if self.market.updated_at and self.portfolio.account_id:
                pass

            if (self.market.updated_at-self.market.last_historical_bar_at >= datetime.timedelta(days=4)):
                logging.critical('More than 3 days of delta between last historical datetime and current datetime')
                return False

        except Exception as e:
            logging.critical(e)
            return False

        return True
