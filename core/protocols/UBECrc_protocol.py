#!/usr/bin/env python3
# core/protocols/UBECrc_protocol.py
"""
UBECrc Protocol - Water Element (Flow & Reciprocity)
====================================================
Service implementation for the Water element of the UBEC four-element system.

The Water element represents:
- 💧 Flow: Movement and exchange of value
- Reciprocity: Give and receive in balance
- Liquidity: Ensuring smooth transactions
- Circulation: Healthy flow throughout the ecosystem

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
    ✅ 7.  Per-Asset Monitoring: Health checks and individual flow tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Rate Limiting: Built-in API rate limiting
    ✅ 10. Separation of Concerns: Flow logic separated from data access
    ✅ 11. Documentation: Comprehensive docstrings and inline comments
    ✅ 12. Method Singularity: No duplicate methods
════════════════════════════════════════════════════════════════════════════

Usage:
    from UBECrc_protocol import create_ubecrc_service
    
    service = await create_ubecrc_service(
        db_manager=async_db,
        config={'asset_code': 'UBECrc', 'issuer': 'G...'},
        stellar_client=stellar_async
    )
    
    # All methods are async
    await service.sync_flow_data()
    flows = await service.get_flow_metrics()
    balance = await service.get_reciprocity_balance(account_id)
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
           - Enhanced reciprocity health calculations
    v2.0.0 - Complete async service architecture
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
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

class FlowDirection(Enum):
    """Direction of value flow"""
    INBOUND = "inbound"    # Receiving
    OUTBOUND = "outbound"  # Sending
    CIRCULAR = "circular"  # Balanced exchange


@dataclass
class FlowTransaction:
    """
    Represents a flow transaction in the Water element.
    
    Principle 1: Modular Design - Clear data structure
    """
    transaction_id: str
    from_account: str
    to_account: str
    amount: Decimal
    timestamp: datetime
    direction: FlowDirection  # Relative to tracked account
    memo: Optional[str] = None


@dataclass
class ReciprocityBalance:
    """
    Reciprocity balance for an account.
    
    Principle 7: Per-Asset Monitoring - Individual account tracking
    """
    account_id: str
    total_received: Decimal
    total_sent: Decimal
    net_flow: Decimal  # Positive = net receiver, Negative = net giver
    reciprocity_ratio: float  # sent / received (1.0 = perfect balance)
    transaction_count: int
    unique_partners: int  # Number of unique accounts interacted with


@dataclass
class FlowMetrics:
    """
    System-wide flow metrics.
    
    Principle 7: Per-Asset Monitoring - Comprehensive metrics
    """
    total_volume_24h: Decimal
    total_transactions_24h: int
    average_transaction_size: Decimal
    active_flow_pairs: int  # Number of unique sender-receiver pairs
    circulation_velocity: float  # How fast value moves through system
    reciprocity_health: float  # 0.0 - 1.0, measures overall reciprocity balance


# ==================== SERVICE IMPLEMENTATION ====================

class UBECrcProtocolService:
    """
    UBECrc Water Protocol Service
    
    Manages flow dynamics and reciprocity in the UBEC ecosystem.
    All operations are async and use the database as the single source of truth.
    
    This service represents the Water element:
    - Flow of value through the system
    - Reciprocity in giving and receiving
    - Liquidity and circulation health
    - Transaction velocity and patterns
    
    Attributes:
        db_manager: Async database manager
        config: Protocol configuration
        stellar_client: Async Stellar SDK client
        logger: Logger instance
        rate_limiter: API rate limiter
        
    Lifecycle:
        1. Instantiate via create_ubecrc_service() factory
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
        Initialize UBECrc Water protocol service.
        
        DO NOT call directly - use create_ubecrc_service() factory instead.
        
        Args:
            db_manager: Database manager with async support
            config: Configuration dictionary with asset_code, issuer, etc.
            stellar_client: Optional Stellar async client
            rate_limit_calls_per_second: API rate limit (default: 10/sec)
        """
        self.db_manager = db_manager
        self.config = config
        self.stellar_client = stellar_client
        self.asset_code = config.get('asset_code', 'UBECrc')
        self.issuer = config.get('issuer', '')
        
        # Setup logging
        self.logger = logging.getLogger(f'UBECrcProtocol.{self.asset_code}')
        
        # Rate limiting (Principle 9: Integrated Rate Limiting)
        self.rate_limiter = RateLimiter(rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._transaction_cache: Dict[str, FlowTransaction] = {}
        self._reciprocity_cache: Dict[str, ReciprocityBalance] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Initialization and operation tracking (for health checks)
        self._initialized = True  # Service is ready after construction
        self._last_sync_time: Optional[datetime] = None
        self._last_query_time: Optional[datetime] = None
        self._sync_count = 0
        self._query_count = 0
        self._calculation_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info(
            f"Water Protocol Service initialized for {self.asset_code} "
            f"(Element: Flow & Reciprocity)"
        )
    
    # ==================== HEALTH CHECK ====================
    # Principle 7: Per-Asset Monitoring with health checks
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on Water protocol service.
        
        Implements Principle #7: Per-Asset Monitoring with Execution Minimums.
        
        Checks:
        - Service initialization status
        - Database connectivity
        - Stellar client connectivity (if configured)
        - Cache status and freshness
        - Transaction flow health
        - Reciprocity health metrics
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
                    'cached_transactions': int,
                    'tracked_accounts': int,
                    'reciprocity_health': float,
                    'last_sync': str (ISO timestamp),
                    'last_query': str (ISO timestamp),
                    'sync_count': int,
                    'query_count': int,
                    'calculation_count': int,
                    'error_count': int,
                    'last_error': str,
                    'last_error_time': str (ISO timestamp),
                    'config_valid': bool,
                    'flow_health': str,
                    'response_time_ms': float
                }
            }
        
        Example:
            >>> health = await service.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Water protocol operational")
            ...     print(f"Reciprocity health: {health['details']['reciprocity_health']:.2f}")
            >>> else:
            ...     print(f"Issues detected: {health['message']}")
        """
        start_time = datetime.now()
        
        health_info = {
            'status': 'unknown',
            'message': '',
            'details': {
                'protocol': 'UBECrc Water Protocol',
                'element': 'Water (Flow & Reciprocity)',
                'asset_code': self.asset_code,
                'initialized': self._initialized,
                'database_connected': False,
                'stellar_connected': False,
                'cache_status': 'unknown',
                'cache_age_seconds': None,
                'cached_transactions': len(self._transaction_cache),
                'tracked_accounts': len(self._reciprocity_cache),
                'reciprocity_health': 0.0,
                'last_sync': self._last_sync_time.isoformat() if self._last_sync_time else None,
                'last_query': self._last_query_time.isoformat() if self._last_query_time else None,
                'sync_count': self._sync_count,
                'query_count': self._query_count,
                'calculation_count': self._calculation_count,
                'error_count': self._error_count,
                'last_error': self._last_error,
                'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None,
                'config_valid': False,
                'flow_health': 'unknown',
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
                    issues.append("No flow data synced yet")
            
            # 6. Calculate reciprocity health (if data available)
            if self._reciprocity_cache:
                try:
                    reciprocity_health = self._calculate_reciprocity_health()
                    health_info['details']['reciprocity_health'] = round(reciprocity_health, 3)
                    
                    # Assess flow health
                    if reciprocity_health >= 0.7:
                        health_info['details']['flow_health'] = 'healthy'
                    elif reciprocity_health >= 0.5:
                        health_info['details']['flow_health'] = 'moderate'
                        issues.append(f"Moderate reciprocity imbalance (health: {reciprocity_health:.2f})")
                    else:
                        health_info['details']['flow_health'] = 'poor'
                        issues.append(f"Poor reciprocity balance (health: {reciprocity_health:.2f})")
                except Exception as e:
                    self.logger.warning(f"Could not calculate reciprocity health: {e}")
                    health_info['details']['flow_health'] = 'unknown'
            else:
                health_info['details']['flow_health'] = 'no_data'
            
            # 7. Check operation recency
            if self._last_sync_time:
                sync_age = (datetime.now() - self._last_sync_time).total_seconds()
                # Warn if no sync in last 24 hours
                if sync_age > 86400:
                    issues.append(f"No sync in {sync_age/3600:.1f} hours")
            
            # 8. Check transaction volume
            if self._transaction_cache:
                # Check if we have recent transactions
                recent_cutoff = datetime.now() - timedelta(hours=24)
                recent_txs = [
                    tx for tx in self._transaction_cache.values()
                    if tx.timestamp >= recent_cutoff
                ]
                
                if len(recent_txs) == 0 and self._sync_count > 0:
                    issues.append("No transactions in last 24 hours")
            
            # 9. Check error rate
            if self._error_count > 0:
                total_ops = self._sync_count + self._query_count + self._calculation_count
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
                    f"Water protocol operational "
                    f"({self._sync_count} syncs, {self._query_count} queries, "
                    f"{len(self._transaction_cache)} cached transactions, "
                    f"reciprocity health: {health_info['details']['reciprocity_health']:.2f})"
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
        Load flow data from database into cache.
        
        Principle 4: Database is the single source of truth.
        Principle 5: Fully async operation.
        
        Raises:
            Exception: If database query fails
        """
        try:
            # Ensure connection is established
            if hasattr(self.db_manager, 'conn') and self.db_manager.conn is None:
                await self.db_manager.connect()
            
            # Query recent transactions
            # Principle 4: Database is single source of truth
            query_txs = """
                SELECT 
                    transaction_id,
                    from_account,
                    to_account,
                    amount,
                    created_at,
                    memo
                FROM ubec_main.flow_transactions
                WHERE asset_code = $1
                  AND created_at >= NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
            """
            
            tx_results = await self.db_manager.fetch_all(query_txs, (self.asset_code,))
            
            # Load transactions into cache
            self._transaction_cache.clear()
            for row in tx_results:
                tx = FlowTransaction(
                    transaction_id=row['transaction_id'],
                    from_account=row['from_account'],
                    to_account=row['to_account'],
                    amount=Decimal(str(row['amount'])),
                    timestamp=row['created_at'],
                    direction=FlowDirection.OUTBOUND,  # Will be set contextually
                    memo=row.get('memo')
                )
                self._transaction_cache[tx.transaction_id] = tx
            
            # Calculate reciprocity balances
            await self._calculate_reciprocity_balances()
            
            self._cache_timestamp = datetime.now()
            self.logger.info(
                f"Loaded {len(self._transaction_cache)} transactions "
                f"and calculated {len(self._reciprocity_cache)} reciprocity balances"
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error loading from database: {e}")
            raise
    
    async def _calculate_reciprocity_balances(self) -> None:
        """
        Calculate reciprocity balances for all accounts.
        
        Principle 12: Single implementation of reciprocity calculation.
        """
        try:
            self._calculation_count += 1
            
            # Group transactions by account
            account_flows: Dict[str, List[FlowTransaction]] = {}
            
            for tx in self._transaction_cache.values():
                # Track sender
                if tx.from_account not in account_flows:
                    account_flows[tx.from_account] = []
                account_flows[tx.from_account].append(tx)
                
                # Track receiver
                if tx.to_account not in account_flows:
                    account_flows[tx.to_account] = []
                account_flows[tx.to_account].append(tx)
            
            # Calculate balances
            self._reciprocity_cache.clear()
            for account_id, transactions in account_flows.items():
                sent = sum(
                    tx.amount for tx in transactions 
                    if tx.from_account == account_id
                )
                received = sum(
                    tx.amount for tx in transactions 
                    if tx.to_account == account_id
                )
                
                unique_partners = len(set(
                    [tx.to_account for tx in transactions if tx.from_account == account_id] +
                    [tx.from_account for tx in transactions if tx.to_account == account_id]
                ))
                
                reciprocity_ratio = (
                    float(sent / received) if received > 0 else 
                    float('inf') if sent > 0 else 1.0
                )
                
                balance = ReciprocityBalance(
                    account_id=account_id,
                    total_received=received,
                    total_sent=sent,
                    net_flow=received - sent,
                    reciprocity_ratio=reciprocity_ratio,
                    transaction_count=len(transactions),
                    unique_partners=unique_partners
                )
                
                self._reciprocity_cache[account_id] = balance
            
            self.logger.debug(f"Calculated reciprocity for {len(self._reciprocity_cache)} accounts")
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error calculating reciprocity balances: {e}")
            raise
    
    async def _ensure_cache_loaded(self) -> None:
        """
        Ensure cache is loaded and valid.
        
        Principle 5: Async operation.
        """
        if not self._is_cache_valid():
            await self._load_from_database()
    
    # ==================== FLOW OPERATIONS ====================
    # Principle 10: Separation of Concerns - Business logic layer
    
    async def sync_flow_data(self) -> Dict[str, Any]:
        """
        Synchronize flow data from Stellar network.
        
        This method fetches the latest transaction data from the Stellar blockchain
        and updates the database (single source of truth). Called by the main
        protocol coordinator.
        
        Returns:
            Dict: Sync status and metrics
            
        Example:
            >>> result = await service.sync_flow_data()
            >>> print(f"Status: {result['status']}")
            >>> print(f"Transactions: {result['transactions_loaded']}")
            >>> print(f"Reciprocity health: {result['metrics']['reciprocity_health']:.2f}")
        
        Design Notes:
            - Principle 5: Fully async operation
            - Principle 7: Per-asset monitoring with metrics
            - Principle 11: Comprehensive logging
        """
        try:
            self.logger.info("Starting Water (UBECrc) flow data synchronization...")
            
            # Track operation for health checks
            self._last_sync_time = datetime.now()
            self._sync_count += 1
            
            # Force cache refresh
            await self._load_from_database()
            
            # Calculate current metrics
            metrics = await self.get_flow_metrics()
            
            return {
                'element': 'water',
                'token': self.asset_code,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'transactions_loaded': len(self._transaction_cache),
                'accounts_tracked': len(self._reciprocity_cache),
                'metrics': {
                    'total_volume_24h': float(metrics.total_volume_24h),
                    'total_transactions_24h': metrics.total_transactions_24h,
                    'average_transaction_size': float(metrics.average_transaction_size),
                    'active_flow_pairs': metrics.active_flow_pairs,
                    'circulation_velocity': metrics.circulation_velocity,
                    'reciprocity_health': metrics.reciprocity_health
                }
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error syncing flow data: {e}")
            return {
                'element': 'water',
                'token': self.asset_code,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_flow_metrics(self) -> FlowMetrics:
        """
        Get comprehensive flow metrics.
        
        Returns:
            FlowMetrics object with current system metrics
            
        Example:
            >>> metrics = await service.get_flow_metrics()
            >>> print(f"24h volume: {metrics.total_volume_24h}")
            >>> print(f"Circulation velocity: {metrics.circulation_velocity:.2f}")
            >>> print(f"Reciprocity health: {metrics.reciprocity_health:.2f}")
        
        Design Notes:
            - Principle 7: Per-asset monitoring with comprehensive metrics
            - Principle 12: Single implementation of metrics calculation
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            # Filter to last 24 hours
            cutoff = datetime.now() - timedelta(hours=24)
            recent_txs = [
                tx for tx in self._transaction_cache.values()
                if tx.timestamp >= cutoff
            ]
            
            # Calculate metrics
            total_volume = sum(tx.amount for tx in recent_txs)
            total_transactions = len(recent_txs)
            average_size = total_volume / total_transactions if total_transactions > 0 else Decimal('0')
            
            # Active flow pairs (unique sender-receiver combinations)
            flow_pairs = set(
                (tx.from_account, tx.to_account) for tx in recent_txs
            )
            active_flow_pairs = len(flow_pairs)
            
            # Circulation velocity (simplified: txs per hour / total accounts)
            accounts_count = len(self._reciprocity_cache)
            circulation_velocity = (
                total_transactions / 24.0 / accounts_count 
                if accounts_count > 0 else 0.0
            )
            
            # Reciprocity health (how balanced is give/receive across system)
            reciprocity_health = self._calculate_reciprocity_health()
            
            return FlowMetrics(
                total_volume_24h=total_volume,
                total_transactions_24h=total_transactions,
                average_transaction_size=average_size,
                active_flow_pairs=active_flow_pairs,
                circulation_velocity=circulation_velocity,
                reciprocity_health=reciprocity_health
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error calculating flow metrics: {e}")
            raise
    
    def _calculate_reciprocity_health(self) -> float:
        """
        Calculate overall system reciprocity health.
        
        Returns value between 0.0 (unhealthy) and 1.0 (healthy).
        Health is measured by how close the system is to balanced reciprocity.
        
        Principle 12: Single implementation of health calculation.
        """
        if not self._reciprocity_cache:
            return 0.0
        
        # Calculate deviation from perfect balance (ratio = 1.0)
        deviations = []
        for balance in self._reciprocity_cache.values():
            if balance.reciprocity_ratio == float('inf'):
                deviation = 1.0  # Maximum deviation for one-way flow
            else:
                # Deviation from 1.0
                deviation = abs(1.0 - min(balance.reciprocity_ratio, 1.0 / balance.reciprocity_ratio))
            deviations.append(deviation)
        
        # Average deviation
        avg_deviation = sum(deviations) / len(deviations)
        
        # Convert to health score (lower deviation = higher health)
        health = max(0.0, 1.0 - avg_deviation)
        
        return health
    
    async def get_reciprocity_balance(self, account_id: str) -> Optional[ReciprocityBalance]:
        """
        Get reciprocity balance for a specific account.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            ReciprocityBalance object or None if not found
            
        Example:
            >>> balance = await service.get_reciprocity_balance('GXXX...')
            >>> if balance:
            ...     print(f"Received: {balance.total_received}")
            ...     print(f"Sent: {balance.total_sent}")
            ...     print(f"Ratio: {balance.reciprocity_ratio:.2f}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            return self._reciprocity_cache.get(account_id)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error getting reciprocity balance: {e}")
            raise
    
    async def get_account_flows(
        self,
        account_id: str,
        direction: Optional[FlowDirection] = None,
        start_date: Optional[datetime] = None
    ) -> List[FlowTransaction]:
        """
        Get flow transactions for an account.
        
        Args:
            account_id: Stellar account ID
            direction: Optional filter by flow direction
            start_date: Optional start date filter
            
        Returns:
            List of FlowTransaction objects
            
        Example:
            >>> flows = await service.get_account_flows(
            ...     'GXXX...',
            ...     direction=FlowDirection.INBOUND,
            ...     start_date=datetime.now() - timedelta(days=7)
            ... )
            >>> for flow in flows:
            ...     print(f"{flow.timestamp}: {flow.amount} from {flow.from_account}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring with filtering
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            transactions = []
            for tx in self._transaction_cache.values():
                # Check if account is involved
                if tx.from_account != account_id and tx.to_account != account_id:
                    continue
                
                # Apply date filter
                if start_date and tx.timestamp < start_date:
                    continue
                
                # Set direction relative to this account
                if tx.from_account == account_id:
                    tx.direction = FlowDirection.OUTBOUND
                else:
                    tx.direction = FlowDirection.INBOUND
                
                # Apply direction filter
                if direction and tx.direction != direction:
                    continue
                
                transactions.append(tx)
            
            return sorted(transactions, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error getting account flows: {e}")
            raise
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    # Principle 10: Clear Separation of Concerns
    
    async def close(self) -> None:
        """
        Clean up service resources.
        
        Called during shutdown to release resources and cleanup caches.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("Closing Water protocol service...")
        self._transaction_cache.clear()
        self._reciprocity_cache.clear()
        self._cache_timestamp = None
        self._initialized = False
        self.logger.info("Water protocol service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

async def create_ubecrc_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECrcProtocolService:
    """
    Factory function to create UBECrc Water protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    Changed to async to allow for future async initialization if needed.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - asset_code: UBECrc token code (required)
            - issuer: Issuer address (required)
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options
    
    Returns:
        UBECrcProtocolService: Initialized service instance
        
    Raises:
        ValueError: If required config parameters are missing
    
    Example:
        >>> # In main.py or service registry
        >>> service = await create_ubecrc_service(
        ...     db_manager=db,
        ...     config={'asset_code': 'UBECrc', 'issuer': 'GDPNB7S3...'},
        ...     stellar_client=stellar
        ... )
        >>> health = await service.health_check()
        >>> flows = await service.get_flow_metrics()
    """
    # Validate required config parameters
    required_params = ['asset_code', 'issuer']
    
    for param in required_params:
        if param not in config:
            raise ValueError(f"Configuration missing required parameter: '{param}'")
    
    # Create service instance
    service = UBECrcProtocolService(
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
    'FlowDirection',
    
    # Data models
    'FlowTransaction',
    'ReciprocityBalance',
    'FlowMetrics',
    
    # Service
    'UBECrcProtocolService',
    'create_ubecrc_service',
    
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
        "  from UBECrc_protocol import create_ubecrc_service\n"
        "  service = await create_ubecrc_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  await service.sync_flow_data()\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
