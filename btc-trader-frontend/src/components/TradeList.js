import React from 'react';
import {
    Box,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
} from '@mui/material';

const TradeList = ({ trades }) => {
    if (!trades || trades.length === 0) {
        return (
            <Box>
                <Typography variant="h6" gutterBottom>
                    Trade History
                </Typography>
                <Typography color="text.secondary">
                    No trades executed
                </Typography>
            </Box>
        );
    }

    const formatDate = (dateStr) => {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleString();
    };

    const formatPrice = (price) => `$${price.toFixed(2)}`;
    const formatReturn = (value) => `${(value * 100).toFixed(2)}%`;

    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                Trade History
            </Typography>
            <TableContainer component={Paper}>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Entry Date</TableCell>
                            <TableCell>Exit Date</TableCell>
                            <TableCell align="right">Entry Price</TableCell>
                            <TableCell align="right">Exit Price</TableCell>
                            <TableCell align="right">Shares</TableCell>
                            <TableCell align="right">Return</TableCell>
                            <TableCell>Type</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {trades.map((trade, index) => (
                            <TableRow
                                key={index}
                                sx={{
                                    backgroundColor: trade.return_value > 0 ? 
                                        'success.light' : 
                                        trade.return_value < 0 ? 
                                            'error.light' : 
                                            'inherit'
                                }}
                            >
                                <TableCell>{formatDate(trade.entry_date)}</TableCell>
                                <TableCell>{formatDate(trade.exit_date)}</TableCell>
                                <TableCell align="right">{formatPrice(trade.entry_price)}</TableCell>
                                <TableCell align="right">
                                    {trade.exit_price ? formatPrice(trade.exit_price) : '-'}
                                </TableCell>
                                <TableCell align="right">{trade.shares.toFixed(4)}</TableCell>
                                <TableCell 
                                    align="right"
                                    sx={{
                                        color: trade.return_value > 0 ? 
                                            'success.dark' : 
                                            trade.return_value < 0 ? 
                                                'error.dark' : 
                                                'inherit'
                                    }}
                                >
                                    {formatReturn(trade.return_value)}
                                </TableCell>
                                <TableCell>{trade.type}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

export default TradeList;
