class MarketData(object):
    pass

class Bars(object):
    """Multiple Bars, usually from past data"""
    def __init__(self,latest_bars, single_bar=False):
        self.length = len(latest_bars)

        if single_bar:
            self.datetime = latest_bars[-1][0]
            self.open = latest_bars[-1][1]
            self.high = latest_bars[-1][2]
            self.low = latest_bars[-1][3]
            self.close = latest_bars[-1][4]
            self.vol = latest_bars[-1][5]
        else:
            self.datetime = [i[0] for i in latest_bars]
            self.open = [i[1] for i in latest_bars]
            self.high = [i[2] for i in latest_bars]
            self.low = [i[3] for i in latest_bars]
            self.close = [i[4] for i in latest_bars]
            self.vol = [i[5] for i in latest_bars]

    def mavg(self, price_type='close'):
        return np.round(
            np.mean(getattr(self, price_type)),
            settings.ROUND_DECIMALS
        )

    def bollingerbands(self, k, price_type='close'):
        ave = np.mean(getattr(self, price_type))
        sd = np.std(getattr(self, price_type))
        upband = ave + (sd*k)
        lwband = ave - (sd*k)
        round_dec = settings.ROUND_DECIMALS
        return np.round(ave,round_dec), np.round(upband,round_dec), np.round(lwband,round_dec)

    def __len__(self):
        return self.length
