#!/usr/bin/env python
import argparse
from datetime import datetime
import logging
import pandas as pd
import os
import sys
import urllib.request
from urllib.request import HTTPError

from botcoin.utils import _find_strategies, _config_logging

# Data APIs
YAHOO_API = 'http://ichart.finance.yahoo.com/table.csv?s={}&c={}&g={}' # symbol, year_from, period
YAHOO_API_2 = 'http://download.finance.yahoo.com/d/quotes.csv?s={}&f=sl1d1t1c1ohgv&e=.csv'
YAHOO_CHART_API = 'http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range={}/csv'
QUANDL_YAHOO_API = 'https://www.quandl.com/api/v3/datasets/YAHOO/{}_{}.csv'
QUANDL_YAHOO_API_AUTH = 'https://www.quandl.com/api/v3/datasets/YAHOO/{}_{}.csv?api_key={}'

def main():
    parser = argparse.ArgumentParser(description='Downloads symbol data from Yahoo.')
    parser.add_argument(dest='algo_file', nargs='+', help='file with strategy scripts')
    parser.add_argument('-d', '--data_dir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    args = parser.parse_args()

    _config_logging()

    strategy = _find_strategies(args.algo_file[0], True)[0]

    logging.info("Downloading {} symbols from Yahoo. Please wait.".format(len(strategy.SYMBOL_LIST)))

    yahoo_symbol_appendix = getattr(strategy, 'YAHOO_SYMBOL_APPENDIX', '')
    start_load_datetime = datetime.now()

    for symbol in strategy.SYMBOL_LIST:

        url = YAHOO_API.format(symbol + yahoo_symbol_appendix, '1990', 'd')
        try:
            csv = urllib.request.urlopen(url)#.read().decode('utf-8')
            df = pd.io.parsers.read_csv(
                csv,
                header=0,
                index_col=0,
            )
            df = df.reindex(index=df.index[::-1])
            if False: #remove_adj_close:
                df.drop('Adj Close', axis=1, inplace=True)
            df.to_csv(os.path.join(args.data_dir, symbol+'.csv'), header=False)
        except HTTPError as e:
            logging.error('Failed to fetch {}. Error: {}. URL: {}'.format(symbol, e, url))

    logging.info('Data download took {}'.format(datetime.now()-start_load_datetime))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
