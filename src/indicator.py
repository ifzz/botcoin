"""
Module with indicator methods, e.g. moving averages, bollinger bands, etc. 
"""
import numpy as np
import pandas as pd

def list_to_series(prices):
    if isinstance(prices, list):
        return pd.Series(prices)
    else:
        return prices

def ma(prices):
    return np.round(np.mean(prices),3)

def bbands(prices, k):
    """ returns average, upper band, and lower band"""
    ave = np.mean(prices)
    sd = np.std(prices)
    upband = ave + (sd*k)
    lwband = ave - (sd*k)
    return np.round(ave,3), np.round(upband,3), np.round(lwband,3)


