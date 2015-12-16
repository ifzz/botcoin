import datetime
import logging
import time

import pandas as pd
from swigibpy import EPosixClientSocket, EWrapperVerbose, Contract

from botcoin.data import MarketData, Bars


class LiveMarketData(MarketData):
    def __init__(self, csv_dir, symbol_list, normalize_prices, normalize_volume, round_decimals):
        super(LiveMarketData, self).__init__(csv_dir, symbol_list, normalize_prices, normalize_volume, round_decimals)

        # Adds 'df' to 'latest_bars' as list of lists, just as in historical update_bars
        for s in self.symbol_list:
            self.symbol_data[s]['latest_bars'] = self.symbol_data[s]['df'].reset_index()[['index', 'open', 'high', 'low', 'close', 'volume']].values.tolist()

        # Last datetime in historical data which can be from
        # any symbol (doesn't matter as all symbols share same index)
        self.last_datetime = self.symbol_data[self.symbol_list[0]]['latest_bars'][-1][0]


        # Connect to IB tws (edemo/demouser)
        self.ib_handler = IbHandler(self)
        self.live = EPosixClientSocket(self.ib_handler, reconnect_auto=True)
        self.live.eConnect("", 7497, 0)
        self.live.reqCurrentTime()


        time.sleep(2)

        self.live.eDisconnect()

    def current_time(self, timestamp):
        self.datetime = pd.Timestamp(datetime.datetime.fromtimestamp(timestamp))
        if self.datetime-self.last_datetime > datetime.timedelta(days=3):
            logging.critical('More than 3 days of delta between last historical datetime and current datetime')

class IbHandler(EWrapperVerbose):

    def __init__(self, market):
        super(IbHandler, self).__init__()
        self.market = market

    def currentTime(self, current_timestamp):
        """ Response from reqCurrentTime(). """
        self.market.current_time(current_timestamp)

    def managedAccounts(self, openOrderEnd):
        pass

    def nextValidId(self, orderId):
        self.market.next_valid_id = orderId

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
