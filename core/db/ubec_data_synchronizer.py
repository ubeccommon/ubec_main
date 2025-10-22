#!/usr/bin/env python3
"""
UBEC Data Synchronizer - Complete Async Implementation
=======================================================

Synchronizes UBEC token family data from the Stellar blockchain to the PostgreSQL database.
Handles all four UBEC tokens: UBEC (Air), UBECrc (Water), UBECgpi (Earth), UBECtt (Fire).

This module implements the service pattern with:
- Pure async operations (no sync fallbacks)
- Database as single source of truth
- Rate limiting with circuit breaker
- Comprehensive health monitoring
- Stellar Horizon API integration

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained synchronizer with clear boundaries
    ✅ 2.  Service Pattern: Factory-based instantiation, no standalone execution
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Per-token health and sync tracking
    ✅ 8.  No Duplicate Config: Uses database configuration
    ✅ 9.  Rate Limiting: Built-in rate limiting with circuit breaker
    ✅ 10. Separation of Concerns: Sync logic separated from data access
    ✅ 11. Documentation: Comprehensive docstrings and inline comments
    ✅ 12. Method Singularity: Uses ServiceHealthCheck utility
════════════════════════════════════════════════════════════════════════════

Usage:
    # Via service registry (RECOMMENDED)
    registry = ServiceRegistry()
    sync = await registry.get('synchronizer')
    
    # Discover holders
    count = await sync.discover_accounts('UBEC', max_accounts=1000)
    
    # Sync specific account
    await sync.sync_account('GACCOUNT...', asset_code='UBEC')
    
    # Sync all data (standardized method name)
    results = await sync.sync_all()
    
    # Sync all tokens (legacy method name)
    results = await sync.sync_all_tokens()
    
    # Health check
    health = await sync.health_check()
    
    await sync.close()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.0.0 (Registry Integration + Method Standardization)
Date: October 21, 2025

Changelog:
    v3.0.0 - Added register_factory pattern for service registry
           - Added sync_all() method (standardized interface)
           - Complete implementation of all methods
           - Enhanced error handling and logging
           - Full ServiceHealthCheck integration
    v2.0.0 - Complete async implementation with enhanced health check
           - Implements all 12 design principles
           - Uses ServiceHealthCheck utility (Principle #12)
           - Added rate limiting with circuit breaker (Principle #9)
    v1.0.0 - Initial synchronizer implementation
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass

# Stellar SDK async imports (Principle #5: Strict Async)
# Handle different import paths across Stellar SDK versions
try:
    from stellar_sdk import ServerAsync, Asset, Account
    from stellar_sdk.exceptions import NotFoundError, BadRequestError
    
    # Try multiple import paths for AiohttpClient (varies by version)
    try:
        from stellar_sdk import AiohttpClient  # v9.0.0+
    except ImportError:
        try:
            from stellar_sdk.client.aiohttp_client import AiohttpClient  # v8.x
        except ImportError:
            from stellar_sdk.aiohttp_client import AiohttpClient  # v7.x
    
    STELLAR_SDK_AVAILABLE = True
except ImportError as e:
    STELLAR_SDK_AVAILABLE = False
    STELLAR_SDK_IMPORT_ERROR = str(e)
    # Define placeholder classes for when SDK is not installed
    ServerAsync = None
    AiohttpClient = None
    Asset = None
    Account = None
    NotFoundError = Exception
    BadRequestError = Exception

# Project imports (Principle #3: Service Registry access)
from core.utils.service_health import ServiceHealthCheck  # Principle #12

# Configure module logger
logger = logging.getLogger('UBECDataSynchronizer')


# ==================== RATE LIMITER WITH CIRCUIT BREAKER ====================
# Principle #9: Integrated Rate Limiting

@dataclass
class RateLimiterMetrics:
    """Metrics for rate limiter performance"""
    total_requests: int = 0
    rate_limited_requests: int = 0
    retry_attempts: int = 0
    current_remaining: int = 0
    current_limit: int = 0
    circuit_breaker_state: str = 'closed'
    circuit_breaker_failures: int = 0


class RateLimiterWithCircuitBreaker:
    """
    Rate limiter with circuit breaker for Stellar Horizon API.
    
    Implements token bucket with adaptive rate limiting and circuit breaker
    to prevent overwhelming the API during outages.
    
    Principle #9: Integrated Rate Limiting
    Principle #5: Strict Async operations
    """
    
    def __init__(
        self,
        calls_per_second: float = 10.0,
        burst_size: int = 20,
        circuit_breaker_threshold: int = 10,
        circuit_breaker_timeout: int = 300  # 5 minutes
    ):
        """
        Initialize rate limiter with circuit breaker.
        
        Args:
            calls_per_second: Sustained rate limit
            burst_size: Maximum burst before limiting
            circuit_breaker_threshold: Failures before opening circuit
            circuit_breaker_timeout: Seconds to wait before retrying
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.burst_size = burst_size
        
        # Circuit breaker
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.circuit_state = 'closed'  # closed, open, half_open
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        
        # Token bucket
        self.tokens = float(burst_size)
        self.last_update = datetime.now()
        
        # Metrics
        self.metrics = RateLimiterMetrics(
            current_limit=int(calls_per_second),
            current_remaining=burst_size
        )
        
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Acquire permission to make an API call.
        
        Implements token bucket with circuit breaker protection.
        
        Principle #5: Async sleep, not blocking
        """
        async with self._lock:
            # Check circuit breaker
            if self.circuit_state == 'open':
                # Check if timeout has expired
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.circuit_breaker_timeout:
                        self.circuit_state = 'half_open'
                        self.failure_count = 0
                    else:
                        self.metrics.circuit_breaker_state = 'open'
                        raise Exception(
                            f"Circuit breaker is OPEN. "
                            f"Retry in {int(self.circuit_breaker_timeout - elapsed)}s"
                        )
            
            # Refill tokens based on time elapsed
            now = datetime.now()
            elapsed = (now - self.last_update).total_seconds()
            self.tokens = min(
                self.burst_size,
                self.tokens + elapsed * self.calls_per_second
            )
            self.last_update = now
            
            # Wait if no tokens available
            if self.tokens < 1.0:
                wait_time = (1.0 - self.tokens) / self.calls_per_second
                self.metrics.rate_limited_requests += 1
                await asyncio.sleep(wait_time)
                self.tokens = 1.0
            
            # Consume token
            self.tokens -= 1.0
            self.metrics.total_requests += 1
            self.metrics.current_remaining = int(self.tokens)
    
    def record_success(self) -> None:
        """Record successful API call (resets circuit breaker)"""
        if self.circuit_state == 'half_open':
            self.circuit_state = 'closed'
            self.failure_count = 0
            logger.info("Circuit breaker closed after successful call")
        
        self.metrics.circuit_breaker_state = self.circuit_state
    
    def record_failure(self) -> None:
        """Record failed API call (may open circuit breaker)"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.metrics.circuit_breaker_failures = self.failure_count
        
        if self.failure_count >= self.circuit_breaker_threshold:
            self.circuit_state = 'open'
            self.metrics.circuit_breaker_state = 'open'
            logger.error(
                f"Circuit breaker OPENED after {self.failure_count} failures. "
                f"Will retry in {self.circuit_breaker_timeout}s"
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current rate limiter metrics"""
        return {
            'total_requests': self.metrics.total_requests,
            'rate_limited_requests': self.metrics.rate_limited_requests,
            'retry_attempts': self.metrics.retry_attempts,
            'current_remaining': self.metrics.current_remaining,
            'current_limit': self.metrics.current_limit,
            'circuit_breaker_state': self.metrics.circuit_breaker_state,
            'circuit_breaker_failures': self.metrics.circuit_breaker_failures
        }


# ==================== UBEC DATA SYNCHRONIZER ====================
# Principle #1: Modular Design with clear boundaries

class UBECDataSynchronizer:
    """
    UBEC Data Synchronizer - Blockchain to Database Synchronization.
    
    Synchronizes UBEC token family data from Stellar blockchain to PostgreSQL,
    implementing all 12 design principles with comprehensive health monitoring.
    
    Attributes:
        db: AsyncDatabaseManager instance (Principle #4: Single Source of Truth)
        settings: Database-backed configuration (Principle #8: No Duplicate Config)
        rate_limiter: Rate limiter with circuit breaker (Principle #9)
        server: Stellar Horizon server client (Principle #5: Async operations)
    
    Principle Compliance:
        - #1: Self-contained module with clear boundaries
        - #2: Factory-based instantiation only
        - #3: Accessed through service registry
        - #4: Database is single source of truth
        - #5: All operations are async/await
        - #6: No sync fallbacks anywhere
        - #7: Per-asset monitoring and tracking
        - #8: Configuration from database only
        - #9: Integrated rate limiting with circuit breaker
        - #10: Clear separation of sync logic from data access
        - #11: Comprehensive documentation throughout
        - #12: Uses ServiceHealthCheck utility
    """
    
    # UBEC token family configuration
    VALID_UBEC_TOKENS = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']
    ELEMENT_MAP = {
        'UBEC': 'Air',
        'UBECrc': 'Water',
        'UBECgpi': 'Earth',
        'UBECtt': 'Fire'
    }
    
    def __init__(
        self,
        db_manager,
        rate_limit_per_second: float = 10.0
    ):
        """
        Initialize UBEC Data Synchronizer.
        
        Args:
            db_manager: AsyncDatabaseManager instance
            rate_limit_per_second: Stellar API rate limit (default: 10/sec)
        
        Note:
            Call initialize() after instantiation to complete setup.
            
        Principle #2: Service Pattern - Use factory function, not direct instantiation
        Principle #5: Async initialization pattern
        """
        self.db = db_manager
        self.logger = logger
        
        # Initialization state
        self.initialized = False
        self.settings: Dict[str, Any] = {}
        
        # Rate limiting (Principle #9)
        self.rate_limiter = RateLimiterWithCircuitBreaker(
            calls_per_second=rate_limit_per_second,
            burst_size=int(rate_limit_per_second * 2),
            circuit_breaker_threshold=10,
            circuit_breaker_timeout=300
        )
        
        # Stellar API client (Principle #5: Async)
        self.server: Optional[ServerAsync] = None
        self.horizon_url: Optional[str] = None
        self.network: Optional[str] = None
        
        # Monitoring metrics (Principle #7: Per-Asset Monitoring)
        self._sync_operations_count = 0
        self._last_sync_time: Optional[datetime] = None
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        # Per-token metrics
        self._token_metrics: Dict[str, Dict[str, Any]] = {
            token: {
                'accounts_synced': 0,
                'last_sync': None,
                'errors': 0,
                'last_error': None
            }
            for token in self.VALID_UBEC_TOKENS
        }
    
    # ==================== INITIALIZATION ====================
    # Principle #5: Strict Async Operations
    
    async def initialize(self) -> None:
        """
        Initialize synchronizer with database configuration.
        
        Loads settings from database and creates Stellar API client.
        
        Principle #4: Single Source of Truth - database configuration
        Principle #5: Strict Async - all operations use async/await
        Principle #8: No Duplicate Config - settings from database only
        
        Raises:
            Exception: If Stellar SDK not available or initialization fails
        """
        if self.initialized:
            self.logger.warning("Synchronizer already initialized")
            return
        
        # Check Stellar SDK availability
        if not STELLAR_SDK_AVAILABLE:
            raise Exception(
                f"Stellar SDK not available: {STELLAR_SDK_IMPORT_ERROR}. "
                "Install with: pip install stellar-sdk"
            )
        
        # Load settings from database (Principle #4 & #8)
        self.settings = await self._load_settings_from_database()
        
        # Extract critical settings
        self.horizon_url = self.settings.get('horizon_url')
        self.network = self.settings.get('network', 'public')
        
        if not self.horizon_url:
            raise ValueError("horizon_url not found in database configuration")
        
        # Initialize Stellar client (Principle #5: Async)
        self.server = ServerAsync(
            horizon_url=self.horizon_url,
            client=AiohttpClient()
        )
        
        self.initialized = True
        self.logger.info(f"✓ Synchronizer initialized: {self.horizon_url}")
    
    async def _load_settings_from_database(self) -> Dict[str, Any]:
        """
        Load configuration settings from database.
        
        Principle #4: Single Source of Truth
        Principle #8: No Duplicate Configuration
        
        Returns:
            Dictionary of configuration settings
        """
        query = """
            SELECT setting_key, setting_value, setting_type
            FROM system_settings
            WHERE setting_key IN ('horizon_url', 'network', 'ubec_issuer')
            AND is_active = TRUE
        """
        
        rows = await self.db.fetch_all(query, ())
        
        settings = {}
        for row in rows:
            key = row['setting_key']
            value = row['setting_value']
            value_type = row.get('setting_type', 'string')
            
            # Convert value based on type
            if value_type == 'integer':
                settings[key] = int(value)
            elif value_type == 'float' or value_type == 'decimal':
                settings[key] = float(value)
            elif value_type == 'boolean':
                settings[key] = value.lower() in ('true', '1', 'yes')
            else:
                settings[key] = value
        
        return settings
    
    # ==================== STELLAR API OPERATIONS ====================
    # Principle #9: Rate Limited API Calls
    
    async def _stellar_api_call(self, api_call, max_retries: int = 3):
        """
        Execute Stellar API call with rate limiting and circuit breaker.
        
        Principle #5: Async operations
        Principle #9: Rate limiting with circuit breaker
        
        Args:
            api_call: Async callable that performs the API request
            max_retries: Maximum retry attempts
            
        Returns:
            API call result
            
        Raises:
            Exception: If all retries fail or circuit breaker is open
        """
        for attempt in range(max_retries):
            try:
                # Acquire rate limit token (Principle #9)
                await self.rate_limiter.acquire()
                
                # Execute API call (Principle #5: Async)
                result = await api_call()
                
                # Record success
                self.rate_limiter.record_success()
                
                return result
                
            except Exception as e:
                # Record failure
                self.rate_limiter.record_failure()
                self._error_count += 1
                self._last_error = str(e)
                self._last_error_time = datetime.now()
                
                # Log and potentially retry
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(
                        f"API call failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"API call failed after {max_retries} attempts: {e}")
                    raise
    
    # ==================== ACCOUNT DISCOVERY ====================
    # Principle #7: Per-Asset Monitoring
    
    async def discover_accounts(
        self,
        asset_code: str,
        max_accounts: int = 200
    ) -> int:
        """
        Discover and sync accounts holding a specific UBEC token.
        
        Queries Stellar Horizon for all accounts holding the specified asset,
        then syncs their balances to the database.
        
        Note: Stellar Horizon API has a maximum limit of 200 accounts per request.
        For larger requests, this method automatically paginates through results.
        
        Args:
            asset_code: UBEC token code (UBEC, UBECrc, UBECgpi, UBECtt)
            max_accounts: Maximum accounts to discover (default: 200, Stellar API limit)
            
        Returns:
            Number of accounts discovered and synced
            
        Raises:
            ValueError: If asset_code is invalid
            
        Example:
            >>> count = await sync.discover_accounts('UBEC', max_accounts=100)
            >>> print(f"Synced {count} UBEC holders")
            
        Principle #5: Async operations throughout
        Principle #7: Per-asset monitoring and tracking
        """
        if not self.initialized:
            await self.initialize()
        
        # Validate asset code
        if asset_code not in self.VALID_UBEC_TOKENS:
            raise ValueError(
                f"Invalid asset code: {asset_code}. "
                f"Must be one of: {self.VALID_UBEC_TOKENS}"
            )
        
        issuer = self.settings.get('ubec_issuer')
        if not issuer:
            raise ValueError("ubec_issuer not found in database configuration")
        
        # Create Stellar asset
        asset = Asset(asset_code, issuer)
        
        # Stellar API limit is 200 per request
        STELLAR_API_LIMIT = 200
        limit_per_request = min(max_accounts, STELLAR_API_LIMIT)
        
        try:
            synced_count = 0
            cursor = None
            
            # Paginate through results if needed
            while synced_count < max_accounts:
                # Calculate how many more accounts we need
                remaining = max_accounts - synced_count
                current_limit = min(remaining, STELLAR_API_LIMIT)
                
                # Build query
                accounts_query = self.server.accounts().for_asset(asset).limit(current_limit)
                
                # Add cursor for pagination if not first request
                if cursor:
                    accounts_query = accounts_query.cursor(cursor)
                
                # Execute query
                accounts_call = lambda q=accounts_query: q.call()
                response = await self._stellar_api_call(accounts_call)
                
                accounts = response.get('_embedded', {}).get('records', [])
                
                # If no accounts returned, we're done
                if not accounts:
                    break
                
                # Sync each account (Principle #5: Async operations)
                for account_data in accounts:
                    account_id = account_data.get('id')
                    if account_id:
                        try:
                            await self.sync_account(account_id, asset_code)
                            synced_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to sync account {account_id}: {e}")
                            self._token_metrics[asset_code]['errors'] += 1
                            self._token_metrics[asset_code]['last_error'] = str(e)
                
                # Check if there are more pages
                next_link = response.get('_links', {}).get('next')
                if not next_link or synced_count >= max_accounts:
                    break
                
                # Update cursor for next page
                cursor = accounts[-1].get('paging_token') if accounts else None
            
            # Update metrics (Principle #7)
            self._token_metrics[asset_code]['accounts_synced'] += synced_count
            self._token_metrics[asset_code]['last_sync'] = datetime.now().isoformat()
            self._sync_operations_count += 1
            self._last_sync_time = datetime.now()
            
            self.logger.info(f"✓ Discovered {synced_count} {asset_code} holders")
            
            return synced_count
            
        except Exception as e:
            self._token_metrics[asset_code]['errors'] += 1
            self._token_metrics[asset_code]['last_error'] = str(e)
            self.logger.error(f"Failed to discover {asset_code} accounts: {e}")
            raise
    
    # ==================== ACCOUNT SYNCHRONIZATION ====================
    
    async def sync_account(
        self,
        account_id: str,
        asset_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sync a specific account's balances to database.
        
        Retrieves account data from Stellar and updates database with current
        balances for all UBEC tokens held.
        
        Args:
            account_id: Stellar account ID (G... address)
            asset_code: Optional - sync specific asset only
            
        Returns:
            Dictionary with sync results
            
        Example:
            >>> result = await sync.sync_account('GACCOUNT...', 'UBEC')
            >>> print(f"Balance: {result['UBEC']['balance']}")
            
        Principle #4: Database is single source of truth
        Principle #5: Async operations
        """
        if not self.initialized:
            await self.initialize()
        
        issuer = self.settings.get('ubec_issuer')
        
        try:
            # Fetch account from Stellar (Principle #5: Async)
            account_call = lambda: self.server.accounts().account_id(account_id).call()
            account_data = await self._stellar_api_call(account_call)
            
            balances = account_data.get('balances', [])
            results = {}
            
            # Process each balance
            for balance in balances:
                asset_type = balance.get('asset_type')
                
                # Skip native (XLM) balances
                if asset_type == 'native':
                    continue
                
                code = balance.get('asset_code')
                balance_issuer = balance.get('asset_issuer')
                
                # Only process UBEC tokens from correct issuer
                if (code in self.VALID_UBEC_TOKENS and 
                    balance_issuer == issuer and
                    (asset_code is None or code == asset_code)):
                    
                    amount = Decimal(balance.get('balance', '0'))
                    
                    # Store in database (Principle #4: Single Source of Truth)
                    await self._store_account_balance(
                        account_id=account_id,
                        asset_code=code,
                        balance=amount
                    )
                    
                    results[code] = {
                        'balance': str(amount),
                        'element': self.ELEMENT_MAP[code]
                    }
            
            return results
            
        except NotFoundError:
            self.logger.warning(f"Account not found: {account_id}")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to sync account {account_id}: {e}")
            raise
    
    async def _store_account_balance(
        self,
        account_id: str,
        asset_code: str,
        balance: Decimal
    ) -> None:
        """
        Store account balance in database.
        
        Principle #4: Database is single source of truth
        Principle #5: Async database operation
        
        Args:
            account_id: Stellar account ID
            asset_code: UBEC token code (parameter name for API compatibility)
            balance: Token balance
            
        Note:
            The account_balances table uses 'asset_code' column, not 'asset_code'.
        """
        # Map asset_code to element for the element column
        element_map = {
            'UBEC': 'air',
            'UBECrc': 'water',
            'UBECgpi': 'earth',
            'UBECtt': 'fire'
        }
        element = element_map.get(asset_code, 'air')
        
        query = """
            INSERT INTO account_balances 
                (account_id, asset_code, element, balance, last_modified_at)
            VALUES ($1, $2::asset_code, $3::element_type, $4, NOW())
            ON CONFLICT (account_id, asset_code) 
            DO UPDATE SET 
                balance = EXCLUDED.balance,
                last_modified_at = EXCLUDED.last_modified_at
        """
        
        await self.db.execute(query, (account_id, asset_code, element, balance))
    
    # ==================== BULK SYNCHRONIZATION ====================
    # Principle #12: Method Singularity
    
    async def sync_all_tokens(
        self,
        max_accounts_per_token: int = 200
    ) -> Dict[str, Any]:
        """
        Synchronize all UBEC tokens (legacy method name).
        
        Discovers and syncs accounts for all four UBEC tokens:
        UBEC (Air), UBECrc (Water), UBECgpi (Earth), UBECtt (Fire).
        
        Note: Stellar Horizon API limits to 200 accounts per request.
        
        Args:
            max_accounts_per_token: Max accounts to discover per token (default: 200)
            
        Returns:
            Dict with sync results for each token
            
        Example:
            >>> results = await sync.sync_all_tokens(max_accounts_per_token=100)
            >>> for token, data in results.items():
            ...     print(f"{token}: {data['accounts']} accounts")
            
        Note:
            This is the legacy method name. Use sync_all() for standardized interface.
            
        Principle #7: Per-asset monitoring
        Principle #12: Method singularity - delegates to sync_all()
        """
        return await self.sync_all(max_accounts_per_token=max_accounts_per_token)
    
    async def sync_all(
        self,
        force: bool = False,
        max_accounts_per_token: int = 200
    ) -> Dict[str, Any]:
        """
        Synchronize all UBEC tokens (standardized method name).
        
        This is the PRIMARY method for full synchronization, called by main.py.
        Discovers and syncs accounts for all four UBEC tokens.
        
        Note: Stellar Horizon API limits to 200 accounts per request. This method
        will paginate automatically if you request more than 200 accounts.
        
        Args:
            force: Force sync even if recently synced (currently ignored)
            max_accounts_per_token: Max accounts to discover per token (default: 200)
            
        Returns:
            Dict with sync results for each token
            
        Example:
            >>> results = await sync.sync_all(max_accounts_per_token=100)
            >>> for token, data in results.items():
            ...     print(f"{token} ({data['element']}): {data['accounts']} accounts")
            
        Principle #5: Async operations
        Principle #7: Per-asset monitoring
        Principle #12: Method singularity - single implementation
        """
        if not self.initialized:
            await self.initialize()
        
        results = {}
        
        for asset_code in self.VALID_UBEC_TOKENS:
            try:
                count = await self.discover_accounts(asset_code, max_accounts_per_token)
                results[asset_code] = {
                    'accounts': count,
                    'element': self.ELEMENT_MAP[asset_code],
                    'status': 'success'
                }
            except Exception as e:
                results[asset_code] = {
                    'accounts': 0,
                    'element': self.ELEMENT_MAP[asset_code],
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    # ==================== HEALTH CHECK ====================
    # Principle #12: Uses ServiceHealthCheck utility
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check using ServiceHealthCheck utility.
        
        Implements Principle #12 (Method Singularity) and Principle #7
        (Per-Asset Monitoring) with detailed metrics.
        
        Returns:
            Health status dictionary with standardized format
            
        Example:
            >>> health = await sync.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("✓ Synchronizer operational")
            >>> else:
            ...     print(f"✗ Issues: {health['message']}")
            
        Principle #12: Uses ServiceHealthCheck utility (method singularity)
        """
        async def check_stellar_connectivity():
            """Verify Stellar API connectivity"""
            if not self.server:
                raise Exception("Stellar server not initialized")
            
            try:
                await self._stellar_api_call(
                    lambda: self.server.ledgers().limit(1).call()
                )
                return "Stellar API accessible"
            except Exception as e:
                raise Exception(f"Stellar API test call failed: {e}")
        
        async def check_settings_loaded():
            """Verify settings are loaded from database"""
            if not self.settings:
                raise Exception("Settings not loaded from database")
            
            required_settings = ['horizon_url', 'ubec_issuer']
            missing = [s for s in required_settings if s not in self.settings]
            
            if missing:
                raise Exception(f"Missing critical settings: {missing}")
            
            return f"Settings loaded ({len(self.settings)} items)"
        
        async def check_rate_limiter_health():
            """Verify rate limiter is functioning"""
            if not self.rate_limiter:
                raise Exception("Rate limiter not initialized")
            
            metrics = self.rate_limiter.get_metrics()
            
            cb_state = metrics.get('circuit_breaker_state', 'unknown')
            if cb_state == 'open':
                raise Exception("Circuit breaker is OPEN (service degraded)")
            
            total_requests = metrics.get('total_requests', 0)
            rate_limited = metrics.get('rate_limited_requests', 0)
            
            if total_requests > 10:
                error_rate = rate_limited / total_requests
                if error_rate > 0.5:
                    raise Exception(
                        f"High rate limit error rate: {error_rate:.1%} "
                        f"({rate_limited}/{total_requests} requests)"
                    )
            
            return f"Rate limiter healthy ({cb_state}, {total_requests} requests)"
        
        # Get rate limiter metrics
        rate_limiter_metrics = None
        if self.rate_limiter:
            rate_limiter_metrics = self.rate_limiter.get_metrics()
        
        # Use ServiceHealthCheck utility (Principle #12)
        return await ServiceHealthCheck.database_dependent_health(
            service_name='synchronizer',
            db_manager=self.db,
            is_initialized=self.initialized,
            additional_checks=[
                check_settings_loaded,
                check_stellar_connectivity,
                check_rate_limiter_health
            ],
            settings_loaded=bool(self.settings),
            sync_operations_count=self._sync_operations_count,
            last_sync_time=self._last_sync_time.isoformat() if self._last_sync_time else None,
            rate_limiter=rate_limiter_metrics,
            has_stellar=self.server is not None,
            horizon_url=self.horizon_url,
            network=self.network,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time.isoformat() if self._last_error_time else None,
            token_metrics=self._token_metrics
        )
    
    # ==================== LIFECYCLE ====================
    
    async def close(self) -> None:
        """
        Clean up synchronizer resources.
        
        Principle #5: Async cleanup operation.
        """
        self.logger.info("Closing UBEC Data Synchronizer...")
        
        if self.server:
            await self.server.close()
            self.server = None
        
        self.initialized = False
        self.logger.info("✓ UBEC Data Synchronizer closed")


# ==================== SERVICE FACTORY ====================
# Principle #2: Service Pattern with factory function

def create_synchronizer_service(db_manager, **kwargs):
    """
    Factory function to create UBEC Data Synchronizer service.
    
    This is a convenience function for creating the service.
    For service registry integration, use register_factory instead.
    
    Principle #2: Service pattern with factory function.
    Principle #3: Dependencies injected via service registry.
    
    Args:
        db_manager: Async database manager
        **kwargs: Additional configuration options
            - rate_limit_per_second: API rate limit (default: 10.0)
    
    Returns:
        UBECDataSynchronizer: Service instance (not initialized)
        
    Note:
        Call initialize() on the returned instance before use.
    
    Example:
        >>> sync = create_synchronizer_service(db_manager, rate_limit_per_second=10.0)
        >>> await sync.initialize()
        >>> health = await sync.health_check()
    """
    return UBECDataSynchronizer(
        db_manager=db_manager,
        rate_limit_per_second=kwargs.get('rate_limit_per_second', 10.0)
    )


# ==================== SERVICE REGISTRY INTEGRATION ====================
# Principle #3: Service Registry for Dependencies

async def register_factory(database, config, stellar_client):
    """
    Factory function for service registry integration.
    
    This is the STANDARD way to create and register the synchronizer service
    with the service registry.
    
    Principle #2: Service Pattern with centralized execution
    Principle #3: Service Registry for Dependencies
    Principle #4: Single Source of Truth (config from database)
    Principle #5: Async initialization
    
    Dependencies:
        database: Database manager service (provides data persistence)
        config: Configuration service (provides database-backed settings)
        stellar_client: Stellar client service (for API access)
    
    Args:
        database: AsyncDatabaseManager from registry
        config: Config service from registry (currently unused, but available)
        stellar_client: Stellar client from registry (currently unused, but available)
    
    Returns:
        Fully initialized UBECDataSynchronizer instance
        
    Raises:
        Exception: If initialization fails
    
    Usage (by service registry):
        registry.register(
            "synchronizer",
            register_factory,
            dependencies=["database", "config", "stellar_client"]
        )
        
        # Later, in application code:
        sync = await registry.get("synchronizer")
        results = await sync.sync_all()
    
    Example:
        >>> # In main.py service registration
        >>> from services.sync.ubec_data_synchronizer import register_factory
        >>> 
        >>> registry.register_factory(
        ...     'synchronizer',
        ...     register_factory,
        ...     dependencies=['database', 'config', 'stellar_client']
        ... )
        >>> 
        >>> # Later in code
        >>> sync = await registry.get('synchronizer')
        >>> health = await sync.health_check()
    """
    logger.info("Creating UBEC Data Synchronizer via factory...")
    
    # Create service instance
    service = UBECDataSynchronizer(
        db_manager=database,
        rate_limit_per_second=10.0  # Default rate limit
    )
    
    # Initialize the service
    await service.initialize()
    
    logger.info("✓ UBEC Data Synchronizer created and initialized")
    
    return service


# ==================== MODULE EXPORTS ====================
# Principle #1: Modular Design - Clear public interface

__all__ = [
    'UBECDataSynchronizer',
    'create_synchronizer_service',
    'register_factory',
    'RateLimiterWithCircuitBreaker',
    'RateLimiterMetrics'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Principle #2: Service Pattern - No standalone execution

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from services.sync.ubec_data_synchronizer import register_factory\n"
        "  # Register with service registry\n"
        "  registry.register_factory(\n"
        "      'synchronizer',\n"
        "      register_factory,\n"
        "      dependencies=['database', 'config', 'stellar_client']\n"
        "  )\n"
        "  # Use the service\n"
        "  sync = await registry.get('synchronizer')\n"
        "  results = await sync.sync_all()\n"
        "  health = await sync.health_check()\n\n"
        "Version 3.0.0 - Registry Integration + Method Standardization:\n"
        "  - Added register_factory for service registry integration\n"
        "  - Added sync_all() method (standardized interface)\n"
        "  - Complete implementation of all methods\n"
        "  - All 12 design principles implemented\n"
        "  - Uses ServiceHealthCheck utility (Principle #12)\n"
        "  - Rate limiting with circuit breaker (Principle #9)\n"
        "  - Database configuration (Principles #4 & #8)\n"
        "  - Per-asset monitoring (Principle #7)\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC to inform\n"
        "  our decisions and recommendations. This project was made possible with\n"
        "  the assistance of Claude and Anthropic PBC."
    )
