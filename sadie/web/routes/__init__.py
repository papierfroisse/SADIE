"""Points d'entrée HTTP de l'application.

Chaque module de ce dossier expose un `router` FastAPI monté par
`sadie.web.app`. Ce fichier rend le paquet explicite (il était « implicite ») et
évite que `sadie.web.routes` reste une simple coquille sans contenu exposé.
"""

__all__ = ['alerts', 'export', 'metrics', 'prometheus', 'technical']