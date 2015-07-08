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
    parser.add_argument('-s', '--symbol_list', required=False, nargs='?', help='symbol list')

    args = parser.parse_args()

    # Strategy parameters
    params = [int(p) for p in args.params]

    csv_dir = os.path.expanduser(args.directory) if args.directory else os.path.dirname(os.path.realpath(__file__)) + '/data/'
    
    symbol_list = args.symbol_list or ['btceUSD_5Min']

    date_to = datetime.now()
    date_from = datetime.strptime("2015-01-01", '%Y-%m-%d') #date_from = datetime.now() - timedelta(weeks=10)

    # Logging config
    log_format = '# %(message)s'
    level=30
    if args.verbose == 1:
        level=20
    if args.verbose >= 2:
        level=10
        log_format = '# %(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s'
    logging.basicConfig(format=log_format, level=level)  


    data = HistoricalCSV(csv_dir, symbol_list, date_from=date_from, date_to=date_to)

    strategy = RandomBuyStrategy(data, params[0],params[1])

    portfolio = Portfolio(data, date_from, strategy=strategy)

    backtest = Backtest(data, portfolio, date_from, date_to)

    logging.debug('Data load time ' + str(data.load_time))
    logging.info('Starting backtest from ' + str(date_from) + ' to ' + str(date_to))

    backtest.start()

if __name__ == '__main__':
    try:
        main()
        logging.info('Done')
    except KeyboardInterrupt as e:
        logging.critical('Execution interrupted')
        sys.exit()
