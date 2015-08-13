#!/usr/bin/env python
import datetime
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
    SYMBOL_LIST = ['btceUSD_1h']
    # DATE_FROM = datetime.datetime.strptime("2011-08-14", '%Y-%m-%d')
    # DATE_TO= datetime.datetime.strptime("2011-09-01", '%Y-%m-%d')
    # pd.set_option('display.max_rows', 50)
    
    market = HistoricalCSV(DATA_DIR, SYMBOL_LIST, date_from=DATE_FROM, date_to=DATE_TO)

    # for m in market.symbol_list:
    #     print(market.symbol_data[m]['df'])

    strategy_parameters = set()
    for i in range(2,30,2):
        for j in range(0,30,2):
            strategy_parameters.add((i,j))
    strategy_parameters = list(strategy_parameters)

    backtest = BacktestManager(
        market,
        strategy_parameters,
    )

    logging.debug(str(len(backtest.strategy_parameters)) + ' combinations of parameters')
    logging.debug('Starting backtest at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    backtest.start()
    
    logging.debug('Calculating performance at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    backtest.calc_performance()

    print(backtest.results)

    logging.debug('Done at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    return backtest

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        logging.critical('Execution interrupted')
