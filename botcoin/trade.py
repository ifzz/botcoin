class Trade(object):
    """
    Complete trade (buy/sell or short/cover)
    """
    def __init__(self, fill):
        # Fake trade happens when there is no proper exit execution, i.e. when backtesting ends
        self.open_position = True
        self.symbol = fill.symbol
        self.direction = fill.order.direction
        self.open_datetime = fill.datetime
        self.quantity = fill.quantity
        self.open_cost = fill.cost
        self.open_price = fill.price
        self.commission = fill.commission

    def __str__(self):
        return "Trade symbol:{}, result:{}, from:{}, to:{}".format(
            self.symbol,
            self.result,
            self.open_datetime,
            self.close_datetime,
        )

    def close_trade(self, new_fill):
        self.open_position = False
        self.close_datetime = new_fill.datetime
        self.close_cost = new_fill.cost
        self.close_price = new_fill.price
        self.commission += new_fill.commission
        self.result = -(self.open_cost + self.close_cost + self.commission)
        return self

    def fake_close_trade(self, close_datetime, close_cost):
        """ Used when backtesting finished and open_positions result need to be estimated """ 
        self.close_datetime = close_datetime
        self.close_cost = close_cost
        self.close_price = math.fabs(close_cost/self.quantity)
        self.result = -(self.open_cost + self.close_cost + self.commission)
        return self