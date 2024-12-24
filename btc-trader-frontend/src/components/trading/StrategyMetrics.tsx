import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
} from '@mui/material';
import { CHART_CONFIG } from '../../config';
import { BacktestMetrics } from '../../types';

interface MetricCardProps {
  label: string;
  value: number;
  format?: (value: number) => string;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, format }) => (
  <Grid item xs={12} sm={6} md={4}>
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        {label}
      </Typography>
      <Typography variant="h6" sx={{
        color: value > 0 ? CHART_CONFIG.colors.success :
          value < 0 ? CHART_CONFIG.colors.error :
            'inherit'
      }}>
        {format ? format(value) : value}
      </Typography>
    </Paper>
  </Grid>
);

interface StrategyMetricsProps {
  metrics: BacktestMetrics;
}

const StrategyMetrics: React.FC<StrategyMetricsProps> = ({ metrics }) => {
  if (!metrics) return null;

  const formatPercent = (value: number): string => `${(value * 100).toFixed(2)}%`;
  const formatCurrency = (value: number): string => `$${value.toFixed(2)}`;
  const formatNumber = (value: number): string => value.toFixed(2);

  const metricsConfig = [
    { label: 'Total Return', value: metrics.total_return, format: formatPercent },
    { label: 'Annual Return', value: metrics.annual_return, format: formatPercent },
    { label: 'Sharpe Ratio', value: metrics.sharpe_ratio, format: formatNumber },
    { label: 'Win Rate', value: metrics.win_rate, format: formatPercent },
    { label: 'Max Drawdown', value: metrics.max_drawdown, format: formatPercent },
    { label: 'Profit Factor', value: metrics.profit_factor, format: formatNumber },
    { label: 'Total Trades', value: metrics.total_trades },
    { label: 'Winning Trades', value: metrics.winning_trades },
    { label: 'Losing Trades', value: metrics.losing_trades }
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