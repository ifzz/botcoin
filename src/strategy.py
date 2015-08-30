import logging

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
        self.positions = {symbol: None for symbol in self.symbol_list}

    def buy(self, symbol, price=None):
        self.positions[symbol] = 'BUY'
        self.events_queue.put(SignalEvent(symbol,'BUY',price))

    def sell(self, symbol, price=None):
        self.positions[symbol] = ''
        self.events_queue.put(SignalEvent(symbol,'SELL',price))

    def short(self, symbol, price=None):
        self.positions[symbol] = 'SHORT'
        self.events_queue.put(SignalEvent(symbol,'SHORT',price))

    def cover(self, symbol, price=None):
        self.positions[symbol] = ''
        self.events_queue.put(SignalEvent(symbol,'COVER',price))

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
                
                if self.positions[s]:
                    if bars.last_high >= average:
                        self.sell(s)

                else:
                    if bars.last_low <= lwband:
                        self.buy(s)

class DonchianStrategy(Strategy):
    def __init__(self, parameters):
        self.parameters = parameters
        self.upper = parameters[0]
        self.lower = parameters[1]

    def generate_signals(self):
        for s in self.symbol_list:
            bars_upper = self.market.bars(s, self.upper)
            bars_lower = self.market.bars(s, self.lower)

            if (len(bars_lower) >= self.lower and len(bars_upper) >= self.upper):

                upband = max(bars_upper.high)
                lwband = min(bars_upper.low)
                bar = self.market.bars(s)

                if self.positions[s]:
                    if bar.low <= lwband:
                        self.sell(s)

                else:
                    if bar.high >= upband:
                        self.buy(s)

        