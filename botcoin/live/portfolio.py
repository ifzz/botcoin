from botcoin.common.portfolio import Portfolio
from botcoin.common.trade import Trade

class LivePortfolio(Portfolio):


    def cash_balance(self):
        return self._cash_balance

    def net_liquidation(self):
        return self._net_liquidation

    def check_signal_consistency(self, symbol, exec_price, direction):
        if exec_price < 0:
            logging.critical(NegativeExecutionPriceError(self.strategy, self.market.updated_at, symbol, exec_price))

    def execute_order(self, order):
        if order.direction in ('BUY', 'SHORT'):
            self.open_trades[order.symbol] = Trade(order)  # Start trade
        else:
            # Checks if there is a similar order in pending_orders to protect
            # against repeated signals coming from strategy
            if self.open_trades[order.symbol].close_order:
                logging.critical("Possible duplicate order being created in portfolio.")

            self.open_trades[order.symbol].exiting(order)  # Flag trade as exiting

        self.if_socket.execute_order(order)
