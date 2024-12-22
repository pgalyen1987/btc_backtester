import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
} from '@mui/material';

const StrategyComparison = ({ results }) => {
  // Only show comparison when we have results from multiple strategies
  if (!results || Object.keys(results).length < 2) {
    return (
      <Box sx={{ mt: 2 }}>
        <Alert severity="info">
          Run at least two different strategies to see performance comparison
        </Alert>
      </Box>
    );
  }

  const metrics = [
    { key: 'total_return', label: 'Total Return', format: (value) => `${(value * 100).toFixed(2)}%` },
    { key: 'annual_return', label: 'Annual Return', format: (value) => `${(value * 100).toFixed(2)}%` },
    { key: 'sharpe_ratio', label: 'Sharpe Ratio', format: (value) => value.toFixed(2) },
    { key: 'sortino_ratio', label: 'Sortino Ratio', format: (value) => value.toFixed(2) },
    { key: 'max_drawdown', label: 'Max Drawdown', format: (value) => `${(value * 100).toFixed(2)}%` },
    { key: 'win_rate', label: 'Win Rate', format: (value) => `${(value * 100).toFixed(2)}%` },
    { key: 'profit_factor', label: 'Profit Factor', format: (value) => value.toFixed(2) },
    { key: 'trade_count', label: 'Trade Count', format: (value) => value },
    { key: 'commission_paid', label: 'Commission Paid', format: (value) => `$${value.toFixed(2)}` },
  ];

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Strategy Comparison
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Metric</TableCell>
              {Object.keys(results).map((strategy) => (
                <TableCell key={strategy} align="right">{strategy}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {metrics.map(({ key, label, format }) => (
              <TableRow key={key}>
                <TableCell component="th" scope="row">
                  {label}
                </TableCell>
                {Object.keys(results).map((strategy) => (
                  <TableCell key={`${strategy}-${key}`} align="right">
                    {format(results[strategy].metrics[key])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default StrategyComparison;
