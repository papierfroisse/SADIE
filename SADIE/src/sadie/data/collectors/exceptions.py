"""
Exceptions spécifiques aux collecteurs de données.
"""

class DataCollectorError(Exception):
    """Classe de base pour les erreurs des collecteurs de données."""
    pass

class APIError(DataCollectorError):
    """Erreur lors de l'appel à une API."""
    
    def __init__(self, source: str, message: str, original_error: Exception = None):
        """
        Initialise l'erreur.
        
        Args:
            source: Source de données concernée
            message: Message d'erreur
            original_error: Exception d'origine (optionnel)
        """
        self.source = source
        self.original_error = original_error
        super().__init__(f"[{source}] {message}")

class RateLimitError(APIError):
    """Erreur de limite de taux d'appels à l'API."""
    pass

class AuthenticationError(APIError):
    """Erreur d'authentification à l'API."""
    pass

class ValidationError(DataCollectorError):
    """Erreur de validation des paramètres."""
    
    def __init__(self, message: str, parameter: str = None):
        """
        Initialise l'erreur.
        
        Args:
            message: Message d'erreur
            parameter: Paramètre concerné (optionnel)
        """
        self.parameter = parameter
        super().__init__(
            f"Erreur de validation{f' pour {parameter}' if parameter else ''}: {message}"
        )

class ConfigurationError(DataCollectorError):
    """Erreur de configuration du collecteur."""
    pass

class DataNotFoundError(DataCollectorError):
    """Erreur lorsque les données demandées ne sont pas trouvées."""
    
    def __init__(self, symbol: str, message: str = None):
        """
        Initialise l'erreur.
        
        Args:
            symbol: Symbole concerné
            message: Message d'erreur additionnel (optionnel)
        """
        self.symbol = symbol
        super().__init__(
            f"Données non trouvées pour {symbol}"
            + (f": {message}" if message else "")
        )

class UnsupportedFeatureError(DataCollectorError):
    """Erreur lorsqu'une fonctionnalité n'est pas supportée."""
    
    def __init__(self, source: str, feature: str):
        """
        Initialise l'erreur.
        
        Args:
            source: Source de données concernée
            feature: Fonctionnalité non supportée
        """
        self.source = source
        self.feature = feature
        super().__init__(
            f"La fonctionnalité '{feature}' n'est pas supportée par {source}"
        )

class ConnectionError(DataCollectorError):
    """Erreur de connexion à l'API."""
    pass

class TimeoutError(DataCollectorError):
    """Erreur de dépassement de délai."""
    pass

class ParsingError(DataCollectorError):
    """Erreur lors du parsing des données."""
    
    def __init__(self, message: str, data: str = None):
        """
        Initialise l'erreur.
        
        Args:
            message: Message d'erreur
            data: Données qui n'ont pas pu être parsées (optionnel)
        """
        self.data = data
        super().__init__(
            f"Erreur de parsing: {message}"
            + (f"\nDonnées: {data}" if data else "")
        ) 