import collections
import datetime
import logging
import queue

import pandas as pd

from .data import MarketData
from .execution import BacktestExecution, Execution
from .strategy import Strategy
from .performance import performance
from .portfolio import Portfolio
from .settings import (
    DATE_FROM,
    DATE_TO,
)

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

    def calc_perf(self):
        self.performance = performance(self.portfolio)


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
    def __init__(self, market, strat_port_pairs):
        if not (isinstance(strat_port_pairs, collections.Iterable) and
                isinstance(strat_port_pairs[0], dict) and
                isinstance(market, MarketData)):
            raise TypeError("Improper parameter type on BacktestManager.__init__()")

        self.strat_port_pairs = strat_port_pairs
        
        # Single market object will be used for all backtesting instances
        self.market = market
        self.engines = []

        for pair in strat_port_pairs:
            events_queue = queue.Queue()
            broker = BacktestExecution(events_queue, market)

            strategy = pair['strategy']
            portfolio = pair['portfolio']

            portfolio.set_market_and_queue(events_queue, market)
            strategy.set_market_and_queue(events_queue, market)

            self.engines.append(TradingEngine(events_queue, market, strategy, portfolio, broker))


        logging.debug("Backtest {} from {} to {}".format(
            market.symbol_list, 
            market.date_from.strftime('%Y-%m-%d'), 
            market.date_to.strftime('%Y-%m-%d'),
        ))
        logging.debug("with {} different strategies".format(str(len(self.engines))))
        logging.debug("Data load took {}".format(str(self.market.load_time)))

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

        logging.debug("Backtest took " + str((datetime.datetime.now()-start_time)))

    def calc_performance(self, order_by='sharpe'):
        start_time = datetime.datetime.now()

        [engine.calc_perf() for engine in self.engines]

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
            ] for engine in self.engines ],
            columns=[
                'strategy',
                'total returns',
                'annualised return',
                'sharpe',
                '# trades',
                'profitable trades'
            ],
        )

        logging.debug("Performance calculated in {}".format(str(datetime.datetime.now()-start_time)))

    def plot_results(self):
        import matplotlib.pyplot as plt

        for engine in self.engines:
            ax = engine.performance['equity_curve'].plot()
            ax.set_title(engine.strategy)
            plt.grid()  
            plt.show()
