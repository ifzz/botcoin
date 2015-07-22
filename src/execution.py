import datetime

from .event import FillEvent
from .settings import COMMISSION_FIXED, COMMISSION_PCT

class Execution(object):
    pass

class BacktestExecution(Execution):
    def __init__(self, events_queue):
        self.events_queue = events_queue

    def execute_order(self, order, last_close):
        if order.type == 'ORDER':

            direction = 1
            if order.direction in ('EXIT','SHORT'):
                direction = -1

            quantity = order.quantity * direction
            cost = last_close * order.quantity * direction
            commission = (COMMISSION_PCT * last_close * order.quantity) + COMMISSION_FIXED

            fill_event = FillEvent(
                datetime.datetime.utcnow(),
                order.symbol,
                quantity,
                order.direction,
                cost,
                commission,
            )
            self.events_queue.put(fill_event)