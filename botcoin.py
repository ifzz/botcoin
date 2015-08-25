#!/usr/bin/env python
import datetime
import logging

import matplotlib.pyplot as plt
import pandas as pd

from src.data import HistoricalCSV
from src.settings import (
    DATA_DIR,
    DATE_FROM,
    DATE_TO,
)
import src.settings
from src.engine import BacktestManager
from src.strategy import RandomBuyStrategy, MACrossStrategy, BBStrategy, DonchianStrategy

def main():
    SYMBOL_LIST = ['krakenEUR_1h']
    # DATE_FROM = datetime.datetime.strptime("2011-08-14", '%Y-%m-%d')
    # DATE_TO= datetime.datetime.strptime("2011-09-01", '%Y-%m-%d')
    # pd.set_option('display.max_rows', 50)

    market = HistoricalCSV(DATA_DIR, SYMBOL_LIST, date_from=DATE_FROM, date_to=DATE_TO)

    # for m in market.symbol_list:
    #     print(market.symbol_data[m]['df'])

    strategy_parameters = set()
    for i in range(150,300,10):
        for j in range(10,50,5):
            strategy_parameters.add((i,j))
    strategy_parameters = list(strategy_parameters)
    strategies = [DonchianStrategy(params) for params in strategy_parameters]
    

    backtest = BacktestManager(
        market,
        strategies,
        # [MACrossStrategy([5,2])],
    )

    logging.debug('Backtest {} from {} to {}'.format(SYMBOL_LIST, DATE_FROM.strftime('%Y-%m-%d'), DATE_TO.strftime('%Y-%m-%d')))
    logging.debug('with {} different strategy'.format(str(len(backtest.strategies))))

    backtest.start()
    
    logging.debug("Backtest took " + str(backtest.backtest_time))

    backtest.calc_performance()

    logging.debug("Performance calculated in " + str(backtest.perf_time))
    
    logging.debug("Done")

    print(backtest.results)
    # print(backtest.engines[0].performance.equity_curve)

    for engine in backtest.engines:
        engine.performance.equity_curve.total.plot()
        plt.show()

    return backtest

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        logging.critical('Execution interrupted')
