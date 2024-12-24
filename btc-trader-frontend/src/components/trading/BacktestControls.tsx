import React from 'react';
import { Box, Button, Grid, TextField } from '@mui/material';
import { BacktestFormData } from '../../types';

interface BacktestControlsProps {
    onSubmit: (formData: BacktestFormData) => void;
}

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

export const BacktestControls: React.FC<BacktestControlsProps> = ({ onSubmit }) => {
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

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ p: 2 }}>
            <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Strategy"
                        value={formData.strategy}
                        onChange={handleChange('strategy')}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Period (days)"
                        value={formData.period_days}
                        onChange={handleChange('period_days')}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Initial Capital"
                        value={formData.initial_capital}
                        onChange={handleChange('initial_capital')}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Position Size"
                        value={formData.position_size}
                        onChange={handleChange('position_size')}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Stop Loss"
                        value={formData.stop_loss}
                        onChange={handleChange('stop_loss')}
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        type="number"
                        label="Take Profit"
                        value={formData.take_profit}
                        onChange={handleChange('take_profit')}
                    />
                </Grid>
                <Grid item xs={12}>
                    <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        type="submit"
                    >
                        Run Backtest
                    </Button>
                </Grid>
            </Grid>
        </Box>
    );
}; 