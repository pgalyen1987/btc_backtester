from btc_trader.strategies.combined_strategy import CombinedStrategy
from btc_trader.strategies.rsi_strategy import RSIStrategy
from btc_trader.strategies.simple_ma_strategy import SimpleMAStrategy
from btc_trader.data.data_loader import DataLoader
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, pd.Series):
        return obj.values.tolist()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def safe_convert_to_list(series):
    """Safely convert a pandas Series or array-like object to a list"""
    try:
        if isinstance(series, (pd.Series, pd.DataFrame)):
            return series.values.tolist()
        elif isinstance(series, np.ndarray):
            return series.tolist()
        elif hasattr(series, '__iter__') and not isinstance(series, str):
            return list(series)
        return [series]
    except Exception as e:
        print(f"Error converting to list: {str(e)}")
        return []

def test_strategy(strategy_class, data, strategy_name):
    """Test a single strategy and return its results"""
    print(f"\nTesting {strategy_name}...")
    
    try:
        # Initialize strategy with default parameters
        if strategy_class == SimpleMAStrategy:
            strategy = strategy_class(data, short_window=20, long_window=50)
        elif strategy_class == RSIStrategy:
            strategy = strategy_class(data, rsi_period=14, rsi_overbought=70, rsi_oversold=30)
        else:
            strategy = strategy_class(data)
        
        # Generate signals
        signals = strategy.generate_signals()
        if isinstance(signals, pd.Series):
            signals = pd.DataFrame({'signal': signals, 'signal_strength': np.abs(signals)})
            signals['close'] = data['close']
        
        # Print basic stats
        print('Data shape:', signals.shape)
        print('\nSignal counts:')
        print(signals['signal'].value_counts())
        print('\nSignal strength stats:')
        print(signals['signal_strength'].describe())
        
        # Save results for frontend testing
        results = {
            'dates': [d.isoformat() for d in signals.index],
            'prices': safe_convert_to_list(signals['close']),
            'signals': safe_convert_to_list(signals['signal']),
            'signal_strength': safe_convert_to_list(signals['signal_strength'])
        }
        
        # Add strategy-specific indicators
        if isinstance(strategy, SimpleMAStrategy):
            results.update({
                'ma_short': safe_convert_to_list(signals['ma_short']),
                'ma_long': safe_convert_to_list(signals['ma_long'])
            })
        elif isinstance(strategy, RSIStrategy):
            results.update({
                'rsi': safe_convert_to_list(signals['rsi'])
            })
        elif isinstance(strategy, CombinedStrategy):
            results.update({
                'ma_short': safe_convert_to_list(signals['ma_short']),
                'ma_long': safe_convert_to_list(signals['ma_long']),
                'rsi': safe_convert_to_list(signals['rsi']),
                'macd': safe_convert_to_list(signals['macd']),
                'macd_signal': safe_convert_to_list(signals['signal_line']),
                'macd_hist': safe_convert_to_list(signals['macd_hist'])
            })
        
        return results
        
    except Exception as e:
        print(f"Error testing {strategy_name} strategy: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_all_strategies():
    """Test all available strategies with default parameters"""
    # Load test data
    loader = DataLoader('BTC-USD')
    data = loader.load_data(period_days=365, interval='1d')
    
    # Ensure column names match strategy requirements
    data.columns = data.columns.str.lower()
    
    # Test each strategy
    strategies = [
        (SimpleMAStrategy, "SimpleMA"),
        (RSIStrategy, "RSI"),
        (CombinedStrategy, "Combined")
    ]
    
    results = {}
    for strategy_class, strategy_name in strategies:
        try:
            result = test_strategy(strategy_class, data, strategy_name)
            if result is not None:
                results[strategy_name] = result
                print(f"\n{strategy_name} strategy test completed successfully")
        except Exception as e:
            print(f"\nError testing {strategy_name} strategy: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return results

if __name__ == "__main__":
    test_all_strategies() 