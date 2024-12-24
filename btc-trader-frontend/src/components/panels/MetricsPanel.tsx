import React from 'react';
import {
    Box,
    Card,
    CardContent,
    Grid,
    Typography,
    Skeleton
} from '@mui/material';
import { BacktestMetrics } from '../../types';

interface MetricsPanelProps {
    metrics: BacktestMetrics | null;
    isLoading?: boolean;
}

interface MetricCardProps {
    label: string;
    value: string | number;
    isLoading?: boolean;
    prefix?: string;
    suffix?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
    label,
    value,
    isLoading = false,
    prefix = '',
    suffix = ''
}) => (
    <Card>
        <CardContent>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                {label}
            </Typography>
            {isLoading ? (
                <Skeleton variant="text" width="60%" />
            ) : (
                <Typography variant="h6">
                    {prefix}
                    {typeof value === 'number' ? value.toLocaleString() : value}
                    {suffix}
                </Typography>
            )}
        </CardContent>
    </Card>
);

export const MetricsPanel: React.FC<MetricsPanelProps> = ({ metrics, isLoading = false }) => {
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                Performance Metrics
            </Typography>
            <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Total Return"
                        value={metrics?.total_return ?? 0}
                        isLoading={isLoading}
                        suffix="%"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Annual Return"
                        value={metrics?.annual_return ?? 0}
                        isLoading={isLoading}
                        suffix="%"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Sharpe Ratio"
                        value={metrics?.sharpe_ratio?.toFixed(2) ?? 0}
                        isLoading={isLoading}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Max Drawdown"
                        value={metrics?.max_drawdown ?? 0}
                        isLoading={isLoading}
                        suffix="%"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Win Rate"
                        value={metrics?.win_rate ?? 0}
                        isLoading={isLoading}
                        suffix="%"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Profit Factor"
                        value={metrics?.profit_factor?.toFixed(2) ?? 0}
                        isLoading={isLoading}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Total Trades"
                        value={metrics?.total_trades ?? 0}
                        isLoading={isLoading}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Winning Trades"
                        value={metrics?.winning_trades ?? 0}
                        isLoading={isLoading}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <MetricCard
                        label="Losing Trades"
                        value={metrics?.losing_trades ?? 0}
                        isLoading={isLoading}
                    />
                </Grid>
            </Grid>
        </Box>
    );
}; 