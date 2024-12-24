declare module '*.svg' {
    const content: any;
    export default content;
}

declare module '*.png' {
    const content: any;
    export default content;
}

declare module '*.jpg' {
    const content: any;
    export default content;
}

declare module '*.json' {
    const content: { [key: string]: any };
    export default content;
}

declare module '@mui/x-date-pickers' {
    export * from '@mui/x-date-pickers/LocalizationProvider';
    export * from '@mui/x-date-pickers/DatePicker';
    export * from '@mui/x-date-pickers/TimePicker';
    export * from '@mui/x-date-pickers/DateTimePicker';
}

declare module '@mui/x-date-pickers/AdapterDateFns' {
    import { DateAdapter } from '@mui/x-date-pickers/internals/models';
    
    export class AdapterDateFns implements DateAdapter<Date> {
        constructor();
        addDays(date: Date, amount: number): Date;
        addMonths(date: Date, amount: number): Date;
        getYear(date: Date): number;
        getMonth(date: Date): number;
        getDate(date: Date): number;
        getHours(date: Date): number;
        getMinutes(date: Date): number;
        getSeconds(date: Date): number;
        getMilliseconds(date: Date): number;
    }
}

declare module 'recharts' {
    export * from '@types/recharts';
}

declare module 'lightweight-charts' {
    export * from 'lightweight-charts';
} 