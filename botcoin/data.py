from botcoin.errors import NoBarsError, NotEnoughBarsError, EmptyBarsError

class MarketData(object):

    def subscribe(self, symbol):
        """ Once subscried, this symbol's MarketEvents will be raised on
        open, during_low, during_high and close. This is used to simulate
        a real time feed on a live trading algorithm. """
        self.subscribed_symbols.add(symbol)

    def unsubscribe(self, symbol):
        """ Unsubscribes from symbol. If subscribed_symbols is empty, will
        start it based on SYMBOL_LIST and remove symbol from it. """
        if not self.subscribed_symbols:
            self.subscribed_symbols = set(self.symbol_list)
        self.subscribed_symbols.remove(symbol)

    def price(self, symbol):
        """ Returns 'current' price """
        if not 'current_price' in self.symbol_data[symbol]:
            raise NoBarsError
        return self.symbol_data[symbol]['current_price']

    def change(self, symbol):
        """ Returns change between last close and 'current' price """
        # In case execution just started and there is no current price
        if not 'current_price' in self.symbol_data[symbol]:
            raise NoBarsError
        last_close = self.yesterday(symbol).close
        return self.symbol_data[symbol]['current_price']/last_close - 1

    def bars(self, symbol, N=1):
        """
        Returns Bars object containing latest N bars from self._latest_bars
        """
        return self.bar_dispatcher('bars', symbol, N)

    def past_bars(self, symbol, N=1):
        """Returns Bars discarding the very last result to simulate data
        past the current date
        """
        return self.bar_dispatcher('past_bars', symbol, N)

    def today(self, symbol):
        """Returns last Bar in self._latest_bars"""
        return self.bar_dispatcher('today', symbol)

    def yesterday(self, symbol):
        """Returns last Bar in self._latest_bars"""
        return self.bar_dispatcher('yesterday', symbol)

    def bar_dispatcher(self, option, symbol, N=1, ):
        if option == 'today':
            bars = self.symbol_data[symbol]['latest_bars'][-1:]

        elif option == 'yesterday':
            bars = self.symbol_data[symbol]['latest_bars'][-2:-1]

        elif option == 'bars':
            bars = self.symbol_data[symbol]['latest_bars'][-N:]

        elif option == 'past_bars':
            bars = self.symbol_data[symbol]['latest_bars'][-(N+1):-1]

        if not bars:
            raise NoBarsError("Something wrong with latest_bars")

        if len(bars) != N:
            raise NotEnoughBarsError("Not enough bars yet")

        if len([bar for bar in bars if bar[4] > 0.0]) != len(bars):
            raise EmptyBarsError("Latest_bars has one or more 0.0 close price(s) within, and will be disconsidered.")

        result = Bars(bars, True) if option in ('today', 'yesterday') else Bars(bars)
        return result

class Bars(object):
    """Multiple Bars, usually from past data"""
    def __init__(self,latest_bars, single_bar=False):
        self.length = len(latest_bars)

        if single_bar:
            self.datetime = latest_bars[-1][0]
            self.open = latest_bars[-1][1]
            self.high = latest_bars[-1][2]
            self.low = latest_bars[-1][3]
            self.close = latest_bars[-1][4]
            self.vol = latest_bars[-1][5]
        else:
            self.datetime = [i[0] for i in latest_bars]
            self.open = [i[1] for i in latest_bars]
            self.high = [i[2] for i in latest_bars]
            self.low = [i[3] for i in latest_bars]
            self.close = [i[4] for i in latest_bars]
            self.vol = [i[5] for i in latest_bars]

    def mavg(self, price_type='close'):
        return np.round(
            np.mean(getattr(self, price_type)),
            settings.ROUND_DECIMALS
        )

    def bollingerbands(self, k, price_type='close'):
        ave = np.mean(getattr(self, price_type))
        sd = np.std(getattr(self, price_type))
        upband = ave + (sd*k)
        lwband = ave - (sd*k)
        round_dec = settings.ROUND_DECIMALS
        return np.round(ave,round_dec), np.round(upband,round_dec), np.round(lwband,round_dec)

    def __len__(self):
        return self.length
