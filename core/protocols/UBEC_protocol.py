#!/usr/bin/env python3
# core/protocols/UBEC_protocol.py
"""
UBEC Protocol - Air Element (Gateway & Universal Access)
========================================================
Service implementation for the Air element of the UBEC four-element system.

The Air element represents:
- 🌬️ Gateway: Universal entry point for all participants
- Diversity: Welcoming all forms of participation
- Accessibility: Lowering barriers to economic inclusion
- Freedom: Unrestricted access to basic economic rights

This module implements the service pattern with:
- Pure async operations (no sync fallbacks)
- Factory function for instantiation
- Database as single source of truth
- Built-in rate limiting
- In-memory caching with TTL
- Comprehensive health monitoring using ServiceHealthCheck utility

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained service with clear boundaries
    ✅ 2.  Service Pattern: No standalone execution, factory-based instantiation
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Health checks and individual account tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Rate Limiting: Built-in API rate limiting
    ✅ 10. Separation of Concerns: Gateway logic separated from data access
    ✅ 11. Documentation: Comprehensive docstrings and inline comments
    ✅ 12. Method Singularity: No duplicate methods, uses ServiceHealthCheck utility
══════════════════════════════════════════════════════════════════════════════

Usage:
    from UBEC_protocol import create_ubec_service
    
    service = await create_ubec_service(
        db_manager=async_db,
        config={'asset_code': 'UBEC', 'issuer': 'G...'},
        stellar_client=stellar_async
    )
    
    # All methods are async
    await service.sync_gateway_data()
    accounts = await service.get_gateway_accounts()
    stats = await service.get_gateway_statistics()
    health = await service.health_check()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.0.0 (Complete Element Protocol Implementation)
Date: October 18, 2025

Changelog:
    v3.0.0 - MAJOR: Fixed element metadata exposure
           - Added element, element_description, and ubuntu_principle properties
           - Implemented proper health_check() using element_protocol_health()
           - Fixed status output to show correct element/principle information
           - Full compliance with health check implementation guide
           - Resolves "unknown" status issues identified in critical review
    v2.2.0 - Standardized health check using ServiceHealthCheck utility
           - Implements Principle #12: Method Singularity with shared utility
           - Removed custom health_check() implementation
           - Now uses ServiceHealthCheck.api_dependent_health()
    v2.1.0 - Enhanced health_check() method for comprehensive monitoring
           - Implements Principle #7: Per-Asset Monitoring with detailed checks
    v2.0.0 - Complete async service architecture
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

# Import standardized health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck


# ==================== RATE LIMITER ====================

class RateLimiter:
    """
    Simple async rate limiter for API calls.
    Implements token bucket algorithm.
    
    Principle 5: Strict Async - All operations use async/await
    Principle 9: Integrated Rate Limiting
    """
    
    def __init__(self, calls_per_second: float = 10.0):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum calls allowed per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Acquire permission to make a call.
        Blocks if rate limit would be exceeded.
        
        Principle 5: Uses async sleep, not blocking time.sleep()
        """
        async with self._lock:
            now = asyncio.get_event_loop().time()
            time_since_last = now - self.last_call
            
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self.last_call = asyncio.get_event_loop().time()


# ==================== DATA MODELS ====================

class GatewayAccessLevel(Enum):
    """Gateway access levels for participants"""
    OPEN = "open"              # Anyone can access
    VERIFIED = "verified"       # Verified participants
    TRUSTED = "trusted"         # Trusted community members
    RESTRICTED = "restricted"   # Limited access


@dataclass
class GatewayAccount:
    """
    Represents a gateway account in the Air element.
    
    Principle 1: Modular Design - Clear data structure
    """
    account_id: str
    access_level: GatewayAccessLevel
    balance: Decimal
    trustline_established: bool
    first_access: datetime
    last_activity: datetime
    transaction_count: int
    diversity_score: float  # 0.0 - 1.0, measures participation diversity


@dataclass
class GatewayStatistics:
    """
    Gateway-wide statistics.
    
    Principle 7: Per-Asset Monitoring - Comprehensive metrics
    """
    total_accounts: int
    active_accounts: int
    total_balance: Decimal
    average_balance: Decimal
    new_accounts_24h: int
    diversity_index: float  # System-wide diversity measure
    trustline_adoption_rate: float


# ==================== SERVICE IMPLEMENTATION ====================

class UBECProtocolService:
    """
    UBEC Air Protocol Service
    
    Manages gateway access and universal participation in the UBEC ecosystem.
    All operations are async and use the database as the single source of truth.
    
    This service represents the Air element:
    - Gateway to the UBEC ecosystem
    - Diversity in participation
    - Universal accessibility
    - Freedom of economic access
    
    Element Metadata:
        element: 'air'
        element_description: 'Gateway & Universal Access'
        ubuntu_principle: 'diversity'
        asset_code: 'UBEC'
        symbol: '🜁'
    
    Attributes:
        db_manager: Async database manager
        config: Protocol configuration
        stellar_client: Async Stellar SDK client
        logger: Logger instance
        rate_limiter: API rate limiter
        
    Lifecycle:
        1. Instantiate via create_ubec_service() factory
        2. Service auto-initializes on first use
        3. Cleanup via close() method
        
    Design Principles:
        - Principle 1: Modular - Clear boundaries and single responsibility
        - Principle 4: Single Source of Truth - Database-driven
        - Principle 5: Strict Async - All I/O operations async
        - Principle 10: Separation of Concerns - Clear layer separation
        - Principle 12: Method Singularity - Uses ServiceHealthCheck utility
    """
    
    def __init__(
        self,
        db_manager,
        config: Dict[str, Any],
        stellar_client = None,
        rate_limit_calls_per_second: float = 10.0
    ):
        """
        Initialize UBEC Air protocol service.
        
        DO NOT call directly - use create_ubec_service() factory instead.
        
        Args:
            db_manager: Database manager with async support
            config: Configuration dictionary with asset_code, issuer, etc.
            stellar_client: Optional Stellar async client
            rate_limit_calls_per_second: API rate limit (default: 10/sec)
        """
        self.db_manager = db_manager
        self.config = config
        self.stellar_client = stellar_client
        
        # Element metadata (CRITICAL: Fixes "unknown" status issue)
        # These properties are exposed in status output
        self.element = 'air'
        self.element_description = 'Gateway & Universal Access'
        self.ubuntu_principle = 'diversity'
        self.asset_code = config.get('asset_code', 'UBEC')
        self.issuer = config.get('issuer', 'unknown')
        self.symbol = '🜁'  # Air element symbol
        
        # Logging
        self.logger = logging.getLogger(f"UBECProtocol.{self.asset_code}")
        
        # Rate limiting (Principle 9)
        self.rate_limiter = RateLimiter(calls_per_second=rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._account_cache: Dict[str, GatewayAccount] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)  # 5-minute cache TTL
        
        # Operational metrics for health checks (Principle 7)
        self._initialized = False
        self._sync_count = 0
        self._query_count = 0
        self._error_count = 0
        self._last_sync_time: Optional[datetime] = None
        self._last_query_time: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info(
            f"Air Protocol Service initialized for {self.asset_code} "
            f"(Element: {self.element_description})"
        )
    
    # ==================== INITIALIZATION ====================
    # Principle 5: Strict Async Operations
    
    async def initialize(self) -> None:
        """
        Initialize the service and verify database connectivity.
        
        This method is called automatically on first use but can be called
        explicitly to ensure the service is ready.
        
        Design Notes:
            - Principle 5: Async initialization
            - Principle 4: Verifies database connection (single source of truth)
        """
        if self._initialized:
            return
        
        self.logger.info("Initializing Air protocol service...")
        
        try:
            # Verify database connection
            await self.db_manager.execute("SELECT 1")
            
            self._initialized = True
            self.logger.info("✓ Air protocol service initialized")
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Failed to initialize Air protocol: {e}")
            raise
    
    async def _ensure_initialized(self) -> None:
        """Ensure service is initialized before operations."""
        if not self._initialized:
            await self.initialize()
    
    # ==================== HEALTH CHECK ====================
    # Principle 12: Method Singularity - Uses ServiceHealthCheck utility
    # Principle 7: Per-Asset Monitoring - Comprehensive health data
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for Air protocol service.
        
        Uses standardized ServiceHealthCheck utility for consistency across
        all services, implementing Principle #12 (Method Singularity).
        
        This implementation follows the element protocol health check pattern,
        which includes:
        - Element-specific metadata (air, diversity, UBEC)
        - Database connectivity validation
        - Cache status and freshness
        - Operational statistics
        - Error tracking
        
        Returns:
            Health status dictionary from ServiceHealthCheck utility:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy' | 'unknown',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'has_db': bool,
                    'db_connection': bool,
                    'db_response_time_ms': float,
                    'cache': {
                        'size': int,
                        'last_sync': str (ISO timestamp),
                        'age_seconds': float,
                        'status': str
                    },
                    'asset_code': str,
                    'element': str,
                    'element_description': str,
                    'ubuntu_principle': str,
                    'symbol': str,
                    'sync_count': int,
                    'query_count': int,
                    'error_count': int,
                    'last_sync': str (ISO timestamp),
                    'last_error': str,
                    'last_error_time': str (ISO timestamp)
                }
            }
        
        Example:
            >>> health = await service.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Air protocol operational")
            >>> print(f"Element: {health['details']['element']}")
            >>> print(f"Principle: {health['details']['ubuntu_principle']}")
        
        Design Notes:
            - Principle 7: Comprehensive per-asset monitoring
            - Principle 12: Delegates to ServiceHealthCheck utility (no duplication)
            - This implementation ensures element metadata is properly exposed
        """
        # Use the standardized element protocol health check
        # This resolves the "unknown" status issue identified in the review
        return await ServiceHealthCheck.element_protocol_health(
            element_name=self.element,
            token_code=self.asset_code,
            db_manager=self.db_manager,
            is_initialized=self._initialized,
            last_sync=self._last_sync_time,
            cached_accounts=len(self._account_cache),
            ubuntu_principle=self.ubuntu_principle,
            # Additional context for comprehensive monitoring
            element_description=self.element_description,
            symbol=self.symbol,
            issuer=self.issuer[:12] + '...' if len(self.issuer) > 12 else self.issuer,
            sync_count=self._sync_count,
            query_count=self._query_count,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time.isoformat() if self._last_error_time else None
        )
    
    # ==================== CACHE MANAGEMENT ====================
    # Principle 4: Single Source of Truth (database) with caching layer
    
    async def _ensure_cache_loaded(self) -> None:
        """
        Ensure account cache is loaded and fresh.
        
        Loads from database if cache is empty or stale.
        
        Design Notes:
            - Principle 4: Database is authoritative, cache is optimization
            - Principle 5: Async operation
        """
        now = datetime.now()
        
        # Check if cache needs refresh
        cache_stale = (
            not self._cache_timestamp or 
            (now - self._cache_timestamp) > self._cache_ttl
        )
        
        if not self._account_cache or cache_stale:
            await self._load_accounts_from_db()
    
    async def _load_accounts_from_db(self) -> None:
        """
        Load gateway accounts from database into cache.
        
        This is the authoritative data load from the single source of truth.
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Async database operation
            - Principle 9: Rate limited if using external API
        """
        await self._ensure_initialized()
        
        try:
            # Apply rate limiting for database queries
            await self.rate_limiter.acquire()
            
            # Query database for UBEC (Air) token holders
            query = """
                SELECT 
                    account_id,
                    balance,
                    trustline_established,
                    created_at as first_access,
                    last_modified as last_activity,
                    (SELECT COUNT(*) FROM ubec_main.stellar_transactions 
                     WHERE source_account = ubec_balances.account_id 
                     OR destination_account = ubec_balances.account_id) as transaction_count
                FROM ubec_main.ubec_balances
                WHERE asset_code = %s
                ORDER BY balance DESC
            """
            
            results = await self.db_manager.fetch(query, (self.asset_code,))
            
            # Convert to GatewayAccount objects
            self._account_cache.clear()
            
            for row in results:
                # Calculate diversity score (simplified - based on activity)
                diversity_score = min(1.0, row['transaction_count'] / 100.0)
                
                # Determine access level (simplified logic)
                if row['balance'] >= Decimal('10000'):
                    access_level = GatewayAccessLevel.TRUSTED
                elif row['balance'] >= Decimal('1000'):
                    access_level = GatewayAccessLevel.VERIFIED
                else:
                    access_level = GatewayAccessLevel.OPEN
                
                account = GatewayAccount(
                    account_id=row['account_id'],
                    access_level=access_level,
                    balance=Decimal(str(row['balance'])),
                    trustline_established=row['trustline_established'],
                    first_access=row['first_access'],
                    last_activity=row['last_activity'],
                    transaction_count=row['transaction_count'],
                    diversity_score=diversity_score
                )
                
                self._account_cache[account.account_id] = account
            
            # Update cache metadata
            self._cache_timestamp = datetime.now()
            self._last_sync_time = datetime.now()
            self._sync_count += 1
            
            self.logger.info(f"Loaded {len(self._account_cache)} gateway accounts into cache")
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error loading accounts from database: {e}")
            raise
    
    # ==================== GATEWAY OPERATIONS ====================
    # Principle 10: Clear Separation - Gateway business logic
    
    async def sync_gateway_data(self) -> Dict[str, Any]:
        """
        Synchronize gateway data from the database.
        
        Refreshes the in-memory cache with latest data from the database,
        which is the single source of truth.
        
        Returns:
            Dictionary with sync results:
            {
                'accounts_synced': int,
                'sync_time': str (ISO timestamp),
                'cache_size': int,
                'duration_seconds': float
            }
        
        Example:
            >>> result = await service.sync_gateway_data()
            >>> print(f"Synced {result['accounts_synced']} accounts")
        
        Design Notes:
            - Principle 4: Database is single source of truth
            - Principle 5: Async operation
        """
        start_time = datetime.now()
        
        try:
            await self._load_accounts_from_db()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                'accounts_synced': len(self._account_cache),
                'sync_time': self._last_sync_time.isoformat() if self._last_sync_time else None,
                'cache_size': len(self._account_cache),
                'duration_seconds': round(duration, 3)
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Gateway sync failed: {e}")
            raise
    
    async def get_gateway_accounts(self, active_only: bool = False) -> List[GatewayAccount]:
        """
        Get all gateway accounts.
        
        Args:
            active_only: If True, return only recently active accounts (last 30 days)
        
        Returns:
            List of GatewayAccount objects
        
        Example:
            >>> accounts = await service.get_gateway_accounts(active_only=True)
            >>> for account in accounts:
            ...     print(f"{account.account_id}: {account.balance}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring capability
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            accounts = list(self._account_cache.values())
            
            if active_only:
                cutoff = datetime.now() - timedelta(days=30)
                accounts = [a for a in accounts if a.last_activity >= cutoff]
            
            return accounts
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error getting gateway accounts: {e}")
            raise
    
    async def get_gateway_statistics(self) -> GatewayStatistics:
        """
        Calculate comprehensive gateway statistics.
        
        Returns:
            GatewayStatistics object with system-wide metrics
        
        Example:
            >>> stats = await service.get_gateway_statistics()
            >>> print(f"Total accounts: {stats.total_accounts}")
            >>> print(f"Diversity index: {stats.diversity_index:.2f}")
        
        Design Notes:
            - Principle 7: Per-Asset Monitoring with comprehensive metrics
            - Principle 5: Async operation
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            accounts = list(self._account_cache.values())
            total_accounts = len(accounts)
            
            if total_accounts == 0:
                return GatewayStatistics(
                    total_accounts=0,
                    active_accounts=0,
                    total_balance=Decimal('0'),
                    average_balance=Decimal('0'),
                    new_accounts_24h=0,
                    diversity_index=0.0,
                    trustline_adoption_rate=0.0
                )
            
            # Active accounts (activity in last 30 days)
            cutoff_30d = datetime.now() - timedelta(days=30)
            active_accounts = len([a for a in accounts if a.last_activity >= cutoff_30d])
            
            # Balance statistics
            balances = [a.balance for a in accounts]
            total_balance = sum(balances)
            average_balance = total_balance / total_accounts if total_accounts > 0 else Decimal('0')
            
            # New accounts in last 24 hours
            cutoff_24h = datetime.now() - timedelta(hours=24)
            new_accounts_24h = len([a for a in accounts if a.first_access >= cutoff_24h])
            
            # Diversity index (simplified - based on balance distribution)
            diversity_index = self._calculate_diversity_index(balances)
            
            # Trustline adoption
            with_trustlines = len([a for a in accounts if a.trustline_established])
            trustline_adoption_rate = with_trustlines / total_accounts if total_accounts > 0 else 0.0
            
            return GatewayStatistics(
                total_accounts=total_accounts,
                active_accounts=active_accounts,
                total_balance=total_balance,
                average_balance=average_balance,
                new_accounts_24h=new_accounts_24h,
                diversity_index=diversity_index,
                trustline_adoption_rate=trustline_adoption_rate
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error calculating gateway statistics: {e}")
            raise
    
    def _calculate_diversity_index(self, balances: List[Decimal]) -> float:
        """
        Calculate diversity index based on balance distribution.
        
        Higher values indicate more diverse distribution.
        Uses simplified Gini coefficient (0 = perfect equality, 1 = perfect inequality)
        Diversity index = 1 - Gini coefficient
        
        Args:
            balances: List of account balances
            
        Returns:
            Diversity index (0.0 - 1.0)
            
        Design Notes:
            - Principle 12: Single implementation of diversity calculation
        """
        if not balances or len(balances) < 2:
            return 0.0
        
        # Sort balances
        sorted_balances = sorted([float(b) for b in balances])
        n = len(sorted_balances)
        
        # Calculate Gini coefficient
        cumsum = 0
        for i, balance in enumerate(sorted_balances):
            cumsum += (2 * (i + 1) - n - 1) * balance
        
        total = sum(sorted_balances)
        if total == 0:
            return 0.0
        
        gini = cumsum / (n * total)
        
        # Convert to diversity index
        diversity = 1.0 - abs(gini)
        
        return max(0.0, min(1.0, diversity))
    
    async def get_account_info(self, account_id: str) -> Optional[GatewayAccount]:
        """
        Get information for a specific gateway account.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            GatewayAccount object or None if not found
            
        Example:
            >>> account = await service.get_account_info('GXXX...')
            >>> if account:
            ...     print(f"Balance: {account.balance}")
            ...     print(f"Active: {account.last_activity}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            return self._account_cache.get(account_id)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error getting account info: {e}")
            raise
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    # Principle 10: Clear Separation of Concerns
    
    async def close(self) -> None:
        """
        Clean up service resources.
        
        Called during shutdown to release resources and cleanup caches.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("Closing Air protocol service...")
        self._account_cache.clear()
        self._cache_timestamp = None
        self._initialized = False
        self.logger.info("Air protocol service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

def create_ubec_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECProtocolService:
    """
    Factory function to create UBEC Air protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - asset_code: UBEC token code (required)
            - issuer: Issuer address (required)
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options
    
    Returns:
        UBECProtocolService: Initialized service instance
        
    Raises:
        ValueError: If required config parameters are missing
    
    Example:
        >>> # In main.py or service registry
        >>> service = create_ubec_service(
        ...     db_manager=db,
        ...     config={'asset_code': 'UBEC', 'issuer': 'GDPNB7S3...'},
        ...     stellar_client=stellar
        ... )
        >>> health = await service.health_check()
        >>> print(f"Element: {health['details']['element']}")
        >>> print(f"Principle: {health['details']['ubuntu_principle']}")
    """
    # Validate required config parameters
    required_params = ['asset_code', 'issuer']
    
    for param in required_params:
        if param not in config:
            raise ValueError(f"Configuration missing required parameter: '{param}'")
    
    # Create service instance
    service = UBECProtocolService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        rate_limit_calls_per_second=kwargs.get('rate_limit_calls_per_second', 10.0)
    )
    
    # Note: No async initialization needed currently
    # Pattern allows for future async initialization if needed
    
    return service


# ==================== MODULE EXPORTS ====================
# Principle 1: Modular Design - Clear public interface

__all__ = [
    # Enums
    'GatewayAccessLevel',
    
    # Data models
    'GatewayAccount',
    'GatewayStatistics',
    
    # Service
    'UBECProtocolService',
    'create_ubec_service',
    
    # Utilities
    'RateLimiter'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Principle 2: Service Pattern - No standalone execution

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from UBEC_protocol import create_ubec_service\n"
        "  service = create_ubec_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  print(f\"Element: {health['details']['element']}\")\n"
        "  print(f\"Principle: {health['details']['ubuntu_principle']}\")\n"
        "  await service.sync_gateway_data()\n\n"
        "Version 3.0.0 - Complete Element Protocol Implementation:\n"
        "  - Fixed element metadata exposure (air, diversity, UBEC)\n"
        "  - Uses ServiceHealthCheck.element_protocol_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Resolves 'unknown' status issues from critical review\n"
        "  - Full compliance with all 12 design principles\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
