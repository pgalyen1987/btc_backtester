import { format } from 'date-fns';

export const formatDate = (timestamp: number): string => {
    return format(new Date(timestamp), 'yyyy-MM-dd HH:mm:ss');
};

export const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(price);
};

export const formatPercent = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value / 100);
};

export const formatNumber = (value: number, decimals: number = 2): string => {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
};

export const serializeDate = (date: Date): number => {
    return date.getTime();
};

export const deserializeDate = (timestamp: number): Date => {
    return new Date(timestamp);
};

export const formatters = {
    formatDate,
    formatPrice,
    formatPercent,
    formatNumber,
    serializeDate,
    deserializeDate
}; 