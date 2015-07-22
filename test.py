#!/usr/bin/env python
import unittest
import os
from src.data import HistoricalCSV

class HistoricalOhlcDataTestCase(unittest.TestCase):
    """Tests for data.py with ohlc historical data."""
    
    @classmethod
    def setUpClass(cls):
        cls.data = HistoricalCSV(
            os.path.dirname(os.path.realpath(__file__)) + '/data/',
            'btceUSD_1h.csv',
            'ohlc',
        )
        #Get a few bars just in case
        for _ in range(0,1000):
            cls.data.update_bars()

    def test_csv_file_load(self):
        """Can an example csv file from btce be loaded? File must exist."""
        self.assertTrue(self.data)

    def test_update_bars(self):
        self.data.update_bars()
        self.assertTrue(self.data.bars(1))
        self.assertTrue(self.data.bars(100))

    def test_latest_bars_integrity(self):
        """
        Can the application screw the order when retrieving latest_bars?
        Obviously will fail if the data is wrong.
        """
        while self.data.continue_execution:
            self.data.update_bars()
        bars = self.data.bars(100)
        openp, highp, lowp, closep = bars.get_all_prices()
        for i in range(0,(len(bars)-1)):
            #High price must be >= all other prices
            self.assertTrue(highp >= lowp)
            self.assertTrue(highp >= openp)
            self.assertTrue(highp >= closep)
            #Low price must be <= all other prices
            self.assertTrue(lowp <= openp)
            self.assertTrue(lowp <= closep)
    
    def test_datetime_is_str(self):
        """Just to make sure datetime is always a string in latest bars"""
        datetimes = self.data.bars(100).datetime()
        for i in range(0,len(datetimes)-1):
            self.assertTrue(type(datetimes[i]) is str)


class HistoricalTickDataTestCase(HistoricalOhlcDataTestCase):
    """Tests for data.py with tick historical data."""

    def setUp(self):
        self.data = HistoricalCSV(
            os.path.dirname(os.path.realpath(__file__)) + '/data/',
            'btcmarketsAUD.csv',
            'tick',
        )
        #Get a few bars
        for _ in range(0,1000):
            self.data.update_bars()

if __name__ == '__main__':
    unittest.main()