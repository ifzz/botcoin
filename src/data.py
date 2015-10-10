from datetime import datetime
import logging
import os

import numpy as np
import pandas as pd

from .event import MarketEvent

class MarketData(object):
    def update_bars(self):
        logging.critical('This method needs to be implemented by your subclass!')
    
    def bars(self, symbol, N=1):
        logging.critical('This method needs to be implemented by your subclass!')


class HistoricalCSV(MarketData):

    def __init__(self, csv_dir, symbol_list, date_from='', date_to='',
                 normalize_prices=True, normalize_volume=True, round_decimals=2):

        # To keep track how long loading everything took
        start_load_datetime = datetime.now()
        self.symbol_list = symbol_list
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
                for c in ('open', 'high', 'low', 'volume'):
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

    def update_bars(self):
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

            self.this_datetime = datetime
            
            return MarketEvent()

        except StopIteration:
            self.continue_execution = False

    def bars(self, symbol, N=1):
        """
        Returns Bars object containing latest N bars from self._latest_bars

        N can't be 0, will be automatically changed to 1
        """
        N=1 if N==0 else N
        return Bars(self.symbol_data[symbol]['latest_bars'][-N:])

    def past_bars(self, symbol, N=1):
        """Returns Bars discarding the very last result to simulate data
        past the current date
        """
        N=1 if N==0 else N
        if len(self.symbol_data[symbol]['latest_bars'][-(N+1):-1]) > 0:
            return Bars(self.symbol_data[symbol]['latest_bars'][-(N+1):-1])
        else:
            return []

    def today(self, symbol):
        """Returns last Bar in self._latest_bars"""
        return Bar(self.symbol_data[symbol]['latest_bars'][-1:])

    def yesterday(self, symbol):
        """Returns last Bar in self._latest_bars"""
        if len(self.symbol_data[symbol]['latest_bars'][-2:-1]) > 0:
            return Bar(self.symbol_data[symbol]['latest_bars'][-2:-1])
        else:
            return []

class Bar(object):
    """Represents a single bar, usually today"""
    def __init__(self,latest_bars):
        if not latest_bars:
            raise ValueError("latest_bars needed to create Bars object")

        self.datetime = latest_bars[-1][0]
        self.open = latest_bars[-1][1]
        self.high = latest_bars[-1][2]
        self.low = latest_bars[-1][3]
        self.close = latest_bars[-1][4]
        self.vol = latest_bars[-1][5]

    def __len__(self):
        return 1

class Bars(object):
    """Multiple Bars, usually from past data"""
    def __init__(self,latest_bars):
        if not latest_bars:
            raise ValueError("latest_bars needed to create Bars object")
        self._latest_bars = latest_bars

        self.datetime = [i[0] for i in latest_bars]
        self.today_datetime = latest_bars[-1][0]

        self.open = [i[1] for i in latest_bars]
        self.today_open = self._latest_bars[-1][1]

        self.high = [i[2] for i in latest_bars]
        self.today_high = latest_bars[-1][2]

        self.low = [i[3] for i in latest_bars]
        self.today_low = latest_bars[-1][3]

        self.close = [i[4] for i in latest_bars]
        self.today_close = latest_bars[-1][4]

        self.vol = [i[5] for i in latest_bars]
        self.today_vol = latest_bars[-1][5]

    def __len__(self):
        return len(self._latest_bars)


def yahoo_api(list_of_symbols, year_from=1900, period='d', remove_adj_close=False):
    import urllib.request
    from settings import DATA_DIR, YAHOO_API

    for s in list_of_symbols:
        csv = urllib.request.urlopen(YAHOO_API.format(s,year_from,period))#.read().decode('utf-8')
        df = pd.io.parsers.read_csv(
            csv,
            header=0,
            index_col=0,
        )
        df = df.reindex(index=df.index[::-1])
        if remove_adj_close:
            df.drop('Adj Close', axis=1, inplace=True)
        df.to_csv(os.path.join(DATA_DIR, s+'.csv'), header=False)
