import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { formatters } from '../../utils/formatters';

interface MetricCardProps {
    label: string;
    value: number;
    format: 'currency' | 'percentage' | 'number';
    description?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
    label,
    value,
    format,
    description
}) => {
    const formatValue = (val: number): string => {
        switch (format) {
            case 'currency':
                return formatters.formatPrice(val);
            case 'percentage':
                return formatters.formatPercent(val);
            default:
                return formatters.formatNumber(val);
        }
    };

    return (
        <Card>
            <CardContent>
                <Typography variant="subtitle2" color="text.secondary">
                    {label}
                </Typography>
                <Typography variant="h6">
                    {formatValue(value)}
                </Typography>
                {description && (
                    <Typography variant="body2" color="text.secondary">
                        {description}
                    </Typography>
                )}
            </CardContent>
        </Card>
    );
}; 