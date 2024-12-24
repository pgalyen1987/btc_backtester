export interface ChartDataPoint {
    timestamp: number;
    price: number;
    volume: number;
    open: number;
    high: number;
    low: number;
    close: number;
}

export interface HistoricalData {
    timestamps: number[];
    prices: number[];
    volumes: number[];
    chart: ChartDataPoint[];
    indicators?: {
        sma?: number[];
        ema?: number[];
        rsi?: number[];
        macd?: {
            macd: number[];
            signal: number[];
            histogram: number[];
        };
        bollinger?: {
            upper: number[];
            middle: number[];
            lower: number[];
        };
    };
}

export interface Strategy {
    id: string;
    name: string;
    description: string;
    indicators: string[];
    parameters: Record<string, unknown>;
}

export interface BacktestMetrics {
    total_return: number;
    annual_return: number;
    total_pnl: number;
    win_rate: number;
    winning_trades: number;
    losing_trades: number;
    sharpe_ratio: number;
    max_drawdown: number;
    total_trades: number;
    avg_trade_return: number;
    profit_factor: number;
    [key: string]: number;
}

export interface BacktestResults {
    trades: Trade[];
    metrics: BacktestMetrics;
}

export interface Trade {
    id: string;
    timestamp: number;
    type: 'buy' | 'sell';
    price: number;
    amount: number;
    profit_loss: number;
    return_pct: number;
}

export interface MetricConfig {
    key: string;
    label: string;
    format: string;
    description?: string;
}

export interface ChartConfig {
    height: number;
    defaultHeight: number;
    margin: {
        top: number;
        right: number;
        bottom: number;
        left: number;
    };
}

export interface LoadingOverlayProps {
    loading: boolean;
    error?: string;
    message?: string;
}

export interface ValidationResult {
    [key: string]: string;
}

export interface ParameterConfig {
    type: string;
    label: string;
    default: any;
    min?: number;
    max?: number;
    step?: number;
    options?: string[];
}

export interface BacktestFormData {
    strategy: string;
    parameters: Record<string, unknown>;
    interval: string;
    period_days: number;
    initial_capital: number;
    position_size: number;
    stop_loss: number;
    take_profit: number;
    commission: number;
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
}

export interface WebSocketMessage {
    type: WebSocketMessageType;
    data: any;
}

export type WebSocketMessageType = 
    | 'trade'
    | 'price'
    | 'error'
    | 'status'
    | 'ping'
    | 'pong'
    | 'subscribe'
    | 'unsubscribe'
    | 'subscribe_response'
    | 'unsubscribe_response'
    | 'connection'
    | 'price_update';

export interface WebSocketPriceUpdate {
    timestamp: number;
    price: number;
    volume: number;
}

export interface WebSocketTradeUpdate {
    id: string;
    timestamp: number;
    type: 'buy' | 'sell';
    price: number;
    amount: number;
}

export interface WebSocketError {
    message: string;
    code?: string;
}

export interface WebSocketStatus {
    connected: boolean;
    subscriptions: string[];
}

export interface Settings {
    apiKey: string;
    secretKey: string;
    testMode: boolean;
    riskLevel: 'low' | 'medium' | 'high';
    maxPositionSize: number;
    stopLossPercentage: number;
    takeProfitPercentage: number;
}

export interface ChartData {
    timestamp: number;
    value: number;
    [key: string]: any;
} 