import logging
import time

from swigibpy import EPosixClientSocket, EWrapperVerbose, Contract

class IbSocket(EPosixClientSocket):
    def connect(self):
        self.eConnect("", 7497, 0)
        while not self.isConnected():
            logging.critical("Failed to connect to tws. Trying again in 5 seconds.")
            time.sleep(5)
            self.eConnect("", 7497, 0)
        self.reqCurrentTime()
        time.sleep(1)  # Waiting for initial requests to come through

    def request_portfolio_data(self, account_id):
        self.reqAccountUpdates(True, account_id)


class IbHandler(EWrapperVerbose):

    def __init__(self, market, portfolio, execution):
        super(IbHandler, self).__init__()
        self.market = market
        self.portfolio = portfolio
        self.execution = execution

    # Portfolio section
    def currentTime(self, timestamp):
        """ Response from reqCurrentTime(). """
        self.market._update_datetime(timestamp)

    def managedAccounts(self, accountId):
        self.portfolio.account_id = accountId

    def updateAccountValue(self, key, value, currency, account):
        if key == 'CashBalance':
            self.portfolio.cash_balance = float(value)
        elif key == 'NetLiquidation':
            self.portfolio.net_liquidation = float(value)
        elif key == 'StockMarketValue':
            self.portfolio.stock_market_value = float(value)
        elif key == 'UnrealizedPnL':
            self.portfolio.unrealized_pnl = float(value)

    def updatePortfolio(self, contract, position, market_price, market_value,
                        average_cost, unrealized_pnl, realized_pnl, account):
        print(contract.symbol, position, market_value, unrealized_pnl)

    def updateAccountTime(self, timestamp):
        self.portfolio.updated_at = timestamp

    def accountDownloadEnd(self, account):
        pass

    # Market section
    # https://www.interactivebrokers.com/en/software/api/apiguide/tables/tick_types.htm
    # 0   BID_SIZE	tickSize()
    # 1   BID_PRICE	tickPrice()
    # 2   ASK_PRICE	tickPrice()
    # 3   ASK_SIZE	tickSize()
    # 4   LAST_PRICE	tickPrice()
    # 5   LAST_SIZE	tickSize()
    # 6   HIGH	tickPrice()
    # 7   LOW	tickPrice()
    # 8   VOLUME	tickSize()
    # 9   CLOSE_PRICE	tickPrice()
    # 14  OPEN_TICK	tickPrice()
    # 21  AVG_VOLUME	tickSize()
    # 37  MARK_PRICE	tickPrice()
    # 45  LAST_TIMESTAMP	tickString()
    # 46  SHORTABLE	tickString()

    def tickString(self, ticker_id, tick_type, value):
        if tick_type == 45:  # LAST_TIMESTAMP
            self.market._update_last_timestamp(ticker_id, value)

    def tickSize(self, ticker_id, tick_type, size):
        if tick_type == 8:  # VOLUME
            self.market._update_volume(ticker_id, size)

    def tickPrice(self, ticker_id, tick_type, price, can_auto_execute):
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
            logging.warning("Trading halted for {}".format(self.market.ticker_dict(ticker_id)))


    # Execution section
    def nextValidId(self, order_id):
        pass
        # self.market.next_valid_id = orderId

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
