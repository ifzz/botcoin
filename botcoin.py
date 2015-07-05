#!/usr/bin/env python
import argparse
import os
from datetime import timedelta, datetime
import logging
import sys
import time

from src.data import HistoricalCSV
from src.strategy import RandomBuyStrategy
from src.portfolio import Portfolio
from src.trade import Backtest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--params', nargs='+', required=False, help='strategy parameters')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='verbose info (-vv for debug)')
    parser.add_argument('-d', '--directory', required=False, nargs='?', help='alternative data directory')
    parser.add_argument('-f', '--filename', required=False, nargs='?', help='csv filename for historical data')

    args = parser.parse_args()

    # Strategy parameters
    params = [int(p) for p in args.params]

    # Data directory
    csv_dir = os.path.expanduser(args.directory) if args.directory else os.path.dirname(os.path.realpath(__file__)) + '/data/'
    # CSV filename
    filename = args.filename or ['btceUSD_5Min.csv']
    date_to = datetime.now()
    date_from = datetime.strptime("2015-01-01", '%Y-%m-%d') 
    #date_from = datetime.now() - timedelta(weeks=10)

    # Logging level
    if args.verbose == 1:
        logging.basicConfig(level=20)
    if args.verbose >= 2:
        logging.basicConfig(level=10)


    data = HistoricalCSV(csv_dir, filename, date_from = date_from, date_to = date_to)

    strategy = RandomBuyStrategy(data, params[0],params[1])

    portfolio = Portfolio(data, date_from, strategy=strategy)

    backtest = Backtest(data, portfolio, date_from, date_to)

    backtest.start()

if __name__ == '__main__':
    try:
        main()
        logging.info('# Done')
    except KeyboardInterrupt as e:
        logging.critical('# Execution interrupted')
        sys.exit()
