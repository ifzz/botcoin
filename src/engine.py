import collections
import datetime
import logging
import queue

from .data import MarketData
from .execution import BacktestExecution, Execution
from .strategy import Strategy
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
            raise TypeError("Improper parameter type on TradingEngine.__init__()")

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
                raise TypeError("Unknown event type")


class BacktestManager(object):
    def __init__(self, market, strategies):
        # Strategy and Portfolio parameters need to be list within a list
        if not (isinstance(strategies, collections.Iterable) and
            isinstance(market, MarketData)):
            raise TypeError("Improper parameter type on BacktestManager.__init__()")

        self.strategies = strategies
        
        # Single market object will be used for all backtesting instances
        self.market = market
        self.engines = []

        for strategy in strategies:
            events_queue = queue.Queue()
            broker = BacktestExecution(events_queue)
            strategy.set_market_and_queue(events_queue, market)
            portfolio = Portfolio(events_queue, market)

            self.engines.append(TradingEngine(events_queue, market, strategy, portfolio, broker))

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

        self.backtest_time = (datetime.datetime.now()-start_time)

    def calc_performance(self):
        start_time = datetime.datetime.now()

        [engine.performance() for engine in self.engines]
        
        self.perf_time = (datetime.datetime.now()-start_time)

        results = ""
        for engine in sorted(self.engines, key=lambda x: x.performance.total_return, reverse=True):
            results += str(engine.strategy.parameters) + ":" + str(engine.performance.total_return) + '\n'
        self.results = results.rstrip()

