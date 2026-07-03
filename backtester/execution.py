from backtester.events import FillEvent

class SimulatedExecutionHandler:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.slippage_bps = 0.0010 
        self.commission_per_share = 0.005 

    def execute_order(self, event, events_queue):
        if event.type == 'ORDER':
            current_price = self.portfolio.current_prices.get(event.ticker, 0)
            if current_price == 0: return
            exec_price = current_price * (1 + self.slippage_bps) if event.direction == 'LONG' else current_price * (1 - self.slippage_bps)
            commission = event.quantity * self.commission_per_share
            events_queue.put(FillEvent(event.date, event.ticker, event.direction, event.quantity, exec_price, commission))