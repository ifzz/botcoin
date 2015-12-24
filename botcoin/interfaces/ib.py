import logging
import sys
import time

from swigibpy import EPosixClientSocket, EWrapperVerbose, Contract, ExecutionFilter

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
        # self.reqPositions()
        self.reqAutoOpenOrders(True)


class IbHandler(EWrapperVerbose):

    def __init__(self, market, portfolio):
        super(IbHandler, self).__init__()
        self.market = market
        self.portfolio = portfolio

    # -------------- Portfolio section --------------

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

    def updatePortfolio(self, contract, position, avg_market_price, market_value,
                        average_cost, unrealized_pnl, realized_pnl, account):

        # IBKR, 500, market_price 41.4049988, market_value 20702.5, unrealized_pnl -10.0, realized_pnl -42.5
        # IBKR, 400, market_price 41.4049988, market_value 16562.0, unrealized_pnl -8.0, realized_pnl -46.0
        # IBKR, 100, market_price 41.420002, market_value 4142.0, unrealized_pnl -0.5, realized_pnl -58.0
        # IBKR, 0, market_price 41.420002, market_value 0.0, unrealized_pnl 0.0, realized_pnl -62.0
        # IBKR, 0, market_price 41.43999865, market_value 0.0, unrealized_pnl 0.0, realized_pnl -62.0
        print("{}, {}, market_price {}, market_value {}, average_cost {}, unrealized_pnl {}, realized_pnl {} ".format(contract.symbol, position, avg_market_price, market_value, average_cost, unrealized_pnl, realized_pnl))
        pass

    def updateAccountTime(self, timestamp):
        self.portfolio.updated_at = timestamp

    def accountDownloadEnd(self, account):
        pass


    def orderStatus(self, order_id, status, filled, remaining, avg_fill_price, perm_id, parent_id, last_fill_price, client_id, why_held):
        # print("Order status - {}, {}/{}, {}, perm_id {}, parent_id {}".format(order_id, filled, remaining, avg_fill_price, perm_id, parent_id))
        if status == 'Filled':  # remaining == 0:
            print(order_id, status, filled, remaining, avg_fill_price, perm_id, parent_id, last_fill_price, client_id, why_held)
        pass

    def openOrder(self, order_id, contract, order, order_state):
        # This is called when an order gets fully executed, problem is most of the times it is called more than once
        # with different commissions values.
        # if order_state.status == 'Filled' and order_state.commission != sys.float_info.max:
        #     direction = order.action # BUY, SELL, SSHORT
        #     quantity = order.totalQuantity
        #     print("Order {} for symbol {} executed. Commission {}. Order qt {}".format(order_id, contract.symbol, order_state.commission, order.totalQuantity))
        pass

    def execDetails(self, req_id, contract, execution):
        # Gets called in every sub execution, not when whole order is finished
        # req_id -1 means an order was filled
        # e = execution
        # if req_id == -1:  # Meaning an order was filled
        #     print("Exec details id {}, {} {}, cumQty {} shares {} avgPrice {}".format(
        #         execution.permId, execution.side, contract.symbol, e.cumQty, e.shares, e.avgPrice))
        pass

    def commissionReport(self, commission_report):
        # commission_report.commission and commission_report.execId
        pass




    # -------------- Market section --------------

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
            logging.warning("Trading halted for {}".format(self.market.ticker_dict[ticker_id]))


    # -------------- Execution section --------------
    def nextValidId(self, order_id):
        self.next_valid_order_id = order_id

    # def orderStatus(self, id, status, filled, remaining, avgFillPrice, permId,
    #                 parentId, lastFilledPrice, clientId, whyHeld):
    #     pass
    #

    #
    # def contractDetailsEnd(self, reqId):
    #     print("Contract details request complete, (request id %i)" % reqId)
    #
    # def contractDetails(self, reqId, contractDetails):
    #     pass


    # -------------- Error section --------------
    # TWS WARNING - 2103: Market data farm connection is broken:ibdemo
    # TWS WARNING - 2103: Market data farm connection is broken:ibdemo
    # TWS WARNING - 2103: Market data farm connection is broken:ibdemo
    # TWS WARNING - 2105: HMDS data farm connection is broken:demohmds
    # TWS SYSTEM-ERROR - 1100: Connectivity between IB and TWS has been lost.
    # TWS SYSTEM-ERROR - 1100: Connectivity between IB and TWS has been lost.
    # TWS SYSTEM-ERROR - 1100: Connectivity between IB and TWS has been lost.
    # IBKR - position 1200, market_value 41.44958335
    # TWS SYSTEM-ERROR - 1102: Connectivity between IB and TWS has been restored - data maintained.
    # IBKR, 1200, market_price 41.4049988, market_value 49686.0, unrealized_pnl -53.5, realized_pnl -62.0
    # TWS call ignored - accountDownloadEnd(DU15235)
    # TWS INFO - 2106: HMDS data farm connection is OK:demohmds
    # TWS INFO - 2104: Market data farm connection is OK:ibdemo
