#!/usr/bin/env python
import logging

from src.event import SignalEvent

class Strategy(object):
    """
    Strategy parent class.
        position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, data):
        self.position = None
        self.data = data

    def go_long(self):
        logging.debug('LONG signal from strategy ' + self.__class__.__name__ + ' close price is ' + str(self.data.get_latest_bars(self.symbol).close[0])) #TODO CHECK THIS SHIT close[0] is not really the last one is it?
        self.position = 'LONG'
        return SignalEvent('btc','LONG')

    def exit(self):
        logging.debug('EXIT signal from strategy ' + self.__class__.__name__ + ' close price is ' + str(self.data.get_latest_bars(self.symbol).close[0])) #TODO CHECK THIS SHIT
        self.position = ''
        return SignalEvent('btc','EXIT')

class RandomBuyStrategy(Strategy):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, data, interval=10, hold=10):
        Strategy.__init__(self, symbol, data)
        self.interval = interval
        self.hold = hold
        self._reset_interval()

    def _reset_interval(self):
        self.floating_interval = self.interval

    def _reset_hold(self):
        self.floating_interval = self.hold

    def generate_signals(self):
        if self.floating_interval == 0:
            if not self.position:
                self._reset_hold()
                return self.go_long()

            elif self.position == 'LONG':
                self._reset_interval()
                return self.exit()

        else:
            self.floating_interval -= 1
