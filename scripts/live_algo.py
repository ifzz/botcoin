 #! /usr/bin/env python
import argparse
import inspect
import logging
import os
import sys
import botcoin

def find_strategies(filename, datadir):
    """ Tries to instantiate the first subclass of botcoin.Strategy it can find with no parameters """
    directory, file_to_load = os.path.split(os.path.abspath(filename))
    sys.path.append(directory)

    strategy_module = __import__(file_to_load.split('.')[0])

    datadir = os.path.expanduser(datadir)

    for name, cls in inspect.getmembers(strategy_module, inspect.isclass):
        if issubclass(cls, botcoin.Strategy):
            return [cls()]

def load_script(filename, datadir, graph=False, all_trades=False, subscriptions=False, verbose=False,):

    if verbose:
        botcoin.settings.VERBOSITY = 10
    logging.basicConfig(format=botcoin.settings.LOG_FORMAT, level=botcoin.settings.VERBOSITY)

    # Run backtest
    live = botcoin.LiveEngine(find_strategies(filename, datadir), datadir)

    live.start()

def main():
    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument(dest='algo_file', nargs='+', help='file with strategy scripts')
    parser.add_argument('-d', '--datadir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    parser.add_argument('-g', '--graph', action='store_true', help='graph equity curve')
    parser.add_argument('-s', '--subscriptions', action='store_true', help='graph symbol subscriptions')
    parser.add_argument('-a', '--all_trades', action='store_true', help='print all_trades dataframe')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose (very chatty, be careful)')
    args = parser.parse_args()

    load_script(
        args.algo_file[0], args.datadir, graph=args.graph,
        all_trades=args.all_trades, subscriptions=args.subscriptions,
        verbose=args.verbose,)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
