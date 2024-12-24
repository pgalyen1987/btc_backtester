import React, { useEffect, useState } from 'react';
import {
    Box,
    Grid,
    Paper,
    Typography,
    TextField,
    Switch,
    FormControlLabel,
    Button,
    Alert
} from '@mui/material';
import { api } from '../services/api';
import { Settings as SettingsType } from '../types';

const defaultSettings: SettingsType = {
    apiKey: '',
    secretKey: '',
    testMode: true,
    riskLevel: 'medium',
    maxPositionSize: 0.1,
    stopLossPercentage: 0.02,
    takeProfitPercentage: 0.05
};

export const Settings: React.FC = () => {
    const [settings, setSettings] = useState<SettingsType>(defaultSettings);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        const loadSettings = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await api.fetchSettings();
                if (!response.success) {
                    throw new Error(response.error || 'Failed to load settings');
                }
                setSettings(response.data ?? defaultSettings);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load settings');
            } finally {
                setLoading(false);
            }
        };

        loadSettings();
    }, []);

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, checked } = event.target;
        setSettings(prev => ({
            ...prev,
            [name]: event.target.type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            const response = await api.updateSettings(settings);
            if (!response.success) {
                throw new Error(response.error || 'Failed to update settings');
            }
            setSuccess(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update settings');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box p={3}>
            <Typography variant="h4" gutterBottom>
                Settings
            </Typography>
            <Paper>
                <Box component="form" onSubmit={handleSubmit} p={3}>
                    <Grid container spacing={3}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="API Key"
                                name="apiKey"
                                value={settings.apiKey}
                                onChange={handleChange}
                                disabled={loading}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Secret Key"
                                name="secretKey"
                                type="password"
                                value={settings.secretKey}
                                onChange={handleChange}
                                disabled={loading}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        name="testMode"
                                        checked={settings.testMode}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                }
                                label="Test Mode"
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Max Position Size"
                                name="maxPositionSize"
                                type="number"
                                value={settings.maxPositionSize}
                                onChange={handleChange}
                                disabled={loading}
                                inputProps={{ min: 0.01, max: 1, step: 0.01 }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Stop Loss %"
                                name="stopLossPercentage"
                                type="number"
                                value={settings.stopLossPercentage}
                                onChange={handleChange}
                                disabled={loading}
                                inputProps={{ min: 0.01, max: 0.5, step: 0.01 }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Take Profit %"
                                name="takeProfitPercentage"
                                type="number"
                                value={settings.takeProfitPercentage}
                                onChange={handleChange}
                                disabled={loading}
                                inputProps={{ min: 0.01, max: 1, step: 0.01 }}
                            />
                        </Grid>
                        {error && (
                            <Grid item xs={12}>
                                <Alert severity="error">{error}</Alert>
                            </Grid>
                        )}
                        {success && (
                            <Grid item xs={12}>
                                <Alert severity="success">Settings updated successfully</Alert>
                            </Grid>
                        )}
                        <Grid item xs={12}>
                            <Button
                                type="submit"
                                variant="contained"
                                color="primary"
                                disabled={loading}
                            >
                                Save Settings
                            </Button>
                        </Grid>
                    </Grid>
                </Box>
            </Paper>
        </Box>
    );
}; 