import { ChartDataPoint, HistoricalData } from '../types';

export const prepareChartData = (data: HistoricalData): ChartDataPoint[] => {
    return data.timestamps.map((timestamp, index) => ({
        timestamp,
        price: data.prices[index],
        volume: data.volumes[index],
        ...(data.indicators?.sma && { sma: data.indicators.sma[index] }),
        ...(data.indicators?.ema && { ema: data.indicators.ema[index] }),
        ...(data.indicators?.rsi && { rsi: data.indicators.rsi[index] }),
        ...(data.indicators?.macd && {
            macd: data.indicators.macd.macd[index],
            signal: data.indicators.macd.signal[index],
            histogram: data.indicators.macd.histogram[index]
        }),
        ...(data.indicators?.bollinger && {
            upper: data.indicators.bollinger.upper[index],
            middle: data.indicators.bollinger.middle[index],
            lower: data.indicators.bollinger.lower[index]
        })
    }));
};

export const getChartDomain = (data: ChartDataPoint[]): [number, number] => {
    const prices = data.map(d => d.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const padding = (max - min) * 0.1;
    return [min - padding, max + padding];
};

export const getVolumeDomain = (data: ChartDataPoint[]): [number, number] => {
    const volumes = data.map(d => d.volume || 0);
    const max = Math.max(...volumes);
    return [0, max * 1.1];
}; 