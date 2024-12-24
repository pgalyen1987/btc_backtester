import os
import json
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path (str, optional): Path to the config file. If not provided,
            looks for 'config.json' in the project root.
            
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    if config_path is None:
        # Get the project root directory (parent of btc_trader)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(project_root, 'config.json')
    
    if not os.path.exists(config_path):
        # Return default configuration if file doesn't exist
        return {
            "trading": {
                "initial_balance": 10000,
                "fee_rate": 0.001
            },
            "backtesting": {
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "timeframe": "1d"
            }
        }
    
    with open(config_path, 'r') as f:
        return json.load(f) 