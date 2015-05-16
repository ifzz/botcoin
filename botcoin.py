#!/usr/bin/env python

import pandas
import datetime
from data import HistoricalCSV

class Strategy(object):
    """
    Strategy
    """

class Portfolio(object):
    """
    Portfolio - as simple
    """



if __name__ == '__main__':
    
    data = HistoricalCSV(
        '/home/lteixeira/Projects/botcoin/data/',
        'btceUSD_5Min.csv',
        'ohlc',
        date_from='2015-01-02',
    )
    
    while data.continue_backtest:
        data.update_bars()


    print '# Done'
