from backtester.events import OrderEvent

class Portfolio:
    def __init__(self, events_queue, initial_capital=100000.0):
        self.events_queue = events_queue
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        self.holdings = {} 
        self.current_prices = {}
        self.equity_curve = []
        self.dates = []

    def update_timeindex(self, event):
        if event.type == 'MARKET':
            self.current_prices = event.data
            portfolio_value = self.current_cash
            for ticker, qty in self.holdings.items():
                portfolio_value += qty * self.current_prices.get(ticker, 0)
            
            self.equity_curve.append(portfolio_value)
            self.dates.append(event.date)

    def update_signal(self, event):
        if event.type == 'SIGNAL':
            total_equity = self.current_cash + sum(q*self.current_prices.get(t,0) for t,q in self.holdings.items())
            target_value = total_equity * 0.15 
            price = self.current_prices.get(event.ticker, 0)
            if price == 0: return

            target_qty = int(target_value / price)
            current_qty = self.holdings.get(event.ticker, 0)

            if event.direction == 'LONG':
                order_qty = target_qty - current_qty
                if order_qty > 0: self.events_queue.put(OrderEvent(event.date, event.ticker, 'LONG', order_qty))
            elif event.direction == 'SHORT':
                order_qty = -target_qty - current_qty
                if order_qty < 0: self.events_queue.put(OrderEvent(event.date, event.ticker, 'SHORT', abs(order_qty)))
            elif event.direction == 'EXIT':
                if current_qty > 0: self.events_queue.put(OrderEvent(event.date, event.ticker, 'SHORT', current_qty))
                elif current_qty < 0: self.events_queue.put(OrderEvent(event.date, event.ticker, 'LONG', abs(current_qty)))

    def update_fill(self, event):
        if event.type == 'FILL':
            fill_cost = event.price * event.quantity
            if event.direction == 'LONG':
                self.current_cash -= (fill_cost + event.commission)
                self.holdings[event.ticker] = self.holdings.get(event.ticker, 0) + event.quantity
            elif event.direction == 'SHORT':
                self.current_cash += (fill_cost - event.commission)
                self.holdings[event.ticker] = self.holdings.get(event.ticker, 0) - event.quantity
            if self.holdings[event.ticker] == 0: del self.holdings[event.ticker]