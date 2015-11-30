from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection, message
from time import sleep

# edemo
# demouser

class LiveEngine(object):
    def __init__(self, strategy, data_dir, start_automatically=True):

        # Single market object will be used for all backtesting instances
        self.market = HistoricalCSVData(
            data_dir or settings.DATA_DIR, #should come from script loader
            getattr(strategies[0], 'SYMBOL_LIST', []),
            normalize_prices = getattr(strategies[0], 'NORMALIZE_PRICES', settings.NORMALIZE_PRICES),
            normalize_volume = getattr(strategies[0], 'NORMALIZE_VOLUME', settings.NORMALIZE_VOLUME),
            round_decimals = getattr(strategies[0], 'ROUND_DECIMALS', settings.ROUND_DECIMALS),
        )

        self.portfolio = Portfolio()
        port.set_modules(self.market, strategy, BacktestExecution())
