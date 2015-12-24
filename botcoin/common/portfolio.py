import datetime
import logging
from math import floor
import queue

import numpy as np
import pandas as pd

from botcoin import settings
from botcoin.backtest.data import BacktestMarketData
from botcoin.common.execution import Execution
from botcoin.common.data import MarketData
from botcoin.common.errors import BarValidationError, NegativeExecutionPriceError, ExecutionPriceOutOfBandError
from botcoin.common.events import MarketEvent, SignalEvent, OrderEvent
from botcoin.common.strategy import Strategy
from botcoin.common.trade import Trade
from botcoin.live.data import LiveMarketData
from botcoin.utils import _round

class Portfolio(object):
    """
    Portfolio root class.
    """
    def __init__(self):

        self.all_positions = []
        self.all_holdings = []
        self.positions = None
        self.holdings = None

        # Holds orders while they're being executed
        self.pending_orders = set()
        # Current open positions
        self.open_trades = {}
        # List of all closed trades
        self.all_trades = []


    def set_modules(self, market, strategy, execution):
        if (not isinstance(market, MarketData) or
            not isinstance(strategy, Strategy) or
            not isinstance(execution, Execution)):
            raise TypeError("Improper parameter type on Portfolio.__init__()")

        # check for symbol names that would conflict with columns used in holdings and positions
        for symbol in market.symbol_list:
            if symbol in ('cash', 'commission', 'total', 'returns', 'equity_curve', 'datetime'):
                raise ValueError("A symbol has an invalid name. Invalid names are 'cash', 'commission','total', 'returns', 'equity_curve', 'datetime'.")

        # Main events queue shared with Market and Execution
        self.events_queue = queue.Queue()
        # Queue used to store signals raised by strategy
        self.signals_queue = queue.Queue()
        self.market = market
        self.strategy = strategy
        self.execution = execution

        # Grabbing config from strategy
        self.NORMALIZE_PRICES = settings.NORMALIZE_PRICES = getattr(strategy, 'NORMALIZE_PRICES', settings.NORMALIZE_PRICES)
        self.NORMALIZE_VOLUME = settings.NORMALIZE_VOLUME = getattr(strategy, 'NORMALIZE_VOLUME', settings.NORMALIZE_VOLUME)
        self.ROUND_LOT_SIZE = settings.ROUND_LOT_SIZE = getattr(strategy, 'ROUND_LOT_SIZE', settings.ROUND_LOT_SIZE)
        self.THRESHOLD_DANGEROUS_TRADE = settings.THRESHOLD_DANGEROUS_TRADE = getattr(strategy, 'THRESHOLD_DANGEROUS_TRADE', settings.THRESHOLD_DANGEROUS_TRADE)
        self.INITIAL_CAPITAL = settings.INITIAL_CAPITAL = getattr(strategy, 'INITIAL_CAPITAL', settings.INITIAL_CAPITAL)
        self.MAX_LONG_POSITIONS = settings.MAX_LONG_POSITIONS = floor(getattr(strategy, 'MAX_LONG_POSITIONS', settings.MAX_LONG_POSITIONS))
        self.MAX_SHORT_POSITIONS = settings.MAX_SHORT_POSITIONS = floor(getattr(strategy, 'MAX_SHORT_POSITIONS', settings.MAX_SHORT_POSITIONS))
        self.POSITION_SIZE = settings.POSITION_SIZE = getattr(strategy, 'POSITION_SIZE', 1.0/self.MAX_LONG_POSITIONS)
        self.ADJUST_POSITION_DOWN = settings.ADJUST_POSITION_DOWN = getattr(strategy, 'ADJUST_POSITION_DOWN', settings.ADJUST_POSITION_DOWN)
        self.COMMISSION_FIXED = settings.COMMISSION_FIXED = getattr(strategy, 'COMMISSION_FIXED', settings.COMMISSION_FIXED)
        self.COMMISSION_PCT = settings.COMMISSION_PCT = getattr(strategy, 'COMMISSION_PCT', settings.COMMISSION_PCT)
        self.MAX_SLIPPAGE = settings.MAX_SLIPPAGE = getattr(strategy, 'MAX_SLIPPAGE', settings.MAX_SLIPPAGE)

        # Setting attributes in execution
        self.execution.events_queue = self.events_queue
        self.execution.market = self.market
        self.execution.commmission_pct = self.COMMISSION_PCT
        self.execution.commission_fixed = self.COMMISSION_FIXED

        # Setting attributes in strategy
        self.strategy.signals_queue = self.signals_queue
        self.strategy.market = self.market

        # Setting attributes in market
        self.market.events_queue_list.append(self.events_queue)

    @property
    def long_positions(self):
        return [trade for trade in self.open_trades.values() if trade.direction in ('BUY')] + \
            [order for order in self.pending_orders if order.direction in ('BUY')]

    @property
    def short_positions(self):
        return [trade for trade in self.open_trades.values() if trade.direction in ('SHORT')] + \
            [order for order in self.pending_orders if order.direction in ('SHORT')]

    def run_cycle(self):
        while True:
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                # Done this way to be able to execute in between
                # signals that come all at once from strategy
                try:
                    event = self.signals_queue.get(False)
                except queue.Empty:
                    break

            if event.type == "MARKET":
                self.handle_market_event(event)

            elif event.type == "SIGNAL":
                self.generate_orders(event)

            elif event.type == "ORDER":
                self.execution.execute_order(event)

            elif event.type == "FILL":
                self.update_from_fill(event)

            else:
                raise TypeError("The fuck is this?")

    def handle_market_event(self, event):
        if event.sub_type == 'before_open':
            self.market_opened()
            self.strategy.market_opened()
            self.strategy.call_strategy_method('before_open')

        elif event.sub_type == 'after_close':
            self.market_closed()
            self.strategy.call_strategy_method('after_close')

        else:
                try:
                    if event.sub_type == 'open':
                        self.strategy.call_strategy_method('open', event.symbol)

                    elif event.sub_type == 'during':
                        self.strategy.call_strategy_method('during', event.symbol)

                    elif event.sub_type == 'close':
                        self.strategy.call_strategy_method('close', event.symbol)

                except BarValidationError as e:
                    # Problems in market bars or past_bars would raise BarValidationError
                    # e.g. nonexisting bars, bars with 0.0 or bars smaller than length
                    # requested should be disconsidered
                    pass

    def market_opened(self):
        cur_datetime = self.market.updated_at

        # If there is no current position and holding, meaning execution just started
        if not self.positions and not self.holdings:
            self.date_from = cur_datetime
            self.positions = self.construct_position(cur_datetime)

            self.holdings = self.construct_holding(cur_datetime, self.INITIAL_CAPITAL, 0.00, self.INITIAL_CAPITAL)

        else:
            if ((cur_datetime <= self.positions['datetime']) or
                (cur_datetime <= self.holdings['datetime'])):
                raise ValueError("New bar arrived with same datetime as previous holding and position. Aborting!")

            # Add current positions/holdings to all_positions/all_holdings lists
            self.all_positions.append(self.positions)
            self.all_holdings.append(self.holdings)

            self.positions = self.construct_position(
                cur_datetime,
                self.positions,
            )
            self.holdings = self.construct_holding(
                cur_datetime,
                self.holdings['cash'],
                self.holdings['commission'],
                self.holdings['total']
            )

    def market_closed(self):
        if self.pending_orders:
            logging.warning("Market closed while there are pending orders. Shouldn't happen in backtesting.")

        # open_positions used for keeping track of open positions over time
        self.positions['open_trades'] = len(self.open_trades)
        # subscribed_symbols used for keeping track of how many
        # symbols were subscribed to each day
        if self.strategy.unsubscribe_all:
            self.positions['subscribed_symbols'] = 0
        else:
            if self.strategy.subscribed_symbols:
                self.positions['subscribed_symbols'] = len(self.strategy.subscribed_symbols)
            else:
                self.positions['subscribed_symbols'] = len(self.market.symbol_list)

        # Restarts holdings 'total' and s based on this_close price and current_position[s]
        self.holdings['total'] = self.net_liquidation
        for s in self.market.symbol_list:
            self.holdings[s] = self.positions[s] * self.market.last_price(s)

        self.verify_consistency()

    def generate_orders(self, signal):
        logging.debug(str(signal))

        symbol = signal.symbol
        direction = signal.direction
        date = self.market.updated_at
        direction_mod = -1 if direction in ('SELL','SHORT') else 1

        exec_price = signal.exec_price or self.market.last_price(symbol)

        # Checks for common consistency errors in signals (usually sign of a broken strategy)
        self.check_signal_consistency(symbol, exec_price, direction)

        # Adjusted execution price for slippage
        adj_price = _round(exec_price * (1+self.MAX_SLIPPAGE*direction_mod))

        cur_position = self.positions[symbol]
        order = None

        if direction in ('BUY', 'SHORT') and cur_position == 0:
            # Cash to be spent on this position
            position_cash = self.net_liquidation*self.POSITION_SIZE
            # Quantity to BUY or SHORT
            quantity = 0

            if ((len(self.long_positions) < self.MAX_LONG_POSITIONS and direction == 'BUY') or
                (len(self.short_positions) < self.MAX_SHORT_POSITIONS and direction == 'SHORT')):

                # Adjust position down if not enough money and
                if direction == 'BUY':
                    if position_cash > self.cash_balance:
                        if self.ADJUST_POSITION_DOWN:
                            position_cash = self.cash_balance
                        else:
                            logging.warning("Can't adjust position, {} missing cash.".format(str(position_cash-cash_balance)))
                            return

                # COMMISSION_FIXED remove the fixed ammount from cash,
                # and COMMISSION_PCT increases the symbol price to reflect the fee
                quantity = direction_mod * (position_cash-self.COMMISSION_FIXED) / (adj_price * (1+self.COMMISSION_PCT))
                if self.ROUND_LOT_SIZE:
                    quantity = floor(quantity/self.ROUND_LOT_SIZE) * self.ROUND_LOT_SIZE

            if quantity != 0.0:
                commission = self.COMMISSION_FIXED + (self.COMMISSION_PCT * abs(quantity) * adj_price)
                estimated_cost = commission + (quantity * adj_price)
                order = OrderEvent(signal, symbol, quantity, direction, adj_price, estimated_cost, date)


        elif direction in ('SELL', 'COVER') and cur_position != 0:
            quantity = -1 * cur_position
            # Checks if there is a similar order in pending_orders to protect
            # against repeated signals coming from strategy
            if not [order for order in self.pending_orders if (order.symbol == symbol and order.quantity == quantity)]:
                order = OrderEvent(signal, symbol, quantity, direction, adj_price, quantity*adj_price, date)

        if order:
            logging.debug(str(order))
            self.pending_orders.add(order)
            self.events_queue.put(order)

    def update_from_fill(self, fill):
        logging.debug(str(fill))

        self.pending_orders.remove(fill.order)

        if fill.order.direction in ('BUY', 'SHORT'):
            self.open_trades[fill.symbol] = Trade(fill)

        elif fill.order.direction in ('SELL', 'COVER'):
            self.open_trades[fill.symbol].close_trade(fill)
            self.all_trades.append(self.open_trades[fill.symbol])
            del self.open_trades[fill.symbol]

        self.positions[fill.symbol] += fill.quantity

        self.holdings['commission'] += fill.commission
        self.holdings['cash'] -= (fill.cost + fill.commission)

    def verify_consistency(self):
        """ Checks for problematic values in current holding and position """

        if (self.holdings['cash'] < 0 or
            self.holdings['total'] < 0 or
            self.holdings['commission'] < 0):
            logging.critical('Cash, total or commission is a negative value. This shouldn\'t be possible.')
            logging.critical('Cash={}, Total={}, Commission={}'.format(
                self.holdings['cash'],
                self.holdings['total'],
                self.holdings['commission'],
            ))
            raise AssertionError("Inconsistency in Portfolio.holdings()")

        open_long = len(self.long_positions)
        open_short = len(self.short_positions)

        if open_long > self.MAX_LONG_POSITIONS or open_short > self.MAX_SHORT_POSITIONS:
            raise AssertionError("Number of open positions is too high. {}/{} open positions and {}/{} short positions".format(
                open_long,
                self.MAX_LONG_POSITIONS,
                open_short,
                self.MAX_SHORT_POSITIONS,
            ))

    def update_last_positions_and_holdings(self):
        # Adds latest current position and holding into 'all' lists, so they
        # can be part of performance as well
        if self.positions and self.holdings:
            self.all_holdings.append(self.holdings)
            self.all_positions.append(self.positions)
            self.holdings, self.positions = None, None

        # "Fake close" trades that are open, so they can be part of trades performance stats
        for trade in self.open_trades.values():

            direction = 1 if trade.direction in ('SELL','SHORT') else -1
            quantity = trade.quantity * direction

            self.all_trades.append(trade.fake_close_trade(
                self.market.updated_at,
                quantity * self.market.last_price(trade.symbol),
            ))

    def construct_position(self, cur_datetime, positions={}):
        """
        Positions held at a point in time.
        Parameters:
            cur_datetime -- date of the point in time in question
            s -- dictionary with symbols as key and ammount owned as value
        """
        if not isinstance(cur_datetime, datetime.datetime) or not isinstance(positions, dict):
            raise TypeError("Improprer parameter type on Portfolio.construct_position()")

        if positions:
            position = dict((k,v) for k, v in [(s, positions[s]) for s in self.market.symbol_list])
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

    def calc_performance(self):
        """
        Calculates multiple performance stats given a portfolio object.
        """
        def drawdown(curve):
            hwm = [0]
            eq_idx = curve.index
            drawdown = pd.Series(index = eq_idx)
            duration = pd.Series(index = eq_idx)

            # Loop over the index range
            for t in range(1, len(eq_idx)):
                cur_hwm = max(hwm[t-1], curve[t])
                hwm.append(cur_hwm)
                drawdown[t]= (hwm[t] - curve[t])/hwm[t]
                duration[t]= 0 if drawdown[t] == 0 else duration[t-1] + 1

            return drawdown.max()*100, duration.max()

        if not self.all_holdings:
            raise ValueError("Portfolio with empty holdings")
        results = {}

        # Saving all trades
        results['all_trades'] = pd.DataFrame(
            [(
                t.symbol,
                t.pnl,
                t.opened_at,
                t.closed_at,
                t.quantity,
                t.open_price,
                t.close_price,
                t.commission,
            ) for t in self.all_trades],
            columns=['symbol', 'pnl', 'open_datetime', 'close_datetime',
                     'quantity', 'open_price', 'close_price', 'commission'],
        )

        results['dangerous_trades'] = results['all_trades'][
            results['all_trades']['pnl'] >
            sum(results['all_trades']['pnl'])*self.THRESHOLD_DANGEROUS_TRADE
        ]

        # Saving portfolio.all_positions in performance
        curve = pd.DataFrame(self.all_positions)
        curve.set_index('datetime', inplace=True)
        results['all_positions'] = curve

        # Saving portfolio.all_holdings in performance
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        results['all_holdings'] = curve

        # Creating equity curve
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        results['equity_curve'] = curve['equity_curve']

        # Number of days elapsed between first and last bar
        days = (curve.index[-1]-curve.index[0]).days
        years = days/365.2425

        # Average bars each year, used to calculate sharpe ratio (N)
        avg_bars_per_year = len(curve.index)/years # curve.groupby(curve.index.year).count())

        # Total return
        results['total_return'] = ((curve['equity_curve'][-1] - 1.0) * 100.0)

        # Annualised return
        results['ann_return'] = results['total_return'] ** 1/years

        # Sharpe ratio
        results['sharpe'] = np.sqrt(avg_bars_per_year) * curve['returns'].mean() / curve['returns'].std() if curve['returns'].mean() else 0.0

        # Trades statistic
        results['trades'] = len(self.all_trades)
        results['trades_per_year'] = results['trades']/years
        results['pct_trades_profit'] = len([trade for trade in self.all_trades if trade.pnl > 0])/results['trades'] if results['trades'] else 0.0
        results['pct_trades_loss'] = len([trade for trade in self.all_trades if trade.pnl <= 0])/results['trades'] if results['trades'] else 0.0

        # Dangerous trades that constitute more than THRESHOLD_DANGEROUS_TRADE of returns
        results['dangerous'] = True if not results['dangerous_trades'].empty else False

        # Drawdown
        results['dd_max'], results['dd_duration'] = drawdown(results['equity_curve'])

        # Subscribed symbols
        results['subscribed_symbols'] = results['all_positions']['subscribed_symbols']
        results['avg_subscribed_symbols'] = results['all_positions']['subscribed_symbols'].mean()

        self.performance = results
        return results
