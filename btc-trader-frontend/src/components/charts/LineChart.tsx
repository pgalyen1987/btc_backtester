import React from 'react';
import { Box } from '@mui/material';
import { BaseChart } from '../common/BaseChart';
import { ChartDataPoint } from '../../types';
import { CHART_CONFIG } from '../../config';

interface LineChartProps {
    data: ChartDataPoint[];
    height?: number;
    showVolume?: boolean;
}

export const LineChart: React.FC<LineChartProps> = ({
    data,
    height = CHART_CONFIG.chart.height,
    showVolume = true
}) => {
    return (
        <Box height={height}>
            <BaseChart
                data={data}
                height={height}
                showVolume={showVolume}
            />
        </Box>
    );
}; 