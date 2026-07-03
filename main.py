import queue
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from backtester.data_handler import YFinanceDataHandler
from backtester.strategy import SectorMomentumStrategy
from backtester.portfolio import Portfolio
from backtester.execution import SimulatedExecutionHandler

if __name__ == "__main__":
    universe = ['XLK', 'XLF', 'XLV', 'XLE', 'XLY', 'XLP', 'XLU', 'XLI', 'XLB', 'XLRE']
    events = queue.Queue()
    
    # Initialize components
    data_handler = YFinanceDataHandler(events, universe, "2016-01-01", "2026-01-01")
    strategy = SectorMomentumStrategy(events, lookback=60, top_k=2)
    portfolio = Portfolio(events, initial_capital=100000.0)
    execution_handler = SimulatedExecutionHandler(portfolio)

    print("Executing event-driven backtest loop...")
    while data_handler.continue_backtest():
        data_handler.update_bars()
        while not events.empty():
            event = events.get()
            if event.type == 'MARKET':
                portfolio.update_timeindex(event)
                strategy.calculate_signals(event)
            elif event.type == 'SIGNAL':
                portfolio.update_signal(event)
            elif event.type == 'ORDER':
                execution_handler.execute_order(event, events)
            elif event.type == 'FILL':
                portfolio.update_fill(event)

    # --- PERFORMANCE TEARSHEET ---
    print("\n--- PERFORMANCE TEARSHEET ANALYSIS ---")
    
    if len(portfolio.equity_curve) == 0:
        print("CRITICAL: Backtest completed but zero market events were processed.")
        print("Please verify that your ticker symbols are valid and your date range contains data.")
    else:
        df = pd.DataFrame({'Equity': portfolio.equity_curve}, index=portfolio.dates)
        df['Returns'] = df['Equity'].pct_change().fillna(0)

        # Check if we have at least two data points to compute dates
        if len(df) < 2:
            print("Insufficient data points collected to generate a tearsheet analysis.")
        else:
            total_days = (df.index[-1] - df.index[0]).days
            cagr = (df['Equity'].iloc[-1] / df['Equity'].iloc[0]) ** (365.25 / total_days) - 1
            
            sharpe = np.sqrt(252) * (df['Returns'].mean() / df['Returns'].std()) if df['Returns'].std() != 0 else 0
            downside_returns = df['Returns'][df['Returns'] < 0]
            sortino = np.sqrt(252) * (df['Returns'].mean() / downside_returns.std()) if len(downside_returns) > 0 and downside_returns.std() != 0 else 0
            
            df['Peak'] = df['Equity'].cummax()
            df['Drawdown'] = (df['Equity'] / df['Peak']) - 1
            max_dd = df['Drawdown'].min()
            calmar = cagr / abs(max_dd) if max_dd != 0 else 0

            print(f"Final Capital:     ${df['Equity'].iloc[-1]:,.2f}")
            print(f"Annualized Return: {cagr*100:.2f}%")
            print(f"Sharpe Ratio:      {sharpe:.2f}")
            print(f"Sortino Ratio:     {sortino:.2f}")
            print(f"Max Drawdown:      {max_dd*100:.2f}%")
            print(f"Calmar Ratio:      {calmar:.2f}")


            # Plotting
            df['Year'] = df.index.year
            df['Month'] = df.index.month
            monthly_returns = df.groupby(['Year', 'Month'])['Returns'].apply(lambda x: (1 + x).prod() - 1).unstack().fillna(0) * 100
        
            fig, axes = plt.subplots(3, 1, figsize=(14, 18), gridspec_kw={'height_ratios': [2, 1, 2]})
            
            axes[0].plot(df.index, df['Equity'], color='teal', linewidth=2)
            axes[0].set_title('Portfolio Growth Performance', fontsize=14, fontweight='bold')
            axes[0].grid(True, linestyle='--', alpha=0.5)
        
            axes[1].fill_between(df.index, df['Drawdown'] * 100, 0, color='crimson', alpha=0.3)
            axes[1].plot(df.index, df['Drawdown'] * 100, color='crimson', linewidth=1)
            axes[1].set_title('Portfolio Drawdown Analysis (Underwater Chart)', fontsize=14, fontweight='bold')
            axes[1].set_ylim(max_dd * 120, 0)
            axes[1].grid(True, linestyle='--', alpha=0.5)
        
            sns.heatmap(monthly_returns, annot=True, fmt=".1f", cmap="RdYlGn", center=0, cbar=True, ax=axes[2])
            axes[2].set_title('Monthly Returns Matrix (%)', fontsize=14, fontweight='bold')
        
            plt.tight_layout()
            plt.show()