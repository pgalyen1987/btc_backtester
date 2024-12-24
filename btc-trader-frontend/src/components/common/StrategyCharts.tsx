import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { PriceChart } from '../charts/PriceChart';
import { LoadingOverlay } from './LoadingOverlay';
import { BacktestResults } from '../../types';

interface StrategyChartsProps {
    results: BacktestResults;
    loading?: boolean;
    error?: string;
}

export const StrategyCharts: React.FC<StrategyChartsProps> = ({
    results,
    loading = false,
    error
}) => {
    if (!results && !loading && !error) {
        return (
            <Box p={2}>
                <Typography color="text.secondary">
                    Run a backtest to see results
                </Typography>
            </Box>
        );
    }

    return (
        <Box position="relative">
            <LoadingOverlay loading={loading} error={error} />
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Paper>
                        <Box p={2}>
                            <Typography variant="h6" gutterBottom>
                                Price Chart
                            </Typography>
                            <PriceChart trades={results.trades} />
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
}; 