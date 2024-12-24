"""Strategy registry for managing and creating trading strategies"""
from typing import Dict, Type, Any, Optional, Set
from .strategy_interface import StrategyInterface
import logging
from functools import lru_cache
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class StrategyRegistry:
    """Registry for managing trading strategies
    
    This class provides a central registry for:
    - Strategy registration
    - Strategy validation
    - Strategy creation from config
    - Strategy parameter validation
    - Strategy persistence and loading
    """
    
    _strategies: Dict[str, Type[StrategyInterface]] = {}
    _parameter_cache: Dict[str, Dict[str, Any]] = {}
    _registered_strategies: Set[str] = set()
    
    @classmethod
    def register(cls, strategy_class: Type[StrategyInterface]) -> None:
        """Register a new strategy class"""
        strategy_name = strategy_class.__name__
        if strategy_name in cls._strategies:
            logger.warning(f"Strategy {strategy_name} already registered, overwriting")
        cls._strategies[strategy_name] = strategy_class
        cls._registered_strategies.add(strategy_name)
        logger.info(f"Registered strategy: {strategy_name}")
    
    @classmethod
    def get_strategy(cls, name: str) -> Optional[Type[StrategyInterface]]:
        """Get strategy class by name"""
        if name not in cls._strategies and name in cls._registered_strategies:
            logger.warning(f"Strategy {name} was registered but is not loaded. Attempting to reload.")
            cls._reload_strategy(name)
        return cls._strategies.get(name)
    
    @classmethod
    def list_strategies(cls) -> Dict[str, Dict[str, Any]]:
        """List all registered strategies with their parameters"""
        result = {}
        for name, strategy in cls._strategies.items():
            if name not in cls._parameter_cache:
                cls._parameter_cache[name] = {
                    'description': strategy.__doc__,
                    'parameters': strategy.get_parameters() if hasattr(strategy, 'get_parameters') else {},
                    'type': 'ML' if hasattr(strategy, 'model') else 'Traditional'
                }
            result[name] = cls._parameter_cache[name]
        return result
    
    @classmethod
    @lru_cache(maxsize=32)
    def validate_parameters(cls, strategy_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize strategy parameters"""
        strategy_class = cls.get_strategy(strategy_name)
        if not strategy_class:
            raise ValueError(f"Strategy {strategy_name} not found")
            
        if not hasattr(strategy_class, 'get_parameters'):
            return parameters
            
        param_specs = strategy_class.get_parameters()
        validated = {}
        
        try:
            for name, spec in param_specs.items():
                if name not in parameters:
                    if 'default' in spec:
                        validated[name] = spec['default']
                        continue
                    raise ValueError(f"Missing required parameter: {name}")
                
                value = parameters[name]
                param_type = spec['type']
                
                # Type conversion
                try:
                    if param_type == 'int':
                        value = int(value)
                    elif param_type == 'float':
                        value = float(value)
                    elif param_type == 'bool':
                        value = bool(value)
                    elif param_type == 'str':
                        value = str(value)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid type for parameter {name}: {str(e)}")
                
                # Range validation
                if 'min' in spec and value < spec['min']:
                    raise ValueError(f"Parameter {name} below minimum: {value} < {spec['min']}")
                if 'max' in spec and value > spec['max']:
                    raise ValueError(f"Parameter {name} above maximum: {value} > {spec['max']}")
                
                validated[name] = value
            
            return validated
        except Exception as e:
            logger.error(f"Error validating parameters for {strategy_name}: {str(e)}")
            raise
    
    @classmethod
    def create_strategy(cls, name: str, data: Any, parameters: Dict[str, Any]) -> StrategyInterface:
        """Create a strategy instance from name and parameters"""
        strategy_class = cls.get_strategy(name)
        if not strategy_class:
            raise ValueError(f"Strategy {name} not found")
            
        try:
            validated_params = cls.validate_parameters(name, parameters)
            return strategy_class(data=data, **validated_params)
        except Exception as e:
            logger.error(f"Error creating strategy {name}: {str(e)}")
            raise
    
    @classmethod
    def get_strategy_info(cls, name: str) -> Dict[str, Any]:
        """Get detailed information about a strategy"""
        strategy_class = cls.get_strategy(name)
        if not strategy_class:
            raise ValueError(f"Strategy {name} not found")
            
        if name not in cls._parameter_cache:
            cls._parameter_cache[name] = {
                'name': name,
                'description': strategy_class.__doc__,
                'parameters': strategy_class.get_parameters() if hasattr(strategy_class, 'get_parameters') else {},
                'type': 'ML' if hasattr(strategy_class, 'model') else 'Traditional',
                'required_data': strategy_class.get_required_data_columns() if hasattr(strategy_class, 'get_required_data_columns') else []
            }
        
        return cls._parameter_cache[name]
    
    @classmethod
    def save_strategy_state(cls, strategy: StrategyInterface, path: str) -> None:
        """Save strategy state to disk"""
        try:
            state = strategy.get_strategy_state()
            with open(path, 'w') as f:
                json.dump(state, f)
            logger.info(f"Saved strategy state to {path}")
        except Exception as e:
            logger.error(f"Error saving strategy state: {str(e)}")
            raise
    
    @classmethod
    def load_strategy_state(cls, strategy: StrategyInterface, path: str) -> None:
        """Load strategy state from disk"""
        try:
            with open(path, 'r') as f:
                state = json.load(f)
            strategy.set_strategy_state(state)
            logger.info(f"Loaded strategy state from {path}")
        except Exception as e:
            logger.error(f"Error loading strategy state: {str(e)}")
            raise
    
    @classmethod
    def _reload_strategy(cls, name: str) -> None:
        """Attempt to reload a registered strategy"""
        try:
            # This would need to be implemented based on your module structure
            pass
        except Exception as e:
            logger.error(f"Error reloading strategy {name}: {str(e)}")
    
    @classmethod
    def clear_caches(cls) -> None:
        """Clear all internal caches"""
        cls._parameter_cache.clear()
        cls.validate_parameters.cache_clear()
        logger.info("Cleared all strategy registry caches") 