from botcoin.common.portfolio import Portfolio

class BacktestPortfolio(Portfolio):

    @property
    def cash_balance(self):
        # Pending orders that remove cash from account
        long_pending_orders = [order for order in self.pending_orders if order.direction in ('BUY','COVER')]

        return self.holdings['cash'] - sum([i.estimated_cost for i in long_pending_orders])

    @property
    def net_liquidation(self):
        value = self.holdings['cash']
        return value + sum([self.positions[s] * self.market.last_price(s) for s in self.market.symbol_list])

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

        # Check for negative execution price
        # Should stop execution during backtesting, but not on live exec
        if exec_price < 0:
            raise NegativeExecutionPriceError(self.strategy, self.market.updated_at, symbol, exec_price)