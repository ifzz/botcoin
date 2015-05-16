#!/usr/bin/env python

import pandas
from datetime import timedelta, datetime
from data import HistoricalCSV

#Debug offset='5T' when reading tick data

if __name__ == '__main__':
    date_from = datetime.now() - timedelta(weeks=10)

    data = HistoricalCSV(
        '/home/lteixeira/Projects/botcoin/data/',
        'btceUSD_5Min.csv',
        'ohlc',
        date_from=date_from,
    )
    
    while data.continue_backtest:
        data.update_bars()

    print data.get_latest_bars(20)

    print '# Done'
