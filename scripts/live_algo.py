 #! /usr/bin/env python
import argparse
import logging
import os
import botcoin
from botcoin.utils import _find_strategies, _config_logging


def main():
    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument(dest='algo_file', nargs='+', help='file with strategy scripts')
    parser.add_argument('-d', '--data_dir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose (very chatty, be careful)')
    args = parser.parse_args()

    _config_logging(args.verbose)

    live = botcoin.LiveEngine(botcoin.utils._find_strategies(args.algo_file[0], args.data_dir, True)[0], args.data_dir)

    live.start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
