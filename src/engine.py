import collections
import datetime
import logging
import queue

import pandas as pd

from .data import MarketData, HistoricalCSV
from .execution import BacktestExecution, Execution
from .strategy import Strategy
from .performance import performance
from .portfolio import Portfolio
import settings

class TradingEngine():
    def __init__(self, events_queue, market, strategy, portfolio, broker):

        if (not isinstance(market, MarketData) or
            not isinstance(events_queue, queue.Queue) or
            not isinstance(strategy, Strategy) or
            not isinstance(portfolio, Portfolio) or
            not isinstance(broker, Execution)):
            raise TypeError("Improper parameter type on TradingEngine.__init__()")

        self.events_queue = events_queue
        self.market = market
        self.strategy = strategy
        self.portfolio = portfolio
        self.broker = broker

    def run_cycle(self):
        while True:
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                break

            if event.type == 'MARKET':
                self.strategy.generate_signals()
                self.portfolio.update_positions_and_holdings()

            elif event.type == 'SIGNAL':
                self.portfolio.generate_orders(event)

            elif event.type == 'ORDER':
                self.broker.execute_order(event)

            elif event.type == 'FILL':
                self.portfolio.consume_fill_event(event)

            else:
                raise TypeError("Unknown event type")


class BacktestManager(object):
    def __init__(self, strat_port_pairs, symbol_list=None, date_from=None, 
                 date_to=None, data_dir=None, start_automatically=True):

        if not (isinstance(strat_port_pairs, collections.Iterable) and
                isinstance(strat_port_pairs[0], dict)):
            raise TypeError("Improper parameter type on BacktestManager.__init__()")

        # Single market object will be used for all backtesting instances
        self.market = HistoricalCSV(
            data_dir or settings.DATA_DIR,
            symbol_list or settings.SYMBOL_LIST,
            date_from = date_from or settings.DATE_FROM,
            date_to = date_to or settings.DATE_TO,
            normalize_prices = settings.NORMALIZE_PRICES,
            normalize_volume = settings.NORMALIZE_VOLUME,
        )

        self.engines = []

        for pair in strat_port_pairs:
            events_queue = queue.Queue()
            broker = BacktestExecution(events_queue, self.market)

            strategy = pair['strategy']
            portfolio = pair['portfolio']

            portfolio.set_market_and_queue(events_queue, self.market)
            strategy.set_market_and_queue(events_queue, self.market)

            self.engines.append(TradingEngine(events_queue, self.market, strategy, portfolio, broker))


        logging.info("Backtest {} from {} to {}".format(
            self.market.symbol_list, 
            self.market.date_from.strftime('%Y-%m-%d'), 
            self.market.date_to.strftime('%Y-%m-%d'),
        ))
        logging.info("with {} different strategies".format(str(len(self.engines))))
        logging.info("Data load took {}".format(str(self.market.load_time)))

        if start_automatically:
            self.start()
            self.calc_performance()

    def start(self):
        """
        Starts backtesting for all engines created.
        New market events are handled on this level to allow for multiple engines
        to run simultaneously with a single market object
        """
        start_time = datetime.datetime.now()
        while self.market.continue_execution:
            new_market_event = self.market.update_bars()
            if new_market_event:
                for engine in self.engines:
                    engine.events_queue.put(new_market_event)
                    engine.run_cycle()

        for engine in self.engines:
            engine.portfolio.update_last_positions_and_holdings()

        logging.info("Backtest took " + str((datetime.datetime.now()-start_time)))

    def calc_performance(self, order_by='sharpe'):
        start_time = datetime.datetime.now()

        for engine in self.engines:
            engine.performance = performance(engine.portfolio)

        # Order engines by sharpe (used for plotting)
        self.engines = sorted(self.engines, key=lambda x: x.performance[order_by], reverse=True)

        # Calc results dataframe that contains performance for all engines
        self.results = pd.DataFrame(
            [[
                engine.strategy.parameters,
                engine.performance['total_return'],
                engine.performance['ann_return'],
                engine.performance['sharpe'],
                engine.performance['trades'],
                engine.performance['pct_trades_profit'],
                engine.performance['dangerous']
            ] for engine in self.engines ],
            columns=[
                'strategy',
                'total returns',
                'annualised return',
                'sharpe',
                '# trades',
                'profitable trades',
                'dangerous'
            ],
        )

        logging.info("Performance calculated in {}".format(str(datetime.datetime.now()-start_time)))

    def plot_open_positions(self):
        import matplotlib.pyplot as plt

        for engine in self.engines:
            ax = engine.performance['all_positions']['open_trades'].plot()
            ax.set_title(engine.strategy)
            plt.grid()  
            plt.show()

    def plot_results(self):
        import matplotlib.pyplot as plt

        for engine in self.engines:
            ax = engine.performance['equity_curve'].plot()
            ax.set_title(engine.strategy)
            plt.grid()  
            plt.show()
