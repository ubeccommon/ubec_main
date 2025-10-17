#!/usr/bin/env python3
"""
UBEC Data Synchronizer - Health Check Enhancement
==================================================

This file contains the ENHANCED health_check() method that should REPLACE
the existing health_check() method in ubec_data_synchronizer.py

Key Changes:
1. Import ServiceHealthCheck utility at top of file
2. Replace existing health_check() method with this enhanced version
3. Add custom health checks for Stellar connectivity and rate limiter

Design Principles Compliance:
- ✅ Principle #12: Method Singularity - Uses ServiceHealthCheck utility
- ✅ Principle #7: Per-Asset Monitoring - Comprehensive health metrics
- ✅ Principle #5: Strict Async - All operations async

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 8.0.0 (ServiceHealthCheck Integration)
Date: October 17, 2025
"""

# ============================================================================
# STEP 1: ADD THIS IMPORT AT THE TOP OF ubec_data_synchronizer.py
# ============================================================================

from core.utils.service_health import ServiceHealthCheck


# ============================================================================
# STEP 2: REPLACE THE EXISTING health_check() METHOD WITH THIS VERSION
# ============================================================================

async def health_check(self) -> Dict[str, Any]:
    """
    Perform comprehensive health check on synchronizer service.
    
    Now uses ServiceHealthCheck utility (Principle #12: Method Singularity)
    for standardized health reporting across all services.
    
    Implements Principle #7 (Per-Asset Monitoring) with detailed metrics:
    - Database connectivity
    - Stellar API connectivity
    - Settings loaded status
    - Rate limiter health and metrics
    - Circuit breaker status
    - Sync operation statistics
    
    Returns:
        Dict with health status and comprehensive metrics:
        {
            'status': 'healthy' | 'degraded' | 'unhealthy',
            'message': str,
            'timestamp': str (ISO 8601),
            'details': {
                'initialized': bool,
                'settings_loaded': bool,
                'sync_operations_count': int,
                'last_sync_time': str or None,
                'rate_limiter': {
                    'total_requests': int,
                    'rate_limited_requests': int,
                    'retry_attempts': int,
                    'current_remaining': int,
                    'current_limit': int,
                    'circuit_breaker_state': str,
                    'circuit_breaker_failures': int
                },
                'has_database': bool,
                'has_stellar': bool,
                'checks_passed': int,
                'checks_failed': int,
                'checks': List[Tuple[str, Any]]
            }
        }
    
    Example:
        health = await sync.health_check()
        
        if health['status'] == 'healthy':
            print("✓ Synchronizer operational")
            print(f"  Sync ops: {health['details']['sync_operations_count']}")
            print(f"  Rate limiter: {health['details']['rate_limiter']['circuit_breaker_state']}")
        else:
            print(f"✗ Synchronizer {health['status']}: {health['message']}")
            if health['details'].get('checks'):
                for status, result in health['details']['checks']:
                    if status == 'fail':
                        print(f"  Failed check: {result}")
    """
    async def check_stellar_connectivity():
        """
        Verify Stellar API connectivity by making a simple test call.
        
        Tests both:
        1. Stellar server is initialized
        2. Can successfully make API calls through rate limiter
        """
        if not self.server:
            raise Exception("Stellar server not initialized")
        
        # Make a simple test call through our rate-limited wrapper
        try:
            await self._stellar_api_call(
                self.server.ledgers().limit(1).call
            )
            return "Stellar API accessible"
        except Exception as e:
            raise Exception(f"Stellar API test call failed: {e}")
    
    async def check_settings_loaded():
        """Verify settings are loaded from database."""
        if not self.settings:
            raise Exception("Settings not loaded from database")
        
        # Verify critical settings exist
        required_settings = ['horizon_url', 'ubec_issuer']
        missing = [s for s in required_settings if s not in self.settings]
        
        if missing:
            raise Exception(f"Missing critical settings: {missing}")
        
        return f"Settings loaded ({len(self.settings)} items)"
    
    async def check_rate_limiter_health():
        """
        Verify rate limiter is functioning and not degraded.
        
        Checks:
        1. Rate limiter exists
        2. Circuit breaker not stuck open
        3. Reasonable error rate
        """
        if not self.rate_limiter:
            raise Exception("Rate limiter not initialized")
        
        metrics = self.rate_limiter.get_metrics()
        
        # Check circuit breaker state
        cb_state = metrics.get('circuit_breaker_state', 'unknown')
        if cb_state == 'open':
            raise Exception(f"Circuit breaker is OPEN (service degraded)")
        
        # Check error rate (warn if > 50% of requests are being rate limited)
        total_requests = metrics.get('total_requests', 0)
        rate_limited = metrics.get('rate_limited_requests', 0)
        
        if total_requests > 10:  # Only check if we have enough samples
            error_rate = rate_limited / total_requests
            if error_rate > 0.5:
                raise Exception(
                    f"High rate limit error rate: {error_rate:.1%} "
                    f"({rate_limited}/{total_requests} requests rate limited)"
                )
        
        return f"Rate limiter healthy ({cb_state} state, {total_requests} total requests)"
    
    # Get rate limiter metrics for inclusion in health response
    rate_limiter_metrics = None
    if self.rate_limiter:
        rate_limiter_metrics = self.rate_limiter.get_metrics()
    
    # Use ServiceHealthCheck utility (Principle #12: Method Singularity)
    return await ServiceHealthCheck.database_dependent_health(
        service_name='synchronizer',
        db_manager=self.db,
        is_initialized=self.initialized,
        additional_checks=[
            check_settings_loaded,
            check_stellar_connectivity,
            check_rate_limiter_health
        ],
        # Additional context for health response
        settings_loaded=bool(self.settings),
        sync_operations_count=self._sync_operations_count,
        last_sync_time=self._last_sync_time.isoformat() if self._last_sync_time else None,
        rate_limiter=rate_limiter_metrics,
        has_stellar=self.server is not None,
        horizon_url=self.horizon_url if hasattr(self, 'horizon_url') else None,
        network=self.network if hasattr(self, 'network') else None
    )


# ============================================================================
# EXPLANATION OF ENHANCEMENTS
# ============================================================================

"""
What Changed:
=============

1. ADDED ServiceHealthCheck Import
   - Top of file: from core.utils.service_health import ServiceHealthCheck

2. REPLACED Custom Health Check Logic
   - Old: Manual dictionary construction with custom checks
   - New: Uses ServiceHealthCheck.database_dependent_health() utility

3. ADDED Three Custom Health Checks
   
   a) check_stellar_connectivity():
      - Verifies Stellar server initialization
      - Tests actual API connectivity with a simple call
      - Uses rate-limited wrapper for realistic test
   
   b) check_settings_loaded():
      - Confirms settings loaded from database (Principle #4)
      - Verifies critical settings like horizon_url, ubec_issuer exist
      - Reports count of loaded settings
   
   c) check_rate_limiter_health():
      - Verifies rate limiter exists and is configured
      - Checks circuit breaker state (warns if open)
      - Calculates and validates error rate
      - Warns if > 50% of requests are being rate limited

4. ENHANCED Metrics Reporting
   - Includes full rate limiter metrics
   - Reports sync operation count
   - Tracks last sync time
   - Shows Stellar connection status
   - Lists horizon URL and network

5. STANDARDIZED Response Format
   - Consistent with all other services
   - Follows health check implementation guide
   - Compatible with service registry health checks


Benefits:
=========

✅ Principle #12 Compliance: Uses ServiceHealthCheck utility
✅ Principle #7 Compliance: Comprehensive per-asset monitoring
✅ Standardized Format: Same structure as all services
✅ Better Diagnostics: Three targeted health checks
✅ Proactive Monitoring: Detects issues before they cause failures
✅ Rate Limiter Visibility: Full metrics in health response
✅ Circuit Breaker Awareness: Know when service is degraded


Example Health Response:
========================

{
  "status": "healthy",
  "message": "synchronizer operational",
  "timestamp": "2025-10-17T03:00:00.000000",
  "details": {
    "initialized": true,
    "settings_loaded": true,
    "sync_operations_count": 1247,
    "last_sync_time": "2025-10-17T02:59:45.123456",
    "rate_limiter": {
      "total_requests": 1200,
      "rate_limited_requests": 3,
      "retry_attempts": 5,
      "current_remaining": 3450,
      "current_limit": 3600,
      "circuit_breaker_state": "closed",
      "circuit_breaker_failures": 0
    },
    "has_database": true,
    "has_stellar": true,
    "horizon_url": "https://horizon.stellar.org",
    "network": "Public Global Stellar Network ; September 2015",
    "checks_passed": 3,
    "checks_failed": 0,
    "checks": [
      ["pass", "Settings loaded (15 items)"],
      ["pass", "Stellar API accessible"],
      ["pass", "Rate limiter healthy (closed state, 1200 total requests)"]
    ]
  }
}


Degraded State Example:
=======================

{
  "status": "degraded",
  "message": "synchronizer degraded: Circuit breaker is OPEN (service degraded)",
  "timestamp": "2025-10-17T03:15:00.000000",
  "details": {
    "initialized": true,
    "settings_loaded": true,
    "sync_operations_count": 1500,
    "last_sync_time": "2025-10-17T03:14:30.123456",
    "rate_limiter": {
      "total_requests": 1450,
      "rate_limited_requests": 145,  # High rate limit hits
      "retry_attempts": 290,
      "current_remaining": 0,
      "current_limit": 3600,
      "circuit_breaker_state": "open",  # Circuit breaker triggered!
      "circuit_breaker_failures": 12
    },
    "has_database": true,
    "has_stellar": true,
    "checks_passed": 2,
    "checks_failed": 1,
    "checks": [
      ["pass", "Settings loaded (15 items)"],
      ["pass", "Stellar API accessible"],
      ["fail", "Circuit breaker is OPEN (service degraded)"]  # Failed check
    ]
  }
}


Integration Instructions:
=========================

1. Open ubec_data_synchronizer.py

2. Add import at top (after other imports):
   from core.utils.service_health import ServiceHealthCheck

3. Find the existing health_check() method (around line 600)

4. REPLACE the entire existing health_check() method with the enhanced
   version from this file

5. Save the file

6. Test:
   python main.py --mode health

7. Expected result:
   - Synchronizer should show "healthy" status
   - All 3 custom checks should pass
   - Rate limiter metrics should be visible


Troubleshooting:
================

If synchronizer shows "degraded":
- Check "checks" list in response to see which check failed
- Common issues:
  * Circuit breaker open: Wait 5 minutes for recovery
  * High error rate: Stellar API may be slow/unavailable
  * Settings not loaded: Check database connection

If synchronizer shows "unhealthy":
- Likely database connection issue
- Or service not initialized properly
- Check "issues" list for specific problems
"""
