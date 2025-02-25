"""Tests unitaires pour les tableaux de bord personnalisables."""

import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from fastapi import HTTPException

# Modèles pour les tests
class Widget:
    """Modèle de widget pour les tests."""
    
    def __init__(self, id, title, type, size, metric_type, timeframe, aggregation, position, collector=None, exchange=None, symbol=None):
        self.id = id
        self.title = title
        self.type = type
        self.size = size
        self.collector = collector
        self.exchange = exchange
        self.metricType = metric_type
        self.symbol = symbol
        self.timeframe = timeframe
        self.aggregation = aggregation
        self.position = position
        self.data = None

    def to_dict(self):
        """Convertit le widget en dictionnaire."""
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "size": self.size,
            "collector": self.collector,
            "exchange": self.exchange,
            "metricType": self.metricType,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "aggregation": self.aggregation,
            "position": self.position,
            "data": self.data
        }


class Dashboard:
    """Modèle de tableau de bord pour les tests."""
    
    def __init__(self, id, name, widgets=None, description=None, is_default=False):
        self.id = id
        self.name = name
        self.description = description
        self.widgets = widgets or []
        self.isDefault = is_default

    def to_dict(self):
        """Convertit le tableau de bord en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "widgets": [w.to_dict() for w in self.widgets],
            "isDefault": self.isDefault
        }


@pytest.fixture
def sample_widget():
    """Fixture pour un widget."""
    return Widget(
        id="widget1",
        title="Débit du collecteur",
        type="line",
        size="medium",
        collector="trade_collector",
        exchange="binance",
        metric_type="throughput",
        symbol="BTC/USD",
        timeframe="1h",
        aggregation="avg",
        position={"x": 0, "y": 0}
    )


@pytest.fixture
def sample_dashboard(sample_widget):
    """Fixture pour un tableau de bord."""
    return Dashboard(
        id="dashboard1",
        name="Tableau de bord principal",
        description="Surveillance des performances des collecteurs",
        widgets=[sample_widget],
        is_default=True
    )


@pytest.mark.asyncio
class TestDashboardRoutes:
    """Tests pour les routes de tableaux de bord."""
    
    async def test_get_dashboards(self):
        """Test de récupération des tableaux de bord."""
        # Import des fonctions de routes
        from sadie.web.routes.dashboards import get_dashboards
        
        # Mock de la fonction de base de données
        with patch('sadie.web.routes.dashboards.get_all_dashboards') as mock_get_all:
            # Configuration du mock
            mock_dashboard = Dashboard(
                id="dashboard1",
                name="Tableau de bord principal",
                description="Description du tableau de bord",
                is_default=True
            )
            mock_get_all.return_value = [mock_dashboard.to_dict()]
            
            # Exécution de la fonction
            response = await get_dashboards(current_user=MagicMock())
            
            # Vérifications
            assert response["success"] is True
            assert len(response["dashboards"]) == 1
            assert response["dashboards"][0]["id"] == "dashboard1"
            assert response["dashboards"][0]["name"] == "Tableau de bord principal"
            assert response["dashboards"][0]["isDefault"] is True
    
    async def test_get_dashboard(self):
        """Test de récupération d'un tableau de bord spécifique."""
        # Import des fonctions de routes
        from sadie.web.routes.dashboards import get_dashboard
        
        # Mock de la fonction de base de données
        with patch('sadie.web.routes.dashboards.get_dashboard_by_id') as mock_get_by_id:
            # Configuration du mock pour un tableau de bord existant
            mock_dashboard = Dashboard(
                id="dashboard1",
                name="Tableau de bord principal",
                description="Description du tableau de bord",
                is_default=True
            )
            mock_get_by_id.return_value = mock_dashboard.to_dict()
            
            # Exécution de la fonction
            response = await get_dashboard(
                dashboard_id="dashboard1",
                current_user=MagicMock()
            )
            
            # Vérifications
            assert response["success"] is True
            assert response["dashboard"]["id"] == "dashboard1"
            assert response["dashboard"]["name"] == "Tableau de bord principal"
            
            # Test avec un tableau de bord inexistant
            mock_get_by_id.return_value = None
            
            # La fonction doit lever une exception
            with pytest.raises(HTTPException) as excinfo:
                await get_dashboard(
                    dashboard_id="nonexistent",
                    current_user=MagicMock()
                )
            
            assert excinfo.value.status_code == 404
    
    async def test_create_dashboard(self):
        """Test de création d'un tableau de bord."""
        # Import des fonctions de routes
        from sadie.web.routes.dashboards import create_dashboard
        
        # Mock des fonctions de base de données
        with patch('sadie.web.routes.dashboards.create_new_dashboard') as mock_create:
            # Configuration du mock
            mock_create.return_value = "dashboard1"
            
            # Exécution de la fonction
            dashboard_data = {
                "name": "Nouveau tableau de bord",
                "description": "Description du tableau de bord",
                "widgets": [],
                "isDefault": False
            }
            
            response = await create_dashboard(
                dashboard_data=dashboard_data,
                current_user=MagicMock(is_admin=True)
            )
            
            # Vérifications
            assert response["success"] is True
            assert response["dashboard_id"] == "dashboard1"
            
            # Vérification des paramètres passés à la fonction create_new_dashboard
            mock_create.assert_called_once()
            args = mock_create.call_args[0][0]
            assert args["name"] == "Nouveau tableau de bord"
            assert args["description"] == "Description du tableau de bord"
            assert args["isDefault"] is False
    
    async def test_update_dashboard(self):
        """Test de mise à jour d'un tableau de bord."""
        # Import des fonctions de routes
        from sadie.web.routes.dashboards import update_dashboard
        
        # Mock des fonctions de base de données
        with patch('sadie.web.routes.dashboards.get_dashboard_by_id') as mock_get, \
             patch('sadie.web.routes.dashboards.update_dashboard_by_id') as mock_update:
            
            # Configuration des mocks
            mock_dashboard = Dashboard(
                id="dashboard1",
                name="Tableau de bord principal",
                description="Description initiale",
                is_default=False
            )
            mock_get.return_value = mock_dashboard.to_dict()
            mock_update.return_value = True
            
            # Exécution de la fonction
            dashboard_data = {
                "name": "Tableau de bord mis à jour",
                "description": "Nouvelle description",
                "isDefault": True
            }
            
            response = await update_dashboard(
                dashboard_id="dashboard1",
                dashboard_data=dashboard_data,
                current_user=MagicMock(is_admin=True)
            )
            
            # Vérifications
            assert response["success"] is True
            
            # Vérification des paramètres passés à la fonction update_dashboard_by_id
            mock_update.assert_called_once()
            args = mock_update.call_args[0]
            assert args[0] == "dashboard1"  # dashboard_id
            assert args[1]["name"] == "Tableau de bord mis à jour"
            assert args[1]["description"] == "Nouvelle description"
            assert args[1]["isDefault"] is True
            
            # Test avec un tableau de bord inexistant
            mock_get.return_value = None
            
            with pytest.raises(HTTPException) as excinfo:
                await update_dashboard(
                    dashboard_id="nonexistent",
                    dashboard_data=dashboard_data,
                    current_user=MagicMock(is_admin=True)
                )
            
            assert excinfo.value.status_code == 404
    
    async def test_delete_dashboard(self):
        """Test de suppression d'un tableau de bord."""
        # Import des fonctions de routes
        from sadie.web.routes.dashboards import delete_dashboard
        
        # Mock des fonctions de base de données
        with patch('sadie.web.routes.dashboards.get_dashboard_by_id') as mock_get, \
             patch('sadie.web.routes.dashboards.delete_dashboard_by_id') as mock_delete:
            
            # Configuration des mocks
            mock_dashboard = Dashboard(
                id="dashboard1",
                name="Tableau de bord principal",
                description="Description",
                is_default=False
            )
            mock_get.return_value = mock_dashboard.to_dict()
            mock_delete.return_value = True
            
            # Exécution de la fonction
            response = await delete_dashboard(
                dashboard_id="dashboard1",
                current_user=MagicMock(is_admin=True)
            )
            
            # Vérifications
            assert response["success"] is True
            
            # Vérification des paramètres passés à la fonction delete_dashboard_by_id
            mock_delete.assert_called_once_with("dashboard1")
            
            # Test avec un tableau de bord inexistant
            mock_get.return_value = None
            
            with pytest.raises(HTTPException) as excinfo:
                await delete_dashboard(
                    dashboard_id="nonexistent",
                    current_user=MagicMock(is_admin=True)
                )
            
            assert excinfo.value.status_code == 404
    
    async def test_add_widget(self):
        """Test d'ajout d'un widget à un tableau de bord."""
        # Import des fonctions de routes
        from sadie.web.routes.dashboards import add_widget
        
        # Mock des fonctions de base de données
        with patch('sadie.web.routes.dashboards.get_dashboard_by_id') as mock_get, \
             patch('sadie.web.routes.dashboards.add_widget_to_dashboard') as mock_add:
            
            # Configuration des mocks
            mock_dashboard = Dashboard(
                id="dashboard1",
                name="Tableau de bord principal",
                description="Description",
                widgets=[]
            )
            mock_get.return_value = mock_dashboard.to_dict()
            mock_add.return_value = "widget1"
            
            # Exécution de la fonction
            widget_data = {
                "title": "Nouveau widget",
                "type": "line",
                "size": "medium",
                "collector": "trade_collector",
                "exchange": "binance",
                "metricType": "throughput",
                "symbol": "BTC/USD",
                "timeframe": "1h",
                "aggregation": "avg",
                "position": {"x": 0, "y": 0}
            }
            
            response = await add_widget(
                dashboard_id="dashboard1",
                widget_data=widget_data,
                current_user=MagicMock(is_admin=True)
            )
            
            # Vérifications
            assert response["success"] is True
            assert response["widget_id"] == "widget1"
            
            # Vérification des paramètres passés à la fonction add_widget_to_dashboard
            mock_add.assert_called_once()
            args = mock_add.call_args[0]
            assert args[0] == "dashboard1"  # dashboard_id
            assert args[1]["title"] == "Nouveau widget"
            assert args[1]["type"] == "line"
            assert args[1]["metricType"] == "throughput"
            
            # Test avec un tableau de bord inexistant
            mock_get.return_value = None
            
            with pytest.raises(HTTPException) as excinfo:
                await add_widget(
                    dashboard_id="nonexistent",
                    widget_data=widget_data,
                    current_user=MagicMock(is_admin=True)
                )
            
            assert excinfo.value.status_code == 404
    
    async def test_update_widget(self):
        """Test de mise à jour d'un widget."""
        # Import des fonctions de routes
        from sadie.web.routes.dashboards import update_widget
        
        # Mock des fonctions de base de données
        with patch('sadie.web.routes.dashboards.get_dashboard_by_id') as mock_get, \
             patch('sadie.web.routes.dashboards.update_widget_in_dashboard') as mock_update:
            
            # Configuration des mocks
            widget = Widget(
                id="widget1",
                title="Widget original",
                type="line",
                size="medium",
                collector="trade_collector",
                exchange="binance",
                metric_type="throughput",
                symbol="BTC/USD",
                timeframe="1h",
                aggregation="avg",
                position={"x": 0, "y": 0}
            )
            
            mock_dashboard = Dashboard(
                id="dashboard1",
                name="Tableau de bord principal",
                widgets=[widget]
            )
            
            mock_get.return_value = mock_dashboard.to_dict()
            mock_update.return_value = True
            
            # Exécution de la fonction
            widget_data = {
                "title": "Widget mis à jour",
                "type": "bar",
                "size": "large",
                "position": {"x": 1, "y": 1}
            }
            
            response = await update_widget(
                dashboard_id="dashboard1",
                widget_id="widget1",
                widget_data=widget_data,
                current_user=MagicMock(is_admin=True)
            )
            
            # Vérifications
            assert response["success"] is True
            
            # Vérification des paramètres passés à la fonction update_widget_in_dashboard
            mock_update.assert_called_once()
            args = mock_update.call_args[0]
            assert args[0] == "dashboard1"  # dashboard_id
            assert args[1] == "widget1"  # widget_id
            assert args[2]["title"] == "Widget mis à jour"
            assert args[2]["type"] == "bar"
            assert args[2]["size"] == "large"
            
            # Test avec un tableau de bord inexistant
            mock_get.return_value = None
            
            with pytest.raises(HTTPException) as excinfo:
                await update_widget(
                    dashboard_id="nonexistent",
                    widget_id="widget1",
                    widget_data=widget_data,
                    current_user=MagicMock(is_admin=True)
                )
            
            assert excinfo.value.status_code == 404
    
    async def test_delete_widget(self):
        """Test de suppression d'un widget."""
        # Import des fonctions de routes
        from sadie.web.routes.dashboards import delete_widget
        
        # Mock des fonctions de base de données
        with patch('sadie.web.routes.dashboards.get_dashboard_by_id') as mock_get, \
             patch('sadie.web.routes.dashboards.remove_widget_from_dashboard') as mock_remove:
            
            # Configuration des mocks
            widget = Widget(
                id="widget1",
                title="Widget à supprimer",
                type="line",
                size="medium",
                collector="trade_collector",
                exchange="binance",
                metric_type="throughput",
                symbol="BTC/USD",
                timeframe="1h",
                aggregation="avg",
                position={"x": 0, "y": 0}
            )
            
            mock_dashboard = Dashboard(
                id="dashboard1",
                name="Tableau de bord principal",
                widgets=[widget]
            )
            
            mock_get.return_value = mock_dashboard.to_dict()
            mock_remove.return_value = True
            
            # Exécution de la fonction
            response = await delete_widget(
                dashboard_id="dashboard1",
                widget_id="widget1",
                current_user=MagicMock(is_admin=True)
            )
            
            # Vérifications
            assert response["success"] is True
            
            # Vérification des paramètres passés à la fonction remove_widget_from_dashboard
            mock_remove.assert_called_once_with("dashboard1", "widget1")
            
            # Test avec un tableau de bord inexistant
            mock_get.return_value = None
            
            with pytest.raises(HTTPException) as excinfo:
                await delete_widget(
                    dashboard_id="nonexistent",
                    widget_id="widget1",
                    current_user=MagicMock(is_admin=True)
                )
            
            assert excinfo.value.status_code == 404


@pytest.mark.asyncio
class TestDashboardDataFunctions:
    """Tests pour les fonctions de données des tableaux de bord."""
    
    @patch('sadie.web.routes.dashboards.global_metrics_manager.get_metrics')
    async def test_fetch_widget_data(self, mock_get_metrics):
        """Test de récupération des données pour un widget."""
        # Import des fonctions
        from sadie.web.routes.dashboards import fetch_widget_data
        
        # Configuration du mock
        mock_metric1 = MagicMock()
        mock_metric1.timestamp = datetime(2024, 5, 1, 10, 0, 0)
        mock_metric1.name = "trade_collector"
        mock_metric1.exchange = "binance"
        mock_metric1.metric_type = "throughput"
        mock_metric1.value = 100.5
        mock_metric1.unit = "msg/s"
        mock_metric1.symbols = ["BTC/USD"]
        
        mock_metric2 = MagicMock()
        mock_metric2.timestamp = datetime(2024, 5, 1, 10, 5, 0)
        mock_metric2.name = "trade_collector"
        mock_metric2.exchange = "binance"
        mock_metric2.metric_type = "throughput"
        mock_metric2.value = 110.2
        mock_metric2.unit = "msg/s"
        mock_metric2.symbols = ["BTC/USD"]
        
        mock_get_metrics.return_value = [mock_metric1, mock_metric2]
        
        # Création d'un widget
        widget = Widget(
            id="widget1",
            title="Débit du collecteur",
            type="line",
            size="medium",
            collector="trade_collector",
            exchange="binance",
            metric_type="throughput",
            symbol="BTC/USD",
            timeframe="1h",
            aggregation="avg",
            position={"x": 0, "y": 0}
        )
        
        # Exécution de la fonction
        result = await fetch_widget_data(widget)
        
        # Vérifications
        assert len(result) == 2
        
        assert result[0]["timestamp"] == mock_metric1.timestamp.isoformat()
        assert result[0]["value"] == mock_metric1.value
        assert result[0]["unit"] == mock_metric1.unit
        
        assert result[1]["timestamp"] == mock_metric2.timestamp.isoformat()
        assert result[1]["value"] == mock_metric2.value
        assert result[1]["unit"] == mock_metric2.unit
        
        # Vérification des paramètres passés à get_metrics
        mock_get_metrics.assert_called_once()
        call_args = mock_get_metrics.call_args[1]
        assert call_args["collector_name"] == "trade_collector"
        assert call_args["exchange"] == "binance"
        assert call_args["metric_type"] == "throughput"
        assert call_args["symbol"] == "BTC/USD"
    
    def test_aggregate_widget_data(self):
        """Test d'agrégation des données d'un widget."""
        # Import des fonctions
        from sadie.web.routes.dashboards import aggregate_widget_data
        
        # Création de données de test
        test_data = [
            {"timestamp": "2024-05-01T10:00:00", "value": 100.0, "unit": "msg/s"},
            {"timestamp": "2024-05-01T10:05:00", "value": 110.0, "unit": "msg/s"},
            {"timestamp": "2024-05-01T10:10:00", "value": 90.0, "unit": "msg/s"},
            {"timestamp": "2024-05-01T10:15:00", "value": 120.0, "unit": "msg/s"},
            {"timestamp": "2024-05-01T10:20:00", "value": 100.0, "unit": "msg/s"}
        ]
        
        # Test de l'agrégation moyenne
        avg_result = aggregate_widget_data(test_data, "avg")
        assert avg_result == 104.0
        
        # Test de l'agrégation maximum
        max_result = aggregate_widget_data(test_data, "max")
        assert max_result == 120.0
        
        # Test de l'agrégation minimum
        min_result = aggregate_widget_data(test_data, "min")
        assert min_result == 90.0
        
        # Test de l'agrégation somme
        sum_result = aggregate_widget_data(test_data, "sum")
        assert sum_result == 520.0
        
        # Test de l'agrégation dernière valeur
        last_result = aggregate_widget_data(test_data, "last")
        assert last_result == 100.0
        
        # Test avec une agrégation inconnue (devrait retourner None)
        unknown_result = aggregate_widget_data(test_data, "unknown")
        assert unknown_result is None
        
        # Test avec des données vides
        empty_result = aggregate_widget_data([], "avg")
        assert empty_result is None 