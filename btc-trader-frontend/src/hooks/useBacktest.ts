import { useState } from 'react';
import { BacktestFormData, BacktestResults } from '../types';
import { api } from '../services/api';

interface UseBacktestReturn {
    runBacktest: (formData: BacktestFormData) => Promise<void>;
    results: BacktestResults | null;
    loading: boolean;
    error: string | null;
}

export const useBacktest = (): UseBacktestReturn => {
    const [results, setResults] = useState<BacktestResults | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const runBacktest = async (formData: BacktestFormData): Promise<void> => {
        try {
            setLoading(true);
            setError(null);

            const response = await api.runBacktest(formData);
            if (!response.success) {
                throw new Error(response.error || 'Failed to run backtest');
            }

            setResults(response.data ?? null);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'An error occurred';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return {
        runBacktest,
        results,
        loading,
        error
    };
}; 