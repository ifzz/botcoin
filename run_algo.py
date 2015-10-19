#!/usr/bin/env python
import argparse
import importlib
import imp
import logging
import os
import sys

import botcoin

def find_strategies(module):
    """ Tries to find strategies in file provided to this script in the following ways:
        1) looks for strategies attribute, which shoud be a list of Strategy subclasses
        2) looks for strategy attribute, which should be an instance of a Strategy subclasses
        3) tries to instantiate the first subclass of botcoin.Strategy it can find with no parameters
    """
    try:
        return module.strategies
    except AttributeError as e:
        pass        

    try:
        return [module.strategy]
    except AttributeError as e:
        pass

    try:
        logging.debug("No strategy/strategies attribute found, will instantiate \
            first subclass of botcoin.Strategy found.")
        import inspect
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, botcoin.Strategy):
                return [cls()]
    except AttributeError as e:
        pass

    raise ValueError('Could not understand your strategy script')


def load_strategies():

    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument('-f', '--file', required=False, nargs='?', help='file with strategy scripts')
    parser.add_argument('-g', '--graph', action='store_true', help='graph equity curve')
    parser.add_argument('-a', '--all_trades', action='store_true', help='print all_trades dataframe')
    args = parser.parse_args()


    # Import file
    if args.file:
        directory, file_to_load = os.path.split(os.path.abspath(args.file))
        sys.path.append(directory)
        strategy_module = __import__(file_to_load.split('.')[0])
    else:
        import custom as strategy_module


    # Run backtest
    backtest = botcoin.Backtest(find_strategies(strategy_module))

    print(backtest.results)

    if args.all_trades:
        backtest.print_all_trades()

    if args.graph:
        backtest.plot_results()

    return backtest


if __name__ == '__main__':
    try:
        load_strategies()
    except KeyboardInterrupt:
        sys.exit("# Execution stopped")
