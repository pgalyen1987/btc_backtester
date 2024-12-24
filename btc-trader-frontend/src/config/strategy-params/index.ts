import { ParameterConfig } from '../../types';
import simpleMAParams from './simple_ma';
import rsiParams from './rsi';
import combinedParams from './combined';

export const strategyParameters: Record<string, Record<string, ParameterConfig>> = {
    simple_ma: simpleMAParams,
    rsi: rsiParams,
    combined: combinedParams
};

export default strategyParameters; 