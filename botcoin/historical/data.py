from datetime import datetime
import logging
import os

import numpy as np
import pandas as pd

from botcoin.data import MarketData
from botcoin.errors import NoBarsException, NotEnoughBarsException, EmptyBarsException
from botcoin.event import MarketEvent
from botcoin import settings

class HistoricalCSV(MarketData):

    def __init__(self, csv_dir, symbol_list, date_from='', date_to='',
                 normalize_prices=True, normalize_volume=True, round_decimals=2,
                 download_data_yahoo=False):

        if download_data_yahoo:
            yahoo_api(symbol_list, csv_dir)

        # To keep track how long loading everything took
        start_load_datetime = datetime.now()
        self.symbol_list = sorted(list(set(symbol_list)))
        self.symbol_data = {}
        comb_index = None

        for s in symbol_list:
            self.symbol_data[s] = {}
            filename = s + '.csv'
            df = self._load_csv(csv_dir, filename, date_from, date_to, normalize_prices, normalize_volume, round_decimals)

            # Original dataframe from csv
            self.symbol_data[s]['df'] = df

            # Combine different file indexes to account for nonexistent values
            # (needs 'is not None' because of Pandas 'The truth value of a DatetimeIndex is ambiguous.' error)
            comb_index = comb_index.union(self.symbol_data[s]['df'].index) if comb_index is not None else self.symbol_data[s]['df'].index

        # After combining all indexes, we can run iterrows in each df
        for s in symbol_list:
            # Original dataframe, padded
            self.symbol_data[s]['df'] = self._pad_empty_values(self.symbol_data[s]['df'].reindex(index=comb_index, method=None))

            # Dataframe iterrows  generator
            self.symbol_data[s]['bars'] = self.symbol_data[s]['df'].iterrows()
            # List that will hold all rows from iterrows, one at a time
            self.symbol_data[s]['latest_bars'] = []

        self.continue_execution = True
        self.date_from = self.symbol_data[self.symbol_list[0]]['df'].index[0]
        self.date_to = self.symbol_data[self.symbol_list[0]]['df'].index[-1]
        self.load_time = datetime.now()-start_load_datetime
        self.subscription_list = []

    def _load_csv(self, csv_dir, filename, date_from, date_to,
                  normalize_adj_close, normalize_volume, round_decimals):

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
            if normalize_adj_close:
                for c in ('open', 'high', 'low'):
                    df[c] = df[c]*(df['adj_close']/df['close'])
                df['close'] = df['adj_close']

        # Rounding prices
        for c in ('open', 'high', 'low', 'close', 'adj_close'):
            df[c] = df[c].round(round_decimals)

        df = df[date_from:] if date_from else df
        df = df[:date_to] if date_to else df

        if df.empty:
            logging.warning("Empty DataFrame loaded for {}.".format(filename)) # Possibly invalid date ranges?

        return df

    @staticmethod
    def _pad_empty_values(df):
        # Fill NaN with 0 in volume column
        df['volume'] = df['volume'].fillna(0)
        # Pad close price forward
        df['close'] = df['close'].ffill()
        # Fill any remaining close NaN in 0 (e.g. beginning of file)
        df['close'] = df['close'].fillna(0)

        # Fill open high and low NaN with close price
        for col in ['open', 'high', 'low']:
            df[col] = df[col].fillna(df['close'])

        return df

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

    def _update_bars(self):
        """
        Generator that updates all prices based on historical data and raises
        MarketEvents to simulate live trading. The order of events is:
            before_open - single event
            open - one event per symbol
            during - two events per symbol (low and high, depending if positive
                     negative day)
            close - one event per symbol
            after_close - single event

        Before raising MarketEvents, all prices need to be updated to maintain
        consistency otherwise portfolio_value will be calculated based on open price
        and it will influence position size calculation
        """

        try:
            for s in self.symbol_list:
                new_row = next(self.symbol_data[s]['bars']) #df.iterows

                datetime = new_row[0]
                openp = new_row[1][0]
                highp = new_row[1][1]
                lowp = new_row[1][2]
                closep = new_row[1][3]
                volume = new_row[1][4]

                if not (highp>=lowp and highp>=openp and highp>=closep and
                    lowp<=openp and lowp<=closep):
                    raise ValueError("Data inconsistency on " + s + " at " +
                        str(datetime) + ". OHLC is " + str(openp) + " " +
                        str(highp) + " " + str(lowp) + " " + str(closep) +
                        ". High price must be >= all other prices" +
                        " and low price must be <= all other prices"
                    )

                bar = tuple([
                    datetime,
                    openp,
                    highp,
                    lowp,
                    closep,
                    volume,
                ])

                self.symbol_data[s]['latest_bars'].append(bar)

            self.datetime = datetime


            # Resets subscribed_symbols (see self.subscribe() comments)
            self.subscribed_symbols = set()

            # Before open
            yield MarketEvent('before_open')

            # On open - open = latest_bars[-1][1]
            for s in self.symbol_list:
                self.symbol_data[s]['current_price'] = self.symbol_data[s]['latest_bars'][-1][1]
            for s in self.symbol_list:
                if s in self.subscribed_symbols or not self.subscribed_symbols:
                    yield MarketEvent('open', s)

            # During #1
            for s in self.symbol_list:
                d = self.symbol_data[s]['latest_bars'][-1]
                self.symbol_data[s]['current_price'] = d[3] if d[4]>d[1] else d[2]
            for s in self.symbol_list:
                if s in self.subscribed_symbols or not self.subscribed_symbols:
                    yield MarketEvent('during', s)

            # During #2
            for s in self.symbol_list:
                d = self.symbol_data[s]['latest_bars'][-1]
                self.symbol_data[s]['current_price'] = d[2] if d[4]>d[1] else d[3]
            for s in self.symbol_list:
                if s in self.subscribed_symbols or not self.subscribed_symbols:
                    yield MarketEvent('during', s)

            # On close
            for s in self.symbol_list:
                self.symbol_data[s]['current_price'] = self.symbol_data[s]['latest_bars'][-1][4]
            for s in self.symbol_list:
                if s in self.subscribed_symbols or not self.subscribed_symbols:
                    yield MarketEvent('close', s)

            # After close, current_price will still be close
            yield MarketEvent('after_close')

        except StopIteration:
            self.continue_execution = False

    def price(self, symbol):
        """ Returns 'current' price """
        return self.symbol_data[symbol]['current_price']

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
            raise NoBarsException("Something wrong with latest_bars")

        if len(bars) != N:
            raise NotEnoughBarsException("Not enough bars yet")

        if len([bar for bar in bars if bar[4] > 0.0]) != len(bars):
            raise EmptyBarsException("Latest_bars has one or more 0.0 close price(s) within, and will be disconsidered.")

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


def yahoo_api(list_of_symbols, data_dir, year_from=1900, period='d', remove_adj_close=False):
    import urllib.request
    from urllib.request import HTTPError
    from botcoin.settings import YAHOO_API
    logging.warning("Downloading {} symbols from Yahoo. Please wait.".format(len(list_of_symbols)))

    for s in list_of_symbols:
        try:
            csv = urllib.request.urlopen(YAHOO_API.format(s,year_from,period))#.read().decode('utf-8')
            df = pd.io.parsers.read_csv(
                csv,
                header=0,
                index_col=0,
            )
            df = df.reindex(index=df.index[::-1])
            if remove_adj_close:
                df.drop('Adj Close', axis=1, inplace=True)
            df.to_csv(os.path.join(data_dir, s+'.csv'), header=False)
        except HTTPError:
            logging.error('Failed to fetch {}'.format(s))
