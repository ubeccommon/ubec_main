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
- Async factory function for proper initialization
- Database as single source of truth
- Built-in rate limiting
- In-memory caching with TTL
- Comprehensive health monitoring using ServiceHealthCheck utility
- Database-driven sync status (fixes "needs_sync" issue)

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained service with clear boundaries
    ✅ 2.  Service Pattern: No standalone execution, async factory-based instantiation
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
    
    # Factory is now async and handles initialization
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

Version: 3.3.0 (Critical Factory Initialization Fix - ACTUALLY ASYNC NOW)
Date: October 23, 2025

Changelog:
    v3.3.0 - CRITICAL FIX: Factory function is NOW ACTUALLY ASYNC
           - FIXED: Changed factory from `def` to `async def` (line 888)
           - FIXED: Added `await service.initialize()` call before return (line 965)
           - FIXED: Documentation now accurately reflects actual implementation
           - Resolves BUG #1 from critical review: "initialized: false" health check issue
           - Resolves BUG #2 implications: Earth/Fire not initializing (same pattern)
           - Service now GUARANTEED to be fully initialized when factory returns
           - Principle #2: Proper async service pattern NOW CORRECTLY IMPLEMENTED
           - Principle #5: Strict async operations INCLUDING factory
           - This version actually does what v3.2.0 CLAIMED to do but didn't
    v3.2.0 - DOCUMENTATION ONLY (code didn't match claims - fixed in v3.3.0)
           - Claimed to make factory async but factory was still `def` not `async def`
           - Claimed to call initialize() but code just returned service without calling it
           - Comments were correct but implementation was wrong
           - v3.3.0 ACTUALLY implements what this version claimed
    v3.1.4 - CRITICAL FIX: Timezone awareness correction
           - FIXED: Added timezone import and changed datetime.now() to datetime.now(timezone.utc)
           - Resolves "can't subtract offset-naive and offset-aware datetimes" error
           - Ensures consistent timezone-aware datetime usage throughout
           - 18 datetime.now() calls updated for UTC timezone awareness
           - Principle #5: Proper async datetime handling maintained
    v3.1.3 - CRITICAL FIX: Column name correction
           - FIXED: Changed column name from synced_at to last_updated
           - Resolves "column synced_at does not exist" error
           - Now matches actual database schema and other protocols
           - Principle #4: Database as Single Source of Truth compliance
    v3.1.2 - CRITICAL FIX: Database table and parameter correction
           - FIXED: Changed table ubec_main.balances to account_balances and to fetch_one() for AsyncDatabaseManager compatibility
           - FIXED: Changed fetch_one(query, asset_code) to fetch_one(query, (asset_code,)) in _get_sync_status_from_db()
           - Resolves table not found and parameter passing errors throughout the service
           - Both table name and parameter tuple format corrected
           - Principle #5: Strict Async Operations compliance maintained
    v3.1.0 - CRITICAL FIX: Database-driven sync status for health checks
           - Added _get_sync_status_from_db() method to query database directly
           - Updated health_check() to use database queries instead of instance variables
           - Fixes issue where protocols show "needs_sync" after successful sync
           - Implements Principle #4: Database as Single Source of Truth
           - Resolves disconnect between synchronizer and protocol status
           - Health checks now reflect actual database state
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
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
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
        1. Instantiate via create_ubec_service() async factory
        2. Factory automatically calls initialize()
        3. Cleanup via close() method
        
    Design Principles:
        - Principle 1: Modular - Clear boundaries and single responsibility
        - Principle 2: Service Pattern - Async factory with proper initialization
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
        Construct UBEC Air protocol service.
        
        DO NOT call directly - use create_ubec_service() async factory instead.
        The factory will call initialize() to complete setup.
        
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
        
        # FIXED: Changed log message to accurately reflect service state
        # Previously said "initialized" but service is only constructed at this point
        self.logger.info(
            f"Air Protocol Service constructed for {self.asset_code} "
            f"(Element: {self.element_description}) - call initialize() to complete setup"
        )
    
    # ==================== INITIALIZATION ====================
    # Principle 5: Strict Async Operations
    
    async def initialize(self) -> None:
        """
        Initialize the service and verify database connectivity.
        
        This method MUST be called after construction to complete service setup.
        The create_ubec_service() factory handles this automatically.
        
        Sets self._initialized = True on successful initialization.
        
        Design Notes:
            - Principle 5: Async initialization
            - Principle 4: Verifies database connection (single source of truth)
            - CRITICAL FIX: This method sets _initialized flag that health checks depend on
        """
        if self._initialized:
            self.logger.debug("Service already initialized, skipping")
            return
        
        self.logger.info("Initializing Air protocol service...")
        
        try:
            # Verify database connection (Principle 4: Single Source of Truth)
            await self.db_manager.execute("SELECT 1")
            
            # CRITICAL: Set initialization flag
            self._initialized = True
            
            # Log successful initialization
            self.logger.info(
                f"✓ Air protocol service initialized successfully\n"
                f"  Asset: {self.asset_code}\n"
                f"  Issuer: {self.issuer[:12]}...\n"
                f"  Element: {self.element} ({self.symbol})\n"
                f"  Principle: {self.ubuntu_principle}\n"
                f"  Schema: {self.db_manager.schema if hasattr(self.db_manager, 'schema') else 'default'}"
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Failed to initialize Air protocol: {e}")
            raise
    
    async def _ensure_initialized(self) -> None:
        """
        Ensure service is initialized before operations.
        
        This is a safety check for operations that require initialization.
        Normally, the factory ensures initialization, but this provides
        an additional safeguard.
        """
        if not self._initialized:
            await self.initialize()
    
    # ==================== DATABASE SYNC STATUS ====================
    # Principle 4: Single Source of Truth - Database queries for actual status
    # CRITICAL FIX: Query database instead of using instance variables
    
    async def _get_sync_status_from_db(self) -> Tuple[Optional[datetime], int]:
        """
        Query database for actual synchronization status.
        
        This method implements the critical fix for the sync status issue.
        Instead of relying on in-memory instance variables that may be out of
        sync with reality, this queries the database directly to get the actual
        last sync time and account count.
        
        The database is the single source of truth (Principle #4), so this
        ensures health checks always reflect the actual system state, even
        when the synchronizer service updates data independently.
        
        Returns:
            Tuple of (last_sync_timestamp, account_count):
                - last_sync_timestamp: Most recent last_updated timestamp or None
                - account_count: Number of distinct accounts in database
        
        Design Notes:
            - Principle 4: Database as Single Source of Truth
            - Principle 5: Async database query
            - Principle 12: Single implementation (no duplication)
            - This fixes the disconnect between synchronizer and protocol services
        
        Example:
            >>> last_sync, count = await service._get_sync_status_from_db()
            >>> if last_sync:
            ...     print(f"Data synced {(datetime.now(timezone.utc) - last_sync).seconds}s ago")
            >>> print(f"{count} accounts in database")
        """
        try:
            # Query for most recent sync time and distinct account count
            # This reflects what the synchronizer actually wrote to the database
            query = """
                SELECT 
                    MAX(last_updated) as last_sync,
                    COUNT(DISTINCT account_id) as account_count
                FROM ubec_main.account_balances
                WHERE asset_code = $1
            """
            
            row = await self.db_manager.fetch_one(query, (self.asset_code,))
            
            if row and row['last_sync']:
                return (row['last_sync'], int(row['account_count']))
            else:
                return (None, 0)
                
        except Exception as e:
            self.logger.error(f"Error querying sync status from database: {e}")
            # On error, return None to indicate unknown status
            return (None, 0)
    
    # ==================== HEALTH CHECK ====================
    # Principle 12: Method Singularity - Uses ServiceHealthCheck utility
    # Principle 7: Per-Asset Monitoring - Comprehensive health data
    # CRITICAL FIX: Uses database queries instead of instance variables
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for Air protocol service.
        
        Uses standardized ServiceHealthCheck utility for consistency across
        all services, implementing Principle #12 (Method Singularity).
        
        CRITICAL FIX v3.3.0: Factory now ACTUALLY async and ACTUALLY calls initialize(),
        so this health check will correctly report initialized: true.
        
        CRITICAL FIX v3.1.0: This method queries the database directly
        for sync status instead of using instance variables. This ensures
        health checks always reflect the actual database state, even when
        the synchronizer service updates data without notifying the protocol.
        
        This implementation follows the element protocol health check pattern,
        which includes:
        - Element-specific metadata (air, diversity, UBEC)
        - Database connectivity validation
        - Cache status and freshness
        - Operational statistics
        - Error tracking
        - ACTUAL sync status from database (not stale instance variables)
        
        Returns:
            Health status dictionary from ServiceHealthCheck utility:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy' | 'unknown',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,  # Now correctly reports true after factory init
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
            >>> print(f"Accounts: {health['details']['cached_accounts']}")
            >>> print(f"Initialized: {health['details']['initialized']}")  # Now true!
        
        Design Notes:
            - Principle 4: Queries database for authoritative sync status
            - Principle 7: Comprehensive per-asset monitoring
            - Principle 12: Delegates to ServiceHealthCheck utility (no duplication)
            - This implementation ensures element metadata is properly exposed
            - Fixes the "needs_sync" issue by using database as truth source
            - Fixes the "initialized: false" issue with proper factory initialization
        """
        # CRITICAL FIX: Query database for actual sync status
        # This replaces the previous use of self._last_sync_time and len(self._account_cache)
        # which were only updated when the protocol's own methods were called
        last_sync_db, account_count_db = await self._get_sync_status_from_db()
        
        # Use the standardized element protocol health check
        # This resolves the "unknown" status issue identified in the review
        return await ServiceHealthCheck.element_protocol_health(
            element_name=self.element,
            token_code=self.asset_code,
            db_manager=self.db_manager,
            is_initialized=self._initialized,  # ✅ Now properly set by factory
            last_sync=last_sync_db,  # ✅ FROM DATABASE (not self._last_sync_time)
            cached_accounts=account_count_db,  # ✅ FROM DATABASE (not len(self._account_cache))
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
        now = datetime.now(timezone.utc)
        
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
                     WHERE source_account = account_balances.account_id 
                     OR destination_account = account_balances.account_id) as transaction_count
                FROM ubec_main.account_balances
                WHERE asset_code = $1
                ORDER BY balance DESC
            """
            
            results = await self.db_manager.fetch(query, self.asset_code)
            
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
            self._cache_timestamp = datetime.now(timezone.utc)
            self._last_sync_time = datetime.now(timezone.utc)
            self._sync_count += 1
            
            self.logger.info(f"Loaded {len(self._account_cache)} gateway accounts into cache")
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
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
        start_time = datetime.now(timezone.utc)
        
        try:
            await self._load_accounts_from_db()
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return {
                'accounts_synced': len(self._account_cache),
                'sync_time': self._last_sync_time.isoformat() if self._last_sync_time else None,
                'cache_size': len(self._account_cache),
                'duration_seconds': round(duration, 3)
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
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
            self._last_query_time = datetime.now(timezone.utc)
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            accounts = list(self._account_cache.values())
            
            if active_only:
                cutoff = datetime.now(timezone.utc) - timedelta(days=30)
                accounts = [a for a in accounts if a.last_activity >= cutoff]
            
            return accounts
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
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
            self._last_query_time = datetime.now(timezone.utc)
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
            cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)
            active_accounts = len([a for a in accounts if a.last_activity >= cutoff_30d])
            
            # Balance statistics
            balances = [a.balance for a in accounts]
            total_balance = sum(balances)
            average_balance = total_balance / total_accounts if total_accounts > 0 else Decimal('0')
            
            # New accounts in last 24 hours
            cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
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
            self._last_error_time = datetime.now(timezone.utc)
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
            self._last_query_time = datetime.now(timezone.utc)
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            return self._account_cache.get(account_id)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
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
# Principle 2: Service Pattern - Async factory for proper initialization

async def create_ubec_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECProtocolService:
    """
    Async factory function to create and initialize UBEC Air protocol service.
    
    CRITICAL FIX v3.3.0: Factory is NOW ACTUALLY ASYNC (async def, not def)
    and ACTUALLY calls await service.initialize() before returning.
    
    This fixes BUG #1 from the critical review: "Missing Air Service in Status Mode"
    which was caused by the service reporting initialized=false because the
    factory never actually called initialize().
    
    Previous version (3.2.0) CLAIMED to do this but the implementation was wrong:
    - Factory was still `def` not `async def`  
    - Factory just returned service without calling initialize()
    - Comments said it was async but code wasn't
    
    This version ACTUALLY implements what v3.2.0 claimed to do.
    
    This is the ONLY proper way to instantiate the service for use in the
    service registry.
    
    Principle 2: Service pattern with async factory function.
    Principle 3: Dependencies injected via service registry.
    Principle 5: Async initialization ensures proper setup.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - asset_code: UBEC token code (required)
            - issuer: Issuer address (required)
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options including:
            - rate_limit_calls_per_second: API rate limit (default: 10.0)
    
    Returns:
        UBECProtocolService: Fully initialized service instance with _initialized = True
        
    Raises:
        ValueError: If required config parameters are missing
        Exception: If initialization fails
    
    Example:
        >>> # In main.py or service registry
        >>> service = await create_ubec_service(
        ...     db_manager=db,
        ...     config={'asset_code': 'UBEC', 'issuer': 'GDPNB7S3...'},
        ...     stellar_client=stellar
        ... )
        >>> # Service is now fully initialized and ready
        >>> health = await service.health_check()
        >>> assert health['details']['initialized'] == True  # Now passes!
        >>> print(f"Element: {health['details']['element']}")
        >>> print(f"Accounts: {health['details']['cached_accounts']}")
    
    Design Notes:
        - CRITICAL: Factory MUST be async to call initialize()
        - CRITICAL: Must call await service.initialize() before returning
        - This fixes BUG #1: "initialized: false" issue from the critical review
        - This fixes BUG #2 implications: Earth/Fire likely have same issue
        - Service is guaranteed to be ready when factory returns
        - v3.3.0 ACTUALLY implements what v3.2.0 documentation claimed
    """
    # Validate required config parameters
    required_params = ['asset_code', 'issuer']
    
    for param in required_params:
        if param not in config:
            raise ValueError(
                f"Configuration missing required parameter: '{param}'. "
                f"Required: {required_params}"
            )
    
    # Create service instance (constructs but does not initialize)
    service = UBECProtocolService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        rate_limit_calls_per_second=kwargs.get('rate_limit_calls_per_second', 10.0)
    )
    
    # CRITICAL FIX v3.3.0: ACTUALLY call initialize() to complete service setup
    # This sets _initialized = True and verifies database connectivity
    # v3.2.0 documentation claimed this happened but code just returned service
    # without calling initialize() - that bug is NOW FIXED in v3.3.0
    await service.initialize()
    
    # Return fully initialized service
    return service


# ==================== REGISTRY INTEGRATION ====================
# Standardized pattern for service registry registration

def register_factory(registry, name: str = 'air', **dependencies):
    """
    Register this service with the service registry using standardized pattern.
    
    This is the proper way to register the Air protocol service with the
    service registry, ensuring all dependencies are properly injected.
    
    CRITICAL: The factory function is async, so the service registry must
    support async factory functions. The registry will await the factory
    when creating service instances.
    
    Args:
        registry: The service registry instance
        name: Service name (default: 'air')
        **dependencies: Dependency service names (database, config, stellar_client)
    
    Example:
        >>> from core.service_registry import ServiceRegistry
        >>> registry = ServiceRegistry()
        >>> 
        >>> # Register dependencies first
        >>> registry.register('database', db_manager)
        >>> registry.register('config', config_service)
        >>> registry.register('stellar_client', stellar_service)
        >>> 
        >>> # Register Air protocol
        >>> register_factory(
        ...     registry,
        ...     name='air',
        ...     database='database',
        ...     config='config',
        ...     stellar_client='stellar_client'
        ... )
    
    Design Notes:
        - Principle 3: Service Registry integration
        - Factory function is async and handles initialization
        - Dependencies injected by registry
        - Registry must support async factories (await the factory call)
    """
    registry.register(
        name=name,
        factory=create_ubec_service,
        dependencies=[
            dependencies.get('database', 'database'),
            dependencies.get('config', 'config'),
            dependencies.get('stellar_client', 'stellar_client')
        ]
    )


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
    'register_factory',
    
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
        "  service = await create_ubec_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  print(f\"Initialized: {health['details']['initialized']}\")  # Now true!\n"
        "  print(f\"Element: {health['details']['element']}\")\n"
        "  print(f\"Accounts: {health['details']['cached_accounts']}\")\n"
        "  await service.sync_gateway_data()\n\n"
        "Version 3.3.0 - CRITICAL Factory Initialization Fix (ACTUALLY ASYNC NOW):\n"
        "  - FIXED: Factory changed from `def` to `async def` (was claimed in v3.2.0)\n"
        "  - FIXED: Factory now calls `await service.initialize()` (was claimed in v3.2.0)\n"
        "  - v3.2.0 documentation was correct but implementation was wrong\n"
        "  - v3.3.0 implementation NOW MATCHES v3.2.0 documentation\n"
        "  - Service is GUARANTEED to be fully initialized (_initialized = True)\n"
        "  - Fixes BUG #1 from critical review: 'initialized: false' health check issue\n"
        "  - Fixes BUG #2 implications: Earth/Fire likely have same pattern issue\n"
        "  - Implements Principle #2: Proper async service pattern\n"
        "  - Implements Principle #5: Strict async operations INCLUDING factory\n\n"
        "Version 3.1.0 - Database-Driven Sync Status (Critical Fix):\n"
        "  - Added _get_sync_status_from_db() method for database queries\n"
        "  - Updated health_check() to use database instead of instance variables\n"
        "  - Fixes 'needs_sync' issue after successful synchronization\n"
        "  - Implements Principle #4: Database as Single Source of Truth\n"
        "  - Resolves disconnect between synchronizer and protocol services\n"
        "  - Health checks now always reflect actual database state\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
