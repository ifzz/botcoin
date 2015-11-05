from event import FillEvent
import settings

class Execution(object):
    pass

class BacktestExecution(Execution):
    def __init__(self):
        pass

    def set_queue_and_market(self, events_queue, market):
        self.events_queue = events_queue
        self.market = market

    def execute_order(self, order):
        cost = order.quantity * order.limit_price
        commission = (settings.COMMISSION_PCT * order.limit_price * abs(order.quantity)) + settings.COMMISSION_FIXED

        fill_event = FillEvent(
            order,
            self.market.this_datetime,
            order.direction,
            order.quantity,
            cost,
            order.limit_price,
            commission,
        )

        self.events_queue.put(fill_event)
