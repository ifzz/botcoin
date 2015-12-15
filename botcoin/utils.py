import itertools
import logging
import numpy as np
import pandas as pd
import urllib.request
from urllib.request import HTTPError

# Data APIs
YAHOO_CHART_API = 'http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range={}/csv'
YAHOO_API = 'http://ichart.finance.yahoo.com/table.csv?s={}&c={}&g={}'
YAHOO_API_2 = 'http://download.finance.yahoo.com/d/quotes.csv?s={}&f=sl1d1t1c1ohgv&e=.csv'


def yahoo_api(list_of_symbols, data_dir, year_from=1900, period='d', remove_adj_close=False):

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


def optimize(*args):
    if not args:
        return
    elif len(args) == 1:
        a = args[0]
        return np.arange(a[0],a[1],a[2])
    else:
        lists_of_elements = [np.arange(a[0],a[1],a[2]) for a in args]
        return list(itertools.product(*lists_of_elements))
