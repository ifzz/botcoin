import datetime
import logging
from math import floor
import queue

import pandas as pd

from .event import MarketEvent, SignalEvent, OrderEvent
import settings
from .trade import Trade

class Portfolio(object):
    """
    Portfolio root class.
    """
    def __init__(self, initial_capital=None, position_size=None, 
                 max_long_pos=None, max_short_pos=None,):

        self.all_positions = []
        self.all_holdings = []
        self.current_positions = None
        self.current_holdings = None

        # Holds orders while they're being executed
        self.pending_orders = set()
        # Current open positions
        self.open_trades = {}
        # List of all closed trades
        self.all_trades = []

        self.initial_capital = initial_capital or settings.INITIAL_CAPITAL
        self.position_size = position_size or settings.POSITION_SIZE
        self.max_long_pos = max_long_pos or settings.MAX_LONG_POSITIONS
        self.max_short_pos = max_short_pos or settings.MAX_SHORT_POSITIONS

    def set_market_and_queue(self, events_queue, market):
        # check for symbol names that would conflict with columns used in holdings and positions
        for symbol in market.symbol_list:
            if symbol in ('cash', 'commission', 'total', 'returns', 'equity_curve', 'datetime'):
                raise ValueError("A symbol has an invalid name (e.g. 'cash', 'commission', etc)")
        # Main events queue shared with Market, Strategy and Execution
        self.events_queue = events_queue
        # Market data object
        self.market = market

    def update_from_market(self):
        """Used to add new position and holdings to portfolio, triggered by a new market signal"""
        
        if self.pending_orders:
            logging.warning("New market event arrived while there are pending orders. Shouldn't happen in backtesting.")

        # Can be any bar
        cur_datetime = self.market.bars(self.market.symbol_list[0]).this_datetime

        # If there is no current position and holding, meaning execution just started
        if not self.current_positions and not self.current_holdings:
            self.date_from = cur_datetime
            self.current_positions = self.construct_position(cur_datetime)

            self.current_holdings = self.construct_holding(cur_datetime, self.initial_capital, 0.00, self.initial_capital)

        else:
            if ((cur_datetime <= self.current_positions['datetime']) or 
                (cur_datetime <= self.current_holdings['datetime'])):
                raise ValueError("New bar arrived with same datetime as previous holding and position. Aborting!")

            # open_positions used for graphing and keeping track of open positions over time
            self.current_positions['open_trades'] = len(self.open_trades)
            

            # Restarts current_holdings 'total' and s based on this_close price and current_position[s]
            self.current_holdings['total'] = self.current_holdings['cash']
            open_long,open_short = 0,0
            for s in self.market.symbol_list:
                # Approximation to the real value
                market_value = self.current_positions[s] * self.market.bars(s).this_close
                
                if market_value < 0:
                    open_short += 1
                elif market_value > 0:
                    open_long += 1

                self.current_holdings[s] = market_value
                self.current_holdings['total'] += market_value

            self.verify_consistency(open_long, open_short)


            # Add current to all lists
            self.all_positions.append(self.current_positions)
            self.all_holdings.append(self.current_holdings)


            self.current_positions = self.construct_position(
                cur_datetime, 
                self.current_positions,
            )
            self.current_holdings = self.construct_holding(
                cur_datetime,
                self.current_holdings['cash'],
                self.current_holdings['commission'],
                self.current_holdings['total']
            )

    def generate_orders(self, signal):
        logging.debug(str(signal))

        symbol = signal.symbol
        sig_type = signal.signal_type
        exec_price = signal.exec_price
        
        bars = self.market.bars(symbol)

        # Not trading if there is no volume, or any price == 0.0
        if 0.0 in (bars.this_open, bars.this_high, bars.this_low, bars.this_close, bars.this_vol):
            return
        
        # Execution price adjusted for slippage
        adj_price = exec_price * (1+settings.MAX_SLIPPAGE)

        cur_position = self.current_positions[symbol]
        available_cash = self.current_holdings['cash'] - sum([i.estimated_cost for i in self.pending_orders])
        portf_value = self.current_holdings['total']

        order = None

        if sig_type in ('BUY', 'SHORT') and cur_position == 0:

            # Check for max positions
            if (len(self.open_trades) + len(self.pending_orders)) < self.max_long_pos:

                # Cash to be spent on this position
                position_cash = portf_value*self.position_size

                # Sometimes last position is a little over cash available
                # so we adjust it down a little bit
                if position_cash > available_cash:
                    if settings.ADJUST_POSITION_DOWN:
                        position_cash = available_cash
                    else:
                        logging.warning("Can't adjust position, {} missing cash.".format(str(position_size-available_cash)))
                        return

                # COMMISSION_FIXED remove the fixed ammount from cash,
                # and COMMISSION_PCT increases the symbol price to reflect the fee
                quantity = floor( (position_cash-settings.COMMISSION_FIXED) / (adj_price * (1+settings.COMMISSION_PCT)) )

                if quantity > 0.0:
                    estimated_cost = settings.COMMISSION_FIXED + (quantity * adj_price * (1+settings.COMMISSION_PCT))
                    order = OrderEvent(signal, symbol, quantity, sig_type, adj_price, estimated_cost)


        elif sig_type in ('SELL', 'COVER') and cur_position > 0:
            quantity = cur_position
            order = OrderEvent(signal, symbol, quantity, sig_type, adj_price)

        if order:
            logging.debug(str(order))
            self.pending_orders.add(order)
            self.events_queue.put(order)

    def update_from_fill(self, fill):
        logging.debug(str(fill))

        if not fill.type == 'FILL':
            raise TypeError("Wrong event type passed to Portfolio.consume_fill_event()")

        self.pending_orders.remove(fill.order)

        if fill.order.direction in ('BUY', 'SHORT'):
            self.open_trades[fill.symbol] = Trade(fill)

        elif fill.order.direction in ('SELL', 'COVER'):
            self.open_trades[fill.symbol].close_trade(fill)
            self.all_trades.append(self.open_trades[fill.symbol])
            del self.open_trades[fill.symbol]

        self.current_positions[fill.symbol] += fill.quantity

        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (fill.cost + fill.commission)
        
        # This is now being computed in update_positions_and_holdings instead of here 
        # self.current_holdings[fill.symbol] += fill.cost
        # self.current_holdings['total'] -= (fill.commission)

    def verify_consistency(self, open_long, open_short):
        """ Checks for problematic values in current holding and position """

        if (self.current_holdings['cash'] < 0 or
            self.current_holdings['total'] < 0 or
            self.current_holdings['commission'] < 0):
            logging.critical('Cash, total or commission is a negative value. This shouldn\'t be possible.')
            logging.critical('Cash={}, Total={}, Commission={}'.format(
                self.current_holdings['cash'],
                self.current_holdings['total'],
                self.current_holdings['commission'],
            ))
            raise AssertionError("Inconsistency in Portfolio.current_holdings()")
        
        if open_long > self.max_long_pos or open_short > self.max_short_pos:
            raise AssertionError("Number of open positions is too high. {}/{} open positions and {}/{} short positions".format(
                open_long,
                self.max_long_pos,
                open_short,
                self.max_short_pos,
            ))

        for s in self.market.symbol_list:
            if (self.current_positions[s] < 0 or self.current_holdings[s] < 0):
                logging.info('Do you really have a short position? {}:{}:{}'.format(s, self.current_positions[s]. self.current_holdings[s]))

    def update_last_positions_and_holdings(self):
        # Adds latest current position and holding into 'all' lists, so they
        # can be part of performance as well
        if self.current_positions and self.current_holdings:
            self.all_holdings.append(self.current_holdings)
            self.all_positions.append(self.current_positions)
            self.current_holdings, self.current_positions = None, None

        # "Fake close" trades that are open, so they can be part of trades performance stats
        for trade in self.open_trades.values():
            bars = self.market.bars(trade.symbol)

            direction = 1 if trade.direction in ('SELL','SHORT') else -1
            quantity = trade.quantity * direction

            self.all_trades.append(trade.fake_close_trade(
                bars.this_datetime,
                quantity * bars.this_close,
            ))                

    def construct_position(self, cur_datetime, current_positions={}):
        """
        Positions held at a point in time.
        Parameters:
            cur_datetime -- date of the point in time in question
            s -- dictionary with symbols as key and ammount owned as value
        """
        if not isinstance(cur_datetime, datetime.datetime) or not isinstance(current_positions, dict):
            raise TypeError("Improprer parameter type on Portfolio.construct_position()")

        if current_positions:
            position = dict((k,v) for k, v in [(s, current_positions[s]) for s in self.market.symbol_list])
        else:
            position = dict((k,v) for k, v in [(s, 0.0) for s in self.market.symbol_list])

        position['datetime'] = cur_datetime

        return position

    def construct_holding(self, cur_datetime, cash, commission, total):
        """
        Holdings at a point in time. All properties represented in cash.
        Parameters:
            cur_datetime -- date of the point in time in question
            cash -- cash held
            commission -- cummulative commission paid up to this day
            total -- cash equivalent of all holdings combined - commission paid
        """
        if not isinstance(cur_datetime, datetime.datetime):
            raise TypeError("Improprer parameter type on portfolio.construct_holding()")

        holding = {}

        holding['datetime'] = cur_datetime
        holding['cash'] = cash
        holding['commission'] = commission
        holding['total'] = total

        return holding

