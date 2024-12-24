import React from 'react';
import {
    Box,
    Typography,
    Grid,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';
import { CHART_CONFIG } from '../../config';

interface MetricCardProps {
    label: string;
    value: number | string;
    format?: (value: number) => string;
}

interface ModelFeature {
    name: string;
    type: string;
    importance?: number;
}

interface TrainingInfo {
    samples: number;
    period: string;
    last_update: string;
}

interface ModelInfo {
    model_type: string;
    training_info: TrainingInfo;
    features: ModelFeature[];
    hyperparameters: Record<string, number | string>;
}

interface ModelInfoProps {
    modelInfo: ModelInfo;
    predictions: any[]; // TODO: Define proper type based on predictions structure
    accuracy: number;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, format }) => (
    <Grid item xs={12} sm={6} md={4}>
        <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                {label}
            </Typography>
            <Typography variant="h6" sx={{
                color: typeof value === 'number' ? (
                    value > 0 ? CHART_CONFIG.colors.success :
                    value < 0 ? CHART_CONFIG.colors.error :
                    'inherit'
                ) : 'inherit'
            }}>
                {typeof value === 'number' && format ? format(value) : value}
            </Typography>
        </Paper>
    </Grid>
);

const ModelInfo: React.FC<ModelInfoProps> = ({ modelInfo, predictions, accuracy }) => {
    if (!modelInfo) return null;

    const formatPercent = (value: number): string => `${(value * 100).toFixed(2)}%`;
    const formatNumber = (value: number): string => value.toFixed(4);

    const metricsConfig = [
        { label: 'Prediction Accuracy', value: accuracy, format: formatPercent },
        { label: 'Model Type', value: modelInfo.model_type },
        { label: 'Training Samples', value: modelInfo.training_info?.samples },
        { label: 'Training Period', value: modelInfo.training_info?.period },
        { label: 'Last Updated', value: new Date(modelInfo.training_info?.last_update).toLocaleDateString() },
    ];

    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                ML Model Information
            </Typography>

            <Grid container spacing={2}>
                {metricsConfig.map((metric) => (
                    <MetricCard
                        key={metric.label}
                        label={metric.label}
                        value={metric.value}
                        format={metric.format}
                    />
                ))}
            </Grid>

            <Box sx={{ mt: 4 }}>
                <Typography variant="subtitle1" gutterBottom>
                    Model Features
                </Typography>
                <TableContainer component={Paper}>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell>Feature</TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell>Importance</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {modelInfo.features.map((feature) => (
                                <TableRow key={feature.name}>
                                    <TableCell>{feature.name}</TableCell>
                                    <TableCell>{feature.type}</TableCell>
                                    <TableCell>
                                        {feature.importance ? formatPercent(feature.importance) : 'N/A'}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Box>

            <Box sx={{ mt: 4 }}>
                <Typography variant="subtitle1" gutterBottom>
                    Model Hyperparameters
                </Typography>
                <TableContainer component={Paper}>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell>Parameter</TableCell>
                                <TableCell>Value</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {Object.entries(modelInfo.hyperparameters).map(([key, value]) => (
                                <TableRow key={key}>
                                    <TableCell>{key}</TableCell>
                                    <TableCell>{typeof value === 'number' ? formatNumber(value) : value}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Box>
        </Box>
    );
};

export default ModelInfo; 