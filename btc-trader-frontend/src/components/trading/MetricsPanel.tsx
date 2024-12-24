import React from 'react';
import { Box, Grid, Typography } from '@mui/material';
import { BacktestMetrics } from '../../types';
import { formatters } from '../../utils/formatters';

interface MetricsPanelProps {
    metrics: BacktestMetrics | null;
}

const metricConfigs = [
    { key: 'totalReturns', label: 'Total Returns', format: 'percent' },
    { key: 'annualizedReturns', label: 'Annualized Returns', format: 'percent' },
    { key: 'maxDrawdown', label: 'Max Drawdown', format: 'percent' },
    { key: 'sharpeRatio', label: 'Sharpe Ratio', format: 'number' },
    { key: 'winRate', label: 'Win Rate', format: 'percent' },
    { key: 'profitFactor', label: 'Profit Factor', format: 'number' }
];

export const MetricsPanel: React.FC<MetricsPanelProps> = ({ metrics }) => {
    if (!metrics) {
        return (
            <Box sx={{ p: 2 }}>
                <Typography color="text.secondary">
                    Run a backtest to see metrics
                </Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
                Backtest Metrics
            </Typography>
            <Grid container spacing={2}>
                {metricConfigs.map(({ key, label, format }) => (
                    <Grid item xs={6} key={key}>
                        <Typography variant="subtitle2" color="text.secondary">
                            {label}
                        </Typography>
                        <Typography variant="h6">
                            {format === 'percent'
                                ? formatters.formatPercent(metrics[key])
                                : formatters.formatNumber(metrics[key])}
                        </Typography>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
}; 