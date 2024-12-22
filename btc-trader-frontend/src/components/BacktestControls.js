import React, { useState, useEffect } from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TextField,
    Button,
    Grid,
    Typography,
    Alert,
} from '@mui/material';

const BacktestControls = ({ onRunBacktest, isLoading }) => {
    const [strategies, setStrategies] = useState([]);
    const [selectedStrategy, setSelectedStrategy] = useState('');
    const [strategyParams, setStrategyParams] = useState({});
    const [parameters, setParameters] = useState({
        period_days: 365,
        interval: '1d',
        initial_capital: 10000,
        stop_loss: 0.02,
        take_profit: 0.03,
        position_size: 1.0,
        commission: 0.001,
    });
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch available strategies when component mounts
        fetchStrategies();
    }, []);

    const fetchStrategies = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/strategies');
            const data = await response.json();
            if (data.error) {
                setError(data.error);
            } else {
                setStrategies(data.strategies);
            }
        } catch (error) {
            setError('Failed to fetch strategies');
            console.error('Error fetching strategies:', error);
        }
    };

    const handleStrategyChange = async (event) => {
        const strategy = event.target.value;
        setSelectedStrategy(strategy);
        
        // Fetch strategy parameters
        try {
            const response = await fetch(`http://localhost:5000/api/strategy/parameters?strategy=${strategy}`);
            const data = await response.json();
            if (data.error) {
                setError(data.error);
            } else {
                // Initialize strategy parameters with defaults
                const params = {};
                Object.entries(data.parameters).forEach(([key, value]) => {
                    params[key] = value.default;
                });
                setStrategyParams(data.parameters);
                setParameters(prev => ({
                    ...prev,
                    strategy_params: params
                }));
            }
        } catch (error) {
            setError('Failed to fetch strategy parameters');
            console.error('Error fetching parameters:', error);
        }
    };

    const handleParameterChange = (param) => (event) => {
        const value = event.target.type === 'number' ? parseFloat(event.target.value) : event.target.value;
        setParameters(prev => ({
            ...prev,
            [param]: value
        }));
    };

    const handleStrategyParamChange = (param) => (event) => {
        const value = event.target.type === 'number' ? parseFloat(event.target.value) : event.target.value;
        setParameters(prev => ({
            ...prev,
            strategy_params: {
                ...prev.strategy_params,
                [param]: value
            }
        }));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        if (!selectedStrategy) {
            setError('Please select a strategy');
            return;
        }
        
        onRunBacktest({
            strategy: selectedStrategy,
            ...parameters
        });
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}
            
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <FormControl fullWidth>
                        <InputLabel>Strategy</InputLabel>
                        <Select
                            value={selectedStrategy}
                            onChange={handleStrategyChange}
                            label="Strategy"
                            required
                        >
                            {strategies.map((strategy) => (
                                <MenuItem key={strategy.name} value={strategy.name}>
                                    {strategy.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                
                {selectedStrategy && Object.entries(strategyParams).map(([param, config]) => (
                    <Grid item xs={12} sm={6} key={param}>
                        <TextField
                            fullWidth
                            label={config.description || param}
                            type={config.type === 'int' || config.type === 'float' ? 'number' : 'text'}
                            value={parameters.strategy_params?.[param] ?? config.default}
                            onChange={handleStrategyParamChange(param)}
                            InputProps={{
                                inputProps: {
                                    min: config.min,
                                    max: config.max,
                                    step: config.type === 'float' ? 0.01 : 1
                                }
                            }}
                        />
                    </Grid>
                ))}
                
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Period (days)"
                        type="number"
                        value={parameters.period_days}
                        onChange={handleParameterChange('period_days')}
                        InputProps={{ inputProps: { min: 1 } }}
                    />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                        <InputLabel>Interval</InputLabel>
                        <Select
                            value={parameters.interval}
                            onChange={handleParameterChange('interval')}
                            label="Interval"
                        >
                            <MenuItem value="1m">1 minute</MenuItem>
                            <MenuItem value="5m">5 minutes</MenuItem>
                            <MenuItem value="15m">15 minutes</MenuItem>
                            <MenuItem value="1h">1 hour</MenuItem>
                            <MenuItem value="4h">4 hours</MenuItem>
                            <MenuItem value="1d">1 day</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Initial Capital"
                        type="number"
                        value={parameters.initial_capital}
                        onChange={handleParameterChange('initial_capital')}
                        InputProps={{ inputProps: { min: 0 } }}
                    />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Stop Loss"
                        type="number"
                        value={parameters.stop_loss}
                        onChange={handleParameterChange('stop_loss')}
                        InputProps={{ inputProps: { min: 0, max: 1, step: 0.01 } }}
                    />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Take Profit"
                        type="number"
                        value={parameters.take_profit}
                        onChange={handleParameterChange('take_profit')}
                        InputProps={{ inputProps: { min: 0, max: 1, step: 0.01 } }}
                    />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Position Size"
                        type="number"
                        value={parameters.position_size}
                        onChange={handleParameterChange('position_size')}
                        InputProps={{ inputProps: { min: 0, max: 1, step: 0.1 } }}
                    />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Commission"
                        type="number"
                        value={parameters.commission}
                        onChange={handleParameterChange('commission')}
                        InputProps={{ inputProps: { min: 0, max: 1, step: 0.001 } }}
                    />
                </Grid>
                
                <Grid item xs={12}>
                    <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        type="submit"
                        disabled={isLoading || !selectedStrategy}
                    >
                        {isLoading ? 'Running Backtest...' : 'Run Backtest'}
                    </Button>
                </Grid>
            </Grid>
        </Box>
    );
};

export default BacktestControls;
