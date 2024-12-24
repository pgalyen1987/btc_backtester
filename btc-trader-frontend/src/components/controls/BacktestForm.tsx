import React from 'react';
import { Box, Button, Grid, TextField, MenuItem } from '@mui/material';
import { BacktestFormData, ParameterConfig } from '../../types';
import { strategyParameters } from '../../config/strategy-params';

interface BacktestFormProps {
    onSubmit: (formData: BacktestFormData) => void;
    loading?: boolean;
    error?: string;
}

const intervals = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' }
];

const defaultFormData: BacktestFormData = {
    strategy: 'sma_crossover',
    parameters: {
        fast_period: 10,
        slow_period: 20
    },
    interval: '1d',
    period_days: 365,
    initial_capital: 10000,
    position_size: 0.1,
    stop_loss: 0.02,
    take_profit: 0.05,
    commission: 0.001
};

export const BacktestForm: React.FC<BacktestFormProps> = ({
    onSubmit,
    loading = false,
    error
}) => {
    const [formData, setFormData] = React.useState<BacktestFormData>(defaultFormData);

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        onSubmit(formData);
    };

    const handleChange = (field: keyof BacktestFormData) => (
        event: React.ChangeEvent<HTMLInputElement>
    ) => {
        const value = event.target.type === 'number' ? Number(event.target.value) : event.target.value;
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleParameterChange = (key: string) => (
        event: React.ChangeEvent<HTMLInputElement>
    ) => {
        const value = Number(event.target.value);
        setFormData(prev => ({
            ...prev,
            parameters: {
                ...prev.parameters,
                [key]: value
            }
        }));
    };

    const currentStrategyParams = strategyParameters[formData.strategy] || {};

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ p: 2 }}>
            <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        select
                        label="Strategy"
                        value={formData.strategy}
                        onChange={handleChange('strategy')}
                        disabled={loading}
                    >
                        {Object.keys(strategyParameters).map(strategy => (
                            <MenuItem key={strategy} value={strategy}>
                                {strategy}
                            </MenuItem>
                        ))}
                    </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        select
                        label="Interval"
                        value={formData.interval}
                        onChange={handleChange('interval')}
                        disabled={loading}
                    >
                        {intervals.map(option => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))}
                    </TextField>
                </Grid>
                {Object.entries(currentStrategyParams).map(([key, param]) => (
                    <Grid item xs={12} sm={6} key={key}>
                        <TextField
                            fullWidth
                            type="number"
                            label={param.label}
                            value={formData.parameters[key] ?? param.default}
                            onChange={handleParameterChange(key)}
                            disabled={loading}
                            inputProps={{
                                min: param.min,
                                max: param.max,
                                step: param.step || 1
                            }}
                        />
                    </Grid>
                ))}
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Period (days)"
                        value={formData.period_days}
                        onChange={handleChange('period_days')}
                        disabled={loading}
                        inputProps={{ min: 1, max: 365 * 2 }}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Initial Capital"
                        value={formData.initial_capital}
                        onChange={handleChange('initial_capital')}
                        disabled={loading}
                        inputProps={{ min: 100, max: 1000000 }}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Position Size"
                        value={formData.position_size}
                        onChange={handleChange('position_size')}
                        disabled={loading}
                        inputProps={{ min: 0.01, max: 1, step: 0.01 }}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Stop Loss"
                        value={formData.stop_loss}
                        onChange={handleChange('stop_loss')}
                        disabled={loading}
                        inputProps={{ min: 0.01, max: 0.5, step: 0.01 }}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Take Profit"
                        value={formData.take_profit}
                        onChange={handleChange('take_profit')}
                        disabled={loading}
                        inputProps={{ min: 0.01, max: 1, step: 0.01 }}
                    />
                </Grid>
                <Grid item xs={12}>
                    <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        type="submit"
                        disabled={loading}
                    >
                        {loading ? 'Running Backtest...' : 'Run Backtest'}
                    </Button>
                </Grid>
            </Grid>
        </Box>
    );
}; 