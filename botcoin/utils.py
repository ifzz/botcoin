import inspect
import itertools
import logging
import numpy as np
import pandas as pd
import os
import sys
import urllib.request
from urllib.request import HTTPError

from botcoin import Strategy

# Data APIs
YAHOO_CHART_API = 'http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range={}/csv'
YAHOO_API = 'http://ichart.finance.yahoo.com/table.csv?s={}&c={}&g={}'
YAHOO_API_2 = 'http://download.finance.yahoo.com/d/quotes.csv?s={}&f=sl1d1t1c1ohgv&e=.csv'


def yahoo_api(list_of_symbols, data_dir, year_from=1900, period='d', remove_adj_close=False):

    logging.warning("Downloading {} symbols from Yahoo. Please wait.".format(len(list_of_symbols)))

    for s in list_of_symbols:
        try:
            csv = urllib.request.urlopen(YAHOO_API.format(s,year_from,period))#.read().decode('utf-8')
            df = pd.io.parsers.read_csv(
                csv,
                header=0,
                index_col=0,
            )
            df = df.reindex(index=df.index[::-1])
            if remove_adj_close:
                df.drop('Adj Close', axis=1, inplace=True)
            df.to_csv(os.path.join(data_dir, s+'.csv'), header=False)
        except HTTPError:
            logging.error('Failed to fetch {}'.format(s))


def optimize(*args):
    """
        Returns all possible combinations of multiple np.arange values based on
        tuples passed to this method. Exposed externally, to be used in backtesting.
    """
    if not args:
        return
    elif len(args) == 1:
        a = args[0]
        return np.arange(a[0],a[1],a[2])
    else:
        lists_of_elements = [np.arange(a[0],a[1],a[2]) for a in args]
        return list(itertools.product(*lists_of_elements))


def _find_strategies(filename, datadir, load_default_only=False):
    """ Tries to find strategies in the module provided in the following ways:
        1) looks for strategies attribute, which shoud be a list of Strategy subclasses
        2) looks for strategy attribute, which should be an instance of a Strategy subclasses
        3) tries to instantiate the first subclass of botcoin.Strategy it can find with no parameters

        Returns list of strategies.
    """
    directory, file_to_load = os.path.split(os.path.abspath(filename))
    sys.path.append(directory)

    strategy_module = __import__(file_to_load.split('.')[0])

    datadir = os.path.expanduser(datadir)

    if not load_default_only:
        try:
            return strategy_module.strategies
        except AttributeError:
            pass

        try:
            return [strategy_module.strategy]
        except AttributeError:
            pass

    for name, cls in inspect.getmembers(strategy_module, inspect.isclass):
        if issubclass(cls, Strategy):
            return [cls()]

    raise ValueError('Could not understand your strategy script')
