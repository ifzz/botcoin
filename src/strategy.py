import logging
import queue

import numpy as np

from .event import SignalEvent

class Strategy(object):
    """
    Strategy root class.
    """
    def __init__(self):
        pass

    def __str__(self):
        return self.__class__.__name__ + " with parameters " + ", ".join([str(i) for i in self.args])

    def set_market(self, market):
        # Market data object
        self.market = market
        # List of tradable symbols
        self.symbol_list = self.market.symbol_list
        # Open positions. Not connected to Portfolio's open_trades
        # Used to keep track of current state across all symbols
        self.positions = {}
        # Entry price for open positions
        self.entry_price = {}

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

    def take_profit(self, profit_pct):
        for s in self.positions:
            if self.positions[s] in ('SHORT'):
                exit_price = self.entry_price[s]*(1-profit_pct)
                if self.market.bars(s).this_low <= exit_price:
                    self.cover(s, exit_price)
            elif self.positions[s] in ('BUY'):
                exit_price = self.entry_price[s]*(1+profit_pct)
                if self.market.bars(s).this_high >= exit_price:
                    self.sell(s, exit_price)

    def stop_loss(self, loss_pct):
        for s in self.positions:
            if self.positions[s] in ('BUY'):
                exit_price = self.entry_price[s]*(1-loss_pct)
                if self.market.bars(s).this_low <= exit_price:
                    self.sell(s, exit_price)
            elif self.positions[s] in ('SHORT'):
                exit_price = self.entry_price[s]*(1+loss_pct)
                if self.market.bars(s).this_high >= exit_price:
                    self.cover(s, exit_price)

def avg(prices):
    return np.round(np.mean(prices),3)

def bbands(prices, k):
    """ returns average, upper band, and lower band"""
    ave = np.mean(prices)
    sd = np.std(prices)
    upband = ave + (sd*k)
    lwband = ave - (sd*k)
    return np.round(ave,3), np.round(upband,3), np.round(lwband,3)


class MACrossStrategy(Strategy):
    def __init__(self, *args):
        self.args = args
        self.fast = args[0]
        self.slow = args[1]

    def logic(self):
        for s in self.symbol_list:
            slow = self.market.bars(s, self.slow).close
            fast = self.market.bars(s, self.fast).close
            if len(slow) == self.slow:
                if s in self.positions:
                    if avg(fast) <= avg(slow):
                        self.sell(s)
                else:
                    if avg(fast) >= avg(slow):
                        self.buy(s)

class BollingerBandStrategy(Strategy):
    def __init__(self, *args):
        self.args = args
        self.length = args[0]
        self.k = args[1]

    def logic(self):
        for s in self.symbol_list:
            bars = self.market.bars(s, self.length)

            if len(bars) >= self.length:
                
                average, upband, lwband = bbands(bars.close, self.k)
                
                if s in self.positions:
                    if bars.this_high >= average:
                        self.sell(s, average)

                else:
                    if bars.this_low <= lwband:
                        self.buy(s, lwband)

class DonchianStrategy(Strategy):
    def __init__(self, *args):
        self.args = args
        self.upper = args[0]
        self.lower = args[1]

    def logic(self):
        for s in self.symbol_list:
            bars_upper = self.market.bars(s, self.upper+1).high
            bars_lower = self.market.bars(s, self.lower+1).low
            bar = self.market.bars(s)

            if (len(bars_lower) > self.lower and len(bars_upper) > self.upper):

                upband = max(bars_upper[:-1])
                lwband = min(bars_lower[:-1])
                if (len(bars_upper[:-1]) != self.upper or
                    len(bars_lower[:-1]) != self.lower):
                    raise AssertionError("{} {} {} {}".format(len(bars_upper.high[:-1]), self.upper, len(bars_lower.low[:-1]), self.lower))

                bar = self.market.today(s)

                if s in self.positions:
                    if bar.low <= lwband:
                        self.sell(s, lwband)

                else:
                    if bar.high >= upband:
                            self.buy(s, upband)