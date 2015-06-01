#!/usr/bin/env python

from src.event import SignalEvent

class RandomBuyForAnInterval(object):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    data -- data object containing bars
    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self,data):
        self.data = data
        self.position = None

    def calculate_signals(self):
        if not self.position:
            self.position = 'LONG'
            return SignalEvent('btc','LONG')
        elif self.position == 'LONG':
            #Send order signal to exit position
            pass
