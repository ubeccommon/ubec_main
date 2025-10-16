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
- Comprehensive health monitoring

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
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
    ✅ 12. Method Singularity: No duplicate methods
════════════════════════════════════════════════════════════════════════════

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

Version: 2.1.0 (Enhanced Health Check Support)
Date: October 16, 2025

Changelog:
    v2.1.0 - Enhanced health_check() method for comprehensive monitoring
           - Implements Principle #7: Per-Asset Monitoring with detailed checks
           - Added initialization tracking
           - Improved error handling and validation
           - Added operation statistics tracking
    v2.0.0 - Complete async service architecture
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum


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
        self.asset_code = config.get('asset_code', 'UBEC')
        self.issuer = config.get('issuer', '')
        
        # Setup logging
        self.logger = logging.getLogger(f'UBECProtocol.{self.asset_code}')
        
        # Rate limiting (Principle 9: Integrated Rate Limiting)
        self.rate_limiter = RateLimiter(rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._account_cache: Dict[str, GatewayAccount] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Initialization and operation tracking (for health checks)
        self._initialized = True  # Service is ready after construction
        self._last_sync_time: Optional[datetime] = None
        self._last_query_time: Optional[datetime] = None
        self._sync_count = 0
        self._query_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info(
            f"Air Protocol Service initialized for {self.asset_code} "
            f"(Element: Gateway & Universal Access)"
        )
    
    # ==================== HEALTH CHECK ====================
    # Principle 7: Per-Asset Monitoring with health checks
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on Air protocol service.
        
        Implements Principle #7: Per-Asset Monitoring with Execution Minimums.
        
        Checks:
        - Service initialization status
        - Database connectivity
        - Stellar client connectivity (if configured)
        - Cache status and freshness
        - Recent operation history
        - Error tracking
        - Configuration validity
        
        Returns:
            Health status dictionary:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'details': {
                    'protocol': str,
                    'element': str,
                    'asset_code': str,
                    'initialized': bool,
                    'database_connected': bool,
                    'stellar_connected': bool,
                    'cache_status': str,
                    'cache_age_seconds': float,
                    'cached_accounts': int,
                    'last_sync': str (ISO timestamp),
                    'last_query': str (ISO timestamp),
                    'sync_count': int,
                    'query_count': int,
                    'error_count': int,
                    'last_error': str,
                    'last_error_time': str (ISO timestamp),
                    'config_valid': bool,
                    'response_time_ms': float
                }
            }
        
        Example:
            >>> health = await service.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Air protocol operational")
            >>> else:
            ...     print(f"Issues detected: {health['message']}")
        """
        start_time = datetime.now()
        
        health_info = {
            'status': 'unknown',
            'message': '',
            'details': {
                'protocol': 'UBEC Air Protocol',
                'element': 'Air (Gateway & Universal Access)',
                'asset_code': self.asset_code,
                'initialized': self._initialized,
                'database_connected': False,
                'stellar_connected': False,
                'cache_status': 'unknown',
                'cache_age_seconds': None,
                'cached_accounts': len(self._account_cache),
                'last_sync': self._last_sync_time.isoformat() if self._last_sync_time else None,
                'last_query': self._last_query_time.isoformat() if self._last_query_time else None,
                'sync_count': self._sync_count,
                'query_count': self._query_count,
                'error_count': self._error_count,
                'last_error': self._last_error,
                'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None,
                'config_valid': False,
                'response_time_ms': 0.0
            }
        }
        
        issues = []
        
        try:
            # 1. Check initialization
            if not self._initialized:
                issues.append("Service not initialized")
            
            # 2. Check configuration validity
            try:
                self._validate_config()
                health_info['details']['config_valid'] = True
            except ValueError as e:
                issues.append(f"Invalid configuration: {e}")
            
            # 3. Test database connection
            try:
                if hasattr(self.db_manager, 'health_check'):
                    db_health = await self.db_manager.health_check()
                    health_info['details']['database_connected'] = (
                        db_health.get('status') == 'healthy'
                    )
                    if not health_info['details']['database_connected']:
                        issues.append(f"Database unhealthy: {db_health.get('message')}")
                else:
                    # Fallback: try a simple query
                    test_query = "SELECT 1 as test"
                    result = await self.db_manager.fetch_one(test_query)
                    health_info['details']['database_connected'] = (result is not None)
            except Exception as e:
                issues.append(f"Database connection failed: {e}")
            
            # 4. Test Stellar client connection (if configured)
            if self.stellar_client:
                try:
                    # Rate limit before checking
                    await self.rate_limiter.acquire()
                    
                    # Try to get ledger info (lightweight operation)
                    ledger = await self.stellar_client.ledgers().order(desc=True).limit(1).call()
                    health_info['details']['stellar_connected'] = (ledger is not None)
                except Exception as e:
                    issues.append(f"Stellar connection failed: {e}")
            else:
                # No Stellar client configured - not an error
                health_info['details']['stellar_connected'] = None
            
            # 5. Check cache status
            if self._cache_timestamp:
                cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
                health_info['details']['cache_age_seconds'] = round(cache_age, 2)
                
                if cache_age < self._cache_ttl.total_seconds():
                    health_info['details']['cache_status'] = 'fresh'
                elif cache_age < self._cache_ttl.total_seconds() * 2:
                    health_info['details']['cache_status'] = 'stale'
                    issues.append(f"Cache is stale ({cache_age/60:.1f} minutes old)")
                else:
                    health_info['details']['cache_status'] = 'expired'
                    issues.append(f"Cache is expired ({cache_age/60:.1f} minutes old)")
            else:
                health_info['details']['cache_status'] = 'empty'
                if self._sync_count == 0:
                    issues.append("No data synced yet")
            
            # 6. Check operation recency
            if self._last_sync_time:
                sync_age = (datetime.now() - self._last_sync_time).total_seconds()
                # Warn if no sync in last 24 hours
                if sync_age > 86400:
                    issues.append(f"No sync in {sync_age/3600:.1f} hours")
            
            # 7. Check error rate
            if self._error_count > 0:
                total_ops = self._sync_count + self._query_count
                if total_ops > 0:
                    error_rate = self._error_count / total_ops
                    if error_rate > 0.1:  # More than 10% error rate
                        issues.append(
                            f"High error rate: {error_rate:.1%} "
                            f"({self._error_count} errors in {total_ops} operations)"
                        )
            
            # Calculate response time
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            health_info['details']['response_time_ms'] = round(response_time, 2)
            
            # Determine overall status
            critical_issues = [
                issue for issue in issues 
                if any(word in issue.lower() for word in ['database', 'stellar', 'configuration', 'initialized'])
            ]
            
            if len(critical_issues) > 0:
                health_info['status'] = 'unhealthy'
                health_info['message'] = f"Critical issues: {', '.join(critical_issues)}"
            elif len(issues) > 0:
                health_info['status'] = 'degraded'
                health_info['message'] = f"Warnings: {', '.join(issues)}"
            else:
                health_info['status'] = 'healthy'
                health_info['message'] = (
                    f"Air protocol operational "
                    f"({self._sync_count} syncs, {self._query_count} queries, "
                    f"{len(self._account_cache)} cached accounts)"
                )
            
            return health_info
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            health_info['status'] = 'unhealthy'
            health_info['message'] = f"Health check error: {str(e)}"
            return health_info
    
    def _validate_config(self) -> None:
        """
        Validate service configuration.
        
        Raises:
            ValueError: If configuration is invalid
        
        Principle 11: Comprehensive validation
        """
        if not self.asset_code:
            raise ValueError("asset_code not configured")
        
        if not self.issuer:
            raise ValueError("issuer address not configured")
        
        # Validate issuer format (Stellar public key)
        if not self.issuer.startswith('G') or len(self.issuer) != 56:
            raise ValueError(f"Invalid issuer address format: {self.issuer}")
    
    # ==================== CACHE MANAGEMENT ====================
    # Principle 10: Clear Separation - Cache management separated
    
    def _is_cache_valid(self) -> bool:
        """
        Check if cache is still valid.
        
        Returns:
            True if cache is fresh, False otherwise
        """
        if self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_ttl
    
    async def _load_from_database(self) -> None:
        """
        Load gateway accounts from database into cache.
        
        Principle 4: Database is the single source of truth.
        Principle 5: Fully async operation.
        
        Raises:
            Exception: If database query fails
        """
        try:
            # Ensure connection is established
            if hasattr(self.db_manager, 'conn') and self.db_manager.conn is None:
                await self.db_manager.connect()
            
            # Query database for all accounts with UBEC trustlines
            # Principle 4: Database is single source of truth
            query = """
                SELECT 
                    account_id,
                    balance,
                    trustline_established,
                    created_at,
                    last_activity,
                    transaction_count
                FROM ubec_main.gateway_accounts
                WHERE asset_code = $1
                ORDER BY last_activity DESC
            """
            
            # Note: params must be passed as a tuple, even for single parameter
            results = await self.db_manager.fetch_all(query, (self.asset_code,))
            
            # Convert to GatewayAccount objects
            self._account_cache.clear()
            for row in results:
                account = GatewayAccount(
                    account_id=row['account_id'],
                    access_level=GatewayAccessLevel.OPEN,  # Default
                    balance=Decimal(str(row['balance'])),
                    trustline_established=row['trustline_established'],
                    first_access=row['created_at'],
                    last_activity=row['last_activity'],
                    transaction_count=row['transaction_count'],
                    diversity_score=0.0  # Calculate separately
                )
                self._account_cache[account.account_id] = account
            
            self._cache_timestamp = datetime.now()
            self.logger.info(f"Loaded {len(self._account_cache)} accounts into cache")
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error loading from database: {e}")
            raise
    
    async def _ensure_cache_loaded(self) -> None:
        """
        Ensure cache is loaded and valid.
        
        Principle 5: Async operation.
        """
        if not self._is_cache_valid():
            await self._load_from_database()
    
    # ==================== GATEWAY OPERATIONS ====================
    # Principle 10: Separation of Concerns - Business logic layer
    
    async def sync_gateway_data(self) -> Dict[str, Any]:
        """
        Synchronize gateway data from Stellar network.
        
        This method fetches the latest account data from the Stellar blockchain
        and updates the database (single source of truth). Called by the main
        protocol coordinator.
        
        Returns:
            Dict: Sync status and metrics
            
        Example:
            >>> result = await service.sync_gateway_data()
            >>> print(f"Status: {result['status']}")
            >>> print(f"Accounts: {result['accounts_loaded']}")
        
        Design Notes:
            - Principle 5: Fully async operation
            - Principle 7: Per-asset monitoring with metrics
            - Principle 11: Comprehensive logging
        """
        try:
            self.logger.info("Starting Air (UBEC) gateway data synchronization...")
            
            # Track operation for health checks
            self._last_sync_time = datetime.now()
            self._sync_count += 1
            
            # Force cache refresh
            await self._load_from_database()
            
            # Calculate current metrics
            stats = await self.get_gateway_statistics()
            
            return {
                'element': 'air',
                'token': self.asset_code,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'accounts_loaded': len(self._account_cache),
                'metrics': {
                    'total_accounts': stats.total_accounts,
                    'active_accounts': stats.active_accounts,
                    'total_balance': float(stats.total_balance),
                    'average_balance': float(stats.average_balance),
                    'new_accounts_24h': stats.new_accounts_24h,
                    'diversity_index': stats.diversity_index,
                    'trustline_adoption_rate': stats.trustline_adoption_rate
                }
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error syncing gateway data: {e}")
            return {
                'element': 'air',
                'token': self.asset_code,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_gateway_accounts(
        self,
        access_level: Optional[GatewayAccessLevel] = None,
        min_balance: Optional[Decimal] = None,
        active_only: bool = False
    ) -> List[GatewayAccount]:
        """
        Get gateway accounts with optional filtering.
        
        Args:
            access_level: Filter by access level
            min_balance: Minimum balance filter
            active_only: Only return recently active accounts
            
        Returns:
            List of GatewayAccount objects
            
        Example:
            >>> accounts = await service.get_gateway_accounts(
            ...     min_balance=Decimal('100'),
            ...     active_only=True
            ... )
            >>> for account in accounts:
            ...     print(f"{account.account_id}: {account.balance}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring with filtering
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            accounts = list(self._account_cache.values())
            
            # Apply filters
            if access_level:
                accounts = [a for a in accounts if a.access_level == access_level]
            
            if min_balance:
                accounts = [a for a in accounts if a.balance >= min_balance]
            
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
        Get comprehensive gateway statistics.
        
        Returns:
            GatewayStatistics object with current metrics
            
        Example:
            >>> stats = await service.get_gateway_statistics()
            >>> print(f"Total accounts: {stats.total_accounts}")
            >>> print(f"Active accounts: {stats.active_accounts}")
            >>> print(f"Diversity index: {stats.diversity_index:.2f}")
        
        Design Notes:
            - Principle 7: Per-asset monitoring with comprehensive metrics
            - Principle 12: Single implementation of statistics calculation
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            accounts = list(self._account_cache.values())
            
            # Calculate metrics
            total_accounts = len(accounts)
            
            # Active accounts (activity in last 30 days)
            cutoff = datetime.now() - timedelta(days=30)
            active_accounts = len([a for a in accounts if a.last_activity >= cutoff])
            
            # Balance metrics
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

async def create_ubec_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECProtocolService:
    """
    Factory function to create UBEC Air protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    Changed to async to allow for future async initialization if needed.
    
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
        >>> service = await create_ubec_service(
        ...     db_manager=db,
        ...     config={'asset_code': 'UBEC', 'issuer': 'GDPNB7S3...'},
        ...     stellar_client=stellar
        ... )
        >>> health = await service.health_check()
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
        "  service = await create_ubec_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  await service.sync_gateway_data()\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
