import datetime

import pandas as pd
from swigibpy import EPosixClientSocket, EWrapperVerbose, Contract

class IbHandler(EWrapperVerbose):

    def __init__(self, market, portfolio, execution):
        super(IbHandler, self).__init__()
        self.market = market
        self.portfolio = portfolio
        self.execution = execution

    # IB related methods
    def currentTime(self, current_timestamp):
        """ Response from reqCurrentTime(). """
        self.datetime = pd.Timestamp(datetime.datetime.fromtimestamp(current_timestamp))

        self.market.datetime = self.datetime
        if self.datetime-self.market.last_datetime >= datetime.timedelta(days=4):
            logging.critical('More than 3 days of delta between last historical datetime and current datetime')

    def managedAccounts(self, openOrderEnd):
        pass

    def nextValidId(self, orderId):
        pass
        # self.market.next_valid_id = orderId

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
            self.market._update_high_price(ticker_id, price)

        elif tick_type == 7:  # LOW
            self.market._update_low_price(ticker_id, price)

        elif tick_type == 14:  # OPEN_TICK
            self.market._update_open_price(ticker_id, price)

    def tickGeneric(self, ticker_id, tick_type, value):
        if tick_type == 49:
            logging.warning("Trading halted for {}".format(self.ticker_dict(ticker_id)))

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
