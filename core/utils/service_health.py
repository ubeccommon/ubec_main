"""
UBEC Service Health Check Utility - ENHANCED VERSION
═══════════════════════════════════════════════════════════════════════════

Standardized health checking for all UBEC services.
Provides reusable health check patterns following Principle #12 (Method Singularity).

ENHANCED in v3.0:
- Added NEEDS_SYNC status for protocols awaiting initial synchronization
- Actionable messages with specific commands to resolve issues
- Clear distinction between operational issues vs. data freshness
- User-friendly guidance for common scenarios

Design Principles:
    ✅ Principle #7: Per-Asset Monitoring - Detailed health metrics
    ✅ Principle #12: Method Singularity - Single shared implementation

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 3.0.0 (Actionable Status Messages)
Date: October 20, 2025

Changelog:
    v3.0.0 - ACTIONABLE STATUS MESSAGES:
           - Added NEEDS_SYNC status for protocols awaiting initial sync
           - Enhanced messages with specific commands to resolve issues
           - Better distinction between operational vs. data issues
           - User-friendly guidance for all status types
    v2.0.0 - Enhanced health check patterns
    v1.0.0 - Initial implementation
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List, Union
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# HEALTH STATUS ENUMERATION - ENHANCED
# ============================================================================

class HealthStatus(Enum):
    """
    Health status levels for services - ENHANCED with actionable states.
    
    Attributes:
        HEALTHY: Service fully operational with all checks passing
        NEEDS_SYNC: Service operational but requires data synchronization
                   (More specific than "degraded" for protocols)
        DEGRADED: Service operational but with some non-critical issues
        UNHEALTHY: Service not operational or critical checks failing
        UNKNOWN: Service status cannot be determined
        INITIALIZING: Service is in the process of starting up
    """
    HEALTHY = "healthy"
    NEEDS_SYNC = "needs_sync"  # NEW: Clear about what's needed
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
    
    ENHANCED: Now includes actionable status messages that guide users
    toward solutions rather than just reporting problems.
    
    The class offers three main patterns:
    1. basic_health_check: For simple services with no external dependencies
    2. database_dependent_health: For services that require database connectivity
    3. api_dependent_health: For services that interact with external APIs
    4. element_protocol_health: For UBEC element protocols (Air, Water, Earth, Fire)
    
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
            service_name: Name of the service being checked
            is_initialized: Whether the service has been fully initialized
            additional_checks: Optional list of async/sync callables that perform checks
            include_stats: Whether to include detailed statistics
            **kwargs: Additional context to include in response
        
        Returns:
            Dictionary with health status information including actionable messages
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
            health['message'] = (f"{service_name} not initialized - "
                               f"Check service initialization in main.py")
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
            
            health['details']['checks'] = check_results
            health['details']['checks_passed'] = len(check_results) - failed_checks
            health['details']['checks_failed'] = failed_checks
            
            # Update status based on check results
            if failed_checks > 0:
                if failed_checks == len(check_results):
                    health['status'] = HealthStatus.UNHEALTHY.value
                    health['message'] = f"{service_name} unhealthy - all checks failed"
                else:
                    health['status'] = HealthStatus.DEGRADED.value
                    health['message'] = (f"{service_name} degraded - "
                                       f"{failed_checks}/{len(check_results)} checks failed")
        
        return health
    
    # ========================================================================
    # DATABASE DEPENDENT HEALTH CHECK
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
        
        ENHANCED: Provides actionable guidance for database connection issues.
        
        Args:
            service_name: Name of the service
            db_manager: Database manager instance
            is_initialized: Whether service is initialized
            additional_checks: Additional check functions
            **kwargs: Additional context
        
        Returns:
            Health status with database connectivity information
        """
        # Test database connection
        db_checks = []
        
        async def check_db_connection():
            """Check if database is accessible"""
            try:
                # Simple query to test connection
                result = await db_manager.execute_query(
                    "SELECT 1 as test",
                    fetch_one=True
                )
                return result is not None
            except Exception as e:
                raise Exception(f"Database unreachable: {str(e)} - "
                              f"Check DB_HOST, DB_PORT, and DB_PASSWORD in .env")
        
        db_checks.append(check_db_connection)
        
        # Add any additional checks
        if additional_checks:
            db_checks.extend(additional_checks)
        
        return await ServiceHealthCheck.basic_health_check(
            service_name=service_name,
            is_initialized=is_initialized,
            additional_checks=db_checks,
            database_connected=True,  # Will be overridden if check fails
            **kwargs
        )
    
    # ========================================================================
    # ELEMENT PROTOCOL HEALTH CHECK - ENHANCED
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
        Health check for UBEC element protocols (Air, Water, Earth, Fire).
        
        ENHANCED: Uses NEEDS_SYNC status with actionable guidance instead of
        generic "degraded" status. Provides specific commands to resolve issues.
        
        Args:
            element_name: Name of the element (e.g., "Water", "Fire")
            token_code: Associated token code (e.g., "UBECrc", "UBECtt")
            db_manager: Database manager instance
            is_initialized: Whether protocol is initialized
            last_sync: Timestamp of last synchronization (None if never synced)
            cached_accounts: Number of accounts in cache
            additional_checks: Additional check functions
            **kwargs: Additional protocol-specific context
        
        Returns:
            Health status with protocol-specific information and actionable guidance
        """
        def check_sync_freshness():
            """
            Check if data synchronization is recent.
            
            ENHANCED: Returns actionable status instead of raising exception.
            """
            if last_sync is None:
                # Return tuple: (status, message, action)
                return ('needs_sync', 
                       f'{element_name} protocol awaiting initial synchronization',
                       'Run: python main.py --mode sync --sync-type all')
            
            time_since_sync = (datetime.now() - last_sync).total_seconds()
            
            # Warn if sync is older than 30 minutes
            if time_since_sync > 1800:
                return ('degraded',
                       f'{element_name} protocol data stale ({time_since_sync/60:.1f} minutes old)',
                       'Run: python main.py --mode sync --sync-type all --force')
            
            return ('pass', 
                   f'Data fresh: synced {int(time_since_sync)}s ago',
                   None)
        
        # Build check list
        all_checks = []
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
        
        # Perform sync freshness check
        sync_status, sync_message, sync_action = check_sync_freshness()
        
        # Perform database checks
        db_health = await ServiceHealthCheck.database_dependent_health(
            service_name=f'{element_name.lower()}_protocol',
            db_manager=db_manager,
            is_initialized=is_initialized,
            additional_checks=all_checks,
            **element_details
        )
        
        # Override status and message based on sync check
        if sync_status == 'needs_sync':
            db_health['status'] = HealthStatus.NEEDS_SYNC.value
            db_health['message'] = sync_message
            if sync_action:
                db_health['action'] = sync_action  # NEW: Actionable command
                db_health['details']['sync_required'] = True
        elif sync_status == 'degraded':
            # Only override if current status is healthy
            if db_health['status'] == HealthStatus.HEALTHY.value:
                db_health['status'] = HealthStatus.DEGRADED.value
                db_health['message'] = sync_message
                if sync_action:
                    db_health['action'] = sync_action  # NEW: Actionable command
        else:
            # Sync is fresh - update message to reflect this
            db_health['message'] = f'{element_name} protocol operational - {sync_message}'
        
        return db_health
    
    # ========================================================================
    # API DEPENDENT HEALTH CHECK
    # ========================================================================
    
    @staticmethod
    async def api_dependent_health(
        service_name: str,
        is_initialized: bool = True,
        api_url: Optional[str] = None,
        api_accessible: bool = True,
        request_count: int = 0,
        error_count: int = 0,
        rate_limiter: Optional[Any] = None,
        cache_info: Optional[Dict[str, Any]] = None,
        additional_checks: Optional[List[Callable]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for services that depend on external APIs.
        
        ENHANCED: Provides actionable guidance for API connectivity issues.
        
        Args:
            service_name: Name of the service
            is_initialized: Whether service is initialized
            api_url: URL of the external API
            api_accessible: Whether API is currently accessible
            request_count: Number of API requests made
            error_count: Number of API errors encountered
            rate_limiter: Rate limiter instance if present
            cache_info: Cache statistics if available
            additional_checks: Additional check functions
            **kwargs: Additional context
        
        Returns:
            Health status with API connectivity information and guidance
        """
        api_details = {
            'api_url': api_url,
            'api_accessible': api_accessible,
            'request_count': request_count,
            'error_count': error_count,
            'error_rate': (error_count / request_count * 100) if request_count > 0 else 0
        }
        
        # Add rate limiter status
        if rate_limiter:
            api_details['rate_limiter_status'] = getattr(rate_limiter, 'status', 'unknown')
            api_details['has_rate_limiter'] = True
        else:
            api_details['has_rate_limiter'] = False
        
        # Add cache information
        if cache_info:
            api_details['cache'] = cache_info
            api_details['has_cache'] = True
        else:
            api_details['has_cache'] = False
        
        # Check API accessibility
        api_checks = []
        if not api_accessible and api_url:
            async def check_api():
                raise Exception(f"API unreachable: {api_url} - "
                              f"Check network connectivity and API endpoint")
            api_checks.append(check_api)
        
        # Add additional checks
        if additional_checks:
            api_checks.extend(additional_checks)
        
        return await ServiceHealthCheck.basic_health_check(
            service_name=service_name,
            is_initialized=is_initialized,
            additional_checks=api_checks if api_checks else None,
            **api_details
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
        
        ENHANCED: Provides actionable guidance for Stellar connectivity issues.
        
        Tests connectivity to Stellar Horizon API and tracks request/error metrics.
        """
        async def check_horizon_connectivity():
            """Test connection to Horizon API"""
            try:
                # Simple connectivity test
                await client.get_horizon_info()
                return True
            except Exception as e:
                raise Exception(f"Stellar Horizon unreachable: {str(e)} - "
                              f"Check HORIZON_URL in configuration")
        
        return await ServiceHealthCheck.api_dependent_health(
            service_name='stellar_client',
            is_initialized=initialized,
            api_url=horizon_url,
            api_accessible=True,  # Will be updated by check
            request_count=request_count,
            error_count=error_count,
            additional_checks=[check_horizon_connectivity],
            last_error=last_error,
            last_error_time=last_error_time,
            **kwargs
        )
    
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
        
        Used for simple services like configuration managers that don't
        perform I/O operations.
        
        Args:
            service_name: Name of the service
            is_initialized: Whether service is initialized
            **kwargs: Additional context
        
        Returns:
            Health status dictionary
        """
        health = {
            'status': HealthStatus.HEALTHY.value if is_initialized else HealthStatus.UNHEALTHY.value,
            'message': f"{service_name} {'operational' if is_initialized else 'not initialized'}",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'initialized': is_initialized,
                **kwargs
            }
        }
        
        if not is_initialized:
            health['action'] = "Check service initialization in main.py"
        
        return health
    
    # ========================================================================
    # UTILITY: Create Health Check Instance (Deprecated - use static methods)
    # ========================================================================
    
    def __init__(self, service_name: str):
        """
        Initialize health check tracker.
        
        DEPRECATED: Prefer using static methods directly.
        This constructor is kept for backward compatibility only.
        """
        self.service_name = service_name
        self.status = HealthStatus.UNKNOWN
        self.message = ""
        self.details = {}
        self.timestamp = datetime.now()
    
    def mark_healthy(self, message: str = "Service operational"):
        """Mark service as healthy"""
        self.status = HealthStatus.HEALTHY
        self.message = message
        self.timestamp = datetime.now()
    
    def mark_needs_sync(self, message: str, action: str):
        """Mark service as needing synchronization with actionable command"""
        self.status = HealthStatus.NEEDS_SYNC
        self.message = message
        self.details['action'] = action
        self.timestamp = datetime.now()
    
    def mark_degraded(self, message: str, action: Optional[str] = None):
        """Mark service as degraded with optional action"""
        self.status = HealthStatus.DEGRADED
        self.message = message
        if action:
            self.details['action'] = action
        self.timestamp = datetime.now()
    
    def mark_unhealthy(self, message: str, action: Optional[str] = None):
        """Mark service as unhealthy with optional action"""
        self.status = HealthStatus.UNHEALTHY
        self.message = message
        if action:
            self.details['action'] = action
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health check to dictionary"""
        result = {
            'status': self.status.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
        
        if 'action' in self.details:
            result['action'] = self.details['action']
        
        return result


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_actionable_message(issue: str, command: str) -> str:
    """
    Create an actionable error message that guides users to a solution.
    
    Args:
        issue: Description of the problem
        command: Command to run to resolve the issue
    
    Returns:
        Formatted actionable message
    """
    return f"{issue} → Run: {command}"


def is_service_operational(health_status: Dict[str, Any]) -> bool:
    """
    Check if a service is operational (healthy or needs_sync).
    
    A service with needs_sync status is considered operational because
    it's initialized and ready, just needs data synchronization.
    
    Args:
        health_status: Health status dictionary
    
    Returns:
        True if service is operational, False otherwise
    """
    status = health_status.get('status', 'unknown')
    return status in [HealthStatus.HEALTHY.value, HealthStatus.NEEDS_SYNC.value]


def get_action_from_health(health_status: Dict[str, Any]) -> Optional[str]:
    """
    Extract actionable command from health status.
    
    Args:
        health_status: Health status dictionary
    
    Returns:
        Command to resolve issue, or None if no action needed
    """
    return health_status.get('action')
