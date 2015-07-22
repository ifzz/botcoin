import datetime
import logging
from math import floor
import queue

import pandas as pd

from .data import MarketData
from .event import MarketEvent, SignalEvent, OrderEvent, FillEvent
from .settings import COMMISSION_FIXED, COMMISSION_PCT
from .strategy import Strategy

class Portfolio(object):
    """
    Portfolio root class.
    """
    def __init__(self, market, strategy, events_queue, initial_capital=100000.0):
        # check if variables instances of the correct objects
        if (not isinstance(market, MarketData) or
            not isinstance(strategy, Strategy) or
            not isinstance(events_queue, queue.Queue)):
            raise TypeError
        # check for symbol names that would conflict with columns used in holdings and positions
        for symbol in market.symbol_list:
            if symbol in ('cash', 'commission', 'total', 'returns', 'equity_curve', 'datetime'):
                raise ValueError

        self.market = market
        self.strategy = strategy
        self.events_queue = events_queue

        self.all_positions = []
        self.all_holdings = []
        self.current_position = None
        self.current_holding = None

        self.initial_capital = initial_capital

    def consume_market_event(self, market):
        if not market.type == 'MARKET':
            raise TypeError

        self.update_positions_and_holdings()

        for signal in self.strategy.generate_signals():
            self.generate_orders(signal)

    def update_positions_and_holdings(self):
        """Used to add new position and holdings to portfolio, triggered by a new market signal"""
        bar = self.market.bars(self.market.symbol_list[0])

        # If there is no current position and holding, meaning execution just started
        if not self.current_position and not self.current_holding:
            self.date_from = bar.last_datetime
            self.current_position = self.construct_position(bar.last_datetime)

            self.current_holding = self.construct_holding(bar.last_datetime, self.initial_capital, 0.00, self.current_position)

        else:
            if ((bar.last_datetime <= self.current_position['datetime']) or 
                (bar.last_datetime <= self.current_holding['datetime'])):
                # logging.debug('Bar datetime is ' + str(bar.last_datetime))
                # logging.debug('Holding datetime is ' + str(last_holding.datetime))
                # logging.debug('Position datetime is ' + str(last_position.datetime))
                logging.critical('New bar arrived with same datetime as previous holding and position. Aborting!')
                raise ValueError

            # Add current to all lists
            self.all_positions.append(self.current_position)
            self.all_holdings.append(self.current_holding)


            self.current_position = self.construct_position(bar.last_datetime, self.current_position)
            self.current_holding = self.construct_holding(
                bar.last_datetime,
                self.current_holding['cash'],
                self.current_holding['commission'],
                self.current_position,
            )


    def generate_orders(self, signal):
        symbol = signal.symbol
        sig_type = signal.signal_type
        order_type = 'MKT'
        order = None

        cur_position = self.current_position[symbol]
        cur_holding = self.current_holding[symbol]
        cash = self.current_holding['cash']

        bar = self.market.bars(symbol)

        if sig_type in ('LONG') and cur_position == 0:
            # COMMISSION_FIXED remove the fixed ammount from cash, 
            # and COMMISSION_PCT increases the symbol price to reflect the fee
            quantity = floor( (cash-COMMISSION_FIXED) / (bar.last_close * (1+COMMISSION_PCT)) )
            order = OrderEvent(symbol, order_type, quantity, sig_type)

        elif sig_type in ('EXIT') and cur_position > 0:
            quantity = cur_position
            order = OrderEvent(symbol, order_type, quantity, sig_type)
        
        if order:
            self.events_queue.put(order)

    def consume_fill_event(self, fill):
        if not fill.type == 'FILL':
            raise TypeError

        self.current_position[fill.symbol] += fill.quantity

        self.current_holding[fill.symbol] += fill.cost
        self.current_holding['commission'] += fill.commission
        self.current_holding['cash'] -= (fill.cost + fill.commission)
        self.current_holding['total'] -= (fill.commission)

        self.verify_consistency()

    def verify_consistency(self):
        """ Checks for problematic values in current holding and position """

        if (self.current_holding['commission'] < 0 or
            self.current_holding['cash'] < 0 or
            self.current_holding['total'] < 0):
            logging.critical('Cash, total or commission is a negative value. This shouldn\'t be possible.')
            raise ValueError
        
        for s in self.market.symbol_list:
            if (self.current_holding[s] < 0 or
                self.current_position[s] < 0):
                logging.info('Do you really have a short position?')

    def construct_position(self, cur_datetime, current_position={}):
        """
        Positions held at a point in time.
        Parameters:
            cur_datetime -- date of the point in time in question
            s -- dictionary with symbols as key and ammount owned as value
        """
        if not isinstance(cur_datetime, datetime.datetime) or not isinstance(current_position, dict):
            raise TypeError

        if current_position:
            position = dict((k,v) for k, v in [(s, current_position[s]) for s in self.market.symbol_list])
        else:
            position = dict((k,v) for k, v in [(s, 0.0) for s in self.market.symbol_list])

        position['datetime'] = cur_datetime

        return position

    def construct_holding(self, cur_datetime, cash, commission, current_position):
        """
        Holdings at a point in time. All properties represented in cash.
        Parameters:
            cur_datetime -- date of the point in time in question
            cash -- cash held
            commission -- cummulative commission paid up to this day
            total -- cash equivalent of all holdings combined - commission paid
        """
        if not isinstance(cur_datetime, datetime.datetime) or not isinstance(current_position, dict):
            raise TypeError

        holding = {}

        holding['datetime'] = cur_datetime
        holding['cash'] = cash
        holding['commission'] = commission
        holding['total'] = cash


        for s in self.market.symbol_list:
            # Approximation to the real value
            market_value = self.current_position[s] * self.market.bars(s).last_close
            holding[s] = market_value
            holding['total'] += market_value

        return holding

    def performance(self):
        # Adds latest current position and holding into 'all' lists, so they
        # can be part of performance as well
        if self.current_position and self.current_holding:
            self.all_holdings.append(self.current_holding)
            self.all_positions.append(self.current_position)
            self.current_holding, self.current_position = None, None

        # Calculate performance
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        return curve
