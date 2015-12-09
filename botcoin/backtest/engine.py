import collections
from datetime import timedelta, datetime
import logging

import pandas as pd

import botcoin
from botcoin import settings
from botcoin.backtest.data import HistoricalCSVData
from botcoin.backtest.execution import BacktestExecution, Execution
from botcoin.strategy import Strategy
from botcoin.portfolio import Portfolio


class Backtest(object):
    def __init__(self, strategies, data_dir, start_automatically=True):

        # Single market object will be used for all backtesting instances
        self.market = HistoricalCSVData(
            data_dir or settings.DATA_DIR, #should come from script loader
            strategies[0].SYMBOL_LIST,
            date_from = getattr(strategies[0], 'DATE_FROM', datetime.now() - timedelta(weeks=52)),
            date_to = getattr(strategies[0], 'DATE_TO', datetime.now()),
        )

        self.portfolios = []

        for strategy in strategies:
            port = Portfolio()
            port.set_modules(self.market, strategy, BacktestExecution())
            self.portfolios.append(port)

        logging.info("Backtesting {} {} with {} symbols from {} to {}".format(
            len(self.portfolios),
            'strategies' if len(self.portfolios) > 1 else 'strategy',
            len(self.market.symbol_list),
            self.market.date_from.strftime('%Y-%m-%d'),
            self.market.date_to.strftime('%Y-%m-%d'),
        ))
        logging.info("Data load took {}".format(str(self.market.load_time)))

        if start_automatically:
            self.start()
            self.calc_performance()

    def start(self):
        """
        Starts backtesting for all portfolios created.
        New market events are handled on this level to allow for multiple portfolios
        to run simultaneously with a single market object
        """
        start_time = datetime.now()
        while self.market.continue_execution:
            for new_market_event in self.market._update_bars():
                if new_market_event:
                    for portfolio in self.portfolios:
                        portfolio.events_queue.put(new_market_event)
                        portfolio.run_cycle()

        [portfolio.update_last_positions_and_holdings() for portfolio in self.portfolios]

        logging.info("Backtest took " + str((datetime.now()-start_time)))

    def calc_performance(self, order_by='sharpe'):
        start_time = datetime.now()

        [portfolio.calc_performance() for portfolio in self.portfolios]

        # Order engines by sharpe (used for plotting)
        self.portfolios = sorted(self.portfolios, key=lambda x: x.performance[order_by], reverse=True)

        # Calc results dataframe that contains performance for all portfolios
        self.results = pd.DataFrame(
            [[
                str(portfolio.strategy),
                portfolio.performance['total_return'],
                portfolio.performance['ann_return'],
                portfolio.performance['sharpe'],
                portfolio.performance['trades'],
                portfolio.performance['pct_trades_profit'],
                portfolio.performance['dangerous'],
                portfolio.performance['dd_max'],
            ] for portfolio in self.portfolios ],
            columns=[
                'strategy',
                'total returns',
                'annualised return',
                'sharpe',
                '# trades',
                'profit %',
                'dangerous',
                'max dd',
            ],
        )

        logging.debug("Performance calculated in {}".format(str(datetime.now()-start_time)))

    def plot_open_positions(self):
        import matplotlib.pyplot as plt

        for portfolio in self.portfolios:
            ax = portfolio.performance['all_positions']['open_trades'].plot()
            ax.set_title(portfolio.strategy)
            plt.grid()
            plt.show()

    def plot_results(self):
        import matplotlib.pyplot as plt

        for portfolio in self.portfolios:
            ax = portfolio.performance['equity_curve'].plot()
            ax.set_title(portfolio.strategy)
            plt.grid()
            plt.show()

    def plot_symbol_subscriptions(self):
        import matplotlib.pyplot as plt

        for portfolio in self.portfolios:
            portfolio.performance['subscribed_symbols'].plot()
            plt.show()

    def print_all_trades(self):
        for port in self.portfolios:
            print(port.performance['all_trades'])

    def strategy_finishing_methods(self):
        [portfolio.strategy.backtest_done(portfolio.performance) for portfolio in self.portfolios]
