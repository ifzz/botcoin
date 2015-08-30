import datetime

from .event import FillEvent
from .settings import COMMISSION_FIXED, COMMISSION_PCT

class Execution(object):
    pass

class BacktestExecution(Execution):
    def __init__(self, events_queue):
        self.events_queue = events_queue

    def execute_order(self, order):
        if order.type == 'ORDER':

            direction = -1 if order.direction in ('SELL','SHORT') else 1

            quantity = order.quantity * direction
            cost = order.quantity * order.limit_price * direction
            commission = (COMMISSION_PCT * order.limit_price * order.quantity) + COMMISSION_FIXED

            fill_event = FillEvent(
                datetime.datetime.utcnow(),
                order,
                quantity,
                cost,
                commission,
            )

            self.events_queue.put(fill_event)