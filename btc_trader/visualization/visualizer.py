"""Visualization utilities for backtesting results"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Visualizer:
    """Visualization utilities for backtesting results"""
    
    def __init__(self, data: pd.DataFrame, output_dir: str = "test_results"):
        """Initialize visualizer
        
        Args:
            data: DataFrame with OHLCV data
            output_dir: Directory to save output files
        """
        self.data = data
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Initialized Visualizer with {len(data)} data points")
    
    def _create_unique_filename(self, prefix: str, extension: str) -> str:
        """Create a unique filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def create_interactive_chart(
        self,
        signals: Optional[pd.Series] = None,
        trades: Optional[List[Dict[str, Any]]] = None,
        show_price: bool = True,
        show_volume: bool = True,
        show_volume_ma: bool = False,
        show_indicators: Optional[List[str]] = None
    ) -> str:
        """Create an interactive HTML chart using Plotly
        
        Args:
            signals: Trading signals (-1, 0, 1)
            trades: List of executed trades
            show_price: Whether to show price chart
            show_volume: Whether to show volume
            show_volume_ma: Whether to show volume moving average
            show_indicators: List of indicators to show ('RSI', 'MACD', etc.)
            
        Returns:
            str: Path to the generated HTML file
        """
        try:
            # Determine which components to show
            components = []
            if show_price:
                components.append('price')
            if show_indicators:
                components.extend(show_indicators)
            if show_volume:
                components.append('volume')
            
            # Calculate subplot heights
            heights = []
            for comp in components:
                if comp == 'price':
                    heights.append(0.4)
                elif comp in ['RSI', 'MACD']:
                    heights.append(0.2)
                elif comp == 'volume':
                    heights.append(0.2)
            
            # Create figure with subplots
            fig = make_subplots(
                rows=len(components),
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=[comp.upper() for comp in components],
                row_heights=heights
            )
            
            current_row = 1
            
            # Add price chart
            if show_price:
                fig.add_trace(
                    go.Candlestick(
                        x=self.data.index,
                        open=self.data['Open'],
                        high=self.data['High'],
                        low=self.data['Low'],
                        close=self.data['Close'],
                        name='OHLC'
                    ),
                    row=current_row, col=1
                )
                current_row += 1
            
            # Add indicators
            if show_indicators:
                for indicator in show_indicators:
                    if indicator == 'RSI':
                        fig.add_trace(
                            go.Scatter(
                                x=self.data.index,
                                y=self.data['RSI'],
                                name='RSI',
                                line=dict(color='blue')
                            ),
                            row=current_row, col=1
                        )
                        # Add overbought/oversold lines
                        fig.add_hline(y=70, line_dash="dash", line_color="red",
                                    row=current_row, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color="green",
                                    row=current_row, col=1)
                        current_row += 1
                    
                    elif indicator == 'MACD':
                        # MACD Line
                        fig.add_trace(
                            go.Scatter(
                                x=self.data.index,
                                y=self.data['MACD'],
                                name='MACD',
                                line=dict(color='blue')
                            ),
                            row=current_row, col=1
                        )
                        # Signal Line
                        fig.add_trace(
                            go.Scatter(
                                x=self.data.index,
                                y=self.data['Signal_Line'],
                                name='Signal',
                                line=dict(color='orange')
                            ),
                            row=current_row, col=1
                        )
                        # MACD Histogram
                        colors = ['red' if x < 0 else 'green'
                                for x in (self.data['MACD'] - self.data['Signal_Line'])]
                        fig.add_trace(
                            go.Bar(
                                x=self.data.index,
                                y=self.data['MACD'] - self.data['Signal_Line'],
                                name='MACD Histogram',
                                marker_color=colors
                            ),
                            row=current_row, col=1
                        )
                        current_row += 1
            
            # Add volume
            if show_volume:
                colors = ['red' if x < 0 else 'green'
                         for x in self.data['Close'].diff()]
                fig.add_trace(
                    go.Bar(
                        x=self.data.index,
                        y=self.data['Volume'],
                        name='Volume',
                        marker_color=colors
                    ),
                    row=current_row, col=1
                )
                
                if show_volume_ma:
                    fig.add_trace(
                        go.Scatter(
                            x=self.data.index,
                            y=self.data['Volume_SMA'],
                            name='Volume MA (20)',
                            line=dict(color='blue')
                        ),
                        row=current_row, col=1
                    )
            
            # Add signals if provided
            if signals is not None and show_price:
                buy_signals = self.data[signals == 1].index
                sell_signals = self.data[signals == -1].index
                
                fig.add_trace(
                    go.Scatter(
                        x=buy_signals,
                        y=self.data.loc[buy_signals, 'Low'] * 0.99,
                        name='Buy Signal',
                        mode='markers',
                        marker=dict(symbol='triangle-up', size=10, color='green')
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=sell_signals,
                        y=self.data.loc[sell_signals, 'High'] * 1.01,
                        name='Sell Signal',
                        mode='markers',
                        marker=dict(symbol='triangle-down', size=10, color='red')
                    ),
                    row=1, col=1
                )
            
            # Add trades if provided
            if trades and show_price:
                entry_dates = [pd.to_datetime(t['entry_date']) for t in trades]
                exit_dates = [pd.to_datetime(t['exit_date']) for t in trades]
                entry_prices = [t['entry_price'] for t in trades]
                exit_prices = [t['exit_price'] for t in trades]
                
                fig.add_trace(
                    go.Scatter(
                        x=entry_dates,
                        y=entry_prices,
                        name='Trade Entry',
                        mode='markers',
                        marker=dict(symbol='circle', size=8, color='blue')
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=exit_dates,
                        y=exit_prices,
                        name='Trade Exit',
                        mode='markers',
                        marker=dict(symbol='circle', size=8, color='purple')
                    ),
                    row=1, col=1
                )
            
            # Update layout
            fig.update_layout(
                title='Trading Chart',
                xaxis_rangeslider_visible=False,
                height=800,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            # Save chart
            filename = self._create_unique_filename('chart', 'html')
            filepath = os.path.join(self.output_dir, filename)
            fig.write_html(filepath)
            
            logger.info(f"Created interactive chart: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating interactive chart: {str(e)}")
            raise 