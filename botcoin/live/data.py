import datetime
import logging
import time

import pandas as pd

from botcoin.common.data import MarketData, Bars
from botcoin.common.events import MarketEvent

class LiveMarketData(MarketData):
    def __init__(self, csv_dir, symbol_list, normalize_prices, normalize_volume, round_decimals,
                 exchange, sec_type, currency):
        super(LiveMarketData, self).__init__(csv_dir, symbol_list, normalize_prices, normalize_volume, round_decimals)

        self.exchange = exchange
        self.sec_type = sec_type
        self.currency = currency

        # Adds 'df' to 'latest_bars' as list of lists, just as in historical update_bars
        for s in self.symbol_list:
            self._data[s]['latest_bars'] = self._data[s]['df'].reset_index()[['index', 'open', 'high', 'low', 'close', 'volume']].values.tolist()

        # Last datetime in historical data which can be from
        # any symbol (doesn't matter as all symbols share same index)
        self.last_historical_bar_at = self._data[self.symbol_list[0]]['latest_bars'][-1][0]

    def _stop(self):
        self.if_socket.eDisconnect()

    def _subscribe(self):
        [self.if_socket.subscribe_market_data(s, self.exchange, self.sec_type, self.currency) for s in self.symbol_list]

    def _update_last_price(self, symbol, price):

        self._data[symbol]['last_price'] = price

        if not 'high' in self._data[symbol]:
            self._data[symbol]['high'] = price
        elif price > self._data[symbol]['high']:
            self._data[symbol]['high'] = price

        if not 'low' in self._data[symbol]:
            self._data[symbol]['low'] = price
        elif price < self._data[symbol]['low']:
            self._data[symbol]['low'] = price

        if not 'open' in self._data[symbol]:
            self._data[symbol]['open'] = price

        self._relay_market_event(MarketEvent('during', symbol))

    def _update_volume(self, symbol, size):
        self._data[symbol]['volume'] = size

    def _update_ask_price(self, symbol, price):
        self._data[symbol]['ask'] = price

    def _update_bid_price(self, symbol, price):
        self._data[symbol]['bid'] = price

    def _update_high_price(self, symbol, price):
        self._data[symbol]['high'] = price

    def _update_low_price(self, symbol, price):
        self._data[symbol]['low'] = price

    def _update_open_price(self, symbol, price):
        self._data[symbol]['open'] = price

    def _update_last_timestamp(self, symbol, timestamp):
        self._data[symbol]['updated_at'] = timestamp
        self._update_datetime(int(timestamp))

    def _update_datetime(self, timestamp):
        self.updated_at = pd.Timestamp(datetime.datetime.fromtimestamp(timestamp))
