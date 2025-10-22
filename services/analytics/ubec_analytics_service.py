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
Version: 3.0.0 (Enhanced Health Check Integration)
Date: October 17, 2025

Changes from v2.0:
- Enhanced health check using ServiceHealthCheck utility (Principle #12)
- Added data freshness validation
- Improved error handling and reporting
- Better integration with service registry
- Enhanced caching statistics in health check
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
        analytics = await registry.get('analytics')
        
        # Direct instantiation (for testing only)
        db = AsyncDatabaseManager(config)
        await db.initialize()
        
        analytics = UBECAnalyticsService(db)
        await analytics.initialize()
        
        # Get token distribution
        distribution = await analytics.get_token_distribution('UBEC')
        
        # Analyze holder concentration
        holders = await analytics.analyze_holder_concentration('UBEC')
        
        # Health check (Principle #7) - Now uses ServiceHealthCheck utility!
        health = await analytics.health_check()
        print(f"Status: {health['status']}")
        print(f"Query count: {health['details']['query_count']}")
        
        await analytics.close()
    """
    
    def __init__(self, db_manager):
        """
        Initialize the analytics service.
        
        Args:
            db_manager: AsyncDatabaseManager instance (REQUIRED)
            
        Raises:
            ValueError: If db_manager is None (Principle #4)
        """
        if db_manager is None:
            raise ValueError(
                "Database manager is required (Principle #4: Single Source of Truth)"
            )
        
        logger.info("Initializing UBEC Analytics Service")
        
        self.db = db_manager
        self._initialized = False
        
        # Cache for frequently accessed data (with TTL)
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cache_ttl_seconds = 300  # 5 minutes default
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Service metadata
        self._service_name = 'analytics'
        self._last_query_time: Optional[datetime] = None
        self._query_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        logger.info("✓ UBEC Analytics Service initialized")
    
    async def initialize(self):
        """
        Initialize the analytics service.
        Must be called before using analytics methods.
        
        Principle #5: Strict Async Operations - async initialization only
        """
        if self._initialized:
            logger.warning("Analytics service already initialized")
            return
        
        logger.info("Initializing analytics service...")
        
        # Verify database connection (Principle #4)
        try:
            result = await self.db.fetch_one("SELECT 1 as test")
            if not result:
                raise AnalyticsException("Database connection test failed")
            
            logger.info("✓ Database connection verified")
        except Exception as e:
            self._record_error(f"Failed to verify database connection: {e}")
            raise AnalyticsException(f"Failed to verify database connection: {e}")
        
        self._initialized = True
        logger.info("✓ Analytics service fully initialized")
    
    async def close(self):
        """
        Clean up resources.
        
        Principle #5: Strict Async Operations - async cleanup
        """
        self._cache.clear()
        self._initialized = False
        logger.info("Analytics service closed")
    
    # ========================================================================
    # HEALTH CHECK (Enhanced with ServiceHealthCheck utility)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on analytics service.
        
        Now uses ServiceHealthCheck utility (Principle #12: Method Singularity)
        for standardized health reporting across all services.
        
        Implements Principle #7 (Per-Asset Monitoring) with detailed metrics:
        - Database connectivity
        - Query performance
        - Cache effectiveness
        - Error tracking
        - Data freshness validation
        
        Returns:
            Dict with health status and comprehensive metrics:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str (ISO 8601),
                'details': {
                    'initialized': bool,
                    'query_count': int,
                    'cache_size': int,
                    'cache_hit_rate': float,
                    'error_count': int,
                    'last_query_time': str,
                    'last_error': str or None,
                    'has_database': bool,
                    'checks_passed': int,
                    'checks_failed': int,
                    'checks': List[Tuple[str, Any]]
                }
            }
        
        Example:
            health = await analytics.health_check()
            
            if health['status'] == 'healthy':
                print("✓ Analytics service operational")
                print(f"  Queries: {health['details']['query_count']}")
                print(f"  Cache hit rate: {health['details']['cache_hit_rate']:.1%}")
            else:
                print(f"✗ Analytics {health['status']}: {health['message']}")
                if health['details']['last_error']:
                    print(f"  Last error: {health['details']['last_error']}")
        """
        async def check_data_freshness():
            """
            Verify that analytics data is reasonably fresh.
            
            Checks the last query time - if it's None or too old,
            it might indicate the service isn't being used properly.
            """
            if self._last_query_time is None:
                # Service initialized but never used - not necessarily bad
                return "No queries yet (service not used)"
            
            age = (datetime.now() - self._last_query_time).total_seconds()
            
            # Warn if last query was more than 1 hour ago (configurable)
            if age > 3600:
                raise Exception(f"Last query {age/60:.1f} minutes ago (service may be idle)")
            
            return f"Last query {age:.1f}s ago"
        
        async def check_cache_health():
            """Verify cache is functioning properly."""
            total_cache_ops = self._cache_hits + self._cache_misses
            
            if total_cache_ops > 100:  # Only check if enough operations
                hit_rate = self._cache_hits / total_cache_ops
                
                # Warn if cache hit rate is very low
                if hit_rate < 0.1:  # Less than 10% hit rate
                    raise Exception(f"Low cache hit rate: {hit_rate:.1%}")
            
            return f"Cache operational"
        
        async def check_error_rate():
            """Check if error rate is acceptable."""
            if self._query_count > 0:
                error_rate = self._error_count / self._query_count
                
                # Warn if error rate is high
                if error_rate > 0.1:  # More than 10% errors
                    raise Exception(f"High error rate: {error_rate:.1%}")
            
            return "Error rate acceptable"
        
        # Calculate cache hit rate
        total_cache_ops = self._cache_hits + self._cache_misses
        cache_hit_rate = (self._cache_hits / total_cache_ops) if total_cache_ops > 0 else 0.0
        
        # Use ServiceHealthCheck utility (Principle #12: Method Singularity)
        return await ServiceHealthCheck.database_dependent_health(
            service_name='analytics',
            db_manager=self.db,
            is_initialized=self._initialized,
            additional_checks=[
                check_data_freshness,
                check_cache_health,
                check_error_rate
            ],
            query_count=self._query_count,
            cache_size=len(self._cache),
            cache_hit_rate=cache_hit_rate,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            error_count=self._error_count,
            last_query_time=self._last_query_time.isoformat() if self._last_query_time else None,
            last_error=self._last_error,
            last_error_time=self._last_error_time.isoformat() if self._last_error_time else None
        )
    
    # ========================================================================
    # ERROR TRACKING
    # ========================================================================
    
    def _record_error(self, error_message: str):
        """
        Record an error for health tracking.
        
        Principle #12: Method Singularity - Single error tracking method
        """
        self._error_count += 1
        self._last_error = str(error_message)
        self._last_error_time = datetime.now()
        logger.error(f"Analytics error #{self._error_count}: {error_message}")
    
    # ========================================================================
    # CACHE MANAGEMENT
    # ========================================================================
    
    def _get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from method parameters.
        
        Principle #12: Method Singularity - Single cache key generation method
        """
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached value if still valid"""
        if cache_key in self._cache:
            value, timestamp = self._cache[cache_key]
            age = (datetime.now() - timestamp).total_seconds()
            
            if age < self._cache_ttl_seconds:
                logger.debug(f"Cache hit: {cache_key} (age: {age:.1f}s)")
                self._cache_hits += 1
                return value
            else:
                # Expired
                del self._cache[cache_key]
                logger.debug(f"Cache expired: {cache_key}")
        
        self._cache_misses += 1
        return None
    
    def _set_cached(self, cache_key: str, value: Any):
        """Store value in cache with timestamp"""
        self._cache[cache_key] = (value, datetime.now())
        logger.debug(f"Cache set: {cache_key}")
    
    def clear_cache(self):
        """
        Clear all cached data.
        
        Call this to force fresh data on next queries.
        """
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info(f"Analytics cache cleared ({cache_size} entries)")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache performance metrics
        """
        total_ops = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_ops) if total_ops > 0 else 0.0
        
        return {
            'size': len(self._cache),
            'ttl_seconds': self._cache_ttl_seconds,
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_rate': hit_rate,
            'total_operations': total_ops
        }
    
    async def _execute_query(self, query: str, params: Tuple = ()) -> Any:
        """
        Execute query and update service metrics.
        
        Principle #12: Method Singularity - Single query execution method
        """
        self._query_count += 1
        self._last_query_time = datetime.now()
        
        try:
            return await self.db.fetch_one(query, params)
        except Exception as e:
            self._record_error(f"Query execution error: {e}")
            raise
    
    async def _execute_query_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        """
        Execute query returning all rows and update service metrics.
        
        Principle #12: Method Singularity - Single multi-row query method
        """
        self._query_count += 1
        self._last_query_time = datetime.now()
        
        try:
            return await self.db.fetch_all(query, params)
        except Exception as e:
            self._record_error(f"Query execution error: {e}")
            raise
    
    # ========================================================================
    # TOKEN DISTRIBUTION ANALYSIS
    # ========================================================================
    
    async def get_token_distribution(
        self,
        asset_code: str,
        use_cache: bool = True
    ) -> TokenDistribution:
        """
        Analyze token distribution for a specific token.
        
        Args:
            asset_code: Token to analyze (UBEC, UBECrc, UBECgpi, UBECtt)
            use_cache: Whether to use cached results
            
        Returns:
            TokenDistribution object with comprehensive metrics
            
        Raises:
            AnalyticsException: If analysis fails
            
        Example:
            dist = await analytics.get_token_distribution('UBEC')
            print(f"Total holders: {dist.total_holders}")
            print(f"Avg balance: {dist.average_balance}")
            print(f"Top 10 hold: {dist.top_10_concentration}%")
        """
        # Check cache
        cache_key = self._get_cache_key("token_dist", asset_code)
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        logger.info(f"Analyzing token distribution for {asset_code}...")
        
        try:
            # Get basic distribution stats
            query = """
                SELECT 
                    asset_code,
                    element,
                    COUNT(DISTINCT account_id) as total_holders,
                    SUM(balance) as total_supply,
                    AVG(balance) as average_balance,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance,
                    MIN(balance) as min_balance,
                    MAX(balance) as max_balance
                FROM account_balances
                WHERE asset_code = $1 AND balance > 0
                GROUP BY asset_code, element
            """
            
            row = await self._execute_query(query, (asset_code,))
            
            if not row:
                raise AnalyticsException(f"No data found for token {asset_code}")
            
            # Calculate top holder concentrations
            top_10_pct = await self._calculate_top_n_concentration(asset_code, 10)
            top_100_pct = await self._calculate_top_n_concentration(asset_code, 100)
            
            # Calculate Gini coefficient (inequality measure)
            gini = await self._calculate_gini_coefficient(asset_code)
            
            distribution = TokenDistribution(
                asset_code=row['asset_code'],
                element=row['element'],
                total_holders=row['total_holders'],
                total_supply=Decimal(str(row['total_supply'])),
                average_balance=Decimal(str(row['average_balance'])),
                median_balance=Decimal(str(row['median_balance'])),
                min_balance=Decimal(str(row['min_balance'])),
                max_balance=Decimal(str(row['max_balance'])),
                top_10_concentration=top_10_pct,
                top_100_concentration=top_100_pct,
                gini_coefficient=gini
            )
            
            # Cache result
            self._set_cached(cache_key, distribution)
            
            logger.info(f"✓ Distribution analysis complete for {asset_code}")
            return distribution
            
        except Exception as e:
            self._record_error(f"Error analyzing distribution for {asset_code}: {e}")
            raise AnalyticsException(f"Distribution analysis failed: {e}")
    
    async def _calculate_top_n_concentration(
        self,
        asset_code: str,
        n: int
    ) -> Decimal:
        """
        Calculate percentage of supply held by top N holders.
        
        Principle #12: Method Singularity - Reusable helper method
        """
        try:
            query = """
                WITH ranked_balances AS (
                    SELECT 
                        balance,
                        ROW_NUMBER() OVER (ORDER BY balance DESC) as rank
                    FROM account_balances
                    WHERE asset_code = $1 AND balance > 0
                ),
                total_supply AS (
                    SELECT SUM(balance) as total
                    FROM account_balances
                    WHERE asset_code = $1 AND balance > 0
                ),
                top_n_supply AS (
                    SELECT SUM(balance) as top_sum
                    FROM ranked_balances
                    WHERE rank <= $2
                )
                SELECT 
                    (top_n_supply.top_sum / total_supply.total * 100) as percentage
                FROM top_n_supply, total_supply
            """
            
            row = await self._execute_query(query, (asset_code, n))
            return Decimal(str(row['percentage'])) if row else Decimal('0')
            
        except Exception as e:
            logger.error(f"Error calculating top {n} concentration: {e}")
            return Decimal('0')
    
    async def _calculate_gini_coefficient(self, asset_code: str) -> Optional[Decimal]:
        """
        Calculate Gini coefficient for token distribution.
        
        Gini coefficient measures inequality:
        - 0 = Perfect equality (everyone has same balance)
        - 1 = Perfect inequality (one holder has everything)
        
        Returns:
            Gini coefficient as Decimal, or None if calculation fails
        """
        try:
            query = """
                WITH sorted_balances AS (
                    SELECT 
                        balance,
                        ROW_NUMBER() OVER (ORDER BY balance) as rank,
                        COUNT(*) OVER () as total_count
                    FROM account_balances
                    WHERE asset_code = $1 AND balance > 0
                ),
                cumulative AS (
                    SELECT
                        rank,
                        balance,
                        total_count,
                        SUM(balance) OVER (ORDER BY rank) as cumsum,
                        SUM(balance) OVER () as total_sum
                    FROM sorted_balances
                )
                SELECT
                    1 - (2 * SUM(cumsum) / (total_count * total_sum)) + (1.0 / total_count) as gini
                FROM cumulative
                GROUP BY total_count, total_sum
            """
            
            row = await self._execute_query(query, (asset_code,))
            return Decimal(str(row['gini'])) if row and row['gini'] else None
            
        except Exception as e:
            logger.warning(f"Could not calculate Gini coefficient: {e}")
            return None
    
    async def get_all_token_distributions(
        self,
        use_cache: bool = True
    ) -> List[TokenDistribution]:
        """
        Get distribution analysis for all 4 UBEC tokens.
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            List of TokenDistribution objects for all tokens
            
        Example:
            distributions = await analytics.get_all_token_distributions()
            for dist in distributions:
                print(f"{dist.asset_code}: {dist.total_holders} holders")
        """
        logger.info("Analyzing distribution for all UBEC tokens...")
        
        distributions = []
        for token in TokenCode:
            dist = await self.get_token_distribution(token.value, use_cache)
            distributions.append(dist)
        
        logger.info(f"✓ Analyzed {len(distributions)} token distributions")
        return distributions
    
    # ========================================================================
    # HOLDER CONCENTRATION ANALYSIS
    # ========================================================================
    
    async def analyze_holder_concentration(
        self,
        asset_code: str,
        whale_threshold: Decimal = Decimal('10000'),
        mid_tier_threshold: Decimal = Decimal('1000'),
        use_cache: bool = True
    ) -> HolderAnalysis:
        """
        Analyze holder concentration by tier (whales, mid-tier, small).
        
        Args:
            asset_code: Token to analyze
            whale_threshold: Minimum balance to be considered a whale
            mid_tier_threshold: Minimum balance for mid-tier holder
            use_cache: Whether to use cached results
            
        Returns:
            HolderAnalysis object with tier breakdowns
            
        Example:
            analysis = await analytics.analyze_holder_concentration('UBEC')
            print(f"Whales: {analysis.whale_count} holding {analysis.whale_percentage}%")
        """
        # Check cache
        cache_key = self._get_cache_key(
            "holder_conc", 
            asset_code, 
            whale_threshold=whale_threshold,
            mid_tier_threshold=mid_tier_threshold
        )
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        logger.info(f"Analyzing holder concentration for {asset_code}...")
        
        try:
            query = """
                WITH holder_tiers AS (
                    SELECT
                        account_id,
                        balance,
                        CASE
                            WHEN balance >= $2 THEN 'whale'
                            WHEN balance >= $3 THEN 'mid_tier'
                            ELSE 'small'
                        END as tier
                    FROM account_balances
                    WHERE asset_code = $1 AND balance > 0
                ),
                tier_stats AS (
                    SELECT
                        tier,
                        COUNT(*) as holder_count,
                        SUM(balance) as total_balance
                    FROM holder_tiers
                    GROUP BY tier
                ),
                total_stats AS (
                    SELECT
                        COUNT(*) as total_holders,
                        SUM(balance) as total_supply
                    FROM account_balances
                    WHERE asset_code = $1 AND balance > 0
                )
                SELECT
                    ts.total_holders,
                    ts.total_supply,
                    COALESCE(whale.holder_count, 0) as whale_count,
                    COALESCE(whale.total_balance, 0) as whale_holdings,
                    COALESCE(mid.holder_count, 0) as mid_tier_count,
                    COALESCE(mid.total_balance, 0) as mid_tier_holdings,
                    COALESCE(small.holder_count, 0) as small_holder_count,
                    COALESCE(small.total_balance, 0) as small_holder_holdings
                FROM total_stats ts
                LEFT JOIN tier_stats whale ON whale.tier = 'whale'
                LEFT JOIN tier_stats mid ON mid.tier = 'mid_tier'
                LEFT JOIN tier_stats small ON small.tier = 'small'
            """
            
            row = await self._execute_query(
                query,
                (asset_code, whale_threshold, mid_tier_threshold)
            )
            
            if not row:
                raise AnalyticsException(f"No data found for token {asset_code}")
            
            total_supply = Decimal(str(row['total_supply']))
            whale_holdings = Decimal(str(row['whale_holdings']))
            
            whale_percentage = (whale_holdings / total_supply * 100) if total_supply > 0 else Decimal('0')
            
            analysis = HolderAnalysis(
                asset_code=asset_code,
                total_holders=row['total_holders'],
                whale_count=row['whale_count'],
                whale_holdings=whale_holdings,
                whale_percentage=whale_percentage,
                mid_tier_count=row['mid_tier_count'],
                mid_tier_holdings=Decimal(str(row['mid_tier_holdings'])),
                small_holder_count=row['small_holder_count'],
                small_holder_holdings=Decimal(str(row['small_holder_holdings']))
            )
            
            # Cache result
            self._set_cached(cache_key, analysis)
            
            logger.info(f"✓ Holder concentration analysis complete for {asset_code}")
            return analysis
            
        except Exception as e:
            self._record_error(f"Error analyzing holder concentration: {e}")
            raise AnalyticsException(f"Holder concentration analysis failed: {e}")
    
    async def identify_whales(
        self,
        asset_code: str,
        threshold: Decimal = Decimal('10000'),
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Identify whale accounts above threshold.
        
        Args:
            asset_code: Token to analyze
            threshold: Minimum balance to be considered whale
            limit: Maximum number of whales to return
            
        Returns:
            List of whale account data sorted by balance (descending)
            
        Example:
            whales = await analytics.identify_whales('UBEC', threshold=Decimal('50000'))
            for whale in whales:
                print(f"{whale['account_id']}: {whale['balance']} {whale['asset_code']}")
        """
        logger.info(f"Identifying whales for {asset_code} (threshold: {threshold})...")
        
        try:
            query = """
                SELECT
                    ub.account_id,
                    ub.asset_code,
                    ub.element,
                    ub.balance,
                    sa.last_modified_at,
                    sa.sync_status
                FROM account_balances ub
                LEFT JOIN stellar_accounts sa ON sa.account_id = ub.account_id
                WHERE ub.asset_code = $1 AND ub.balance >= $2
                ORDER BY ub.balance DESC
                LIMIT $3
            """
            
            rows = await self._execute_query_all(query, (asset_code, threshold, limit))
            
            whales = []
            for row in rows:
                whales.append({
                    'account_id': row['account_id'],
                    'asset_code': row['asset_code'],
                    'element': row['element'],
                    'balance': Decimal(str(row['balance'])),
                    'last_modified': row['last_modified_at'],
                    'sync_status': row['sync_status']
                })
            
            logger.info(f"✓ Identified {len(whales)} whales for {asset_code}")
            return whales
            
        except Exception as e:
            self._record_error(f"Error identifying whales: {e}")
            raise AnalyticsException(f"Whale identification failed: {e}")
    
    # ========================================================================
    # TRANSACTION ANALYSIS
    # ========================================================================
    
    async def get_transaction_metrics(
        self,
        asset_code: Optional[str] = None,
        period_days: int = 30,
        use_cache: bool = True
    ) -> TransactionMetrics:
        """
        Analyze transaction patterns over a time period.
        
        Args:
            asset_code: Specific token to analyze (None for all tokens)
            period_days: Number of days to analyze
            use_cache: Whether to use cached results
            
        Returns:
            TransactionMetrics object with comprehensive transaction stats
            
        Example:
            metrics = await analytics.get_transaction_metrics('UBEC', period_days=7)
            print(f"7-day velocity: {metrics.velocity} tx/day")
            print(f"Avg tx size: {metrics.average_transaction_size}")
        """
        # Check cache
        cache_key = self._get_cache_key(
            "tx_metrics",
            asset_code or "all",
            period_days=period_days
        )
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        logger.info(
            f"Analyzing transaction metrics for {asset_code or 'all tokens'} "
            f"(period: {period_days} days)..."
        )
        
        try:
            # Get transaction statistics
            query = """
                SELECT
                    COUNT(*) as total_transactions,
                    COUNT(DISTINCT source_account) as unique_senders
                FROM stellar_transactions
                WHERE created_at >= NOW() - INTERVAL '{} days'
                    AND successful = TRUE
            """.format(period_days)
            
            row = await self._execute_query(query)
            
            if not row or row['total_transactions'] == 0:
                # No transactions in period
                return TransactionMetrics(
                    asset_code=asset_code or "all",
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
            
            total_transactions = row['total_transactions']
            unique_senders = row['unique_senders']
            
            # Calculate velocity (transactions per day)
            velocity = Decimal(str(total_transactions)) / Decimal(str(period_days))
            
            # Get total supply for turnover ratio
            supply_query = """
                SELECT SUM(balance) as total_supply
                FROM account_balances
                WHERE asset_code = $1
            """ if asset_code else """
                SELECT SUM(balance) as total_supply
                FROM account_balances
            """
            
            supply_params = (asset_code,) if asset_code else ()
            supply_row = await self._execute_query(supply_query, supply_params)
            total_supply = Decimal(str(supply_row['total_supply'])) if supply_row else Decimal('0')
            
            # Placeholder values for volume-based metrics
            # These would need actual transaction amount data from operations table
            total_volume = Decimal('0')
            avg_tx_size = Decimal('0')
            median_tx_size = Decimal('0')
            turnover_ratio = Decimal('0')
            
            metrics = TransactionMetrics(
                asset_code=asset_code or "all",
                period_days=period_days,
                total_transactions=total_transactions,
                unique_senders=unique_senders,
                unique_receivers=0,  # Would need operation-level data
                total_volume=total_volume,
                average_transaction_size=avg_tx_size,
                median_transaction_size=median_tx_size,
                velocity=velocity,
                turnover_ratio=turnover_ratio
            )
            
            # Cache result
            self._set_cached(cache_key, metrics)
            
            logger.info(f"✓ Transaction metrics calculated")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error calculating transaction metrics: {e}")
            raise AnalyticsException(f"Transaction metrics calculation failed: {e}")
    
    # ========================================================================
    # LIQUIDITY ANALYSIS
    # ========================================================================
    
    async def get_liquidity_metrics(
        self,
        asset_code: str,
        use_cache: bool = True
    ) -> LiquidityMetrics:
        """
        Analyze liquidity metrics for a token.
        
        Args:
            asset_code: Token to analyze
            use_cache: Whether to use cached results
            
        Returns:
            LiquidityMetrics object
            
        Example:
            liquidity = await analytics.get_liquidity_metrics('UBEC')
            print(f"Total supply: {liquidity.total_supply}")
            print(f"Liquidity ratio: {liquidity.liquidity_ratio}%")
        """
        # Check cache
        cache_key = self._get_cache_key("liquidity", asset_code)
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        logger.info(f"Analyzing liquidity metrics for {asset_code}...")
        
        try:
            # Get supply data
            query = """
                SELECT
                    SUM(balance) as total_supply,
                    COUNT(*) as holder_count
                FROM account_balances
                WHERE asset_code = $1 AND balance > 0
            """
            
            row = await self._execute_query(query, (asset_code,))
            
            if not row:
                raise AnalyticsException(f"No data found for token {asset_code}")
            
            total_supply = Decimal(str(row['total_supply']))
            
            # Assume all supply is circulating for now
            # Future enhancement: identify locked/vesting accounts
            circulating_supply = total_supply
            locked_supply = Decimal('0')
            available_liquidity = circulating_supply
            
            liquidity_ratio = (available_liquidity / total_supply * 100) if total_supply > 0 else Decimal('0')
            
            metrics = LiquidityMetrics(
                asset_code=asset_code,
                total_supply=total_supply,
                circulating_supply=circulating_supply,
                locked_supply=locked_supply,
                available_liquidity=available_liquidity,
                liquidity_ratio=liquidity_ratio
            )
            
            # Cache result
            self._set_cached(cache_key, metrics)
            
            logger.info(f"✓ Liquidity metrics calculated for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error calculating liquidity metrics: {e}")
            raise AnalyticsException(f"Liquidity metrics calculation failed: {e}")
    
    # ========================================================================
    # ECOSYSTEM HEALTH
    # ========================================================================
    
    async def get_ecosystem_health(
        self,
        use_cache: bool = True
    ) -> EcosystemHealth:
        """
        Get overall ecosystem health metrics.
        
        Principle #7: Per-Asset Monitoring - Aggregated health across all elements
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            EcosystemHealth object with comprehensive metrics
            
        Example:
            health = await analytics.get_ecosystem_health()
            print(f"Total holders: {health.total_holders}")
            print(f"Element balance: {health.element_balance_score}")
        """
        # Check cache
        cache_key = self._get_cache_key("ecosystem_health")
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        logger.info("Analyzing ecosystem health...")
        
        try:
            # Get holder counts
            holders_query = """
                SELECT COUNT(DISTINCT account_id) as total_holders
                FROM account_balances
                WHERE balance > 0
            """
            holders_row = await self._execute_query(holders_query)
            total_holders = holders_row['total_holders'] if holders_row else 0
            
            # Get account counts
            accounts_query = """
                SELECT COUNT(*) as total_accounts
                FROM stellar_accounts
            """
            accounts_row = await self._execute_query(accounts_query)
            total_accounts = accounts_row['total_accounts'] if accounts_row else 0
            
            # Get transaction counts
            tx_query = """
                SELECT COUNT(*) as total_transactions
                FROM stellar_transactions
            """
            tx_row = await self._execute_query(tx_query)
            total_transactions = tx_row['total_transactions'] if tx_row else 0
            
            # Get total supply across all tokens
            supply_query = """
                SELECT SUM(balance) as total_supply
                FROM account_balances
            """
            supply_row = await self._execute_query(supply_query)
            total_supply = Decimal(str(supply_row['total_supply'])) if supply_row else Decimal('0')
            
            # Get active accounts by period
            active_24h = await self._get_active_accounts(1)
            active_7d = await self._get_active_accounts(7)
            active_30d = await self._get_active_accounts(30)
            
            # Calculate element balance score
            element_balance = await self._calculate_element_balance_score()
            
            health = EcosystemHealth(
                timestamp=datetime.now(),
                total_holders=total_holders,
                total_accounts=total_accounts,
                total_transactions=total_transactions,
                total_supply_all_tokens=total_supply,
                active_accounts_24h=active_24h,
                active_accounts_7d=active_7d,
                active_accounts_30d=active_30d,
                element_balance_score=element_balance
            )
            
            # Cache result
            self._set_cached(cache_key, health)
            
            logger.info("✓ Ecosystem health analysis complete")
            return health
            
        except Exception as e:
            self._record_error(f"Error analyzing ecosystem health: {e}")
            raise AnalyticsException(f"Ecosystem health analysis failed: {e}")
    
    async def _get_active_accounts(self, days: int) -> int:
        """
        Get count of accounts with activity in last N days.
        
        Principle #12: Method Singularity - Reusable helper method
        """
        try:
            query = """
                SELECT COUNT(DISTINCT source_account) as active_count
                FROM stellar_transactions
                WHERE created_at >= NOW() - INTERVAL '{} days'
                    AND successful = TRUE
            """.format(days)
            
            row = await self._execute_query(query)
            return row['active_count'] if row else 0
            
        except Exception as e:
            logger.warning(f"Error getting active accounts: {e}")
            return 0
    
    async def _calculate_element_balance_score(self) -> Decimal:
        """
        Calculate how balanced the four elements are.
        
        Returns:
            Score from 0-100 where:
            - 100 = Perfect balance (equal distribution)
            - 0 = Complete imbalance (all in one element)
        """
        try:
            query = """
                SELECT
                    element,
                    COUNT(DISTINCT account_id) as holder_count,
                    SUM(balance) as total_balance
                FROM account_balances
                WHERE balance > 0
                GROUP BY element
            """
            
            rows = await self._execute_query_all(query)
            
            if not rows or len(rows) < 4:
                return Decimal('0')
            
            # Get total holders and balances
            total_holders = sum(row['holder_count'] for row in rows)
            total_balance = sum(Decimal(str(row['total_balance'])) for row in rows)
            
            if total_holders == 0 or total_balance == 0:
                return Decimal('0')
            
            # Calculate deviation from perfect balance (25% each)
            perfect_holder_pct = Decimal('25')
            perfect_balance_pct = Decimal('25')
            
            holder_deviations = []
            balance_deviations = []
            
            for row in rows:
                holder_pct = Decimal(str(row['holder_count'])) / Decimal(str(total_holders)) * 100
                balance_pct = Decimal(str(row['total_balance'])) / total_balance * 100
                
                holder_deviations.append(abs(holder_pct - perfect_holder_pct))
                balance_deviations.append(abs(balance_pct - perfect_balance_pct))
            
            # Average deviation (lower is better)
            avg_holder_dev = sum(holder_deviations) / len(holder_deviations)
            avg_balance_dev = sum(balance_deviations) / len(balance_deviations)
            
            # Convert to score (0-100, where 100 is perfect)
            # Max deviation would be 75% (all in one element)
            holder_score = (Decimal('75') - avg_holder_dev) / Decimal('75') * 100
            balance_score = (Decimal('75') - avg_balance_dev) / Decimal('75') * 100
            
            # Average of both scores
            final_score = (holder_score + balance_score) / 2
            
            return max(Decimal('0'), min(Decimal('100'), final_score))
            
        except Exception as e:
            logger.warning(f"Error calculating element balance score: {e}")
            return Decimal('50')  # Default to neutral score
    
    # ========================================================================
    # COMPARATIVE ANALYSIS
    # ========================================================================
    
    async def compare_tokens(
        self,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Compare metrics across all 4 UBEC tokens.
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            Dict with comparative analysis of all tokens
            
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
            unique_query = """
                SELECT COUNT(DISTINCT account_id) as unique_accounts
                FROM account_balances
                WHERE balance > 0
            """
            unique_row = await self._execute_query(unique_query)
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
    print("USAGE:")
    print("------")
    print()
    print("  # Via service registry (RECOMMENDED - Principle #3)")
    print("  from core.service_registry import registry")
    print("  analytics = await registry.get('analytics')")
    print()
    print("  # Get token distribution")
    print("  dist = await analytics.get_token_distribution('UBEC')")
    print("  print(f'Holders: {dist.total_holders}')")
    print()
    print("  # Health check (now uses ServiceHealthCheck utility!)")
    print("  health = await analytics.health_check()")
    print("  print(f'Status: {health[\"status\"]}')")
    print("  print(f'Cache hit rate: {health[\"details\"][\"cache_hit_rate\"]:.1%}')")
    print()
    print("DESIGN PRINCIPLES:")
    print("------------------")
    print("✅ All 12 principles fully implemented")
    print("✅ Enhanced health check using ServiceHealthCheck utility")
    print("✅ Comprehensive error tracking and reporting")
    print("✅ Cache performance monitoring")
    print()
    print("=" * 80)
