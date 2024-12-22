from btc_trader.data.data_loader import DataLoader
from btc_trader.strategies.simple_ma_strategy import SimpleMAStrategy
from btc_trader.strategies.rsi_strategy import RSIStrategy
from btc_trader.strategies.macd_strategy import MACDStrategy
from btc_trader.strategies.combined_strategy import CombinedStrategy
from btc_trader.visualization.visualizer import Visualizer
from btc_trader.utils.indicators import add_indicators, calculate_pivots
import pandas as pd

def print_strategy_results(name, results):
    """Print strategy backtest results in a formatted way"""
    print(f"\n{name} Strategy Results:")
    print("=" * 50)
    print(f"Total Return: {results['total_return']:.2%}")
    print(f"Annual Return: {results['annual_return']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Sortino Ratio: {results['sortino_ratio']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2%}")
    print(f"Win Rate: {results['win_rate']:.2%}")
    print(f"Profit Factor: {results['profit_factor']:.2f}")
    print(f"Number of Trades: {results['trade_count']}")
    print(f"Total Commission Paid: ${results['commission_paid']:.2f}")
    print("-" * 50)

def main():
    # Initialize data loader and fetch data
    loader = DataLoader("BTC-USD")
    data = loader.fetch_data(period_days=30, interval='1h')
    
    # Add technical indicators
    indicators = {
        'SMA': [20, 50],
        'EMA': [20],
        'RSI': [14],
        'MACD': None,
        'BBANDS': None,
        'STOCH': [14],
        'ADX': [14],
        'ATR': [14],
        'VWAP': None,
        'OBV': None,
        'SUPPORT_RESISTANCE': [20],
        'VOLATILITY': [14],
        'MOMENTUM': [14],
        'ICHIMOKU': None,
        'PATTERNS': None
    }
    
    data_with_indicators = add_indicators(data, indicators)
    
    # Add pivot points
    data_with_indicators = calculate_pivots(data_with_indicators, method='fibonacci')
    
    # Initialize strategies
    strategies = {
        'Simple MA': SimpleMAStrategy(data_with_indicators, short_window=20, long_window=50),
        'RSI': RSIStrategy(data_with_indicators, rsi_period=14),
        'MACD': MACDStrategy(data_with_indicators, volume_filter=True),
        'Combined': CombinedStrategy(data_with_indicators)
    }
    
    # Backtest all strategies
    results = {}
    for name, strategy in strategies.items():
        results[name] = strategy.backtest(
            initial_capital=10000.0,
            stop_loss=0.02,
            take_profit=0.05,
            position_size=0.8,
            commission=0.001
        )
        print_strategy_results(name, results[name])
    
    # Find best performing strategy
    best_strategy = max(results.items(), key=lambda x: x[1]['total_return'])
    print(f"\nBest Performing Strategy: {best_strategy[0]}")
    
    # Create visualizations
    visualizer = Visualizer(data_with_indicators)
    
    # Create individual strategy charts
    visualizer.create_interactive_chart('btc_analysis.html')
    visualizer.create_static_chart('btc_analysis.png')
    
    # Create strategy comparison visualizations
    visualizer.create_strategy_comparison(results, 'strategy_comparison.html')
    visualizer.create_strategy_metrics_comparison(results, 'strategy_metrics.html')
    
    print("\nVisualization files have been created:")
    print("1. btc_analysis.html - Technical analysis chart")
    print("2. btc_analysis.png - Static technical analysis chart")
    print("3. strategy_comparison.html - Strategy performance comparison")
    print("4. strategy_metrics.html - Strategy metrics comparison")
    
    # Print recent trades from best strategy
    print("\nRecent Trades from Best Strategy:")
    print("-" * 50)
    trades_df = pd.DataFrame(best_strategy[1]['trades'])
    if not trades_df.empty:
        trades_df['return'] = trades_df['return'].fillna(0)
        trades_df['return'] = trades_df['return'].map('{:.2%}'.format)
        print(trades_df.tail().to_string())

if __name__ == "__main__":
    main() 