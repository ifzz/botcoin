from .event import FillEvent
import settings

class Execution(object):
    pass

class BacktestExecution(Execution):
    def __init__(self, events_queue, market):
        self.events_queue = events_queue
        self.market = market

    def execute_order(self, order):
        if order.type == 'ORDER':

            direction = -1 if order.direction in ('SELL','SHORT') else 1

            quantity = order.quantity * direction
            cost = order.quantity * order.limit_price * direction
            commission = (settings.COMMISSION_PCT * order.limit_price * order.quantity) + settings.COMMISSION_FIXED

            fill_event = FillEvent(
                order,
                self.market.bars(order.symbol).this_datetime,
                quantity,
                cost,
                commission,
            )

            self.events_queue.put(fill_event)