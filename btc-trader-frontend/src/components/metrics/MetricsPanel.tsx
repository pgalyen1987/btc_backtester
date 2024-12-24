import React from 'react';
import { Grid } from '@mui/material';
import { MetricCard } from '../common/MetricCard';
import { BacktestMetrics } from '../../types';

interface MetricsPanelProps {
    metrics: BacktestMetrics | null;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({ metrics }) => {
    if (!metrics) {
        return null;
    }

    return (
        <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                    label="Total Return"
                    value={metrics.total_return}
                    format="percentage"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                    label="Profit/Loss"
                    value={metrics.total_pnl}
                    format="currency"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                    label="Win Rate"
                    value={metrics.win_rate}
                    format="percentage"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                    label="Sharpe Ratio"
                    value={metrics.sharpe_ratio}
                    format="number"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                    label="Max Drawdown"
                    value={metrics.max_drawdown}
                    format="percentage"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                    label="Total Trades"
                    value={metrics.total_trades}
                    format="number"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                    label="Average Trade"
                    value={metrics.avg_trade_return}
                    format="percentage"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                    label="Profit Factor"
                    value={metrics.profit_factor}
                    format="number"
                />
            </Grid>
        </Grid>
    );
}; 