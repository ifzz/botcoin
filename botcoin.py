#!/usr/bin/env python
import datetime
import logging
from os.path import dirname
import sys

import settings
from src.data import yahoo_api
from src.engine import BacktestManager
from src.strategy import RandomBuyStrategy, MACrossStrategy, BBStrategy, DonchianStrategy, MeanRevertingWeeklyStrategy
from src.portfolio import Portfolio

def main():
    
    settings.SYMBOL_LIST = settings.ASX_50
    settings.DATE_FROM = datetime.datetime.strptime("2014", '%Y')
    settings.DATE_TO = datetime.datetime.strptime("2016", '%Y')
    # settings.DATE_TO = datetime.datetime.now()  - datetime.timedelta(weeks=52)
    # settings.DATE_FROM = datetime.datetime.now()  - datetime.timedelta(weeks=52)
    # settings.DATE_TO = datetime.datetime.now()


    # strategy_parameters = set()
    # for i in range(20,120,20):
    #     for j in range(5,40,5):
    #         strategy_parameters.add((i,j))
    # strategy_parameters = list(strategy_parameters)
    # strategies = [DonchianStrategy(params) for params in strategy_parameters]
    
    strategies = [MeanRevertingWeeklyStrategy([30,10])]

    pairs = [{'portfolio':Portfolio(max_long_pos=10, position_size=0.1), 'strategy':strategy} for strategy in strategies]

    backtest = BacktestManager(pairs)#,start_automatically=False)

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
