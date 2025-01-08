"""Base collector class for SADIE."""
from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Base class for all data collectors.
    
    This class defines the interface that all collectors must implement.
    It provides basic functionality for:
    - Starting and stopping data collection
    - Managing connection state
    - Error handling and logging
    - Configuration management
    """
    
    def __init__(self):
        """Initialize base collector."""
        self._running = False
        self._config: Dict[str, Any] = {}
        
    @property
    def is_running(self) -> bool:
        """Check if collector is running."""
        return self._running
        
    @property
    def config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()
        
    def configure(self, **kwargs) -> None:
        """Update collector configuration.
        
        Args:
            **kwargs: Configuration key-value pairs
        """
        self._config.update(kwargs)
        logger.debug(f"Updated configuration: {kwargs}")
        
    @abstractmethod
    async def start(self) -> None:
        """Start data collection.
        
        This method must be implemented by all collectors.
        It should initialize any necessary connections and
        start the data collection process.
        
        Raises:
            CollectorError: If start fails
        """
        self._running = True
        
    @abstractmethod
    async def stop(self) -> None:
        """Stop data collection.
        
        This method must be implemented by all collectors.
        It should properly close all connections and clean up
        any resources.
        
        Raises:
            CollectorError: If stop fails
        """
        self._running = False
        
    async def restart(self) -> None:
        """Restart data collection.
        
        This is a convenience method that stops and starts
        the collector. Subclasses can override this if they
        need custom restart behavior.
        
        Raises:
            CollectorError: If restart fails
        """
        await self.stop()
        await self.start()
        
    def validate_config(self, required_keys: Optional[list] = None) -> None:
        """Validate collector configuration.
        
        Args:
            required_keys: List of required configuration keys
            
        Raises:
            CollectorError: If configuration is invalid
        """
        if required_keys:
            missing = [key for key in required_keys if key not in self._config]
            if missing:
                raise ValueError(f"Missing required configuration: {missing}")
                
    async def health_check(self) -> bool:
        """Check collector health.
        
        Returns:
            bool: True if collector is healthy
            
        This is a basic implementation that just checks if
        the collector is running. Subclasses should override
        this to provide more detailed health checks.
        """
        return self.is_running 