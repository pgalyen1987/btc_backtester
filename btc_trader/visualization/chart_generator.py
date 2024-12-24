import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, Optional

class ChartGenerator:
    @staticmethod
    def create_candlestick_chart(data: pd.DataFrame, title: str = "BTC/USD Price History") -> Dict[str, Any]:
        """
        Create an interactive candlestick chart with volume
        """
        fig = make_subplots(rows=2, cols=1, shared_xaxis=True, 
                           vertical_spacing=0.03, subplot_titles=(title, 'Volume'),
                           row_heights=[0.7, 0.3])

        # Add candlestick
        fig.add_trace(go.Candlestick(x=data.index,
                                    open=data['open'],
                                    high=data['high'],
                                    low=data['low'],
                                    close=data['close'],
                                    name='OHLC'),
                     row=1, col=1)

        # Add volume bar chart
        fig.add_trace(go.Bar(x=data.index,
                            y=data['volume'],
                            name='Volume'),
                     row=2, col=1)

        # Update layout
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=False,
            template='plotly_dark'
        )

        return fig.to_dict()

    @staticmethod
    def create_technical_chart(data: pd.DataFrame, 
                             indicators: Dict[str, pd.Series],
                             title: str = "Technical Analysis") -> Dict[str, Any]:
        """
        Create a technical analysis chart with indicators
        """
        fig = make_subplots(rows=2, cols=1, shared_xaxis=True,
                           vertical_spacing=0.03, subplot_titles=(title, 'Volume'),
                           row_heights=[0.7, 0.3])

        # Add candlestick
        fig.add_trace(go.Candlestick(x=data.index,
                                    open=data['open'],
                                    high=data['high'],
                                    low=data['low'],
                                    close=data['close'],
                                    name='OHLC'),
                     row=1, col=1)

        # Add indicators
        for name, series in indicators.items():
            fig.add_trace(go.Scatter(x=data.index,
                                   y=series,
                                   name=name,
                                   line=dict(width=1)),
                         row=1, col=1)

        # Add volume
        fig.add_trace(go.Bar(x=data.index,
                            y=data['volume'],
                            name='Volume'),
                     row=2, col=1)

        # Update layout
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=800,
            template='plotly_dark'
        )

        return fig.to_dict() 