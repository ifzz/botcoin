#!/usr/bin/env python
import pandas as pd

class RandomBuyForAnInterval(object):
    """
    Buys the asset every 1-n candles, and holds it for an entire candle

    data -- data object containing bars
    position -- current position held (LONG, SHORT or None)
    """
    def __init__(self,data,n):
        self.data = data
        self.position = None
        self.n = n

    def calculate_signals(self):
        if self.position == None:
            pass
        elif self.position == 'LONG':
            #Send order signal to exit position
            pass
