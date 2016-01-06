from math import fsum
import numpy as np

from botcoin.common.errors import ExecutionPriceOutOfBandError, NegativeExecutionPriceError
from botcoin.common.events import FillEvent
from botcoin.common.portfolio import Portfolio
from botcoin.common.trade import Trade

class BacktestPortfolio(Portfolio):

    def cash_balance(self):
        # Pending orders that remove cash from account
        money_held = fsum([t.estimated_cost for t in self.open_trades.values() if t.direction in ('BUY','COVER') and not t.open_is_fully_filled])
        return self.holdings['cash'] - money_held

    def net_liquidation(self):
        market_value = fsum([self.open_trades[s].open_filled_quantity * self.market.last_price(s) for s in self.open_trades])

        return self.holdings['cash'] + market_value

    def check_signal_consistency(self, symbol, exec_price, direction):
        """ Looks for consistency errors common during backtesting, such as
         execution price outside low-high range. """
        today = self.market.today(symbol)

        # Checks for execution prices above today.high or below today.low
        # Should stop execution during backtesting, but not on live exec
        if not (exec_price <= today.high and exec_price >= today.low):
            raise ExecutionPriceOutOfBandError(
                self.strategy, self.market.updated_at, symbol, direction,
                exec_price, today.high, today.low,
            )

        # Check for negative or null execution price
        # Should stop execution during backtesting, but not on live exec
        if exec_price <= 0:
            raise NegativeExecutionPriceError(self.strategy, self.market.updated_at, symbol, exec_price)

    def execute_order(self, order):
        if order.direction in ('BUY', 'SHORT'):
            self.open_trades[order.symbol] = Trade(order)  # Start trade
        else:
            # Checks if there is a similar order in pending_orders to protect
            # against repeated signals coming from strategy
            if self.open_trades[order.symbol].close_order:
                logging.critical("Possible duplicate order being created in portfolio.")

            self.open_trades[order.symbol].update_close_order(order)  # Flag trade as exiting

        commission = self.risk.determine_commission(order.quantity, order.limit_price)

        # in case I mess up and remove abs() again
        assert(commission>=0)

        # Fake fill
        fill_event = FillEvent(
            order.symbol,
            order.direction,
            order.quantity,
            order.limit_price,
            commission,
        )

        self.events_queue.put(fill_event)

    def update_last_positions_and_holdings(self):
        # Adds latest current position and holding into 'all' lists, so they
        # can be part of performance as well
        if self.holdings:
            self.all_holdings.append(self.holdings)
            self.holdings, self.positions = None, None

        # "Fake close" trades that are open, so they can be part of trades performance stats
        for trade in self.open_trades.values():

            direction = 1 if trade.direction in ('SELL','SHORT') else -1
            quantity = trade.quantity * direction
            trade.fake_close_trade(self.market.updated_at, quantity * self.market.last_price(trade.symbol))

            self.all_trades.append(trade)
