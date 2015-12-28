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

        self.commission = 0

        self.open_filled_quantity = 0
        self.open_cost = 0
        self.open_order = order

        self.close_filled_quantity = 0
        self.close_cost = 0
        self.close_order = None

        self.is_open = False
        self.is_fully_filled = False


    def update_open_fill(self, fill):
        self.is_open = True
        self.open_filled_quantity += fill.quantity
        self.open_cost += fill.cost
        self.commission = fill.commission
        self.avg_open_price = fill.price

        if self.open_filled_quantity == self.quantity:
            self.is_fully_filled = True
            logging.debug('{} order for {} filled'.format(self.direction, self.symbol))

    def exiting(self, order):
        self.close_order = order

    def update_close_fill(self, new_fill):

        if not self.is_fully_filled:
            raise AssertionError('Closing {} trade before it even started on {}.'.format(self.symbol,new_fill.created_at))

        self.close_filled_quantity += new_fill.quantity
        self.avg_close_price = new_fill.price

        if self.close_filled_quantity == -self.quantity:
            self.is_open = False
            self.commission += new_fill.commission
            self.close_cost += new_fill.cost
            self.closed_at = new_fill.created_at
            self.pnl = -(self.open_cost + self.close_cost + self.commission)

            assert(self.close_cost ==  -self.quantity*self.avg_close_price)
            assert(self.open_cost ==  self.quantity*self.avg_open_price)

            logging.debug('{} order for {} filled'.format(new_fill.direction, self.symbol))

    def fake_close_trade(self, created_at, close_cost):
        """ Used when backtesting finished and open_positions result need to be estimated """
        self.closed_at = created_at
        self.close_cost = close_cost
        self.avg_close_price = close_cost/-self.quantity
        self.pnl = -(self.open_cost + self.close_cost + self.commission)
