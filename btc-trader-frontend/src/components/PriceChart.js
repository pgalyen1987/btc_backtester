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
    Scatter,
} from 'recharts';
import { Box } from '@mui/material';

const PriceChart = ({ data, signals }) => {
    if (!data || !signals) return null;

    // Transform the data into the format expected by recharts
    const chartData = data.dates.map((date, index) => ({
        date: new Date(date).getTime(),
        price: data.total[index],
        returns: data.returns[index],
        buySignal: signals[index] === 1 ? data.total[index] : null,
        sellSignal: signals[index] === -1 ? data.total[index] : null,
    }));

    return (
        <Box height={400}>
            <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="date"
                        type="number"
                        domain={['auto', 'auto']}
                        tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis
                        yAxisId="price"
                        domain={['auto', 'auto']}
                        tickFormatter={(value) => `$${value.toLocaleString()}`}
                    />
                    <YAxis
                        yAxisId="returns"
                        orientation="right"
                        tickFormatter={(value) => `${(value * 100).toFixed(2)}%`}
                    />
                    <Tooltip
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                        formatter={(value, name) => {
                            if (name === 'returns') {
                                return [`${(value * 100).toFixed(2)}%`, 'Returns'];
                            }
                            return [`$${value.toLocaleString()}`, name];
                        }}
                    />
                    <Legend />
                    
                    {/* Portfolio Value Line */}
                    <Line
                        yAxisId="price"
                        type="monotone"
                        dataKey="price"
                        stroke="#8884d8"
                        dot={false}
                        name="Portfolio Value"
                    />
                    
                    {/* Returns Line */}
                    <Line
                        yAxisId="returns"
                        type="monotone"
                        dataKey="returns"
                        stroke="#82ca9d"
                        dot={false}
                        name="Returns"
                    />
                    
                    {/* Buy Signals */}
                    <Scatter
                        yAxisId="price"
                        dataKey="buySignal"
                        fill="#00ff00"
                        name="Buy Signal"
                    />
                    
                    {/* Sell Signals */}
                    <Scatter
                        yAxisId="price"
                        dataKey="sellSignal"
                        fill="#ff0000"
                        name="Sell Signal"
                    />
                </ComposedChart>
            </ResponsiveContainer>
        </Box>
    );
};

export default PriceChart;
