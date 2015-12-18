import datetime
import logging
import time

import pandas as pd
from swigibpy import EPosixClientSocket, EWrapperVerbose, Contract

from botcoin.data import MarketData, Bars


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
        self.last_datetime = self._data[self.symbol_list[0]]['latest_bars'][-1][0]

        # Connect to IB tws (edemo/demouser)
        self.ib_handler = IbHandler(self)
        self.live = EPosixClientSocket(self.ib_handler, reconnect_auto=True)
        self.live.eConnect("", 7497, 0)
        while not self.live.isConnected():
            logging.critical("Failed to connect to tws. Trying again in 5 seconds.")
            time.sleep(5)
            self.live.eConnect("", 7497, 0)

        self.live.reqCurrentTime()

        self.live_symbols = {}
        self.next_ticker_id = 0

        for s in self.symbol_list:
            self.subscribe(s.split('.')[0])

    def _stop(self):
        self.live.eDisconnect()

    def _subscribe(self, symbol):
        c = Contract()
        c.symbol = symbol
        c.secType = self.sec_type
        c.exchange = self.exchange
        c.currency = self.currency

        self.live.reqMktData(self.next_ticker_id, c, "", False, None)

        self.live_symbols[self.next_ticker_id] = symbol
        self.next_ticker_id += 1

    def _update_last_price(self, ticker_id, price):
        print('price', self.live_symbols[ticker_id], price)

    def _update_volume(self, ticker_id, size):
        print('volume', self.live_symbols[ticker_id], size)

    def _update_ask_price(self, ticker_id, price):
        print('ask', self.live_symbols[ticker_id], price)

    def _update_bid_price(self, ticker_id, price):
        print('bid', self.live_symbols[ticker_id], price)

    def _update_high(self, ticker_id, price):
        print('high', self.live_symbols[ticker_id], price)

    def _update_low(self, ticker_id, price):
        print('low', self.live_symbols[ticker_id], price)

    def _update_open(self, ticker_id, price):
        print('open', self.live_symbols[ticker_id], price)

    def _update_last_timestamp(self, ticker_id, timestamp):
        print('last timestamp', self.live_symbols[ticker_id], timestamp)

    def _update_current_time(self, timestamp):
        self.datetime = pd.Timestamp(datetime.datetime.fromtimestamp(timestamp))
        if self.datetime-self.last_datetime >= datetime.timedelta(days=4):
            logging.critical('More than 3 days of delta between last historical datetime and current datetime')

    # Methods that should be referenced by users


class IbHandler(EWrapperVerbose):

    def __init__(self, market):
        super(IbHandler, self).__init__()
        self.market = market

    # IB related methods
    def currentTime(self, current_timestamp):
        """ Response from reqCurrentTime(). """
        self.market._update_current_time(current_timestamp)

    def managedAccounts(self, openOrderEnd):
        pass

    def nextValidId(self, orderId):
        self.market.next_valid_id = orderId

    """
        https://www.interactivebrokers.com/en/software/api/apiguide/tables/tick_types.htm
        0   BID_SIZE	tickSize()
        1   BID_PRICE	tickPrice()
        2   ASK_PRICE	tickPrice()
        3   ASK_SIZE	tickSize()
        4   LAST_PRICE	tickPrice()
        5   LAST_SIZE	tickSize()
        6   HIGH	tickPrice()
        7   LOW	tickPrice()
        8   VOLUME	tickSize()
        9   CLOSE_PRICE	tickPrice()
        14  OPEN_TICK	tickPrice()
        21  AVG_VOLUME	tickSize()
        37  MARK_PRICE	tickPrice()
        45  LAST_TIMESTAMP	tickString()
        46  SHORTABLE	tickString()
    """

    def tickString(self, ticker_id, tick_type, value):
        if tick_type == 45:  # LAST_TIMESTAMP
            self.market._update_last_timestamp(ticker_id, value)

    def tickSize(self, ticker_id, tick_type, size):
        if tick_type == 8:  # VOLUME
            self.market._update_volume(ticker_id, size)

    def tickPrice(self, ticker_id, tick_type, price, canAutoExecute):
        if tick_type == 4:  # LAST_PRICE
            self.market._update_last_price(ticker_id, price)

        elif tick_type == 1:  # BID_PRICE
            self.market._update_bid_price(ticker_id, price)

        elif tick_type == 2:  # ASK_PRICE
            self.market._update_ask_price(ticker_id, price)
        #
        elif tick_type == 6:  # HIGH
            print('HIGH', self.market.live_symbols[ticker_id], price)

        elif tick_type == 7:  # LOW
            print('LOW', self.market.live_symbols[ticker_id], price)

        elif tick_type == 14:  # OPEN_TICK
            print('OPEN_TICK', self.market.live_symbols[ticker_id], price)


    # def orderStatus(self, id, status, filled, remaining, avgFillPrice, permId,
    #                 parentId, lastFilledPrice, clientId, whyHeld):
    #     pass
    #
    # def openOrder(self, orderID, contract, order, orderState):
    #     pass
    #
    # def openOrderEnd(self):
    #     pass
    #
    # def contractDetailsEnd(self, reqId):
    #     print("Contract details request complete, (request id %i)" % reqId)
    #
    # def contractDetails(self, reqId, contractDetails):
    #     pass
