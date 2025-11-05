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
Version: 3.5.4 (Service Registry Compliance Fix)
Date: November 1, 2025

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


@dataclass
class TokenDistribution:
    """Token distribution metrics"""
    asset_code: str
    element: str
    total_holders: int
    total_supply: Decimal
    average_balance: Decimal
    median_balance: Decimal
    min_balance: Decimal
    max_balance: Decimal
    top_10_concentration: Decimal  # Percentage held by top 10
    top_100_concentration: Decimal  # Percentage held by top 100
    gini_coefficient: Optional[Decimal] = None  # Inequality measure


@dataclass
class HolderAnalysis:
    """Holder concentration analysis"""
    asset_code: str
    total_holders: int
    whale_count: int  # Holders above whale threshold
    whale_holdings: Decimal
    whale_percentage: Decimal
    mid_tier_count: int
    mid_tier_holdings: Decimal
    small_holder_count: int
    small_holder_holdings: Decimal


@dataclass
class TransactionMetrics:
    """Transaction analysis metrics"""
    asset_code: str
    period_days: int
    total_transactions: int
    unique_senders: int
    unique_receivers: int
    total_volume: Decimal
    average_transaction_size: Decimal
    median_transaction_size: Decimal
    velocity: Decimal  # Transactions per day
    turnover_ratio: Decimal  # Volume / Total Supply


@dataclass
class LiquidityMetrics:
    """Liquidity analysis"""
    asset_code: str
    total_supply: Decimal
    circulating_supply: Decimal
    locked_supply: Decimal
    available_liquidity: Decimal
    liquidity_ratio: Decimal  # Available / Total


@dataclass
class EcosystemHealth:
    """Overall ecosystem health metrics"""
    timestamp: datetime
    total_holders: int
    total_accounts: int
    total_transactions: int
    total_supply_all_tokens: Decimal
    active_accounts_24h: int
    active_accounts_7d: int
    active_accounts_30d: int
    element_balance_score: Decimal  # How balanced are the 4 elements


class AnalyticsException(Exception):
    """Custom exception for analytics-related errors"""
    pass


class UBECAnalyticsService:
    """
    Comprehensive analytics service for UBEC token ecosystem.
    
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
        analytics = await registry.get('ubec_analytics_service')
        
        # CLI command interface - main.py interface methods
        result = await analytics.get_distribution_overview()  # Overview analytics
        result = await analytics.get_top_holders(limit=50)    # Holder rankings
        result = await analytics.get_network_metrics()        # Network metrics
        
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
            db_manager: AsyncDatabaseManager instance
            config: Configuration service or dict
        """
        self.db = db_manager
        self.config = config
        self._initialized = False
        
        # Get schema from config (Principle #4: Single Source of Truth)
        if hasattr(config, 'get'):
            # Settings object
            self.db_schema = config.get('db_schema', 'ubec_main')
        else:
            # Dictionary
            self.db_schema = config.get('db_schema', 'ubec_main')
        
        # Caching for performance
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_clear = datetime.now()
        
        # Metrics tracking (Principle #7: Per-Asset Monitoring)
        self._query_count = 0
        self._cache_hits = 0
        self._error_count = 0
        self._last_error = None
        self._last_error_time = None
        
        logger.info(f"✓ ubec_analytics_service v3.5.4 initialized")
    
    async def initialize(self) -> None:
        """
        Initialize the analytics service.
        
        Required by service registry pattern (Principle #2, #3).
        Performs any async initialization needed.
        """
        if self._initialized:
            logger.warning("Analytics service already initialized")
            return
        
        # Verify database connection
        try:
            await self.db.fetch_one(f"SELECT 1 FROM {self.db_schema}.system_settings LIMIT 1", ())
            self._initialized = True
            logger.info("ubec_analytics_service async initialization complete")
        except Exception as e:
            self._record_error(f"Initialization failed: {e}")
            raise AnalyticsException(f"Failed to initialize analytics service: {e}")
    
    async def close(self) -> None:
        """
        Close the analytics service and cleanup resources.
        
        Implements Principle #2 (Service Pattern) and Principle #3 (Service Registry).
        This method is called by the service registry during shutdown.
        
        Performs:
        - Cache cleanup
        - Resource deallocation
        - Metric reset
        - State cleanup
        
        Note:
            This method is idempotent - safe to call multiple times.
        """
        try:
            # Clear all caches
            self._cache.clear()
            
            # Reset metrics
            self._query_count = 0
            self._cache_hits = 0
            self._error_count = 0
            self._last_error = None
            self._last_error_time = None
            
            # Mark as uninitialized
            self._initialized = False
            
            logger.info("✓ ubec_analytics_service closed")
            
        except Exception as e:
            logger.error(f"Error closing ubec_analytics_service: {e}")
            # Don't re-raise - cleanup should be best-effort
    
    # ========================================================================
    # HEALTH CHECK (Principle #7 & #12)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check using standardized ServiceHealthCheck.
        
        Implements:
        - Principle #7: Per-Asset Monitoring with health tracking
        - Principle #12: Method Singularity using ServiceHealthCheck utility
        
        Returns:
            Health status dictionary from ServiceHealthCheck utility:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy' | 'unknown',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'database_connected': bool,
                    'schema': str,
                    'query_count': int,
                    'cache_hits': int,
                    'cache_hit_rate': float,
                    'error_count': int,
                    'last_error': str,
                    'last_error_time': str
                }
            }
        
        Example:
            >>> health = await analytics.health_check()
            >>> if health['status'] == 'healthy':
            ...     print(f"Analytics operational, {health['details']['query_count']} queries")
        """
        return await ServiceHealthCheck.database_dependent_health(
            service_name='ubec_analytics_service',
            db_manager=self.db,
            is_initialized=self._initialized,
            additional_context={
                'schema': self.db_schema,
                'query_count': self._query_count,
                'cache_hits': self._cache_hits,
                'cache_hit_rate': self._cache_hits / max(self._query_count, 1),
                'error_count': self._error_count,
                'last_error': self._last_error,
                'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None
            }
        )
    
    # ========================================================================
    # INTERNAL UTILITIES
    # ========================================================================
    
    def _get_cache_key(self, method: str, *args, **kwargs) -> str:
        """Generate cache key for a method call"""
        key_parts = [method]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if valid"""
        if key in self._cache:
            cached_value, cached_time = self._cache[key]
            if (datetime.now() - cached_time).total_seconds() < self._cache_ttl:
                self._cache_hits += 1
                return cached_value
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Store value in cache"""
        self._cache[key] = (value, datetime.now())
        
        # Periodic cache cleanup
        if (datetime.now() - self._last_cache_clear).total_seconds() > 600:  # 10 minutes
            self._clear_expired_cache()
    
    def _clear_expired_cache(self) -> None:
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, cached_time) in self._cache.items()
            if (now - cached_time).total_seconds() >= self._cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]
        self._last_cache_clear = now
    
    def _record_error(self, error_msg: str) -> None:
        """Record error for health monitoring"""
        self._error_count += 1
        self._last_error = error_msg
        self._last_error_time = datetime.now()
        logger.error(error_msg)
    
    async def _execute_query(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Execute a query and return single result.
        
        Principle #5: Strict async operations.
        Automatically tracks query metrics.
        """
        try:
            self._query_count += 1
            return await self.db.fetch_one(query, params)
        except Exception as e:
            self._record_error(f"Query execution failed: {e}")
            raise
    
    async def _execute_query_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a query and return all results.
        
        Principle #5: Strict async operations.
        Automatically tracks query metrics.
        """
        try:
            self._query_count += 1
            return await self.db.fetch_all(query, params)
        except Exception as e:
            self._record_error(f"Query execution failed: {e}")
            raise
    
    # ========================================================================
    # MAIN.PY INTERFACE METHODS (v3.4.0+)
    # These methods are called directly by main.py CLI commands
    # ========================================================================
    
    async def get_distribution_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive distribution overview for all tokens.
        
        Main.py interface method for 'analytics' command.
        Includes transaction velocity metrics (v3.4.0+).
        
        Returns:
            Dict with complete analytics overview including:
            - distributions: List of TokenDistribution for each element
            - summary: Aggregated statistics
            - rankings: Token rankings by various metrics
            - velocity: Transaction velocity metrics per token
            
        Example (from main.py):
            analytics = await registry.get('ubec_analytics_service')
            overview = await analytics.get_distribution_overview()
            print(f"Total holders: {overview['summary']['total_holders']}")
            print(f"Avg velocity: {overview['summary']['avg_velocity']}")
        """
        logger.info("Generating distribution overview with velocity metrics...")
        
        try:
            # Get distributions for all tokens
            distributions = await self.get_all_token_distributions(use_cache=True)
            
            # Get velocity metrics for all tokens
            velocities = {}
            for token in TokenCode:
                try:
                    velocity = await self.get_transaction_velocity(token.value, period_days=30)
                    velocities[token.value] = velocity
                except Exception as e:
                    logger.warning(f"Could not get velocity for {token.value}: {e}")
                    velocities[token.value] = Decimal('0')
            
            # Create summary statistics
            summary = {
                'total_holders': sum(d.total_holders for d in distributions),
                'total_supply': float(sum(d.total_supply for d in distributions)),
                'avg_concentration': float(sum(d.top_10_concentration for d in distributions) / len(distributions)),
                'avg_velocity': float(sum(velocities.values()) / len(velocities)) if velocities else 0,
                'tokens_analyzed': len(distributions)
            }
            
            # Create rankings
            rankings = {
                'by_holders': [
                    {'token': d.asset_code, 'element': d.element, 'holders': d.total_holders}
                    for d in sorted(distributions, key=lambda d: d.total_holders, reverse=True)
                ],
                'by_supply': [
                    {'token': d.asset_code, 'element': d.element, 'supply': float(d.total_supply)}
                    for d in sorted(distributions, key=lambda d: d.total_supply, reverse=True)
                ],
                'by_velocity': [
                    {'token': token, 'velocity': float(vel)}
                    for token, vel in sorted(velocities.items(), key=lambda x: x[1], reverse=True)
                ]
            }
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'distributions': [asdict(d) for d in distributions],
                'velocities': {k: float(v) for k, v in velocities.items()},
                'summary': summary,
                'rankings': rankings
            }
            
            logger.info("✓ Distribution overview with velocity generated")
            return result
            
        except Exception as e:
            self._record_error(f"Error generating distribution overview: {e}")
            raise AnalyticsException(f"Distribution overview failed: {e}")
    
    async def get_top_holders(self, token_code: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Get top holders across all tokens or for specific token.
        
        Main.py interface method for holder analysis.
        
        Args:
            token_code: Optional token code to filter (None = all tokens)
            limit: Maximum number of holders to return per token
            
        Returns:
            Dict with top holders by token:
            {
                'UBEC': [{'account_id': ..., 'balance': ...}, ...],
                'UBECrc': [...],
                ...
            }
        
        Example (from main.py):
            holders = await analytics.get_top_holders(limit=50)
            for token, accounts in holders.items():
                print(f"{token}: {len(accounts)} top holders")
        """
        logger.info(f"Getting top {limit} holders" + (f" for {token_code}" if token_code else ""))
        
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'limit': limit,
                'holders': {}
            }
            
            tokens = [TokenCode(token_code)] if token_code else list(TokenCode)
            
            for token in tokens:
                query = f"""
                    SELECT 
                        account_id,
                        balance,
                        last_modified,
                        RANK() OVER (ORDER BY balance DESC) as rank
                    FROM {self.db_schema}.ubec_balances
                    WHERE asset_code = $1 AND balance > 0
                    ORDER BY balance DESC
                    LIMIT $2
                """
                
                rows = await self._execute_query_all(query, (token.value, limit))
                
                result['holders'][token.value] = [
                    {
                        'account_id': row['account_id'],
                        'balance': float(row['balance']),
                        'last_modified': row['last_modified'].isoformat() if row['last_modified'] else None,
                        'rank': row['rank']
                    }
                    for row in rows
                ]
            
            logger.info(f"✓ Retrieved top holders for {len(result['holders'])} token(s)")
            return result
            
        except Exception as e:
            self._record_error(f"Error getting top holders: {e}")
            raise AnalyticsException(f"Top holders query failed: {e}")
    
    async def get_network_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive network metrics.
        
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
            token_code: Optional token code (None = all tokens)
            period_days: Analysis period in days
            
        Returns:
            Velocity metrics by token
        """
        logger.info(f"Calculating velocity for {period_days} days")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'period_days': period_days,
            'velocities': {}
        }
        
        tokens = [TokenCode(token_code)] if token_code else list(TokenCode)
        
        for token in tokens:
            velocity = await self.get_transaction_velocity(token.value, period_days)
            result['velocities'][token.value] = float(velocity)
        
        return result
    
    async def calculate_concentration(self, token_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate holder concentration.
        
        Alternative CLI method for concentration analysis.
        
        Args:
            token_code: Optional token code (None = all tokens)
            
        Returns:
            Concentration analysis by token
        """
        logger.info("Calculating holder concentration")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'concentrations': {}
        }
        
        tokens = [TokenCode(token_code)] if token_code else list(TokenCode)
        
        for token in tokens:
            analysis = await self.analyze_holder_concentration(token.value)
            result['concentrations'][token.value] = asdict(analysis)
        
        return result
    
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
        
        Analyzes:
        - Total holders and supply
        - Balance statistics (average, median, min, max)
        - Top holder concentration (top 10, top 100)
        - Gini coefficient (inequality measure)
        
        Args:
            asset_code: Token code to analyze (UBEC, UBECrc, UBECgpi, UBECtt)
            use_cache: Whether to use cached results if available
            
        Returns:
            TokenDistribution dataclass with complete metrics
            
        Raises:
            AnalyticsException: If token code invalid or query fails
            
        Example:
            dist = await analytics.get_token_distribution('UBEC')
            print(f"Total holders: {dist.total_holders}")
            print(f"Top 10 control: {dist.top_10_concentration}%")
        """
        # Validate token code
        try:
            TokenCode(asset_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {asset_code}")
        
        # Check cache
        cache_key = self._get_cache_key('get_token_distribution', asset_code)
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
        
        logger.info(f"Analyzing distribution for {asset_code}...")
        
        try:
            # Query with explicit schema name (Principle #4)
            query = f"""
                WITH holder_stats AS (
                    SELECT 
                        asset_code,
                        COUNT(DISTINCT account_id) as total_holders,
                        SUM(balance) as total_supply,
                        AVG(balance) as avg_balance,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance,
                        MIN(balance) as min_balance,
                        MAX(balance) as max_balance
                    FROM {self.db_schema}.ubec_balances
                    WHERE asset_code = $1 AND balance > 0
                    GROUP BY asset_code
                ),
                top_holders AS (
                    SELECT 
                        asset_code,
                        MAX(top_10_sum) as top_10_sum,
                        MAX(top_100_sum) as top_100_sum
                    FROM (
                        SELECT 
                            asset_code,
                            SUM(balance) FILTER (WHERE rank <= 10) as top_10_sum,
                            SUM(balance) FILTER (WHERE rank <= 100) as top_100_sum
                        FROM (
                            SELECT 
                                asset_code,
                                balance,
                                RANK() OVER (PARTITION BY asset_code ORDER BY balance DESC) as rank
                            FROM {self.db_schema}.ubec_balances
                            WHERE asset_code = $1 AND balance > 0
                        ) ranked
                        GROUP BY asset_code
                    ) aggregated
                    GROUP BY asset_code
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
            
            # Calculate Gini coefficient
            gini = await self._calculate_gini_coefficient(asset_code)
            
            distribution = TokenDistribution(
                asset_code=row['asset_code'],
                element=element.value,
                total_holders=row['total_holders'],
                total_supply=Decimal(str(row['total_supply'])),
                average_balance=Decimal(str(row['avg_balance'])),
                median_balance=Decimal(str(row['median_balance'])),
                min_balance=Decimal(str(row['min_balance'])),
                max_balance=Decimal(str(row['max_balance'])),
                top_10_concentration=Decimal(str(row['top_10_concentration'])),
                top_100_concentration=Decimal(str(row['top_100_concentration'])),
                gini_coefficient=gini
            )
            
            # Cache result
            self._set_cache(cache_key, distribution)
            
            logger.info(f"✓ Distribution analysis complete for {asset_code}")
            return distribution
            
        except Exception as e:
            self._record_error(f"Error analyzing distribution for {asset_code}: {e}")
            raise AnalyticsException(f"Distribution analysis failed: {e}")
    
    async def get_all_token_distributions(
        self,
        use_cache: bool = True
    ) -> List[TokenDistribution]:
        """
        Get distribution metrics for all UBEC tokens.
        
        Args:
            use_cache: Whether to use cached results if available
            
        Returns:
            List of TokenDistribution for all four elements
            
        Example:
            distributions = await analytics.get_all_token_distributions()
            for dist in distributions:
                print(f"{dist.asset_code}: {dist.total_holders} holders")
        """
        logger.info("Analyzing all token distributions...")
        
        distributions = []
        for token in TokenCode:
            dist = await self.get_token_distribution(token.value, use_cache)
            distributions.append(dist)
        
        logger.info(f"✓ Analyzed {len(distributions)} token distributions")
        return distributions
    
    async def _calculate_gini_coefficient(self, asset_code: str) -> Decimal:
        """
        Calculate Gini coefficient for token distribution.
        
        Gini coefficient measures inequality (0 = perfect equality, 1 = perfect inequality).
        
        Args:
            asset_code: Token to analyze
            
        Returns:
            Gini coefficient as Decimal
        """
        query = f"""
            WITH ordered_balances AS (
                SELECT 
                    balance,
                    ROW_NUMBER() OVER (ORDER BY balance) as rank,
                    COUNT(*) OVER () as total_count,
                    SUM(balance) OVER () as total_balance
                FROM {self.db_schema}.ubec_balances
                WHERE asset_code = $1 AND balance > 0
            ),
            gini_parts AS (
                SELECT 
                    SUM((2 * rank - total_count - 1) * balance) as numerator,
                    MAX(total_count * total_balance) as denominator
                FROM ordered_balances
            )
            SELECT 
                CASE 
                    WHEN denominator > 0 THEN numerator::DECIMAL / denominator
                    ELSE 0
                END as gini
            FROM gini_parts
        """
        
        row = await self._execute_query(query, (asset_code,))
        return Decimal(str(row['gini'])) if row and row['gini'] else Decimal('0')
    
    # ========================================================================
    # HOLDER CONCENTRATION ANALYSIS
    # ========================================================================
    
    async def analyze_holder_concentration(
        self,
        asset_code: str,
        whale_threshold: Optional[Decimal] = None
    ) -> HolderAnalysis:
        """
        Analyze holder concentration with whale/mid-tier/small holder breakdown.
        
        Args:
            asset_code: Token to analyze
            whale_threshold: Balance threshold for whale classification.
                           If None, uses top 1% of balances
            
        Returns:
            HolderAnalysis dataclass with concentration metrics
            
        Example:
            analysis = await analytics.analyze_holder_concentration('UBEC')
            print(f"Whales: {analysis.whale_count} ({analysis.whale_percentage}%)")
        """
        try:
            TokenCode(asset_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {asset_code}")
        
        logger.info(f"Analyzing holder concentration for {asset_code}...")
        
        try:
            # Determine whale threshold if not provided
            if whale_threshold is None:
                threshold_query = f"""
                    SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY balance) as threshold
                    FROM {self.db_schema}.ubec_balances
                    WHERE asset_code = $1 AND balance > 0
                """
                row = await self._execute_query(threshold_query, (asset_code,))
                whale_threshold = Decimal(str(row['threshold'])) if row else Decimal('0')
            
            # Calculate mid-tier threshold (median)
            mid_query = f"""
                SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as threshold
                FROM {self.db_schema}.ubec_balances
                WHERE asset_code = $1 AND balance > 0
            """
            row = await self._execute_query(mid_query, (asset_code,))
            mid_threshold = Decimal(str(row['threshold'])) if row else Decimal('0')
            
            # Analyze tiers
            query = f"""
                WITH tiers AS (
                    SELECT 
                        CASE 
                            WHEN balance >= $2 THEN 'whale'
                            WHEN balance >= $3 THEN 'mid_tier'
                            ELSE 'small'
                        END as tier,
                        COUNT(*) as holder_count,
                        SUM(balance) as total_balance
                    FROM {self.db_schema}.ubec_balances
                    WHERE asset_code = $1 AND balance > 0
                    GROUP BY tier
                ),
                totals AS (
                    SELECT 
                        COUNT(*) as total_holders,
                        SUM(balance) as total_supply
                    FROM {self.db_schema}.ubec_balances
                    WHERE asset_code = $1 AND balance > 0
                )
                SELECT 
                    t.tier,
                    t.holder_count,
                    t.total_balance,
                    totals.total_holders,
                    totals.total_supply
                FROM tiers t
                CROSS JOIN totals
            """
            
            rows = await self._execute_query_all(
                query,
                (asset_code, float(whale_threshold), float(mid_threshold))
            )
            
            # Extract metrics
            metrics = {row['tier']: row for row in rows}
            total_holders = rows[0]['total_holders'] if rows else 0
            total_supply = Decimal(str(rows[0]['total_supply'])) if rows else Decimal('0')
            
            whale = metrics.get('whale', {})
            mid = metrics.get('mid_tier', {})
            small = metrics.get('small', {})
            
            analysis = HolderAnalysis(
                asset_code=asset_code,
                total_holders=total_holders,
                whale_count=whale.get('holder_count', 0),
                whale_holdings=Decimal(str(whale.get('total_balance', 0))),
                whale_percentage=(
                    Decimal(str(whale.get('total_balance', 0))) / total_supply * 100
                    if total_supply > 0 else Decimal('0')
                ),
                mid_tier_count=mid.get('holder_count', 0),
                mid_tier_holdings=Decimal(str(mid.get('total_balance', 0))),
                small_holder_count=small.get('holder_count', 0),
                small_holder_holdings=Decimal(str(small.get('total_balance', 0)))
            )
            
            logger.info(f"✓ Holder concentration analysis complete for {asset_code}")
            return analysis
            
        except Exception as e:
            self._record_error(f"Error analyzing holder concentration for {asset_code}: {e}")
            raise AnalyticsException(f"Holder concentration analysis failed: {e}")
    
    # ========================================================================
    # TRANSACTION ANALYSIS
    # ========================================================================
    
    async def get_transaction_metrics(
        self,
        asset_code: str,
        period_days: int = 30
    ) -> TransactionMetrics:
        """
        Get comprehensive transaction metrics for a token.
        
        Args:
            asset_code: Token to analyze
            period_days: Analysis period in days
            
        Returns:
            TransactionMetrics dataclass with transaction analysis
            
        Example:
            metrics = await analytics.get_transaction_metrics('UBEC', period_days=7)
            print(f"Velocity: {metrics.velocity} tx/day")
            print(f"Volume: {metrics.total_volume}")
        """
        try:
            TokenCode(asset_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {asset_code}")
        
        logger.info(f"Analyzing transactions for {asset_code} ({period_days} days)...")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
            query = f"""
                WITH tx_stats AS (
                    SELECT 
                        COUNT(*) as total_transactions,
                        COUNT(DISTINCT from_account) as unique_senders,
                        COUNT(DISTINCT to_account) as unique_receivers,
                        SUM(amount) as total_volume,
                        AVG(amount) as avg_amount,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median_amount
                    FROM {self.db_schema}.ubec_transactions
                    WHERE asset_code = $1
                      AND transaction_time >= $2
                      AND transaction_type = 'payment'
                ),
                supply_stats AS (
                    SELECT SUM(balance) as total_supply
                    FROM {self.db_schema}.ubec_balances
                    WHERE asset_code = $1 AND balance > 0
                )
                SELECT 
                    tx.*,
                    supply.total_supply
                FROM tx_stats tx
                CROSS JOIN supply_stats supply
            """
            
            row = await self._execute_query(query, (asset_code, cutoff_date))
            
            if not row or row['total_transactions'] == 0:
                # No transactions in period
                return TransactionMetrics(
                    asset_code=asset_code,
                    period_days=period_days,
                    total_transactions=0,
                    unique_senders=0,
                    unique_receivers=0,
                    total_volume=Decimal('0'),
                    average_transaction_size=Decimal('0'),
                    median_transaction_size=Decimal('0'),
                    velocity=Decimal('0'),
                    turnover_ratio=Decimal('0')
                )
            
            total_volume = Decimal(str(row['total_volume']))
            total_supply = Decimal(str(row['total_supply']))
            
            metrics = TransactionMetrics(
                asset_code=asset_code,
                period_days=period_days,
                total_transactions=row['total_transactions'],
                unique_senders=row['unique_senders'],
                unique_receivers=row['unique_receivers'],
                total_volume=total_volume,
                average_transaction_size=Decimal(str(row['avg_amount'])),
                median_transaction_size=Decimal(str(row['median_amount'])),
                velocity=Decimal(str(row['total_transactions'])) / Decimal(str(period_days)),
                turnover_ratio=(
                    total_volume / total_supply if total_supply > 0 else Decimal('0')
                )
            )
            
            logger.info(f"✓ Transaction metrics complete for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error analyzing transactions for {asset_code}: {e}")
            raise AnalyticsException(f"Transaction analysis failed: {e}")
    
    async def get_transaction_velocity(
        self,
        asset_code: str,
        period_days: int = 30
    ) -> Decimal:
        """
        Get transaction velocity (transactions per day).
        
        Args:
            asset_code: Token to analyze
            period_days: Analysis period
            
        Returns:
            Velocity as Decimal (transactions/day)
        """
        metrics = await self.get_transaction_metrics(asset_code, period_days)
        return metrics.velocity
    
    # ========================================================================
    # LIQUIDITY ANALYSIS
    # ========================================================================
    
    async def get_liquidity_metrics(self, asset_code: str) -> LiquidityMetrics:
        """
        Analyze token liquidity and supply metrics.
        
        Args:
            asset_code: Token to analyze
            
        Returns:
            LiquidityMetrics dataclass with liquidity analysis
            
        Example:
            liquidity = await analytics.get_liquidity_metrics('UBEC')
            print(f"Liquidity ratio: {liquidity.liquidity_ratio}")
        """
        try:
            TokenCode(asset_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {asset_code}")
        
        logger.info(f"Analyzing liquidity for {asset_code}...")
        
        try:
            query = f"""
                WITH supply_breakdown AS (
                    SELECT 
                        SUM(balance) as total_supply,
                        SUM(CASE WHEN is_locked THEN balance ELSE 0 END) as locked_supply,
                        SUM(CASE WHEN NOT is_locked THEN balance ELSE 0 END) as circulating_supply
                    FROM {self.db_schema}.ubec_balances
                    WHERE asset_code = $1 AND balance > 0
                )
                SELECT 
                    total_supply,
                    circulating_supply,
                    locked_supply,
                    circulating_supply as available_liquidity,
                    CASE 
                        WHEN total_supply > 0 
                        THEN circulating_supply::DECIMAL / total_supply
                        ELSE 0
                    END as liquidity_ratio
                FROM supply_breakdown
            """
            
            row = await self._execute_query(query, (asset_code,))
            
            if not row:
                raise AnalyticsException(f"No liquidity data found for {asset_code}")
            
            metrics = LiquidityMetrics(
                asset_code=asset_code,
                total_supply=Decimal(str(row['total_supply'])),
                circulating_supply=Decimal(str(row['circulating_supply'])),
                locked_supply=Decimal(str(row['locked_supply'])),
                available_liquidity=Decimal(str(row['available_liquidity'])),
                liquidity_ratio=Decimal(str(row['liquidity_ratio']))
            )
            
            logger.info(f"✓ Liquidity analysis complete for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error analyzing liquidity for {asset_code}: {e}")
            raise AnalyticsException(f"Liquidity analysis failed: {e}")
    
    # ========================================================================
    # ECOSYSTEM HEALTH
    # ========================================================================
    
    async def get_ecosystem_health(self) -> EcosystemHealth:
        """
        Get comprehensive ecosystem health metrics.
        
        Analyzes:
        - Total accounts and holders
        - Transaction activity
        - Token supply distribution
        - Active account trends
        - Element balance score
        
        Returns:
            EcosystemHealth dataclass with ecosystem metrics
            
        Example:
            health = await analytics.get_ecosystem_health()
            print(f"Total holders: {health.total_holders}")
            print(f"Active 24h: {health.active_accounts_24h}")
        """
        logger.info("Calculating ecosystem health metrics...")
        
        try:
            # Get basic stats
            basic_query = f"""
                WITH account_stats AS (
                    SELECT 
                        COUNT(DISTINCT account_id) as total_accounts,
                        COUNT(DISTINCT CASE WHEN balance > 0 THEN account_id END) as total_holders
                    FROM {self.db_schema}.ubec_balances
                ),
                tx_stats AS (
                    SELECT COUNT(*) as total_transactions
                    FROM {self.db_schema}.ubec_transactions
                ),
                supply_stats AS (
                    SELECT SUM(balance) as total_supply
                    FROM {self.db_schema}.ubec_balances
                    WHERE balance > 0
                )
                SELECT 
                    a.total_accounts,
                    a.total_holders,
                    t.total_transactions,
                    s.total_supply
                FROM account_stats a
                CROSS JOIN tx_stats t
                CROSS JOIN supply_stats s
            """
            
            basic = await self._execute_query(basic_query, ())
            
            # Get active accounts
            now = datetime.now()
            cutoff_24h = now - timedelta(hours=24)
            cutoff_7d = now - timedelta(days=7)
            cutoff_30d = now - timedelta(days=30)
            
            active_query = f"""
                SELECT 
                    COUNT(DISTINCT CASE 
                        WHEN transaction_time >= $1 
                        THEN from_account 
                    END) as active_24h,
                    COUNT(DISTINCT CASE 
                        WHEN transaction_time >= $2 
                        THEN from_account 
                    END) as active_7d,
                    COUNT(DISTINCT CASE 
                        WHEN transaction_time >= $3 
                        THEN from_account 
                    END) as active_30d
                FROM {self.db_schema}.ubec_transactions
            """
            
            active = await self._execute_query(active_query, (cutoff_24h, cutoff_7d, cutoff_30d))
            
            # Calculate element balance score
            balance_score = await self._calculate_element_balance_score()
            
            health = EcosystemHealth(
                timestamp=now,
                total_holders=basic['total_holders'],
                total_accounts=basic['total_accounts'],
                total_transactions=basic['total_transactions'],
                total_supply_all_tokens=Decimal(str(basic['total_supply'])),
                active_accounts_24h=active['active_24h'],
                active_accounts_7d=active['active_7d'],
                active_accounts_30d=active['active_30d'],
                element_balance_score=balance_score
            )
            
            logger.info("✓ Ecosystem health metrics calculated")
            return health
            
        except Exception as e:
            self._record_error(f"Error calculating ecosystem health: {e}")
            raise AnalyticsException(f"Ecosystem health calculation failed: {e}")
    
    async def _calculate_element_balance_score(self) -> Decimal:
        """
        Calculate how balanced the four elements are.
        
        Perfect balance (all elements equal) = 100
        Complete imbalance (one element dominates) = 0
        
        Returns:
            Balance score as Decimal (0-100)
        """
        query = f"""
            WITH element_supplies AS (
                SELECT 
                    asset_code,
                    SUM(balance) as supply
                FROM {self.db_schema}.ubec_balances
                WHERE balance > 0
                GROUP BY asset_code
            ),
            supply_stats AS (
                SELECT 
                    supply,
                    AVG(supply) OVER () as avg_supply,
                    STDDEV(supply) OVER () as stddev_supply
                FROM element_supplies
            )
            SELECT 
                CASE 
                    WHEN MAX(stddev_supply) = 0 THEN 100  -- Perfect balance
                    ELSE 100 - (MIN(stddev_supply) / NULLIF(MAX(avg_supply), 0) * 100)
                END as balance_score
            FROM supply_stats
        """
        
        row = await self._execute_query(query, ())
        return Decimal(str(row['balance_score'])) if row else Decimal('0')
    
    # ========================================================================
    # COMPARATIVE ANALYSIS
    # ========================================================================
    
    async def compare_tokens(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Compare all UBEC tokens side-by-side.
        
        Args:
            use_cache: Whether to use cached distributions
            
        Returns:
            Dict with comparative analysis:
            - tokens: Per-token metrics
            - totals: Aggregated totals
            - rankings: Comparative rankings
            
        Example:
            comparison = await analytics.compare_tokens()
            for token, metrics in comparison['tokens'].items():
                print(f"{token}: {metrics['total_holders']} holders")
        """
        logger.info("Comparing all UBEC tokens...")
        
        try:
            # Get distributions for all tokens
            distributions = await self.get_all_token_distributions(use_cache)
            
            comparison = {
                'timestamp': datetime.now().isoformat(),
                'tokens': {},
                'totals': {
                    'total_holders': 0,
                    'total_supply': Decimal('0'),
                    'unique_accounts': 0
                },
                'rankings': {
                    'by_holders': [],
                    'by_supply': [],
                    'by_concentration': []
                }
            }
            
            # Compile token data
            for dist in distributions:
                comparison['tokens'][dist.asset_code] = {
                    'element': dist.element,
                    'total_holders': dist.total_holders,
                    'total_supply': float(dist.total_supply),
                    'average_balance': float(dist.average_balance),
                    'median_balance': float(dist.median_balance),
                    'top_10_concentration': float(dist.top_10_concentration),
                    'gini_coefficient': float(dist.gini_coefficient) if dist.gini_coefficient else None
                }
                
                comparison['totals']['total_supply'] += dist.total_supply
            
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
    print("VERSION: 3.5.4 (Service Registry Compliance Fix)")
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
    print("  analytics = await registry.get('ubec_analytics_service')")
    print()
    print("  # Main.py interface methods (v3.4.0+, enhanced v3.5.4)")
    print("  result = await analytics.get_distribution_overview()  # Overview + velocity")
    print("  result = await analytics.get_top_holders(limit=50)    # Holders")
    print("  result = await analytics.get_network_metrics()        # Metrics")
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
    print()
    print("=" * 80)
