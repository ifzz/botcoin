import datetime
import logging
import time

from botcoin import settings
from botcoin.common.errors import DataIsTooOldError
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

        self.portfolio = LivePortfolio(self.market, strategy)
        self.strategy = strategy

        # Connect to IB tws (edemo/demouser)
        self.if_handler = IbHandler(self.market, self.portfolio)
        self.if_socket = IbSocket(self.if_handler, reconnect_auto=True)
        self.if_socket.connect()

        self.portfolio.if_socket = self.if_socket
        self.market.if_socket = self.if_socket

        logging.info("Live execution with strategy {}.".format(self.portfolio.strategy))


    def start(self):
        while not self._initial_status_check():
            time.sleep(1)

        self.if_socket.request_portfolio_data(self.portfolio.account_id)

        self.portfolio.market_opened()

        self.strategy.before_open()

        for s in self.market.symbol_list:
            if self.strategy.is_subscribed_to(s):
                self.market._subscribe_to_market_data(s)

        while True:
            self.portfolio.run_cycle()

    def stop(self):
        self.market._stop()

    def _initial_status_check(self):
        # Checks if the attributes below were set by if_handler
        try:
            if self.market.updated_at and self.portfolio.account_id:
                pass
        except AttributeError:
            return False

        # Checks last local historical data available and verifies if it
        # is too old ( >=4 days delta on monday, >=2 every for the rest)
        now = self.market.updated_at
        delta = now-self.market.last_historical_bar_at
        old_data = False
        if now.weekday() == 0:
            if delta >= datetime.timedelta(days=4):
                old_data = True
        else:
            if delta >= datetime.timedelta(days=2):
                old_data = True
        if old_data: raise DataIsTooOldError

        return True
