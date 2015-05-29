#!/usr/bin/env python
import pandas as pd
import os
from datetime import datetime
from event import MarketEvent


class HistoricalCSV(object):

    def __init__(self, csv_dir, filename, filetype, interval='', date_from='', date_to=''):
        
        temp_datetime = datetime.now()

        df = None
        if filetype == 'ohlc':
            df = self._load_csv_ohlc(csv_dir,filename)
        elif filetype == 'tick':
            df = self._load_csv_tick(csv_dir,filename,interval)
        else:
            raise ValueError
        
        df = df[date_from:] if date_from else df
        df = df[:date_to] if date_to else df

        self.load_time = datetime.now()-temp_datetime

        self._bars = df.iterrows()
        self._latest_bars = []
        #Will almost remain true in live trading
        self.continue_execution = True
        
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
        
        return df

    def update_bars(self):
        try:
            new_row = next(self._bars) #df.iterows
            
            bar = tuple([
                new_row[0],#.strftime("%Y-%m-%d %H:%M:%S"), #datetime
                new_row[1][0], #open
                new_row[1][1], #high
                new_row[1][2], #low
                new_row[1][3], #close
                new_row[1][4], #volume
            ])
            
            self._latest_bars.append(bar)
        except StopIteration:
            self.continue_execution = False
        return MarketEvent()

    def get_latest_bars(self, N=1):
        """
        Returns Bars object containing latest N bars from self._latest_bars
        """
        return Bars(self._latest_bars[-N:])


class Bars(object):

    def __init__(self,latest_bars):
        if latest_bars:
            self._latest_bars = latest_bars
        else:
            raise ValueError

    def __len__(self):
        return len(self._latest_bars)
        
    def datetime(self):
        #TODO check offset so daily data doesn't have %H:%M:%S
        return [i[0].strftime("%Y-%m-%d %H:%M:%S") for i in self._latest_bars]       

    def open(self):
        return [i[1] for i in self._latest_bars]

    def high(self):
        return [i[2] for i in self._latest_bars]

    def low(self):
        return [i[3] for i in self._latest_bars]

    def close(self):
        return [i[4] for i in self._latest_bars]

    def vol(self):
        return [i[5] for i in self._latest_bars]

    def get_all_prices(self):
        return self.open(), self.high(), self.low(), self.close()

    def get_all(self):
        return self.datetime(), self.open(), self.high(), self.low(), self.close(), self.vol()
