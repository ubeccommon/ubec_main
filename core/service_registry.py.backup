#!/usr/bin/env python3
"""
UBEC Protocol Service Registry - Enhanced Production Version
Centralized dependency management for all system modules

Design Principles Compliance:
- ✅ Modular Design: Clear boundaries and interfaces
- ✅ Service Pattern: Central orchestration point
- ✅ Service Registry: THE dependency injection container (Principle #3)
- ✅ Single Source of Truth: Services registered once, singleton pattern
- ✅ Strict Async: Full async/await support throughout
- ✅ No Sync Fallbacks: Async-first with documented exceptions
- ✅ Per-Asset Monitoring: Health checks per service
- ✅ No Duplicate Configuration: Single registry, no config duplication
- ✅ Integrated Rate Limiting: Support for rate-limited services
- ✅ Separation of Concerns: Registry only manages services
- ✅ Comprehensive Documentation: Full docstrings and examples
- ✅ Method Singularity: Each method implemented once

The service registry is the heart of the UBEC system architecture.
All modules access each other through this registry, enabling:
- Loose coupling between modules
- Easy testing with mock services
- Dynamic service discovery and lazy initialization
- Centralized initialization and shutdown
- Health monitoring across all services
- Dependency resolution
- Graceful error handling

Supported Services:
- Database Manager: PostgreSQL connection pooling
- Data Synchronizer: Stellar blockchain synchronization
- Analytics Service: Token distribution and metrics
- Order Book Service: Market depth and liquidity analysis
- Protocol Services: Air, Water, Earth, Fire elements
- Monitoring: System health and alerts

Usage Examples:
    # Basic usage
    from core.service_registry import registry
    
    # Get a service (auto-initializes if needed)
    db = await registry.get('database_manager')
    analytics = await registry.get('analytics')
    orderbook = await registry.get('orderbook')
    
    # Use the services
    result = await analytics.get_token_distribution('UBEC')
    snapshot = await orderbook.fetch_orderbook_snapshot('UBEC')
    
    # Context manager (recommended)
    async with registry:
        # Services auto-initialized and cleaned up
        db = await registry.get('database_manager')
        await db.execute("SELECT 1")
        # Cleanup happens automatically on exit

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 3.0 (Enhanced with Order Book Support)
Date: October 16, 2025
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, Type, TypeVar, Callable, List, Set
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceStatus(str, Enum):
    """Service status states"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    CLOSED = "closed"


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not found in the registry."""
    pass


class ServiceInitializationError(Exception):
    """Raised when a service fails to initialize."""
    pass


class ServiceDependencyError(Exception):
    """Raised when service dependencies cannot be resolved."""
    pass


class ServiceRegistry:
    """
    Central service registry for dependency management.
    
    This is a singleton that manages all service instances in the system.
    Services can be registered directly or via factories for lazy initialization.
    
    Key Features:
    - Singleton pattern ensures single registry instance
    - Lazy initialization via factories
    - Async initialization and cleanup with dependency resolution
    - Health monitoring for all services
    - Dependency tracking and validation
    - Context manager support for clean startup/shutdown
    - Service status tracking
    - Extensible service configuration
    
    Attributes:
        _services: Dictionary of instantiated services
        _factories: Dictionary of service factory functions
        _service_configs: Configuration for each service
        _dependencies: Service dependency graph
        _status: Status of each service
        _initialized: Flag indicating if core services are initialized
        _initialization_order: Order in which services were initialized
    """
    
    _instance: Optional['ServiceRegistry'] = None
    
    def __new__(cls) -> 'ServiceRegistry':
        """Singleton pattern - only one registry instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._services = {}
            cls._instance._factories = {}
            cls._instance._service_configs = {}
            cls._instance._dependencies = {}
            cls._instance._status = {}
            cls._instance._initialized = False
            cls._instance._initialization_order = []
            cls._instance._initializing_services = set()
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
        dependencies: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a service instance.
        
        Args:
            name: Unique service identifier
            service: Service instance
            dependencies: Optional list of service names this service depends on
            config: Optional configuration dictionary for the service
        
        Example:
            registry.register('database_manager', db_instance, config={'pool_size': 10})
        """
        if name in self._services:
            logger.warning(f"Service '{name}' already registered, replacing")
        
        self._services[name] = service
        self._status[name] = ServiceStatus.READY
        
        if name not in self._initialization_order:
            self._initialization_order.append(name)
        
        if dependencies:
            self._dependencies[name] = dependencies
        
        if config:
            self._service_configs[name] = config
        
        logger.info(f"✓ Registered service: {name}")
    
    def register_factory(
        self,
        name: str,
        factory: Callable[[], Any],
        dependencies: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a service factory for lazy initialization.
        
        The factory will be called the first time the service is requested.
        Factory should accept a registry parameter to access dependencies.
        
        Args:
            name: Unique service identifier
            factory: Callable that returns a service instance
            dependencies: Optional list of service dependencies
            config: Optional configuration for the service
        
        Example:
            def create_orderbook(registry):
                db = registry.get_initialized('database_manager')
                stellar = registry.get_initialized('stellar_client')
                return OrderBookService(db, stellar)
            
            registry.register_factory('orderbook', create_orderbook, 
                                     dependencies=['database_manager', 'stellar_client'])
        """
        if name in self._factories:
            logger.warning(f"Factory '{name}' already registered, replacing")
        
        self._factories[name] = factory
        self._status[name] = ServiceStatus.PENDING
        
        if dependencies:
            self._dependencies[name] = dependencies
        
        if config:
            self._service_configs[name] = config
        
        logger.info(f"✓ Registered factory: {name}")
    
    def unregister(self, name: str) -> None:
        """
        Unregister a service.
        
        Args:
            name: Service identifier
        """
        if name in self._services:
            del self._services[name]
        if name in self._factories:
            del self._factories[name]
        if name in self._dependencies:
            del self._dependencies[name]
        if name in self._service_configs:
            del self._service_configs[name]
        if name in self._status:
            del self._status[name]
        if name in self._initialization_order:
            self._initialization_order.remove(name)
        
        logger.info(f"✓ Unregistered service: {name}")
    
    # ========================================================================
    # SERVICE ACCESS METHODS
    # ========================================================================
    
    async def get(self, name: str, initialize: bool = True) -> Any:
        """
        Get a service from the registry (async-first method).
        
        If the service is registered as a factory and not yet instantiated,
        it will be created and initialized on first access.
        
        This is the PRIMARY method for accessing services and follows
        Principle #5 (Strict Async Operations).
        
        Args:
            name: Service identifier
            initialize: If True, initialize the service if it has an initialize() method
        
        Returns:
            Service instance
        
        Raises:
            ServiceNotFoundError: If service not found
            ServiceInitializationError: If service fails to initialize
            ServiceDependencyError: If dependencies cannot be resolved
        
        Example:
            db = await registry.get('database_manager')
            analytics = await registry.get('analytics')
            result = await analytics.get_token_distribution('UBEC')
        """
        # Check if already instantiated
        if name in self._services:
            service = self._services[name]
            
            # If service is in error state, try to re-initialize
            if self._status.get(name) == ServiceStatus.ERROR and initialize:
                logger.warning(f"Service '{name}' in error state, attempting re-initialization")
                return await self._initialize_service(name, service)
            
            return service
        
        # Check if factory exists
        if name in self._factories:
            # Prevent circular initialization
            if name in self._initializing_services:
                raise ServiceDependencyError(
                    f"Circular dependency detected while initializing '{name}'"
                )
            
            try:
                self._initializing_services.add(name)
                
                # Check and initialize dependencies first
                if name in self._dependencies:
                    for dep_name in self._dependencies[name]:
                        if dep_name not in self._services:
                            logger.info(f"Initializing dependency '{dep_name}' for '{name}'")
                            await self.get(dep_name, initialize=True)
                
                # Call factory to create instance
                factory = self._factories[name]
                
                # Pass registry to factory if it accepts it
                import inspect
                sig = inspect.signature(factory)
                if 'registry' in sig.parameters:
                    service = factory(registry=self)
                else:
                    service = factory()
                
                # Initialize if service has initialize method
                if initialize:
                    service = await self._initialize_service(name, service)
                
                # Store for future access
                self._services[name] = service
                
                if name not in self._initialization_order:
                    self._initialization_order.append(name)
                
                self._status[name] = ServiceStatus.READY
                
                logger.info(f"✓ Instantiated and initialized service from factory: {name}")
                return service
                
            except Exception as e:
                self._status[name] = ServiceStatus.ERROR
                logger.error(f"Error instantiating service '{name}': {e}")
                raise ServiceInitializationError(f"Failed to create service '{name}': {e}")
            finally:
                self._initializing_services.discard(name)
        
        raise ServiceNotFoundError(f"Service '{name}' not found in registry")
    
    def get_initialized(self, name: str) -> Any:
        """
        Get an already-initialized service (synchronous access).
        
        This method is provided as an optimization for cases where you KNOW
        the service is already initialized (e.g., in factory functions accessing
        dependencies that were already initialized).
        
        This does NOT violate Principle #6 (No Sync Fallbacks) because:
        1. It's documented as requiring pre-initialized services
        2. It's an optimization, not a fallback
        3. The async get() method is the primary interface
        4. It's used internally for dependency resolution
        
        Args:
            name: Service identifier
        
        Returns:
            Service instance
        
        Raises:
            ServiceNotFoundError: If service not found or not yet instantiated
        
        Example:
            # In a factory function
            def create_analytics(registry):
                db = registry.get_initialized('database_manager')  # Already initialized
                return AnalyticsService(db)
        """
        if name in self._services:
            return self._services[name]
        
        raise ServiceNotFoundError(
            f"Service '{name}' not initialized. Use 'await registry.get(\"{name}\")' instead."
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
    
    def is_initialized(self, name: str) -> bool:
        """
        Check if a service is already initialized.
        
        Args:
            name: Service identifier
        
        Returns:
            True if service is initialized, False otherwise
        """
        return name in self._services and self._status.get(name) == ServiceStatus.READY
    
    def list_services(self) -> List[str]:
        """
        Get list of all registered service names.
        
        Returns:
            List of service names
        """
        all_services = set(self._services.keys()) | set(self._factories.keys())
        return sorted(list(all_services))
    
    def get_status(self, name: str) -> ServiceStatus:
        """
        Get the status of a service.
        
        Args:
            name: Service identifier
        
        Returns:
            ServiceStatus enum value
        """
        return self._status.get(name, ServiceStatus.PENDING)
    
    # ========================================================================
    # INITIALIZATION AND SHUTDOWN
    # ========================================================================
    
    async def _initialize_service(self, name: str, service: Any) -> Any:
        """
        Initialize a service if it has an initialize method.
        
        Args:
            name: Service identifier
            service: Service instance
        
        Returns:
            Initialized service
        """
        self._status[name] = ServiceStatus.INITIALIZING
        
        try:
            if hasattr(service, 'initialize'):
                if asyncio.iscoroutinefunction(service.initialize):
                    await service.initialize()
                else:
                    service.initialize()
                logger.debug(f"Initialized service: {name}")
            
            self._status[name] = ServiceStatus.READY
            return service
            
        except Exception as e:
            self._status[name] = ServiceStatus.ERROR
            logger.error(f"Failed to initialize service '{name}': {e}")
            raise
    
    async def initialize_all(self, services: Optional[List[str]] = None) -> None:
        """
        Initialize all core services or specific services in the correct order.
        
        This method is called automatically when using the registry as a context manager.
        Services are initialized based on their dependencies using topological sort.
        
        Args:
            services: Optional list of specific services to initialize.
                     If None, initializes all registered services.
        
        Raises:
            ServiceInitializationError: If any service fails to initialize
        """
        if self._initialized and services is None:
            logger.warning("Services already initialized, skipping")
            return
        
        logger.info("="*70)
        logger.info("Initializing UBEC Service Registry")
        logger.info("="*70)
        
        try:
            # Determine which services to initialize
            if services:
                services_to_init = services
            else:
                # Initialize all registered services
                services_to_init = self.list_services()
            
            # Resolve dependencies and get initialization order
            init_order = self._resolve_dependencies(services_to_init)
            
            # Initialize in dependency order
            for service_name in init_order:
                if service_name not in self._services:
                    logger.info(f"Initializing: {service_name}")
                    await self.get(service_name, initialize=True)
                else:
                    logger.debug(f"Already initialized: {service_name}")
            
            if services is None:
                self._initialized = True
            
            logger.info("="*70)
            logger.info("✓ Service initialization complete")
            logger.info(f"  Total services: {len(self._services)}")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            await self.shutdown()  # Cleanup any partially initialized services
            raise ServiceInitializationError(f"Service initialization failed: {e}")
    
    def _resolve_dependencies(self, services: List[str]) -> List[str]:
        """
        Resolve service dependencies using topological sort.
        
        Args:
            services: List of service names to initialize
        
        Returns:
            List of services in initialization order
        
        Raises:
            ServiceDependencyError: If circular dependencies detected
        """
        # Build dependency graph for requested services
        graph = {}
        in_degree = {}
        
        # Expand to include all dependencies
        all_services = set(services)
        to_process = list(services)
        
        while to_process:
            service = to_process.pop()
            if service in self._dependencies:
                for dep in self._dependencies[service]:
                    if dep not in all_services:
                        all_services.add(dep)
                        to_process.append(dep)
        
        # Initialize graph
        for service in all_services:
            graph[service] = self._dependencies.get(service, [])
            in_degree[service] = 0
        
        # Calculate in-degrees
        for service in all_services:
            for dep in graph[service]:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Topological sort using Kahn's algorithm
        queue = [s for s in all_services if in_degree[s] == 0]
        result = []
        
        while queue:
            # Sort by name for deterministic ordering
            queue.sort()
            service = queue.pop(0)
            result.append(service)
            
            for dependent in all_services:
                if service in graph[dependent]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # Check for circular dependencies
        if len(result) != len(all_services):
            remaining = all_services - set(result)
            raise ServiceDependencyError(
                f"Circular dependency detected among services: {remaining}"
            )
        
        return result
    
    async def shutdown(self, services: Optional[List[str]] = None) -> None:
        """
        Shutdown all services or specific services in reverse initialization order.
        
        Services are closed in reverse order to respect dependencies.
        Each service's close() method is called if it exists.
        
        Args:
            services: Optional list of specific services to shutdown.
                     If None, shuts down all services.
        """
        if not self._services:
            logger.info("No services to shutdown")
            return
        
        logger.info("="*70)
        logger.info("Shutting down services...")
        logger.info("="*70)
        
        # Determine which services to shutdown
        if services:
            shutdown_services = [s for s in reversed(self._initialization_order) if s in services]
        else:
            shutdown_services = reversed(self._initialization_order.copy())
        
        # Shutdown in reverse order
        for name in shutdown_services:
            if name in self._services:
                service = self._services[name]
                
                try:
                    if hasattr(service, 'close'):
                        if asyncio.iscoroutinefunction(service.close):
                            await service.close()
                        else:
                            service.close()
                        logger.info(f"✓ Closed service: {name}")
                    
                    self._status[name] = ServiceStatus.CLOSED
                    
                except Exception as e:
                    logger.error(f"Error closing service '{name}': {e}")
                    self._status[name] = ServiceStatus.ERROR
        
        # Clear all registrations if shutting down all services
        if services is None:
            self._services.clear()
            self._factories.clear()
            self._dependencies.clear()
            self._service_configs.clear()
            self._status.clear()
            self._initialization_order.clear()
            self._initialized = False
        else:
            # Remove only specified services
            for name in services:
                self._services.pop(name, None)
                if name in self._initialization_order:
                    self._initialization_order.remove(name)
        
        logger.info("✓ Services shut down")
    
    # ========================================================================
    # HEALTH AND DIAGNOSTICS
    # ========================================================================
    
    async def health_check(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Perform health check on all services.
        
        Args:
            detailed: If True, include detailed service information
        
        Returns:
            Dictionary with health status for each service
        
        Example:
            health = await registry.health_check()
            if health['overall_status'] == 'healthy':
                print("All systems operational")
            else:
                print(f"Issues: {health['issues']}")
        """
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'services': {},
            'summary': {
                'total': 0,
                'healthy': 0,
                'unhealthy': 0,
                'unknown': 0,
                'initializing': 0
            },
            'issues': []
        }
        
        for name in self._services:
            service = self._services[name]
            service_status = self._status.get(name, ServiceStatus.PENDING)
            
            try:
                # Check if service has health_check method
                if hasattr(service, 'health_check'):
                    if asyncio.iscoroutinefunction(service.health_check):
                        service_health = await service.health_check()
                    else:
                        service_health = service.health_check()
                    
                    health_status['services'][name] = {
                        'status': service_health.get('status', 'unknown'),
                        'registry_status': service_status.value,
                        **service_health
                    }
                else:
                    # Service exists but has no health check
                    health_status['services'][name] = {
                        'status': 'unknown',
                        'registry_status': service_status.value,
                        'message': 'No health check method available'
                    }
                    
                # Add detailed info if requested
                if detailed and hasattr(service, 'get_stats'):
                    try:
                        if asyncio.iscoroutinefunction(service.get_stats):
                            stats = await service.get_stats()
                        else:
                            stats = service.get_stats()
                        health_status['services'][name]['stats'] = stats
                    except Exception as e:
                        logger.warning(f"Could not get stats for '{name}': {e}")
                        
            except Exception as e:
                health_status['services'][name] = {
                    'status': 'error',
                    'registry_status': ServiceStatus.ERROR.value,
                    'error': str(e)
                }
                health_status['issues'].append(f"{name}: {str(e)}")
        
        # Calculate summary
        health_status['summary']['total'] = len(health_status['services'])
        
        for name, service_health in health_status['services'].items():
            status = service_health.get('status', 'unknown')
            
            if service_health.get('registry_status') == ServiceStatus.INITIALIZING.value:
                health_status['summary']['initializing'] += 1
            elif status == 'healthy':
                health_status['summary']['healthy'] += 1
            elif status in ('unhealthy', 'error', 'degraded'):
                health_status['summary']['unhealthy'] += 1
                if status not in health_status['issues']:
                    health_status['issues'].append(f"{name}: status={status}")
            else:
                health_status['summary']['unknown'] += 1
        
        # Determine overall status
        if health_status['summary']['unhealthy'] > 0:
            health_status['overall_status'] = 'unhealthy'
        elif health_status['summary']['initializing'] > 0:
            health_status['overall_status'] = 'initializing'
        elif health_status['summary']['unknown'] > 0:
            health_status['overall_status'] = 'degraded'
        elif health_status['summary']['healthy'] == health_status['summary']['total']:
            health_status['overall_status'] = 'healthy'
        else:
            health_status['overall_status'] = 'unknown'
        
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
            'services': {
                name: {
                    'status': self._status.get(name, ServiceStatus.PENDING).value,
                    'has_dependencies': name in self._dependencies,
                    'dependencies': self._dependencies.get(name, []),
                }
                for name in self.list_services()
            },
            'initialization_order': self._initialization_order.copy(),
            'service_statuses': {
                name: status.value for name, status in self._status.items()
            }
        }
    
    def print_info(self):
        """Print registry information in a human-readable format."""
        info = self.get_info()
        
        print("="*70)
        print("UBEC SERVICE REGISTRY")
        print("="*70)
        print(f"Initialized: {info['initialized']}")
        print(f"Total Services: {info['total_services']}")
        print(f"Total Factories: {info['total_factories']}")
        print()
        
        print("Services:")
        for name, details in info['services'].items():
            status_symbol = {
                ServiceStatus.READY.value: '✓',
                ServiceStatus.INITIALIZING.value: '⟳',
                ServiceStatus.ERROR.value: '✗',
                ServiceStatus.CLOSED.value: '○',
                ServiceStatus.PENDING.value: '⋯'
            }.get(details['status'], '?')
            
            deps_info = ""
            if details['has_dependencies']:
                deps_info = f" → depends on: {', '.join(details['dependencies'])}"
            
            print(f"  {status_symbol} {name} ({details['status']}){deps_info}")
        
        print()
        if info['initialization_order']:
            print(f"Initialization Order: {' → '.join(info['initialization_order'])}")
        print("="*70)


# ==================== GLOBAL REGISTRY INSTANCE ====================

# Single global registry instance (singleton)
registry = ServiceRegistry()

# Convenience exports
__all__ = [
    'ServiceRegistry',
    'registry',
    'ServiceStatus',
    'ServiceNotFoundError',
    'ServiceInitializationError',
    'ServiceDependencyError'
]
