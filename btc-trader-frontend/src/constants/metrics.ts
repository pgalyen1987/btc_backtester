import { MetricConfig } from '../types';

export const metrics: MetricConfig[] = [
    {
        key: 'totalReturns',
        label: 'Total Returns',
        format: 'percent',
        description: 'Total percentage return over the backtest period'
    },
    {
        key: 'annualizedReturns',
        label: 'Annualized Returns',
        format: 'percent',
        description: 'Returns normalized to a yearly basis'
    },
    {
        key: 'maxDrawdown',
        label: 'Max Drawdown',
        format: 'percent',
        description: 'Largest peak-to-trough decline'
    },
    {
        key: 'sharpeRatio',
        label: 'Sharpe Ratio',
        format: 'number',
        description: 'Risk-adjusted return metric'
    },
    {
        key: 'winRate',
        label: 'Win Rate',
        format: 'percent',
        description: 'Percentage of profitable trades'
    },
    {
        key: 'profitFactor',
        label: 'Profit Factor',
        format: 'number',
        description: 'Ratio of gross profits to gross losses'
    }
];

export default metrics; 