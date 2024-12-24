import { ParameterConfig } from '../../types';

const rsiParams: Record<string, ParameterConfig> = {
    period: {
        type: 'number',
        label: 'RSI Period',
        default: 14,
        min: 2,
        max: 50,
        step: 1
    },
    overbought: {
        type: 'number',
        label: 'Overbought Level',
        default: 70,
        min: 50,
        max: 90,
        step: 1
    },
    oversold: {
        type: 'number',
        label: 'Oversold Level',
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

export default rsiParams; 