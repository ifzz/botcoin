import logging

from .event import SignalEvent

class Strategy(object):
    """
    Strategy parent class.
        position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, events_queue, market, parameters):
        self.events_queue = events_queue
        self.market = market
        self.parameters = parameters
        self.symbol_list = self.market.symbol_list

        self.positions = {symbol: None for symbol in self.symbol_list}

    def buy(self, symbol):
        self.positions[symbol] = 'BUY'
        return SignalEvent(symbol,'BUY')

    def exit(self, symbol):
        self.positions[symbol] = ''
        return SignalEvent(symbol,'SELL')

    def short(self, symbol):
        self.positions[symbol] = 'SHORT'
        return SignalEvent(symbol,'SHORT')

    def cover(self, symbol):
        self.positions[symbol] = ''
        return SignalEvent(symbol,'COVER')

class RandomBuyStrategy(Strategy):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, events_queue, market, parameters=[5, 5]):
        Strategy.__init__(self, events_queue, market, parameters)
        self.interval = parameters[0]
        self.hold = parameters[1]
        self.floating_interval = self.interval

    def generate_signals(self):
        for s in self.symbol_list:
            if self.floating_interval == 0:
                if not self.positions[s]:
                    self.floating_interval = self.hold  
                    self.events_queue.put(self.buy(s))

                elif self.positions[s] == 'BUY':
                    self.floating_interval = self.interval
                    self.events_queue.put(self.exit(s))
            self.floating_interval -= 1
