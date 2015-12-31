import datetime

class Event(object):
    """
    Priority is
        10 Fill
        10 Order
        20 Signal
        30 Market
    """
    def __lt__(self, other):
         return (self.priority, self.created_at) < (other.priority, other.created_at)

class MarketEvent(Event):
    def __init__(self, sub_type, symbol=None):
        self.priority = 30
        self.symbol = symbol
        if sub_type and sub_type in ('before_open', 'open', 'during' ,'close', 'after_close'):
            self.sub_type = sub_type
        elif sub_type:
            raise ValueError("Wrong type of MarketEvent sub_type.")
        self.created_at = datetime.datetime.now()


class SignalEvent(Event):
    def __init__(self, symbol, direction, exec_price):
        if direction not in ('BUY', 'SELL', 'SHORT', 'COVER'):
            raise ValueError("Unknown direction - {}".format(direction))

        self.priority = 20
        self.symbol = symbol
        self.direction = direction
        self.exec_price = exec_price
        self.created_at = datetime.datetime.now()

    def __str__(self):
        return "Signal - {}:{}:{}".format(self.symbol,self.direction,str(self.exec_price))


class OrderEvent(Event):

    def __init__(self, signal, symbol, quantity, direction, limit_price,
                 estimated_cost):

        if not isinstance(signal, SignalEvent):
            raise TypeError("signal is not instance of SignalEvent")

        self.priority = 10
        self.type = 'LMT'
        self.signal = signal
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.limit_price = limit_price
        self.estimated_cost = estimated_cost
        self.created_at = datetime.datetime.now()

    def __str__(self):
        return "Order - {} : {} : {} : {}".format(self.symbol,self.direction,str(self.quantity),str(self.estimated_cost))

class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, symbol, direction, quantity,
                 price, commission):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional
        commission.

        Parameters:
        symbol - The instrument which was filled.
        direction - The direction of fill ('BUY' or 'SELL')
        quantity - The filled quantity.
        cost - The holdings value in dollars.
        price - avg price paid
        commission - comission paid
        """

        self.priority = 10
        self.symbol = symbol
        self.direction = direction
        self.quantity = quantity
        self.price = price
        self.commission = commission
        self.created_at = datetime.datetime.now()

    def __str__(self):
        return "Fill - {}:{}:{}".format(self.symbol,self.direction,self.quantity)
