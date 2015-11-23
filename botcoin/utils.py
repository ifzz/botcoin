import itertools
import logging
import numpy as np

from botcoin.strategy import Strategy

def optimize(*args):
    if not args:
        return
    elif len(args) == 1:
        a = args[0]
        return np.arange(a[0],a[1],a[2])
    else:
        lists_of_elements = [np.arange(a[0],a[1],a[2]) for a in args]
        return list(itertools.product(*lists_of_elements))

def find_strategies(module):
    """ Tries to find strategies in modulo provided in the following ways:
        1) looks for strategies attribute, which shoud be a list of Strategy subclasses
        2) looks for strategy attribute, which should be an instance of a Strategy subclasses
        3) tries to instantiate the first subclass of botcoin.Strategy it can find with no parameters
    """
    try:
        return module.strategies
    except AttributeError:
        pass

    try:
        return [module.strategy]
    except AttributeError:
        pass

    logging.debug("No strategy/strategies attribute found, will instantiate " +
        "first subclass of botcoin.Strategy found.")
    import inspect
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if issubclass(cls, Strategy):
            return [cls()]

    raise ValueError('Could not understand your strategy script')
