from botcoin import settings
from botcoin.data import MarketData
from botcoin.live.execution import LiveExecution
from botcoin.portfolio import settings, Portfolio

class LiveEngine(object):
    def __init__(self, strategy, data_dir):

        settings.NORMALIZE_PRICES = getattr(strategy, 'NORMALIZE_PRICES', settings.NORMALIZE_PRICES)
        settings.NORMALIZE_VOLUME = getattr(strategy, 'NORMALIZE_VOLUME', settings.NORMALIZE_VOLUME)
        settings.ROUND_DECIMALS = getattr(strategy, 'ROUND_DECIMALS', settings.ROUND_DECIMALS)

        # Single market object will be used for all backtesting instances
        self.market = MarketData(
            data_dir or settings.DATA_DIR, #should come from script loader
            getattr(strategy, 'SYMBOL_LIST', []),
        )

        # print(self.market.symbol_data['CBA.AX']['df'][-1])
        self.portfolio = Portfolio()
        self.portfolio.set_modules(self.market, strategy, LiveExecution())

    def start(self):
        # while True:
        self.portfolio.run_cycle
