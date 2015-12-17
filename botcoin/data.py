from datetime import datetime
import logging
import numpy as np
import os
import pandas as pd

from botcoin.errors import NoBarsError, NotEnoughBarsError, EmptyBarsError

class MarketData(object):
    """ General MarketData that is subclassed in both live and backtest modes. """

    def __init__(self, csv_dir, symbol_list, normalize_prices, normalize_volume, round_decimals):

        # To keep track how long loading everything took
        start_load_datetime = datetime.now()
        self.symbol_list = sorted(list(set(symbol_list)))
        self.symbol_data = {}

        self._read_all_csvs(csv_dir, normalize_prices, normalize_volume, round_decimals)

        self._pad_empty_values()

        self.load_time = datetime.now()-start_load_datetime
        self.round_decimals = round_decimals

    def _read_all_csvs(self, csv_dir, normalize_prices, normalize_volume, round_decimals):

        comb_index = None

        for s in self.symbol_list:

            self.symbol_data[s] = {}
            filename = s + '.csv'

            self.symbol_data[s]['df'] = self._read_csv(csv_dir, filename, normalize_prices, normalize_volume, round_decimals)

            # Combine different file indexes to account for nonexistent values
            # (needs 'is not None' because of Pandas 'The truth value of a DatetimeIndex is ambiguous.' error)
            comb_index = comb_index.union(self.symbol_data[s]['df'].index) if comb_index is not None else self.symbol_data[s]['df'].index

        # Reindex
        for s in self.symbol_list:
            self.symbol_data[s]['df'] = self.symbol_data[s]['df'].reindex(index=comb_index, method=None)

    @staticmethod
    def _read_csv(csv_dir, filename, normalize_prices,
                  normalize_volume, round_decimals):

        df = pd.io.parsers.read_csv(
            os.path.expanduser(csv_dir+filename),
            header=None,
            index_col=0,
            names=['datetime', 'open', 'high', 'low', 'close', 'volume', 'adj_close']
        )

        try:
            # Tries to index with %Y-%m-%d %H:%M:%S format
            df.index = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M:%S')
        except ValueError:
            # On ValueError try again with %Y-%m-%d
            df.index = pd.to_datetime(df.index, format='%Y-%m-%d')


        if not df['adj_close'].empty:
            # Rounding adj_close to prevent rounding problems when low == close
            df['adj_close'] = df['adj_close'].round(round_decimals)

            # Normalizing prices and volume based on adj_close prices
            if normalize_volume:
                df['volume'] = df['volume']*(df['adj_close']/df['close'])
            if normalize_prices:
                for c in ('open', 'high', 'low'):
                    df[c] = df[c]*(df['adj_close']/df['close'])
                df['close'] = df['adj_close']

        # Rounding prices
        for c in ('open', 'high', 'low', 'close', 'adj_close'):
            df[c] = df[c].round(round_decimals)

        return df

    def _pad_empty_values(self):

        for s in self.symbol_list:
            df = self.symbol_data[s]['df']

            # Fill NaN with 0 in volume column
            df['volume'] = df['volume'].fillna(0)
            # Pad close price forward
            df['close'] = df['close'].ffill()
            # Fill any remaining close NaN in 0 (e.g. beginning of file)
            df['close'] = df['close'].fillna(0)

            # Fill open high and low NaN with close price
            for col in ['open', 'high', 'low']:
                df[col] = df[col].fillna(df['close'])

            self.symbol_data[s]['df'] = df

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
        """
        Returns Bars discarding the very last result to simulate data past the current date
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

        result = Bars(bars, self.round_decimals, True) if option in ('today', 'yesterday') else Bars(bars, self.round_decimals, )
        return result


class Bars(object):
    """Multiple Bars, usually from past data"""
    def __init__(self, latest_bars, round_decimals, single_bar=False):
        self.length = len(latest_bars)
        self.round_decimals = round_decimals

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
            self.round_decimals
        )

    def bollingerbands(self, k, price_type='close'):
        ave = np.mean(getattr(self, price_type))
        sd = np.std(getattr(self, price_type))
        upband = ave + (sd*k)
        lwband = ave - (sd*k)
        return np.round(ave,self.round_decimals), np.round(upband,self.round_decimals), np.round(lwband,self.round_decimals)

    def __len__(self):
        return self.length
