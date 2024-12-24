import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { BaseChart } from '../common/BaseChart';
import { useHistoricalData } from '../../hooks/useHistoricalData';
import { ChartDataPoint } from '../../types';

interface HistoricalPriceChartProps {
    periodDays?: number;
    interval?: string;
}

export const HistoricalPriceChart: React.FC<HistoricalPriceChartProps> = ({
    periodDays = 365,
    interval = '1d'
}) => {
    const { data, loading, error, fetchData } = useHistoricalData();

    React.useEffect(() => {
        fetchData('BTC-USD', interval, periodDays);
    }, [interval, periodDays, fetchData]);

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" height={400}>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" height={400}>
                <Typography color="error">{error}</Typography>
            </Box>
        );
    }

    if (!data) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" height={400}>
                <Typography>No data available</Typography>
            </Box>
        );
    }

    const chartData: ChartDataPoint[] = data.prices.map(([timestamp, price, volume]) => ({
        timestamp,
        price,
        volume: volume || 0
    }));

    return (
        <BaseChart
            data={chartData}
            showVolume={true}
            height={400}
        />
    );
}; 