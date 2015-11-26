class BarValidationError(Exception):
    pass

class NoBarsError(BarValidationError):
    pass

class NotEnoughBarsError(BarValidationError):
    pass

class EmptyBarsError(BarValidationError):
    pass

class NegativeExecutionPriceError(Exception):
    def __init__(self, strategy, date, symbol, exec_price):
        self.message = ''.join([
            "Can't execute Signal with negative price.",
            "Strategy {}, date {}, symbol {}, price {}.".format(
                strategy, date, symbol, exec_price,
        )])

        self.strategy = strategy
        self.date = date
        self.symbol = symbol
        self.exec_price = exec_price

        super(NegativeExecutionPriceError, self).__init__(self.message)

class ExecutionPriceOutOfBandError(Exception):
    def __init__(self, strategy, date, symbol, exec_price, high, low):
        self.message = ''.join([
            "You're trying to execute with a price that is out of band today. ",
            "Strategy {}, date {}, symbol {}, exec_price {}, high {}, low {}".format(
                strategy, date, symbol, exec_price, high, low,
        )])

        self.strategy = strategy
        self.date = date
        self.symbol = symbol
        self.exec_price = exec_price
        self.high = high
        self.low = low

        super(ExecutionPriceOutOfBandError, self).__init__(self.message)
