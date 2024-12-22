import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from finta import TA
import pandas as pd

# Download BTC-USD hourly data for the last 30 days (yfinance limitation for hourly data)
btc = yf.Ticker("BTC-USD")
end_date = datetime.now()
start_date = end_date - timedelta(days=30)  # Maximum period for hourly data
btc_data = btc.history(interval='1h', start=start_date, end=end_date)

# Calculate technical indicators
btc_data['SMA_20'] = TA.SMA(btc_data, 20)  # 20-period Simple Moving Average
btc_data['EMA_20'] = TA.EMA(btc_data, 20)  # 20-period Exponential Moving Average
btc_data['RSI'] = TA.RSI(btc_data)  # Relative Strength Index
macd = TA.MACD(btc_data)  # MACD
btc_data['MACD'] = macd['MACD']
btc_data['MACD_SIGNAL'] = macd['SIGNAL']
bbands = TA.BBANDS(btc_data)
btc_data['BB_UPPER'] = bbands['BB_UPPER']
btc_data['BB_MIDDLE'] = bbands['BB_MIDDLE']
btc_data['BB_LOWER'] = bbands['BB_LOWER']

# Create interactive Plotly figure with subplots
fig = make_subplots(rows=4, cols=1, 
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    subplot_titles=('Price & Indicators', 'RSI', 'MACD', 'Volume'),
                    row_heights=[0.4, 0.2, 0.2, 0.2])

# Add candlestick chart
fig.add_trace(
    go.Candlestick(
        x=btc_data.index,
        open=btc_data['Open'],
        high=btc_data['High'],
        low=btc_data['Low'],
        close=btc_data['Close'],
        name='OHLC'
    ),
    row=1, col=1
)

# Add Moving Averages
fig.add_trace(
    go.Scatter(x=btc_data.index, y=btc_data['SMA_20'], name='SMA 20', line=dict(color='blue')),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=btc_data.index, y=btc_data['EMA_20'], name='EMA 20', line=dict(color='orange')),
    row=1, col=1
)

# Add Bollinger Bands
fig.add_trace(
    go.Scatter(x=btc_data.index, y=btc_data['BB_UPPER'], name='BB Upper', line=dict(color='gray', dash='dash')),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=btc_data.index, y=btc_data['BB_LOWER'], name='BB Lower', line=dict(color='gray', dash='dash')),
    row=1, col=1
)

# Add RSI
fig.add_trace(
    go.Scatter(x=btc_data.index, y=btc_data['RSI'], name='RSI', line=dict(color='purple')),
    row=2, col=1
)
# Add RSI overbought/oversold lines
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# Add MACD
fig.add_trace(
    go.Scatter(x=btc_data.index, y=btc_data['MACD'], name='MACD', line=dict(color='blue')),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(x=btc_data.index, y=btc_data['MACD_SIGNAL'], name='Signal', line=dict(color='orange')),
    row=3, col=1
)

# Add volume bar chart
fig.add_trace(
    go.Bar(x=btc_data.index, y=btc_data['Volume'], name='Volume'),
    row=4, col=1
)

# Update layout
fig.update_layout(
    title='Bitcoin Technical Analysis - Hourly Data (Last 30 Days)',
    yaxis_title='Price (USD)',
    yaxis2_title='RSI',
    yaxis3_title='MACD',
    yaxis4_title='Volume',
    xaxis_rangeslider_visible=False,
    height=1200
)

# Update y-axes
fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
fig.update_yaxes(title_text="RSI", row=2, col=1)
fig.update_yaxes(title_text="MACD", row=3, col=1)
fig.update_yaxes(title_text="Volume", row=4, col=1)

# Save as HTML
fig.write_html('btc_analysis.html')
print("Interactive graph has been saved as 'btc_analysis.html'")

# Create and save a static matplotlib version
plt.figure(figsize=(12, 16))

# Price and indicators
plt.subplot(4, 1, 1)
plt.plot(btc_data.index, btc_data['Close'], label='Close Price', color='black', alpha=0.7)
plt.plot(btc_data.index, btc_data['SMA_20'], label='SMA 20', color='blue')
plt.plot(btc_data.index, btc_data['EMA_20'], label='EMA 20', color='orange')
plt.plot(btc_data.index, btc_data['BB_UPPER'], label='BB Upper', color='gray', linestyle='--')
plt.plot(btc_data.index, btc_data['BB_LOWER'], label='BB Lower', color='gray', linestyle='--')
plt.title('Bitcoin Technical Analysis - Hourly Data (Last 30 Days)')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)

# RSI
plt.subplot(4, 1, 2)
plt.plot(btc_data.index, btc_data['RSI'], label='RSI', color='purple')
plt.axhline(y=70, color='r', linestyle='--')
plt.axhline(y=30, color='g', linestyle='--')
plt.ylabel('RSI')
plt.legend()
plt.grid(True)

# MACD
plt.subplot(4, 1, 3)
plt.plot(btc_data.index, btc_data['MACD'], label='MACD', color='blue')
plt.plot(btc_data.index, btc_data['MACD_SIGNAL'], label='Signal', color='orange')
plt.ylabel('MACD')
plt.legend()
plt.grid(True)

# Volume
plt.subplot(4, 1, 4)
plt.bar(btc_data.index, btc_data['Volume'], label='Volume', alpha=0.7)
plt.ylabel('Volume')
plt.legend()
plt.grid(True)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the static plot
plt.savefig('btc_price_history.png')
print("Static graph has been saved as 'btc_price_history.png'") 