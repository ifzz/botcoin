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
    SYMBOL_LIST = ['btceUSD_1d']
    pd.set_option('display.max_rows', 50)
    
    market = HistoricalCSV(DATA_DIR, SYMBOL_LIST, date_from=DATE_FROM, date_to=DATE_TO)

    strategy_parameters = set()
    for i in range(5,30):
        for j in range(5,30):
            strategy_parameters.add((i,j))
    strategy_parameters = list(strategy_parameters)

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
