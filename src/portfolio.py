#!/usr/bin/env python
import collections
import datetime
import logging

from .data import HistoricalCSV
from .event import MarketEvent, SignalEvent, OrderEvent, FillEvent

class Position(object):
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
        self.symbol_dict = symbol_dict

class Holding(object):
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

        self.symbol_dict = symbol_dict
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
        strategy -- 
    """
    def __init__(self, data, date_from, strategy, initial_capital=100000.0):
        if not isinstance(data, HistoricalCSV) or not isinstance(date_from, datetime.datetime):
            raise TypeError
        if not strategy:
            raise ValueError

        self.data = data
        self.initial_capital = initial_capital
        self.strategy = strategy

        self.all_positions = []
        self.all_holdings = []

        # TEMP
        self.results = []
        self.buy_price = 0
        self.sell_price = 0

    def consume_market_event(self, event):
        if not event.type == 'MARKET':
            raise TypeError

        self.add_new_position_and_holding()

        for signal in self.strategy.generate_signals():
            self.generate_orders(signal)

    def add_new_position_and_holding(self):
        """Used to add new position and holdings to portfolio, triggered by a new market signal"""
        bar = self.data.get_latest_bars(self.data.symbol_list[0])
        
        # if lists are empty, we need to add initial position and holding objects to it
        if not self.all_positions or not self.all_holdings:
            self.date_from = bar.last_datetime
            self.add_position(Position(bar.last_datetime))
            self.add_holding(Holding(bar.last_datetime, self.initial_capital, 0.00, self.initial_capital))

        else:
            last_position = self.all_positions[-1]
            last_holding = self.all_holdings[-1]

            if ((bar.last_datetime <= last_position.datetime) or 
                (bar.last_datetime <= last_holding.datetime)):
                # logging.debug('Bar datetime is ' + str(bar.last_datetime))
                # logging.debug('Holding datetime is ' + str(last_holding.datetime))
                # logging.debug('Position datetime is ' + str(last_position.datetime))
                logging.critical('New bar arrived with same datetime as previous holding and position. Aborting!')
                raise ValueError

            new_position = Position(bar.last_datetime, last_position.symbol_dict)
            new_holding = Holding(
                bar.last_datetime,
                last_holding.cash,
                last_holding.comission,
                last_holding.total,
                last_holding.symbol_dict
            )

            self.add_position(new_position)
            self.add_holding(new_holding)

    def generate_orders(self, signal):
        # TODO update positions and holdings based on fill events

        if signal.signal_type == 'LONG':
            self.buy_price = self.data.get_latest_bars(signal.symbol).last_close

        elif signal.signal_type == 'SHORT':
            pass

        elif signal.signal_type == 'EXIT':
            self.sell_price = self.data.get_latest_bars(signal.symbol).last_close

            self.results.append(self.sell_price-self.buy_price)

    def add_position(self, positions):
        if isinstance(positions, Position):
            self.all_positions.append(positions)
        else:
            raise TypeError

    def add_holding(self, holding):
        if isinstance(holding, Holding):
            self.all_holdings.append(holding)
        else:
            raise TypeError

    def set_external_queue(self, external_events_queue):
        self.external_events_queue = external_events_queue
        return self
    
    def performance(self):
        return sum(self.results)
