from botcoin.data import MarketData, Bars
from botcoin.event import MarketEvent
from botcoin import settings

class HistoricalCSVData(MarketData):

    def __init__(self, csv_dir, symbol_list):

        super(HistoricalCSVData, self).__init__(csv_dir,symbol_list)

        for s in symbol_list:
            # Limit between date_From and date_to
            self.symbol_data[s]['df'] = self.symbol_data[s]['df'][settings.DATE_FROM:] if settings.DATE_FROM else self.symbol_data[s]['df']
            self.symbol_data[s]['df'] = self.symbol_data[s]['df'][:settings.DATE_TO] if settings.DATE_TO else self.symbol_data[s]['df']

            # Check for empty dfs
            if self.symbol_data[s]['df'].empty:
                logging.warning("Empty DataFrame loaded for {}.".format(filename)) # Possibly invalid date ranges?

            # Dataframe iterrows  generator
            self.symbol_data[s]['bars'] = self.symbol_data[s]['df'].iterrows()

            # List that will hold all rows from iterrows, one at a time
            self.symbol_data[s]['latest_bars'] = []

        self.continue_execution = True
        self.date_from = self.symbol_data[self.symbol_list[0]]['df'].index[0]
        self.date_to = self.symbol_data[self.symbol_list[0]]['df'].index[-1]

    def _update_bars(self):
        """
        Generator that updates all prices based on historical data and raises
        MarketEvents to simulate live trading. The order of events is:
            before_open - single event
            open - one event per symbol
            during - two events per symbol (low and high, depending if positive
                     negative day)
            close - one event per symbol
            after_close - single event

        Before raising MarketEvents, all prices need to be updated to maintain
        consistency otherwise portfolio_value will be calculated based on open price
        and it will influence position size calculation
        """

        try:
            for s in self.symbol_list:
                new_row = next(self.symbol_data[s]['bars']) #df.iterows

                datetime = new_row[0]
                openp = new_row[1][0]
                highp = new_row[1][1]
                lowp = new_row[1][2]
                closep = new_row[1][3]
                volume = new_row[1][4]

                if not (highp>=lowp and highp>=openp and highp>=closep and
                    lowp<=openp and lowp<=closep):
                    raise ValueError("Data inconsistency on " + s + " at " +
                        str(datetime) + ". OHLC is " + str(openp) + " " +
                        str(highp) + " " + str(lowp) + " " + str(closep) +
                        ". High price must be >= all other prices" +
                        " and low price must be <= all other prices"
                    )

                bar = tuple([
                    datetime,
                    openp,
                    highp,
                    lowp,
                    closep,
                    volume,
                ])

                self.symbol_data[s]['latest_bars'].append(bar)

            self.datetime = datetime


            # Before open
            yield MarketEvent('before_open')

            # On open - open = latest_bars[-1][1]
            for s in self.symbol_list:
                self.symbol_data[s]['current_price'] = self.symbol_data[s]['latest_bars'][-1][1]
            for s in self.symbol_list:
                yield MarketEvent('open', s)

            # During #1
            for s in self.symbol_list:
                d = self.symbol_data[s]['latest_bars'][-1]
                self.symbol_data[s]['current_price'] = d[3] if d[4]>d[1] else d[2]
            for s in self.symbol_list:
                yield MarketEvent('during', s)

            # During #2
            for s in self.symbol_list:
                d = self.symbol_data[s]['latest_bars'][-1]
                self.symbol_data[s]['current_price'] = d[2] if d[4]>d[1] else d[3]
            for s in self.symbol_list:
                yield MarketEvent('during', s)

            # On close
            for s in self.symbol_list:
                self.symbol_data[s]['current_price'] = self.symbol_data[s]['latest_bars'][-1][4]
            for s in self.symbol_list:
                yield MarketEvent('close', s)

            # After close, current_price will still be close
            yield MarketEvent('after_close')

        except StopIteration:
            self.continue_execution = False
