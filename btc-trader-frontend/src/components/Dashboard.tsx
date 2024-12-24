import React from 'react';
import { Box, Grid, Paper } from '@mui/material';
import { HistoricalPriceChart } from './charts/HistoricalPriceChart';

export const Dashboard: React.FC = () => {
    return (
        <Box p={3}>
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Paper>
                        <Box p={2}>
                            <HistoricalPriceChart />
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
}; 