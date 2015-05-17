#!/usr/bin/env python

import pandas
from datetime import timedelta, datetime
from data import HistoricalCSV

#Debug offset='5T' when reading tick data

if __name__ == '__main__':
    
    date_to = datetime.now()
    date_from = datetime.now() - timedelta(weeks=10)
    

    data = HistoricalCSV(
        '/home/lteixeira/Projects/botcoin/data/',
        'btceUSD_5Min.csv',
        'ohlc',
        date_from = date_from,
        date_to = date_to,
    )
    
    while data.continue_backtest:
        data.update_bars()

    latest_bars =  data.get_latest_bars(20)
    #open
    o = [i[2] for i in latest_bars]
    #close
    c = [i[4] for i in latest_bars]

    print o
    print c
    print '# Done'
