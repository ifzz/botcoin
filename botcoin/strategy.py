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
        self.add_signal_to_queue(symbol, 'BUY', price)

    def sell(self, symbol, price=None):
        self.add_signal_to_queue(symbol, 'SELL', price)

    def short(self, symbol, price=None):
        self.add_signal_to_queue(symbol, 'SHORT', price)

    def cover(self, symbol, price=None):
        self.add_signal_to_queue(symbol, 'COVER', price)

    def add_signal_to_queue(self, symbol, sig_type, price):
        self.events_queue.put(SignalEvent(symbol, sig_type, price))

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

    # def take_profit(self, s, profit_pct, entry_price=None, exec_round=0):
    #     entry_price = entry_price or self.entry_price[s]

    #     if self.positions[s] in ('SHORT'):
    #         exit_price = entry_price*(1-profit_pct)
    #         if self.market.bars(s).this_low <= exit_price:
    #             self.cover(s, exit_price, exec_round)
    #     elif self.positions[s] in ('BUY'):
    #         exit_price = entry_price*(1+profit_pct)
    #         if self.market.bars(s).this_high >= exit_price:
    #             self.sell(s, exit_price, exec_round)

    # def stop_loss(self, s, loss_pct, entry_price=None, exec_round=0):
    #     entry_price = entry_price or self.entry_price[s]

    #     if self.positions[s] in ('BUY'):
    #         exit_price = entry_price*(1-loss_pct)
    #         if self.market.bars(s).this_low <= exit_price:
    #             self.sell(s, exit_price, exec_round)
    #     elif self.positions[s] in ('SHORT'):
    #         exit_price = entry_price*(1+loss_pct)
    #         if self.market.bars(s).this_high >= exit_price:
    #             self.cover(s, exit_price, exec_round)

