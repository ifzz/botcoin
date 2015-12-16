#!/usr/bin/env python
import argparse
import logging
import os
import botcoin


def main():
    parser = argparse.ArgumentParser(description='Botcoin script execution.')
    parser.add_argument(dest='algo_file', nargs='+', help='file with strategy scripts')
    parser.add_argument('-d', '--data_dir', default=os.path.join(os.getcwd(),'data/'), required=False, nargs='?', help='data directory containing ohlc csvs (default is ./data/)')
    parser.add_argument('-g', '--graph_equity', action='store_true', help='graph equity curve')
    parser.add_argument('-s', '--graph_subscriptions', action='store_true', help='graph symbol subscriptions')
    parser.add_argument('-a', '--all_trades', action='store_true', help='print all_trades dataframe')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose (very chatty, be careful)')
    args = parser.parse_args()

    botcoin.utils._config_logging(args.verbose)

    # Run backtest
    backtest = botcoin.Backtest(botcoin.utils._find_strategies(args.algo_file[0]), args.data_dir)

    print(backtest.results)

    if args.all_trades:
        backtest.print_all_trades()

    if args.graph_equity:
        backtest.plot_results()

    if args.graph_subscriptions:
        backtest.plot_symbol_subscriptions()

    backtest.strategy_finishing_methods()

    return backtest


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Execution stopped")
