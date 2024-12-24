import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Scatter,
  TooltipFormatter,
  LabelFormatter
} from 'recharts';
import { Box } from '@mui/material';
import { Trade } from '../../types';
import { CHART_CONFIG } from '../../config';
import { formatters } from '../../utils/formatters';

interface PriceChartProps {
  trades: Trade[];
  height?: number;
}

export const PriceChart: React.FC<PriceChartProps> = ({
  trades,
  height = CHART_CONFIG.chart.height
}) => {
  const chartData = trades.map(trade => ({
    timestamp: trade.timestamp,
    price: trade.price,
    type: trade.type,
    amount: trade.amount
  }));

  const formatTooltipLabel: LabelFormatter = (label) => {
    return formatters.formatDate(Number(label));
  };

  const formatTooltipValue: TooltipFormatter = (value, name) => {
    if (typeof value === 'number') {
      switch (name) {
        case 'price':
          return [formatters.formatPrice(value), 'Price'];
        case 'amount':
          return [formatters.formatNumber(value), 'Amount'];
        default:
          return [value.toString(), name];
      }
    }
    return [value.toString(), name];
  };

  return (
    <Box height={height}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatters.formatDate}
            type="number"
            domain={['auto', 'auto']}
          />
          <YAxis
            yAxisId="price"
            orientation="right"
            tickFormatter={formatters.formatPrice}
            domain={['auto', 'auto']}
          />
          <Tooltip
            labelFormatter={formatTooltipLabel}
            formatter={formatTooltipValue}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            yAxisId="price"
            stroke={CHART_CONFIG.colors.primary}
            dot={false}
          />
          <Scatter
            dataKey="price"
            yAxisId="price"
            data={chartData.filter(d => d.type === 'buy')}
            fill={CHART_CONFIG.colors.success}
            shape="circle"
          />
          <Scatter
            dataKey="price"
            yAxisId="price"
            data={chartData.filter(d => d.type === 'sell')}
            fill={CHART_CONFIG.colors.error}
            shape="circle"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  );
}; 