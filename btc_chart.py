from pandas import DataFrame
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

def get_btc_data(start="2008-01-01", interval="1m") -> DataFrame:
    """
    Download BTC-USD data from Yahoo Finance
    Args:
        start (str): Start date in YYYY-MM-DD format
        interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    Returns:
        pandas.DataFrame: Historical BTC data
    """
    btc = yf.Ticker("BTC-USD")
    
    # Note: Yahoo Finance limits 1m data to last 7 days, so we'll fetch in chunks
    end = datetime.now()
    start_date = datetime.strptime(start, "%Y-%m-%d")
    
    # First try to get all available data
    try:
        hist = btc.history(start=start_date, end=end, interval=interval)
        if len(hist) == 0:
            # If no 1m data available, fall back to daily data
            print("1-minute data not available for the entire range. Falling back to daily data.")
            hist = btc.history(start=start_date, end=end, interval="1d")
    except Exception as e:
        print(f"Error fetching 1-minute data: {e}")
        print("Falling back to daily data.")
        hist = btc.history(start=start_date, end=end, interval="1d")
    
    return hist

def create_interactive_chart(data):
    """
    Create an interactive candlestick chart using Plotly
    Args:
        data (pandas.DataFrame): Historical BTC data
    """
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'])])

    fig.update_layout(
        title='Bitcoin (BTC-USD) Price Chart',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template='plotly_dark',
        xaxis_rangeslider_visible=True  # Add range slider for better navigation
    )

    # Add buttons for time range selection
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=list([
                    dict(label="All",
                         method="relayout",
                         args=[{"xaxis.autorange": True}]),
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

    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    # Save the interactive chart as HTML in the static directory
    fig.write_html('static/btc_chart.html')

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