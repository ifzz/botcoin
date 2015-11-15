from . event import FillEvent
from . import settings

class Execution(object):
    pass

class BacktestExecution(Execution):
    def __init__(self):
        pass

    def execute_order(self, order):
        cost = order.quantity * order.limit_price
        commission = (settings.COMMISSION_PCT * order.limit_price * abs(order.quantity)) + settings.COMMISSION_FIXED

        fill_event = FillEvent(
            order,
            order.direction,
            order.quantity,
            cost,
            order.limit_price,
            commission,
            order.created_at, #needs to be market.datetime
        )

        self.events_queue.put(fill_event)
