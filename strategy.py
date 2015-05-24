#!/usr/bin/env python
import pandas as pd

class RandomBuyForAnInterval(object):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    data -- data object containing bars
    position -- current position held (LONG, SHORT or EXIT)
    """
    def __init__(self,events,data):
        self.data = data
        self.events = events
        self.position = None

    def calculate_signals(self):
        if self.position == 'EXIT':
            pass
        elif self.position == 'LONG':
            #Send order signal to exit position
            pass
