#!/usr/bin/env python
import datetime
import logging

import pandas as pd

from src.data import HistoricalCSV, yahoo_api
from src.settings import (
    DATA_DIR,
    DATE_FROM,
    DATE_TO,
)
import src.settings
from src.engine import BacktestManager
from src.strategy import RandomBuyStrategy, MACrossStrategy, BBStrategy, DonchianStrategy

def main():
    SYMBOL_LIST = src.settings.ASX_50
    DATE_FROM = datetime.datetime.strptime("2010", '%Y')
    DATE_TO = datetime.datetime.now() - datetime.timedelta(weeks=52)
    # DATE_FROM = datetime.datetime.now() - datetime.timedelta(weeks=52)
    # DATE_TO= datetime.datetime.now()


    # for m in market.symbol_list:
    #     print(market.symbol_data[m]['df'])

    strategy_parameters = set()
    for i in range(0,100,5):
        for j in range(1,6,1):
            strategy_parameters.add((i,j))
    strategy_parameters = list(strategy_parameters)
    strategies = [BBStrategy(params) for params in strategy_parameters]
    
    market = HistoricalCSV(DATA_DIR, SYMBOL_LIST, date_from=DATE_FROM, date_to=DATE_TO)

    backtest = BacktestManager(
        market,
        # strategies,
        [BBStrategy([30,3])],
    )

    logging.debug('Backtest {} from {} to {}'.format(SYMBOL_LIST, DATE_FROM.strftime('%Y-%m-%d'), DATE_TO.strftime('%Y-%m-%d')))
    logging.debug('with {} different strategy'.format(str(len(backtest.strategies))))

    backtest.start()
    
    logging.debug("Backtest took " + str(backtest.backtest_time))

    backtest.calc_performance()

    logging.debug("Performance calculated in " + str(backtest.perf_time))
    
    logging.debug("Done")

    print(backtest.results)

    backtest.plot_results()

    return backtest

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        logging.critical('Execution interrupted')
