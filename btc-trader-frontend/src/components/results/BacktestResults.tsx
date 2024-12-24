import React from 'react';
import { Box, Grid, Paper } from '@mui/material';
import { TradesTable } from '../tables/TradesTable';
import { MetricsPanel } from '../metrics/MetricsPanel';
import { PriceChart } from '../charts/PriceChart';
import { BacktestResults as BacktestResultsType } from '../../types';

interface BacktestResultsProps {
    results: BacktestResultsType;
    loading?: boolean;
}

export const BacktestResults: React.FC<BacktestResultsProps> = ({
    results,
    loading = false
}) => {
    return (
        <Grid container spacing={3}>
            <Grid item xs={12}>
                <Paper>
                    <Box p={2}>
                        <PriceChart trades={results.trades} />
                    </Box>
                </Paper>
            </Grid>
            <Grid item xs={12}>
                <Paper>
                    <Box p={2}>
                        <MetricsPanel metrics={results.metrics} />
                    </Box>
                </Paper>
            </Grid>
            <Grid item xs={12}>
                <Paper>
                    <Box p={2}>
                        <TradesTable trades={results.trades} />
                    </Box>
                </Paper>
            </Grid>
        </Grid>
    );
}; 