from botcoin.event import FillEvent
from botcoin.execution import Execution

class BacktestExecution(Execution):

    def execute_order(self, order):
        cost = order.quantity * order.limit_price
        commission = (self.commmission_pct * order.limit_price * abs(order.quantity)) + self.commission_fixed

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
