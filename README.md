# Bitcoin Price Chart Generator

This module downloads historical Bitcoin (BTC-USD) data using Yahoo Finance and generates an interactive candlestick chart.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script:

```bash
python btc_chart.py
```

This will:
1. Download the last year of Bitcoin price data
2. Generate an interactive HTML chart (`btc_chart.html`)
3. Open the generated HTML file in your web browser to view the interactive chart

## Features

- Interactive candlestick chart
- Dark theme for better visualization
- Zoom and pan capabilities
- Hover tooltips with price information
- Date range selector

## Data Source

Data is fetched from Yahoo Finance using the yfinance package. 