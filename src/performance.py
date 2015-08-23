import numpy as np
import pandas as pd


class Performance(object):
    """
    Calculates multiple performance stats given a portfolio object.
    """
    def __init__(self, portfolio):
        if not portfolio.all_holdings:
            raise ValueError("Portfolio with empty holdings")
        curve = pd.DataFrame(portfolio.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve
        
        self.total_return = ((self.equity_curve['equity_curve'][-1] - 1.0) * 100.0)