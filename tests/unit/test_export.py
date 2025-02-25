"""Tests unitaires pour l'exportation de données de métriques."""

import json
import csv
import io
from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from fastapi import Response
from fastapi.responses import StreamingResponse

from sadie.web.routes.export import (
    transform_metrics_for_export,
    calculate_start_time,
    generate_export_filename
)


class TestExportFunctions:
    """Tests pour les fonctions d'exportation."""
    
    def test_transform_metrics_for_export(self):
        """Test de la transformation des métriques pour l'exportation."""
        # Création de métriques de test
        mock_metric1 = MagicMock()
        mock_metric1.timestamp = datetime(2024, 5, 1, 10, 0, 0)
        mock_metric1.name = "test_collector"
        mock_metric1.exchange = "binance"
        mock_metric1.metric_type = "throughput"
        mock_metric1.value = 100.5
        mock_metric1.unit = "msg/s"
        mock_metric1.symbols = ["BTC/USD", "ETH/USD"]
        
        mock_metric2 = MagicMock()
        mock_metric2.timestamp = datetime(2024, 5, 1, 10, 1, 0)
        mock_metric2.name = "another_collector"
        mock_metric2.exchange = "kraken"
        mock_metric2.metric_type = "latency"
        mock_metric2.value = 5.2
        mock_metric2.unit = "ms"
        mock_metric2.symbols = ["BTC/EUR"]
        
        metrics = [mock_metric1, mock_metric2]
        
        # Transformation des métriques
        result = transform_metrics_for_export(metrics)
        
        # Vérifications
        assert len(result) == 2
        
        assert result[0]["timestamp"] == "2024-05-01T10:00:00"
        assert result[0]["collector_name"] == "test_collector"
        assert result[0]["exchange"] == "binance"
        assert result[0]["metric_type"] == "throughput"
        assert result[0]["value"] == 100.5
        assert result[0]["unit"] == "msg/s"
        assert result[0]["symbols"] == ["BTC/USD", "ETH/USD"]
        
        assert result[1]["timestamp"] == "2024-05-01T10:01:00"
        assert result[1]["collector_name"] == "another_collector"
        assert result[1]["exchange"] == "kraken"
        assert result[1]["metric_type"] == "latency"
        assert result[1]["value"] == 5.2
        assert result[1]["unit"] == "ms"
        assert result[1]["symbols"] == ["BTC/EUR"]
    
    def test_calculate_start_time(self):
        """Test du calcul de la date de début."""
        now = datetime(2024, 5, 1, 12, 0, 0)
        
        # Tests pour différentes fenêtres temporelles
        result_5m = calculate_start_time("5m", now)
        assert result_5m == datetime(2024, 5, 1, 11, 55, 0)
        
        result_15m = calculate_start_time("15m", now)
        assert result_15m == datetime(2024, 5, 1, 11, 45, 0)
        
        result_1h = calculate_start_time("1h", now)
        assert result_1h == datetime(2024, 5, 1, 11, 0, 0)
        
        result_6h = calculate_start_time("6h", now)
        assert result_6h == datetime(2024, 5, 1, 6, 0, 0)
        
        result_24h = calculate_start_time("24h", now)
        assert result_24h == datetime(2024, 4, 30, 12, 0, 0)
        
        result_7d = calculate_start_time("7d", now)
        assert result_7d == datetime(2024, 4, 24, 12, 0, 0)
        
        # Test pour une fenêtre temporelle invalide (devrait retourner 24h par défaut)
        result_invalid = calculate_start_time("invalid", now)
        assert result_invalid == datetime(2024, 4, 30, 12, 0, 0)
    
    def test_generate_export_filename(self):
        """Test de la génération du nom de fichier d'exportation."""
        # Création d'une date fixe pour le test
        with patch('sadie.web.routes.export.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 5, 1, 12, 30, 15)
            mock_datetime.strftime = datetime.strftime
            
            # Test avec tous les paramètres définis
            filename = generate_export_filename(
                extension="json",
                collector_name="test_collector",
                exchange="binance",
                metric_type="throughput"
            )
            assert filename == "metrics-collector_test_collector-exchange_binance-type_throughput-20240501_123015.json"
            
            # Test avec seulement l'extension
            filename = generate_export_filename(extension="csv")
            assert filename == "metrics-20240501_123015.csv"
            
            # Test avec quelques paramètres
            filename = generate_export_filename(
                extension="json",
                exchange="kraken"
            )
            assert filename == "metrics-exchange_kraken-20240501_123015.json"


@pytest.mark.asyncio
class TestExportEndpoints:
    """Tests pour les endpoints d'exportation."""
    
    @patch('sadie.web.routes.export.global_metrics_manager.get_metrics')
    async def test_export_metrics_json(self, mock_get_metrics):
        """Test de l'exportation des métriques au format JSON."""
        from sadie.web.routes.export import export_metrics_json
        
        # Configuration des mocks
        mock_metric1 = MagicMock()
        mock_metric1.timestamp = datetime(2024, 5, 1, 10, 0, 0)
        mock_metric1.name = "test_collector"
        mock_metric1.exchange = "binance"
        mock_metric1.metric_type = "throughput"
        mock_metric1.value = 100.5
        mock_metric1.unit = "msg/s"
        mock_metric1.symbols = ["BTC/USD", "ETH/USD"]
        
        mock_get_metrics.return_value = [mock_metric1]
        
        # Exécution de la fonction
        response = await export_metrics_json(
            collector_name="test_collector",
            exchange="binance",
            metric_type="throughput",
            symbol="BTC/USD",
            timeframe="1h"
        )
        
        # Vérifications
        assert isinstance(response, Response)
        assert response.headers["Content-Disposition"].startswith("attachment; filename=metrics-collector_test_collector")
        assert response.headers["Content-Disposition"].endswith(".json")
        
        # Vérification du contenu JSON
        content = json.loads(response.body.decode())
        assert len(content) == 1
        assert content[0]["collector_name"] == "test_collector"
        assert content[0]["exchange"] == "binance"
        assert content[0]["metric_type"] == "throughput"
        assert content[0]["value"] == 100.5
    
    @patch('sadie.web.routes.export.global_metrics_manager.get_metrics')
    async def test_export_metrics_csv(self, mock_get_metrics):
        """Test de l'exportation des métriques au format CSV."""
        from sadie.web.routes.export import export_metrics_csv
        
        # Configuration des mocks
        mock_metric1 = MagicMock()
        mock_metric1.timestamp = datetime(2024, 5, 1, 10, 0, 0)
        mock_metric1.name = "test_collector"
        mock_metric1.exchange = "binance"
        mock_metric1.metric_type = "throughput"
        mock_metric1.value = 100.5
        mock_metric1.unit = "msg/s"
        mock_metric1.symbols = ["BTC/USD", "ETH/USD"]
        
        mock_get_metrics.return_value = [mock_metric1]
        
        # Exécution de la fonction
        response = await export_metrics_csv(
            collector_name="test_collector",
            exchange="binance",
            metric_type="throughput",
            symbol=None,
            timeframe="24h"
        )
        
        # Vérifications
        assert isinstance(response, StreamingResponse)
        assert response.headers["Content-Disposition"].startswith("attachment; filename=metrics-collector_test_collector")
        assert response.headers["Content-Disposition"].endswith(".csv")
        
        # Vérification du contenu CSV
        content = "".join([chunk for chunk in response.body_iterator])
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)
        
        # Vérification de l'en-tête
        assert rows[0] == ["timestamp", "collector_name", "exchange", "metric_type", "value", "unit", "symbols"]
        
        # Vérification des données
        assert rows[1][0] == "2024-05-01T10:00:00"
        assert rows[1][1] == "test_collector"
        assert rows[1][2] == "binance"
        assert rows[1][3] == "throughput"
        assert float(rows[1][4]) == 100.5
        assert rows[1][5] == "msg/s"
        assert rows[1][6] == "BTC/USD,ETH/USD" 