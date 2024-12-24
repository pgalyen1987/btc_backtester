import { ParameterConfig } from '../../types';

const simpleMAParams: Record<string, ParameterConfig> = {
    shortPeriod: {
        type: 'number',
        label: 'Short Period',
        default: 9,
        min: 2,
        max: 50,
        step: 1
    },
    longPeriod: {
        type: 'number',
        label: 'Long Period',
        default: 21,
        min: 5,
        max: 200,
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

export default simpleMAParams; 