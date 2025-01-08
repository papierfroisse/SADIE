"""
Exceptions personnalisées pour le package SADIE.
"""

class SADIEError(Exception):
    """Classe de base pour les exceptions SADIE."""
    pass

class SADIEConfigError(SADIEError):
    """Levée quand il y a une erreur de configuration."""
    pass

class SADIEInitError(SADIEError):
    """Levée quand il y a une erreur d'initialisation."""
    pass

class SADIEDataError(SADIEError):
    """Levée quand il y a une erreur liée aux données."""
    pass

class SADIEModelError(SADIEError):
    """Levée quand il y a une erreur liée aux modèles."""
    pass

class SADIEAPIError(SADIEError):
    """Levée quand il y a une erreur d'API."""
    pass

class SADIEDatabaseError(SADIEError):
    """Levée quand il y a une erreur de base de données."""
    pass

class SADIEValidationError(SADIEError):
    """Levée quand il y a une erreur de validation."""
    pass 