#!/usr/bin/env python
import logging

from src.event import SignalEvent

class Strategy(object):

    def go_long(self, bars):
        logging.debug('LONG signal from strategy ' + self.__class__.__name__ + ' close price is ' + str(bars.close()[0]))
        self.position = 'LONG'
        return SignalEvent('btc','LONG')

    def exit(self, bars):
        logging.debug('EXIT signal from strategy ' + self.__class__.__name__ + ' close price is ' + str(bars.close()[0]))
        self.position = ''
        return SignalEvent('btc','EXIT')

class RandomBuyStrategy(Strategy):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self, interval=10, hold=10):
        self.position = None
        self.interval = interval
        self.hold = hold
        self._reset_interval()

    def _reset_interval(self):
        self.floating_interval = self.interval

    def _reset_hold(self):
        self.floating_interval = self.hold

    def generate_signals(self, bars):
        if self.floating_interval == 0:
            if not self.position:
                self._reset_hold()
                logging.debug('going long - self.hold = ' + str(self.hold) + ' and floating = ' + str(self.floating_interval))
                return self.go_long(bars)    

            elif self.position == 'LONG':
                self._reset_interval()
                logging.debug('exiting - self.interval = ' + str(self.interval) + ' and floating = ' + str(self.floating_interval))
                return self.exit(bars)

        else:
            self.floating_interval -= 1