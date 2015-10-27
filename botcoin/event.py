class Event(object):
    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with 
    corresponding bars.
    """

    def __init__(self, sub_type=None):
        self.type = 'MARKET'
        
        if sub_type and sub_type in ('open', 'during' ,'close', 'after_close'):
            self.sub_type = sub_type
        elif sub_type:
            raise ValueError("Wrong type of MarketEvent sub_type.")


class SignalEvent(Event):
    """
    Handles the event of a new Strategy generated signal.
    Exchanged directly between Portfolio and its strategies.
    Parameters
        datetime - The timestamp at which the signal was generated.
        signal_type - "BUY", "SELL", "SHORT" or "COVER".
        price - Target price defined by strategy. 
            If None, last close will be used by portfolio.
    """
    
    def __init__(self, symbol, direction, exec_price):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.direction = direction
        self.exec_price = exec_price

    def __str__(self):
        return "Signal - {}:{}:{}".format(self.symbol,self.direction,str(self.exec_price))


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, signal, symbol, quantity, direction, limit_price, 
                 estimated_cost=0.0):
        """
        Initialises a Limit order order, has a quantity (integer)
        and its direction ('BUY', 'SELL', 'SHORT' and 'COVER' ).

        Parameters:
        symbol - The instrument to trade.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        limit_price - Limit price to be used for execution.
        estimated_cost -How much the order is expected to cost, used 
            to calculate money locked in before order is executed.
        """
        if not isinstance(signal, SignalEvent):
            raise TypeError("signal is not instance of SignalEvent")

        self.type = 'ORDER'
        self.signal = signal
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.limit_price = limit_price

        if direction in ('BUY', 'COVER') and not estimated_cost:
            raise ValueError("BUY or COVER require estimated_cost")
        self.estimated_cost = estimated_cost

    def __str__(self):
        return "Order - {}:{}:{}".format(self.symbol,self.direction,str(self.quantity),str(self.estimated_cost))

class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, order, datetime, direction,
                 quantity, cost, price, commission):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional 
        commission.

        Parameters:
        datetime - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        cost - The holdings value in dollars.
        commission - comission paid
        """
        if not isinstance(order, OrderEvent):
            raise TypeError("order is not instance of OrderEvent")

        self.type = 'FILL'
        self.order = order
        self.symbol = order.symbol
        self.datetime = datetime
        self.direction = direction
        self.quantity = quantity
        self.cost = cost
        self.price = price
        self.commission = commission

    def __str__(self):
        return "Fill - {}:{}:{}".format(self.symbol,str(self.quantity),str(self.cost))
