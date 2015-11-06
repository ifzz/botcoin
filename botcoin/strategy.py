import logging
import queue

import numpy as np

from event import SignalEvent

class Strategy(object):
    """
    Strategy root class.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.initialize()

    def __str__(self):
        return self.__class__.__name__ + "(" + ",".join([str(i) for i in self.args]) + ")"

    def get_arg(self, index, default=None):
        if isinstance(index, int):
            try:
                return self.args[index]
            except IndexError:
                return default

        elif isinstance(index, str):
            try:
                return self.kwargs[index]
            except KeyError:
                return default

    def buy(self, symbol, price=None):
        sig = SignalEvent(symbol, 'BUY', price, self.market.datetime)
        self.signals_queue.put(sig)

    def sell(self, symbol, price=None):
        sig = SignalEvent(symbol, 'SELL', price, self.market.datetime)
        self.signals_queue.put(sig)

    def short(self, symbol, price=None):
        sig = SignalEvent(symbol, 'SHORT', price, self.market.datetime)
        self.signals_queue.put(sig)

    def cover(self, symbol, price=None):
        sig = SignalEvent(symbol, 'COVER', price, self.market.datetime)
        self.signals_queue.put(sig)

    def before_open(self, context):
        # Can (but doesn't have to) be implemented on the subclass
        pass

    def open(self, context, symbol):
        # Can (but doesn't have to) be implemented on the subclass
        pass

    def during(self, context, symbol):
        # Can (but doesn't have to) be implemented on the subclass
        pass

    def close(self, context, symbol):
        # Can (but doesn't have to) be implemented on the subclass
        pass

    def after_close(self, context):
        # Can (but doesn't have to) be implemented on the subclass
        pass
