#!/usr/bin/env python
import collections
import datetime

from .data import HistoricalCSV
from .event import MarketEvent, SignalEvent, OrderEvent, FillEvent

class Positions(object):
    """
    Positions held at a point in time. Only hold symbols that have a position currently.
    If symbol isn't included in symbol_dict, it is implied there is no position.
    Parameters:
        datetime -- date of the point in time in question
        symbol_dict -- dictionary with symbols as key and ammount owned as value
    """
    def __init__(self, current_datetime, symbol_dict={}):
        if not isinstance(current_datetime, datetime.datetime) or not isinstance(symbol_dict, dict):
            raise TypeError        
        self.datetime = current_datetime
        self.s = symbol_dict

class Holdings(object):
    """
    Holdings at a point in time. All properties represented in cash.
    If symbol isn't included in symbol_dict, it is implied there is no holdings for it.
    Parameters:
        datetime -- date of the point in time in question
        symbol_dict -- dictionary with symbols as key and cash equivalent owned as value
        cash -- cash held
        comission -- cummulative comissions paid up to this day
        total -- cash equivalent of all holdings combined - comissions paid
    """
    def __init__(self, current_datetime, cash, comission, total, symbol_dict={}):
        if not isinstance(current_datetime, datetime.datetime) or not isinstance(symbol_dict, dict):
            raise TypeError

        self.s = symbol_dict
        self.datetime = current_datetime
        self.cash = cash
        self.comission = comission
        self.total = total

class Portfolio(object):
    """
    Portfolio root class. Needs to have visibility on all types of events.
    Parameters:
        data -- 
        date_from -- 
        initial_capital -- 
        all_positions --
        all_holdings -- 
        strategies -- 
    """
    def __init__(self, data, date_from, strategy, initial_capital=100000.0):
        if not isinstance(data, HistoricalCSV) or not isinstance(date_from, datetime.datetime):
            raise TypeError
        if not strategies:
            raise ValueError

        self.data = data
        self.date_from = date_from
        self.initial_capital = initial_capital
        self.strategy = strategy

        self.all_positions = []
        self.all_holdings = []

        # Creating first position and holding
        self.add_position(Positions(date_from))
        self.add_holding(Holdings(date_from, initial_capital, 0.00, initial_capital))

        # TEMP
        self.results = []
        self.buy_price = 0
        self.sell_price = 0

    def consume_market_event(self, event):
        if not event.type == 'MARKET':
            raise TypeError

        self.consume_signal_events(self.strategy.generate_signals())

    # def generate_signals(self):
    #     # 2 stage to remove Nones from list (added by strategies that return no signal)
    #     return [s for s in [strategy.generate_signals() for strategy in self.strategies] if s]

    def consume_signal_events(self, signals):
        [self.generate_orders(signal) for signal in signals]

    def generate_orders(self, signal):
        if signal.signal_type == 'LONG':
            self.buy_price = self.data.get_latest_bars(signal.symbol).close()[0]

        elif signal.signal_type == 'EXIT':
            self.sell_price = self.data.get_latest_bars(signal.symbol).close()[0]
        
            self.results.append(self.sell_price-self.buy_price)

    def add_position(self, positions):
        if isinstance(positions, Positions):
            self.all_positions.append(positions)
        else:
            raise TypeError

    def add_holding(self, holding):
        if isinstance(holding, Holdings):
            self.all_holdings.append(holding)
        else:
            raise TypeError

    def set_external_queue(self, external_events_queue):
        self.external_events_queue = external_events_queue
        return self
    
    def performance(self):
        return sum(self.results)
