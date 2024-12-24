import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface LoadingOverlayProps {
    loading: boolean;
    error?: string;
    message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
    loading,
    error,
    message = 'Loading...'
}) => {
    if (!loading && !error) {
        return null;
    }

    return (
        <Box
            sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                zIndex: 1000
            }}
        >
            {loading && (
                <>
                    <CircularProgress size={40} />
                    <Typography
                        variant="body1"
                        color="text.secondary"
                        sx={{ mt: 2 }}
                    >
                        {message}
                    </Typography>
                </>
            )}
            {error && (
                <Typography
                    variant="body1"
                    color="error"
                    align="center"
                    sx={{ px: 2 }}
                >
                    {error}
                </Typography>
            )}
        </Box>
    );
}; 