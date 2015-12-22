import datetime
import logging
import time

import pandas as pd
from swigibpy import Contract

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

        self.ticker_dict = {}
        self.next_ticker_id = 0

    def _stop(self):
        self.if_socket.eDisconnect()

    def _subscribe(self, symbol):
        c = Contract()
        c.symbol = symbol
        c.secType = self.sec_type
        c.exchange = self.exchange
        c.currency = self.currency

        self.if_socket.reqMktData(self.next_ticker_id, c, "", False, None)

        self.ticker_dict[self.next_ticker_id] = symbol
        self.next_ticker_id += 1

    def _update_last_price(self, ticker_id, price):
        symbol = self.ticker_dict[ticker_id]

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

    def _update_volume(self, ticker_id, size):
        self._data[self.ticker_dict[ticker_id]]['volume'] = size

    def _update_ask_price(self, ticker_id, price):
        self._data[self.ticker_dict[ticker_id]]['ask'] = price

    def _update_bid_price(self, ticker_id, price):
        self._data[self.ticker_dict[ticker_id]]['bid'] = price

    def _update_high_price(self, ticker_id, price):
        self._data[self.ticker_dict[ticker_id]]['high'] = price

    def _update_low_price(self, ticker_id, price):
        self._data[self.ticker_dict[ticker_id]]['low'] = price

    def _update_open_price(self, ticker_id, price):
        self._data[self.ticker_dict[ticker_id]]['open'] = price

    def _update_last_timestamp(self, ticker_id, timestamp):
        self._data[self.ticker_dict[ticker_id]]['updated_at'] = timestamp
        self._update_datetime(int(timestamp))

    def _update_datetime(self, timestamp):
        self.updated_at = pd.Timestamp(datetime.datetime.fromtimestamp(timestamp))
