#!/usr/bin/env python
import pandas as pd
import os

class HistoricalCSV(object):

    def __init__(self, csv_dir, filename, filetype, interval='', date_from='', date_to=''):
        
        self.latest_bars = []
        self.continue_backtest = True
        
        self.df = None
        if filetype == 'ohlc':
            self.df = self._load_csv_ohlc(csv_dir,filename)
        elif filetype == 'tick':
            self.df = self._load_csv_tick(csv_dir,filename,interval)
        else:
            raise ValueError
        
        self.df = self.df[date_from:] if date_from else self.df
        self.df = self.df[:date_to] if date_to else self.df
        self.df = self.df.iterrows()

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
        return df

    def get_latest_bars(self, N=1):
        return self.latest_bars[-N:]

    def update_bars(self):
        try:
            new_row = self.df.next() #df.iterows
            bar = tuple([
                new_row[0], #datetime
                new_row[1][0], #open
                new_row[1][1], #high
                new_row[1][2], #low
                new_row[1][3], #close
                new_row[1][4], #volume
            ])
        except StopIteration:
            self.continue_backtest = False
        else:
            self.latest_bars.append(bar)
        #self.events.put(MarketEvent())