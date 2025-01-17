"""Prometheus metrics middleware for FastAPI."""
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, Counter, Histogram

# Web metrics
REQUEST_COUNT = Counter(
    'sadie_http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'sadie_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0)
)

def setup_metrics(app: FastAPI) -> None:
    """Setup Prometheus metrics middleware.
    
    Args:
        app: FastAPI application
    """
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next: Callable) -> Response:
        """Track request metrics.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in chain
            
        Returns:
            FastAPI response
        """
        start_time = time.time()
        
        # Get request method and path for labels
        method = request.method
        endpoint = request.url.path
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # Record error metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=500
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
            
            raise e

    @app.get("/metrics")
    async def metrics() -> Response:
        """Expose Prometheus metrics.
        
        Returns:
            Response with Prometheus metrics
        """
        return Response(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        ) 