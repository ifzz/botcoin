#!/usr/bin/env python
import datetime
import logging
from os.path import dirname
import sys

import settings
from src.engine import BacktestManager
from src.strategy import RandomBuyStrategy, MACrossStrategy, BBStrategy, DonchianStrategy, MeanRevertingWeeklyStrategy
from src.portfolio import Portfolio

def main():
    
    settings.SYMBOL_LIST = settings.ASX_50
    settings.DATE_FROM = datetime.datetime.strptime("2005", '%Y')
    settings.DATE_TO = datetime.datetime.now() - datetime.timedelta(weeks=52)

    # strv ategy_parameters = set()
    # for i in range(10,250,10):
    #     for j in range(5,100,5):
    #         strategy_parameters.add((i,j))
    # strategy_parameters = list(strategy_parameters)
    # strategies = [DonchianStrategy(params) for params in strategy_parameters]
    
    strategies = [DonchianStrategy([90,1])]

    pairs = [{'portfolio':Portfolio(max_long_pos=5), 'strategy':strategy} for strategy in strategies]

    backtest = BacktestManager(pairs)

    print(backtest.results)

    print(backtest.engines[0].performance['all_trades'])

    backtest.plot_results()

    return backtest

if __name__ == '__main__':
    try:
        sys.path.append(dirname(__file__))
        main()
    except KeyboardInterrupt as e:
        import logging
        logging.critical('Execution interrupted')
