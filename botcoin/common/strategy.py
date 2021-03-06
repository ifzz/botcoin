import datetime
import logging
import queue

import numpy as np

from botcoin.common.events import SignalEvent

class Strategy(object):
    """
    Strategy root class.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.initialize()
        self.positions = {s:SymbolStatus() for s in self.SYMBOL_LIST}
        self.subscribed_symbols = set()
        self.unsubscribe_all = False

    def __str__(self):
        return self.__class__.__name__ + "(" + ",".join([str(i) for i in self.args]) + ")"

    def get_arg(self, index, default=None):
        if isinstance(index, int):
            try:
                return self.args[index]
            except IndexError:
                return default

        elif isinstance(index, str):
            try:
                return self.kwargs[index]
            except KeyError:
                return default

    def buy(self, symbol, price=None):
        if self.is_neutral(symbol):
            self._signal_dispatcher('BUY', symbol, price)

    def sell(self, symbol, price=None):
        if self.is_long(symbol):
            self._signal_dispatcher('SELL', symbol, price)

    def short(self, symbol, price=None):
        if self.is_neutral(symbol):
            self._signal_dispatcher('SHORT', symbol, price)

    def cover(self, symbol, price=None):
        if self.is_short(symbol):
            self._signal_dispatcher('COVER', symbol, price)

    def _signal_dispatcher(self, operation, symbol, price=None):
        if operation not in ('BUY', 'SELL', 'SHORT', 'COVER'):
            raise ValueError("Operation needs to be BUY SELL SHORT or COVER.")
        price = price or self.market.last_price(symbol)

        self.positions[symbol].update(operation, price)
        sig = SignalEvent(symbol, operation, price)
        self.events_queue.put(sig)

    def _market_opened(self):
        # Restart symbol subscriptions
        self.subscribed_symbols = set()
        self.unsubscribe_all = False

    def _call_strategy_method(self, method_name, symbol=None):
        method = getattr(self, method_name)
        if symbol:
            if self.is_subscribed_to(symbol):
                method(symbol)
        else:
            method()

    # Methods that should be overrided by each algorithm
    def before_open(self):
        pass

    def open(self, symbol):
        pass

    def during(self, symbol):
        pass

    def close(self, symbol):
        pass

    def after_close(self):
        pass

    def backtest_done(self, performance):
        pass

    # Symbol state methods and properties
    @property
    def long_symbols(self):
        return [s for s in self.positions if self.positions[s].status == 'BUY']

    @property
    def short_symbols(self):
        return [s for s in self.positions if self.positions[s].status == 'SHORT']

    def is_long(self, symbol):
        return True if self.positions[symbol].status == 'BUY' else False

    def is_short(self, symbol):
        return True if self.positions[symbol].status == 'SHORT' else False

    def is_neutral(self, symbol):
        return True if self.positions[symbol].status == '' else False

    def is_subscribed_to(self, symbol):
        if not self.unsubscribe_all and (symbol in self.subscribed_symbols or not self.subscribed_symbols):
            return True
        return False

    def subscribe(self, symbol):
        """ Once subscried, this symbol's MarketEvents will be raised on
        open, during_low, during_high and close. This is used to simulate
        a real time feed on a live trading algorithm. """
        self.subscribed_symbols.add(symbol)

    def unsubscribe(self, symbol=None):
        """ Unsubscribes from symbol. If subscribed_symbols is empty, will
        start it based on SYMBOL_LIST and remove symbol from it. """
        if not symbol:
            self.unsubscribe_all = True
        else:
            if not self.subscribed_symbols:
                self.subscribed_symbols = set(self.market.symbol_list)
            self.subscribed_symbols.remove(symbol)

    def trade_profitability(self, direction, entry_price, exit_price):
        """ Checks if, given an entry and exit price, a trade would be profitable.
        Uses same methods from risk that are used to calculate position size by
        portfolio.
        """
        quantity, entry_comm = self.risk.calculate_quantity_and_commission(direction, entry_price)
        exit_comm = self.risk.determine_commission(quantity, exit_price)
        total_comm = entry_comm + exit_comm
        return (exit_price - entry_price)*quantity - total_comm

class SymbolStatus(object):
    def __init__(self, status=''):
        self.status = status
        self.entry_price = ''
        self.exit_price = ''

    def update(self, operation, price):
        self.status = operation if operation in ('BUY', 'SHORT') else ''
        # Update entry price if BUY or SHORT
        self.entry_price = price if operation in ('BUY', 'SHORT') else self.entry_price
        # Update exit_price if SELL or COVER
        self.exit_price = price if  operation in ('SELL', 'COVER') else self.exit_price
        self.updated_at = datetime.datetime.now()

    def __str__(self):
        return self.status
