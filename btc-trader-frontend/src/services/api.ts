import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export interface HistoricalData {
    timestamps: number[];
    prices: number[];
    volumes: number[];
    chart: Array<{
        timestamp: number;
        open: number;
        high: number;
        low: number;
        close: number;
        volume: number;
    }>;
}

export const isValidHistoricalData = (data: any): data is HistoricalData => {
    if (!data || typeof data !== 'object') return false;
    if (!Array.isArray(data.timestamps) || 
        !Array.isArray(data.prices) || 
        !Array.isArray(data.volumes) || 
        !Array.isArray(data.chart)) {
        return false;
    }
    const length = data.timestamps.length;
    if (data.prices.length !== length || 
        data.volumes.length !== length || 
        data.chart.length !== length) {
        return false;
    }
    return data.chart.every((point: any) => (
        typeof point === 'object' &&
        typeof point.timestamp === 'number' &&
        typeof point.open === 'number' &&
        typeof point.high === 'number' &&
        typeof point.low === 'number' &&
        typeof point.close === 'number' &&
        typeof point.volume === 'number'
    ));
};

export const fetchHistoricalData = async (
    period: string = '1y',
    interval: string = '1d'
): Promise<HistoricalData> => {
    try {
        const response = await axios.get(`${API_BASE_URL}/historical-data`, {
            params: { period, interval }
        });
        
        const data = response.data;
        if (!isValidHistoricalData(data)) {
            throw new Error('Invalid historical data format received from server');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching historical data:', error);
        throw error;
    }
}; 