import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import { Strategy } from '../types';
import { strategyParameters } from '../config/strategy-params';

const strategies: Strategy[] = [
  {
    id: 'simple_ma',
    name: 'Simple Moving Average',
    description: 'A basic strategy using simple moving average crossovers',
    indicators: ['SMA'],
    parameters: {
      fast_period: 10,
      slow_period: 20
    }
  },
  {
    id: 'rsi',
    name: 'RSI Strategy',
    description: 'A strategy based on the Relative Strength Index',
    indicators: ['RSI'],
    parameters: {
      period: 14,
      overbought: 70,
      oversold: 30
    }
  },
  {
    id: 'combined',
    name: 'Combined Strategy',
    description: 'A strategy combining multiple technical indicators',
    indicators: ['SMA', 'RSI', 'MACD'],
    parameters: {
      sma_period: 20,
      rsi_period: 14,
      macd_fast: 12,
      macd_slow: 26,
      macd_signal: 9
    }
  }
];

export const Strategies: React.FC = () => {
  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Available Strategies
      </Typography>
      <Grid container spacing={3}>
        {strategies.map(strategy => (
          <Grid item xs={12} md={4} key={strategy.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {strategy.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {strategy.description}
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                  Indicators:
                </Typography>
                <List dense>
                  {strategy.indicators.map(indicator => (
                    <ListItem key={indicator}>
                      <ListItemText primary={indicator} />
                    </ListItem>
                  ))}
                </List>
                <Typography variant="subtitle2" gutterBottom>
                  Parameters:
                </Typography>
                <List dense>
                  {Object.entries(strategyParameters[strategy.id] || {}).map(([key, param]) => (
                    <ListItem key={key}>
                      <ListItemText
                        primary={param.label}
                        secondary={`Default: ${param.default}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}; 