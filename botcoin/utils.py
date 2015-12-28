import inspect
import itertools
import logging
from math import floor
import numpy as np
import pandas as pd
import os
import sys

from .common.strategy import Strategy

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


def _find_strategies(filename, load_default_only=False):
    """ Tries to find strategies in the module provided in the following ways:
        1) looks for strategies attribute, which shoud be a list of Strategy subclasses
        2) looks for strategy attribute, which should be an instance of a Strategy subclasses
        3) tries to instantiate the first subclass of botcoin.Strategy it can find with no parameters

        Returns list of strategies.
    """
    directory, file_to_load = os.path.split(os.path.abspath(filename))
    sys.path.append(directory)

    strategy_module = __import__(file_to_load.split('.')[0])

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

def _basic_config(verbose=None):
    # Logging
    verbosity = 10 if verbose else 20
    log_format = '# %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format, level=verbosity)

    # Pandas
    pd.set_option('display.max_rows', 200)
    pd.set_option('display.width', 1000)

def _grab_settings_from_strategy(strategy):
    from . import settings
    global ROUND_DECIMALS, ROUND_DECIMALS_BELOW_ONE
    d = {}

    d['NORMALIZE_PRICES'] = getattr(strategy, 'NORMALIZE_PRICES', settings.NORMALIZE_PRICES)
    d['NORMALIZE_VOLUME'] = getattr(strategy, 'NORMALIZE_VOLUME', settings.NORMALIZE_VOLUME)
    d['CURRENCY'] = getattr(strategy, 'CURRENCY', settings.CURRENCY)
    d['EXCHANGE'] = getattr(strategy, 'EXCHANGE', settings.EXCHANGE)
    d['SEC_TYPE'] = getattr(strategy, 'SEC_TYPE', settings.SEC_TYPE)
    d['INITIAL_CAPITAL'] = getattr(strategy, 'INITIAL_CAPITAL', settings.INITIAL_CAPITAL)
    d['CAPITAL_TRADABLE_CAP'] = getattr(strategy, 'CAPITAL_TRADABLE_CAP', settings.CAPITAL_TRADABLE_CAP)
    d['ROUND_LOT_SIZE'] = getattr(strategy, 'ROUND_LOT_SIZE', settings.ROUND_LOT_SIZE)
    d['COMMISSION_FIXED'] = getattr(strategy, 'COMMISSION_FIXED', settings.COMMISSION_FIXED)
    d['COMMISSION_PCT'] = getattr(strategy, 'COMMISSION_PCT', settings.COMMISSION_PCT)
    d['COMMISSION_MIN'] = getattr(strategy, 'COMMISSION_MIN', settings.COMMISSION_MIN)
    d['MAX_SLIPPAGE'] = getattr(strategy, 'MAX_SLIPPAGE', settings.MAX_SLIPPAGE)
    d['MAX_LONG_POSITIONS'] = floor(getattr(strategy, 'MAX_LONG_POSITIONS', settings.MAX_LONG_POSITIONS))
    d['MAX_SHORT_POSITIONS'] = floor(getattr(strategy, 'MAX_SHORT_POSITIONS', settings.MAX_SHORT_POSITIONS))
    d['POSITION_SIZE'] = getattr(strategy, 'POSITION_SIZE', 1.0/d['MAX_LONG_POSITIONS'] if d['MAX_LONG_POSITIONS'] else 1.0/d['MAX_SHORT_POSITIONS'])
    d['ADJUST_POSITION_DOWN'] = getattr(strategy, 'ADJUST_POSITION_DOWN', settings.ADJUST_POSITION_DOWN)
    d['THRESHOLD_DANGEROUS_TRADE'] = getattr(strategy, 'THRESHOLD_DANGEROUS_TRADE', settings.THRESHOLD_DANGEROUS_TRADE)
    d['ROUND_DECIMALS'] = ROUND_DECIMALS = getattr(strategy, 'ROUND_DECIMALS', settings.ROUND_DECIMALS)
    d['ROUND_DECIMALS_BELOW_ONE'] = ROUND_DECIMALS_BELOW_ONE = getattr(strategy, 'ROUND_DECIMALS_BELOW_ONE', settings.ROUND_DECIMALS_BELOW_ONE)
    return d

def _round(value):
    if value >= 1:
        return np.round(value, ROUND_DECIMALS)
    else:
        return np.round(value, ROUND_DECIMALS_BELOW_ONE)
