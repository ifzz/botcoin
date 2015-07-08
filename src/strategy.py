#!/usr/bin/env python
import logging

from src.event import SignalEvent

class Strategy(object):
    """
    Strategy parent class.
        position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, data):
        self.data = data
        self.symbol_list = self.data.symbol_list

        self.positions = {symbol: None for symbol in self.symbol_list}

    def buy(self, symbol):
        # logging.debug('LONG signal for ' + symbol + ' close price is ' + str(self.data.get_latest_bars(symbol).last_close)) #TODO CHECK THIS SHIT close[0] is not really the last one is it?
        self.positions[symbol] = 'LONG'
        return SignalEvent(symbol,'LONG')

    def short(self, symbol):
        # logging.debug('SHORT signal for ' + symbol + ' close price is ' + str(self.data.get_latest_bars(symbol).last_close)) #TODO CHECK THIS SHIT close[0] is not really the last one is it?
        self.positions[symbol] = 'SHORT'
        return SignalEvent(symbol,'SHORT')

    def exit(self, symbol):
        # logging.debug('EXIT signal for ' + symbol + ' close price is ' + str(self.data.get_latest_bars(symbol).last_close)) #TODO CHECK THIS SHIT
        self.positions[symbol] = ''
        return SignalEvent(symbol,'EXIT')

class RandomBuyStrategy(Strategy):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, data, interval=10, hold=10):
        Strategy.__init__(self, data)
        self.interval = interval
        self.hold = hold
        self._reset_interval()

    def _reset_interval(self):
        self.floating_interval = self.interval

    def _reset_hold(self):
        self.floating_interval = self.hold

    def generate_signals(self):
        signals = []
        for s in self.symbol_list:
            if self.floating_interval == 0:
                if not self.positions[s]:
                    self._reset_hold()
                    signals.append(self.buy(s))

                elif self.positions[s] == 'LONG':
                    self._reset_interval()
                    signals.append(self.exit(s))
            else:
                self.floating_interval -= 1
        return signals