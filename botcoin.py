#!/usr/bin/env python
import os
from datetime import timedelta, datetime
import queue
import sys
import time

import pandas

from src.data import HistoricalCSV
from src.strategy import RandomBuyForAnInterval

csv_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'
filename = 'btceUSD_5Min.csv'
filetype = 'ohlc'
date_to = datetime.now()
date_from = datetime.now() - timedelta(weeks=10)

def backtest(events, data, portofolio, strategy, execution):

    #Start backtest
    while data.continue_execution:

        events.put(data.update_bars())

        while True:
            try:
                event = events.get(False)
            except queue.Empty:
                break

            new_event = None

            if event.type == 'MARKET':
                new_event = strategy.calculate_signals()
            elif event.type == 'SIGNAL':
                pass
            elif event.type == 'ORDER':
                pass
            elif event.type == 'FILL':
                pass

            if new_event:
                print(new_event.type,data.get_latest_bars().datetime())
            #put new_event to events if new_event

def main():
    """Instantiate data, portfolio, strategy and execution classes."""
    
    global csv_dir, filename, filetype, data_to, data_from
    events = queue.Queue()

    print('# Starting data load')
    data = HistoricalCSV(csv_dir, filename, filetype, date_from = date_from, date_to = date_to)

    
    strategy = RandomBuyForAnInterval(data)
    portfolio = None
    execution = None

    time_backtest = datetime.now()
    print('# Starting backtest')
    backtest(events, data, portfolio, strategy, execution)
    
    print('# Data load took',data.load_time)
    print('# Backtest took',str(datetime.now()-time_backtest))
    print('# Done')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        sys.exit('# Execution interrupted')


