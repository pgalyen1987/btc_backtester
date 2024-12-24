import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { API_BASE_URL } from '../../config';

interface InteractiveChartProps {
  chartPath: string;
  title?: string;
}

const InteractiveChart: React.FC<InteractiveChartProps> = ({ chartPath, title }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!chartPath) {
      setLoading(false);
      return;
    }

    const checkChartAvailability = async () => {
      try {
        // Ensure the chart path is relative to the API URL
        const fullChartPath = chartPath.startsWith('http') 
          ? chartPath 
          : `${API_BASE_URL}/static/charts/${chartPath}`;

        const response = await fetch(fullChartPath);
        if (!response.ok) {
          throw new Error('Failed to load chart');
        }
        setLoading(false);
        setError(null);
      } catch (err) {
        console.error('Chart loading error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    };

    checkChartAvailability();
  }, [chartPath]);

  if (!chartPath) return null;

  // Ensure the chart path is relative to the API URL
  const fullChartPath = chartPath.startsWith('http') 
    ? chartPath 
    : `${API_BASE_URL}/static/charts/${chartPath}`;

  return (
    <Box>
      {title && (
        <Typography variant="h6" gutterBottom align="center">
          {title}
        </Typography>
      )}
      <Box sx={{ width: '100%', height: '600px', position: 'relative' }}>
        {loading && (
          <Box sx={{ 
            position: 'absolute', 
            top: '50%', 
            left: '50%', 
            transform: 'translate(-50%, -50%)'
          }}>
            <CircularProgress />
          </Box>
        )}
        {error && (
          <Box sx={{ 
            position: 'absolute', 
            top: '50%', 
            left: '50%', 
            transform: 'translate(-50%, -50%)', 
            width: '100%' 
          }}>
            <Alert severity="error">
              Failed to load chart: {error}
            </Alert>
          </Box>
        )}
        {!loading && !error && (
          <iframe
            src={fullChartPath}
            style={{
              width: '100%',
              height: '100%',
              border: 'none',
              borderRadius: '4px',
              backgroundColor: '#fff'
            }}
            title={title || 'Interactive Chart'}
          />
        )}
      </Box>
    </Box>
  );
};

export default InteractiveChart; 