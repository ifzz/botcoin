#!/usr/bin/env python
import os
import sys
import time
import pandas
from datetime import timedelta, datetime
import Queue

from data import HistoricalCSV
from event import *


csv_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'
filename = 'btceUSD_1h.csv'
filetype = 'ohlc'
date_to = datetime.now()
date_from = datetime.now() - timedelta(weeks=10)

def backtest(data, portofolio, strategy, execution):

    #Start backtest
    while data.continue_execution:
        
        data.update_bars()

        while True:
            try:
                event = events.get(False)
            except Queue.Empty:
                break

            if event.type == 'MARKET':
                strategy.calculate_signals()
            elif event.type == 'SIGNAL':
                pass
            elif event.type == 'ORDER':
                pass
            elif event.type == 'FILL':
                pass

def main():
    """Instantiate data, portfolio, strategy and execution classes."""
    
    global csv_dir, filename, filetype, data_to, data_from
    events = Queue.Queue()

    print '# Starting data load'
    data = HistoricalCSV(events, csv_dir, filename, filetype, date_from = date_from, date_to = date_to)

    portfolio = None
    strategy = None
    execution = None

    time_backtest = datetime.now()
    print '# Starting backtest'
    backtest(events, data, portfolio, strategy, execution)
    
    print '# Data load took',data.load_time    
    print '# Backtest took',str(datetime.now()-time_backtest)
    print '# Done'


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        sys.exit('# Execution interrupted')


