import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { PriceChart } from '../charts/PriceChart';
import { MetricsPanel } from './MetricsPanel';
import { TradesTable } from '../common/TradesTable';
import { BacktestResults } from '../../types';

interface StrategyComparisonProps {
    results: BacktestResults;
}

export const StrategyComparison: React.FC<StrategyComparisonProps> = ({ results }) => {
    return (
        <Grid container spacing={2}>
            <Grid item xs={12}>
                <Paper>
                    <Box p={2}>
                        <Typography variant="h6" gutterBottom>
                            Strategy Performance
                        </Typography>
                        <PriceChart trades={results.trades} />
                    </Box>
                </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
                <Paper>
                    <Box p={2}>
                        <MetricsPanel metrics={results.metrics} />
                    </Box>
                </Paper>
            </Grid>
            <Grid item xs={12} md={8}>
                <Paper>
                    <Box p={2}>
                        <TradesTable trades={results.trades} />
                    </Box>
                </Paper>
            </Grid>
        </Grid>
    );
}; 