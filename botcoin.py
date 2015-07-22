#!/usr/bin/env python
import logging
import pandas as pd

from src.data import HistoricalCSV
from src.settings import (
    DATA_DIR,
    SYMBOL_LIST,
    DATE_FROM,
    DATE_TO,
)
from src.trade import BacktestManager

def main():
    SYMBOL_LIST = ['btceUSD_1d','btceUSD_4h']
    pd.set_option('display.max_rows', 50)
    
    market = HistoricalCSV(DATA_DIR, SYMBOL_LIST, date_from=DATE_FROM, date_to=DATE_TO)


    for d in market.symbol_data:
        print(market.symbol_data[d]['df'])

    strategy_parameters = [[10,1]]

    backtest = BacktestManager(
        market,
        strategy_parameters,
    )

    backtest.start()
    
    print( backtest.performance() )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        logging.critical('Execution interrupted')
