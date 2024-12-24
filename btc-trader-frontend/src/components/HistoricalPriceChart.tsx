import React from 'react';
import { useHistoricalData } from '../hooks/useHistoricalData';

interface HistoricalPriceChartProps {
    period?: string;
    interval?: string;
}

export const HistoricalPriceChart: React.FC<HistoricalPriceChartProps> = ({
    period = '1y',
    interval = '1d'
}) => {
    const { data, loading, error } = useHistoricalData(period, interval);

    if (loading) return <div>Loading chart data...</div>;
    if (error) return <div>Error loading chart: {error}</div>;
    if (!data) return <div>No data available</div>;

    // Basic SVG chart
    const width = 800;
    const height = 400;
    const padding = 40;

    // Calculate scales
    const minPrice = Math.min(...data.prices);
    const maxPrice = Math.max(...data.prices);
    const priceRange = maxPrice - minPrice;

    // Create points for the line
    const points = data.prices.map((price, index) => {
        const x = (index / (data.prices.length - 1)) * (width - 2 * padding) + padding;
        const y = height - padding - ((price - minPrice) / priceRange) * (height - 2 * padding);
        return `${x},${y}`;
    }).join(' ');

    return (
        <div>
            <h2>BTC Historical Price</h2>
            <svg 
                width={width} 
                height={height} 
                style={{ border: '1px solid #ccc' }}
            >
                {/* Price line */}
                <polyline
                    points={points}
                    fill="none"
                    stroke="#4299e1"
                    strokeWidth="2"
                />

                {/* Price axis labels */}
                <text x="10" y="20" fontSize="12">${maxPrice.toFixed(2)}</text>
                <text x="10" y={height - 10} fontSize="12">${minPrice.toFixed(2)}</text>

                {/* Date axis labels */}
                <text x={padding} y={height - 5} fontSize="12">
                    {new Date(data.timestamps[0]).toLocaleDateString()}
                </text>
                <text x={width - padding} y={height - 5} fontSize="12" textAnchor="end">
                    {new Date(data.timestamps[data.timestamps.length - 1]).toLocaleDateString()}
                </text>
            </svg>
        </div>
    );
}; 