import numpy as np

from botcoin import Backtest, Portfolio, Strategy, settings


"""
Bad strategies:
    GapDownStrategy (works on some years)
    Buy on 1/5 days average breakout (trend and reversal versions)
    BollingerBreakout

OK strategies
    VolumeBreakout (40-80,5,5)

"""
class GapDownStrategy(Strategy):
    def __init__(self, *args):
        self.args = args
        self.number_pos = args[0]
        self.pct_profit = args[1]

    def logic(self):
        list_gapped_down = []
        for s in self.symbol_list:
            today = self.market.today(s)
            yesterday = self.market.yesterday(s)
            if yesterday and today:
                if today.open < yesterday.low:
                    list_gapped_down.append((s,(today.open-yesterday.low)/yesterday.low))


        list_gapped_down = sorted(list_gapped_down, key=lambda x: x[1] )

        [self.buy(s, self.market.today(s).open, 0) for s,v in list_gapped_down[:self.number_pos]]
        for s,v in list_gapped_down[:self.number_pos]:
            exit_price = self.market.today(s).open*(1+self.pct_profit)
            if self.market.today(s).high >= exit_price:
                self.sell(s, exit_price, 1)

        [self.sell(s, self.market.today(s).close, 2) for s,v in list_gapped_down[:self.number_pos]]

class Test(Strategy):
    
    def __init__(self, *args):
        self.args = args
        self.avg_days = args[0]
        self.pct_profit = args[1]
        self.pos = args[2]
        self.symbols_to_buy_tomorrow = []

    def logic(self):
        # At market open
        if self.symbols_to_buy_tomorrow:
            if len(self.symbols_to_buy_tomorrow) > self.pos:
                raise ValueError("Something wrong")

            [self.buy(s, self.market.today(s).open) for s,v in self.symbols_to_buy_tomorrow]
            
            for s,v in self.symbols_to_buy_tomorrow:
                exit_price = self.market.today(s).open*(1+self.pct_profit)
                if self.market.today(s).high >= exit_price:
                    self.sell(s, exit_price, 1)


            [self.sell(s, self.market.today(s).close, 2) for s,v in self.symbols_to_buy_tomorrow]

        # At market end
        self.symbols_to_buy_tomorrow = []

        for s in self.symbol_list:
            bars = self.market.past_bars(s, self.avg_days)
            today = self.market.today(s)
            if len(bars) == 5:
                avg = np.round(np.mean(bars.close),2)
                if today.close > avg:
                    self.symbols_to_buy_tomorrow.append((s,today.close-avg))

        if self.symbols_to_buy_tomorrow:
            self.symbols_to_buy_tomorrow = sorted(self.symbols_to_buy_tomorrow, key=lambda x: x[1], reverse=True)[:self.pos]


class VolumeBreakout(Strategy):
    def __init__(self, *args):
        self.args = args
        self.vol_days = args[0]
        self.exit_days = args[1]
        self.pos = args[2]

    def logic(self):
        for s in self.symbol_list:
            vol_bars = self.market.past_bars(s, self.vol_days)
            price_bars = self.market.past_bars(s, self.exit_days)
            if vol_bars and price_bars:

                volume_band = max(vol_bars.vol)
                exit_band = min(price_bars.low)

                if self.market.today(s).vol > volume_band:
                    self.buy(s,self.market.today(s).close, 0)

                if self.market.today(s).low < exit_band:
                    self.sell(s,exit_band,1)

from botcoin import bbands

class BollingerBreakout(Strategy):
    def __init__(self, *args):
        self.args = args
        self.len = args[0]
        self.k = args[1]

    def logic(self):
        for s in self.symbol_list:
            bars = self.market.past_bars(s, self.len)
            if bars:
                avg, upband, lwband = bbands(bars.close,self.k)

                if self.market.today(s).high > upband:
                    self.buy(s, upband, 0)

                if self.market.today(s).low < lwband:
                    self.sell(s,avg,1)

class MA3Cross(Strategy):
    def __init__(self, *args):
        self.args = args
        self.super_fast = args[0]
        self.fast = args[1]
        self.slow = args[2]
        self.pos = args[3]

    def logic(self):
        for s in self.symbol_list:
            super_fast = np.avg(self.market.bars(s, self.super_fast).close)
            fast = np.avg(self.market.bars(s, self.fast).close)
            slow = np.avg(self.market.bars(s, self.slow).close)

            if fast > slow:
                self.buy(s, self.market.today(s).close)
            if super_fast < fast:
                self.sell(s, self.market.today(s).close)


symbol_list = settings.ASX_50
params = []
for i in np.arange(20,200,20):
    for j in np.arange(1,5,1):
        params.append((i,j))
# strategies = [VolumeBreakout(i,j,5) for i,j in params]
strategies=[BollingerBreakout(10,30,50,5)] #for i,j in params]
portfolios = [{'portfolio':Portfolio(max_long_pos=strategy.args[3], position_size=1/strategy.args[3]), 'strategy':strategy} for strategy in strategies]

import datetime

backtest = Backtest(
    portfolios,
    symbol_list,
    date_from=datetime.datetime.strptime('2010', '%Y'),
    date_to=datetime.datetime.strptime('2015', '%Y')
)

print(backtest.results)
backtest.plot_results()