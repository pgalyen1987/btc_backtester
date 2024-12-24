declare module '*.svg' {
    const content: string;
    export default content;
}

declare module '*.png' {
    const content: string;
    export default content;
}

declare module '*.jpg' {
    const content: string;
    export default content;
}

declare module '*.json' {
    const content: { [key: string]: any };
    export default content;
}

declare module '@mui/x-date-pickers/AdapterDateFns' {
    import { Adapter } from '@mui/x-date-pickers/internals';
    export default class AdapterDateFns implements Adapter<Date> {}
}

declare module '@mui/x-date-pickers' {
    export * from '@mui/x-date-pickers/LocalizationProvider';
    export * from '@mui/x-date-pickers/DatePicker';
}

declare module 'recharts' {
    export * from 'recharts/types';
}
