 #! /usr/bin/env python
import argparse
import logging
import os
import botcoin


def main():

    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument(dest='algo_file', nargs='+', help='file with strategy scripts')
    parser.add_argument('-d', '--data_dir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose (very chatty, be careful)')
    args = parser.parse_args()

    botcoin.utils._config_logging(args.verbose)

    f = args.algo_file[0]
    logging.info("Reading strategies from {}".format(f))

    live = botcoin.LiveEngine(botcoin.utils._find_strategies(f, True)[0], args.data_dir)

    try:
        live.start()
    except KeyboardInterrupt:
        live.stop()
        logging.critical("Execution stopped")


if __name__ == '__main__':
    main()
