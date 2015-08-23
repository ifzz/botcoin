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
from src.engine import BacktestManager
from src.strategy import RandomBuyStrategy, MACrossStrategy

def main():
    SYMBOL_LIST = ['btceUSD_5Min']
    # DATE_FROM = datetime.datetime.strptime("2011-08-14", '%Y-%m-%d')
    # DATE_TO= datetime.datetime.strptime("2011-09-01", '%Y-%m-%d')
    # pd.set_option('display.max_rows', 50)
    
    market = HistoricalCSV(DATA_DIR, SYMBOL_LIST, date_from=DATE_FROM, date_to=DATE_TO)

    # for m in market.symbol_list:
    #     print(market.symbol_data[m]['df'])

    strategy_parameters = set()
    for i in range(0,50,1):
        for j in range(0,50,1):
            strategy_parameters.add((i,j))
    strategy_parameters = list(strategy_parameters)
    strategies = [MACrossStrategy(params) for params in strategy_parameters]
    

    backtest = BacktestManager(
        market,
        [MACrossStrategy([50,5])],
    )

    logging.debug('Starting backtest from ' + DATE_FROM.strftime('%Y-%m-%d') + ' to ' + DATE_TO.strftime('%Y-%m-%d'))
    logging.debug('with ' + str(len(backtest.strategies)) + ' combinations of parameters')

    backtest.start()
    
    logging.debug("Backtest took " + str(backtest.backtest_time))

    backtest.calc_performance()

    logging.debug("Performance calculated in " + str(backtest.perf_time))
    
    logging.debug("Done")

    print(backtest.results)
    # print(backtest.engines[0].performance.equity_curve)

    return backtest

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        logging.critical('Execution interrupted')
