import numpy as np
import pandas as pd


def performance(portfolio):
    """
    Calculates multiple performance stats given a portfolio object.
    """

    if not portfolio.all_holdings:
        raise ValueError("Portfolio with empty holdings")
    results = {}

    curve = pd.DataFrame(portfolio.all_positions)
    curve.set_index('datetime', inplace=True) 
    results['all_positions'] = curve

    curve = pd.DataFrame(portfolio.all_holdings)
    curve.set_index('datetime', inplace=True) 
    results['all_holdings'] = curve

    # Creating equity curve
    curve['returns'] = curve['total'].pct_change()
    curve['equity_curve'] = (1.0+curve['returns']).cumprod()
    results['equity_curve'] = curve['equity_curve']

    # Number of days elapsed between first and last bar
    days = (curve.index[-1]-curve.index[0]).days
    years = days/365.2425

    # Average bars each year, used to calculate sharpe ratio (N)
    avg_bars_per_year = len(curve.index)/years # curve.groupby(curve.index.year).count())
    
    # Total return
    results['total_return'] = ((curve['equity_curve'][-1] - 1.0) * 100.0)

    # Annualised return
    results['ann_return'] = results['total_return'] ** 1/years

    # Sharpe ratio
    results['sharpe'] = np.sqrt(avg_bars_per_year) * curve['returns'].mean() / curve['returns'].std()

    # Trades statistic
    results['trades'] = len(portfolio.all_trades)
    results['trades_per_year'] = results['trades']/years
    results['pct_trades_profit'] = len([trade for trade in portfolio.all_trades if trade.result > 0])/results['trades']
    results['pct_trades_loss'] = len([trade for trade in portfolio.all_trades if trade.result <= 0])/results['trades']

    return results
