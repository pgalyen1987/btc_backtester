// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:5000/ws';

// Chart Configuration
export const CHART_CONFIG = {
    colors: {
        primary: '#1976d2',
        success: '#4caf50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196f3',
        secondary: '#9c27b0'
    },
    chart: {
        height: 400,
        defaultHeight: 400,
        margin: {
            top: 20,
            right: 30,
            left: 30,
            bottom: 20
        }
    },
    animation: {
        duration: 300
    },
    defaultTimeframe: '1d',
    timeframes: ['1m', '5m', '15m', '1h', '4h', '1d'],
    indicators: {
        sma: {
            periods: [10, 20, 50, 200]
        },
        rsi: {
            period: 14,
            overbought: 70,
            oversold: 30
        },
        macd: {
            fastPeriod: 12,
            slowPeriod: 26,
            signalPeriod: 9
        }
    }
};

// API Endpoints
export const API_ENDPOINTS = {
    strategies: '/api/strategies',
    backtest: '/api/backtest',
    data: '/api/data',
    metrics: '/api/metrics',
    trades: '/api/trades',
    settings: '/api/settings'
};

// Backtest Configuration
export const BACKTEST_CONFIG = {
    maxPeriod: 365,
    minPeriod: 1,
    defaultPeriod: 30,
    maxParallelBacktests: 4,
    defaultCapital: 10000
};

// Application Configuration
export const APP_CONFIG = {
    defaultStrategy: 'moving_average',
    supportedExchanges: ['binance', 'coinbase', 'kraken'],
    defaultExchange: 'binance',
    apiTimeout: 30000
};

// Export strategy parameters
export * from './strategy-params'; 