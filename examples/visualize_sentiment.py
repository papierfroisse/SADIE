"""Script for real-time visualization of sentiment data."""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from sadie.data.collectors.sentiment import (
    get_sentiment_category,
    get_subjectivity_category,
)
from sadie.storage.database import DatabaseManager


class SentimentDashboard:
    """Real-time sentiment visualization dashboard."""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        symbols: List[str],
        update_interval: float = 5.0,
        lookback_hours: int = 24,
    ):
        """Initialize the dashboard.
        
        Args:
            db_manager: Database manager instance
            symbols: List of trading pair symbols to monitor
            update_interval: Data update interval in seconds
            lookback_hours: Hours of historical data to display
        """
        self.db_manager = db_manager
        self.symbols = symbols
        self.update_interval = update_interval
        self.lookback_hours = lookback_hours
        
        # Initialize Dash app
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Set up the dashboard layout."""
        self.app.layout = html.Div([
            # Header
            html.H1(
                "Cryptocurrency Sentiment Analysis",
                style={"textAlign": "center"},
            ),
            
            # Symbol selector
            html.Div([
                html.Label("Select Symbol:"),
                dcc.Dropdown(
                    id="symbol-selector",
                    options=[
                        {"label": symbol, "value": symbol}
                        for symbol in self.symbols
                    ],
                    value=self.symbols[0],
                    clearable=False,
                ),
            ], style={"width": "200px", "margin": "10px"}),
            
            # Time range selector
            html.Div([
                html.Label("Time Range:"),
                dcc.Dropdown(
                    id="timerange-selector",
                    options=[
                        {"label": "1 Hour", "value": 1},
                        {"label": "4 Hours", "value": 4},
                        {"label": "12 Hours", "value": 12},
                        {"label": "24 Hours", "value": 24},
                    ],
                    value=4,
                    clearable=False,
                ),
            ], style={"width": "200px", "margin": "10px"}),
            
            # Main charts
            dcc.Graph(id="sentiment-chart"),
            
            # Statistics cards
            html.Div([
                html.Div([
                    html.H4("Current Sentiment"),
                    html.Div(id="current-sentiment"),
                ], className="stat-card"),
                
                html.Div([
                    html.H4("Tweet Volume"),
                    html.Div(id="tweet-volume"),
                ], className="stat-card"),
                
                html.Div([
                    html.H4("Sentiment Distribution"),
                    html.Div(id="sentiment-distribution"),
                ], className="stat-card"),
            ], style={
                "display": "flex",
                "justifyContent": "space-around",
                "margin": "20px",
            }),
            
            # Update interval
            dcc.Interval(
                id="interval-component",
                interval=self.update_interval * 1000,  # Convert to milliseconds
                n_intervals=0,
            ),
        ])
    
    def setup_callbacks(self):
        """Set up dashboard callbacks."""
        @self.app.callback(
            [
                Output("sentiment-chart", "figure"),
                Output("current-sentiment", "children"),
                Output("tweet-volume", "children"),
                Output("sentiment-distribution", "children"),
            ],
            [
                Input("interval-component", "n_intervals"),
                Input("symbol-selector", "value"),
                Input("timerange-selector", "value"),
            ],
        )
        async def update_charts(n_intervals: int, symbol: str, hours: int):
            """Update dashboard charts and statistics.
            
            Args:
                n_intervals: Number of update intervals
                symbol: Selected trading pair symbol
                hours: Number of hours to display
            
            Returns:
                Updated chart figure and statistics
            """
            # Fetch data
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            data = await self.db_manager.get_sentiment(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
            )
            
            if not data:
                return self.create_empty_chart(), "No data", "No data", "No data"
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df["created_at"] = pd.to_datetime(df["created_at"])
            df.set_index("created_at", inplace=True)
            
            # Resample to minute intervals
            resampled = df.resample("1min").agg({
                "polarity": "mean",
                "subjectivity": "mean",
                "tweet_id": "count",
            }).rename(columns={"tweet_id": "volume"})
            
            # Calculate moving averages
            resampled["polarity_ma"] = resampled["polarity"].rolling(
                window=30,
                min_periods=1,
            ).mean()
            resampled["volume_ma"] = resampled["volume"].rolling(
                window=30,
                min_periods=1,
            ).mean()
            
            # Create chart
            fig = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(
                    f"{symbol} Sentiment",
                    "Tweet Volume",
                ),
            )
            
            # Add sentiment traces
            fig.add_trace(
                go.Scatter(
                    x=resampled.index,
                    y=resampled["polarity"],
                    name="Raw Sentiment",
                    line=dict(color="lightgray"),
                    opacity=0.5,
                ),
                row=1,
                col=1,
            )
            
            fig.add_trace(
                go.Scatter(
                    x=resampled.index,
                    y=resampled["polarity_ma"],
                    name="30min MA",
                    line=dict(color="blue"),
                ),
                row=1,
                col=1,
            )
            
            # Add volume traces
            fig.add_trace(
                go.Bar(
                    x=resampled.index,
                    y=resampled["volume"],
                    name="Volume",
                    marker_color="lightgray",
                    opacity=0.5,
                ),
                row=2,
                col=1,
            )
            
            fig.add_trace(
                go.Scatter(
                    x=resampled.index,
                    y=resampled["volume_ma"],
                    name="Volume MA",
                    line=dict(color="orange"),
                ),
                row=2,
                col=1,
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )
            
            fig.update_yaxes(title_text="Sentiment", row=1, col=1)
            fig.update_yaxes(title_text="Tweets", row=2, col=1)
            
            # Calculate current statistics
            current_sentiment = resampled["polarity_ma"].iloc[-1]
            current_volume = resampled["volume_ma"].iloc[-1]
            
            sentiment_html = html.Div([
                html.P(f"Current: {current_sentiment:.3f}"),
                html.P(f"Category: {get_sentiment_category(current_sentiment)}"),
            ])
            
            volume_html = html.Div([
                html.P(f"Current: {current_volume:.1f} tweets/min"),
                html.P(f"Total: {len(data)} tweets"),
            ])
            
            # Calculate sentiment distribution
            categories = pd.Series([
                get_sentiment_category(record["polarity"])
                for record in data
            ]).value_counts()
            
            distribution_html = html.Div([
                html.P(f"{category}: {count} ({count/len(data)*100:.1f}%)")
                for category, count in categories.items()
            ])
            
            return fig, sentiment_html, volume_html, distribution_html
    
    def create_empty_chart(self) -> go.Figure:
        """Create an empty chart figure.
        
        Returns:
            Empty plotly figure
        """
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(
                "Sentiment",
                "Tweet Volume",
            ),
        )
        
        fig.update_layout(
            height=800,
            showlegend=False,
        )
        
        fig.update_yaxes(title_text="Sentiment", row=1, col=1)
        fig.update_yaxes(title_text="Tweets", row=2, col=1)
        
        return fig
    
    def run(self, host: str = "localhost", port: int = 8050):
        """Run the dashboard server.
        
        Args:
            host: Server host
            port: Server port
        """
        self.app.run_server(
            host=host,
            port=port,
            debug=True,
        )


async def main():
    """Run the sentiment visualization dashboard."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    # Initialize database manager
    db_manager = DatabaseManager(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "sadie"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )
    await db_manager.connect()
    
    try:
        # Create and run dashboard
        dashboard = SentimentDashboard(
            db_manager=db_manager,
            symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
            update_interval=5.0,
            lookback_hours=24,
        )
        
        dashboard.run()
    
    except Exception as e:
        logger.error("Error running dashboard: %s", str(e), exc_info=True)
    
    finally:
        # Clean up
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 