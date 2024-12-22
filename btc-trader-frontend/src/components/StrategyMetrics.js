import React from 'react';
import {
    Box,
    Typography,
    Grid,
    Paper,
} from '@mui/material';

const MetricCard = ({ label, value, format }) => (
    <Grid item xs={12} sm={6} md={4}>
        <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                {label}
            </Typography>
            <Typography variant="h6">
                {format ? format(value) : value}
            </Typography>
        </Paper>
    </Grid>
);

const StrategyMetrics = ({ metrics }) => {
    if (!metrics) return null;

    const formatPercent = (value) => `${(value * 100).toFixed(2)}%`;
    const formatCurrency = (value) => `$${value.toFixed(2)}`;
    const formatNumber = (value) => value.toFixed(2);

    const metricsConfig = [
        { label: 'Total Return', value: metrics.total_return, format: formatPercent },
        { label: 'Annual Return', value: metrics.annual_return, format: formatPercent },
        { label: 'Sharpe Ratio', value: metrics.sharpe_ratio, format: formatNumber },
        { label: 'Sortino Ratio', value: metrics.sortino_ratio, format: formatNumber },
        { label: 'Max Drawdown', value: metrics.max_drawdown, format: formatPercent },
        { label: 'Win Rate', value: metrics.win_rate, format: formatPercent },
        { label: 'Profit Factor', value: metrics.profit_factor, format: formatNumber },
        { label: 'Trade Count', value: metrics.trade_count },
        { label: 'Commission Paid', value: metrics.commission_paid, format: formatCurrency },
    ];

    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                Strategy Performance
            </Typography>
            <Grid container spacing={2}>
                {metricsConfig.map((metric) => (
                    <MetricCard
                        key={metric.label}
                        label={metric.label}
                        value={metric.value}
                        format={metric.format}
                    />
                ))}
            </Grid>
        </Box>
    );
};

export default StrategyMetrics;
