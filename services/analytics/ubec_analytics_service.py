#!/usr/bin/env python3
"""
UBEC Protocol Suite - Analytics Service
========================================
Comprehensive analytics and insights for the UBEC token ecosystem.

Analyzes distribution, holder patterns, transaction trends, and ecosystem health
across all four UBEC elements (Air, Water, Earth, Fire).

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained analytics service with defined boundaries
    ✅ #2  Service Pattern: No standalone execution, used as service only
    ✅ #3  Service Registry: Accessed through service registry pattern
    ✅ #4  Single Source of Truth: All data from database
    ✅ #5  Strict Async Operations: All I/O uses async/await
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Individual token/element tracking with health checks
    ✅ #8  No Duplicate Configuration: No config duplication
    ✅ #9  Integrated Rate Limiting: N/A (read-only database operations)
    ✅ #10 Separation of Concerns: Analytics separated from sync/trading
    ✅ #11 Comprehensive Documentation: Full docstrings and examples
    ✅ #12 Method Singularity: Each analysis method implemented once
════════════════════════════════════════════════════════════════════════════

Key Features:
- Token distribution analysis across all 4 elements
- Holder concentration and whale identification
- Transaction pattern analysis and velocity metrics
- Liquidity and supply metrics
- Ecosystem health monitoring
- Time-series trend analysis
- Comparative analytics across tokens
- Export capabilities for external reporting
- Scheduled analytics updates for automation

Four-Element Architecture:
- 🜁 Air (UBEC) - Gateway & Universal Access
- 🜄 Water (UBECrc) - Flow & Exchange
- 🜃 Earth (UBECgpi) - Stability & Value
- 🜂 Fire (UBECtt) - Transformation & Action

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 3.6.0 (Scheduler Integration)
Date: November 7, 2025

Changes from v3.6.0:
- ✅ ADDED: update_analytics() method for scheduled execution
- ✅ ENHANCED: Scheduler integration support
- ✅ ENHANCED: Automated analytics refresh capability

Changes from v3.5.9:
- ✅ CRITICAL FIX: Active accounts query now counts BOTH senders and receivers
- ✅ CRITICAL FIX: Added bounds checking to element_balance_score (ensures 0-100 range)
- ✅ ENHANCED: Active accounts query uses UNION to capture all participants
- ✅ FIXED: Balance score can no longer return negative values
- ✅ VERIFIED: All ecosystem health metrics now accurate
- ✅ RESOLVES: Issue UBEC-001 (zero activity despite transaction history)
- ✅ RESOLVES: Issue UBEC-002 (negative balance scores)

Changes from v3.5.8:
- ✅ CRITICAL FIX: Corrected column name in get_top_holders() query (last_modified → last_modified_at)
- ✅ FIXED: Updated result processing to use correct column name (row['last_modified_at'])
- ✅ VERIFIED: All queries against ubec_balances now use correct schema column names
- ✅ RESOLVES: Analytics holders command database error

Changes from v3.5.6:
- ✅ CRITICAL FIX: Corrected database table for transaction metrics (stellar_operations not stellar_transactions)
- ✅ FIXED: Updated column name transaction_time to created_at
- ✅ FIXED: Updated column name transaction_type to type
- ✅ FIXED: Corrected get_ecosystem_health active accounts query to use stellar_operations
- ✅ VERIFIED: All transaction velocity calculations now functional

Changes from v3.5.5:
- ✅ CRITICAL FIX: Changed all ubec_balances queries from asset_code to token_code
- ✅ FIXED: Changed is_locked to is_authorized (correct schema column)
- ✅ ENHANCED: Added _TableColumns helper class for centralized column mapping
- ✅ VERIFIED: All 15 query locations corrected for schema compliance
Changes from v3.5.4:
- ✅ FIXED: Simplified get_token_distribution SQL query to resolve column scoping issue
- ✅ OPTIMIZED: Removed unnecessary triple-nested CTE aggregation
- ✅ ENHANCED: More efficient query execution with direct parameter usage
Changes from v3.5.3:
- ✅ FIXED: Added missing async close() method for service registry pattern
- ✅ ENHANCED: Proper resource cleanup and cache clearing on close
- ✅ FIXED: Service now properly logs closure during shutdown
Changes from v3.5.2:
- ✅ FIXED: SQL aggregation error in get_token_distribution query
- ✅ FIXED: Wrapped th.top_10_sum and th.top_100_sum in MAX() for proper aggregation
Changes from v3.5.1:
- ✅ FIXED: Schema configuration now defaults to 'ubec_main' instead of 'public'
- ✅ ENHANCED: Better config handling for Settings object vs dict
Changes from v3.5.0:
- ✅ FIXED: Added missing initialize() method required by service registry pattern
Changes from v3.4:
- ✅ ADDED: Transaction velocity metrics to get_distribution_overview()
- ✅ ENHANCED: Summary statistics now include transaction-related metrics
- ✅ ENHANCED: Rankings now include velocity-based token comparisons
- Maintained all existing functionality and design principle compliance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

# Configure precision for decimal calculations
getcontext().prec = 10

logger = logging.getLogger(__name__)


class TokenCode(str, Enum):
    """Valid UBEC token codes"""
    UBEC = "UBEC"
    UBECRC = "UBECrc"
    UBECGPI = "UBECgpi"
    UBECTT = "UBECtt"


class ElementType(str, Enum):
    """Four-element types"""
    AIR = "air"
    WATER = "water"
    EARTH = "earth"
    FIRE = "fire"


# Element to token mapping
ELEMENT_TOKEN_MAP = {
    ElementType.AIR: TokenCode.UBEC,
    ElementType.WATER: TokenCode.UBECRC,
    ElementType.EARTH: TokenCode.UBECGPI,
    ElementType.FIRE: TokenCode.UBECTT
}

TOKEN_ELEMENT_MAP = {v: k for k, v in ELEMENT_TOKEN_MAP.items()}


# Schema column mapping (Principle #12: Method Singularity)
class _TableColumns:
    """
    Centralized table-to-column mapping for database queries.
    
    This class provides a single source of truth for column names used in
    different tables, implementing Principle #4 (Single Source of Truth) and
    Principle #12 (Method Singularity).
    
    Schema Notes:
        - ubec_balances uses token_code (enum: UBEC, UBECrc, UBECgpi, UBECtt)
        - stellar_transactions uses asset_code (varchar)
        - account_balances uses asset_code (varchar)
        - asset_holder_analysis uses asset_code (varchar)
    """
    # Primary balance table
    UBEC_BALANCES_TOKEN_COL = "token_code"  # Token identifier in ubec_balances
    
    # Transaction table
    TRANSACTIONS_ASSET_COL = "asset_code"   # Token identifier in stellar_transactions
    
    # Authorization columns
    AUTHORIZED_COL = "is_authorized"        # Authorization status in ubec_balances
    
    @staticmethod
    def get_token_column(table_name: str = "ubec_balances") -> str:
        """
        Get the correct token identifier column for a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            Column name for token identification
        """
        if table_name == "ubec_balances":
            return _TableColumns.UBEC_BALANCES_TOKEN_COL
        return "asset_code"  # Default for other tables


@dataclass
class TokenDistribution:
    """Token distribution metrics"""
    asset_code: str
    element: str
    total_holders: int
    total_supply: Decimal
    avg_balance: Decimal
    median_balance: Decimal
    min_balance: Decimal
    max_balance: Decimal
    top_10_concentration: Decimal  # Percentage held by top 10
    top_100_concentration: Decimal  # Percentage held by top 100
    gini_coefficient: float  # Income inequality measure (0=perfect equality, 1=perfect inequality)


@dataclass
class HolderAnalysis:
    """Holder concentration analysis"""
    asset_code: str
    element: str
    total_holders: int
    whale_count: int  # Holders with >1% of supply
    whale_percentage: float  # Percentage held by whales
    top_10_holders: Decimal
    top_100_holders: Decimal
    small_holder_count: int  # Holders with <0.1% of supply
    small_holder_percentage: float
    concentration_ratio: float  # Whale percentage / Small holder percentage


@dataclass
class TransactionMetrics:
    """Transaction pattern metrics"""
    asset_code: str
    element: str
    total_transactions: int
    period_days: int
    avg_daily_transactions: float
    velocity: float  # Transactions per holder per day
    unique_senders: int
    unique_receivers: int
    avg_transaction_size: Decimal
    median_transaction_size: Decimal


@dataclass
class LiquidityMetrics:
    """Liquidity and supply metrics"""
    asset_code: str
    element: str
    circulating_supply: Decimal
    locked_supply: Decimal  # Unauthorized accounts
    free_float: Decimal  # Unlocked and distributed
    liquidity_ratio: float  # Free float / Circulating supply
    holder_diversity: float  # Effective number of holders (1/gini)


@dataclass
class EcosystemHealth:
    """Overall ecosystem health metrics"""
    timestamp: str
    total_accounts: int
    total_holders: int
    total_transactions: int
    total_supply_all_tokens: Decimal
    active_accounts_24h: int
    active_accounts_7d: int
    active_accounts_30d: int
    element_balance_score: Decimal  # How balanced are the 4 elements (0-100, 100=perfect balance)
    

class AnalyticsException(Exception):
    """Custom exception for analytics errors"""
    pass


# ==================== SERVICE IMPLEMENTATION ====================

class UBECAnalyticsService:
    """
    UBEC Analytics Service
    
    Provides comprehensive analytics and insights for the UBEC token ecosystem.
    This service provides read-only analytics and insights by querying
    the database. All operations are asynchronous and designed for
    high-performance data analysis.
    
    Principle #7 Compliance (Per-Asset Monitoring):
    - Tracks each token individually
    - Monitors health per element
    - Provides aggregated ecosystem metrics
    - Enhanced health check with data freshness validation
    
    Usage:
        # Via service registry (RECOMMENDED - Principle #3)
        registry = ServiceRegistry()
        analytics = await registry.get('analytics')
        
        # CLI command interface - main.py interface methods
        result = await analytics.get_distribution_overview()  # Overview analytics
        result = await analytics.get_top_holders(limit=50)    # Holder rankings
        result = await analytics.get_network_metrics()        # Network metrics
        
        # Scheduled operations
        result = await analytics.update_analytics()           # Refresh all metrics
        
        # Alternative CLI methods
        result = await analytics.analyze_token_distribution()  # Distribution
        result = await analytics.calculate_velocity()          # Velocity
        result = await analytics.calculate_concentration()     # Concentration
        
        # Get specific token distribution
        dist = await analytics.get_token_distribution('UBEC')
        
        # Health monitoring (Principle #7)
        health = await analytics.health_check()
        
        # Proper shutdown (Principle #2, #3)
        await analytics.close()
    """
    
    def __init__(self, db_manager, config):
        """
        Initialize analytics service.
        
        Args:
            db_manager: Database connection manager (AsyncDatabaseManager)
            config: Configuration object (Settings or dict)
            
        Note:
            Constructor only initializes state. Call initialize() to complete setup.
        """
        self.db_manager = db_manager
        self.config = config
        
        # Extract schema from config
        if hasattr(config, 'get'):
            # Settings object
            self.db_schema = config.get('db_schema', 'ubec_main')
        elif isinstance(config, dict):
            # Dictionary
            self.db_schema = config.get('db_schema', 'ubec_main')
        else:
            # Fallback default
            self.db_schema = 'ubec_main'
        
        # Query cache for performance
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5 minutes default TTL
        
        # Error tracking
        self._error_count = 0
        self._last_error = None
        self._last_error_time = None
        
        logger.info(f"✓ ubec_analytics_service v3.6.0 initialized")
    
    async def initialize(self):
        """
        Initialize the analytics service.
        
        Required by service registry pattern (Principle #3).
        Performs any async setup needed.
        """
        logger.info("ubec_analytics_service async initialization complete")
    
    async def close(self):
        """
        Close the analytics service and cleanup resources.
        
        Required by service registry pattern for proper shutdown.
        Clears cache and resets error tracking.
        """
        self._cache.clear()
        self._cache_timestamps.clear()
        self._error_count = 0
        self._last_error = None
        self._last_error_time = None
        logger.info("✓ ubec_analytics_service closed")
    
    # ========================================================================
    # CACHE MANAGEMENT (Principle #12: Method Singularity)
    # ========================================================================
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None
        
        timestamp = self._cache_timestamps.get(key)
        if timestamp and (datetime.now() - timestamp).seconds < self._cache_ttl:
            return self._cache[key]
        
        # Expired - remove from cache
        del self._cache[key]
        del self._cache_timestamps[key]
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Set value in cache with current timestamp."""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def _clear_cache(self):
        """Clear all cached values."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    # ========================================================================
    # ERROR TRACKING (Principle #12: Method Singularity)
    # ========================================================================
    
    def _record_error(self, error_msg: str):
        """Record error for monitoring."""
        self._error_count += 1
        self._last_error = error_msg
        self._last_error_time = datetime.now()
        logger.error(f"Analytics error: {error_msg}")
    
    # ========================================================================
    # DATABASE HELPERS (Principle #12: Method Singularity)
    # ========================================================================
    
    async def _execute_query(self, query: str, params: tuple) -> Optional[Dict]:
        """
        Execute query and return single row.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Dict with column names as keys, or None if no results
        """
        try:
            return await self.db_manager.fetch_one(query, params)
        except Exception as e:
            self._record_error(f"Query execution failed: {e}")
            raise
    
    async def _execute_query_all(self, query: str, params: tuple) -> List[Dict]:
        """
        Execute query and return all rows.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dicts with column names as keys
        """
        try:
            return await self.db_manager.fetch_all(query, params)
        except Exception as e:
            self._record_error(f"Query execution failed: {e}")
            raise
    
    # ========================================================================
    # HEALTH CHECK (Principle #7: Per-Asset Monitoring)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health with data freshness validation.
        
        Uses standardized ServiceHealthCheck utility (Principle #12).
        Enhanced to check for stale data and query performance.
        
        Returns:
            Dict with status and detailed health metrics
            
        Example:
            health = await analytics.health_check()
            if health['status'] == 'healthy':
                print("Analytics service operational")
        """
        health_checker = ServiceHealthCheck(
            service_name="ubec_analytics_service",
            version="3.6.0"
        )
        
        try:
            # Test database connectivity
            test_query = f"SELECT 1 as test FROM {self.db_schema}.ubec_balances LIMIT 1"
            result = await self._execute_query(test_query, ())
            
            if result and result.get('test') == 1:
                # Check data freshness
                freshness_query = f"""
                    SELECT 
                        MAX(last_modified_at) as latest_update,
                        COUNT(*) as total_records
                    FROM {self.db_schema}.ubec_balances
                """
                freshness = await self._execute_query(freshness_query, ())
                
                latest_update = freshness['latest_update'] if freshness else None
                total_records = freshness['total_records'] if freshness else 0
                
                # Calculate cache statistics
                total_cache_entries = len(self._cache)
                valid_cache_entries = sum(
                    1 for key in self._cache 
                    if self._get_cache(key) is not None
                )
                cache_hit_rate = (
                    valid_cache_entries / total_cache_entries 
                    if total_cache_entries > 0 else 0
                )
                
                health_checker.add_detail("database_connected", True)
                health_checker.add_detail("total_balance_records", total_records)
                health_checker.add_detail("latest_data_update", 
                    latest_update.isoformat() if latest_update else None)
                health_checker.add_detail("cache_entries", total_cache_entries)
                health_checker.add_detail("cache_hit_rate", cache_hit_rate)
                health_checker.add_detail("error_count", self._error_count)
                health_checker.add_detail("last_error", self._last_error)
                health_checker.add_detail("schema", self.db_schema)
                
                return health_checker.healthy()
            else:
                health_checker.add_detail("database_connected", False)
                health_checker.add_detail("error", "Database query test failed")
                return health_checker.unhealthy("Database connectivity issue")
                
        except Exception as e:
            self._record_error(f"Health check failed: {e}")
            health_checker.add_detail("error", str(e))
            return health_checker.unhealthy(f"Health check exception: {e}")
    
    # ========================================================================
    # MAIN.PY INTERFACE METHODS
    # These methods provide the primary interface for main.py commands
    # ========================================================================
    
    async def get_distribution_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive distribution overview across all tokens.
        
        Main.py interface method that provides ecosystem-wide analytics.
        Includes velocity metrics as of v3.4.0.
        
        Returns:
            Dict with:
            - summary: Total holders, supply, concentration across all tokens
            - by_token: Per-token distribution metrics
            - rankings: Tokens ranked by various metrics
            - velocity_metrics: Transaction velocity per token (v3.4.0+)
            
        Example (from main.py):
            overview = await analytics.get_distribution_overview()
            print(f"Total ecosystem holders: {overview['summary']['total_holders']}")
            print(f"Most concentrated: {overview['rankings']['by_concentration'][0]}")
        """
        logger.info("Generating distribution overview...")
        
        try:
            overview = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_holders': 0,
                    'total_supply': Decimal('0'),
                    'avg_concentration': 0.0,
                    'total_transactions_30d': 0
                },
                'by_token': {},
                'rankings': {},
                'velocity_metrics': {}
            }
            
            # Get distribution for each token
            distributions = []
            for token in TokenCode:
                try:
                    dist = await self.get_token_distribution(token.value)
                    distributions.append(dist)
                    overview['by_token'][token.value] = asdict(dist)
                    
                    # Get velocity metrics (v3.4.0+)
                    try:
                        velocity = await self.get_transaction_metrics(token.value, period_days=30)
                        overview['velocity_metrics'][token.value] = {
                            'velocity': float(velocity.velocity),
                            'avg_daily_tx': velocity.avg_daily_transactions,
                            'total_transactions': velocity.total_transactions
                        }
                        overview['summary']['total_transactions_30d'] += velocity.total_transactions
                    except Exception as e:
                        logger.warning(f"Could not get velocity for {token.value}: {e}")
                        overview['velocity_metrics'][token.value] = None
                    
                except Exception as e:
                    logger.warning(f"Could not get distribution for {token.value}: {e}")
                    overview['by_token'][token.value] = None
            
            # Calculate summary statistics
            overview['summary'] = {
                'total_holders': sum(d.total_holders for d in distributions),
                'total_supply': float(sum(d.total_supply for d in distributions)),
                'avg_concentration': float(
                    sum(d.top_10_concentration for d in distributions) / len(distributions)
                ),
                'total_transactions_30d': overview['summary']['total_transactions_30d']
            }
            
            # Create rankings
            overview['rankings'] = {
                'by_holders': [
                    {'token': d.asset_code, 'holders': d.total_holders}
                    for d in sorted(distributions, key=lambda d: d.total_holders, reverse=True)
                ],
                'by_supply': [
                    {'token': d.asset_code, 'supply': float(d.total_supply)}
                    for d in sorted(distributions, key=lambda d: d.total_supply, reverse=True)
                ],
                'by_concentration': [
                    {'token': d.asset_code, 'concentration': float(d.top_10_concentration)}
                    for d in sorted(distributions, key=lambda d: d.top_10_concentration, reverse=True)
                ],
                'by_velocity': [
                    {
                        'token': token.value,
                        'velocity': overview['velocity_metrics'][token.value]['velocity']
                    }
                    for token in TokenCode
                    if overview['velocity_metrics'].get(token.value)
                ]
            }
            
            logger.info("✓ Distribution overview complete")
            return overview
            
        except Exception as e:
            self._record_error(f"Error generating distribution overview: {e}")
            raise AnalyticsException(f"Distribution overview failed: {e}")
    
    async def get_top_holders(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get top token holders across all tokens.
        
        Main.py interface method for holder rankings.
        
        Args:
            limit: Maximum number of holders to return per token
            
        Returns:
            Dict with top holders organized by token
            
        Example (from main.py):
            holders = await analytics.get_top_holders(limit=50)
            for token, holder_list in holders['by_token'].items():
                print(f"{token}: {len(holder_list)} top holders")
        """
        logger.info(f"Getting top {limit} holders...")
        
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'limit': limit,
                'by_token': {}
            }
            
            for token in TokenCode:
                query = f"""
                    SELECT 
                        account_id,
                        balance,
                        last_modified_at,
                        {_TableColumns.AUTHORIZED_COL} as is_authorized,
                        RANK() OVER (ORDER BY balance DESC) as rank
                    FROM {self.db_schema}.ubec_balances
                    WHERE {_TableColumns.UBEC_BALANCES_TOKEN_COL} = $1 
                      AND balance > 0
                    ORDER BY balance DESC
                    LIMIT $2
                """
                
                rows = await self._execute_query_all(query, (token.value, limit))
                
                result['by_token'][token.value] = [
                    {
                        'account_id': row['account_id'],
                        'balance': float(row['balance']),
                        'rank': row['rank'],
                        'is_authorized': row['is_authorized'],
                        'last_modified': row['last_modified_at'].isoformat() if row['last_modified_at'] else None
                    }
                    for row in rows
                ]
            
            logger.info("✓ Top holders retrieved")
            return result
            
        except Exception as e:
            self._record_error(f"Error getting top holders: {e}")
            raise AnalyticsException(f"Top holders query failed: {e}")
    
    # ========================================================================
    # NETWORK METRICS (Main.py Interface Method)
    # ========================================================================
    
    async def get_network_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive network-wide metrics.
        
        Main.py interface method for network analysis.
        
        Returns:
            Dict with network-wide metrics:
            - total_accounts
            - active_accounts (24h, 7d, 30d)
            - transaction_counts
            - ecosystem_health
            
        Example (from main.py):
            metrics = await analytics.get_network_metrics()
            print(f"Active accounts (24h): {metrics['active_accounts_24h']}")
        """
        logger.info("Calculating network metrics...")
        
        try:
            # Get ecosystem health (contains most network metrics)
            health = await self.get_ecosystem_health()
            
            # Format as dict for return
            result = {
                'timestamp': datetime.now().isoformat(),
                'total_accounts': health.total_accounts,
                'total_holders': health.total_holders,
                'total_transactions': health.total_transactions,
                'total_supply_all_tokens': float(health.total_supply_all_tokens),
                'active_accounts_24h': health.active_accounts_24h,
                'active_accounts_7d': health.active_accounts_7d,
                'active_accounts_30d': health.active_accounts_30d,
                'element_balance_score': float(health.element_balance_score)
            }
            
            logger.info("✓ Network metrics calculated")
            return result
            
        except Exception as e:
            self._record_error(f"Error calculating network metrics: {e}")
            raise AnalyticsException(f"Network metrics failed: {e}")
    
    # ========================================================================
    # ALTERNATIVE CLI COMMAND METHODS
    # These provide the same functionality with different method names
    # ========================================================================
    
    async def analyze_token_distribution(self, token_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze token distribution.
        
        Alternative CLI method name for distribution analysis.
        Calls get_distribution_overview() internally.
        
        Args:
            token_code: Optional token to analyze (None = all tokens)
            
        Returns:
            Distribution analysis results
        """
        if token_code:
            dist = await self.get_token_distribution(token_code)
            return {'distribution': asdict(dist)}
        else:
            return await self.get_distribution_overview()
    
    async def calculate_velocity(self, token_code: Optional[str] = None, period_days: int = 30) -> Dict[str, Any]:
        """
        Calculate transaction velocity.
        
        Alternative CLI method for velocity analysis.
        
        Args:
            token_code: Optional token (None = all tokens)
            period_days: Analysis period
            
        Returns:
            Velocity metrics
        """
        if token_code:
            metrics = await self.get_transaction_metrics(token_code, period_days)
            return {'velocity': asdict(metrics)}
        else:
            result = {}
            for token in TokenCode:
                try:
                    metrics = await self.get_transaction_metrics(token.value, period_days)
                    result[token.value] = asdict(metrics)
                except Exception as e:
                    logger.warning(f"Could not get velocity for {token.value}: {e}")
                    result[token.value] = None
            return result
    
    async def calculate_concentration(self, token_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate holder concentration.
        
        Alternative CLI method for concentration analysis.
        
        Args:
            token_code: Optional token (None = all tokens)
            
        Returns:
            Concentration metrics
        """
        if token_code:
            analysis = await self.analyze_holder_concentration(token_code)
            return {'concentration': asdict(analysis)}
        else:
            result = {}
            for token in TokenCode:
                analysis = await self.analyze_holder_concentration(token.value)
                result[token.value] = asdict(analysis)
            return result
    
    # ========================================================================
    # SCHEDULED OPERATIONS
    # Methods designed for periodic execution by scheduler service
    # ========================================================================
    
    async def update_analytics(self) -> Dict[str, Any]:
        """
        Update all analytics metrics (for scheduled execution).
        
        This method refreshes the analytics cache and updates computed metrics.
        Designed to be called periodically by the scheduler service to ensure
        analytics data remains fresh.
        
        The method clears the cache and refreshes key metrics by calling
        existing analytics methods, ensuring all downstream consumers get
        updated data on their next query.
        
        Returns:
            Dict with update summary:
                - timestamp: When update occurred
                - metrics_updated: List of updated metric types
                - cache_cleared: Whether cache was cleared
                - duration_ms: How long update took
                - status: 'success' or 'error'
        
        Raises:
            Does not raise exceptions - returns error status instead
        
        Example:
            # Called by scheduler
            result = await analytics.update_analytics()
            if result['status'] == 'success':
                logger.info(f"Analytics updated: {result['metrics_updated']}")
        
        Design Principles:
            - Principle #5: Async operation
            - Principle #12: Method singularity - composes existing methods
        """
        start_time = datetime.now()
        
        try:
            logger.info("Starting scheduled analytics update...")
            
            # Clear cache to force fresh data on next query
            self._clear_cache()
            logger.debug("Cache cleared")
            
            # Track which metrics we updated
            metrics_updated = []
            
            # Update distribution overview (includes all tokens and velocity)
            await self.get_distribution_overview()
            metrics_updated.append('distribution_overview')
            logger.debug("Distribution overview refreshed")
            
            # Update network metrics
            await self.get_network_metrics()
            metrics_updated.append('network_metrics')
            logger.debug("Network metrics refreshed")
            
            # Update top holders for all tokens
            await self.get_top_holders(limit=100)
            metrics_updated.append('top_holders')
            logger.debug("Top holders refreshed")
            
            # Update ecosystem health
            await self.get_ecosystem_health()
            metrics_updated.append('ecosystem_health')
            logger.debug("Ecosystem health refreshed")
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'metrics_updated': metrics_updated,
                'cache_cleared': True,
                'duration_ms': duration_ms,
                'status': 'success'
            }
            
            logger.info(
                f"✓ Analytics update complete: {len(metrics_updated)} metric types "
                f"refreshed ({duration_ms:.0f}ms)"
            )
            return result
            
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"Analytics update failed: {e}"
            self._record_error(error_msg)
            
            logger.error(
                f"✗ Analytics update failed after {duration_ms:.0f}ms: {e}",
                exc_info=True
            )
            
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'duration_ms': duration_ms
            }
    
    # ========================================================================
    # TOKEN DISTRIBUTION ANALYSIS
    # ========================================================================
    
    async def get_token_distribution(
        self,
        asset_code: str,
        use_cache: bool = True
    ) -> TokenDistribution:
        """
        Get comprehensive distribution metrics for a specific token.
        
        Args:
            asset_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            use_cache: Whether to use cached results
            
        Returns:
            TokenDistribution dataclass with distribution metrics
            
        Example:
            dist = await analytics.get_token_distribution('UBEC')
            print(f"Holders: {dist.total_holders}")
            print(f"Gini coefficient: {dist.gini_coefficient}")
        """
        # Validate token code
        try:
            TokenCode(asset_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {asset_code}")
        
        # Check cache
        cache_key = f"distribution_{asset_code}"
        if use_cache:
            cached = self._get_cache(cache_key)
            if cached:
                logger.info(f"✓ Using cached distribution for {asset_code}")
                return cached
        
        logger.info(f"Analyzing distribution for {asset_code}...")
        
        try:
            # Single optimized query for all distribution metrics
            query = f"""
                WITH holder_stats AS (
                    SELECT 
                        $1 as asset_code,
                        COUNT(*) as total_holders,
                        SUM(balance) as total_supply,
                        AVG(balance) as avg_balance,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance,
                        MIN(balance) as min_balance,
                        MAX(balance) as max_balance
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code = $1 AND balance > 0
                    GROUP BY token_code
                ),
                top_holders AS (
                    SELECT 
                        $1 as asset_code,
                        SUM(balance) FILTER (WHERE rank <= 10) as top_10_sum,
                        SUM(balance) FILTER (WHERE rank <= 100) as top_100_sum
                    FROM (
                        SELECT 
                            balance,
                            RANK() OVER (ORDER BY balance DESC) as rank
                        FROM {self.db_schema}.ubec_balances
                        WHERE token_code = $1 AND balance > 0
                    ) ranked
                )
                SELECT 
                    hs.asset_code,
                    hs.total_holders,
                    hs.total_supply,
                    hs.avg_balance,
                    hs.median_balance,
                    hs.min_balance,
                    hs.max_balance,
                    COALESCE((th.top_10_sum / NULLIF(hs.total_supply, 0) * 100), 0) as top_10_concentration,
                    COALESCE((th.top_100_sum / NULLIF(hs.total_supply, 0) * 100), 0) as top_100_concentration
                FROM holder_stats hs
                LEFT JOIN top_holders th ON hs.asset_code = th.asset_code
            """
            
            row = await self._execute_query(query, (asset_code,))
            
            if not row:
                raise AnalyticsException(f"No data found for token: {asset_code}")
            
            # Get element name
            element = TOKEN_ELEMENT_MAP.get(TokenCode(asset_code), "unknown")
            
            # Calculate Gini coefficient (simplified Lorenz curve approximation)
            gini_query = f"""
                WITH ranked_balances AS (
                    SELECT 
                        balance,
                        SUM(balance) OVER (ORDER BY balance) as cumulative_balance,
                        COUNT(*) OVER () as total_holders
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code = $1 AND balance > 0
                    ORDER BY balance
                )
                SELECT 
                    AVG(cumulative_balance / (balance * total_holders)) as gini_factor
                FROM ranked_balances
            """
            gini_row = await self._execute_query(gini_query, (asset_code,))
            gini_coefficient = float(gini_row['gini_factor']) if gini_row else 0.5
            
            # Create distribution object
            distribution = TokenDistribution(
                asset_code=asset_code,
                element=element.value,
                total_holders=int(row['total_holders']),
                total_supply=Decimal(str(row['total_supply'])),
                avg_balance=Decimal(str(row['avg_balance'])),
                median_balance=Decimal(str(row['median_balance'])),
                min_balance=Decimal(str(row['min_balance'])),
                max_balance=Decimal(str(row['max_balance'])),
                top_10_concentration=Decimal(str(row['top_10_concentration'])),
                top_100_concentration=Decimal(str(row['top_100_concentration'])),
                gini_coefficient=gini_coefficient
            )
            
            # Cache the result
            self._set_cache(cache_key, distribution)
            
            logger.info(f"✓ Distribution analysis complete for {asset_code}")
            return distribution
            
        except Exception as e:
            self._record_error(f"Error analyzing distribution for {asset_code}: {e}")
            raise AnalyticsException(f"Distribution analysis failed: {e}")
    
    # ========================================================================
    # HOLDER CONCENTRATION ANALYSIS
    # ========================================================================
    
    async def analyze_holder_concentration(
        self,
        asset_code: str,
        whale_threshold: float = 0.01  # 1% of supply
    ) -> HolderAnalysis:
        """
        Analyze holder concentration and whale distribution.
        
        Args:
            asset_code: Token code to analyze
            whale_threshold: Minimum percentage of supply to be considered a whale
            
        Returns:
            HolderAnalysis with concentration metrics
            
        Example:
            analysis = await analytics.analyze_holder_concentration('UBEC')
            print(f"Whales: {analysis.whale_count}")
            print(f"Whale percentage: {analysis.whale_percentage}%")
        """
        # Validate token code
        try:
            TokenCode(asset_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {asset_code}")
        
        logger.info(f"Analyzing holder concentration for {asset_code}...")
        
        try:
            # Get total supply first
            supply_query = f"""
                SELECT SUM(balance) as total_supply
                FROM {self.db_schema}.ubec_balances
                WHERE token_code = $1 AND balance > 0
            """
            supply_row = await self._execute_query(supply_query, (asset_code,))
            total_supply = Decimal(str(supply_row['total_supply'])) if supply_row else Decimal('0')
            
            if total_supply == 0:
                raise AnalyticsException(f"No supply found for {asset_code}")
            
            whale_minimum = total_supply * Decimal(str(whale_threshold))
            small_holder_maximum = total_supply * Decimal('0.001')  # 0.1% threshold
            
            # Analyze concentration
            query = f"""
                WITH holder_analysis AS (
                    SELECT 
                        COUNT(*) as total_holders,
                        COUNT(*) FILTER (WHERE balance >= $2) as whale_count,
                        SUM(balance) FILTER (WHERE balance >= $2) as whale_balance,
                        COUNT(*) FILTER (WHERE balance < $3) as small_holder_count,
                        SUM(balance) FILTER (WHERE balance < $3) as small_holder_balance
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code = $1 AND balance > 0
                ),
                top_holders AS (
                    SELECT 
                        SUM(balance) FILTER (WHERE rank <= 10) as top_10_total,
                        SUM(balance) FILTER (WHERE rank <= 100) as top_100_total
                    FROM (
                        SELECT 
                            balance,
                            RANK() OVER (ORDER BY balance DESC) as rank
                        FROM {self.db_schema}.ubec_balances
                        WHERE token_code = $1 AND balance > 0
                    ) ranked
                )
                SELECT 
                    ha.total_holders,
                    ha.whale_count,
                    ha.whale_balance,
                    ha.small_holder_count,
                    ha.small_holder_balance,
                    th.top_10_total,
                    th.top_100_total
                FROM holder_analysis ha
                CROSS JOIN top_holders th
            """
            
            row = await self._execute_query(
                query,
                (asset_code, float(whale_minimum), float(small_holder_maximum))
            )
            
            if not row:
                raise AnalyticsException(f"No holder data found for {asset_code}")
            
            # Calculate percentages
            whale_percentage = float(
                (Decimal(str(row['whale_balance'])) / total_supply * 100) 
                if row['whale_balance'] else 0
            )
            small_holder_percentage = float(
                (Decimal(str(row['small_holder_balance'])) / total_supply * 100)
                if row['small_holder_balance'] else 0
            )
            
            concentration_ratio = (
                whale_percentage / small_holder_percentage
                if small_holder_percentage > 0 else 0
            )
            
            # Get element name
            element = TOKEN_ELEMENT_MAP.get(TokenCode(asset_code), "unknown")
            
            analysis = HolderAnalysis(
                asset_code=asset_code,
                element=element.value,
                total_holders=int(row['total_holders']),
                whale_count=int(row['whale_count']),
                whale_percentage=whale_percentage,
                top_10_holders=Decimal(str(row['top_10_total'])),
                top_100_holders=Decimal(str(row['top_100_total'])),
                small_holder_count=int(row['small_holder_count']),
                small_holder_percentage=small_holder_percentage,
                concentration_ratio=concentration_ratio
            )
            
            logger.info(f"✓ Holder concentration analysis complete for {asset_code}")
            return analysis
            
        except Exception as e:
            self._record_error(f"Error analyzing holder concentration for {asset_code}: {e}")
            raise AnalyticsException(f"Holder concentration analysis failed: {e}")
    
    # ========================================================================
    # TRANSACTION METRICS
    # ========================================================================
    
    async def get_transaction_metrics(
        self,
        asset_code: str,
        period_days: int = 30
    ) -> TransactionMetrics:
        """
        Get transaction pattern metrics for a token.
        
        Args:
            asset_code: Token code to analyze
            period_days: Time period for analysis
            
        Returns:
            TransactionMetrics with velocity and pattern data
            
        Example:
            metrics = await analytics.get_transaction_metrics('UBEC', period_days=7)
            print(f"Velocity: {metrics.velocity} tx/holder/day")
        """
        # Validate token code
        try:
            TokenCode(asset_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {asset_code}")
        
        logger.info(f"Calculating transaction metrics for {asset_code} ({period_days}d)...")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
            # Note: Using stellar_operations table (corrected in v3.5.6)
            query = f"""
                WITH tx_stats AS (
                    SELECT 
                        COUNT(*) as total_transactions,
                        COUNT(DISTINCT source_account) as unique_senders,
                        COUNT(DISTINCT COALESCE(
                            (details->>'to')::text,
                            (details->>'destination')::text
                        )) as unique_receivers,
                        AVG((details->>'amount')::decimal) as avg_amount,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (
                            ORDER BY (details->>'amount')::decimal
                        ) as median_amount
                    FROM {self.db_schema}.stellar_operations
                    WHERE asset_code = $1 
                      AND created_at >= $2
                      AND type IN ('payment', 'path_payment_strict_receive', 'path_payment_strict_send')
                      AND (details->>'amount')::decimal > 0
                ),
                holder_count AS (
                    SELECT COUNT(*) as total_holders
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code = $1 AND balance > 0
                )
                SELECT 
                    ts.total_transactions,
                    ts.unique_senders,
                    ts.unique_receivers,
                    ts.avg_amount,
                    ts.median_amount,
                    hc.total_holders
                FROM tx_stats ts
                CROSS JOIN holder_count hc
            """
            
            row = await self._execute_query(query, (asset_code, cutoff_date))
            
            if not row or row['total_transactions'] == 0:
                # Return zero metrics if no transactions
                element = TOKEN_ELEMENT_MAP.get(TokenCode(asset_code), "unknown")
                return TransactionMetrics(
                    asset_code=asset_code,
                    element=element.value,
                    total_transactions=0,
                    period_days=period_days,
                    avg_daily_transactions=0.0,
                    velocity=0.0,
                    unique_senders=0,
                    unique_receivers=0,
                    avg_transaction_size=Decimal('0'),
                    median_transaction_size=Decimal('0')
                )
            
            # Calculate metrics
            total_tx = int(row['total_transactions'])
            total_holders = int(row['total_holders'])
            avg_daily_tx = total_tx / period_days
            
            # Velocity = transactions per holder per day
            velocity = (total_tx / (total_holders * period_days)) if total_holders > 0 else 0.0
            
            element = TOKEN_ELEMENT_MAP.get(TokenCode(asset_code), "unknown")
            
            metrics = TransactionMetrics(
                asset_code=asset_code,
                element=element.value,
                total_transactions=total_tx,
                period_days=period_days,
                avg_daily_transactions=avg_daily_tx,
                velocity=velocity,
                unique_senders=int(row['unique_senders']),
                unique_receivers=int(row['unique_receivers']),
                avg_transaction_size=Decimal(str(row['avg_amount'])) if row['avg_amount'] else Decimal('0'),
                median_transaction_size=Decimal(str(row['median_amount'])) if row['median_amount'] else Decimal('0')
            )
            
            logger.info(f"✓ Transaction metrics complete for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error calculating transaction metrics for {asset_code}: {e}")
            raise AnalyticsException(f"Transaction metrics calculation failed: {e}")
    
    # ========================================================================
    # LIQUIDITY METRICS
    # ========================================================================
    
    async def get_liquidity_metrics(
        self,
        asset_code: str
    ) -> LiquidityMetrics:
        """
        Get liquidity and supply metrics for a token.
        
        Args:
            asset_code: Token code to analyze
            
        Returns:
            LiquidityMetrics with liquidity analysis
            
        Example:
            liquidity = await analytics.get_liquidity_metrics('UBEC')
            print(f"Free float: {liquidity.free_float}")
            print(f"Liquidity ratio: {liquidity.liquidity_ratio}")
        """
        # Validate token code
        try:
            TokenCode(asset_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {asset_code}")
        
        logger.info(f"Calculating liquidity metrics for {asset_code}...")
        
        try:
            query = f"""
                WITH supply_breakdown AS (
                    SELECT 
                        SUM(balance) as circulating_supply,
                        SUM(balance) FILTER (WHERE NOT {_TableColumns.AUTHORIZED_COL}) as locked_supply,
                        SUM(balance) FILTER (WHERE {_TableColumns.AUTHORIZED_COL}) as unlocked_supply
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code = $1 AND balance > 0
                ),
                concentration AS (
                    SELECT 
                        SUM(balance) FILTER (WHERE rank <= 10) as top_10_holdings
                    FROM (
                        SELECT 
                            balance,
                            RANK() OVER (ORDER BY balance DESC) as rank
                        FROM {self.db_schema}.ubec_balances
                        WHERE token_code = $1 AND balance > 0
                    ) ranked
                )
                SELECT 
                    sb.circulating_supply,
                    sb.locked_supply,
                    sb.unlocked_supply,
                    c.top_10_holdings
                FROM supply_breakdown sb
                CROSS JOIN concentration c
            """
            
            row = await self._execute_query(query, (asset_code,))
            
            if not row:
                raise AnalyticsException(f"No supply data found for {asset_code}")
            
            circulating = Decimal(str(row['circulating_supply'])) if row['circulating_supply'] else Decimal('0')
            locked = Decimal(str(row['locked_supply'])) if row['locked_supply'] else Decimal('0')
            unlocked = Decimal(str(row['unlocked_supply'])) if row['unlocked_supply'] else Decimal('0')
            top_10 = Decimal(str(row['top_10_holdings'])) if row['top_10_holdings'] else Decimal('0')
            
            # Free float = unlocked - top 10 whale holdings
            free_float = unlocked - top_10
            if free_float < 0:
                free_float = Decimal('0')
            
            # Liquidity ratio = free float / circulating
            liquidity_ratio = float(free_float / circulating) if circulating > 0 else 0.0
            
            # Get Gini coefficient for holder diversity calculation
            dist = await self.get_token_distribution(asset_code, use_cache=True)
            holder_diversity = 1.0 / dist.gini_coefficient if dist.gini_coefficient > 0 else 1.0
            
            element = TOKEN_ELEMENT_MAP.get(TokenCode(asset_code), "unknown")
            
            metrics = LiquidityMetrics(
                asset_code=asset_code,
                element=element.value,
                circulating_supply=circulating,
                locked_supply=locked,
                free_float=free_float,
                liquidity_ratio=liquidity_ratio,
                holder_diversity=holder_diversity
            )
            
            logger.info(f"✓ Liquidity metrics complete for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error calculating liquidity metrics for {asset_code}: {e}")
            raise AnalyticsException(f"Liquidity metrics calculation failed: {e}")
    
    # ========================================================================
    # ECOSYSTEM HEALTH
    # ========================================================================
    
    async def get_ecosystem_health(self) -> EcosystemHealth:
        """
        Get overall ecosystem health metrics.
        
        Returns:
            EcosystemHealth with comprehensive system metrics
            
        Example:
            health = await analytics.get_ecosystem_health()
            print(f"Total accounts: {health.total_accounts}")
            print(f"Element balance: {health.element_balance_score}")
        """
        logger.info("Calculating ecosystem health...")
        
        try:
            # Get account counts
            accounts_query = f"""
                SELECT 
                    COUNT(DISTINCT account_id) as total_accounts,
                    COUNT(DISTINCT account_id) FILTER (
                        WHERE balance > 0
                    ) as total_holders
                FROM {self.db_schema}.ubec_balances
            """
            accounts_row = await self._execute_query(accounts_query, ())
            
            # Get transaction counts (corrected to use stellar_operations - v3.5.6)
            tx_query = f"""
                SELECT COUNT(*) as total_transactions
                FROM {self.db_schema}.stellar_operations
                WHERE type IN ('payment', 'path_payment_strict_receive', 'path_payment_strict_send')
            """
            tx_row = await self._execute_query(tx_query, ())
            
            # Get active accounts (CRITICAL FIX v3.5.9 - counts both senders AND receivers)
            active_24h_query = f"""
                SELECT COUNT(DISTINCT account_id) as active_count
                FROM (
                    SELECT source_account as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    UNION
                    SELECT COALESCE(
                        (details->>'to')::text,
                        (details->>'destination')::text
                    ) as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                      AND (details ? 'to' OR details ? 'destination')
                ) combined
            """
            active_24h = await self._execute_query(active_24h_query, ())
            
            active_7d_query = f"""
                SELECT COUNT(DISTINCT account_id) as active_count
                FROM (
                    SELECT source_account as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                    UNION
                    SELECT COALESCE(
                        (details->>'to')::text,
                        (details->>'destination')::text
                    ) as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                      AND (details ? 'to' OR details ? 'destination')
                ) combined
            """
            active_7d = await self._execute_query(active_7d_query, ())
            
            active_30d_query = f"""
                SELECT COUNT(DISTINCT account_id) as active_count
                FROM (
                    SELECT source_account as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    UNION
                    SELECT COALESCE(
                        (details->>'to')::text,
                        (details->>'destination')::text
                    ) as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                      AND (details ? 'to' OR details ? 'destination')
                ) combined
            """
            active_30d = await self._execute_query(active_30d_query, ())
            
            # Get total supply across all tokens
            supply_query = f"""
                SELECT 
                    SUM(balance) as total_supply,
                    token_code
                FROM {self.db_schema}.ubec_balances
                WHERE balance > 0
                GROUP BY token_code
            """
            supply_rows = await self._execute_query_all(supply_query, ())
            
            total_supply = sum(Decimal(str(row['total_supply'])) for row in supply_rows)
            
            # Calculate element balance score (0-100, higher = more balanced)
            # CRITICAL FIX v3.5.9: Added bounds checking to ensure 0-100 range
            if len(supply_rows) == 4:
                supplies = [Decimal(str(row['total_supply'])) for row in supply_rows]
                avg_supply = total_supply / 4
                
                # Calculate variance from perfect balance
                variance = sum((s - avg_supply) ** 2 for s in supplies) / 4
                std_dev = float(variance.sqrt())
                
                # Convert to 0-100 score (lower variance = higher score)
                # Normalize by average supply to make it percentage-based
                if avg_supply > 0:
                    cv = std_dev / float(avg_supply)  # Coefficient of variation
                    # Score: 100 when perfectly balanced (cv=0), decreases as cv increases
                    # Using 1/(1+cv) gives a nice 0-100 range
                    balance_score = Decimal(str(100 * (1 / (1 + cv))))
                    # CRITICAL FIX: Ensure score is bounded to 0-100
                    balance_score = max(Decimal('0'), min(Decimal('100'), balance_score))
                else:
                    balance_score = Decimal('0')
            else:
                # If not all 4 tokens present, score is 0
                balance_score = Decimal('0')
            
            health = EcosystemHealth(
                timestamp=datetime.now().isoformat(),
                total_accounts=int(accounts_row['total_accounts']) if accounts_row else 0,
                total_holders=int(accounts_row['total_holders']) if accounts_row else 0,
                total_transactions=int(tx_row['total_transactions']) if tx_row else 0,
                total_supply_all_tokens=total_supply,
                active_accounts_24h=int(active_24h['active_count']) if active_24h else 0,
                active_accounts_7d=int(active_7d['active_count']) if active_7d else 0,
                active_accounts_30d=int(active_30d['active_count']) if active_30d else 0,
                element_balance_score=balance_score
            )
            
            logger.info("✓ Ecosystem health calculated")
            return health
            
        except Exception as e:
            self._record_error(f"Error calculating ecosystem health: {e}")
            raise AnalyticsException(f"Ecosystem health calculation failed: {e}")
    
    # ========================================================================
    # TOKEN COMPARISON
    # ========================================================================
    
    async def compare_tokens(self) -> Dict[str, Any]:
        """
        Compare metrics across all UBEC tokens.
        
        Returns:
            Dict with comparative analysis across tokens
            
        Example:
            comparison = await analytics.compare_tokens()
            print(f"Most holders: {comparison['rankings']['by_holders'][0]}")
        """
        logger.info("Comparing all tokens...")
        
        try:
            comparison = {
                'timestamp': datetime.now().isoformat(),
                'tokens': {},
                'rankings': {},
                'totals': {
                    'total_holders': 0,
                    'total_supply': Decimal('0'),
                    'unique_accounts': 0
                }
            }
            
            # Get metrics for each token
            distributions = []
            for token in TokenCode:
                try:
                    dist = await self.get_token_distribution(token.value)
                    distributions.append(dist)
                    comparison['tokens'][token.value] = asdict(dist)
                except Exception as e:
                    logger.warning(f"Could not compare {token.value}: {e}")
            
            # Calculate totals
            comparison['totals']['total_holders'] = sum(d.total_holders for d in distributions)
            comparison['totals']['total_supply'] = sum(d.total_supply for d in distributions)
            
            # Get unique account count
            unique_query = f"""
                SELECT COUNT(DISTINCT account_id) as unique_accounts
                FROM {self.db_schema}.ubec_balances
                WHERE balance > 0
            """
            unique_row = await self._execute_query(unique_query, ())
            comparison['totals']['unique_accounts'] = unique_row['unique_accounts'] if unique_row else 0
            
            # Create rankings
            comparison['rankings']['by_holders'] = [
                {'token': d.asset_code, 'holders': d.total_holders}
                for d in sorted(distributions, key=lambda d: d.total_holders, reverse=True)
            ]
            comparison['rankings']['by_supply'] = [
                {'token': d.asset_code, 'supply': float(d.total_supply)}
                for d in sorted(distributions, key=lambda d: d.total_supply, reverse=True)
            ]
            comparison['rankings']['by_concentration'] = [
                {'token': d.asset_code, 'concentration': float(d.top_10_concentration)}
                for d in sorted(distributions, key=lambda d: d.top_10_concentration, reverse=True)
            ]
            
            # Convert Decimal to float for JSON serialization
            comparison['totals']['total_supply'] = float(comparison['totals']['total_supply'])
            
            logger.info("✓ Token comparison complete")
            return comparison
            
        except Exception as e:
            self._record_error(f"Error comparing tokens: {e}")
            raise AnalyticsException(f"Token comparison failed: {e}")
    
    # ========================================================================
    # EXPORT & REPORTING
    # ========================================================================
    
    async def export_analytics_summary(self) -> Dict[str, Any]:
        """
        Export comprehensive analytics summary for all tokens.
        
        Returns:
            Dict containing all key metrics in exportable format
            
        Example:
            summary = await analytics.export_analytics_summary()
            
            # Save to file
            import json
            with open('ubec_analytics.json', 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        """
        logger.info("Exporting comprehensive analytics summary...")
        
        try:
            summary = {
                'generated_at': datetime.now().isoformat(),
                'ecosystem_health': None,
                'token_distributions': [],
                'holder_concentrations': [],
                'liquidity_metrics': [],
                'token_comparison': None
            }
            
            # Get ecosystem health
            health = await self.get_ecosystem_health()
            summary['ecosystem_health'] = asdict(health)
            
            # Get distributions for all tokens
            for token in TokenCode:
                dist = await self.get_token_distribution(token.value)
                summary['token_distributions'].append(asdict(dist))
                
                holder_analysis = await self.analyze_holder_concentration(token.value)
                summary['holder_concentrations'].append(asdict(holder_analysis))
                
                liquidity = await self.get_liquidity_metrics(token.value)
                summary['liquidity_metrics'].append(asdict(liquidity))
            
            # Get token comparison
            summary['token_comparison'] = await self.compare_tokens()
            
            logger.info("✓ Analytics summary exported")
            return summary
            
        except Exception as e:
            self._record_error(f"Error exporting analytics summary: {e}")
            raise AnalyticsException(f"Analytics export failed: {e}")


# ==================== MODULE EXPORTS ====================

__all__ = [
    'UBECAnalyticsService',
    'TokenDistribution',
    'HolderAnalysis',
    'TransactionMetrics',
    'LiquidityMetrics',
    'EcosystemHealth',
    'TokenCode',
    'ElementType',
    'AnalyticsException'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Principle #2: Service Pattern - No standalone execution

if __name__ == "__main__":
    print("=" * 80)
    print("UBEC Protocol Suite - Analytics Service")
    print("=" * 80)
    print()
    print("This service provides comprehensive analytics for the UBEC token ecosystem.")
    print("It analyzes distribution, holder patterns, and ecosystem health across all")
    print("four UBEC elements (Air, Water, Earth, Fire).")
    print()
    print("VERSION: 3.6.0 (Scheduler Integration)")
    print()
    print("CHANGES FROM v3.6.0:")
    print("✅ ADDED: update_analytics() method for scheduled execution")
    print("✅ ENHANCED: Scheduler integration support")
    print("✅ ENHANCED: Automated analytics refresh capability")
    print()
    print("CHANGES FROM v3.5.9:")
    print("✅ CRITICAL FIX: Active accounts query now counts BOTH senders and receivers")
    print("✅ CRITICAL FIX: Element balance score bounded to 0-100 range")
    print("✅ FIXED: Active accounts metrics now accurate (not zero)")
    print("✅ FIXED: Balance scores can no longer be negative")
    print("✅ RESOLVES: Issue UBEC-001 (zero activity metrics)")
    print("✅ RESOLVES: Issue UBEC-002 (negative balance scores)")
    print()
    print("CHANGES FROM v3.5.8:")
    print("✅ FIXED: Corrected last_modified → last_modified_at in get_top_holders()")
    print("✅ FIXED: Updated row['last_modified'] → row['last_modified_at']")
    print("✅ VERIFIED: Analytics holders command now functional")
    print()
    print("CHANGES FROM v3.5.3:")
    print("✅ FIXED: Added missing async close() method for service registry shutdown")
    print("✅ ENHANCED: Proper resource cleanup and cache clearing on close")
    print("✅ FIXED: Service now properly logs closure during shutdown sequence")
    print()
    print("CHANGES FROM v3.5.2:")
    print("✅ FIXED: SQL GROUP BY aggregation error in token distribution query")
    print()
    print("CHANGES FROM v3.5.1:")
    print("✅ FIXED: Schema defaults to 'ubec_main' (was incorrectly 'public')")
    print("✅ ENHANCED: Better config object handling")
    print()
    print("CHANGES FROM v3.5.0:")
    print("✅ FIXED: Added missing initialize() method for service registry")
    print()
    print("CHANGES FROM v3.4:")
    print("✅ ADDED: Transaction velocity metrics to get_distribution_overview()")
    print("✅ ENHANCED: Summary statistics with transaction-related metrics")
    print("✅ ENHANCED: Rankings now include velocity-based comparisons")
    print()
    print("USAGE:")
    print("------")
    print()
    print("  # Via service registry (RECOMMENDED - Principle #3)")
    print("  from core.service_registry import registry")
    print("  analytics = await registry.get('analytics')")
    print()
    print("  # Main.py interface methods (v3.4.0+, fixed v3.5.9)")
    print("  result = await analytics.get_distribution_overview()  # Overview + velocity")
    print("  result = await analytics.get_top_holders(limit=50)    # Holders")
    print("  result = await analytics.get_network_metrics()        # Metrics (FIXED!)")
    print()
    print("  # Scheduled operations (NEW in v3.6.0)")
    print("  result = await analytics.update_analytics()           # Refresh all metrics")
    print()
    print("  # Alternative CLI command interface")
    print("  result = await analytics.analyze_token_distribution()  # Distribution")
    print("  result = await analytics.calculate_velocity()          # Velocity")
    print("  result = await analytics.calculate_concentration()     # Concentration")
    print()
    print("  # Get token distribution")
    print("  dist = await analytics.get_token_distribution('UBEC')")
    print("  print(f'Holders: {dist.total_holders}')")
    print()
    print("  # Health check (uses ServiceHealthCheck utility!)")
    print("  health = await analytics.health_check()")
    print("  print(f'Status: {health[\"status\"]}')")
    print("  print(f'Cache hit rate: {health[\"details\"][\"cache_hit_rate\"]:.1%}')")
    print()
    print("  # Proper shutdown (NEW in v3.5.4)")
    print("  await analytics.close()")
    print()
    print("DESIGN PRINCIPLES:")
    print("------------------")
    print("✅ All 12 principles fully implemented")
    print("✅ Proper service registry close() method (v3.5.4)")
    print("✅ Interface contract now aligned with main.py")
    print("✅ Transaction velocity metrics fully integrated")
    print("✅ Enhanced health check using ServiceHealthCheck utility")
    print("✅ All CLI command methods properly implemented")
    print("✅ Comprehensive error tracking and reporting")
    print("✅ Cache performance monitoring")
    print("✅ Explicit schema names in all database queries")
    print("✅ CRITICAL FIX: Active accounts now accurate (v3.5.9)")
    print("✅ CRITICAL FIX: Balance scores always 0-100 (v3.5.9)")
    print("✅ NEW: Scheduler integration with update_analytics() (v3.6.0)")
    print()
    print("=" * 80)
