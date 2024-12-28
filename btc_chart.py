from pandas import DataFrame
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_btc_data(start="2008-01-01", interval="1d") -> DataFrame:
    """
    Download BTC-USD data from Yahoo Finance
    Args:
        start (str): Start date in YYYY-MM-DD format
        interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    Returns:
        pandas.DataFrame: Historical BTC data
    """
    btc = yf.Ticker("BTC-USD")
    
    end = datetime.now()
    start_date = datetime.strptime(start, "%Y-%m-%d")
    
    try:
        hist = btc.history(start=start_date, end=end, interval=interval)
        if len(hist) == 0:
            print(f"No data available for interval {interval}. Falling back to daily data.")
            hist = btc.history(start=start_date, end=end, interval="1d")
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Falling back to daily data.")
        hist = btc.history(start=start_date, end=end, interval="1d")
    
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
    
    return data

def create_interactive_chart(data):
    """
    Create an interactive candlestick chart using Plotly
    Args:
        data (pandas.DataFrame): Historical BTC data
    """
    # Calculate indicators
    data = calculate_indicators(data)
    
    # Create figure with secondary y-axis
    fig = make_subplots(rows=3, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.05,
                       row_heights=[0.6, 0.2, 0.2])

    # Add candlestick chart
    fig.add_trace(go.Candlestick(x=data.index,
                                open=data['Open'],
                                high=data['High'],
                                low=data['Low'],
                                close=data['Close'],
                                name='BTC-USD'),
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

    # Add RSI
    fig.add_trace(go.Scatter(x=data.index, 
                            y=data['RSI'],
                            line=dict(color='purple', width=1),
                            name='RSI'),
                  row=3, col=1)
    
    # Add RSI overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    # Update layout
    fig.update_layout(
        title='Bitcoin (BTC-USD) Technical Analysis',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        xaxis_rangeslider_visible=False,  # Disable default rangeslider
        height=1000,  # Increase height to accommodate all charts
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    # Update y-axes labels
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)

    # Add buttons for time range selection
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.1,
                showactive=True,
                buttons=list([
                    dict(label="All",
                         method="relayout",
                         args=[{"xaxis.autorange": True}]),
                    dict(label="YTD",
                         method="relayout",
                         args=[{"xaxis.range": [
                             datetime(datetime.now().year, 1, 1).strftime("%Y-%m-%d"),
                             datetime.now().strftime("%Y-%m-%d")
                         ]}]),
                    dict(label="Last Month",
                         method="relayout",
                         args=[{"xaxis.range": [
                             (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                             datetime.now().strftime("%Y-%m-%d")
                         ]}]),
                    dict(label="Last Week",
                         method="relayout",
                         args=[{"xaxis.range": [
                             (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                             datetime.now().strftime("%Y-%m-%d")
                         ]}])
                ]),
            )
        ]
    )

    # Add hover data
    fig.update_layout(
        hoverdistance=100,
        spikedistance=1000,
        hovermode='x unified',
    )

    fig.update_xaxes(
        showspikes=True,
        spikesnap="cursor",
        spikemode="across",
        spikethickness=1
    )

    # Create static directory in the correct location
    static_dir = os.path.join(SCRIPT_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Save the interactive chart as HTML in the static directory
    chart_path = os.path.join(static_dir, 'btc_chart.html')
    fig.write_html(chart_path, include_plotlyjs=True, full_html=True)

def main():
    # Get BTC data from 2008
    btc_data = get_btc_data()
    
    # Create and save the interactive chart
    create_interactive_chart(btc_data)
    print("Chart has been generated as 'static/btc_chart.html'")
    print(f"Data points retrieved: {len(btc_data)}")
    print(f"Date range: from {btc_data.index[0]} to {btc_data.index[-1]}")

if __name__ == "__main__":
    main() 