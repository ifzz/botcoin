#!/usr/bin/env python
from datetime import datetime
import queue


class Trade(object):
    pass

class Backtest(Trade):
    def __init__(self, data, portfolio, strategies, date_from=None, date_to=None):
        if not strategies: # need to check if is iterable of strategies
            raise ValueError

        self.data = data
        self.portfolio = portfolio
        self.strategies = strategies        
        self.events = queue.Queue()

        self.date_from = date_from
        self.date_to = date_to

    def start(self):
        time_started = datetime.now()

        while self.data.continue_execution:

            self.events.put(self.data.update_bars())

            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break

                new_event = None

                if event.type == 'DATA':
                    for strategy in self.strategies:
                        new_event = strategy.generate_signals(self.data.get_latest_bars())
                        self.events.put(new_event) if new_event else None
                
                elif event.type == 'SIGNAL':
                    self.portfolio.generate_orders(event, self.data.get_latest_bars())

                elif event.type == 'ORDER':
                    pass

                elif event.type == 'FILL':
                    pass

        print(self.portfolio.performance())


        time_ended = datetime.now()
        self.run_time = time_ended - time_started