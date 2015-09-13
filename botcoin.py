#!/usr/bin/env python
import datetime

from src.data import HistoricalCSV, yahoo_api
from src.settings import (
    DATA_DIR,
    DATE_FROM,
    DATE_TO,
)
import src.settings
from src.engine import BacktestManager
from src.strategy import RandomBuyStrategy, MACrossStrategy, BBStrategy, DonchianStrategy
from src.portfolio import Portfolio

def main():
    SYMBOL_LIST = src.settings.ASX_50
    DATE_FROM = datetime.datetime.strptime("2005", '%Y')
    DATE_TO = datetime.datetime.now() - datetime.timedelta(weeks=52)
    # DATE_FROM = datetime.datetime.now() - datetime.timedelta(weeks=52)
    # DATE_TO= datetime.datetime.now()


    strategy_parameters = set()
    for i in range(0,150,5):
        for j in range(1,5,1):
            strategy_parameters.add((i,j))
    strategy_parameters = list(strategy_parameters)
    strategies = [BBStrategy(params) for params in strategy_parameters]
    
    # strategies = [BBStrategy([30, 2])]

    pairs = [{'strategy':strategy,'portfolio':Portfolio(max_long_pos=5)} for strategy in strategies]

    market = HistoricalCSV(DATA_DIR, SYMBOL_LIST, date_from=DATE_FROM, date_to=DATE_TO)

    backtest = BacktestManager(
        market,
        pairs,
    )

    backtest.start()

    backtest.calc_performance()

    print(backtest.results)

    backtest.plot_results()

    return backtest

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        import logging
        logging.critical('Execution interrupted')
