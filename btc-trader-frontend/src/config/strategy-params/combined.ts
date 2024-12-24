import { ParameterConfig } from '../../types';

const combinedParams: Record<string, ParameterConfig> = {
    smaShortPeriod: {
        type: 'number',
        label: 'SMA Short Period',
        default: 9,
        min: 2,
        max: 50,
        step: 1
    },
    smaLongPeriod: {
        type: 'number',
        label: 'SMA Long Period',
        default: 21,
        min: 5,
        max: 200,
        step: 1
    },
    rsiPeriod: {
        type: 'number',
        label: 'RSI Period',
        default: 14,
        min: 2,
        max: 50,
        step: 1
    },
    rsiOverbought: {
        type: 'number',
        label: 'RSI Overbought',
        default: 70,
        min: 50,
        max: 90,
        step: 1
    },
    rsiOversold: {
        type: 'number',
        label: 'RSI Oversold',
        default: 30,
        min: 10,
        max: 50,
        step: 1
    },
    stopLoss: {
        type: 'number',
        label: 'Stop Loss %',
        default: 2,
        min: 0.1,
        max: 10,
        step: 0.1
    },
    takeProfit: {
        type: 'number',
        label: 'Take Profit %',
        default: 3,
        min: 0.1,
        max: 20,
        step: 0.1
    }
};

export default combinedParams; 