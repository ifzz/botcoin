#!/usr/bin/env python
import argparse
import logging
import os
import sys
import botcoin




def main():
    parser = argparse.ArgumentParser(description='Downloads symbol data from Quandl.')
    parser.add_argument(dest='algo_file', nargs='+', help='file with strategy scripts')
    parser.add_argument('-d', '--datadir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    args = parser.parse_args()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
