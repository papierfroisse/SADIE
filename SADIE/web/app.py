"""FastAPI application setup."""
import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .middleware.metrics import setup_metrics
from .routers import trades, analysis, websocket
from ..core.metrics import MEMORY_USAGE, CPU_USAGE
import psutil

logger = logging.getLogger(__name__)

def create_app(
    title: str = "SADIE API",
    description: str = "Système Avancé d'Intelligence et d'Exécution",
    version: str = "0.1.0",
    debug: bool = False
) -> FastAPI:
    """Create FastAPI application.
    
    Args:
        title: Application title
        description: Application description
        version: Application version
        debug: Enable debug mode
        
    Returns:
        FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        debug=debug
    )

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup metrics
    setup_metrics(app)

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Include routers
    app.include_router(trades.router, prefix="/api/v1")
    app.include_router(analysis.router, prefix="/api/v1")
    app.include_router(websocket.router, prefix="/ws")

    @app.on_event("startup")
    async def startup_event():
        """Initialize application on startup."""
        logger.info("Starting SADIE API")
        
        # Start system metrics collection
        start_system_metrics()

    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on application shutdown."""
        logger.info("Shutting down SADIE API")

    return app

def start_system_metrics():
    """Start collecting system metrics."""
    import threading
    import time

    def collect_metrics():
        while True:
            try:
                # Update memory usage
                process = psutil.Process()
                memory_info = process.memory_info()
                MEMORY_USAGE.set(memory_info.rss)

                # Update CPU usage
                cpu_percent = process.cpu_percent(interval=1)
                CPU_USAGE.set(cpu_percent)

                time.sleep(15)  # Collect every 15 seconds
            except Exception as e:
                logger.error(f"Error collecting system metrics: {str(e)}")
                time.sleep(60)  # Wait longer on error

    # Start metrics collection in background thread
    thread = threading.Thread(target=collect_metrics, daemon=True)
    thread.start() 