"""Module de visualisation des graphiques."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional

class ChartVisualizer:
    """Création des graphiques interactifs."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialisation du visualiseur.
        
        Args:
            data: DataFrame avec colonnes timestamp, open, high, low, close, volume
        """
        self.data = data
        
    def create_chart(self, 
                    indicators: Optional[Dict] = None,
                    patterns: Optional[List[Dict]] = None) -> Dict:
        """Crée un graphique complet avec bougies et indicateurs.
        
        Args:
            indicators: Dictionnaire des indicateurs à afficher
            patterns: Liste des motifs harmoniques à afficher
            
        Returns:
            Dictionnaire avec les données et la mise en page du graphique
        """
        # Création du graphique principal
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3]
        )
        
        # Ajout des bougies
        fig.add_trace(
            go.Candlestick(
                x=self.data['timestamp'],
                open=self.data['open'],
                high=self.data['high'],
                low=self.data['low'],
                close=self.data['close'],
                name="OHLC"
            ),
            row=1, col=1
        )
        
        # Ajout du volume
        colors = ['red' if row['open'] > row['close'] else 'green'
                 for _, row in self.data.iterrows()]
        
        fig.add_trace(
            go.Bar(
                x=self.data['timestamp'],
                y=self.data['volume'],
                name="Volume",
                marker_color=colors
            ),
            row=2, col=1
        )
        
        # Ajout des indicateurs si présents
        if indicators:
            if 'bollinger_bands' in indicators:
                bb = indicators['bollinger_bands']
                fig.add_trace(
                    go.Scatter(
                        x=self.data['timestamp'],
                        y=bb['upper'],
                        name="BB Upper",
                        line=dict(color='gray', dash='dash')
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=self.data['timestamp'],
                        y=bb['middle'],
                        name="BB Middle",
                        line=dict(color='gray')
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=self.data['timestamp'],
                        y=bb['lower'],
                        name="BB Lower",
                        line=dict(color='gray', dash='dash')
                    ),
                    row=1, col=1
                )
        
        # Mise en page
        fig.update_layout(
            title="Analyse Technique",
            yaxis_title="Prix",
            yaxis2_title="Volume",
            xaxis_rangeslider_visible=False,
            height=800,
            template='plotly_dark'
        )
        
        return {
            'data': fig.data,
            'layout': fig.layout
        }