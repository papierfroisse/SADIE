"""Point d'entrée principal de l'application."""

from web.app import app

# L'application sera importée par uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 