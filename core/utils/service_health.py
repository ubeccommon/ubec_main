#!/usr/bin/env python3
# core/utils/service_health.py
"""
UBEC Protocol Suite - Service Health Check Utilities
=====================================================
Reusable health check functionality for all UBEC services.

This module implements Principle #12 (Method Singularity) by providing
shared health check utilities that prevent code duplication across services.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained utility with clear boundaries
    ✅ #2  Service Pattern: Utility module, no standalone execution
    ✅ #3  Service Registry: Used by all registered services
    ✅ #4  Single Source of Truth: Health data from authoritative sources
    ✅ #5  Strict Async: All I/O operations use async/await
    ✅ #6  No Sync Fallbacks: Pure async (with sync option for config-like services)
    ✅ #7  Per-Asset Monitoring: Enables individual service health tracking
    ✅ #8  No Duplicate Config: No configuration in this utility
    ✅ #9  Integrated Rate Limiting: Supports rate limiter health checks
    ✅ #10 Separation of Concerns: Health logic isolated from business logic
    ✅ #11 Comprehensive Documentation: Full docstrings and examples
    ✅ #12 Method Singularity: One implementation for all services
════════════════════════════════════════════════════════════════════════════

Usage Examples:

    # Basic service health check
    from core.utils.service_health import ServiceHealthCheck
    
    class MyService:
        async def health_check(self) -> Dict[str, Any]:
            return await ServiceHealthCheck.basic_health_check(
                service_name='my_service',
                is_initialized=self._initialized,
                cache_size=len(self._cache)
            )
    
    # Database-dependent service
    class DatabaseService:
        async def health_check(self) -> Dict[str, Any]:
            return await ServiceHealthCheck.database_dependent_health(
                service_name='database_service',
                db_manager=self.db,
                is_initialized=self._initialized,
                pool_size=self.db.pool_size
            )
    
    # API-dependent service with rate limiting
    class APIService:
        async def health_check(self) -> Dict[str, Any]:
            return await ServiceHealthCheck.api_dependent_health(
                service_name='api_service',
                is_initialized=self._initialized,
                rate_limiter=self.rate_limiter,
                cache_info={'size': len(self._cache), 'ttl': 300},
                api_connected=await self.test_connection()
            )
    
    # Synchronous service (e.g., config)
    class ConfigService:
        def health_check(self) -> Dict[str, Any]:
            return ServiceHealthCheck.sync_basic_health_check(
                service_name='config',
                is_initialized=True,
                config_loaded=len(self._config) > 0
            )

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 2.0.0
Date: October 17, 2025
Author: UBEC Protocol Team with Claude AI assistance
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List, Union
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# HEALTH STATUS ENUMERATION
# ============================================================================

class HealthStatus(Enum):
    """
    Health status levels for services.
    
    Attributes:
        HEALTHY: Service fully operational with all checks passing
        DEGRADED: Service operational but with some non-critical issues
        UNHEALTHY: Service not operational or critical checks failing
        UNKNOWN: Service status cannot be determined
        INITIALIZING: Service is in the process of starting up
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"


# ============================================================================
# MAIN SERVICE HEALTH CHECK CLASS
# ============================================================================

class ServiceHealthCheck:
    """
    Base health check implementation for UBEC services.
    
    This class provides reusable health check functionality that can be
    used by all services in the system, following Principle #12 (Method Singularity).
    
    The class offers three main patterns:
    1. basic_health_check: For simple services with no external dependencies
    2. database_dependent_health: For services that require database connectivity
    3. api_dependent_health: For services that interact with external APIs
    
    All methods return standardized health status dictionaries for consistency
    across the entire system.
    """
    
    # ========================================================================
    # BASIC HEALTH CHECK (Core Implementation)
    # ========================================================================
    
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
        All other health check methods build upon this foundation.
        
        Args:
            service_name: Name of the service being checked (e.g., 'analytics', 'synchronizer')
            is_initialized: Whether the service has been fully initialized
            additional_checks: Optional list of async/sync callables that perform additional checks
            include_stats: Whether to include detailed statistics (for debugging/monitoring)
            **kwargs: Additional context to include in response (e.g., cache_size, pool_size)
        
        Returns:
            Dictionary with health status information:
            {
                'status': 'healthy'|'degraded'|'unhealthy'|'unknown'|'initializing',
                'message': 'Human-readable status description',
                'timestamp': 'ISO 8601 timestamp of check',
                'details': {
                    'initialized': bool,
                    'checks': [('pass'|'fail', result), ...],  # if additional_checks provided
                    **kwargs  # Any additional context provided
                }
            }
        
        Implementation Notes:
            - Principle #5: Strict async operations
            - Principle #7: Per-Asset monitoring with comprehensive health data
            - Principle #12: Single implementation used by all services
        
        Example:
            async def check_connection():
                return await self.db.test_connection()
            
            async def check_cache():
                return len(self._cache) > 0
            
            health = await ServiceHealthCheck.basic_health_check(
                service_name='my_service',
                is_initialized=self._initialized,
                additional_checks=[check_connection, check_cache],
                cache_size=len(self._cache),
                last_sync=self.last_sync_time.isoformat()
            )
        """
        # Initialize health response structure
        health = {
            'status': HealthStatus.HEALTHY.value,
            'message': f"{service_name} operational",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'initialized': is_initialized,
                **kwargs
            }
        }
        
        # Check initialization status first
        if not is_initialized:
            health['status'] = HealthStatus.UNHEALTHY.value
            health['message'] = f"{service_name} not initialized"
            return health
        
        # Run additional checks if provided
        if additional_checks:
            check_results = []
            failed_checks = 0
            
            for i, check in enumerate(additional_checks):
                try:
                    # Support both async and sync check functions
                    if asyncio.iscoroutinefunction(check):
                        result = await check()
                    else:
                        result = check()
                    
                    check_results.append(('pass', result))
                    logger.debug(f"Health check {i+1} for {service_name}: PASS")
                    
                except Exception as e:
                    failed_checks += 1
                    check_results.append(('fail', str(e)))
                    logger.warning(f"Health check {i+1} for {service_name}: FAIL - {e}")
                    
                    # Determine severity based on failure count
                    if failed_checks == len(additional_checks):
                        # All checks failed - unhealthy
                        health['status'] = HealthStatus.UNHEALTHY.value
                        health['message'] = f"{service_name} unhealthy: all checks failed"
                    else:
                        # Some checks failed - degraded
                        health['status'] = HealthStatus.DEGRADED.value
                        health['message'] = f"{service_name} degraded: {failed_checks}/{len(additional_checks)} checks failed"
            
            health['details']['checks'] = check_results
            health['details']['checks_passed'] = len(additional_checks) - failed_checks
            health['details']['checks_failed'] = failed_checks
        
        return health
    
    # ========================================================================
    # DATABASE-DEPENDENT HEALTH CHECK
    # ========================================================================
    
    @staticmethod
    async def database_dependent_health(
        service_name: str,
        db_manager: Any,
        is_initialized: bool = True,
        additional_checks: Optional[List[Callable]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for services that depend on database connectivity.
        
        This method automatically includes database connectivity checks in addition
        to any service-specific checks provided.
        
        Args:
            service_name: Name of the service (e.g., 'synchronizer', 'analytics')
            db_manager: Database manager instance with connection capabilities
            is_initialized: Whether service is initialized
            additional_checks: Optional list of additional async/sync checks beyond DB
            **kwargs: Additional context (e.g., query_count, last_sync)
        
        Returns:
            Health status dictionary with database-specific details
        
        Implementation Notes:
            - Automatically tests database connectivity
            - Measures database response time
            - Reports connection pool status if available
            - Principle #4: Database as single source of truth
            - Principle #7: Per-Asset monitoring with DB metrics
        
        Example:
            class SynchronizerService:
                async def health_check(self) -> Dict[str, Any]:
                    async def check_sync_lag():
                        lag = await self.calculate_sync_lag()
                        if lag > 100:
                            raise Exception(f"Sync lag too high: {lag} ledgers")
                        return lag
                    
                    return await ServiceHealthCheck.database_dependent_health(
                        service_name='synchronizer',
                        db_manager=self.db,
                        is_initialized=self._initialized,
                        additional_checks=[check_sync_lag],
                        accounts_tracked=await self.get_account_count(),
                        last_sync=self.last_sync_time.isoformat()
                    )
        """
        async def check_db_connection():
            """Test database connectivity and measure response time."""
            start_time = datetime.now()
            
            try:
                # Try to use test_connection if available
                if hasattr(db_manager, 'test_connection'):
                    result = await db_manager.test_connection()
                # Try to use health_check if available
                elif hasattr(db_manager, 'health_check'):
                    db_health = await db_manager.health_check()
                    result = db_health.get('status') == 'healthy'
                # Fallback: try simple query
                elif hasattr(db_manager, 'execute_query'):
                    await db_manager.execute_query("SELECT 1")
                    result = True
                else:
                    logger.warning(f"Database manager for {service_name} has no standard health check method")
                    result = True  # Assume healthy if we can't check
                
                # Calculate response time
                end_time = datetime.now()
                response_time_ms = (end_time - start_time).total_seconds() * 1000
                
                # Add response time to result
                if isinstance(result, dict):
                    result['response_time_ms'] = round(response_time_ms, 2)
                
                return result
                
            except Exception as e:
                logger.error(f"Database health check failed for {service_name}: {e}")
                raise
        
        # Build check list
        all_checks = [check_db_connection]
        if additional_checks:
            all_checks.extend(additional_checks)
        
        # Add database-specific details
        db_details = {
            'has_database': True,
            **kwargs
        }
        
        # Try to get pool information if available
        if hasattr(db_manager, '_pool') and db_manager._pool:
            try:
                db_details['pool_size'] = db_manager._pool.get_size()
                db_details['pool_max'] = getattr(db_manager, 'max_pool_size', 'unknown')
            except Exception:
                pass  # Pool info not critical
        
        return await ServiceHealthCheck.basic_health_check(
            service_name=service_name,
            is_initialized=is_initialized,
            additional_checks=all_checks,
            **db_details
        )
    
    # ========================================================================
    # API-DEPENDENT HEALTH CHECK
    # ========================================================================
    
    @staticmethod
    async def api_dependent_health(
        service_name: str,
        is_initialized: bool = True,
        rate_limiter: Optional[Any] = None,
        cache_info: Optional[Dict[str, Any]] = None,
        additional_checks: Optional[List[Callable]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for services that depend on external APIs.
        
        This method includes checks for rate limiting, caching, and API connectivity
        in addition to any service-specific checks.
        
        Args:
            service_name: Name of the service (e.g., 'stellar_client', 'orderbook')
            is_initialized: Whether service is initialized
            rate_limiter: Optional rate limiter instance for API calls
            cache_info: Optional cache statistics dictionary
            additional_checks: Optional list of additional async/sync checks
            **kwargs: Additional context (e.g., api_connected, last_request_time)
        
        Returns:
            Health status dictionary with API-specific details
        
        Implementation Notes:
            - Reports rate limiter status and configuration
            - Includes cache metrics if caching is used
            - Supports additional API connectivity checks
            - Principle #9: Integrated rate limiting with health monitoring
            - Principle #7: Per-Asset monitoring with API metrics
        
        Example:
            class StellarClientService:
                async def health_check(self) -> Dict[str, Any]:
                    async def check_horizon_api():
                        try:
                            await self.server.fetch_base_fee()
                            return True
                        except Exception as e:
                            raise Exception(f"Horizon API unreachable: {e}")
                    
                    return await ServiceHealthCheck.api_dependent_health(
                        service_name='stellar_client',
                        is_initialized=self._initialized,
                        rate_limiter=self.rate_limiter,
                        cache_info={
                            'size': len(self._cache),
                            'ttl': self.cache_ttl,
                            'hit_rate': self.cache_hit_rate
                        },
                        additional_checks=[check_horizon_api],
                        horizon_url=self.horizon_url,
                        network=self.network
                    )
        """
        api_details = {
            'has_api': True,
            **kwargs
        }
        
        # Add rate limiter information
        if rate_limiter:
            api_details['rate_limiter'] = {
                'active': True,
                'calls_per_second': getattr(rate_limiter, 'calls_per_second', 'unknown'),
                'max_calls': getattr(rate_limiter, 'max_calls', 'unknown'),
                'window_seconds': getattr(rate_limiter, 'window_seconds', 'unknown')
            }
            api_details['has_rate_limiter'] = True
        else:
            api_details['has_rate_limiter'] = False
        
        # Add cache information
        if cache_info:
            api_details['cache'] = cache_info
            api_details['has_cache'] = True
        else:
            api_details['has_cache'] = False
        
        return await ServiceHealthCheck.basic_health_check(
            service_name=service_name,
            is_initialized=is_initialized,
            additional_checks=additional_checks,
            **api_details
        )
    
    # ========================================================================
    # ELEMENT PROTOCOL HEALTH CHECK
    # ========================================================================
    
    @staticmethod
    async def element_protocol_health(
        element_name: str,
        token_code: str,
        db_manager: Any,
        is_initialized: bool = True,
        last_sync: Optional[datetime] = None,
        cached_accounts: int = 0,
        additional_checks: Optional[List[Callable]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check specifically for UBEC element protocols (Air, Water, Earth, Fire).
        
        This specialized health check includes element-specific metrics like sync
        freshness, account tracking, and Ubuntu principle alignment.
        
        Args:
            element_name: Name of element ('air', 'water', 'earth', 'fire')
            token_code: Token code ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
            db_manager: Database manager instance
            is_initialized: Whether protocol is initialized
            last_sync: Timestamp of last successful sync operation
            cached_accounts: Number of accounts in memory cache
            additional_checks: Optional list of element-specific checks
            **kwargs: Additional element-specific context
        
        Returns:
            Health status dictionary with element protocol details
        
        Implementation Notes:
            - Checks data freshness (warns if sync > 30 minutes old)
            - Reports cache status
            - Includes Ubuntu principle alignment if available
            - Principle #7: Per-Asset monitoring for each element
        
        Example:
            class UBECttProtocol:  # Fire Element
                async def health_check(self) -> Dict[str, Any]:
                    async def check_transformation_metrics():
                        count = await self.db.execute_query(
                            "SELECT COUNT(*) FROM transformation_actions WHERE verified = true"
                        )
                        return count > 0
                    
                    return await ServiceHealthCheck.element_protocol_health(
                        element_name='fire',
                        token_code='UBECtt',
                        db_manager=self.db,
                        is_initialized=self._initialized,
                        last_sync=self.last_sync_time,
                        cached_accounts=len(self._account_cache),
                        additional_checks=[check_transformation_metrics],
                        ubuntu_principle='regeneration',
                        verified_transformations=await self.get_verified_count()
                    )
        """
        async def check_sync_freshness():
            """Check if data sync is recent enough."""
            if last_sync is None:
                raise Exception("Never synchronized")
            
            time_since_sync = (datetime.now() - last_sync).total_seconds()
            
            # Warn if sync is older than 30 minutes
            if time_since_sync > 1800:
                raise Exception(f"Data stale: {time_since_sync/60:.1f} minutes since last sync")
            
            return time_since_sync
        
        # Build check list
        all_checks = [check_sync_freshness]
        if additional_checks:
            all_checks.extend(additional_checks)
        
        # Element-specific details
        element_details = {
            'element': element_name,
            'token_code': token_code,
            'last_sync': last_sync.isoformat() if last_sync else None,
            'cached_accounts': cached_accounts,
            'data_fresh': last_sync is not None,
            **kwargs
        }
        
        return await ServiceHealthCheck.database_dependent_health(
            service_name=f'{element_name}_protocol',
            db_manager=db_manager,
            is_initialized=is_initialized,
            additional_checks=all_checks,
            **element_details
        )
    
    # ========================================================================
    # STELLAR CLIENT HEALTH CHECK
    # ========================================================================
    
    @staticmethod
    async def stellar_client_health(
        client: Any,
        horizon_url: str,
        initialized: bool,
        request_count: int = 0,
        error_count: int = 0,
        last_error: Optional[str] = None,
        last_error_time: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for Stellar client service.
        
        Tests connectivity to Stellar Horizon API and tracks request/error metrics.
        Follows Principle #7 (Per-Asset Monitoring) with execution minimums.
        
        Args:
            client: StellarClientService instance
            horizon_url: Horizon server URL
            initialized: Whether client is initialized
            request_count: Total API requests made
            error_count: Total errors encountered
            last_error: Most recent error message
            last_error_time: Timestamp of last error
            **kwargs: Additional context
        
        Returns:
            Health status dictionary
        
        Example:
            return await ServiceHealthCheck.stellar_client_health(
                client=self,
                horizon_url=self.horizon_url,
                initialized=self._initialized,
                request_count=self._request_count,
                error_count=self._error_count,
                last_error=self._last_error,
                last_error_time=self._last_error_time
            )
        """
        import time
        
        checks = []
        details = {
            'initialized': initialized,
            'horizon_url': horizon_url,
            'request_count': request_count,
            'error_count': error_count,
            'last_error': last_error,
            'last_error_time': last_error_time,
            **kwargs
        }
        
        # Check 1: Initialization
        if not initialized:
            checks.append(('fail', 'Client not initialized'))
            return {
                'status': 'unhealthy',
                'message': 'Stellar client not initialized',
                'details': details,
                'checks': checks
            }
        
        checks.append(('pass', 'Client initialized'))
        
        # Check 2: Connectivity test
        try:
            start = time.time()
            response = await client._client.root().call()
            elapsed_ms = (time.time() - start) * 1000
            
            details['response_time_ms'] = round(elapsed_ms, 2)
            details['network_passphrase'] = response.get('network_passphrase', 'unknown')
            details['horizon_version'] = response.get('horizon_version', 'unknown')
            details['core_version'] = response.get('core_version', 'unknown')
            details['protocol_version'] = response.get('current_protocol_version', 'unknown')
            
            checks.append(('pass', f'Horizon API accessible ({elapsed_ms:.1f}ms)'))
            
        except Exception as e:
            checks.append(('fail', f'Horizon API unreachable: {str(e)}'))
            details['connection_error'] = str(e)
            
            return {
                'status': 'unhealthy',
                'message': f'Stellar API connection failed: {str(e)}',
                'details': details,
                'checks': checks,
                'timestamp': datetime.now().isoformat()
            }
        
        # Check 3: Error rate
        if request_count > 0:
            error_rate = error_count / request_count
            details['error_rate'] = round(error_rate, 4)
            
            if error_rate > 0.1:  # >10% error rate
                checks.append(('warn', f'High error rate: {error_rate:.1%}'))
                status_msg = f'Stellar API degraded (error rate: {error_rate:.1%})'
            else:
                checks.append(('pass', f'Error rate acceptable: {error_rate:.2%}'))
                status_msg = 'Stellar API operational'
        else:
            checks.append(('pass', 'No requests yet'))
            status_msg = 'Stellar API operational'
        
        # Check 4: Recent errors
        if last_error and last_error_time:
            try:
                last_error_dt = datetime.fromisoformat(last_error_time)
                time_since_error = (datetime.now() - last_error_dt).total_seconds()
                
                if time_since_error < 60:  # Error within last minute
                    checks.append(('warn', f'Recent error: {last_error}'))
                else:
                    checks.append(('pass', f'Last error {int(time_since_error)}s ago'))
            except:
                pass
        
        # Determine overall status
        has_failures = any(status == 'fail' for status, _ in checks)
        has_warnings = any(status == 'warn' for status, _ in checks)
        
        if has_failures:
            overall_status = 'unhealthy'
        elif has_warnings:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'message': status_msg,
            'details': details,
            'checks': checks,
            'checks_passed': sum(1 for s, _ in checks if s == 'pass'),
            'checks_failed': sum(1 for s, _ in checks if s == 'fail'),
            'checks_warned': sum(1 for s, _ in checks if s == 'warn'),
            'timestamp': datetime.now().isoformat()
        }
    
    # ========================================================================
    # SYNCHRONOUS HEALTH CHECK (for config-like services)
    # ========================================================================
    
    @staticmethod
    def sync_basic_health_check(
        service_name: str,
        is_initialized: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synchronous basic health check for services without async requirements.
        
        This is used for simple services like configuration managers that don't
        perform I/O operations and don't need async capabilities.
        
        Args:
            service_name: Name of the service (e.g., 'config')
            is_initialized: Whether service is initialized
            **kwargs: Additional context to include
        
        Returns:
            Health status dictionary (non-async)
        
        Implementation Notes:
            - No async operations
            - Suitable for config, utility services
            - Returns immediately
            - Principle #6: No sync fallbacks (this is intentionally sync)
        
        Example:
            class ConfigService:
                def health_check(self) -> Dict[str, Any]:
                    return ServiceHealthCheck.sync_basic_health_check(
                        service_name='config',
                        is_initialized=True,
                        config_loaded=len(self._config) > 0,
                        num_settings=len(self._config),
                        horizon_url=self.horizon_url,
                        network=self.network
                    )
        """
        status = HealthStatus.HEALTHY.value if is_initialized else HealthStatus.UNHEALTHY.value
        message = f"{service_name} operational" if is_initialized else f"{service_name} not initialized"
        
        health = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': {
                'initialized': is_initialized,
                'async': False,  # Indicate this is a sync check
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
    
    This is a convenience function for dynamically creating health check methods
    during service initialization.
    
    Args:
        service_name: Name of the service
        check_type: Type of health check:
            - 'basic': Simple service with no external dependencies
            - 'database': Service that requires database connectivity
            - 'api': Service that interacts with external APIs
            - 'element': Element protocol (air/water/earth/fire)
        **context: Context to pass to health check (db_manager, rate_limiter, etc.)
    
    Returns:
        Async callable that performs the appropriate health check
    
    Usage:
        class MyService:
            def __init__(self, db_manager):
                self.db = db_manager
                self._initialized = False
                
                # Create health check method
                self.health_check = create_health_check_method(
                    service_name='my_service',
                    check_type='database',
                    db_manager=self.db,
                    is_initialized=lambda: self._initialized
                )
            
            async def initialize(self):
                # ... initialization code ...
                self._initialized = True
    
    Note:
        - For 'database' type: Must provide 'db_manager' in context
        - For 'api' type: Can provide 'rate_limiter' and/or 'cache_info' in context
        - For 'element' type: Must provide 'element_name', 'token_code', 'db_manager'
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
    elif check_type == 'element':
        async def health_check():
            return await ServiceHealthCheck.element_protocol_health(
                **context
            )
    else:  # 'basic' or unknown type
        async def health_check():
            return await ServiceHealthCheck.basic_health_check(
                service_name=service_name,
                **context
            )
    
    return health_check


def validate_health_response(health: Dict[str, Any]) -> bool:
    """
    Validate that a health check response has the correct structure.
    
    This can be used in tests or for defensive programming to ensure
    health check implementations return properly structured data.
    
    Args:
        health: Health check response dictionary
    
    Returns:
        True if valid, False otherwise
    
    Example:
        health = await service.health_check()
        assert validate_health_response(health), "Invalid health check response"
    """
    required_fields = ['status', 'message', 'timestamp', 'details']
    
    # Check required fields exist
    if not all(field in health for field in required_fields):
        return False
    
    # Check status is valid
    valid_statuses = [status.value for status in HealthStatus]
    if health['status'] not in valid_statuses:
        return False
    
    # Check details is a dict
    if not isinstance(health['details'], dict):
        return False
    
    # Check initialized field exists in details
    if 'initialized' not in health['details']:
        return False
    
    return True


# ============================================================================
# PUBLIC EXPORTS
# ============================================================================

__all__ = [
    'HealthStatus',
    'ServiceHealthCheck',
    'create_health_check_method',
    'validate_health_response'
]
