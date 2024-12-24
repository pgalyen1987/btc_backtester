import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper
} from '@mui/material';
import { BacktestResults } from '../../types';

interface MetricConfig {
    key: string;
    label: string;
    format: (value: number) => string;
}

interface MetricsTableProps {
    metrics: MetricConfig[];
    data: Record<string, BacktestResults>;
    strategies: string[];
}

const MetricsTable: React.FC<MetricsTableProps> = ({ metrics, data, strategies }) => {
    return (
        <TableContainer component={Paper}>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell>Metric</TableCell>
                        {strategies.map(strategy => (
                            <TableCell key={strategy} align="right">{strategy}</TableCell>
                        ))}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {metrics.map(metric => (
                        <TableRow key={metric.key}>
                            <TableCell>{metric.label}</TableCell>
                            {strategies.map(strategy => (
                                <TableCell key={`${strategy}-${metric.key}`} align="right">
                                    {metric.format(data[strategy].metrics[metric.key])}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default MetricsTable; 