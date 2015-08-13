import collections
from datetime import datetime
import logging
import queue

from .data import MarketData
from .execution import BacktestExecution, Execution
from .strategy import Strategy, RandomBuyStrategy
from .performance import Performance
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
            raise TypeError

        self.events_queue = events_queue
        self.market = market
        self.strategy = strategy
        self.portfolio = portfolio
        self.broker = broker

    def performance(self):
        self.performance = Performance(self.portfolio)

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
                raise TypeError


class BacktestManager(object):
    def __init__(self, market, strategy_parameters, portfolio_parameters=[[]]):
        # Strategy and Portfolio parameters need to be list within a list
        if not (isinstance(strategy_parameters, collections.Iterable) and
            isinstance(strategy_parameters[0], collections.Iterable)):
            raise TypeError
        if not (isinstance(portfolio_parameters, collections.Iterable) and
                isinstance(portfolio_parameters[0], collections.Iterable)):
            raise TypeError
        # Single market object will be used for all backtesting instances
        if not (isinstance(market, MarketData)):
            raise TypeError

        self.strategy_parameters = strategy_parameters

        self.market = market
        self.engines = set()

        for params in strategy_parameters:
            events_queue = queue.Queue()
            broker = BacktestExecution(events_queue)
            strategy = RandomBuyStrategy(events_queue, market, params)
            portfolio = Portfolio(events_queue, market)

            self.engines.add(TradingEngine(events_queue, market, strategy, portfolio, broker))

    def start(self):
        """
        Starts backtesting for all engines created.
        New market events are handled on this level to allow for multiple engines
        to run simultaneously with a single market object
        """
        while self.market.continue_execution:
            new_market_event = self.market.update_bars()
            if new_market_event:
                for engine in self.engines:
                    engine.events_queue.put(new_market_event)
                    engine.run_cycle()

        for engine in self.engines:
            engine.portfolio.update_last_positions_and_holdings()

    def calc_performance(self):
        [engine.performance() for engine in self.engines]
        performance = {engine.performance.total_return: str(engine.strategy.parameters) for engine in self.engines}
        results = '\n'.join([str(val) + ' : ' + str(performance[val]) for val in sorted(performance.keys(), reverse=True)])
        self.results = results

