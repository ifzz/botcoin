import logging

class Trade(object):
    """
    Complete trade (buy/sell or short/cover)
    """
    def __init__(self, order):
        self.symbol = order.symbol
        self.direction = order.direction
        self.opened_at = order.created_at
        self.quantity = order.quantity

        self.estimated_cost = order.estimated_cost

        self.open_filled_quantity = 0.0
        self.open_cost = 0.0
        self.open_commission = 0.0
        self.open_order = order

        self.close_filled_quantity = 0.0
        self.close_cost = 0.0
        self.close_commission = 0.0
        self.close_order = None

    @property
    def open_is_fully_filled(self):
        return self.open_filled_quantity == self.quantity

    @property
    def close_is_fully_filled(self):
        return self.close_filled_quantity == -self.quantity

    # @property
    # def status(self):
    #     if self.close_is_fully_filled:
    #         return 3  # close filled, trade finished
    #     elif self.close_order:
    #         return 2  # there is a close order, position being exited
    #     elif self.open_is_fully_filled:
    #         return 1  # trade openned, open fully filled
    #     else:
    #         return 0  # order submitted but not executed at all

    @property
    def commission(self):
        return self.open_commission + self.close_commission

    def fill_is_relevant_to_portfolio(self, fill):
        # Returns False if fill contains info which would have been already consumed by portfolio
        if (
            (fill.direction in ('BUY', 'SHORT') and self.open_is_fully_filled) or  # fill already reported
            (fill.direction in ('SELL', 'COVER') and self.close_is_fully_filled) or  # fill already reported
            (abs(self.quantity) != abs(fill.quantity))  # partial fill (need abs because quantity is reversed for close (e.g. 100 buy becomse -100 sell))
        ):
            return False
        else:
            return True

    def update_from_fill(self, fill):
        if fill.direction in ('BUY', 'SHORT'):

            self.open_filled_quantity = fill.quantity
            self.open_commission = fill.commission
            self.avg_open_price = fill.price
            self.open_cost = fill.quantity*fill.price

            if self.open_is_fully_filled:
                logging.debug('{} order for {} filled'.format(self.direction, self.symbol))

        elif fill.direction in ('SELL', 'COVER'):

            if not self.open_is_fully_filled:
                raise AssertionError('Closing {} trade before it even started on {}.'.format(self.symbol,fill.created_at))

            self.close_filled_quantity = fill.quantity
            self.close_cost = fill.quantity*fill.price
            self.close_commission = fill.commission
            self.avg_close_price = fill.price

            if self.close_is_fully_filled:
                self.closed_at = fill.created_at
                self.pnl = -(self.open_cost + self.close_cost + self.commission)

                assert(self.close_cost == -self.quantity*self.avg_close_price)
                assert(self.open_cost == self.quantity*self.avg_open_price)

                logging.debug('{} order for {} filled'.format(fill.direction, self.symbol))

    def update_close_order(self, order):
        self.close_order = order

    def fake_close_trade(self, closed_at, close_cost):
        """ Used when backtesting finished and open_positions result need to be estimated """
        self.closed_at = closed_at
        self.close_cost = close_cost
        self.avg_close_price = close_cost/-self.quantity
        self.pnl = -(self.open_cost + self.close_cost + self.commission)
