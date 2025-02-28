"""
Module d'optimisation des stratégies de trading.

Ce module permet d'optimiser les paramètres des stratégies de trading
pour trouver les combinaisons offrant les meilleures performances.
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Type
import pandas as pd
import numpy as np
from itertools import product
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
from dataclasses import dataclass, field
from pathlib import Path
import json
import joblib
from datetime import datetime

from sadie.core.backtest.strategy import Strategy
from sadie.core.backtest.engine import BacktestEngine, BacktestResult


@dataclass
class OptimizationConfig:
    """Configuration pour l'optimisation d'une stratégie."""
    
    # Paramètres à optimiser avec leurs plages de valeurs
    parameters: Dict[str, List[Any]] = field(default_factory=dict)
    
    # Métrique à optimiser (maximize=True) ou minimiser (maximize=False)
    metric: str = "total_return"
    maximize: bool = True
    
    # Nombre de workers pour le parallélisme
    n_jobs: int = -1  # -1 = tous les cores disponibles
    
    # Utiliser la validation croisée ?
    use_cross_validation: bool = False
    n_splits: int = 5
    
    # Chemin pour sauvegarder les résultats
    save_path: Optional[str] = None
    
    # Fonction d'évaluation personnalisée (si metric n'est pas suffisant)
    custom_eval_func: Optional[Callable[[BacktestResult], float]] = None


@dataclass
class OptimizationResult:
    """Résultat d'une optimisation de stratégie."""
    
    # Les paramètres optimaux trouvés
    best_parameters: Dict[str, Any]
    
    # Résultat du backtest avec les meilleurs paramètres
    best_result: BacktestResult
    
    # Tous les résultats triés par performance (du meilleur au pire)
    all_results: List[Tuple[Dict[str, Any], float]]
    
    # Configuration d'optimisation utilisée
    config: OptimizationConfig
    
    # Métriques calculées
    metric: str
    metric_value: float
    
    # Temps d'exécution en secondes
    execution_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit les résultats en dictionnaire."""
        return {
            "best_parameters": self.best_parameters,
            "best_metrics": self.best_result.metrics.to_dict(),
            "metric_optimized": self.metric,
            "metric_value": float(self.metric_value),
            "execution_time": self.execution_time,
            "top_results": [
                {
                    "parameters": params,
                    "metric_value": float(value)
                }
                for params, value in self.all_results[:10]  # Top 10
            ]
        }
    
    def save(self, file_path: Optional[str] = None) -> str:
        """
        Sauvegarde les résultats d'optimisation.
        
        Args:
            file_path: Chemin où sauvegarder les résultats (optionnel)
            
        Returns:
            str: Chemin où les résultats ont été sauvegardés
        """
        if file_path is None:
            # Utiliser le chemin spécifié dans la configuration ou en créer un par défaut
            file_path = self.config.save_path or f"optimization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Assurer que le répertoire existe
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder au format JSON
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
        
        return file_path
    
    @staticmethod
    def load(file_path: str) -> 'OptimizationResult':
        """
        Charge des résultats d'optimisation depuis un fichier.
        
        Args:
            file_path: Chemin du fichier de résultats
            
        Returns:
            OptimizationResult: Résultats d'optimisation chargés
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Recréer l'objet (partiellement, car certaines données comme best_result ne sont pas sauvegardées)
        result = OptimizationResult(
            best_parameters=data["best_parameters"],
            best_result=None,  # Ne peut pas être chargé depuis JSON
            all_results=[(r["parameters"], r["metric_value"]) for r in data["top_results"]],
            config=None,  # Ne peut pas être chargé complètement depuis JSON
            metric=data["metric_optimized"],
            metric_value=data["metric_value"],
            execution_time=data["execution_time"]
        )
        
        return result


class StrategyOptimizer:
    """Optimiseur de stratégies de trading."""
    
    def __init__(
        self,
        strategy_class: Type[Strategy],
        engine: Optional[BacktestEngine] = None,
        config: Optional[OptimizationConfig] = None
    ):
        """
        Initialise un nouvel optimiseur de stratégies.
        
        Args:
            strategy_class: Classe de la stratégie à optimiser
            engine: Moteur de backtesting (optionnel)
            config: Configuration d'optimisation (optionnel)
        """
        self.strategy_class = strategy_class
        self.engine = engine or BacktestEngine()
        self.config = config or OptimizationConfig()
    
    def optimize(self, data: pd.DataFrame) -> OptimizationResult:
        """
        Optimise les paramètres de la stratégie sur les données fournies.
        
        Args:
            data: Données historiques pour le backtest
            
        Returns:
            OptimizationResult: Résultats de l'optimisation
        """
        start_time = time.time()
        
        # Générer toutes les combinaisons de paramètres
        param_names = list(self.config.parameters.keys())
        param_values = list(self.config.parameters.values())
        param_combinations = list(product(*param_values))
        
        # Fonction d'évaluation
        def evaluate_params(params_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], float, BacktestResult]:
            # Créer une instance de la stratégie avec ces paramètres
            strategy = self.strategy_class(**params_dict)
            
            # Exécuter le backtest
            result = self.engine.run(strategy, data)
            
            # Évaluer la performance selon la métrique choisie
            if self.config.custom_eval_func:
                metric_value = self.config.custom_eval_func(result)
            elif hasattr(result.metrics, self.config.metric):
                metric_value = getattr(result.metrics, self.config.metric)
            else:
                raise ValueError(f"Métrique '{self.config.metric}' non trouvée")
            
            return params_dict, metric_value, result
        
        # Exécuter l'optimisation (en parallèle si n_jobs != 1)
        all_results = []
        
        if self.config.n_jobs == 1:
            # Exécution séquentielle
            for combo in param_combinations:
                params_dict = dict(zip(param_names, combo))
                params_dict, metric_value, result = evaluate_params(params_dict)
                all_results.append((params_dict, metric_value, result))
        else:
            # Exécution parallèle
            n_jobs = self.config.n_jobs if self.config.n_jobs > 0 else None
            with ProcessPoolExecutor(max_workers=n_jobs) as executor:
                # Préparer les futures
                futures = []
                for combo in param_combinations:
                    params_dict = dict(zip(param_names, combo))
                    futures.append(executor.submit(evaluate_params, params_dict))
                
                # Récupérer les résultats au fur et à mesure
                for future in as_completed(futures):
                    params_dict, metric_value, result = future.result()
                    all_results.append((params_dict, metric_value, result))
        
        # Trier les résultats selon la métrique
        all_results.sort(key=lambda x: x[1], reverse=self.config.maximize)
        
        # Extraire les meilleurs paramètres
        best_params, best_metric, best_result = all_results[0]
        
        # Préparer le résultat final
        optimization_result = OptimizationResult(
            best_parameters=best_params,
            best_result=best_result,
            all_results=[(params, metric) for params, metric, _ in all_results],
            config=self.config,
            metric=self.config.metric,
            metric_value=best_metric,
            execution_time=time.time() - start_time
        )
        
        # Sauvegarder les résultats si un chemin est spécifié
        if self.config.save_path:
            optimization_result.save(self.config.save_path)
        
        return optimization_result


def optimize_strategy(
    strategy_class: Type[Strategy],
    data: pd.DataFrame,
    parameters: Dict[str, List[Any]],
    metric: str = "total_return",
    maximize: bool = True,
    n_jobs: int = -1,
    save_path: Optional[str] = None
) -> OptimizationResult:
    """
    Fonction utilitaire pour optimiser une stratégie en une seule ligne.
    
    Args:
        strategy_class: Classe de la stratégie à optimiser
        data: Données historiques pour le backtest
        parameters: Dictionnaire des paramètres à optimiser
        metric: Métrique à optimiser
        maximize: True pour maximiser, False pour minimiser
        n_jobs: Nombre de workers pour le parallélisme
        save_path: Chemin pour sauvegarder les résultats
        
    Returns:
        OptimizationResult: Résultats de l'optimisation
    """
    config = OptimizationConfig(
        parameters=parameters,
        metric=metric,
        maximize=maximize,
        n_jobs=n_jobs,
        save_path=save_path
    )
    
    optimizer = StrategyOptimizer(
        strategy_class=strategy_class,
        config=config
    )
    
    return optimizer.optimize(data) 