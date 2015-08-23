from datetime import timedelta, datetime
import logging
import os
import pandas as pd

# Pandas config
pd.set_option('display.max_rows', 200)
pd.set_option('display.width', 1000) 

# Logging config
VERBOSITY = 10
LOG_FORMAT = '# %(levelname)s:%(module)s - %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=VERBOSITY)

# Directories
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
SRC_DIR = os.path.join(BASE_DIR, 'src/')


# Backtesting specific configuration
DATE_TO = datetime.now()
DATE_FROM = DATE_TO - timedelta(weeks=52) #datetime.strptime("2015-01-01", '%Y-%m-%d') #

# If both COMMISSION_FIXED and COMMISSION_PCT are set, both will be charged on each trade
# Fixed commission charged on each trade
COMMISSION_FIXED = 0.0
# Percentage commission charged on each trade
COMMISSION_PCT = 0.0026 #maker commission of Kraken

# Used by portfolio to calculate limit_prices and estimated cost for Orders
MAX_SLIPPAGE = 0.0

SYMBOL_LIST = [
    'btceUSD_1h',
]

