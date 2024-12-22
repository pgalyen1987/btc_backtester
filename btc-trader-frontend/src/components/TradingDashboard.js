import React, { useState } from 'react';
import { Box, Grid, Paper, Typography, Alert } from '@mui/material';
import BacktestControls from './BacktestControls';
import PriceChart from './PriceChart';
import StrategyComparison from './StrategyComparison';
import TradeList from './TradeList';
import StrategyMetrics from './StrategyMetrics';

const TradingDashboard = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState({});
  const [selectedStrategy, setSelectedStrategy] = useState(null);

  const handleRunBacktest = async (params) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });
      
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        // Store results by strategy name
        setResults(prev => ({
          ...prev,
          [params.strategy]: data
        }));
        setSelectedStrategy(params.strategy);
      }
    } catch (error) {
      setError('Failed to run backtest: ' + error.message);
      console.error('Backtest error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectedResult = selectedStrategy ? results[selectedStrategy] : null;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Trading Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <BacktestControls
              onRunBacktest={handleRunBacktest}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            {selectedResult ? (
              <PriceChart
                data={selectedResult.portfolio}
                signals={selectedResult.signals}
              />
            ) : (
              <Alert severity="info">
                Run a backtest to see results
              </Alert>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          {selectedResult && (
            <Paper sx={{ p: 2 }}>
              <StrategyMetrics metrics={selectedResult.metrics} />
            </Paper>
          )}
        </Grid>
        
        <Grid item xs={12} md={8}>
          {selectedResult && (
            <Paper sx={{ p: 2 }}>
              <TradeList trades={selectedResult.trades} />
            </Paper>
          )}
        </Grid>
        
        <Grid item xs={12}>
          <StrategyComparison
            results={results}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default TradingDashboard; 