import React from 'react';
import {
    ResponsiveContainer,
    ComposedChart,
    Line,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    TooltipProps
} from 'recharts';
import { Trade } from '../../types';
import { formatters } from '../../utils/formatters';

interface PriceChartProps {
    trades: Trade[];
}

interface ChartDataPoint {
    timestamp: number;
    price: number;
    volume: number;
    type: 'buy' | 'sell';
}

export const PriceChart: React.FC<PriceChartProps> = ({ trades }) => {
    const chartData: ChartDataPoint[] = trades.map(trade => ({
        timestamp: trade.timestamp,
        price: trade.price,
        volume: trade.amount,
        type: trade.type
    }));

    const formatTooltipValue = (value: string | number | Array<string | number>, name: string) => {
        const numValue = typeof value === 'number' ? value : parseFloat(value as string);
        return [
            name === 'price'
                ? formatters.formatPrice(numValue)
                : formatters.formatNumber(numValue),
            name.charAt(0).toUpperCase() + name.slice(1)
        ];
    };

    const formatLabel = (label: string | number) => {
        const timestamp = typeof label === 'number' ? label : parseInt(label, 10);
        return formatters.formatDate(timestamp);
    };

    return (
        <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatLabel}
                />
                <YAxis
                    yAxisId="price"
                    orientation="right"
                    tickFormatter={(value: number) => formatters.formatPrice(value)}
                />
                <YAxis
                    yAxisId="volume"
                    orientation="left"
                    tickFormatter={(value: number) => formatters.formatNumber(value)}
                />
                <Tooltip
                    labelFormatter={formatLabel}
                    formatter={formatTooltipValue}
                />
                <Legend />
                <Bar
                    dataKey="volume"
                    yAxisId="volume"
                    fill="#8884d8"
                    opacity={0.5}
                    name="Volume"
                />
                <Line
                    type="monotone"
                    dataKey="price"
                    yAxisId="price"
                    stroke="#82ca9d"
                    dot={false}
                    name="Price"
                />
            </ComposedChart>
        </ResponsiveContainer>
    );
}; 