 #! /usr/bin/env python
 
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection, message
from time import sleep

# edemo
# demouser

class RealTimeMarket(object):
    def __init__(self, debug_mode=False):
        self.tws_conn = ibConnection()

        if debug_mode:
            self.tws_conn.registerAll(self.watcher)
        else:
            self.tws_conn.register(self.error_handler, 'Error')
            self.tws_conn.register(self.tick_handler, 'TickSize', 'TickPrice', 'TickString')
            self.tws_conn.register(self.next_valid_id_handler, 'NextValidId')

        self.tickers = {}

    def connect(self):
        self.tws_conn.connect()
    def disconnect(self):
        self.tws_conn.disconnect()

    def tick_handler(self, msg):
        # https://www.interactivebrokers.com/en/software/api/apiguide/tables/tick_types.htm
        # 0   BID_SIZE	tickSize()
        # 1   BID_PRICE	tickPrice()
        # 2   ASK_PRICE	tickPrice()
        # 3   ASK_SIZE	tickSize()
        # 4   LAST_PRICE	tickPrice()
        # 5   LAST_SIZE	tickSize()
        # 6   HIGH	tickPrice()
        # 7   LOW	tickPrice()
        # 8   VOLUME	tickSize()
        # 9   CLOSE_PRICE	tickPrice()
        # 14  OPEN_TICK	tickPrice()
        # 21  AVG_VOLUME	tickSize()
        # 37  MARK_PRICE	tickPrice()
        # 45  LAST_TIMESTAMP	tickString()
        # 46  SHORTABLE	tickString()

        if isinstance(msg, message.tickPrice):

            if msg.field == 4:  # LAST_PRICE
                print("{} price for {}".format(msg.price, self.tickers[msg.tickerId]))


        elif isinstance(msg, message.tickSize):

            if msg.field == 8:  # VOLUME
                print('{} volume for {}'.format(msg.size, self.tickers[msg.tickerId]))

        elif isinstance(msg, message.tickString):
            pass

        else:
            print(msg)

    def error_handler(self, error):
        print(error)

    def next_order_id_handler(self, msg):
        self.next_order_id = msg.orderId

    def watcher(self, msg):
        print(msg)

    def make_contract(self, sym, sec_type, exchange, currency):
        c = Contract()
        c.m_symbol, c.m_secType, c.m_exchange, c.m_currency = sym, sec_type, exchange, currency
        return c

    def req_market_data(self, sym, sec_type='STK', exchange='ASX', currency='AUD'):
        c = self.make_contract(sym,sec_type,exchange,currency)
        self.tws_conn.reqMktData(self.next_tick_id, c, '', snapshot=False)
        self.tickers[self.next_tick_id] = sym
        self.next_tick_id += 1

def main():
    live_market = RealTimeMarket()
    live_market.connect()
    live_market.req_market_data('CBA')
    live_market.req_market_data('ANZ')
    live_market.req_market_data('NAB')
    live_market.req_market_data('WTP')
    live_market.req_market_data('AAC')
    live_market.req_market_data('ADO')
    live_market.req_market_data('AJA')
    live_market.req_market_data('AJL')
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        live_market.disconnect()

if __name__ == '__main__':
    main()
