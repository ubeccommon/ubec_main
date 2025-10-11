#!/usr/bin/env python3
"""
UBEC Protocol Service Registry - Production Version
Centralized dependency management for all system modules

Design Principles Compliance:
- ✅ Service Registry for Dependencies (Principle #3)
- ✅ Single Source of Truth: Services registered once
- ✅ Strict Async: Full async/await support
- ✅ No Duplicate Configuration: Central service management
- ✅ Comprehensive Documentation: Full docstrings and examples

The service registry is the heart of the UBEC system architecture.
All modules access each other through this registry, enabling:
- Loose coupling between modules
- Easy testing with mock services
- Dynamic service discovery
- Centralized initialization and shutdown
- Health monitoring across all services

Usage Examples:
    # Basic usage
    from core.service_registry import registry
    
    # Get a service
    db = await registry.get('database_manager')
    sync = await registry.get('synchronizer')
    
    # Use the service
    result = await sync.sync_account('GXXX...')
    
    # In main.py (context manager)
    async with registry:
        # Services auto-initialized and cleaned up
        db = await registry.get('database_manager')

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 2.0 (Async Context Manager Support)
Date: October 11, 2025
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, Type, TypeVar, Callable, List
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not found in the registry."""
    pass


class ServiceInitializationError(Exception):
    """Raised when a service fails to initialize."""
    pass


class ServiceRegistry:
    """
    Central service registry for dependency management.
    
    This is a singleton that manages all service instances in the system.
    Services can be registered directly or via factories for lazy initialization.
    
    Key Features:
    - Singleton pattern ensures single registry instance
    - Lazy initialization via factories
    - Async initialization and cleanup
    - Health monitoring for all services
    - Dependency tracking
    - Context manager support for clean startup/shutdown
    
    Attributes:
        _services: Dictionary of instantiated services
        _factories: Dictionary of service factory functions
        _dependencies: Service dependency graph
        _initialized: Flag indicating if core services are initialized
    """
    
    _instance: Optional['ServiceRegistry'] = None
    
    def __new__(cls) -> 'ServiceRegistry':
        """Singleton pattern - only one registry instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._services = {}
            cls._instance._factories = {}
            cls._instance._dependencies = {}
            cls._instance._initialized = False
            cls._instance._initialization_order = []
        return cls._instance
    
    def __init__(self):
        """Initialize registry (only runs once due to singleton)."""
        pass
    
    async def __aenter__(self):
        """Async context manager entry - initialize all services."""
        await self.initialize_all()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup all services."""
        await self.shutdown()
    
    # ========================================================================
    # REGISTRATION METHODS
    # ========================================================================
    
    def register(
        self,
        name: str,
        service: Any,
        dependencies: Optional[List[str]] = None
    ) -> None:
        """
        Register a service instance.
        
        Args:
            name: Unique service identifier
            service: Service instance
            dependencies: Optional list of service names this service depends on
        
        Example:
            registry.register('database_manager', db_instance)
        """
        if name in self._services:
            logger.warning(f"Service '{name}' already registered, replacing")
        
        self._services[name] = service
        self._initialization_order.append(name)
        
        if dependencies:
            self._dependencies[name] = dependencies
        
        logger.info(f"✓ Registered service: {name}")
    
    def register_factory(
        self,
        name: str,
        factory: Callable[[], Any],
        dependencies: Optional[List[str]] = None
    ) -> None:
        """
        Register a service factory for lazy initialization.
        
        The factory will be called the first time the service is requested.
        
        Args:
            name: Unique service identifier
            factory: Callable that returns a service instance
            dependencies: Optional list of service dependencies
        
        Example:
            registry.register_factory('monitor', lambda: AssetMonitor())
        """
        if name in self._factories:
            logger.warning(f"Factory '{name}' already registered, replacing")
        
        self._factories[name] = factory
        
        if dependencies:
            self._dependencies[name] = dependencies
        
        logger.info(f"✓ Registered factory: {name}")
    
    # ========================================================================
    # SERVICE ACCESS METHODS
    # ========================================================================
    
    async def get(self, name: str, initialize: bool = True) -> Any:
        """
        Get a service from the registry.
        
        If the service is registered as a factory and not yet instantiated,
        it will be created on first access.
        
        Args:
            name: Service identifier
            initialize: If True, initialize the service if it has an initialize() method
        
        Returns:
            Service instance
        
        Raises:
            ServiceNotFoundError: If service not found
            ServiceInitializationError: If service fails to initialize
        
        Example:
            db = await registry.get('database_manager')
            result = await db.fetch_all('SELECT * FROM accounts')
        """
        # Check if already instantiated
        if name in self._services:
            return self._services[name]
        
        # Check if factory exists
        if name in self._factories:
            try:
                # Call factory to create instance
                factory = self._factories[name]
                service = factory()
                
                # Initialize if service has initialize method
                if initialize and hasattr(service, 'initialize'):
                    if asyncio.iscoroutinefunction(service.initialize):
                        await service.initialize()
                    else:
                        service.initialize()
                
                # Store for future access
                self._services[name] = service
                self._initialization_order.append(name)
                
                logger.info(f"✓ Instantiated service from factory: {name}")
                return service
                
            except Exception as e:
                logger.error(f"Error instantiating service '{name}': {e}")
                raise ServiceInitializationError(f"Failed to create service '{name}': {e}")
        
        raise ServiceNotFoundError(f"Service '{name}' not found in registry")
    
    def get_sync(self, name: str) -> Any:
        """
        Synchronous get - only returns already-instantiated services.
        Does NOT initialize services. Use for accessing pre-initialized services.
        
        Args:
            name: Service identifier
        
        Returns:
            Service instance
        
        Raises:
            ServiceNotFoundError: If service not found or not yet instantiated
        """
        if name in self._services:
            return self._services[name]
        
        raise ServiceNotFoundError(
            f"Service '{name}' not found. Use async get() to auto-initialize."
        )
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered (either as instance or factory).
        
        Args:
            name: Service identifier
        
        Returns:
            True if service exists, False otherwise
        """
        return name in self._services or name in self._factories
    
    def list_services(self) -> List[str]:
        """
        Get list of all registered service names.
        
        Returns:
            List of service names
        """
        all_services = set(self._services.keys()) | set(self._factories.keys())
        return sorted(list(all_services))
    
    # ========================================================================
    # INITIALIZATION AND SHUTDOWN
    # ========================================================================
    
    async def initialize_all(self) -> None:
        """
        Initialize all core services in the correct order.
        
        This method is called automatically when using the registry as a context manager.
        Services are initialized based on their dependencies.
        
        Order:
        1. Database Manager (no dependencies)
        2. Data Synchronizer (depends on database)
        3. Other services (depend on database and/or synchronizer)
        """
        if self._initialized:
            logger.warning("Services already initialized, skipping")
            return
        
        logger.info("="*70)
        logger.info("Initializing UBEC Service Registry")
        logger.info("="*70)
        
        try:
            # Step 1: Initialize Database Manager (foundation service)
            await self._initialize_database_manager()
            
            # Step 2: Initialize Data Synchronizer (depends on database)
            await self._initialize_data_synchronizer()
            
            # Step 3: Initialize other services as they're added
            # (Future services will be added here)
            
            self._initialized = True
            logger.info("="*70)
            logger.info("✓ All core services initialized successfully")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            await self.shutdown()  # Cleanup any partially initialized services
            raise ServiceInitializationError(f"Service initialization failed: {e}")
    
    async def _initialize_database_manager(self) -> None:
        """Initialize the database manager service."""
        try:
            from core.db.database_manager import AsyncDatabaseManager
            
            # Get database configuration from environment
            # Try UBEC_ prefixed variables first, then fall back to non-prefixed
            db_config = {
                'host': os.getenv('UBEC_DB_HOST', os.getenv('DB_HOST', 'localhost')),
                'port': int(os.getenv('UBEC_DB_PORT', os.getenv('DB_PORT', '5432'))),
                'database': os.getenv('UBEC_DB_NAME', os.getenv('DB_NAME', 'ubec')),
                'schema': os.getenv('UBEC_DB_SCHEMA', os.getenv('DB_SCHEMA', 'ubec_main')),
                'user': os.getenv('UBEC_DB_USER', os.getenv('DB_USER', 'postgres')),
                'password': os.getenv('UBEC_DB_PASSWORD', os.getenv('DB_PASSWORD', '')),
                'min_pool_size': int(os.getenv('UBEC_DB_MIN_POOL', os.getenv('DB_MIN_POOL', '2'))),
                'max_pool_size': int(os.getenv('UBEC_DB_MAX_POOL', os.getenv('DB_MAX_POOL', '10')))
            }
            
            # Create and initialize database manager
            db_manager = AsyncDatabaseManager(**db_config)
            await db_manager.initialize()
            
            self.register('database_manager', db_manager)
            logger.info("✓ Database Manager initialized")
            
        except ImportError:
            logger.error("Cannot import AsyncDatabaseManager - module not found")
            raise
        except Exception as e:
            logger.error(f"Database Manager initialization failed: {e}")
            raise
    
    async def _initialize_data_synchronizer(self) -> None:
        """Initialize the data synchronizer service."""
        try:
            from core.db.ubec_data_synchronizer import UBECDataSynchronizer
            
            # Get database manager (already initialized)
            db_manager = self.get_sync('database_manager')
            
            # Create and initialize synchronizer
            synchronizer = UBECDataSynchronizer(db_manager)
            await synchronizer.initialize()
            
            self.register('synchronizer', synchronizer, dependencies=['database_manager'])
            logger.info("✓ Data Synchronizer initialized")
            
        except ImportError:
            logger.error("Cannot import UBECDataSynchronizer - module not found")
            raise
        except Exception as e:
            logger.error(f"Data Synchronizer initialization failed: {e}")
            raise
    
    async def shutdown(self) -> None:
        """
        Shutdown all services in reverse initialization order.
        
        Services are closed in reverse order to respect dependencies.
        Each service's close() method is called if it exists.
        """
        if not self._services:
            logger.info("No services to shutdown")
            return
        
        logger.info("="*70)
        logger.info("Shutting down services...")
        logger.info("="*70)
        
        # Shutdown in reverse order
        for name in reversed(self._initialization_order):
            if name in self._services:
                service = self._services[name]
                
                try:
                    if hasattr(service, 'close'):
                        if asyncio.iscoroutinefunction(service.close):
                            await service.close()
                        else:
                            service.close()
                        logger.info(f"✓ Closed service: {name}")
                except Exception as e:
                    logger.error(f"Error closing service '{name}': {e}")
        
        # Clear all registrations
        self._services.clear()
        self._factories.clear()
        self._dependencies.clear()
        self._initialization_order.clear()
        self._initialized = False
        
        logger.info("✓ All services shut down")
    
    # ========================================================================
    # HEALTH AND DIAGNOSTICS
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all services.
        
        Returns:
            Dictionary with health status for each service
        
        Example:
            health = await registry.health_check()
            if health['overall_status'] == 'healthy':
                print("All systems operational")
        """
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'services': {},
            'summary': {
                'total': 0,
                'healthy': 0,
                'unhealthy': 0,
                'unknown': 0
            }
        }
        
        for name in self._services:
            service = self._services[name]
            
            try:
                # Check if service has health_check method
                if hasattr(service, 'health_check'):
                    if asyncio.iscoroutinefunction(service.health_check):
                        service_health = await service.health_check()
                    else:
                        service_health = service.health_check()
                    
                    health_status['services'][name] = service_health
                else:
                    # Service exists but has no health check
                    health_status['services'][name] = {
                        'status': 'unknown',
                        'message': 'No health check method available'
                    }
            except Exception as e:
                health_status['services'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Calculate summary
        health_status['summary']['total'] = len(health_status['services'])
        
        for service_health in health_status['services'].values():
            status = service_health.get('status', 'unknown')
            if status == 'healthy':
                health_status['summary']['healthy'] += 1
            elif status in ('unhealthy', 'error', 'degraded'):
                health_status['summary']['unhealthy'] += 1
            else:
                health_status['summary']['unknown'] += 1
        
        # Determine overall status
        if health_status['summary']['unhealthy'] > 0:
            health_status['overall_status'] = 'unhealthy'
        elif health_status['summary']['unknown'] > 0:
            health_status['overall_status'] = 'degraded'
        else:
            health_status['overall_status'] = 'healthy'
        
        return health_status
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get registry information and statistics.
        
        Returns:
            Dictionary with registry metadata
        """
        return {
            'initialized': self._initialized,
            'total_services': len(self._services),
            'total_factories': len(self._factories),
            'services': list(self._services.keys()),
            'factories': list(self._factories.keys()),
            'initialization_order': self._initialization_order.copy(),
            'dependencies': self._dependencies.copy()
        }


# ==================== GLOBAL REGISTRY INSTANCE ====================

# Single global registry instance (singleton)
registry = ServiceRegistry()

# Convenience exports
__all__ = [
    'ServiceRegistry',
    'registry',
    'ServiceNotFoundError',
    'ServiceInitializationError'
]
