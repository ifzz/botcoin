from datetime import datetime
import os

from src.data import HistoricalCSV
#os.path.dirname(os.path.realpath(__file__)) + 
data = HistoricalCSV('data/', ['btceUSD_5Min'], date_from=datetime.strptime("2015-01-01", '%Y-%m-%d'), date_to=datetime.now())

