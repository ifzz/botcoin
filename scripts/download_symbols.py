#!/usr/bin/env python
import argparse
from datetime import datetime
import logging
import numpy as np
import pandas as pd
import os
import sys
import urllib.request
from urllib.request import HTTPError

from botcoin.utils import _find_strategies, _basic_config

# Data APIs
YAHOO_API = 'http://ichart.finance.yahoo.com/table.csv?s={}&c={}&g={}' # symbol, year_from, period
YAHOO_API_2 = 'http://download.finance.yahoo.com/d/quotes.csv?s={}&f=sl1d1t1c1ohgv&e=.csv'
YAHOO_CHART_API = 'http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range={}/csv'
QUANDL_YAHOO_API = 'https://www.quandl.com/api/v3/datasets/YAHOO/{}_{}.csv'
QUANDL_YAHOO_API_AUTH = 'https://www.quandl.com/api/v3/datasets/YAHOO/{}_{}.csv?api_key={}'

def main():
    parser = argparse.ArgumentParser(description='Downloads symbol data from Yahoo.')
    parser.add_argument(dest='algo_file', nargs='*', help='file with strategy scripts')
    parser.add_argument('-d', '--data_dir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    parser.add_argument('-s', '--symbols', nargs='+', help='Space separated symbols (used instead of symbol_list in strategy file)')
    parser.add_argument('-y', '--yahoo_suffix', help='Yahoo suffix to be appended to symbols (e.g. .AX for ASX or .NZ for NZX)')
    args = parser.parse_args()

    _basic_config()

    if args.symbols:
        symbol_list = args.symbols
        yahoo_suffix = args.yahoo_suffix or ''
    else:
        strategy = _find_strategies(args.algo_file[0], True)[0]
        symbol_list = strategy.SYMBOL_LIST
        yahoo_suffix = args.yahoo_suffix or getattr(strategy, 'YAHOO_SUFFIX', '')

    logging.info("Downloading {} symbols from Yahoo with suffix '{}'. Please wait.".format(len(symbol_list),yahoo_suffix))

    start_load_datetime = datetime.now()

    for symbol in symbol_list:

        url = YAHOO_API.format(symbol + yahoo_suffix, '1990', 'd')
        try:
            csv = urllib.request.urlopen(url)#.read().decode('utf-8')
            df = pd.io.parsers.read_csv(
                csv,
                header=0,
                index_col=0,
                names=['datetime', 'open', 'high', 'low', 'close', 'volume', 'adj_close'],
            )
            df = df.reindex(index=df.index[::-1])

            if False: #remove_adj_close:
                df.drop('Adj Close', axis=1, inplace=True)

            # Checking data consistency
            if (df['high'] < df['open']).any() == True:
                dates = df.loc[(df['high'] < df['open']) == True].index
                logging.info('Inconsistent data detected - {} high < open on {}'.format(symbol, dates))
                # df['high'] = np.where(df['high'] < df['open'], df['open'], df['high'])
                # logging.info('Fixed {} high < open on {}'.format(symbol, dates))

            if (df['high'] < df['close']).any() == True:
                dates = df.loc[(df['high'] < df['close']) == True].index
                logging.info('Inconsistent data detected - {} high < close on {}'.format(symbol, dates))
                # df['high'] = np.where(df['high'] < df['close'], df['close'], df['high'])
                # logging.info('Fixed {} high < close on {}'.format(symbol, dates))

            if (df['low'] > df['open']).any() == True:
                dates = df.loc[(df['low'] > df['open']) == True].index
                logging.info('Inconsistent data detected - {} low > open on {}'.format(symbol, dates))
                # df['low'] = np.where(df['low'] > df['open'], df['open'], df['low'])
                # logging.info('Fixed {} low > open on {}'.format(symbol, dates))

            if (df['low'] > df['close']).any() == True:
                dates = df.loc[(df['low'] > df['close']) == True].index
                logging.info('Inconsistent data detected - {} low > close on {}'.format(symbol, dates))
                # df['low'] = np.where(df['low'] > df['close'], df['close'], df['low'])
                # logging.info('Fixed {} low > close on {}'.format(symbol, dates))

            if (df['high'] < df['low']).any() == True:
                dates = df.loc[(df['high'] < df['low']) == True].index
                logging.info('Inconsistent data detected - {} high < low on {}'.format(symbol, dates))
                # df['high'] = np.where(df['high'] < df['low'], df['low'], df['high'])
                # logging.info('Fixed {} high < low on {}'.format(symbol, dates))

            # Write csv
            df.to_csv(os.path.join(args.data_dir, symbol+'.csv'), header=False)

        except HTTPError as e:
            logging.error('Failed to fetch {}. Error: {}. URL: {}'.format(symbol, e, url))

    logging.info('Data download took {}'.format(datetime.now()-start_load_datetime))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
