import { useState, useEffect } from 'react';
import { fetchHistoricalData, HistoricalData } from '../services/api';

interface UseHistoricalDataResult {
    data: HistoricalData | null;
    loading: boolean;
    error: string | null;
    refetch: () => Promise<void>;
}

export const useHistoricalData = (
    period: string = '1y',
    interval: string = '1d'
): UseHistoricalDataResult => {
    const [data, setData] = useState<HistoricalData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    
    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);
            const historicalData = await fetchHistoricalData(period, interval);
            setData(historicalData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch historical data');
        } finally {
            setLoading(false);
        }
    };
    
    useEffect(() => {
        fetchData();
    }, [period, interval]);
    
    return {
        data,
        loading,
        error,
        refetch: fetchData
    };
}; 