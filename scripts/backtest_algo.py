#!/usr/bin/env python
import argparse
import importlib
import imp
import logging
import os
import sys
import botcoin


def load_script(filename, datadir, graph=False, all_trades=False, verbose=False):

    if verbose:
        botcoin.settings.VERBOSITY = 10
    logging.basicConfig(format=botcoin.settings.LOG_FORMAT, level=botcoin.settings.VERBOSITY)

    directory, file_to_load = os.path.split(os.path.abspath(filename))
    sys.path.append(directory)
    try:
        strategy_module = __import__(file_to_load.split('.')[0])
    except ImportError:
        pass

    if 'strategy_module' not in locals():
        raise ValueError('Could not understand your strategy file')

    datadir = os.path.expanduser(datadir)

    # Run backtest
    backtest = botcoin.Backtest(_find_strategies(strategy_module), datadir)

    print(backtest.results)

    if all_trades:
        backtest.print_all_trades()

    if graph:
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

def main():
    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument(dest='algo_file', nargs='+', help='file with strategy scripts')
    parser.add_argument('-d', '--datadir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    parser.add_argument('-g', '--graph', action='store_true', help='graph equity curve')
    parser.add_argument('-a', '--all_trades', action='store_true', help='print all_trades dataframe')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose (very chatty, be careful)')
    args = parser.parse_args()

    load_script(args.algo_file[0], args.datadir, graph=args.graph, all_trades=args.all_trades, verbose=args.verbose)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
        sys.exit()
