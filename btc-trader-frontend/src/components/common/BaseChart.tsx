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
    Legend
} from 'recharts';
import { ChartDataPoint } from '../../types';
import { formatters } from '../../utils/formatters';

interface BaseChartProps {
    data: ChartDataPoint[];
    height?: number;
    showVolume?: boolean;
    children?: React.ReactNode;
}

export const BaseChart: React.FC<BaseChartProps> = ({
    data,
    height = 400,
    showVolume = true,
    children
}) => {
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
        <ResponsiveContainer width="100%" height={height}>
            <ComposedChart data={data}>
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
                {showVolume && (
                    <YAxis
                        yAxisId="volume"
                        orientation="left"
                        tickFormatter={(value: number) => formatters.formatNumber(value)}
                    />
                )}
                <Tooltip
                    labelFormatter={formatLabel}
                    formatter={formatTooltipValue}
                />
                <Legend />
                {showVolume && (
                    <Bar
                        dataKey="volume"
                        yAxisId="volume"
                        fill="#8884d8"
                        opacity={0.5}
                        name="Volume"
                    />
                )}
                <Line
                    type="monotone"
                    dataKey="price"
                    yAxisId="price"
                    stroke="#82ca9d"
                    dot={false}
                    name="Price"
                />
                {children}
            </ComposedChart>
        </ResponsiveContainer>
    );
}; 