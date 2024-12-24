import React from 'react';
import { Paper, Box } from '@mui/material';

interface ChartContainerProps {
    children: React.ReactNode;
}

const ChartContainer: React.FC<ChartContainerProps> = ({ children }) => {
    return (
        <Paper
            elevation={2}
            sx={{
                p: 2,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative'
            }}
        >
            <Box sx={{ flex: 1, minHeight: 0 }}>
                {children}
            </Box>
        </Paper>
    );
};

export default ChartContainer; 