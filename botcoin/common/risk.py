from math import floor

from botcoin.utils import _round

class RiskAnalysis(object):
    def __init__(self, COMMISSION_FIXED, COMMISSION_PCT, COMMISSION_MIN,
                CAPITAL_TRADABLE_CAP, POSITION_SIZE, ROUND_LOT_SIZE,
                MAX_SLIPPAGE, ADJUST_POSITION_DOWN, cash_balance_method, net_liquidation_method):

        self.COMMISSION_FIXED = COMMISSION_FIXED
        self.COMMISSION_PCT = COMMISSION_PCT
        self.COMMISSION_MIN = COMMISSION_MIN
        self.CAPITAL_TRADABLE_CAP = CAPITAL_TRADABLE_CAP
        self.POSITION_SIZE = POSITION_SIZE
        self.ROUND_LOT_SIZE = ROUND_LOT_SIZE
        self.MAX_SLIPPAGE = MAX_SLIPPAGE
        self.ADJUST_POSITION_DOWN = ADJUST_POSITION_DOWN
        self.cash_balance = cash_balance_method
        self.net_liquidation = net_liquidation_method

    def adjust_price_for_slippage(self, direction, price):
        direction_mod = -1 if direction in ('SELL','SHORT') else 1
        return _round(price * (1+self.MAX_SLIPPAGE*direction_mod))

    def determine_commission(self, quantity, price):
        return max(self.COMMISSION_FIXED + (self.COMMISSION_PCT * abs(quantity) * price), self.COMMISSION_MIN)

    def calculate_quantity_and_commission(self, direction, adj_price, current_quantity=None):
        direction_mod = -1 if direction in ('SELL','SHORT') else 1
        quantity = 0
        estimated_commission = 0
        cash_balance = self.cash_balance()
        net_liquidation = self.net_liquidation()

        if direction in ('BUY', 'SHORT'):

            # Cash to be spent on this position
            if self.CAPITAL_TRADABLE_CAP:
                position_cash = min(self.CAPITAL_TRADABLE_CAP, net_liquidation)*self.POSITION_SIZE
            else:
                position_cash = net_liquidation*self.POSITION_SIZE

            # Adjust position down if not enough money and
            if direction == 'BUY':
                if position_cash > cash_balance:
                    if self.ADJUST_POSITION_DOWN:
                        position_cash = cash_balance
                    else:
                        logging.warning("Can't adjust position, {} missing cash.".format(str(position_cash-cash_balance)))
                        return quantity, estimated_commission

            quantity = direction_mod * position_cash / adj_price
            quantity = floor(quantity/self.ROUND_LOT_SIZE) * self.ROUND_LOT_SIZE if self.ROUND_LOT_SIZE else quantity

            estimated_commission = self.determine_commission(quantity, adj_price)

            # For as long as estimated cost is bigger than position_cash available
            while estimated_commission + quantity * adj_price > position_cash:
                # Adjust quantity down
                quantity -= self.ROUND_LOT_SIZE or 1  # What if can buy less than 1 (e.g. BTC)
                # Recalculate commission
                estimated_commission = self.determine_commission(quantity, adj_price)

        elif direction in ('SELL', 'COVER'):
            quantity = -1 * current_quantity  # Should raise TypeError if current_quality is None
            estimated_commission =  self.determine_commission(quantity, adj_price)

        return quantity, estimated_commission
