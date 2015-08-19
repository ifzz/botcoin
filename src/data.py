from datetime import datetime
import logging
import os
import pandas as pd

from .event import MarketEvent

class MarketData(object):
    def update_bars(self):
        logging.critical('This method needs to be implemented by your subclass!')
    
    def bars(self, symbol, N=1):
        logging.critical('This method needs to be implemented by your subclass!')


class HistoricalCSV(MarketData):

    def __init__(self, csv_dir, symbol_list, date_from='', date_to='', filetype='ohlc', interval=''):

        # To keep track how long loading everything took
        start_load_datetime = datetime.now()
        comb_index = None
        self.symbol_list = symbol_list
        self.symbol_data = {}

        for s in symbol_list:
            self.symbol_data[s] = {}
            filename = s + '.csv'
            df = self._load_csv(csv_dir, filename, date_from, date_to, filetype, interval)
            
            # Original dataframe from csv
            self.symbol_data[s]['df'] = df
            
            # Calculating average delta between each row
            delta_df = pd.DataFrame({'date':df.index})
            delta_df['delta'] = (delta_df['date'] - delta_df['date'].shift(1))
            self.symbol_data[s]['delta'] = (delta_df['delta'].mean())

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

        # If not all symbols have the same delta
        if len(set([self.symbol_data[s]['delta'] for s in symbol_list])) > 1:
            logging.critical('Data files have different time deltas between bars - not a good sign! You should probably check that.')

        self.continue_execution = True

        self.load_time = datetime.now()-start_load_datetime

    def _load_csv(self, csv_dir, filename, date_from, date_to, filetype, interval):
        if filetype == 'ohlc':
            df = self._load_csv_ohlc(csv_dir, filename)
        elif filetype == 'tick':
            if not interval:
                # If using tick data, needs an interval to create ohlc
                raise ValueError
            df = self._load_csv_tick(csv_dir, filename, interval)
        else:
            raise ValueError
        
        df = df[date_from:] if date_from else df
        df = df[:date_to] if date_to else df
        
        return df

    @staticmethod
    def _load_csv_tick(csv_dir, filename, interval):
        
        interval = interval or '1d'

        df = pd.io.parsers.read_csv(
            os.path.expanduser(csv_dir+filename),
            header=0, 
            index_col=0, 
            names=['timestamp', 'price', 'volume']
        )
        df.index = pd.to_datetime((df.index.values*1e9).astype(int))
        df = pd.concat(
            [
                df['price'].resample(interval, how='ohlc'),
                df['volume'].resample(interval, how='sum'),
            ],
            axis=1,
        )
        return df

    @staticmethod
    def _load_csv_ohlc(csv_dir, filename):
        
        df = pd.io.parsers.read_csv(
            os.path.expanduser(csv_dir+filename),
            header=None,
            index_col=0,
            names=['datetime', 'open', 'high', 'low', 'close', 'volume']
        )

        try:
            # Tries to index with %Y-%m-%d %H:%M:%S format
            df.index = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M:%S')
        except ValueError:
            # On ValueError try again with %Y-%m-%d
            df.index = pd.to_datetime(df.index, format='%Y-%m-%d')

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
                    raise ValueError("Data inconsistency at " +
                        datetime +
                        ". High price must be >= all other prices"
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
            
            return MarketEvent()

        except StopIteration:
            self.continue_execution = False
        
    def bars(self, symbol, N=1):
        """
        Returns Bars object containing latest N bars from self._latest_bars
        """
        return Bars(self.symbol_data[symbol]['latest_bars'][-N:])

class Bars(object):

    def __init__(self,latest_bars):
        if not latest_bars:
            raise ValueError("latest_bars needed to create Bars object")

        self._latest_bars = latest_bars

        self.datetime = [i[0] for i in self._latest_bars]
        self.last_datetime = self._latest_bars[-1][0]

        self.open = [i[1] for i in self._latest_bars]
        self.last_open = self._latest_bars[-1][1]

        self.high = [i[2] for i in self._latest_bars]
        self.last_high = self._latest_bars[-1][2]

        self.low = [i[3] for i in self._latest_bars]
        self.last_low = self._latest_bars[-1][3]

        self.close = [i[4] for i in self._latest_bars]
        self.last_close = self._latest_bars[-1][4]

        self.vol = [i[5] for i in self._latest_bars]
        self.last_vol = self._latest_bars[-1][5]

    def __len__(self):
        return len(self._latest_bars)

    def get_all_prices(self):
        return self.open, self.high, self.low, self.close

    def get_all(self):
        return self.datetime, self.open, self.high, self.low, self.close, self.vol
