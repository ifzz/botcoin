#!/usr/bin/env python
import argparse
import logging
import os
import sys
import botcoin

def find_strategies(filename, datadir):
    """ Tries to find strategies in modulo provided in the following ways:
        1) looks for strategies attribute, which shoud be a list of Strategy subclasses
        2) looks for strategy attribute, which should be an instance of a Strategy subclasses
        3) tries to instantiate the first subclass of botcoin.Strategy it can find with no parameters
    """
    directory, file_to_load = os.path.split(os.path.abspath(filename))
    sys.path.append(directory)

    strategy_module = __import__(file_to_load.split('.')[0])

    datadir = os.path.expanduser(datadir)

    try:
        return strategy_module.strategies
    except AttributeError:
        pass
    try:
        return [strategy_module.strategy]
    except AttributeError:
        pass
    import inspect
    for name, cls in inspect.getmembers(strategy_module, inspect.isclass):
        if issubclass(cls, botcoin.Strategy):
            return [cls()]

    raise ValueError('Could not understand your strategy script')

def load_script(filename, datadir, graph_equity=False, graph_subscriptions=False, all_trades=False, verbose=False,):

    if verbose:
        botcoin.settings.VERBOSITY = 10
    logging.basicConfig(format=botcoin.settings.LOG_FORMAT, level=botcoin.settings.VERBOSITY)


    # Run backtest
    backtest = botcoin.Backtest(find_strategies(filename, datadir), datadir)

    print(backtest.results)

    if all_trades:
        backtest.print_all_trades()

    if graph_equity:
        backtest.plot_results()

    if graph_subscriptions:
        backtest.plot_symbol_subscriptions()

    backtest.strategy_finishing_methods()

    return backtest


def main():
    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument(dest='algo_file', nargs='+', help='file with strategy scripts')
    parser.add_argument('-d', '--datadir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    parser.add_argument('-g', '--graph_equity', action='store_true', help='graph equity curve')
    parser.add_argument('-s', '--graph_subscriptions', action='store_true', help='graph symbol subscriptions')
    parser.add_argument('-a', '--all_trades', action='store_true', help='print all_trades dataframe')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose (very chatty, be careful)')
    args = parser.parse_args()

    load_script(
        args.algo_file[0], args.datadir, graph_equity=args.graph_equity,
        graph_subscriptions=args.graph_subscriptions, all_trades=args.all_trades,
        verbose=args.verbose,)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
