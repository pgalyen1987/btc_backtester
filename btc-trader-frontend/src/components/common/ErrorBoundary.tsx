import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Alert, Box } from '@mui/material';

interface Props {
  children: ReactNode;
  fallback?: (error: Error) => ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Chart Error:', error, errorInfo);
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  render(): ReactNode {
    const { hasError, error } = this.state;
    const { fallback, children } = this.props;

    if (hasError) {
      if (fallback) {
        return fallback(error!);
      }
      return (
        <Box sx={{ p: 2 }}>
          <Alert severity="error">
            {error?.message || 'An error occurred while rendering the component'}
          </Alert>
        </Box>
      );
    }

    return children;
  }
}

export default ErrorBoundary; 