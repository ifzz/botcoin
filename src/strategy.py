import logging
import queue

import numpy as np

from .event import SignalEvent

class Strategy(object):
    """
    Strategy root class.
    """
    def __init__(self, parameters):
        pass

    def __str__(self):
        return self.__class__.__name__ + " with parameters " + ", ".join([str(i) for i in self.parameters])

    def set_market(self, market):
        # Market data object
        self.market = market
        # List of tradable symbols
        self.symbol_list = self.market.symbol_list
        # Open positions. Not connected to Portfolio's open_trades
        # Used to keep track of current state across all symbols
        self.positions = {}

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
        price = price or self.market.bars(symbol).this_close
        signal = SignalEvent(symbol, sig_type, price)
        self.signals_to_execute.setdefault(exec_round, []).append(signal)

    def update_position_from_fill(self, fill):
        if fill.direction in ('BUY', 'SHORT'):
            self.positions[fill.symbol] = fill.direction
        else:
            del(self.positions[fill.symbol])

def avg(prices):
    return np.round(np.mean(prices),3)

def bbands(prices, k):
    """ returns average, upper band, and lower band"""
    ave = np.mean(prices)
    sd = np.std(prices)
    upband = ave + (sd*k)
    lwband = ave - (sd*k)
    return np.round(ave,3), np.round(upband,3), np.round(lwband,3)

class RandomBuyStrategy(Strategy):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, parameters=[5, 5]):
        self.parameters = parameters
        self.interval = parameters[0]
        self.hold = parameters[1]
        self.floating_interval = self.interval

    def logic(self):
        for s in self.symbol_list:
            if self.floating_interval == 0:
                if not self.positions[s]:
                    self.floating_interval = self.hold  
                    self.buy(s)

                elif self.positions[s] == 'BUY':
                    self.floating_interval = self.interval
                    self.selll(s)
            self.floating_interval -= 1

class MACrossStrategy(Strategy):
    def __init__(self, parameters):
        self.parameters = parameters
        self.fast = parameters[0]
        self.slow = parameters[1]

    def logic(self):
        for s in self.symbol_list:
            slow = self.market.bars(s, self.slow).close
            fast = self.market.bars(s, self.fast).close
            if len(slow) == self.slow:
                if self.positions[s]:
                    if avg(fast) <= avg(slow):
                        self.sell(s)

                else:
                    if avg(fast) >= avg(slow):
                        self.buy(s)

class BBStrategy(Strategy):
    def __init__(self, parameters):
        self.parameters = parameters
        self.length = parameters[0]
        self.k = parameters[1]

    def logic(self):
        for s in self.symbol_list:
            bars = self.market.bars(s, self.length)

            if len(bars) >= self.length:
                
                average, upband, lwband = bbands(bars.close, self.k)
                
                if s in self.positions:
                    if bars.this_high >= average:
                        self.sell(s, bars.this_close)

                else:
                    if bars.this_low <= lwband:
                        self.buy(s, bars.this_close)

class DonchianStrategy(Strategy):
    def __init__(self, parameters):
        self.parameters = parameters
        self.upper = parameters[0]
        self.lower = parameters[1]

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

                bar = self.market.bars(s)

                if s in self.positions:
                    if bar.this_low <= lwband:
                        self.sell(s, lwband)

                else:
                    if bar.this_high >= upband:
                            self.buy(s, upband)

class BasicMeanRevertingStrategy(Strategy):

        def __init__(self, parameters):
            self.parameters = parameters
            self.length = parameters[0]
            self.max_positions = parameters[1]

        def create_ordered_list(self):
            # Creates list of pct distance on open
            list_pct_from_avg = []
            for s in self.symbol_list:
                bars = self.market.bars(s, self.length+1)
                if (len(bars)-1) >= self.length and bars.this_close:
                    # avg is calculated not using current bar, but past bars
                    avg = np.mean(bars.close[:-1])
                    list_pct_from_avg.append((s, (avg-bars.this_close)/avg))   
            return list_pct_from_avg

        def logic(self):
            list_pct_from_avg = self.create_ordered_list()
            # Generating signals for the extremes in the list
            if list_pct_from_avg:
                ordered_list = sorted(list_pct_from_avg, key=lambda tup: tup[1])
                list_to_buy = [s for s, pct in ordered_list[0:self.max_positions]]

                [self.buy(s, self.market.bars(s).this_open) for s in list_to_buy]

                # selling on open of this bar
                [self.sell(s, self.market.bars(s).this_close, 2) for s in list_to_buy]
                    
class WeeklyMeanRevertingStrategy(Strategy):

        def __init__(self, parameters):
            self.parameters = parameters
            self.length = parameters[0]
            self.max_positions = parameters[1]

        def create_ordered_list(self):
            # Creates list of pct distance on open
            list_pct_from_avg = []
            for s in self.symbol_list:
                bars = self.market.bars(s, self.length+1)
                if (len(bars)-1) >= self.length and bars.this_close:
                    # avg is calculated not using current bar, but past bars
                    avg = np.mean(bars.close[:-1])
                    list_pct_from_avg.append((s, (avg-bars.this_close)/avg))   
            return list_pct_from_avg

        def logic(self):
            weekday = self.market.this_datetime.weekday()
            week_number = self.market.this_datetime.isocalendar()[1]
            if weekday == 0:
                list_pct_from_avg = self.create_ordered_list()
                # Generating signals for the extremes in the list
                if list_pct_from_avg:

                    ordered_list = sorted(list_pct_from_avg, key=lambda tup: tup[1])
                    list_to_buy = [s for s, pct_from_avg in ordered_list[0:self.max_positions]]

                    [self.sell(s, self.market.bars(s).this_open) for s in self.positions]

                    [self.buy(s, self.market.bars(s).this_open, 1) for s in list_to_buy]

class BasicMeanRevertingStrategy2(Strategy):

        def __init__(self, parameters):
            self.parameters = parameters
            self.length = parameters[0]
            self.max_positions = parameters[1]

        def create_ordered_list(self):
            # Creates list of pct distance on open
            list_pct_from_avg = []
            for s in self.symbol_list:
                bars = self.market.bars(s, self.length+1)
                if (len(bars)-1) >= self.length and bars.this_close:
                    # avg is calculated not using current bar, but past bars
                    avg = np.mean(bars.close[:-1])
                    list_pct_from_avg.append((s, (avg-bars.this_close)/avg))   
            return list_pct_from_avg

        def logic(self):
            list_pct_from_avg = self.create_ordered_list()
            # Generating signals for the extremes in the list
            if list_pct_from_avg:
                ordered_list = sorted(list_pct_from_avg, key=lambda tup: tup[1])
                list_to_buy = ordered_list[0:self.max_positions]
                list_to_sell = [s for s in self.positions if s not in list_to_buy]

                # selling on open of this bar
                [self.sell(s, self.market.bars(s).this_open) for s in list_to_sell]

                [self.buy(s, self.market.bars(s).this_open, 1) for s,pct_from_avg in list_to_buy if s not in self.positions]
                    