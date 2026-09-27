"""Point d'entrée principal de l'application."""

# Import absolu : `from web.app import app` ne fonctionnait que depuis la racine
# du dépôt (le dossier `sadie/` n'étant pas dans sys.path), et échouait donc dès
# que le paquet était installé ou importé autrement.
from sadie.web.app import app

# L'application sera importée par uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 