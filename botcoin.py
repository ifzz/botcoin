#!/usr/bin/env python3
import os
import sys
import time
import pandas
from datetime import timedelta, datetime
from data import openp, highp, lowp, closep, vol
from data import HistoricalCSV


csv_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'
filename = 'btceUSD_5Min.csv'
filetype = 'ohlc'
date_to = datetime.now()
date_from = datetime.now() - timedelta(weeks=10)


def backtest():
    global csv_dir, filename, filetype, date_to, date_from
    
    time_started = datetime.now()

    #Load CSV file
    data = HistoricalCSV(csv_dir, filename, filetype, date_from = date_from, date_to = date_to)
    
    time_backtest = datetime.now()

    #Start backtest
    while data.continue_backtest:
        data.update_bars()

        latest_bars =  data.get_latest_bars(20)


    print('# Data load took',str(time_backtest-time_started))
    print('# Backtest took',str(datetime.now()-time_backtest))
    print('# Done')

if __name__ == '__main__':
    try:
        backtest()
    except KeyboardInterrupt as e:
        sys.exit('# Execution interrupted')
