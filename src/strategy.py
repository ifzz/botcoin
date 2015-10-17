import logging
import queue

import numpy as np

from .event import SignalEvent
import settings

class Strategy(object):
    """
    Strategy root class.
    """
    def __init__(self, *args):
        # Open positions. Not connected to Portfolio's open_trades
        # Used to keep track of current state across all symbols
        self.positions = {}
        # Entry price for open positions
        self.entry_price = {}
        
        self.args = args
        self.initialize()

    def __str__(self):
        return self.__class__.__name__ + " with parameters " + ", ".join([str(i) for i in self.args])

    def set_market(self, market):
        # Market data object
        self.market = market
        # List of tradable symbols
        self.symbol_list = self.market.symbol_list


    def generate_signals(self):
        self.signals_to_execute = {}
        self.logic()

        signals_queue = queue.Queue()
        for key in sorted(self.signals_to_execute.keys()):
            signals_queue.put(self.signals_to_execute[key])
        return signals_queue

    def buy(self, symbol, price=None, exec_round=0):
        self.add_signal_to_queue(symbol, 'BUY', price, exec_round)

    def sell(self, symbol, price=None, exec_round=0):
        self.add_signal_to_queue(symbol, 'SELL', price, exec_round)

    def short(self, symbol, price=None, exec_round=0):
        self.add_signal_to_queue(symbol, 'SHORT', price, exec_round)

    def cover(self, symbol, price=None, exec_round=0):
        self.add_signal_to_queue(symbol, 'COVER', price, exec_round)

    def add_signal_to_queue(self, symbol, sig_type, price, exec_round):
        price = price or self.market.today(symbol).close
        signal = SignalEvent(symbol, sig_type, price)
        self.signals_to_execute.setdefault(exec_round, []).append(signal)

    def update_position_from_fill(self, fill):
        if fill.direction in ('BUY', 'SHORT'):
            self.positions[fill.symbol] = fill.direction
            self.entry_price[fill.symbol] = fill.price
        else:
            del(self.positions[fill.symbol])
            del(self.entry_price[fill.symbol])

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