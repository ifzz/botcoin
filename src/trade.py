#!/usr/bin/env python
from datetime import datetime
import logging
import queue

class Trade(object):
    pass

class Backtest(Trade):
    def __init__(self, data, portfolio, date_from=None, date_to=None):
        self.data = data
        self.date_from = date_from
        self.date_to = date_to
        # Holds events to/from external sources e.g. market, execution, broker, etc
        self.external_events_queue = queue.Queue()
        # Portfolio that contains strategies within itself
        self.portfolio = portfolio.set_external_queue(self.external_events_queue)

    def start(self):
        time_started = datetime.now()

        while self.data.continue_execution:

            self.get_new_bar()

            while True:
                try:
                    event = self.external_events_queue.get(False)
                except queue.Empty:
                    break

                if event.type == 'MARKET':
                    self.portfolio.consume_market_event(event)

                elif event.type == 'ORDER':
                    pass # Not used in backtesting

                elif event.type == 'FILL':
                    pass # Not used in backtetsting

                else:
                    raise TypeError

        print(self.portfolio.performance())

        self.run_time = datetime.now() - time_started

    def get_new_bar(self):
        # update_bars can only be called here!    
        new_bar = self.data.update_bars()
        if new_bar:
            self.external_events_queue.put(new_bar)