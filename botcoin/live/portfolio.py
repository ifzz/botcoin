from botcoin.common.portfolio import Portfolio
from botcoin.common.trade import Trade

class LivePortfolio(Portfolio):


    def cash_balance(self):
        return self._cash_balance

    def net_liquidation(self):
        return self._net_liquidation

    def check_signal_consistency(self, symbol, exec_price, direction):
        if exec_price < 0:
            logging.critical(ValueError("You're trying to execute with a price that is out of band today. Strategy {}, date {}, symbol {}, direction {}, exec_price {}, high {}, low {}".format(
                self.strategy, self.market.updated_at, symbol, direction, exec_price, today.high, today.low,
            )))

    def execute_order(self, order):
        if order.direction in ('BUY', 'SHORT'):
            self.open_trades[order.symbol] = Trade(order)  # Start trade
        else:
            # Checks if there is a similar order in pending_orders to protect
            # against repeated signals coming from strategy
            if self.open_trades[order.symbol].status in ('CLOSE SUBMITTED', 'CLOSED'):
                logging.critical("Possible duplicate order being created in portfolio.")

            self.open_trades[order.symbol].update_close_order(order)  # Flag trade as exiting

        self.if_socket.execute_order(order)
