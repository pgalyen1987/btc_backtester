import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { Trade } from '../../types';
import { formatters } from '../../utils/formatters';

interface TradeListProps {
  trades: Trade[];
}

export const TradeList: React.FC<TradeListProps> = ({ trades }) => {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Type</TableCell>
            <TableCell align="right">Price</TableCell>
            <TableCell align="right">Amount</TableCell>
            <TableCell align="right">P/L</TableCell>
            <TableCell align="right">Return %</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {trades.map((trade, index) => (
            <TableRow key={index}>
              <TableCell>{formatters.formatDate(trade.timestamp)}</TableCell>
              <TableCell>{trade.type}</TableCell>
              <TableCell align="right">{formatters.formatPrice(trade.price)}</TableCell>
              <TableCell align="right">{formatters.formatNumber(trade.amount)}</TableCell>
              <TableCell align="right">{formatters.formatPrice(trade.profit_loss)}</TableCell>
              <TableCell align="right">{formatters.formatPercent(trade.return_pct)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}; 