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

def create_interactive_chart(data):
    """
    Create an interactive candlestick chart using Plotly
    Args:
        data (pandas.DataFrame): Historical BTC data
    """
    # Calculate indicators
    data = calculate_indicators(data)
    
    # Get the date range from the data
    start_date = data.index[0]
    end_date = data.index[-1]
    
    # Create figure with secondary y-axis
    fig = make_subplots(rows=4, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.05,
                       row_heights=[0.5, 0.2, 0.15, 0.15])

    # Add candlestick chart
    fig.add_trace(go.Candlestick(x=data.index,
                                open=data['Open'],
                                high=data['High'],
                                low=data['Low'],
                                close=data['Close'],
                                name='BTC-USD'),
                  row=1, col=1)

    # Add Bollinger Bands
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'],
                            line=dict(color='gray', width=1, dash='dash'),
                            name='BB Upper'),
                  row=1, col=1)
    
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'],
                            line=dict(color='gray', width=1, dash='dash'),
                            name='BB Lower',
                            fill='tonexty'),  # Fill between upper and lower bands
                  row=1, col=1)

    # Add moving averages
    fig.add_trace(go.Scatter(x=data.index, y=data['MA20'],
                            line=dict(color='yellow', width=1),
                            name='20 MA'),
                  row=1, col=1)
    
    fig.add_trace(go.Scatter(x=data.index, y=data['MA50'],
                            line=dict(color='blue', width=1),
                            name='50 MA'),
                  row=1, col=1)
    
    fig.add_trace(go.Scatter(x=data.index, y=data['MA200'],
                            line=dict(color='red', width=1),
                            name='200 MA'),
                  row=1, col=1)

    # Add volume bar chart
    colors = ['red' if row['Open'] - row['Close'] >= 0 
              else 'green' for index, row in data.iterrows()]
    
    fig.add_trace(go.Bar(x=data.index, 
                        y=data['Volume'],
                        marker_color=colors,
                        name='Volume'),
                  row=2, col=1)

    # Add MACD
    fig.add_trace(go.Scatter(x=data.index,
                            y=data['MACD'],
                            line=dict(color='blue', width=1),
                            name='MACD'),
                  row=3, col=1)
    
    fig.add_trace(go.Scatter(x=data.index,
                            y=data['Signal_Line'],
                            line=dict(color='orange', width=1),
                            name='Signal Line'),
                  row=3, col=1)

    # Add RSI
    fig.add_trace(go.Scatter(x=data.index, 
                            y=data['RSI'],
                            line=dict(color='purple', width=1),
                            name='RSI'),
                  row=4, col=1)
    
    # Add RSI overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=4, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=4, col=1)

    # Update layout
    fig.update_layout(
        title='Bitcoin (BTC-USD) Technical Analysis',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        height=1200,  # Increase height to accommodate all charts
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        xaxis=dict(
            type="date",
            range=[start_date, end_date],
            autorange=False  # Disable autorange to force our range
        ),
        xaxis2=dict(
            type="date",
            range=[start_date, end_date],
            autorange=False
        ),
        xaxis3=dict(
            type="date",
            range=[start_date, end_date],
            autorange=False
        ),
        xaxis4=dict(
            type="date",
            range=[start_date, end_date],
            autorange=False
        )
    )

    # Update y-axes labels
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="RSI", row=4, col=1)

    # Configure x-axes for all subplots
    for i in range(1, 5):
        fig.update_xaxes(
            type="date",
            showspikes=True,
            spikesnap="cursor",
            spikemode="across",
            spikethickness=1,
            range=[start_date, end_date],  # Set the date range
            autorange=False,  # Disable autorange to force our range
            constrain="domain",  # Constrain the range to the data domain
            row=i, col=1
        )

    # Add range slider and selector to the main price chart
    fig.update_xaxes(
        rangeslider=dict(
            visible=True,
            thickness=0.05,
            bgcolor="#232323",
            yaxis=dict(
                range=[data['Low'].min(), data['High'].max()],  # Set y-axis range for rangeslider
                rangemode="fixed"  # Lock the range
            )
        ),
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1D", step="day", stepmode="backward"),
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=2, label="2Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            font=dict(color="white"),
            bgcolor="#232323",
            activecolor="#f7931a"
        ),
        row=1, col=1
    )

    # Add hover data
    fig.update_layout(
        hoverdistance=100,
        spikedistance=1000,
        hovermode='x unified'
    )

    # Configure additional plot settings
    config = {
        'displayModeBar': True,
        'scrollZoom': False,  # Disable scroll zoom to maintain the selected range
        'showTips': True,
        'responsive': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['select2d', 'lasso2d'],
        'modeBarButtonsToRemove': ['autoScale2d', 'zoomIn2d', 'zoomOut2d']  # Remove zoom buttons
    }

    # Create static directory in the correct location
    static_dir = os.path.join(SCRIPT_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Save the interactive chart as HTML in the static directory
    chart_path = os.path.join(static_dir, 'btc_chart.html')
    
    # Create HTML with proper DOCTYPE and encoding
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <title>Bitcoin Price Chart</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #1a1a1a;
        }}
        .chart-container {{
            width: 100vw;
            height: 100vh;
            margin: 0;
            padding: 0;
        }}
    </style>
    <script>
        // Block source map requests
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {{
            if (url && typeof url === 'string' && url.endsWith('.map')) {{
                return new Promise((resolve) => resolve(new Response('', {{status: 200}})));
            }}
            return originalFetch(url, options);
        }};
        
        // Disable source maps in Plotly
        window.PLOTLYENV = {{
            mapboxAccessToken: undefined,
            PLOTLYJS_SOURCE_MAP: false,
            src: ''
        }};
        
        // Force the chart to respect the selected date range
        window.addEventListener('DOMContentLoaded', function() {{
            var graphDiv = document.querySelector('.js-plotly-plot');
            if (graphDiv) {{
                // Wait for Plotly to be fully initialized
                var checkPlotly = setInterval(function() {{
                    if (graphDiv._fullLayout) {{
                        clearInterval(checkPlotly);
                        var startDate = new Date('{start_date}');
                        var endDate = new Date('{end_date}');
                        
                        // Force relayout with the correct range
                        Plotly.relayout(graphDiv, {{
                            'xaxis.range': [startDate, endDate],
                            'xaxis2.range': [startDate, endDate],
                            'xaxis3.range': [startDate, endDate],
                            'xaxis4.range': [startDate, endDate],
                            'xaxis.autorange': false,
                            'xaxis2.autorange': false,
                            'xaxis3.autorange': false,
                            'xaxis4.autorange': false
                        }}).then(function() {{
                            // Notify parent that chart is ready
                            window.parent.postMessage('chartReady', '*');
                        }});
                    }}
                }}, 50);
            }}
        }});
    </script>
</head>
<body>
    <div class="chart-container">
        {chart_div}
    </div>
</body>
</html>"""

    # Generate the chart HTML with minified scripts and no source maps
    chart_html = fig.to_html(
        full_html=False,
        include_plotlyjs=True,
        config=config,
        default_height='100%',
        include_mathjax=False,
        validate=True
    )

    # Write to file
    with open(chart_path, 'w', encoding='utf-8') as f:
        # Format the template with all values at once
        formatted_html = html_template.format(
            chart_div=chart_html,
            start_date=str(start_date),
            end_date=str(end_date)
        )
        f.write(formatted_html)

    logger.info(f"Chart saved to {chart_path}")

def main():
    # Get BTC data - allow user to specify interval via environment variable
    interval = os.getenv('CHART_INTERVAL', '1d')
    btc_data = get_btc_data(interval=interval)
    
    # Create and save the interactive chart
    create_interactive_chart(btc_data)
    logger.info("Chart has been generated as 'static/btc_chart.html'")

if __name__ == "__main__":
    main() 