from backtester.events import SignalEvent

class SectorMomentumStrategy:
    def __init__(self, events_queue, lookback=60, top_k=2):
        self.events_queue = events_queue
        self.lookback = lookback
        self.top_k = top_k
        self.price_history = {} 
        self.current_longs = []
        self.current_shorts = []
        self.days_passed = 0

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            self.days_passed += 1
            
            for ticker, price in event.data.items():
                if ticker not in self.price_history:
                    self.price_history[ticker] = []
                self.price_history[ticker].append(price)
                if len(self.price_history[ticker]) > self.lookback:
                    self.price_history[ticker].pop(0)

            if self.days_passed % 20 == 0:
                returns = {}
                for ticker, prices in self.price_history.items():
                    if len(prices) == self.lookback:
                        ret = (prices[-1] / prices[0]) - 1
                        returns[ticker] = ret
                
                if not returns: return

                sorted_returns = sorted(returns.items(), key=lambda x: x[1], reverse=True)
                top_assets = [x[0] for x in sorted_returns[:self.top_k]]
                bottom_assets = [x[0] for x in sorted_returns[-self.top_k:]]

                for ticker in self.current_longs:
                    if ticker not in top_assets:
                        self.events_queue.put(SignalEvent(event.date, ticker, 'EXIT'))
                for ticker in self.current_shorts:
                    if ticker not in bottom_assets:
                        self.events_queue.put(SignalEvent(event.date, ticker, 'EXIT'))

                for ticker in top_assets:
                    if ticker not in self.current_longs:
                        self.events_queue.put(SignalEvent(event.date, ticker, 'LONG'))
                for ticker in bottom_assets:
                    if ticker not in self.current_shorts:
                        self.events_queue.put(SignalEvent(event.date, ticker, 'SHORT'))

                self.current_longs = top_assets
                self.current_shorts = bottom_assets