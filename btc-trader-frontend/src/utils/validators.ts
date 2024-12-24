import { ValidationResult } from '../types';

export const validateStrategyParameters = (
    parameters: Record<string, unknown>
): ValidationResult => {
    const errors: ValidationResult = {};

    // Validate each parameter
    Object.entries(parameters).forEach(([key, value]) => {
        if (value === undefined || value === null) {
            errors[key] = 'This field is required';
            return;
        }

        if (typeof value === 'number') {
            if (isNaN(value)) {
                errors[key] = 'Must be a valid number';
            }
        }

        if (typeof value === 'string' && value.trim() === '') {
            errors[key] = 'This field cannot be empty';
        }
    });

    return errors;
};

export const validateDateRange = (startDate: Date, endDate: Date): ValidationResult => {
    const errors: ValidationResult = {};

    if (!startDate) {
        errors.startDate = 'Start date is required';
    }

    if (!endDate) {
        errors.endDate = 'End date is required';
    }

    if (startDate && endDate && startDate > endDate) {
        errors.endDate = 'End date must be after start date';
    }

    return errors;
};

export const validateTimeframe = (timeframe: string): ValidationResult => {
    const errors: ValidationResult = {};
    const validTimeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M'];

    if (!timeframe) {
        errors.timeframe = 'Timeframe is required';
    } else if (!validTimeframes.includes(timeframe)) {
        errors.timeframe = 'Invalid timeframe';
    }

    return errors;
};

export const validateBacktestForm = (
    formData: Record<string, unknown>
): ValidationResult => {
    const errors: ValidationResult = {};

    // Validate strategy selection
    if (!formData.strategy) {
        errors.strategy = 'Strategy is required';
    }

    // Validate parameters
    if (formData.parameters) {
        const paramErrors = validateStrategyParameters(formData.parameters as Record<string, unknown>);
        Object.assign(errors, paramErrors);
    }

    // Validate dates
    if (formData.startDate && formData.endDate) {
        const dateErrors = validateDateRange(
            formData.startDate as Date,
            formData.endDate as Date
        );
        Object.assign(errors, dateErrors);
    }

    // Validate timeframe
    if (formData.timeframe) {
        const timeframeErrors = validateTimeframe(formData.timeframe as string);
        Object.assign(errors, timeframeErrors);
    }

    return errors;
}; 