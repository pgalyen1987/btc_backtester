import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class Visualizer:
    def __init__(self, data):
        self.data = data

    def create_interactive_chart(self, filename='chart.html'):
        """
        Create an interactive HTML chart using Plotly
        
        Args:
            filename (str): Output HTML file name
        """
        # Create figure with subplots
        fig = make_subplots(rows=4, cols=1,
                           shared_xaxes=True,
                           vertical_spacing=0.05,
                           subplot_titles=('Price & Indicators', 'RSI', 'MACD', 'Volume'),
                           row_heights=[0.4, 0.2, 0.2, 0.2])

        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='OHLC'
            ),
            row=1, col=1
        )

        # Add indicators if they exist in the data
        if 'SMA_20' in self.data.columns:
            fig.add_trace(
                go.Scatter(x=self.data.index, y=self.data['SMA_20'],
                          name='SMA 20', line=dict(color='blue')),
                row=1, col=1
            )

        if 'EMA_20' in self.data.columns:
            fig.add_trace(
                go.Scatter(x=self.data.index, y=self.data['EMA_20'],
                          name='EMA 20', line=dict(color='orange')),
                row=1, col=1
            )

        if all(x in self.data.columns for x in ['BB_UPPER', 'BB_LOWER']):
            fig.add_trace(
                go.Scatter(x=self.data.index, y=self.data['BB_UPPER'],
                          name='BB Upper', line=dict(color='gray', dash='dash')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=self.data.index, y=self.data['BB_LOWER'],
                          name='BB Lower', line=dict(color='gray', dash='dash')),
                row=1, col=1
            )

        # Add RSI
        if 'RSI_14' in self.data.columns:
            fig.add_trace(
                go.Scatter(x=self.data.index, y=self.data['RSI_14'],
                          name='RSI', line=dict(color='purple')),
                row=2, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # Add MACD
        if all(x in self.data.columns for x in ['MACD', 'MACD_SIGNAL']):
            fig.add_trace(
                go.Scatter(x=self.data.index, y=self.data['MACD'],
                          name='MACD', line=dict(color='blue')),
                row=3, col=1
            )
            fig.add_trace(
                go.Scatter(x=self.data.index, y=self.data['MACD_SIGNAL'],
                          name='Signal', line=dict(color='orange')),
                row=3, col=1
            )

        # Add volume
        fig.add_trace(
            go.Bar(x=self.data.index, y=self.data['Volume'], name='Volume'),
            row=4, col=1
        )

        # Update layout
        fig.update_layout(
            title='Technical Analysis Chart',
            yaxis_title='Price (USD)',
            yaxis2_title='RSI',
            yaxis3_title='MACD',
            yaxis4_title='Volume',
            xaxis_rangeslider_visible=False,
            height=1200
        )

        # Save as HTML
        fig.write_html(filename)

    def create_static_chart(self, filename='chart.png'):
        """
        Create a static chart using Matplotlib
        
        Args:
            filename (str): Output PNG file name
        """
        plt.figure(figsize=(12, 16))

        # Price and indicators
        plt.subplot(4, 1, 1)
        plt.plot(self.data.index, self.data['Close'], label='Close Price', color='black', alpha=0.7)
        
        if 'SMA_20' in self.data.columns:
            plt.plot(self.data.index, self.data['SMA_20'], label='SMA 20', color='blue')
        if 'EMA_20' in self.data.columns:
            plt.plot(self.data.index, self.data['EMA_20'], label='EMA 20', color='orange')
        if all(x in self.data.columns for x in ['BB_UPPER', 'BB_LOWER']):
            plt.plot(self.data.index, self.data['BB_UPPER'], label='BB Upper', color='gray', linestyle='--')
            plt.plot(self.data.index, self.data['BB_LOWER'], label='BB Lower', color='gray', linestyle='--')
        
        plt.title('Technical Analysis Chart')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True)

        # RSI
        if 'RSI_14' in self.data.columns:
            plt.subplot(4, 1, 2)
            plt.plot(self.data.index, self.data['RSI_14'], label='RSI', color='purple')
            plt.axhline(y=70, color='r', linestyle='--')
            plt.axhline(y=30, color='g', linestyle='--')
            plt.ylabel('RSI')
            plt.legend()
            plt.grid(True)

        # MACD
        if all(x in self.data.columns for x in ['MACD', 'MACD_SIGNAL']):
            plt.subplot(4, 1, 3)
            plt.plot(self.data.index, self.data['MACD'], label='MACD', color='blue')
            plt.plot(self.data.index, self.data['MACD_SIGNAL'], label='Signal', color='orange')
            plt.ylabel('MACD')
            plt.legend()
            plt.grid(True)

        # Volume
        plt.subplot(4, 1, 4)
        plt.bar(self.data.index, self.data['Volume'], label='Volume', alpha=0.7)
        plt.ylabel('Volume')
        plt.legend()
        plt.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(filename)

    def create_strategy_comparison(self, strategies_results, filename='strategy_comparison.html'):
        """
        Create an interactive comparison chart of different strategies
        
        Args:
            strategies_results (dict): Dictionary of strategy results
            filename (str): Output HTML file name
        """
        fig = make_subplots(rows=2, cols=2,
                           subplot_titles=('Portfolio Value Comparison',
                                         'Cumulative Returns',
                                         'Drawdown Comparison',
                                         'Monthly Returns Distribution'),
                           vertical_spacing=0.15,
                           horizontal_spacing=0.1)

        colors = ['blue', 'red', 'green', 'purple', 'orange']
        
        # Portfolio Value Comparison
        for (name, results), color in zip(strategies_results.items(), colors):
            portfolio = results['portfolio']
            fig.add_trace(
                go.Scatter(x=portfolio.index, y=portfolio['total'],
                          name=f"{name}", line=dict(color=color)),
                row=1, col=1
            )

        # Cumulative Returns
        for (name, results), color in zip(strategies_results.items(), colors):
            portfolio = results['portfolio']
            cum_returns = (1 + portfolio['returns']).cumprod()
            fig.add_trace(
                go.Scatter(x=portfolio.index, y=cum_returns,
                          name=f"{name} Returns", line=dict(color=color)),
                row=1, col=2
            )

        # Drawdown Comparison
        for (name, results), color in zip(strategies_results.items(), colors):
            portfolio = results['portfolio']
            drawdown = portfolio['total'] / portfolio['total'].cummax() - 1
            fig.add_trace(
                go.Scatter(x=portfolio.index, y=drawdown,
                          name=f"{name} Drawdown", line=dict(color=color)),
                row=2, col=1
            )

        # Monthly Returns Distribution
        for (name, results), color in zip(strategies_results.items(), colors):
            portfolio = results['portfolio']
            monthly_returns = portfolio['monthly_returns'].dropna()
            fig.add_trace(
                go.Box(y=monthly_returns, name=name,
                      marker_color=color),
                row=2, col=2
            )

        # Update layout
        fig.update_layout(
            title='Strategy Comparison',
            height=1000,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            )
        )

        # Update axes labels
        fig.update_yaxes(title_text="Portfolio Value", row=1, col=1)
        fig.update_yaxes(title_text="Cumulative Returns", row=1, col=2)
        fig.update_yaxes(title_text="Drawdown", row=2, col=1)
        fig.update_yaxes(title_text="Monthly Returns", row=2, col=2)

        # Save as HTML
        fig.write_html(filename)

    def create_strategy_metrics_comparison(self, strategies_results, filename='strategy_metrics.html'):
        """
        Create an interactive comparison of strategy metrics
        
        Args:
            strategies_results (dict): Dictionary of strategy results
            filename (str): Output HTML file name
        """
        metrics = ['total_return', 'annual_return', 'sharpe_ratio', 'sortino_ratio',
                  'max_drawdown', 'win_rate', 'profit_factor', 'volatility']
        
        fig = go.Figure()
        
        # Create bar charts for each metric
        for metric in metrics:
            values = [results[metric] for results in strategies_results.values()]
            names = list(strategies_results.keys())
            
            # Convert to percentage for certain metrics
            if metric in ['total_return', 'annual_return', 'max_drawdown', 'win_rate']:
                values = [v * 100 for v in values]
            
            fig.add_trace(
                go.Bar(
                    name=metric,
                    x=names,
                    y=values,
                    text=[f"{v:.2f}{'%' if metric in ['total_return', 'annual_return', 'max_drawdown', 'win_rate'] else ''}" 
                          for v in values],
                    textposition='auto',
                )
            )

        # Update layout
        fig.update_layout(
            title='Strategy Metrics Comparison',
            barmode='group',
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            ),
            yaxis_title='Value'
        )

        # Save as HTML
        fig.write_html(filename) 