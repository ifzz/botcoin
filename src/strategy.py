import logging

from .event import SignalEvent

class Strategy(object):
    """
    Strategy parent class.
        position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, market):
        self.market = market
        self.symbol_list = self.market.symbol_list

        self.positions = {symbol: None for symbol in self.symbol_list}

    def buy(self, symbol):
        self.positions[symbol] = 'LONG'
        return SignalEvent(symbol,'LONG')

    def short(self, symbol):
        self.positions[symbol] = 'SHORT'
        return SignalEvent(symbol,'SHORT')

    def exit(self, symbol):
        self.positions[symbol] = ''
        return SignalEvent(symbol,'EXIT')

class RandomBuyStrategy(Strategy):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, market, parameters=[5, 5]):
        Strategy.__init__(self, market)
        self.interval = parameters[0]
        self.hold = parameters[1]
        self.floating_interval = self.interval

    def generate_signals(self):
        signals = []
        for s in self.symbol_list:
            if self.floating_interval == 0:
                if not self.positions[s]:
                    self.floating_interval = self.hold  
                    signals.append(self.buy(s))

                elif self.positions[s] == 'LONG':
                    self.floating_interval = self.interval
                    signals.append(self.exit(s))
            self.floating_interval -= 1
        return signals