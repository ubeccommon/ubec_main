#!/usr/bin/env python3
# core/utils/service_health.py
"""
Service Health Check Utilities
===============================
Reusable health check functionality for all UBEC services.

This module implements Principle #12 (Method Singularity) by providing
shared health check utilities that prevent code duplication across services.

Design Principles:
- ✅ Method Singularity: One implementation for all services
- ✅ Strict Async: All operations use async/await
- ✅ Clear Documentation: Comprehensive docstrings
- ✅ Separation of Concerns: Health logic isolated

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 1.0.0
Date: October 16, 2025
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels for services."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceHealthCheck:
    """
    Base health check implementation for UBEC services.
    
    This class provides reusable health check functionality that can be
    used by all services in the system, following Principle #12 (Method Singularity).
    """
    
    @staticmethod
    async def basic_health_check(
        service_name: str,
        is_initialized: bool = True,
        additional_checks: Optional[List[Callable]] = None,
        include_stats: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a basic health check for a service.
        
        This is the canonical health check implementation used across all services.
        
        Args:
            service_name: Name of the service being checked
            is_initialized: Whether the service has been initialized
            additional_checks: Optional list of async callables that perform additional checks
            include_stats: Whether to include detailed statistics
            **kwargs: Additional context to include in response
        
        Returns:
            Dictionary with health status information:
            {
                'status': 'healthy'|'degraded'|'unhealthy'|'unknown',
                'message': 'Service description',
                'timestamp': 'ISO timestamp',
                'details': {...},
                'stats': {...}  # if include_stats=True
            }
        
        Example:
            async def check_connection():
                return await self.db.test_connection()
            
            health = await ServiceHealthCheck.basic_health_check(
                service_name='my_service',
                is_initialized=self._initialized,
                additional_checks=[check_connection],
                cache_size=len(self._cache)
            )
        """
        health = {
            'status': HealthStatus.HEALTHY.value,
            'message': f"{service_name} operational",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'initialized': is_initialized,
                **kwargs
            }
        }
        
        # Check initialization status
        if not is_initialized:
            health['status'] = HealthStatus.UNHEALTHY.value
            health['message'] = f"{service_name} not initialized"
            return health
        
        # Run additional checks if provided
        if additional_checks:
            check_results = []
            for check in additional_checks:
                try:
                    if asyncio.iscoroutinefunction(check):
                        result = await check()
                    else:
                        result = check()
                    check_results.append(('pass', result))
                except Exception as e:
                    check_results.append(('fail', str(e)))
                    health['status'] = HealthStatus.DEGRADED.value
                    health['message'] = f"{service_name} degraded: {str(e)}"
            
            health['details']['checks'] = check_results
        
        return health
    
    @staticmethod
    async def database_dependent_health(
        service_name: str,
        db_manager: Any,
        is_initialized: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for services that depend on database connectivity.
        
        Args:
            service_name: Name of the service
            db_manager: Database manager instance
            is_initialized: Whether service is initialized
            **kwargs: Additional context
        
        Returns:
            Health status dictionary
        """
        async def check_db():
            """Test database connectivity."""
            if hasattr(db_manager, 'test_connection'):
                return await db_manager.test_connection()
            return True
        
        return await ServiceHealthCheck.basic_health_check(
            service_name=service_name,
            is_initialized=is_initialized,
            additional_checks=[check_db],
            has_database=True,
            **kwargs
        )
    
    @staticmethod
    async def api_dependent_health(
        service_name: str,
        is_initialized: bool = True,
        rate_limiter: Optional[Any] = None,
        cache_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for services that depend on external APIs.
        
        Args:
            service_name: Name of the service
            is_initialized: Whether service is initialized
            rate_limiter: Optional rate limiter instance
            cache_info: Optional cache statistics
            **kwargs: Additional context
        
        Returns:
            Health status dictionary
        """
        details = {}
        
        if rate_limiter:
            details['rate_limiter'] = {
                'calls_per_second': getattr(rate_limiter, 'calls_per_second', 'unknown'),
                'active': True
            }
        
        if cache_info:
            details['cache'] = cache_info
        
        return await ServiceHealthCheck.basic_health_check(
            service_name=service_name,
            is_initialized=is_initialized,
            has_rate_limiter=rate_limiter is not None,
            has_cache=cache_info is not None,
            **details,
            **kwargs
        )
    
    @staticmethod
    def sync_basic_health_check(
        service_name: str,
        is_initialized: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synchronous basic health check for services without async requirements.
        
        Args:
            service_name: Name of the service
            is_initialized: Whether service is initialized
            **kwargs: Additional context
        
        Returns:
            Health status dictionary
        """
        health = {
            'status': HealthStatus.HEALTHY.value if is_initialized else HealthStatus.UNHEALTHY.value,
            'message': f"{service_name} operational" if is_initialized else f"{service_name} not initialized",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'initialized': is_initialized,
                **kwargs
            }
        }
        
        return health


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def create_health_check_method(
    service_name: str,
    check_type: str = 'basic',
    **context
) -> Callable:
    """
    Factory function to create a health check method for a service.
    
    Args:
        service_name: Name of the service
        check_type: Type of health check ('basic', 'database', 'api')
        **context: Context to pass to health check
    
    Returns:
        Async callable that performs health check
    
    Example:
        class MyService:
            def __init__(self):
                self.health_check = create_health_check_method(
                    'my_service',
                    check_type='database',
                    db_manager=self.db
                )
    """
    if check_type == 'database':
        async def health_check():
            return await ServiceHealthCheck.database_dependent_health(
                service_name=service_name,
                **context
            )
    elif check_type == 'api':
        async def health_check():
            return await ServiceHealthCheck.api_dependent_health(
                service_name=service_name,
                **context
            )
    else:
        async def health_check():
            return await ServiceHealthCheck.basic_health_check(
                service_name=service_name,
                **context
            )
    
    return health_check


# ============================================================================
# PUBLIC EXPORTS
# ============================================================================

__all__ = [
    'HealthStatus',
    'ServiceHealthCheck',
    'create_health_check_method'
]
