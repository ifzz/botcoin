import logging

from botcoin import settings
from botcoin.data import MarketData
from botcoin.live.execution import LiveExecution
from botcoin.portfolio import settings, Portfolio

class LiveEngine(object):
    def __init__(self, strategy, data_dir):

        settings.fetch_parameters_from_strategy(strategy)

        # Single market object will be used for all backtesting instances
        self.market = MarketData(
            data_dir or settings.DATA_DIR, #should come from script loader
            getattr(strategy, 'SYMBOL_LIST', []),
        )

        # print(self.market.symbol_data['CBA.AX']['df'][-1])
        self.portfolio = Portfolio()
        self.portfolio.set_modules(self.market, strategy, LiveExecution())
        self.strategy = strategy


    def start(self):
        logging.info("Live execution with strategy {}.".format(self.portfolio.strategy))

        # while True:
        self.portfolio.run_cycle
