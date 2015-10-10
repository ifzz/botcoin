#!/usr/bin/env python
import argparse
import importlib
import logging
import os
import sys

import settings
from src.data import *
from src.backtest import *
from src.event import *
from src.execution import *
from src.strategy import *
from src.portfolio import *


if __name__ == '__main__':
    sys.path.append(settings.BASE_DIR)

    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument('-f', '--file', required=False, nargs='?', help='file with strategy scripts')
    args = parser.parse_args()

    try:
        if args.file:
            importlib.import_module(args.file)
        else:
            import custom
    except KeyboardInterrupt:
        sys.exit("# Execution stopped")
    except ImportError as e:
        logging.error(e)
