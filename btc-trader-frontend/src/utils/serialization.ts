import { ChartData, ChartDataPoint } from '../types';
import { formatters } from './formatters';

export const serializeChartData = (data: ChartDataPoint[]): ChartData[] => {
    return data.map(({ timestamp, price, volume, ...rest }) => ({
        ...rest,
        timestamp: formatters.serializeDate(new Date(timestamp)),
        value: price,
        volume
    }));
};

export const deserializeChartData = (data: ChartData[]): ChartDataPoint[] => {
    return data.map(({ timestamp, value, volume, ...rest }) => ({
        ...rest,
        timestamp: formatters.deserializeDate(timestamp).getTime(),
        price: value,
        volume
    }));
}; 