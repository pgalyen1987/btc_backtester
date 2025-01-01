import warnings
import pandas as pd
from pandas import DataFrame
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Filter out specific warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance.utils')
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas.core.frame')

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_btc_data(start="2008-01-01", end=None, interval="1d") -> DataFrame:
    """
    Download BTC-USD data from Yahoo Finance
    Args:
        start (str): Start date in YYYY-MM-DD format
        end (str): End date in YYYY-MM-DD format (optional, defaults to current date)
        interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 1h, 1d, 5d, 1wk, 1mo)
    Returns:
        pandas.DataFrame: Historical BTC data
    """
    btc = yf.Ticker("BTC-USD")
    
    # Define interval limits and chunks
    interval_limits = {
        # Minute intervals
        '1m':  {'days': 7, 'chunk_size': 7},
        '2m':  {'days': 7, 'chunk_size': 7},
        '5m':  {'days': 7, 'chunk_size': 7},
        '15m': {'days': 7, 'chunk_size': 7},
        '30m': {'days': 7, 'chunk_size': 7},
        '60m': {'days': 7, 'chunk_size': 7},
        # Hourly interval
        '1h':  {'days': 730, 'chunk_size': 30},  # 2 years
        # Daily and above
        '1d':  {'days': 365*10, 'chunk_size': None},  # 10 years
        '5d':  {'days': 365*5,  'chunk_size': None},  # 5 years
        '1wk': {'days': 365*5,  'chunk_size': None},  # 5 years
        '1mo': {'days': 365*10, 'chunk_size': None}   # 10 years
    }
    
    if interval not in interval_limits:
        logger.warning(f"Invalid interval '{interval}'. Falling back to daily data.")
        interval = '1d'
    
    end_date = datetime.strptime(end, "%Y-%m-%d") if end else datetime.now()
    start_date = datetime.strptime(start, "%Y-%m-%d")
    
    # Check if requested date range exceeds the limit
    max_days = interval_limits[interval]['days']
    date_range = (end_date - start_date).days
    
    if date_range > max_days:
        logger.warning(f"Requested date range ({date_range} days) exceeds maximum allowed ({max_days} days) for {interval} interval.")
        logger.info(f"Adjusting start date to {max_days} days before end date.")
        start_date = end_date - pd.Timedelta(days=max_days)
    
    chunk_size = interval_limits[interval]['chunk_size']
    
    if chunk_size is None:
        # Fetch all data at once for daily and longer intervals
        try:
            hist = btc.history(start=start_date, end=end_date, interval=interval)
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            logger.warning("Falling back to daily data.")
            hist = btc.history(start=start_date, end=end_date, interval="1d")
    else:
        # Fetch data in chunks for minute/hourly intervals
        chunks = []
        current_end = end_date
        current_start = current_end - pd.Timedelta(days=chunk_size)
        final_start = start_date
        
        while current_start >= final_start and len(chunks) < 100:  # Limit to 100 chunks for safety
            try:
                logger.info(f"Fetching {interval} data from {current_start} to {current_end}")
                chunk = btc.history(start=current_start, end=current_end, interval=interval)
                if len(chunk) > 0:
                    chunks.append(chunk)
                else:
                    logger.warning(f"No data available for period {current_start} to {current_end}")
                
                current_end = current_start
                current_start = current_end - pd.Timedelta(days=chunk_size)
            except Exception as e:
                logger.error(f"Error fetching chunk: {e}")
                break
        
        if not chunks:
            logger.warning("No data available for the specified interval. Falling back to daily data.")
            hist = btc.history(start=start_date, end=end_date, interval="1d")
        else:
            hist = pd.concat(chunks[::-1])  # Reverse to get chronological order
            hist = hist[~hist.index.duplicated(keep='first')]  # Remove any duplicates
    
    # Forward fill missing values first, then backward fill any remaining NaNs
    hist = hist.ffill().bfill()
    
    logger.info(f"Successfully fetched {len(hist)} data points with {interval} interval")
    logger.info(f"Date range: from {hist.index[0]} to {hist.index[-1]}")
    
    return hist

def calculate_indicators(data: DataFrame) -> DataFrame:
    """
    Calculate technical indicators
    Args:
        data (pandas.DataFrame): Historical BTC data
    Returns:
        pandas.DataFrame: Data with technical indicators
    """
    # Calculate moving averages
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # Calculate Bollinger Bands
    data['BB_middle'] = data['Close'].rolling(window=20).mean()
    data['BB_upper'] = data['BB_middle'] + 2 * data['Close'].rolling(window=20).std()
    data['BB_lower'] = data['BB_middle'] - 2 * data['Close'].rolling(window=20).std()
    
    return data

def create_chart_html(fig, filename, title):
    """Create HTML file for a chart component"""
    config = {
        'displayModeBar': True,
        'scrollZoom': False,
        'showTips': True,
        'responsive': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['select2d', 'lasso2d'],
        'modeBarButtonsToRemove': ['autoScale2d', 'zoomIn2d', 'zoomOut2d']
    }
    
    chart_html = fig.to_html(
        full_html=False,
        include_plotlyjs=True,
        config=config,
        include_mathjax=False,
        validate=True
    )
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            background-color: #1a1a1a;
            width: 100%;
            height: 100%;
        }}
        .chart-container {{
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        {chart_div}
    </div>
</body>
</html>"""
    
    # Write to file
    chart_path = os.path.join(SCRIPT_DIR, 'static', filename)
    with open(chart_path, 'w', encoding='utf-8') as f:
        f.write(html_template.format(title=title, chart_div=chart_html))

def create_interactive_charts(data):
    """Create separate interactive charts for each component"""
    # Calculate indicators
    data = calculate_indicators(data)
    
    # Get the date range from the data
    start_date = data.index[0]
    end_date = data.index[-1]
    
    # Create price chart with Bollinger Bands
    price_fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    price_fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'], name='BTC-USD'
    ))
    
    # Add Bollinger Bands
    price_fig.add_trace(go.Scatter(
        x=data.index, y=data['BB_upper'],
        line=dict(color='gray', width=1, dash='dash'),
        name='BB Upper'
    ))
    price_fig.add_trace(go.Scatter(
        x=data.index, y=data['BB_lower'],
        line=dict(color='gray', width=1, dash='dash'),
        name='BB Lower', fill='tonexty'
    ))
    
    # Add moving averages
    price_fig.add_trace(go.Scatter(
        x=data.index, y=data['MA20'],
        line=dict(color='yellow', width=1),
        name='20 MA'
    ))
    price_fig.add_trace(go.Scatter(
        x=data.index, y=data['MA50'],
        line=dict(color='blue', width=1),
        name='50 MA'
    ))
    price_fig.add_trace(go.Scatter(
        x=data.index, y=data['MA200'],
        line=dict(color='red', width=1),
        name='200 MA'
    ))
    
    # Update price chart layout
    price_fig.update_layout(
        height=500,
        template='plotly_dark',
        showlegend=True,
        margin=dict(t=0, l=0, r=0, b=0),
        xaxis=dict(
            type="date",
            range=[start_date, end_date],
            autorange=False
        )
    )
    
    # Create volume chart
    volume_fig = make_subplots(rows=1, cols=1)
    colors = ['red' if row['Open'] - row['Close'] >= 0 
              else 'green' for index, row in data.iterrows()]
    volume_fig.add_trace(go.Bar(
        x=data.index,
        y=data['Volume'],
        marker_color=colors,
        name='Volume'
    ))
    volume_fig.update_layout(
        height=200,
        template='plotly_dark',
        showlegend=False,
        margin=dict(t=0, l=0, r=0, b=0),
        xaxis=dict(
            type="date",
            range=[start_date, end_date],
            autorange=False
        )
    )
    
    # Create MACD chart
    macd_fig = make_subplots(rows=1, cols=1)
    macd_fig.add_trace(go.Scatter(
        x=data.index,
        y=data['MACD'],
        line=dict(color='blue', width=1),
        name='MACD'
    ))
    macd_fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Signal_Line'],
        line=dict(color='orange', width=1),
        name='Signal Line'
    ))
    macd_fig.update_layout(
        height=200,
        template='plotly_dark',
        showlegend=True,
        margin=dict(t=0, l=0, r=0, b=0),
        xaxis=dict(
            type="date",
            range=[start_date, end_date],
            autorange=False
        )
    )
    
    # Create RSI chart
    rsi_fig = make_subplots(rows=1, cols=1)
    rsi_fig.add_trace(go.Scatter(
        x=data.index,
        y=data['RSI'],
        line=dict(color='purple', width=1),
        name='RSI'
    ))
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(
        height=200,
        template='plotly_dark',
        showlegend=False,
        margin=dict(t=0, l=0, r=0, b=0),
        xaxis=dict(
            type="date",
            range=[start_date, end_date],
            autorange=False
        ),
        yaxis=dict(
            range=[0, 100]
        )
    )
    
    # Save all charts
    create_chart_html(price_fig, 'price_chart.html', 'BTC Price Chart')
    create_chart_html(volume_fig, 'volume_chart.html', 'BTC Volume Chart')
    create_chart_html(macd_fig, 'macd_chart.html', 'BTC MACD Chart')
    create_chart_html(rsi_fig, 'rsi_chart.html', 'BTC RSI Chart')
    
    logger.info("All charts have been generated in the static directory")

def main():
    # Get BTC data - allow user to specify interval via environment variable
    interval = os.getenv('CHART_INTERVAL', '1d')
    btc_data = get_btc_data(interval=interval)
    
    # Create and save the interactive chart
    create_interactive_charts(btc_data)
    logger.info("Chart has been generated as 'static/btc_chart.html'")

if __name__ == "__main__":
    main() 