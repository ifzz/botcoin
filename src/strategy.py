import logging

import numpy as np

from .event import SignalEvent
from .indicator import ma, bbands

class Strategy(object):
    """
    Strategy parent class.
        position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, parameters):
        pass

    def __str__(self):
        return self.__class__.__name__ + " with parameters " + ", ".join([str(i) for i in self.parameters])

    def set_market_and_queue(self, events_queue, market):
        self.events_queue = events_queue
        self.market = market
        self.symbol_list = self.market.symbol_list
        self.positions = {}

    def buy(self, symbol, price=None):
        self.positions[symbol] = 'BUY'
        self.add_signal(symbol, 'BUY', price)

    def sell(self, symbol, price=None):
        del(self.positions[symbol])
        self.add_signal(symbol, 'SELL', price)

    def short(self, symbol, price=None):
        self.positions[symbol] = 'SHORT'
        self.add_signal(symbol, 'SHORT', price)

    def cover(self, symbol, price=None):
        del(self.positions[symbol])
        self.add_signal(symbol, 'COVER', price)

    def add_signal(self, symbol, sig_type, price=None):
        price = price or self.market.bars(symbol).this_close
        self.events_queue.put(SignalEvent(symbol, sig_type, price))

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

    def generate_signals(self):
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

    def generate_signals(self):
        for s in self.symbol_list:
            slow = self.market.bars(s, self.slow).close
            fast = self.market.bars(s, self.fast).close
            if len(slow) == self.slow:
                if self.positions[s]:
                    if ma(fast) <= ma(slow):
                        self.sell(s)

                else:
                    if ma(fast) >= ma(slow):
                        self.buy(s)

class BBStrategy(Strategy):
    def __init__(self, parameters):
        self.parameters = parameters
        self.length = parameters[0]
        self.k = parameters[1]

    def generate_signals(self):
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

    def generate_signals(self):
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

class MeanRevertingWeeklyStrategy(Strategy):

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

        def generate_signals(self):
            list_pct_from_avg = self.create_ordered_list()

            # Generating signals for the extremes in the list
            if list_pct_from_avg:
                ordered_list = sorted(list_pct_from_avg, key=lambda tup: tup[1])
                list_to_buy = ordered_list[0:self.max_positions]
                list_to_sell = [s for s in self.positions if s not in list_to_buy]
                # print("Selling {}.\nBuying {}".format(list_to_sell,list_to_buy))
                # input()
                # selling on open of this bar
                [self.sell(s, self.market.bars(s).this_open) for s in list_to_sell]

                #, self.market.bars(s).this_open
                [self.buy(s, self.market.bars(s).this_close) for s,pct_from_avg in list_to_buy if s not in self.positions]
                        
