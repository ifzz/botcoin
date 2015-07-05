#!/usr/bin/env python
    
from datetime import datetime
import logging
import os
import pandas as pd

from src.event import MarketEvent

class HistoricalCSV(object):

    def __init__(self, csv_dir, symbol_list, date_from='', date_to='', filetype='ohlc', interval=''):

        # To keep track how long loading everything took
        start_load_datetime = datetime.now()

        self.symbol_list = symbol_list
        self.symbol_data = {}

        for s in symbol_list:
            self.symbol_data[s] = {}
            df = self._load_csv(csv_dir, s, date_from, date_to, filetype, interval)
            self.symbol_data[s]['_bars'] = df.iterrows()
            self.symbol_data[s]['_latest_bars'] = []

        # Should always remain true in live trading
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
            header=0,
            index_col=0,
            names=['datetime', 'open', 'high', 'low', 'close', 'volume']
        )

        try:
            #Tries to index with %Y-%m-%d %H:%M:%S format
            df.index = pd.to_datetime(df.index,format='%Y-%m-%d %H:%M:%S')
        except ValueError:
            #On ValueError try again with %Y-%m-%d
            df.index = pd.to_datetime(df.index,format='%Y-%m-%d')
        
        # Fills NaN with 0 in volume column
        df['volume'] = df['volume'].fillna(0)

        # Pads prices forward for NaN cells on price columns
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].ffill()

        return df

    def update_bars(self):
        for s in self.symbol_list:
            try:
                new_row = next(self.symbol_data[s]['_bars']) #df.iterows

                bar = tuple([
                    new_row[0],#.strftime("%Y-%m-%d %H:%M:%S"), #datetime
                    new_row[1][0], #open
                    new_row[1][1], #high
                    new_row[1][2], #low
                    new_row[1][3], #close
                    new_row[1][4], #volume
                ])

                self.symbol_data[s]['_latest_bars'].append(bar)
            except StopIteration:
                # TODO atm if one data file ends, backtesting will stop
                self.continue_execution = False

        return MarketEvent()

    def get_latest_bars(self, symbol, N=1):
        """
        Returns Bars object containing latest N bars from self._latest_bars
        """
        return Bars(self.symbol_data[symbol]['_latest_bars'][-N:])


class Bars(object):

    def __init__(self,latest_bars):
        if not latest_bars:
            raise ValueError

        self._latest_bars = latest_bars

        #TODO check offset so daily data doesn't have %H:%M:%S
        self.datetime = [i[0].strftime("%Y-%m-%d %H:%M:%S") for i in self.latest_bars]

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

    # def datetime(self):
    #     #TODO check offset so daily data doesn't have %H:%M:%S
    #     return [i[0].strftime("%Y-%m-%d %H:%M:%S") for i in self._latest_bars]       

    # def open(self):
    #     return [i[1] for i in self._latest_bars]

    # def high(self):
    #     return [i[2] for i in self._latest_bars]

    # def low(self):
    #     return [i[3] for i in self._latest_bars]

    # def close(self):
    #     return [i[4] for i in self._latest_bars]

    # def vol(self):
    #     return [i[5] for i in self._latest_bars]

    def get_all_prices(self):
        return self.open, self.high, self.low, self.close

    def get_all(self):
        return self.datetime, self.open, self.high, self.low, self.close, self.vol
