#!/usr/bin/env python
import pandas
from datetime import timedelta, datetime
from data import openp, highp, lowp, closep, vol
from data import HistoricalCSV
import os

if __name__ == '__main__':
    
    csv_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'

    date_to = datetime.now()
    date_from = datetime.now() - timedelta(weeks=10)

    data = HistoricalCSV(
        csv_dir,
        'btceUSD_5Min.csv',
        'ohlc',
        date_from = date_from,
        date_to = date_to,
    )
    
    #Start backtesting
    while data.continue_backtest:
        data.update_bars()

        latest_bars =  data.get_latest_bars(20)
    
    

    print '# Done backtesting'
