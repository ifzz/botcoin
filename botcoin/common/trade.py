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

        self.open_filled_quantity = 0
        self.open_cost = 0
        self.open_commission = 0
        self.open_order = order

        self.close_filled_quantity = 0
        self.close_cost = 0
        self.close_commission = 0
        self.close_order = None

    @property
    def open_is_fully_filled(self):
        return self.open_filled_quantity == self.quantity

    @property
    def close_is_fully_filled(self):
        return self.close_filled_quantity == -self.quantity

    @property
    def status(self):
        if self.close_is_fully_filled:
            return 'CLOSED'  # close filled, trade finished
        elif self.close_order:
            return 'CLOSE SUBMITTED'  # there is a close order, position being exited
        elif self.open_is_fully_filled:
            return 'OPEN'  # trade openned, open fully filled
        else:
            return 'OPEN SUBMITTED'  # order submitted but not executed at all

    @property
    def commission(self):
        return self.open_commission + self.close_commission

    def update_open_fill(self, fill):
        self.open_filled_quantity = fill.quantity
        self.open_cost = fill.cost
        self.open_commission = fill.commission
        self.avg_open_price = fill.price

        if self.open_is_fully_filled:
            logging.debug('{} order for {} filled'.format(self.direction, self.symbol))

    def update_close_order(self, order):
        self.close_order = order

    def update_close_fill(self, new_fill):
        if not self.open_is_fully_filled:
            raise AssertionError('Closing {} trade before it even started on {}.'.format(self.symbol,new_fill.created_at))

        self.close_filled_quantity = new_fill.quantity
        self.avg_close_price = new_fill.price
        self.close_cost = new_fill.cost
        self.close_commission = new_fill.commission

        if self.close_is_fully_filled:
            self.closed_at = new_fill.created_at
            self.pnl = -(self.open_cost + self.close_cost + self.commission)

            assert(self.close_cost == -self.quantity*self.avg_close_price)
            assert(self.open_cost == self.quantity*self.avg_open_price)

            logging.debug('{} order for {} filled'.format(new_fill.direction, self.symbol))

    def fake_close_trade(self, created_at, close_cost):
        """ Used when backtesting finished and open_positions result need to be estimated """
        self.closed_at = created_at
        self.close_cost = close_cost
        self.avg_close_price = close_cost/-self.quantity
        self.pnl = -(self.open_cost + self.close_cost + self.commission)
