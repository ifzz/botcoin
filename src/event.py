class Event(object):
    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with 
    corresponding bars.
    """

    def __init__(self):
        self.type = 'MARKET'


class SignalEvent(Event):
    """
    Handles the event of a new Strategy generated signal.
    Exchanged directly between Portfolio and its strategies.
    Parameters
        datetime - The timestamp at which the signal was generated.
        signal_type - 'LONG' or 'SHORT'.
    """
    
    def __init__(self, symbol, signal_type):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.signal_type = signal_type

class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol, order_type, quantity, direction):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        """
        
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print("Order: Symbol={}, Type={}, Quantity={}, Direction={}".format(
            self.symbol, self.order_type, self.quantity, self.direction))


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, timeindex, symbol, quantity, 
                 direction, cost, commission):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional 
        commission.

        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        cost - The holdings value in dollars.
        commission - comission paid
        """
        
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.cost = cost
        self.commission = commission
            