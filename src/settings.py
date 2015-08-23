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


# List of symbols
ASX_TOP_50 = ['AGL.AX','AIO.AX','AMC.AX','AMP.AX','ANZ.AX','APA.AX','ASX.AX','AZJ.AX','BHP.AX','BXB.AX','CBA.AX','CCL.AX','CPU.AX','CSL.AX','CTX.AX','CWN.AX','DXS.AX','FDC.AX','GMG.AX','GPT.AX','IAG.AX','IPL.AX','JHX.AX','LLC.AX','MGR.AX','MPL.AX','MQG.AX','NAB.AX','NCM.AX','ORG.AX','ORI.AX','OSH.AX','QBE.AX','RHC.AX','RIO.AX','S32.AX','SCG.AX','SEK.AX','SGP.AX','SHL.AX','STO.AX','SUN.AX','SYD.AX','TCL.AX','TLS.AX','WBC.AX','WES.AX','WFD.AX','WOW.AX','WPL.AX',]
