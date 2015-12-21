from datetime import datetime
import logging
import numpy as np
import os
import pandas as pd

from botcoin.common.errors import NoBarsError, NotEnoughBarsError, EmptyBarsError
from botcoin.common.event import MarketEvent

class MarketData(object):
    """ General MarketData that is subclassed in both live and backtest modes. """

    def __init__(self, csv_dir, symbol_list, normalize_prices, normalize_volume, round_decimals):

        # To keep track how long loading everything took
        start_load_datetime = datetime.now()
        self.symbol_list = sorted(list(set(symbol_list)))
        # Dictionary where all symbol data is kept
        self._data = {}
        # events_queue for all portfolios using this market object
        self.events_queue_list = []

        # Parsing csvs, treating data and setting bars
        self._read_all_csvs(csv_dir, normalize_prices, normalize_volume, round_decimals)
        self._check_data_consistency()
        self._pad_empty_values()

        self.load_time = datetime.now()-start_load_datetime
        self._round_decimals = round_decimals

    def _read_all_csvs(self, csv_dir, normalize_prices, normalize_volume, round_decimals):

        comb_index = None

        for s in self.symbol_list:

            self._data[s] = {}
            filename = s + '.csv'

            self._data[s]['df'] = self._read_csv(csv_dir, filename, normalize_prices, normalize_volume, round_decimals)

            # Combine different file indexes to account for nonexistent values
            # (needs 'is not None' because of Pandas 'The truth value of a DatetimeIndex is ambiguous.' error)
            comb_index = comb_index.union(self._data[s]['df'].index) if comb_index is not None else self._data[s]['df'].index

        # Reindex
        for s in self.symbol_list:
            self._data[s]['df'] = self._data[s]['df'].reindex(index=comb_index, method=None)

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

    def _check_data_consistency(self):
        inconsistencies = []
        for s in self.symbol_list:
            df = self._data[s]['df']

            if (df['high'] < df['low']).any() == True:
                dates = df.loc[(df['high'] < df['low']) == True].index
                inconsistencies.append('{} high < low on {}'.format(s, dates))

            if (df['high'] < df['open']).any() == True:
                dates = df.loc[(df['high'] < df['open']) == True].index
                inconsistencies.append('{} high < open on {}'.format(s, dates))

            if (df['high'] < df['close']).any() == True:
                dates = df.loc[(df['high'] < df['close']) == True].index
                inconsistencies.append('{} high < close on {}'.format(s, dates))

            if (df['low'] > df['open']).any() == True:
                dates = df.loc[(df['low'] > df['open']) == True].index
                inconsistencies.append('{} low > open on {}'.format(s, dates))

            if (df['low'] > df['close']).any() == True:
                dates = df.loc[(df['low'] > df['close']) == True].index
                inconsistencies.append('{} low > close on {}'.format(s, dates))

        if inconsistencies:
            raise ValueError('Possible inconsistencies in data, cancelling backtest.\n' + '\n'.join(inconsistencies))

    def _pad_empty_values(self):

        for s in self.symbol_list:
            df = self._data[s]['df']

            # Fill NaN with 0 in volume column
            df['volume'] = df['volume'].fillna(0)
            # Pad close price forward
            df['close'] = df['close'].ffill()
            # Fill any remaining close NaN in 0 (e.g. beginning of file)
            df['close'] = df['close'].fillna(0)

            # Fill open high and low NaN with close price
            for col in ['open', 'high', 'low']:
                df[col] = df[col].fillna(df['close'])

            self._data[s]['df'] = df

    def _relay_market_event(self, e):
        """ Puts e, which should be a MarketEvent on all queues in self.events_queue_list """
        if isinstance(e, MarketEvent):
            [q.put(e) for q in self.events_queue_list]
        else:
            raise TypeError("MarketData._relay_market_event only accepts MarketEvent objects.")

    def _todays_bar(self, symbol):
        """ Returns today's prices, volume and last_timestamp as an ordered tuple. """

        if 'last_timestamp' in self._data[symbol]:
            return (
                self._data[symbol]['last_timestamp'],
                self._data[symbol]['open'],
                self._data[symbol]['high'],
                self._data[symbol]['low'],
                self._data[symbol]['close'],
                self._data[symbol]['volume'],
            )

    def last_price(self, symbol):
        """ Returns last recorded price """
        if not 'last_price' in self._data[symbol]:
            raise NoBarsError
        return self._data[symbol]['last_price']

    def change(self, symbol):
        """ Returns change between last close and last recorded price """
        # In case execution just started and there is no current price
        if not 'last_price' in self._data[symbol]:
            raise NoBarsError
        last_close = self.yesterday(symbol).close
        return self._data[symbol]['last_price']/last_close - 1

    def bars(self, symbol, N=1):
        """ Returns latest N bars including today's values """
        return self._bar_dispatcher('bars', symbol, N)

    def past_bars(self, symbol, N=1):
        """ Returns latest N bars not including today's values """
        return self._bar_dispatcher('past_bars', symbol, N)

    def today(self, symbol):
        """ Returns today's OHLC values in a bar """
        return self._bar_dispatcher('today', symbol)

    def yesterday(self, symbol):
        """ Returns yesterday's values - last bar in self._latest_bars """
        return self._bar_dispatcher('yesterday', symbol)

    def _bar_dispatcher(self, option, symbol, N=1, ):
        if option == 'today':
            bars = [self._todays_bar(symbol)]
            # bars = self._data[symbol]['latest_bars'][-1:]  # old implementation

        elif option == 'yesterday':
            bars = self._data[symbol]['latest_bars'][-1:]

        elif option == 'bars':
            bars = self._data[symbol]['latest_bars'][-(N-1):]
            bars.append(self._todays_bar(symbol))

        elif option == 'past_bars':
            bars = self._data[symbol]['latest_bars'][-N:]
            # bars = self._data[symbol]['latest_bars'][-(N+1):-1]  # old implementation

        if not bars:
            raise NoBarsError("Something wrong with latest_bars")

        if len(bars) != N:
            raise NotEnoughBarsError("Not enough bars yet")

        if len([bar for bar in bars if bar[4] > 0.0]) != len(bars):
            raise EmptyBarsError("Latest_bars for {} has one or more 0.0 close prices, and will be disconsidered.".format(symbol))

        result = Bars(bars, self._round_decimals, True) if option in ('today', 'yesterday') else Bars(bars, self._round_decimals, )
        return result


class Bars(object):
    """
    Object exposed to users to reflect prices on a single or on multiple days.
    """
    def __init__(self, latest_bars, round_decimals, single_bar=False):
        self.length = len(latest_bars)
        self._round_decimals = round_decimals

        if single_bar:
            self.last_timestamp = latest_bars[-1][0]
            self.open = latest_bars[-1][1]
            self.high = latest_bars[-1][2]
            self.low = latest_bars[-1][3]
            self.close = latest_bars[-1][4]
            self.vol = latest_bars[-1][5]
        else:
            self.last_timestamp = [i[0] for i in latest_bars]
            self.open = [i[1] for i in latest_bars]
            self.high = [i[2] for i in latest_bars]
            self.low = [i[3] for i in latest_bars]
            self.close = [i[4] for i in latest_bars]
            self.vol = [i[5] for i in latest_bars]

    def mavg(self, price_type='close'):
        return np.round(
            np.mean(getattr(self, price_type)),
            self._round_decimals
        )

    def bollingerbands(self, k, price_type='close'):
        ave = np.mean(getattr(self, price_type))
        sd = np.std(getattr(self, price_type))
        upband = ave + (sd*k)
        lwband = ave - (sd*k)
        return np.round(ave,self._round_decimals), np.round(upband,self._round_decimals), np.round(lwband,self._round_decimals)

    def __len__(self):
        return self.length
