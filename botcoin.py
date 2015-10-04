#!/usr/bin/env python
import datetime
import logging
import sys

import numpy as np

import settings
from src.data import yahoo_api
from src.backtest import Backtest
from src.strategy import Strategy, RandomBuyStrategy, MACrossStrategy, BollingerBandStrategy, DonchianStrategy, BasicMeanRevertingStrategy, WeeklyMeanRevertingStrategy
from src.portfolio import Portfolio

def main():
    
    settings.SYMBOL_LIST = settings.ASX_50
    settings.DATE_FROM = datetime.datetime.strptime("2015-07", '%Y-%m')
    settings.DATE_TO = datetime.datetime.strptime("2016", '%Y')
    # settings.DATE_TO = datetime.datetime.now()  - datetime.timedelta(weeks=52)
    # settings.DATE_FROM = datetime.datetime.now()  - datetime.timedelta(weeks=52)
    # settings.DATE_TO = datetime.datetime.now()


    strategy_parameters = set()
    for i in np.arange(0.005,0.1,0.005):
        for j in np.arange(0.005,0.1,0.005):
            strategy_parameters.add((i,j))
    strategy_parameters = list(strategy_parameters)
    strategies = [BasicMeanRevertingStrategy(5,1,i[0],i[1]) for i in strategy_parameters]

    strategies = [BasicMeanRevertingStrategy(5,1)]

    pairs = [{'portfolio':Portfolio(max_long_pos=strategy.args[1], position_size=1/strategy.args[1]), 'strategy':strategy} for strategy in strategies]

    backtest = Backtest(pairs)

    print(backtest.results)

    print(backtest.portfolios[0].performance['all_trades'])

    backtest.plot_results()

if __name__ == '__main__':
    try:
        sys.path.append(settings.BASE_DIR)
        main()
    except KeyboardInterrupt as e:
        import logging
        logging.critical('Execution interrupted')
