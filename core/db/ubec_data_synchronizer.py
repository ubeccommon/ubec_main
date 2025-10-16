#!/usr/bin/env python3
"""
UBEC Data Synchronizer - Production-Grade Async Version with Enhanced Rate Limiting

Synchronizes data between Stellar blockchain and the ubec_main database schema.
Compatible with the four-element protocol architecture.

Design Principles Compliance:
- ✅ Modular Design: Self-contained service with defined boundaries
- ✅ Service Pattern: No standalone execution (used via main.py only)
- ✅ Service Registry: Dependencies managed through central registry
- ✅ Database as Single Source of Truth: Settings loaded from database
- ✅ Strict Async: All I/O operations use async/await
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ No Duplicate Configuration: Settings stored once in database
- ✅ Integrated Rate Limiting: Production-grade with exponential backoff
- ✅ Clear Separation of Concerns: Active vs passive operations separated
- ✅ Comprehensive Documentation: Docstrings and inline comments
- ✅ Method Singularity: Each method implemented exactly once

Key Features:
- FULLY ASYNC operations (async/await pattern throughout)
- Production-grade rate limiting with exponential backoff and jitter
- Intelligent retry logic with circuit breaker pattern
- Proper 429 HTTP response handling
- Configurable rate limit buffer from database
- Comprehensive error handling and recovery
- Rate limit metrics tracking
- Transaction-safe operations with async context managers
- Progress tracking for long-running operations
- Idempotent operations (safe to retry)
- Liquidity pool tracking and synchronization

Enhanced Rate Limiting v6.0:
- Exponential backoff with jitter (prevents thundering herd)
- Configurable retry attempts from database settings
- Circuit breaker for repeated failures (fails fast after threshold)
- Rate limit buffer configurable via database (default: 50 requests)
- Proactive rate limit checking before requests
- Reactive 429 response handling with intelligent backoff
- Clock skew handling for rate limit reset times
- Comprehensive rate limit metrics and logging

Schema Mapping:
- stellar_accounts: Core account data
- ubec_balances: Token holdings with foreign key to stellar_accounts
- stellar_transactions: Transaction records
- stellar_operations: Operation details
- ubec_sync_status: Synchronization tracking
- liquidity_pools: Pool data with reserves and fees
- liquidity_pool_owners: Individual LP positions

Four-Element Architecture:
- 🌬️ Air (UBEC) - Gateway & Universal Access
- 💧 Water (UBECrc) - Flow & Exchange  
- 🌍 Earth (UBECgpi) - Stability & Value
- 🔥 Fire (UBECtt) - Transformation & Action

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 6.3 (Production-Grade Rate Limiting - Comprehensive Exception Handling)
Date: October 16, 2025

Changes in v6.3:
    - 🔥 CRITICAL FIX: Comprehensive exception inspection for all 429 patterns
    - ✅ Checks three ways stellar-sdk can signal rate limit:
      1. Direct status_code attribute on exception
      2. Wrapped in exception.response.status_code
      3. Using status attribute instead of status_code
    - ✅ Diagnostic logging to identify actual exception types
    - ✅ Handles Response objects whether returned, raised, or wrapped
    - ✅ Robust retry logic regardless of stellar-sdk exception format
Changes in v6.2:
    - 🔥 CRITICAL FIX: Handle Response objects raised as EXCEPTIONS by stellar-sdk
    - ✅ Stellar SDK can raise Response objects OR return them - now handles both
    - ✅ Exception handler checks hasattr(e, 'status_code') for raised Response objects
    - ✅ Parse X-RateLimit-Reset from exception object's headers
    - ✅ Same intelligent retry logic whether Response or Exception
    - ✅ Comprehensive logging distinguishes between Response types
    - ✅ Complete 429 handling coverage for all stellar-sdk behaviors
Changes in v6.1:
    - 🔥 CRITICAL FIX: Properly handle stellar-sdk Response objects with status_code=429
    - ✅ Stellar SDK sometimes returns Response objects instead of raising exceptions
    - ✅ Parse X-RateLimit-Reset header from Response object headers (300s = 5 minutes)
    - ✅ Intelligent wait based on reset time before retry
    - ✅ Fallback to exponential backoff with jitter if no reset time
    - ✅ Comprehensive logging for both Response objects and exceptions
    - ✅ Maintains all production-grade rate limiting features from v6.0
Changes in v6.0:
    - 🔥 ENHANCED: Production-grade rate limiting with exponential backoff
    - ✅ Added jitter to backoff to prevent thundering herd problem
    - ✅ Configurable retry attempts and rate limit buffer from database
    - ✅ Circuit breaker pattern for repeated failures
    - ✅ Explicit 429 HTTP response handling
    - ✅ Clock skew handling for rate limit reset calculations
    - ✅ Comprehensive rate limit metrics tracking
    - ✅ Better error categorization and logging
    - ✅ Graceful degradation under sustained rate limiting
    - ✅ Maintains all 12 design principles
"""

import os
import asyncio
import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
import aiohttp

# Configure precision for decimal calculations
getcontext().prec = 10

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SyncException(Exception):
    """Base exception for sync-related errors."""
    pass


class RateLimitException(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by failing fast when service is degraded.
    After threshold failures, opens circuit and rejects requests.
    Periodically tests if service recovered (half-open state).
    
    Design Principle: Method Singularity - Single implementation used system-wide.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before testing recovery
            expected_exception: Exception type that triggers circuit
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
    
    def record_success(self):
        """Record successful operation."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker OPENED after {self.failure_count} failures"
            )
    
    def can_attempt(self) -> bool:
        """Check if operation can be attempted."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout elapsed
            if self.last_failure_time:
                elapsed = asyncio.get_event_loop().time() - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker entering HALF_OPEN state")
                    return True
            return False
        
        # HALF_OPEN state - allow attempt
        return True
    
    async def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerException: If circuit is open
        """
        if not self.can_attempt():
            raise CircuitBreakerException(
                f"Circuit breaker is OPEN. "
                f"Service unavailable after {self.failure_count} failures."
            )
        
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except self.expected_exception as e:
            self.record_failure()
            raise


# ============================================================================
# RATE LIMITER WITH EXPONENTIAL BACKOFF
# ============================================================================

class RateLimiter:
    """
    Production-grade rate limiter with exponential backoff and jitter.
    
    Features:
    - Tracks API rate limits from response headers
    - Proactive rate limit checking (prevents 429s)
    - Reactive 429 handling with intelligent backoff
    - Exponential backoff with jitter
    - Configurable buffer to stay under limits
    - Clock skew handling
    
    Design Principles:
    - Strict Async: All operations async
    - Method Singularity: Single rate limiter implementation
    - Integrated Rate Limiting: Built into service
    """
    
    def __init__(
        self,
        rate_limit_buffer: int = 50,
        max_retries: int = 5,
        base_backoff: float = 1.0,
        max_backoff: float = 120.0,
        backoff_factor: float = 2.0
    ):
        """
        Initialize rate limiter.
        
        Args:
            rate_limit_buffer: Number of requests to keep as buffer
            max_retries: Maximum retry attempts for rate-limited requests
            base_backoff: Initial backoff time in seconds
            max_backoff: Maximum backoff time in seconds
            backoff_factor: Multiplier for exponential backoff
        """
        self.rate_limit_buffer = rate_limit_buffer
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff
        self.backoff_factor = backoff_factor
        
        # Rate limit tracking
        self.rate_limit_remaining = 3000
        self.rate_limit_limit = 3600
        self.rate_limit_reset = 0
        
        # Metrics
        self.total_requests = 0
        self.rate_limited_requests = 0
        self.retry_attempts = 0
        
        # Circuit breaker for repeated rate limit failures
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=10,
            recovery_timeout=300,  # 5 minutes
            expected_exception=RateLimitException
        )
    
    def update_from_headers(self, headers: Dict[str, str]):
        """
        Update rate limit state from API response headers.
        
        Args:
            headers: HTTP response headers
        """
        try:
            # Parse rate limit headers with fallbacks
            remaining = headers.get('X-Ratelimit-Remaining') or headers.get('x-ratelimit-remaining')
            limit = headers.get('X-Ratelimit-Limit') or headers.get('x-ratelimit-limit')
            reset = headers.get('X-Ratelimit-Reset') or headers.get('x-ratelimit-reset')
            
            if remaining:
                self.rate_limit_remaining = int(remaining)
            if limit:
                self.rate_limit_limit = int(limit)
            if reset:
                self.rate_limit_reset = int(reset)
            
            logger.debug(
                f"Rate limit updated: {self.rate_limit_remaining}/{self.rate_limit_limit} "
                f"(resets at {self.rate_limit_reset})"
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing rate limit headers: {e}")
    
    async def check_and_wait(self):
        """
        Check rate limit and wait if necessary (proactive check).
        
        This prevents hitting rate limits by waiting BEFORE making requests
        when we're close to the limit.
        """
        # Check if we're within buffer zone
        if self.rate_limit_remaining <= self.rate_limit_buffer:
            # Calculate wait time with clock skew handling
            now = int(datetime.now().timestamp())
            reset_time = self.rate_limit_reset
            
            # If reset time is in the past (clock skew), use minimum wait
            if reset_time <= now:
                wait_time = 5  # Minimum 5 seconds
                logger.warning(
                    f"Rate limit reset time in past (clock skew?). "
                    f"Waiting minimum {wait_time}s"
                )
            else:
                wait_time = reset_time - now
                # Cap wait time at reasonable maximum
                wait_time = min(wait_time, 300)  # Max 5 minutes
            
            logger.warning(
                f"Rate limit buffer reached "
                f"({self.rate_limit_remaining}/{self.rate_limit_limit}). "
                f"Waiting {wait_time}s for reset..."
            )
            
            await asyncio.sleep(wait_time)
            
            # Reset tracking after wait
            self.rate_limit_remaining = self.rate_limit_limit
    
    async def handle_429(self, response: aiohttp.ClientResponse, attempt: int):
        """
        Handle 429 Too Many Requests response (reactive handling).
        
        Uses exponential backoff with jitter to prevent thundering herd.
        
        Args:
            response: The 429 response
            attempt: Current retry attempt number
            
        Raises:
            RateLimitException: If max retries exceeded
        """
        self.rate_limited_requests += 1
        self.retry_attempts += 1
        
        # Try to get Retry-After header
        retry_after = response.headers.get('Retry-After')
        
        if retry_after:
            try:
                wait_time = int(retry_after)
                logger.warning(f"Rate limited (429). Retry-After: {wait_time}s")
            except ValueError:
                # Retry-After might be HTTP date
                wait_time = None
        else:
            wait_time = None
        
        # If no Retry-After, use exponential backoff
        if wait_time is None:
            # Calculate exponential backoff: base * (factor ^ attempt)
            wait_time = min(
                self.base_backoff * (self.backoff_factor ** attempt),
                self.max_backoff
            )
            
            # Add jitter (randomize ±25% to prevent thundering herd)
            jitter = wait_time * 0.25 * (random.random() * 2 - 1)
            wait_time = wait_time + jitter
            
            logger.warning(
                f"Rate limited (429). Attempt {attempt + 1}/{self.max_retries}. "
                f"Backing off for {wait_time:.1f}s (with jitter)"
            )
        
        # Check if we should retry
        if attempt >= self.max_retries - 1:
            raise RateLimitException(
                f"Rate limit exceeded after {self.max_retries} attempts",
                retry_after=int(wait_time)
            )
        
        # Wait before retry
        await asyncio.sleep(wait_time)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get rate limiter metrics.
        
        Returns:
            dict: Rate limit metrics
        """
        return {
            'total_requests': self.total_requests,
            'rate_limited_requests': self.rate_limited_requests,
            'retry_attempts': self.retry_attempts,
            'current_remaining': self.rate_limit_remaining,
            'current_limit': self.rate_limit_limit,
            'circuit_breaker_state': self.circuit_breaker.state.value,
            'circuit_breaker_failures': self.circuit_breaker.failure_count
        }


# ============================================================================
# MAIN SYNCHRONIZER CLASS
# ============================================================================

class UBECDataSynchronizer:
    """
    Production-grade asynchronous data synchronizer.
    
    Synchronizes data between Stellar blockchain and ubec_main database
    with enterprise-grade rate limiting and error handling.
    
    This class ensures proper operation ordering:
    1. Create account records in stellar_accounts
    2. Create balance records in ubec_balances (requires account to exist)
    3. Store transaction/operation data
    4. Sync liquidity pool data and participants
    
    All operations are designed to be idempotent and can be safely retried.
    All I/O operations use async/await patterns for maximum efficiency.
    
    Settings are loaded from database (single source of truth principle).
    """
    
    # Element mapping - ONLY for UBEC family tokens
    ELEMENT_MAP = {
        'UBEC': 'air',
        'UBECrc': 'water',
        'UBECgpi': 'earth',
        'UBECtt': 'fire'
    }
    
    # Valid UBEC token codes (what we store in database)
    VALID_UBEC_TOKENS = {'UBEC', 'UBECrc', 'UBECgpi', 'UBECtt'}
    
    # Operation type mapping for Stellar
    OPERATION_TYPE_MAP = {
        'payment': 'payment',
        'exchange_in': 'path_payment_strict_receive',
        'exchange_out': 'path_payment_strict_send',
        'dex_manage_buy_offer': 'manage_buy_offer',
        'dex_manage_sell_offer': 'manage_sell_offer',
        'create_account': 'create_account',
        'change_trust': 'change_trust'
    }
    
    def __init__(self, db_manager):
        """
        Initialize the async data synchronizer.
        
        Args:
            db_manager: AsyncDatabaseManager instance
        """
        logger.info(f"Initializing UBEC Data Synchronizer v6.0 (Production-Grade)")
        
        # Store database manager
        self.db = db_manager
        
        # Settings will be loaded from database
        self.settings = {}
        self.accounts = {}
        
        # Network configuration defaults (will be overridden by database settings)
        self.network = None
        self.horizon_url = None
        self.ubec_code = "UBEC"
        self.ubec_issuer = None
        
        # Stellar server (initialized in async context)
        self.server = None
        
        # Rate limiter (configured after loading settings)
        self.rate_limiter: Optional[RateLimiter] = None
        
        # Session for async HTTP requests
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("✓ UBEC Data Synchronizer initialized - awaiting settings load")
    
    async def _load_settings_from_database(self):
        """
        Load settings from database (single source of truth).
        Settings are stored in a configuration table.
        """
        try:
            # Load system settings from database
            query = """
                SELECT setting_key, setting_value, setting_type
                FROM system_settings
                WHERE is_active = TRUE
                ORDER BY setting_key
            """
            
            rows = await self.db.fetch_all(query)
            
            if not rows:
                # Use environment variables as fallback
                logger.warning("No settings found in database, using environment variables")
                self.settings = {
                    'horizon_url': os.getenv('HORIZON_URL', 'https://horizon.stellar.org'),
                    'network_passphrase': os.getenv('NETWORK_PASSPHRASE', 'Public Global Stellar Network ; September 2015'),
                    'ubec_code': os.getenv('UBEC_CODE', 'UBEC'),
                    'ubec_issuer': os.getenv('UBEC_ISSUER', 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN'),
                    'rate_limit_buffer': int(os.getenv('RATE_LIMIT_BUFFER', '50')),
                    'max_retries': int(os.getenv('MAX_RETRIES', '5')),
                    'base_backoff': float(os.getenv('BASE_BACKOFF', '1.0')),
                    'max_backoff': float(os.getenv('MAX_BACKOFF', '120.0'))
                }
            else:
                # Convert database rows to settings dict
                self.settings = {}
                for row in rows:
                    key = row['setting_key']
                    value = row['setting_value']
                    setting_type = row.get('setting_type', 'string')
                    
                    # Convert types
                    if setting_type == 'integer':
                        value = int(value)
                    elif setting_type == 'float':
                        value = float(value)
                    elif setting_type == 'boolean':
                        value = value.lower() in ('true', '1', 'yes')
                    
                    self.settings[key] = value
                
                logger.info(f"✓ Loaded {len(self.settings)} settings from database")
            
            # Extract commonly used settings
            self.horizon_url = self.settings.get('horizon_url', 'https://horizon.stellar.org')
            self.network = self.settings.get('network_passphrase', 'Public Global Stellar Network ; September 2015')
            self.ubec_code = self.settings.get('ubec_code', 'UBEC')
            self.ubec_issuer = self.settings.get('ubec_issuer', 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN')
            
            # Load issuers for all 4 UBEC tokens
            self.ubecrc_issuer = self.settings.get('ubecrc_issuer') or os.getenv('UBECRC_ISSUER') or self.ubec_issuer
            self.ubecgpi_issuer = self.settings.get('ubecgpi_issuer') or os.getenv('UBECGPI_ISSUER') or self.ubec_issuer
            self.ubectt_issuer = self.settings.get('ubectt_issuer') or os.getenv('UBECTT_ISSUER') or self.ubec_issuer
            
            # Initialize rate limiter with configuration from database
            rate_limit_buffer = self.settings.get('rate_limit_buffer', 50)
            max_retries = self.settings.get('max_retries', 5)
            base_backoff = self.settings.get('base_backoff', 1.0)
            max_backoff = self.settings.get('max_backoff', 120.0)
            backoff_factor = self.settings.get('backoff_factor', 2.0)
            
            self.rate_limiter = RateLimiter(
                rate_limit_buffer=rate_limit_buffer,
                max_retries=max_retries,
                base_backoff=base_backoff,
                max_backoff=max_backoff,
                backoff_factor=backoff_factor
            )
            
            logger.info(
                f"✓ Rate limiter configured: buffer={rate_limit_buffer}, "
                f"retries={max_retries}, backoff={base_backoff}s-{max_backoff}s"
            )
            
            # Log issuer configuration
            logger.info(f"Token issuer configuration:")
            logger.info(f"  UBEC:    {self.ubec_issuer}")
            logger.info(f"  UBECrc:  {self.ubecrc_issuer}")
            logger.info(f"  UBECgpi: {self.ubecgpi_issuer}")
            logger.info(f"  UBECtt:  {self.ubectt_issuer}")
            
        except Exception as e:
            logger.error(f"Error loading settings from database: {e}")
            raise
    
    def _get_issuer_for_token(self, token_code: str) -> str:
        """
        Get the correct issuer address for a specific token.
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            str: Issuer address for the token
        """
        issuer_map = {
            'UBEC': self.ubec_issuer,
            'UBECrc': self.ubecrc_issuer,
            'UBECgpi': self.ubecgpi_issuer,
            'UBECtt': self.ubectt_issuer
        }
        return issuer_map.get(token_code, self.ubec_issuer)
    
    async def initialize(self, stellar_client):
        """
        Initialize the synchronizer with Stellar client.
        
        Args:
            stellar_client: Initialized Stellar ServerAsync client
        """
        logger.info("Initializing UBEC Data Synchronizer...")
        
        # Store Stellar server
        self.server = stellar_client
        
        # Load settings from database
        await self._load_settings_from_database()
        
        # Create aiohttp session for direct API calls
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        
        logger.info("✓ UBEC Data Synchronizer fully initialized")
    
    async def close(self):
        """
        Clean up resources.
        """
        if self.session:
            await self.session.close()
            self.session = None
    
    # ========================================================================
    # STELLAR API REQUEST WRAPPER WITH RATE LIMITING
    # ========================================================================
    
    async def _stellar_api_call(self, request_func, *args, **kwargs):
        """
        Execute Stellar API call with rate limiting and retry logic.
        
        This is the SINGLE METHOD for all Stellar API calls, ensuring
        consistent rate limiting across the synchronizer.
        
        Design Principle: Method Singularity - All API calls go through here.
        
        Args:
            request_func: Async function to call Stellar API
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            API response
            
        Raises:
            RateLimitException: If rate limit cannot be satisfied
            CircuitBreakerException: If circuit breaker is open
        """
        if not self.rate_limiter:
            raise RuntimeError("Rate limiter not initialized")
        
        # Proactive rate limit check
        await self.rate_limiter.check_and_wait()
        
        # Track request
        self.rate_limiter.total_requests += 1
        
        # Execute with circuit breaker protection
        async def _execute():
            for attempt in range(self.rate_limiter.max_retries):
                try:
                    # Make the API call
                    response = await request_func(*args, **kwargs)
                    
                    # CRITICAL FIX: Check if response is a Response object with status_code
                    # Stellar SDK sometimes returns Response objects instead of raising exceptions
                    if hasattr(response, 'status_code') and response.status_code == 429:
                        logger.warning(
                            f"Rate limited (429 Response object) on attempt {attempt + 1}"
                        )
                        
                        # Parse rate limit headers from Response object
                        if hasattr(response, 'headers'):
                            headers = dict(response.headers)
                            self.rate_limiter.update_from_headers(headers)
                            
                            # Get reset time from headers
                            reset_seconds = headers.get('X-RateLimit-Reset') or headers.get('x-ratelimit-reset')
                            if reset_seconds:
                                try:
                                    wait_time = int(reset_seconds)
                                    logger.warning(
                                        f"Rate limit reset in {wait_time}s. "
                                        f"Waiting before retry {attempt + 1}/{self.rate_limiter.max_retries}..."
                                    )
                                    await asyncio.sleep(wait_time)
                                except (ValueError, TypeError):
                                    # Fallback to exponential backoff
                                    wait_time = min(
                                        self.rate_limiter.base_backoff * (self.rate_limiter.backoff_factor ** attempt),
                                        self.rate_limiter.max_backoff
                                    )
                                    # Add jitter
                                    jitter = wait_time * 0.25 * (random.random() * 2 - 1)
                                    wait_time = wait_time + jitter
                                    logger.warning(f"Using exponential backoff: {wait_time:.1f}s")
                                    await asyncio.sleep(wait_time)
                            else:
                                # No reset time in headers, use exponential backoff
                                wait_time = min(
                                    self.rate_limiter.base_backoff * (self.rate_limiter.backoff_factor ** attempt),
                                    self.rate_limiter.max_backoff
                                )
                                # Add jitter
                                jitter = wait_time * 0.25 * (random.random() * 2 - 1)
                                wait_time = wait_time + jitter
                                logger.warning(f"Using exponential backoff: {wait_time:.1f}s")
                                await asyncio.sleep(wait_time)
                        
                        # Record rate limit hit
                        self.rate_limiter.rate_limited_requests += 1
                        self.rate_limiter.retry_attempts += 1
                        self.rate_limiter.circuit_breaker.record_failure()
                        
                        # Check if we should retry
                        if attempt >= self.rate_limiter.max_retries - 1:
                            raise RateLimitException(
                                f"Rate limit exceeded after {self.rate_limiter.max_retries} attempts"
                            )
                        
                        # Retry
                        continue
                    
                    # Update rate limits from response headers
                    if hasattr(response, '_headers'):
                        self.rate_limiter.update_from_headers(response._headers)
                    elif hasattr(response, 'headers'):
                        self.rate_limiter.update_from_headers(dict(response.headers))
                    
                    # Success - record in circuit breaker
                    self.rate_limiter.circuit_breaker.record_success()
                    
                    return response
                    
                except aiohttp.ClientResponseError as e:
                    # Handle 429 Too Many Requests as exception
                    if e.status == 429:
                        logger.warning(f"Rate limited (429 exception) on attempt {attempt + 1}")
                        
                        # Use our rate limiter's 429 handler
                        if hasattr(e, 'response'):
                            await self.rate_limiter.handle_429(e.response, attempt)
                        else:
                            # If no response object, use exponential backoff
                            wait_time = min(
                                self.rate_limiter.base_backoff * (self.rate_limiter.backoff_factor ** attempt),
                                self.rate_limiter.max_backoff
                            )
                            await asyncio.sleep(wait_time)
                        
                        # Record failure in circuit breaker
                        self.rate_limiter.circuit_breaker.record_failure()
                        
                        # Retry
                        continue
                    else:
                        # Other HTTP errors - don't retry
                        raise
                
                except Exception as e:
                    # DEBUG: Comprehensive exception inspection
                    logger.debug(f"Exception type: {type(e).__name__}")
                    logger.debug(f"Exception dir: {[attr for attr in dir(e) if not attr.startswith('_')]}")
                    logger.debug(f"Has status_code: {hasattr(e, 'status_code')}")
                    logger.debug(f"Has status: {hasattr(e, 'status')}")
                    logger.debug(f"Has response: {hasattr(e, 'response')}")
                    
                    # Check if exception IS a Response object with status_code
                    if hasattr(e, 'status_code') and getattr(e, 'status_code', None) == 429:
                        logger.warning(
                            f"Rate limited (429 Response raised as exception) on attempt {attempt + 1}"
                        )
                        exception_has_429 = True
                        response_obj = e
                    # Check if exception HAS a Response object in .response attribute
                    elif hasattr(e, 'response') and hasattr(e.response, 'status_code') and e.response.status_code == 429:
                        logger.warning(
                            f"Rate limited (429 wrapped in exception) on attempt {attempt + 1}"
                        )
                        exception_has_429 = True
                        response_obj = e.response
                    # Check for 'status' attribute (some exceptions use this instead)
                    elif hasattr(e, 'status') and getattr(e, 'status', None) == 429:
                        logger.warning(
                            f"Rate limited (429 via status attribute) on attempt {attempt + 1}"
                        )
                        exception_has_429 = True
                        response_obj = e
                    else:
                        exception_has_429 = False
                        response_obj = None
                    
                    if exception_has_429:
                        # Parse rate limit headers from Response object
                        headers = None
                        if hasattr(response_obj, 'headers'):
                            headers = dict(response_obj.headers)
                            self.rate_limiter.update_from_headers(headers)
                        
                        # Get reset time from headers
                        if headers:
                            reset_seconds = headers.get('X-RateLimit-Reset') or headers.get('x-ratelimit-reset')
                            if reset_seconds:
                                try:
                                    wait_time = int(reset_seconds)
                                    logger.warning(
                                        f"Rate limit reset in {wait_time}s. "
                                        f"Waiting before retry {attempt + 1}/{self.rate_limiter.max_retries}..."
                                    )
                                    await asyncio.sleep(wait_time)
                                except (ValueError, TypeError):
                                    # Fallback to exponential backoff
                                    wait_time = min(
                                        self.rate_limiter.base_backoff * (self.rate_limiter.backoff_factor ** attempt),
                                        self.rate_limiter.max_backoff
                                    )
                                    # Add jitter
                                    jitter = wait_time * 0.25 * (random.random() * 2 - 1)
                                    wait_time = wait_time + jitter
                                    logger.warning(f"Using exponential backoff: {wait_time:.1f}s")
                                    await asyncio.sleep(wait_time)
                            else:
                                # No reset time in headers, use exponential backoff
                                wait_time = min(
                                    self.rate_limiter.base_backoff * (self.rate_limiter.backoff_factor ** attempt),
                                    self.rate_limiter.max_backoff
                                )
                                # Add jitter
                                jitter = wait_time * 0.25 * (random.random() * 2 - 1)
                                wait_time = wait_time + jitter
                                logger.warning(f"Using exponential backoff: {wait_time:.1f}s")
                                await asyncio.sleep(wait_time)
                        else:
                            # No headers, use exponential backoff
                            wait_time = min(
                                self.rate_limiter.base_backoff * (self.rate_limiter.backoff_factor ** attempt),
                                self.rate_limiter.max_backoff
                            )
                            jitter = wait_time * 0.25 * (random.random() * 2 - 1)
                            wait_time = wait_time + jitter
                            logger.warning(f"Using exponential backoff: {wait_time:.1f}s")
                            await asyncio.sleep(wait_time)
                        
                        # Record rate limit hit
                        self.rate_limiter.rate_limited_requests += 1
                        self.rate_limiter.retry_attempts += 1
                        self.rate_limiter.circuit_breaker.record_failure()
                        
                        # Check if we should retry
                        if attempt >= self.rate_limiter.max_retries - 1:
                            raise RateLimitException(
                                f"Rate limit exceeded after {self.rate_limiter.max_retries} attempts",
                                retry_after=int(wait_time) if 'wait_time' in locals() else None
                            )
                        
                        # Retry
                        continue
                    else:
                        # Unexpected error (not a 429 Response)
                        logger.error(f"API call failed: {e}")
                        raise
            
            # Max retries exceeded
            raise RateLimitException(
                f"Rate limit exceeded after {self.rate_limiter.max_retries} attempts"
            )
        
        # Execute with circuit breaker
        return await self.rate_limiter.circuit_breaker.call(_execute)
    
    # ========================================================================
    # ACCOUNT AND BALANCE SYNCHRONIZATION
    # ========================================================================
    
    async def sync_account(
        self,
        account_id: str,
        force_refresh: bool = False
    ) -> bool:
        """
        Synchronize single account from Stellar.
        
        Args:
            account_id: Stellar account ID
            force_refresh: Force refresh even if recently synced
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Syncing account {account_id}...")
            
            # Ensure settings are loaded
            if not self.settings:
                logger.info("Settings not loaded yet, loading from database...")
                await self._load_settings_from_database()
            
            if not self.server:
                logger.error("Stellar server not initialized")
                return False
            
            # Fetch account data from Stellar with rate limiting
            try:
                account = await self._stellar_api_call(
                    self.server.accounts().account_id(account_id).call
                )
            except Exception as e:
                logger.error(f"Error fetching account {account_id}: {e}")
                return False
            
            # Store account data
            await self._store_account(account)
            
            # Store balances
            balances = account.get('balances', [])
            await self._store_balances(account_id, balances)
            
            logger.info(f"✓ Account {account_id} synced successfully")
            return True
            
        except CircuitBreakerException:
            logger.error("Circuit breaker is open - service temporarily unavailable")
            return False
        except RateLimitException as e:
            logger.error(f"Rate limit exceeded syncing account {account_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error syncing account {account_id}: {e}")
            return False
    
    async def _store_account(self, account_data: Dict):
        """
        Store or update account in database.
        
        Args:
            account_data: Account data from Stellar API
        """
        try:
            account_id = account_data['id']
            
            query = """
                INSERT INTO stellar_accounts (
                    account_id, sequence, subentry_count, home_domain,
                    last_modified_at, sync_status
                )
                VALUES ($1, $2, $3, $4, NOW(), $5)
                ON CONFLICT (account_id) DO UPDATE SET
                    sequence = EXCLUDED.sequence,
                    subentry_count = EXCLUDED.subentry_count,
                    home_domain = EXCLUDED.home_domain,
                    last_modified_at = NOW(),
                    sync_status = EXCLUDED.sync_status
            """
            
            params = (
                account_id,
                int(account_data.get('sequence', '0')),
                int(account_data.get('subentry_count', 0)),
                account_data.get('home_domain'),
                'synced'
            )
            
            await self.db.execute(query, params)
            logger.debug(f"Account stored: {account_id}")
            
        except Exception as e:
            logger.error(f"Error storing account {account_data.get('id')}: {e}")
            raise
    
    async def _store_balances(self, account_id: str, balances: List[Dict]):
        """
        Store or update balances for an account.
        Only stores UBEC family tokens (UBEC, UBECrc, UBECgpi, UBECtt).
        
        Args:
            account_id: Stellar account ID
            balances: List of balance objects from Stellar API
        """
        try:
            stored_count = 0
            skipped_count = 0
            
            for balance in balances:
                # Determine token info
                if balance['asset_type'] == 'native':
                    token_code = 'XLM'
                else:
                    token_code = balance.get('asset_code', 'UNKNOWN')
                
                # CRITICAL: Only store UBEC family tokens
                if token_code not in self.VALID_UBEC_TOKENS:
                    skipped_count += 1
                    logger.debug(f"Skipping non-UBEC token: {token_code} for account {account_id}")
                    continue
                
                # Get element for this UBEC token
                element = self.ELEMENT_MAP.get(token_code, 'air')
                
                # Calculate numeric balance
                balance_amount = Decimal(balance.get('balance', '0'))
                
                # Get authorization flags
                is_authorized = balance.get('is_authorized', False)
                is_auth_maintain = balance.get('is_authorized_to_maintain_liabilities', False)
                is_clawback = balance.get('is_clawback_enabled', False)
                
                query = """
                    INSERT INTO ubec_balances (
                        account_id, token_code, element,
                        balance, limit_amount, 
                        buying_liabilities, selling_liabilities,
                        is_authorized, is_authorized_to_maintain_liabilities, 
                        is_clawback_enabled
                    )
                    VALUES (
                        $1, $2::ubec_main.token_code, $3::ubec_main.element_type,
                        $4, $5,
                        $6, $7,
                        $8, $9, $10
                    )
                    ON CONFLICT (account_id, token_code) DO UPDATE SET
                        balance = EXCLUDED.balance,
                        limit_amount = EXCLUDED.limit_amount,
                        buying_liabilities = EXCLUDED.buying_liabilities,
                        selling_liabilities = EXCLUDED.selling_liabilities,
                        is_authorized = EXCLUDED.is_authorized,
                        is_authorized_to_maintain_liabilities = EXCLUDED.is_authorized_to_maintain_liabilities,
                        is_clawback_enabled = EXCLUDED.is_clawback_enabled,
                        last_modified_at = CURRENT_TIMESTAMP
                """
                
                params = (
                    account_id,
                    token_code,
                    element,
                    balance_amount,
                    Decimal(balance.get('limit', '0')) if 'limit' in balance else None,
                    Decimal(balance.get('buying_liabilities', '0')),
                    Decimal(balance.get('selling_liabilities', '0')),
                    is_authorized,
                    is_auth_maintain,
                    is_clawback
                )
                
                await self.db.execute(query, params)
                stored_count += 1
            
            logger.debug(
                f"Balance storage for {account_id}: "
                f"{stored_count} UBEC tokens stored, {skipped_count} non-UBEC assets skipped"
            )
            
        except Exception as e:
            logger.error(f"Error storing balances for {account_id}: {e}")
            raise
    
    # ========================================================================
    # TRANSACTION SYNCHRONIZATION
    # ========================================================================
    
    async def sync_transactions(
        self,
        account_id: str,
        limit: int = 200,
        cursor: Optional[str] = None
    ) -> int:
        """
        Synchronize transactions for an account.
        
        Args:
            account_id: Stellar account ID
            limit: Maximum transactions to fetch
            cursor: Starting cursor for pagination
            
        Returns:
            int: Number of transactions synchronized
        """
        try:
            logger.info(f"Syncing transactions for {account_id} (limit: {limit})")
            
            # Ensure settings are loaded
            if not self.settings:
                await self._load_settings_from_database()
            
            if not self.server:
                logger.error("Stellar server not initialized")
                return 0
            
            # Build request
            request = self.server.transactions().for_account(account_id).limit(limit)
            
            if cursor:
                request = request.cursor(cursor)
            
            # Fetch transactions with rate limiting
            response = await self._stellar_api_call(request.call)
            
            # Store transactions
            transactions = response.get('_embedded', {}).get('records', [])
            
            for tx in transactions:
                await self._ensure_account_exists(tx['source_account'])
                await self._store_transaction(tx)
                await self._extract_and_store_operations(tx)
            
            logger.info(f"✓ Synced {len(transactions)} transactions for {account_id}")
            return len(transactions)
            
        except CircuitBreakerException:
            logger.error("Circuit breaker is open - service temporarily unavailable")
            return 0
        except RateLimitException as e:
            logger.error(f"Rate limit exceeded syncing transactions: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error syncing transactions for {account_id}: {e}")
            return 0
    
    async def _ensure_account_exists(self, account_id: str):
        """
        Ensure an account record exists in the database before storing related data.
        
        Args:
            account_id: Stellar account ID
        """
        try:
            query = """
                INSERT INTO stellar_accounts (account_id, sync_status)
                VALUES ($1, 'partial')
                ON CONFLICT (account_id) DO NOTHING
            """
            await self.db.execute(query, (account_id,))
            
        except Exception as e:
            logger.error(f"Error ensuring account exists {account_id}: {e}")
            raise
    
    async def _store_transaction(self, tx_data: Dict):
        """
        Store transaction in database.
        
        Args:
            tx_data: Transaction data from Stellar API
        """
        try:
            query = """
                INSERT INTO stellar_transactions (
                    transaction_hash, ledger_sequence, created_at, source_account,
                    fee_charged, operation_count, memo_type, memo,
                    successful, result_code
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (transaction_hash) DO UPDATE SET
                    successful = EXCLUDED.successful,
                    result_code = EXCLUDED.result_code
            """
            
            params = (
                tx_data['hash'],
                tx_data.get('ledger_sequence', 0),
                tx_data.get('created_at'),
                tx_data.get('source_account'),
                int(tx_data.get('fee_charged', 0)),
                tx_data.get('operation_count', 0),
                tx_data.get('memo_type'),
                tx_data.get('memo'),
                tx_data.get('successful', True),
                tx_data.get('result_xdr', '')[:100] if tx_data.get('result_xdr') else None
            )
            
            await self.db.execute(query, params)
            logger.debug(f"Transaction stored: {tx_data['hash']}")
            
        except Exception as e:
            logger.error(f"Error storing transaction {tx_data.get('hash')}: {e}")
            raise
    
    async def _extract_and_store_operations(self, tx_data: Dict):
        """
        Extract and store individual operations from a transaction.
        
        Args:
            tx_data: Transaction data from Stellar API
        """
        try:
            transaction_hash = tx_data['hash']
            
            if not self.server:
                logger.warning("Stellar server not initialized, skipping operation extraction")
                return
            
            # Get operations for this transaction with rate limiting
            operations_response = await self._stellar_api_call(
                self.server.operations().for_transaction(transaction_hash).call
            )
            
            operations = operations_response.get('_embedded', {}).get('records', [])
            
            if not operations:
                logger.debug(f"No operations found for transaction {transaction_hash}")
                return
            
            stored_count = 0
            
            for op in operations:
                try:
                    # Only process UBEC-related operations
                    op_type = op.get('type')
                    
                    # Skip non-payment/exchange operations
                    if op_type not in ['payment', 'path_payment_strict_receive', 'path_payment_strict_send',
                                       'manage_buy_offer', 'manage_sell_offer', 'create_account', 'change_trust']:
                        continue
                    
                    # Check if this operation involves a UBEC token
                    asset_code = None
                    asset_issuer = None
                    
                    if op_type == 'payment':
                        asset_type = op.get('asset_type', 'native')
                        if asset_type != 'native':
                            asset_code = op.get('asset_code')
                            asset_issuer = op.get('asset_issuer')
                    elif op_type in ['path_payment_strict_receive', 'path_payment_strict_send']:
                        asset_type = op.get('asset_type', 'native')
                        if asset_type != 'native':
                            asset_code = op.get('asset_code')
                            asset_issuer = op.get('asset_issuer')
                    elif op_type in ['manage_buy_offer', 'manage_sell_offer']:
                        selling = op.get('selling_asset_type', 'native')
                        if selling != 'native':
                            asset_code = op.get('selling_asset_code')
                            asset_issuer = op.get('selling_asset_issuer')
                    elif op_type == 'change_trust':
                        asset_type = op.get('asset_type', 'native')
                        if asset_type != 'native':
                            asset_code = op.get('asset_code')
                            asset_issuer = op.get('asset_issuer')
                    
                    # Skip if not a UBEC token
                    if not asset_code or asset_code not in self.VALID_UBEC_TOKENS:
                        continue
                    
                    # Verify it's the correct issuer
                    expected_issuer = self._get_issuer_for_token(asset_code)
                    if asset_issuer != expected_issuer:
                        continue
                    
                    # Get element for this token
                    element = self.ELEMENT_MAP.get(asset_code, 'air')
                    
                    # Extract operation details
                    operation_id = op.get('id')
                    source_account = op.get('source_account')
                    created_at = op.get('created_at')
                    type_i = op.get('type_i', 0)
                    
                    # Extract from/to accounts based on operation type
                    from_account = None
                    to_account = None
                    amount = None
                    
                    if op_type == 'payment':
                        from_account = op.get('from')
                        to_account = op.get('to')
                        amount = Decimal(op.get('amount', '0'))
                    elif op_type in ['path_payment_strict_receive', 'path_payment_strict_send']:
                        from_account = op.get('from')
                        to_account = op.get('to')
                        amount = Decimal(op.get('amount', '0'))
                    elif op_type == 'create_account':
                        from_account = op.get('funder')
                        to_account = op.get('account')
                        amount = Decimal(op.get('starting_balance', '0'))
                    
                    # Map operation type
                    mapped_type = self.OPERATION_TYPE_MAP.get(op_type, op_type)
                    
                    # Store operation
                    query = """
                        INSERT INTO stellar_operations (
                            operation_id, transaction_hash, operation_element, asset_code,
                            type, type_i, source_account, amount, asset_type, asset_issuer,
                            from_account, to_account, details, created_at, metadata
                        )
                        VALUES (
                            $1, $2, $3::ubec_main.element_type, $4::ubec_main.token_code,
                            $5::ubec_main.transaction_type, $6, $7, $8, $9, $10,
                            $11, $12, $13, $14, $15
                        )
                        ON CONFLICT (operation_id) DO UPDATE SET
                            amount = EXCLUDED.amount,
                            details = EXCLUDED.details,
                            metadata = EXCLUDED.metadata
                    """
                    
                    # Create details JSONB
                    details = {
                        'type': op_type,
                        'source': source_account
                    }
                    
                    # Add type-specific details
                    if op_type in ['path_payment_strict_receive', 'path_payment_strict_send']:
                        details['source_amount'] = op.get('source_amount')
                        details['source_asset'] = f"{op.get('source_asset_code', 'XLM')}:{op.get('source_asset_issuer', 'native')}"
                        details['path'] = op.get('path', [])
                    
                    import json
                    details_json = json.dumps(details)
                    metadata_json = json.dumps(op)
                    
                    params = (
                        operation_id,
                        transaction_hash,
                        element,
                        asset_code,
                        mapped_type,
                        type_i,
                        source_account,
                        amount,
                        op.get('asset_type'),
                        asset_issuer,
                        from_account,
                        to_account,
                        details_json,
                        created_at,
                        metadata_json
                    )
                    
                    await self.db.execute(query, params)
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing operation {op.get('id')}: {e}")
                    continue
            
            if stored_count > 0:
                logger.debug(f"Stored {stored_count} UBEC operations for transaction {transaction_hash[:8]}...")
            
        except Exception as e:
            logger.error(f"Error extracting operations for transaction {tx_data.get('hash')}: {e}")
    
    # ========================================================================
    # LIQUIDITY POOL SYNCHRONIZATION
    # ========================================================================
    
    async def sync_liquidity_pools(
        self,
        asset_code: str,
        asset_issuer: str
    ) -> Dict[str, Any]:
        """
        Synchronize liquidity pools involving a specific asset.
        
        Args:
            asset_code: Asset code (UBEC, UBECrc, UBECgpi, UBECtt)
            asset_issuer: Asset issuer address
            
        Returns:
            dict: Sync results with pool and participant counts
        """
        logger.info(f"Syncing liquidity pools for {asset_code}:{asset_issuer[:8]}...")
        
        try:
            # Ensure settings are loaded
            if not self.settings or not self.horizon_url:
                logger.info("Settings not loaded yet, loading from database...")
                await self._load_settings_from_database()
            
            pools_synced = 0
            participants_synced = 0
            total_tvl = Decimal('0')
            
            # Use direct API call to fetch liquidity pools
            if not self.session:
                timeout = aiohttp.ClientTimeout(total=30)
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Build API URL
            url = f"{self.horizon_url}/liquidity_pools"
            params = {
                'reserves': f"{asset_code}:{asset_issuer}",
                'limit': 200
            }
            
            # Check rate limit before request
            await self.rate_limiter.check_and_wait()
            self.rate_limiter.total_requests += 1
            
            async with self.session.get(url, params=params) as response:
                # Update rate limits
                self.rate_limiter.update_from_headers(dict(response.headers))
                
                if response.status == 429:
                    # Handle rate limit
                    await self.rate_limiter.handle_429(response, 0)
                    return {
                        'success': False,
                        'asset_code': asset_code,
                        'error': 'Rate limited'
                    }
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error fetching liquidity pools: {response.status} - {error_text}")
                    return {
                        'success': False,
                        'asset_code': asset_code,
                        'error': f"API error: {response.status}"
                    }
                
                data = await response.json()
                pools = data.get('_embedded', {}).get('records', [])
                
                logger.info(f"Found {len(pools)} liquidity pools for {asset_code}")
                
                # Process each pool
                for pool_data in pools:
                    try:
                        pool_id = await self._store_liquidity_pool(pool_data, asset_code)
                        
                        if pool_id:
                            pools_synced += 1
                            
                            # Calculate pool TVL
                            reserves = pool_data.get('reserves', [])
                            primary_issuer = self._get_issuer_for_token(asset_code)
                            
                            for reserve in reserves:
                                asset_str = reserve.get('asset', '')
                                if f"{asset_code}:{primary_issuer}" in asset_str:
                                    amount = Decimal(reserve.get('amount', '0'))
                                    total_tvl += amount
                                    break
                        
                    except Exception as e:
                        logger.error(f"Error processing pool {pool_data.get('id')}: {e}")
                        continue
                
                # Sync participants
                logger.info(f"Syncing LP participants for {asset_code}...")
                participants_synced = await self._sync_all_pool_participants(asset_code)
                
                logger.info(
                    f"✓ LP sync complete for {asset_code}: "
                    f"{pools_synced} pools, {participants_synced} participants, "
                    f"TVL: {total_tvl:,.2f}"
                )
                
                return {
                    'success': True,
                    'asset_code': asset_code,
                    'pools_synced': pools_synced,
                    'participants_synced': participants_synced,
                    'total_tvl': float(total_tvl)
                }
                
        except Exception as e:
            logger.error(f"Error syncing liquidity pools for {asset_code}: {e}")
            return {
                'success': False,
                'asset_code': asset_code,
                'error': str(e)
            }
    
    async def _store_liquidity_pool(
        self,
        pool_data: Dict,
        primary_asset: str
    ) -> Optional[str]:
        """
        Store liquidity pool metadata in database.
        
        Args:
            pool_data: Pool data from Stellar API
            primary_asset: Primary UBEC asset in the pool
            
        Returns:
            str: Pool ID, or None if failed
        """
        try:
            pool_id = pool_data['id']
            fee_bp = int(pool_data.get('fee_bp', 30))
            trustline_count = int(pool_data.get('total_trustlines', 0))
            total_shares = Decimal(pool_data.get('total_shares', '0'))
            
            # Parse reserves
            reserves = pool_data.get('reserves', [])
            if len(reserves) < 2:
                logger.warning(f"Pool {pool_id} has insufficient reserves")
                return None
            
            # Parse asset A
            asset_a_str = reserves[0].get('asset', 'native')
            if asset_a_str == 'native':
                asset_a_code = 'XLM'
                asset_a_issuer = None
            else:
                parts = asset_a_str.split(':')
                asset_a_code = parts[0] if parts else 'UNKNOWN'
                asset_a_issuer = parts[1] if len(parts) > 1 else None
            
            # Parse asset B
            asset_b_str = reserves[1].get('asset', 'native')
            if asset_b_str == 'native':
                asset_b_code = 'XLM'
                asset_b_issuer = None
            else:
                parts = asset_b_str.split(':')
                asset_b_code = parts[0] if parts else 'UNKNOWN'
                asset_b_issuer = parts[1] if len(parts) > 1 else None
            
            # Get reserve amounts
            reserve_a = Decimal(reserves[0].get('amount', '0'))
            reserve_b = Decimal(reserves[1].get('amount', '0'))
            
            # Determine UBEC asset position
            ubec_asset_position = None
            ubec_balance = Decimal('0')
            
            primary_issuer = self._get_issuer_for_token(primary_asset)
            
            if asset_a_code == primary_asset and asset_a_issuer == primary_issuer:
                ubec_asset_position = 'a'
                ubec_balance = reserve_a
            elif asset_b_code == primary_asset and asset_b_issuer == primary_issuer:
                ubec_asset_position = 'b'
                ubec_balance = reserve_b
            
            # Create pair name
            pair = f"{asset_a_code}/{asset_b_code}"
            
            # Get element
            element = self.ELEMENT_MAP.get(primary_asset, 'air')
            
            # Store in database
            query = """
                INSERT INTO liquidity_pools (
                    id, asset_a_code, asset_a_issuer, asset_b_code, asset_b_issuer,
                    pair, primary_element, token_code,
                    reserve_a, reserve_b, total_shares, balance,
                    ubec_asset_position, fee_bp, trustline_count,
                    sync_timestamp, sync_status
                )
                VALUES (
                    $1, $2, $3, $4, $5, 
                    $6, $7::ubec_main.element_type, $8::ubec_main.token_code,
                    $9, $10, $11, $12,
                    $13, $14, $15,
                    NOW(), 'active'
                )
                ON CONFLICT (id) DO UPDATE SET
                    reserve_a = EXCLUDED.reserve_a,
                    reserve_b = EXCLUDED.reserve_b,
                    total_shares = EXCLUDED.total_shares,
                    balance = EXCLUDED.balance,
                    trustline_count = EXCLUDED.trustline_count,
                    sync_timestamp = NOW(),
                    last_modified_at = NOW()
            """
            
            params = (
                pool_id,
                asset_a_code,
                asset_a_issuer,
                asset_b_code,
                asset_b_issuer,
                pair,
                element,
                primary_asset,
                reserve_a,
                reserve_b,
                total_shares,
                ubec_balance,
                ubec_asset_position,
                fee_bp,
                trustline_count
            )
            
            await self.db.execute(query, params)
            
            logger.debug(f"Liquidity pool stored: {pair} ({pool_id[:8]}...): {ubec_balance} {primary_asset}")
            return pool_id
            
        except Exception as e:
            logger.error(f"Error storing liquidity pool: {e}")
            return None
    
    async def _sync_all_pool_participants(self, token_code: str) -> int:
        """
        Sync LP participants by checking all accounts for liquidity_pool_shares.
        
        Args:
            token_code: Token code to sync participants for
            
        Returns:
            int: Number of participants synced
        """
        try:
            # Get all accounts
            query = "SELECT account_id FROM stellar_accounts"
            account_rows = await self.db.fetch_all(query)
            
            if not account_rows:
                logger.info("No accounts in database to check for LP positions")
                return 0
            
            logger.info(f"Checking {len(account_rows)} accounts for LP positions...")
            
            participants_synced = 0
            accounts_checked = 0
            
            element = self.ELEMENT_MAP.get(token_code, 'air')
            
            for row in account_rows:
                account_id = row['account_id']
                
                try:
                    # Fetch account data with rate limiting
                    account_data = await self._stellar_api_call(
                        self.server.accounts().account_id(account_id).call
                    )
                    
                    # Look for liquidity_pool_shares
                    balances = account_data.get('balances', [])
                    
                    for balance in balances:
                        if balance.get('asset_type') == 'liquidity_pool_shares':
                            pool_id = balance.get('liquidity_pool_id')
                            shares = Decimal(balance.get('balance', '0'))
                            
                            if shares > 0:
                                # Check if this pool is tracked
                                pool_query = """
                                    SELECT total_shares, balance, token_code
                                    FROM liquidity_pools
                                    WHERE id = $1 AND token_code = $2
                                """
                                pool_data = await self.db.fetch_one(
                                    pool_query,
                                    (pool_id, token_code)
                                )
                                
                                if pool_data:
                                    # Calculate ownership
                                    total_shares = Decimal(pool_data['total_shares'])
                                    pool_ubec_balance = Decimal(pool_data['balance'])
                                    
                                    if total_shares > 0:
                                        ownership_percentage = (shares / total_shares) * Decimal('100')
                                        ubec_balance = (shares / total_shares) * pool_ubec_balance
                                    else:
                                        ownership_percentage = Decimal('0')
                                        ubec_balance = Decimal('0')
                                    
                                    # Store participant position
                                    insert_query = """
                                        INSERT INTO liquidity_pool_owners (
                                            account_id, liquidity_pool_id, shares,
                                            ownership_percentage, ubec_balance,
                                            element, token_code,
                                            sync_timestamp, sync_status
                                        )
                                        VALUES (
                                            $1, $2, $3, $4, $5,
                                            $6::ubec_main.element_type, $7::ubec_main.token_code,
                                            NOW(), 'synced'
                                        )
                                        ON CONFLICT (account_id, liquidity_pool_id) DO UPDATE SET
                                            shares = EXCLUDED.shares,
                                            ownership_percentage = EXCLUDED.ownership_percentage,
                                            ubec_balance = EXCLUDED.ubec_balance,
                                            sync_timestamp = NOW(),
                                            last_modified_at = NOW()
                                    """
                                    
                                    await self.db.execute(insert_query, (
                                        account_id, pool_id, shares,
                                        ownership_percentage, ubec_balance,
                                        element, token_code
                                    ))
                                    
                                    participants_synced += 1
                                    logger.debug(
                                        f"LP position synced: {account_id[:8]}... "
                                        f"owns {ownership_percentage:.4f}% of pool {pool_id[:8]}..."
                                    )
                    
                    accounts_checked += 1
                    
                    if accounts_checked % 50 == 0:
                        logger.info(
                            f"  Progress: {accounts_checked}/{len(account_rows)} accounts checked, "
                            f"{participants_synced} LP positions found"
                        )
                    
                except CircuitBreakerException:
                    logger.error("Circuit breaker opened during LP participant sync")
                    break
                except RateLimitException:
                    logger.warning("Rate limited during LP participant sync, continuing...")
                    continue
                except Exception as e:
                    logger.error(f"Error checking LP positions for {account_id}: {e}")
                    continue
            
            logger.info(
                f"✓ LP participant sync complete: {participants_synced} positions found "
                f"in {accounts_checked} accounts"
            )
            
            return participants_synced
            
        except Exception as e:
            logger.error(f"Error syncing LP participants: {e}")
            return 0
    
    # ========================================================================
    # ACCOUNT DISCOVERY
    # ========================================================================
    
    async def discover_accounts(
        self,
        max_accounts: int = 1000,
        asset_code: str = 'UBEC'
    ) -> int:
        """
        Discover account holders (compatibility wrapper).
        
        Args:
            max_accounts: Maximum number of accounts to discover
            asset_code: Asset code to discover holders for
            
        Returns:
            int: Number of accounts discovered
        """
        logger.info(f"Discovering {asset_code} holders (max: {max_accounts})...")
        
        count = await self.discover_asset_holders(
            asset_code=asset_code,
            limit=200,
            max_accounts=max_accounts
        )
        
        logger.info(f"✓ Discovery complete: {count} {asset_code} holders found")
        
        return count
    
    async def discover_asset_holders(
        self,
        asset_code: str,
        limit: int = 200,
        max_accounts: int = 1000
    ) -> int:
        """
        Discover accounts holding a specific asset.
        
        Args:
            asset_code: Asset code to search for
            limit: Records per page
            max_accounts: Maximum accounts to discover
            
        Returns:
            int: Number of accounts discovered
        """
        # Ensure settings loaded
        if not self.settings:
            logger.info("Settings not loaded yet, loading from database...")
            await self._load_settings_from_database()
        
        if not self.server:
            logger.error("Stellar server not initialized")
            return 0
        
        logger.info(f"Discovering holders of {asset_code}...")
        
        try:
            discovered = 0
            cursor = None
            
            asset_issuer = self._get_issuer_for_token(asset_code)
            logger.info(f"Using issuer: {asset_issuer} for {asset_code}")
            
            from stellar_sdk import Asset
            asset = Asset(asset_code, asset_issuer)
            
            while discovered < max_accounts:
                # Build request
                request = self.server.accounts().for_asset(asset).limit(limit)
                
                if cursor:
                    request = request.cursor(cursor)
                
                # Fetch accounts with rate limiting
                try:
                    response = await self._stellar_api_call(request.call)
                except CircuitBreakerException:
                    logger.error("Circuit breaker opened during discovery")
                    break
                except RateLimitException:
                    logger.warning("Rate limited during discovery")
                    break
                except Exception as e:
                    logger.error(f"Error fetching accounts: {e}")
                    break
                
                # Get records
                records = response.get('_embedded', {}).get('records', [])
                
                if not records:
                    logger.info(f"No more {asset_code} holders found")
                    break
                
                # Process each account
                for account_data in records:
                    try:
                        await self._store_account(account_data)
                        
                        balances = account_data.get('balances', [])
                        await self._store_balances(account_data['id'], balances)
                        
                        discovered += 1
                        
                        if discovered % 50 == 0:
                            logger.info(f"  Discovered {discovered} {asset_code} holders...")
                        
                    except Exception as e:
                        logger.error(f"Error processing account {account_data.get('id')}: {e}")
                        continue
                
                # Check for next page
                next_link = response.get('_links', {}).get('next', {}).get('href')
                if not next_link or discovered >= max_accounts:
                    break
                
                # Extract cursor
                if 'cursor=' in next_link:
                    cursor = next_link.split('cursor=')[1].split('&')[0]
                else:
                    break
                
                await asyncio.sleep(0.5)
            
            logger.info(f"✓ Discovered {discovered} holders of {asset_code}")
            return discovered
            
        except Exception as e:
            logger.error(f"Error discovering {asset_code} holders: {e}")
            return 0
    
    async def discover_all_ubec_holders(self, max_per_asset: int = 1000) -> Dict[str, int]:
        """
        Discover all holders of all 4 UBEC tokens.
        
        Args:
            max_per_asset: Maximum accounts per asset
            
        Returns:
            dict: Discovery results per asset
        """
        logger.info("="*70)
        logger.info("Discovering All UBEC Token Holders")
        logger.info("="*70)
        
        results = {}
        assets = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']
        
        for asset_code in assets:
            logger.info(f"\nSearching for {asset_code} holders...")
            count = await self.discover_asset_holders(
                asset_code=asset_code,
                limit=200,
                max_accounts=max_per_asset
            )
            results[asset_code] = count
        
        total = sum(results.values())
        logger.info("="*70)
        logger.info(f"Discovery Complete: {total} total account records")
        for asset, count in results.items():
            logger.info(f"  {asset}: {count} holders")
        logger.info("="*70)
        
        return results
    
    # ========================================================================
    # BULK SYNCHRONIZATION METHODS
    # ========================================================================
    
    async def sync_account_data(
        self,
        asset_code: str = 'UBEC',
        limit: Optional[int] = 5000
    ) -> Dict[str, Any]:
        """
        Synchronize account data for all holders.
        
        Args:
            asset_code: Asset code to sync
            limit: Maximum accounts to sync
            
        Returns:
            dict: Sync results
        """
        logger.info(f"Syncing account data for {asset_code} holders (limit: {limit})...")
        
        try:
            if not self.settings:
                await self._load_settings_from_database()
            
            # Get accounts
            if limit is None:
                query = """
                    SELECT DISTINCT account_id
                    FROM ubec_balances
                    WHERE token_code = $1
                """
                rows = await self.db.fetch_all(query, (asset_code,))
            else:
                query = """
                    SELECT DISTINCT account_id
                    FROM ubec_balances
                    WHERE token_code = $1
                    LIMIT $2
                """
                rows = await self.db.fetch_all(query, (asset_code, limit))
            
            if not rows:
                logger.warning(f"No accounts found holding {asset_code}")
                return {
                    'success': True,
                    'asset_code': asset_code,
                    'accounts_synced': 0,
                    'message': f'No accounts found holding {asset_code}'
                }
            
            synced = 0
            failed = 0
            
            for row in rows:
                account_id = row['account_id']
                
                try:
                    success = await self.sync_account(account_id)
                    if success:
                        synced += 1
                    else:
                        failed += 1
                    
                    if synced % 50 == 0:
                        logger.info(f"  Progress: {synced}/{len(rows)} accounts synced")
                    
                except Exception as e:
                    logger.error(f"Error syncing account {account_id}: {e}")
                    failed += 1
                    continue
            
            logger.info(f"✓ Account sync complete: {synced} synced, {failed} failed")
            
            return {
                'success': True,
                'asset_code': asset_code,
                'accounts_synced': synced,
                'accounts_failed': failed,
                'total_accounts': len(rows)
            }
            
        except Exception as e:
            logger.error(f"Error syncing account data for {asset_code}: {e}")
            return {
                'success': False,
                'asset_code': asset_code,
                'error': str(e)
            }
    
    async def sync_balance_data(
        self,
        asset_code: str = 'UBEC'
    ) -> Dict[str, Any]:
        """
        Synchronize balance data for all holders.
        
        Args:
            asset_code: Asset code to sync
            
        Returns:
            dict: Sync results
        """
        logger.info(f"Syncing balance data for {asset_code} holders...")
        
        try:
            if not self.settings:
                await self._load_settings_from_database()
            
            if not self.server:
                logger.error("Stellar server not initialized")
                return {
                    'success': False,
                    'asset_code': asset_code,
                    'error': 'Stellar server not initialized'
                }
            
            # Get accounts
            query = """
                SELECT DISTINCT account_id
                FROM ubec_balances
                WHERE token_code = $1
            """
            
            rows = await self.db.fetch_all(query, (asset_code,))
            
            if not rows:
                logger.warning(f"No accounts found holding {asset_code}")
                return {
                    'success': True,
                    'asset_code': asset_code,
                    'balances_synced': 0,
                    'message': f'No accounts found holding {asset_code}'
                }
            
            synced = 0
            failed = 0
            
            for row in rows:
                account_id = row['account_id']
                
                try:
                    # Fetch account with rate limiting
                    account = await self._stellar_api_call(
                        self.server.accounts().account_id(account_id).call
                    )
                    
                    balances = account.get('balances', [])
                    await self._store_balances(account_id, balances)
                    
                    synced += 1
                    
                    if synced % 50 == 0:
                        logger.info(f"  Progress: {synced}/{len(rows)} balances synced")
                    
                except Exception as e:
                    logger.error(f"Error syncing balance for {account_id}: {e}")
                    failed += 1
                    continue
            
            logger.info(f"✓ Balance sync complete: {synced} synced, {failed} failed")
            
            return {
                'success': True,
                'asset_code': asset_code,
                'balances_synced': synced,
                'balances_failed': failed,
                'total_balances': len(rows)
            }
            
        except Exception as e:
            logger.error(f"Error syncing balance data for {asset_code}: {e}")
            return {
                'success': False,
                'asset_code': asset_code,
                'error': str(e)
            }
    
    async def sync_transaction_data(
        self,
        asset_code: str = 'UBEC',
        days_back: int = 7,
        limit_per_account: int = 100
    ) -> Dict[str, Any]:
        """
        Synchronize recent transactions.
        
        Args:
            asset_code: Asset code to sync
            days_back: Number of days of history
            limit_per_account: Maximum transactions per account
            
        Returns:
            dict: Sync results
        """
        logger.info(f"Syncing transaction data for {asset_code} holders (last {days_back} days)...")
        
        try:
            if not self.settings:
                await self._load_settings_from_database()
            
            # Get accounts
            query = """
                SELECT DISTINCT account_id
                FROM ubec_balances
                WHERE token_code = $1
            """
            
            rows = await self.db.fetch_all(query, (asset_code,))
            
            if not rows:
                logger.warning(f"No accounts found holding {asset_code}")
                return {
                    'success': True,
                    'asset_code': asset_code,
                    'transactions_synced': 0,
                    'message': f'No accounts found holding {asset_code}'
                }
            
            total_transactions = 0
            accounts_processed = 0
            accounts_failed = 0
            
            for row in rows:
                account_id = row['account_id']
                
                try:
                    tx_count = await self.sync_transactions(
                        account_id=account_id,
                        limit=limit_per_account
                    )
                    
                    total_transactions += tx_count
                    accounts_processed += 1
                    
                    if accounts_processed % 20 == 0:
                        logger.info(
                            f"  Progress: {accounts_processed}/{len(rows)} accounts, "
                            f"{total_transactions} transactions synced"
                        )
                    
                except Exception as e:
                    logger.error(f"Error syncing transactions for {account_id}: {e}")
                    accounts_failed += 1
                    continue
            
            logger.info(
                f"✓ Transaction sync complete: {total_transactions} transactions from "
                f"{accounts_processed} accounts ({accounts_failed} failed)"
            )
            
            return {
                'success': True,
                'asset_code': asset_code,
                'transactions_synced': total_transactions,
                'accounts_processed': accounts_processed,
                'accounts_failed': accounts_failed,
                'total_accounts': len(rows)
            }
            
        except Exception as e:
            logger.error(f"Error syncing transaction data for {asset_code}: {e}")
            return {
                'success': False,
                'asset_code': asset_code,
                'error': str(e)
            }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current synchronization status.
        
        Returns:
            dict: Synchronization statistics
        """
        try:
            stats = {}
            
            # Count accounts
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM stellar_accounts")
            stats['total_accounts'] = result['count'] if result else 0
            
            # Count balances
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM ubec_balances")
            stats['total_balances'] = result['count'] if result else 0
            
            # Count transactions
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM stellar_transactions")
            stats['total_transactions'] = result['count'] if result else 0
            
            # Count liquidity pools
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM liquidity_pools")
            stats['total_pools'] = result['count'] if result else 0
            
            # Count LP owners
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM liquidity_pool_owners")
            stats['total_lp_owners'] = result['count'] if result else 0
            
            # Get last activity
            result = await self.db.fetch_one(
                "SELECT MAX(last_modified_at) as last_activity FROM stellar_accounts"
            )
            stats['last_sync_time'] = result['last_activity'] if result and result['last_activity'] else 'Never'
            
            # Rate limit info
            if self.rate_limiter:
                stats['rate_limiter'] = self.rate_limiter.get_metrics()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            dict: Health status information
        """
        health = {
            'status': 'unknown',
            'database': False,
            'stellar': False,
            'settings_loaded': bool(self.settings),
            'rate_limiter_initialized': self.rate_limiter is not None
        }
        
        try:
            # Check database
            result = await self.db.fetch_one("SELECT 1 as test")
            health['database'] = result is not None
            
            # Check Stellar connection
            if self.server:
                try:
                    await self._stellar_api_call(
                        self.server.ledgers().limit(1).call
                    )
                    health['stellar'] = True
                except:
                    health['stellar'] = False
            
            # Check circuit breaker
            if self.rate_limiter:
                health['circuit_breaker'] = self.rate_limiter.circuit_breaker.state.value
                health['rate_limit_metrics'] = self.rate_limiter.get_metrics()
            
            # Determine overall status
            if health['database'] and health['stellar'] and health['settings_loaded']:
                if self.rate_limiter and self.rate_limiter.circuit_breaker.state == CircuitState.OPEN:
                    health['status'] = 'degraded'
                else:
                    health['status'] = 'healthy'
            elif health['database']:
                health['status'] = 'degraded'
            else:
                health['status'] = 'unhealthy'
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
        
        return health


# ==================== MODULE EXPORTS ====================

__all__ = [
    'UBECDataSynchronizer',
    'SyncException',
    'RateLimitException',
    'CircuitBreakerException',
    'CircuitBreaker',
    'RateLimiter'
]
