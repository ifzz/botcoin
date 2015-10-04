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
        price = price or self.market.bars(symbol).this_close
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

class RandomBuyStrategy(Strategy):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, *args):
        self.args = args
        self.interval = args[0]
        self.hold = args[1]
        self.floating_interval = self.interval

    def logic(self):
        for s in self.symbol_list:
            if self.floating_interval == 0:
                if s in self.positions:
                    self.floating_interval = self.interval
                    self.sell(s)
                else:
                    self.floating_interval = self.hold  
                    self.buy(s)
            self.floating_interval -= 1

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

                bar = self.market.bars(s)

                if s in self.positions:
                    if bar.this_low <= lwband:
                        self.sell(s, lwband)

                else:
                    if bar.this_high >= upband:
                            self.buy(s, upband)

class BasicMeanRevertingStrategy(Strategy):

        def __init__(self, *args):
            self.args = args
            self.length = args[0]
            self.max_positions = args[1]

        def create_ordered_list(self):
            # Creates list of pct distance on open
            list_pct_from_avg = []
            for s in self.symbol_list:
                bars = self.market.bars(s, self.length+1)
                if (len(bars)-1) >= self.length and bars.this_close:
                    # avg is calculated not using current bar, but past bars
                    avg = np.mean(bars.close[:-1])
                    list_pct_from_avg.append((s, (avg-bars.close[-2])/avg))
            return list_pct_from_avg

        def logic(self):
            list_pct_from_avg = self.create_ordered_list()
            # Generating signals for the extremes in the list
            if list_pct_from_avg:
                ordered_list = sorted(list_pct_from_avg, key=lambda tup: tup[1], reverse=True)
                list_to_buy = [s for s, pct in ordered_list[0:self.max_positions]]
                
                [self.buy(s, self.market.bars(s).this_open) for s in list_to_buy]

                [self.sell(s, self.market.bars(s).this_close, 2) for s in list_to_buy]
                    
class WeeklyMeanRevertingStrategy(Strategy):

        def __init__(self, *args):
            self.args = args
            self.length = args[0]
            self.max_positions = args[1]
            self.take_profit_pct = args[2] if 2 in args else 1.00
            self.stop_loss_pct = args[3] if 3 in args else 1.00

            self.last_week = None

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
            this_week = self.market.this_datetime.isocalendar()[1]

            # Beggining of the week
            if self.last_week != this_week:

                # If there are positions leftover from last week
                # e.g. when the market doesn't open past friday
                # will sell on this open
                if self.positions:
                    [self.sell(s, self.market.bars(s).this_open) for s in self.positions]

                list_pct_from_avg = self.create_ordered_list()

                if list_pct_from_avg:
                    ordered_list = sorted(list_pct_from_avg, key=lambda tup: tup[1])
                    list_to_buy = [s for s, pct_from_avg in ordered_list[0:self.max_positions]]
                    # Buy with this open price
                    [self.buy(s, self.market.bars(s).this_open, 1) for s in list_to_buy]

                    self.last_week = this_week

            # Middle of the week
            self.take_profit(self.take_profit_pct)
            
            # End of the week
            if weekday == 4:
                # Sell on market close
                [self.sell(s, self.market.bars(s).this_close) for s in self.positions]
