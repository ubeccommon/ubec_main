# core/service_registry.py
"""
UBEC Protocol Service Registry
Centralized dependency management for all modules

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

from typing import Dict, Any, Optional, Type, TypeVar
import asyncio

from config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class ServiceRegistry:
    """
    Central service registry for dependency management
    
    All inter-module dependencies must go through this registry.
    Enables:
        - Loose coupling between modules
        - Dynamic service discovery
        - Easy testing with mock services
        - Centralized initialization
    
    Usage:
        from core.service_registry import registry
        
        # Get service
        synchronizer = registry.get('synchronizer')
        
        # Use service
        result = await synchronizer.sync_account_data()
    """
    
    _instance: Optional['ServiceRegistry'] = None
    _services: Dict[str, Any] = {}
    _factories: Dict[str, Type] = {}
    
    def __new__(cls) -> 'ServiceRegistry':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, name: str, service: Any) -> None:
        """
        Register a service instance
        
        Args:
            name: Service name
            service: Service instance
        """
        if name in self._services:
            logger.warning(f"Service '{name}' already registered, replacing")
        
        self._services[name] = service
        logger.info(f"Registered service: {name}")
    
    def register_factory(self, name: str, service_class: Type[T]) -> None:
        """
        Register a service factory (lazy initialization)
        
        Args:
            name: Service name
            service_class: Service class to instantiate on first get()
        """
        if name in self._factories:
            logger.warning(f"Factory '{name}' already registered, replacing")
        
        self._factories[name] = service_class
        logger.info(f"Registered factory: {name}")
    
    def get(self, name: str) -> Any:
        """
        Get a service from registry
        
        Args:
            name: Service name
        
        Returns:
            Service instance
        
        Raises:
            KeyError: If service not found
        """
        # Check if already instantiated
        if name in self._services:
            return self._services[name]
        
        # Check if factory exists
        if name in self._factories:
            # Lazy instantiation
            service_class = self._factories[name]
            service = service_class()
            self._services[name] = service
            logger.info(f"Instantiated service from factory: {name}")
            return service
        
        raise KeyError(f"Service '{name}' not found in registry")
    
    def has(self, name: str) -> bool:
        """Check if service exists"""
        return name in self._services or name in self._factories
    
    async def initialize_core_services(self) -> None:
        """
        Initialize all core services
        
        Called once at application startup
        """
        logger.info("Initializing core services...")
        
        # Import services
        from core.db.ubec_data_synchronizer import UBECDataSynchronizer
        from core.holonic.ubec_holonic_evaluator import UBECHolonicEvaluator
        from core.distribution.ubec_distribution_manager import UBECDistributionManager
        from core.audit.audit_system import UBECAuditSystem
        
        # Instantiate and register
        synchronizer = UBECDataSynchronizer()
        await synchronizer.initialize()
        self.register('synchronizer', synchronizer)
        
        evaluator = UBECHolonicEvaluator()
        self.register('evaluator', evaluator)
        
        distribution_mgr = UBECDistributionManager()
        self.register('distribution_manager', distribution_mgr)
        
        audit_system = UBECAuditSystem()
        self.register('audit_system', audit_system)
        
        logger.info("Core services initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all services"""
        logger.info("Shutting down services...")
        
        for name, service in self._services.items():
            if hasattr(service, 'close'):
                try:
                    await service.close()
                    logger.info(f"Closed service: {name}")
                except Exception as e:
                    logger.error(f"Error closing {name}: {e}")
        
        self._services.clear()
        self._factories.clear()
        
        logger.info("All services shut down")


# Global registry instance
registry = ServiceRegistry()
