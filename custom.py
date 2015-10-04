#!/usr/bin/env python
from botcoin import Backtest, Strategy, BollingerBandStrategy, Portfolio, settings

# Create your custom strategies and run a backtest here.

strategies = [BollingerBandStrategy(30,1)]

pairs = [{'portfolio':Portfolio(max_long_pos=strategy.args[1], position_size=1/strategy.args[1]), 'strategy':strategy} for strategy in strategies]

backtest = Backtest(pairs, symbol_list=settings.ASX_50)

print(backtest.results)

backtest.plot_results()