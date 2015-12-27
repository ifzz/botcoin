import os
import unittest

import botcoin


class TestBacktestResults(unittest.TestCase):
    SETUP_DONE = False

    @classmethod
    def setUpClass(cls):
        datadir = os.path.join(os.getcwd(),'tests/data/')
        d = 'tests/strategies/'

        cls.backtest_1 = botcoin.BacktestEngine(botcoin.utils._find_strategies(d+'1.py'), datadir, False)
        cls.backtest_2 = botcoin.BacktestEngine(botcoin.utils._find_strategies(d+'2.py'), datadir, False)
        cls.backtest_3 = botcoin.BacktestEngine(botcoin.utils._find_strategies(d+'3.py'), datadir, False)

        # backtest = botcoin.BacktestEngine(botcoin.utils._find_strategies(f), args.data_dir)

    def test_backtest_1(self):
        self.backtest_1.start()

    def test_backtest_2(self):
        self.backtest_2.start()

    def test_backtest_3(self):
        self.backtest_3.start()
