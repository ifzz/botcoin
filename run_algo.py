#!/usr/bin/env python
import argparse
import importlib
import imp
import logging
import os
import sys

import botcoin


def load_script(filename=None):

    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument('-f', '--file', required=False, nargs='?', help='file with strategy scripts')
    parser.add_argument('-g', '--graph', action='store_true', help='graph equity curve')
    parser.add_argument('-a', '--all_trades', action='store_true', help='print all_trades dataframe')
    parser.add_argument('-d', '--debug', action='store_true', help='debugging (very verbose, be careful)')
    args = parser.parse_args()

    if args.debug:
        botcoin.settings.VERBOSITY = 10
    logging.basicConfig(format=botcoin.settings.LOG_FORMAT, level=botcoin.settings.VERBOSITY)


    filename = args.file or filename
    if filename:
        directory, file_to_load = os.path.split(os.path.abspath(filename))
        sys.path.append(directory)
        strategy_module = __import__(file_to_load.split('.')[0])
    else:
        try:
            import custom as strategy_module
        except ImportError:
            logging.critical("No strategy found")
            sys.exit()


    # Run backtest
    backtest = botcoin.Backtest(_find_strategies(strategy_module))

    print(backtest.results)

    if args.all_trades:
        backtest.print_all_trades()

    if args.graph:
        backtest.plot_results()

    backtest.strategy_finishing_methods()

    return backtest

def _find_strategies(module):
    """ Tries to find strategies in file provided to this script in the following ways:
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
        if issubclass(cls, botcoin.Strategy):
            return [cls()]

    raise ValueError('Could not understand your strategy script')


if __name__ == '__main__':
    try:
        load_script()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
        sys.exit()
