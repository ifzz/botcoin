from datetime import datetime
import logging
import queue

from .data import MarketData
from .execution import BacktestExecution, Execution
from .strategy import Strategy, RandomBuyStrategy
from .portfolio import Portfolio
from .settings import (
    DATE_FROM,
    DATE_TO,
)

class TradingEngine():
    def __init__(self, events_queue, market, portfolio, broker):

        if (not isinstance(market, MarketData) or
            not isinstance(events_queue, queue.Queue) or
            not isinstance(portfolio, Portfolio) or
            not isinstance(broker, Execution)):
            raise TypeError

        self.events_queue = events_queue
        self.market = market
        self.portfolio = portfolio
        self.broker = broker

    def get_new_market_event(self):
        # update_bars can only be called here!
        market_event = self.market.update_bars()
        if market_event:
            self.events_queue.put(market_event)

    def start(self):
        while self.market.continue_execution:

            self.get_new_market_event()

            while True:
                try:
                    event = self.events_queue.get(False)
                except queue.Empty:
                    break

                if event.type == 'MARKET':
                    self.portfolio.consume_market_event(event)

                elif event.type == 'ORDER':
                    self.broker.execute_order(event, self.market.bars(event.symbol).last_close)

                elif event.type == 'FILL':
                    self.portfolio.consume_fill_event(event)

                else:
                    raise TypeError


class BacktestManager(object):
    def __init__(self, market, strategy_parameters, portfolio_parameters=[[]]):

        # Strategy and Portfolio parameters need to be list within a list
        if not (isinstance(strategy_parameters, list) and
            isinstance(strategy_parameters[0], list)):
            raise TypeError
        if not (isinstance(portfolio_parameters, list) and
                isinstance(portfolio_parameters[0], list)):
            raise TypeError
        # Single market object will be used for all backtesting instances
        if not (isinstance(market, MarketData)):
            raise TypeError

        events_queue = queue.Queue()
        broker = BacktestExecution(events_queue)
        strategy = RandomBuyStrategy(market, strategy_parameters[0])
        portfolio = Portfolio(market, strategy, events_queue)

        self.engines = [TradingEngine(events_queue, market, portfolio, broker)]

    def start(self):
        [engine.start() for engine in self.engines]

    def performance(self):
        return [engine.portfolio.performance() for engine in self.engines]
            