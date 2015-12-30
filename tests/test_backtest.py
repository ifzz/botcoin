import os
import unittest

import botcoin

class TestBacktestResults(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        datadir = os.path.join(os.getcwd(),'tests/data/')
        d = 'tests/test-strategies/'

        cls.backtest_1 = botcoin.BacktestEngine(botcoin.utils._find_strategies(d+'1.py'), datadir)
        cls.backtest_2 = botcoin.BacktestEngine(botcoin.utils._find_strategies(d+'2.py'), datadir)
        cls.backtest_3 = botcoin.BacktestEngine(botcoin.utils._find_strategies(d+'3.py'), datadir)
        cls.backtest_4 = botcoin.BacktestEngine(botcoin.utils._find_strategies(d+'4.py'), datadir)


    def test_backtest_1(self):
        p = self.backtest_1.portfolios[0].performance

        self.assertEqual(p['total_return'], 165.41281507199974)
        self.assertEqual(p['ann_return'], 33.1590505537513)
        self.assertEqual(p['sharpe'], 1.114249900076798)
        self.assertEqual(p['trades'], 316)
        self.assertEqual(p['pct_trades_profit'], 0.7025316455696202)
        self.assertFalse(p['dangerous'])
        self.assertEqual(p['dd_max'], 19.76260149365303)


    def test_backtest_2(self):
        self.assertEqual(len(self.backtest_2.portfolios),2)

        p1 = self.backtest_2.portfolios[0].performance
        p2 = self.backtest_2.portfolios[1].performance

        self.assertEqual(p1['total_return'], -61.691336000000121)
        self.assertEqual(p1['ann_return'], -12.366793517552164)
        self.assertEqual(p1['sharpe'], -0.74219880452314713)
        self.assertEqual(p1['trades'], 164)
        self.assertEqual(p1['pct_trades_profit'], 0.6463414634146342)
        self.assertTrue(p1['dangerous'])
        self.assertEqual(p1['dd_max'], 73.467987804878121)

        self.assertEqual(p2['total_return'], -82.619999999999976)
        self.assertEqual(p2['ann_return'], -16.562203814489568)
        self.assertEqual(p2['sharpe'], -0.99062060442123556)
        self.assertEqual(p2['trades'], 309)
        self.assertEqual(p2['pct_trades_profit'], 0.6084142394822006)
        self.assertTrue(p2['dangerous'])
        self.assertEqual(p2['dd_max'], 86.142869423192607)


    def test_backtest_3(self):
        p = self.backtest_3.portfolios[0].performance

        self.assertEqual(p['total_return'], 12.468103535999919)
        self.assertEqual(p['ann_return'], 2.4993860075452528)
        self.assertEqual(p['sharpe'], 0.28952996326910801)
        self.assertEqual(p['trades'], 43)
        self.assertEqual(p['pct_trades_profit'], 0.46511627906976744)
        self.assertTrue(p['dangerous'])
        self.assertEqual(p['dd_max'], 17.826826601244857)

    def test_backtest_4(self):
        p = self.backtest_4.portfolios[0].performance

        self.assertEqual(p['total_return'], -10.676699999999961)
        self.assertEqual(p['ann_return'], -5.3936163205393992)
        self.assertEqual(p['sharpe'], -0.39370223309104263)
        self.assertEqual(p['trades'], 146)
        self.assertEqual(p['pct_trades_profit'], 0.3356164383561644)
        self.assertTrue(p['dangerous'])
        self.assertEqual(p['dd_max'], 20.876631733774555)
