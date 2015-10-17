#!/usr/bin/env python
import argparse
import importlib
import imp
import logging
import sys

import settings
from src.data import *
from src.backtest import *
from src.event import *
from src.execution import *
from src.strategy import *
from src.portfolio import *


def load_strategies():
    sys.path.append(settings.BASE_DIR)

    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument('-f', '--file', required=False, nargs='?', help='file with strategy scripts')
    args = parser.parse_args()

    if args.file:
        directory, file_to_load = os.path.split(os.path.abspath(args.file))
        sys.path.append(directory)
        s = __import__(file_to_load.split('.')[0])
        # print(dir(s),s.strategies)
        # input()
    else:
        import strategies.custom as s

    try:
        strategies = s.strategies
    except AttributeError as e:
        sys.exit('# No strategies attribute in your algo')


    backtest = Backtest(strategies)

    print(backtest.results)

    if len(s.strategies) == 1:
        print(backtest.portfolios[0].performance['all_trades'])
        backtest.plot_results()

    return Backtest



    # except ImportError as e:
    #     logging.error(e)


if __name__ == '__main__':
    try:
        load_strategies()
    except KeyboardInterrupt:
        sys.exit("# Execution stopped")
