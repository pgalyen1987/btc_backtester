import { ChartConfig } from '../types';

export const chartConfig: ChartConfig = {
    height: 400,
    defaultHeight: 300,
    margin: {
        top: 20,
        right: 30,
        bottom: 30,
        left: 60
    }
};

export const colors = {
    primary: '#2196f3',
    success: '#4caf50',
    error: '#f44336',
    warning: '#ff9800',
    info: '#00bcd4',
    secondary: '#9e9e9e'
};

export const animation = {
    duration: 300,
    easing: 'ease-in-out'
};

export const defaultTimeframe = '1d';
export const timeframes = ['1h', '4h', '1d', '1w', '1M'];

export const indicators = {
    sma: {
        periods: [9, 20, 50, 200],
        colors: ['#ff9800', '#2196f3', '#4caf50', '#9c27b0']
    },
    ema: {
        periods: [9, 21, 55, 200],
        colors: ['#ff9800', '#2196f3', '#4caf50', '#9c27b0']
    },
    rsi: {
        period: 14,
        overbought: 70,
        oversold: 30,
        color: '#2196f3'
    },
    macd: {
        fastPeriod: 12,
        slowPeriod: 26,
        signalPeriod: 9,
        colors: {
            macd: '#2196f3',
            signal: '#ff9800',
            histogram: '#4caf50'
        }
    },
    bollinger: {
        period: 20,
        stdDev: 2,
        colors: {
            upper: '#ff9800',
            middle: '#2196f3',
            lower: '#ff9800'
        }
    }
}; 