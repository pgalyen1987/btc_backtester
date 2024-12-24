import React from 'react';
import { Box, Grid, Paper } from '@mui/material';
import { BacktestForm } from '../controls/BacktestForm';
import { MetricsPanel } from '../trading/MetricsPanel';
import { TradesTable } from '../tables/TradesTable';
import { PriceChart } from '../charts/PriceChart';
import { BacktestFormData } from '../../types';
import { useBacktest } from '../../hooks/useBacktest';
import { LoadingOverlay } from '../common/LoadingOverlay';

export const TradingDashboard: React.FC = () => {
    const { runBacktest, results, loading, error } = useBacktest();

    const handleSubmit = (formData: BacktestFormData) => {
        runBacktest(formData);
    };

    return (
        <Box sx={{ position: 'relative', p: 3 }}>
            <LoadingOverlay loading={loading} error={error ?? undefined} />
            <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                    <Paper>
                        <BacktestForm
                            onSubmit={handleSubmit}
                            loading={loading}
                            error={error ?? undefined}
                        />
                    </Paper>
                </Grid>
                <Grid item xs={12} md={8}>
                    <Paper>
                        <Box p={2}>
                            <PriceChart trades={results?.trades || []} />
                        </Box>
                    </Paper>
                </Grid>
                <Grid item xs={12}>
                    <Paper>
                        <Box p={2}>
                            <MetricsPanel metrics={results?.metrics ?? null} />
                        </Box>
                    </Paper>
                </Grid>
                <Grid item xs={12}>
                    <Paper>
                        <Box p={2}>
                            <TradesTable trades={results?.trades || []} />
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
}; 