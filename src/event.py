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

    def __init__(self, symbol, quantity, direction, limit_price, estimated_cost=0.0):
        """
        Initialises a Limit order order, has a quantity (integer)
        and its direction ('BUY', 'SELL', 'SHORT' and 'COVER' ).

        Parameters:
        symbol - The instrument to trade.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        limit_price - Price 
        """
        
        self.type = 'ORDER'
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.limit_price = limit_price

        if direction in ('BUY', 'COVER') and not estimated_cost:
            raise ValueError # BUY or COVER require estimated_cost
        self.estimated_cost = estimated_cost

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print("Order: Symbol={}, Quantity={}, Direction={}, Limit price={}".format(
            self.symbol, self.quantity, self.direction, self.limit_price))


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, timeindex, order, quantity,
                 cost, commission):
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
        self.order = order
        self.symbol = order.symbol
        self.quantity = quantity
        self.cost = cost
        self.commission = commission
            