import numpy as np
import pandas as pd


class Performance(object):
    """
    Calculates multiple performance stats given a portfolio object.
    """
    def __init__(self, portfolio):
        if not portfolio.all_holdings:
            raise ValueError("Portfolio with empty holdings")

        # Creating equity curve
        curve = pd.DataFrame(portfolio.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve
        
        # Total return
        self.total_return = ((self.equity_curve['equity_curve'][-1] - 1.0) * 100.0)

        # Annualised return
        self.ann_return = self.total_return ** 1/((curve.index[-1]-curve.index[0]).days/365.2425)
