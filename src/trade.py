

class Trade(object):
    """
    Complete trade (buy/sell or short/cover)
    """
    def __init__(self, fill):
        # Fake trade happens when there is no proper exit execution, i.e. when backtesting ends
        self.fake_trade = False
        self.symbol = fill.symbol
        self.direction = fill.order.direction
        self.open_datetime = fill.datetime
        self.quantity = fill.quantity
        self.open_cost = fill.cost
        self.open_commission = fill.commission

    def close_trade(self, new_fill):
        self.close_datetime = new_fill.datetime
        self.close_cost = new_fill.cost
        self.close_commission = new_fill.commission
        self.result = self.open_cost + self.close_cost - (self.open_commission + self.close_commission)
        return self

    def fake_close_trade(self, close_datetime, close_cost):
        """ Used when backtesting finished and open_positions result need to be estimated """ 
        self.fake_trade = True
        self.close_datetime = close_datetime
        self.close_cost = close_cost
        self.result = self.open_cost + self.close_cost - self.open_commission
        return self