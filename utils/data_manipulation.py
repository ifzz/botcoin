#!/usr/bin/env python
import pandas as pd
import os

def read_tick_csv(filename):
    """
    Reads csv with tick data and returns dataframe.
    Assumes no header column, and format "timestamp,price,volume"
    """
    df = pd.io.parsers.read_csv(
        os.path.expanduser(filename),
        header=0, 
        index_col=0, 
        names=['timestamp', 'price', 'volume']
    )
    df.index = pd.to_datetime((df.index.values*1e9).astype(int))
    return df

def convert_tick_to_ohlc(df, period='1d'):
    """
    Converts a tick dataframe to ohlc. Returns a dataframe with ohlc data.
    Possible periods are s, Min, h, d, w, m
    """
    df = pd.concat(
        [
            df['price'].resample(period, how='ohlc'),
            df['volume'].resample(period, how='sum'),
        ],
        axis=1,
    )
    return df

def limit_interval(df, from_date='2015-01-01', to_date=''):
    return df[from_date:to_date] if to_date else df[from_date:]

def write_df(df,output):
    df.to_csv(output)

def break_tick_data_into_ohlc(folder, filename, output):
    df = read_tick_csv(folder+filename)
    for period in ['1Min','5Min','15Min','30Min','1h','4h','1d']:
        new_df = convert_tick_to_ohlc(df,period)
        new_df.to_csv(folder+output+'_'+period+'.csv',header=False)

if __name__ == '__main__':
    pass
    break_tick_data_into_ohlc('/home/lteixeira/Projects/botcoin/data/','btceUSD.csv','btceUSD')
    


    