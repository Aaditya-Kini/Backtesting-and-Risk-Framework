import yfinance as yf
from backtester.events import MarketEvent

class YFinanceDataHandler:
    def __init__(self, events_queue, tickers, start_date, end_date):
        self.events_queue = events_queue
        self.tickers = tickers
        print("Downloading market data...")
        self.data = yf.download(tickers, start=start_date, end=end_date)['Close'].dropna()
        self.dates = self.data.index.tolist()
        self.current_date_idx = 0

    def continue_backtest(self):
        return self.current_date_idx < len(self.dates)

    def update_bars(self):
        if self.continue_backtest():
            date = self.dates[self.current_date_idx]
            market_data = self.data.loc[date].to_dict()
            self.events_queue.put(MarketEvent(date, market_data))
            self.current_date_idx += 1