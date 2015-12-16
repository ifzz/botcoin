import inspect
import itertools
import logging
import numpy as np
import pandas as pd
import os
import sys

from botcoin import Strategy

# Data APIs
YAHOO_API = 'http://ichart.finance.yahoo.com/table.csv?s={}&c={}&g={}' # symbol, year_from, period
YAHOO_API_2 = 'http://download.finance.yahoo.com/d/quotes.csv?s={}&f=sl1d1t1c1ohgv&e=.csv'
YAHOO_CHART_API = 'http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range={}/csv'
QUANDL_YAHOO_API = 'https://www.quandl.com/api/v3/datasets/YAHOO/{}_{}.csv'
QUANDL_YAHOO_API_AUTH = 'https://www.quandl.com/api/v3/datasets/YAHOO/{}_{}.csv?api_key={}'


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

def _config_logging(verbose):
    verbosity = 10 if verbose else 20
    log_format = '# %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format, level=verbosity)
