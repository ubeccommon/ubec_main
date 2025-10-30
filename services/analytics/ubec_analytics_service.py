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
Version: 3.3.0 (Operations Table Fix - Proper Transaction Metrics)
Date: October 26, 2025

Changes from v3.2:
- ✅ FIXED: Changed transaction metrics query from stellar_transactions to stellar_operations
- ✅ FIXED: Use from_account/to_account instead of non-existent destination column
- ✅ FIXED: Added asset_code filter to ensure token-specific metrics
- ✅ FIXED: Proper grouping by transaction_hash for transaction counts
- ✅ IMPROVED: More accurate velocity and volume calculations per token
- ✅ VERIFIED: All queries now reference only existing columns
- Maintained all CLI command methods and health checking
- Full compliance with all 12 design principles
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
        
        # CLI command interface
        result = await analytics.analyze_token_distribution()  # All tokens
        result = await analytics.calculate_velocity()  # Velocity metrics
        result = await analytics.calculate_concentration()  # Concentration metrics
        
        # Direct analysis methods
        dist = await analytics.get_token_distribution('UBEC')
        holders = await analytics.analyze_holder_concentration('UBEC')
        
        # Health check (Principle #7) - Uses ServiceHealthCheck utility!
        health = await analytics.health_check()
        print(f"Status: {health['status']}")
        print(f"Query count: {health['details']['query_count']}")
        
        await analytics.close()
    """
    
    def __init__(self, db_manager):
        """
        Initialize analytics service.
        
        Args:
            db_manager: Database manager instance for queries
        """
        self.db_manager = db_manager
        self._initialized = False
        
        # Cache for frequently accessed data (Principle #4: Single Source of Truth)
        # Cache points to database as source, doesn't duplicate data
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)  # 5 minute cache
        
        # Query tracking for health checks (Principle #7)
        self._query_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        self._last_query_time: Optional[datetime] = None
        self._cache_hits = 0
        self._cache_misses = 0
        
        logger.info("UBEC Analytics Service created (awaiting initialization)")
    
    # ========================================================================
    # LIFECYCLE MANAGEMENT (Principles #5, #6)
    # ========================================================================
    
    async def initialize(self) -> None:
        """
        Initialize analytics service.
        
        Principle #5: Async initialization
        Principle #6: No sync fallbacks
        """
        if self._initialized:
            logger.warning("Analytics service already initialized")
            return
        
        logger.info("Initializing UBEC Analytics Service")
        
        try:
            # Verify database connectivity
            test_query = "SELECT 1 as test"
            result = await self.db_manager.fetch_one(test_query, ())
            
            if not result or result['test'] != 1:
                raise AnalyticsException("Database connectivity test failed")
            
            self._initialized = True
            logger.info("✓ UBEC Analytics Service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics service: {e}")
            raise AnalyticsException(f"Initialization failed: {e}")
    
    async def close(self) -> None:
        """
        Close analytics service and cleanup resources.
        
        Principle #5: Async cleanup
        """
        if not self._initialized:
            return
        
        logger.info("Analytics service closed")
        self._initialized = False
        self._cache.clear()
    
    # ========================================================================
    # HEALTH CHECK (Principle #7: Per-Asset Monitoring)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for analytics service.
        
        Principle #7: Per-Asset Monitoring with health validation
        Uses ServiceHealthCheck utility (Principle #12: Method Singularity)
        """
        # Additional validation checks
        additional_checks = []
        
        def check_error_count():
            if self._error_count > 10:
                raise ValueError(f"High error count: {self._error_count}")
            return True
        
        def check_recent_errors():
            if self._last_error_time:
                time_since_error = datetime.now() - self._last_error_time
                if time_since_error < timedelta(minutes=5):
                    raise ValueError("Recent errors detected")
            return True
        
        async def check_database_query():
            test_query = "SELECT COUNT(*) as count FROM ubec_balances WHERE balance > 0"
            result = await self.db_manager.fetch_one(test_query, ())
            if result and result.get('count', 0) > 0:
                return f"Database responsive ({result['count']} active balances)"
            raise ValueError("No active balances found")
        
        additional_checks.extend([check_error_count, check_recent_errors, check_database_query])
        
        return await ServiceHealthCheck.database_dependent_health(
            service_name='ubec_analytics_service',
            db_manager=self.db_manager,
            is_initialized=self._initialized,
            additional_checks=additional_checks,
            query_count=self._query_count,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time.isoformat() if self._last_error_time else None,
            last_query_time=self._last_query_time.isoformat() if self._last_query_time else None,
            cache_size=len(self._cache),
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            cache_hit_rate=(
                self._cache_hits / (self._cache_hits + self._cache_misses)
                if (self._cache_hits + self._cache_misses) > 0 else 0
            )
        )

    # ========================================================================
    # CLI COMMAND INTERFACE METHODS
    # ========================================================================
    
    async def analyze_token_distribution(
        self,
        token_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        CLI command: Analyze token distribution.
        
        Called by main.py with: python main.py analytics --analysis-type distribution
        
        Args:
            token_code: Optional specific token, otherwise analyzes all tokens
            
        Returns:
            Dict with distribution analysis for CLI output
        """
        logger.info(f"Analyzing token distribution{f' for {token_code}' if token_code else ' (all tokens)'}...")
        
        try:
            if token_code:
                # Single token analysis
                dist = await self.get_token_distribution(token_code)
                result = {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'data': {
                        'analysis_type': 'distribution',
                        'token': token_code,
                        'distribution': asdict(dist)
                    }
                }
            else:
                # All tokens analysis
                distributions = await self.get_all_token_distributions()
                result = {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'data': {
                        'analysis_type': 'distribution',
                        'tokens': [asdict(d) for d in distributions],
                        'summary': {
                            'total_tokens': len(distributions),
                            'total_holders': sum(d.total_holders for d in distributions),
                            'total_supply': float(sum(d.total_supply for d in distributions))
                        }
                    }
                }
            
            logger.info("✓ Distribution analysis complete")
            return result
            
        except Exception as e:
            self._record_error(f"Distribution analysis failed: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def calculate_velocity(
        self,
        period_days: int = 30,
        token_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        CLI command: Calculate velocity metrics.
        
        Called by main.py with: python main.py analytics --analysis-type velocity
        
        Args:
            period_days: Analysis period (default 30 days)
            token_code: Optional specific token, otherwise analyzes all tokens
            
        Returns:
            Dict with velocity metrics for CLI output
        """
        logger.info(f"Calculating velocity metrics (period: {period_days} days)...")
        
        try:
            velocity_metrics = []
            
            if token_code:
                tokens = [TokenCode(token_code)]
            else:
                tokens = list(TokenCode)
            
            for token in tokens:
                try:
                    metrics = await self.get_transaction_metrics(token.value, period_days)
                    velocity_metrics.append({
                        'token': token.value,
                        'period_days': period_days,
                        'total_transactions': metrics.total_transactions,
                        'velocity': float(metrics.velocity),
                        'total_volume': float(metrics.total_volume),
                        'unique_senders': metrics.unique_senders,
                        'unique_receivers': metrics.unique_receivers
                    })
                except Exception as e:
                    logger.warning(f"Could not get velocity for {token.value}: {e}")
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'analysis_type': 'velocity',
                    'timestamp': datetime.now().isoformat(),
                    'period_days': period_days,
                    'velocity_metrics': velocity_metrics,
                    'summary': {
                        'total_transactions': sum(m['total_transactions'] for m in velocity_metrics),
                        'average_velocity': sum(m['velocity'] for m in velocity_metrics) / len(velocity_metrics) if velocity_metrics else 0,
                        'total_unique_senders': sum(m['unique_senders'] for m in velocity_metrics)
                    }
                }
            }
            
            logger.info(f"✓ Velocity calculation complete for {len(velocity_metrics)} tokens")
            return result
            
        except Exception as e:
            self._record_error(f"Velocity calculation failed: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def calculate_concentration(
        self,
        token_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        CLI command: Calculate holder concentration metrics.
        
        Called by main.py with: python main.py analytics --analysis-type concentration
        
        Args:
            token_code: Optional specific token, otherwise analyzes all tokens
            
        Returns:
            Dict with concentration metrics for CLI output
        """
        logger.info(f"Calculating concentration metrics{f' for {token_code}' if token_code else ' (all tokens)'}...")
        
        try:
            concentration_data = []
            
            if token_code:
                tokens = [TokenCode(token_code)]
            else:
                tokens = list(TokenCode)
            
            for token in tokens:
                try:
                    holder_analysis = await self.analyze_holder_concentration(token.value)
                    concentration_data.append({
                        'token': token.value,
                        'total_holders': holder_analysis.total_holders,
                        'whale_count': holder_analysis.whale_count,
                        'whale_percentage': float(holder_analysis.whale_percentage),
                        'mid_tier_count': holder_analysis.mid_tier_count,
                        'small_holder_count': holder_analysis.small_holder_count
                    })
                except Exception as e:
                    logger.warning(f"Could not get concentration for {token.value}: {e}")
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'analysis_type': 'concentration',
                    'concentration_metrics': concentration_data,
                    'summary': {
                        'total_holders': sum(c['total_holders'] for c in concentration_data),
                        'total_whales': sum(c['whale_count'] for c in concentration_data),
                        'average_whale_percentage': sum(c['whale_percentage'] for c in concentration_data) / len(concentration_data) if concentration_data else 0
                    }
                }
            }
            
            logger.info(f"✓ Concentration calculation complete for {len(concentration_data)} tokens")
            return result
            
        except Exception as e:
            self._record_error(f"Concentration calculation failed: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    # ========================================================================
    # INTERNAL HELPER METHODS
    # ========================================================================
    
    async def _execute_query(
        self,
        query: str,
        params: tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a query and return single row.
        
        Principle #12: Method Singularity - centralized query execution
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Single row as dict, or None
        """
        try:
            self._query_count += 1
            self._last_query_time = datetime.now()
            
            result = await self.db_manager.fetch_one(query, params)
            return result
            
        except Exception as e:
            self._record_error(f"Query execution error: {e}")
            raise
    
    async def _execute_query_all(
        self,
        query: str,
        params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return all rows.
        
        Principle #12: Method Singularity - centralized query execution
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of rows as dicts
        """
        try:
            self._query_count += 1
            self._last_query_time = datetime.now()
            
            results = await self.db_manager.fetch_all(query, params)
            return results
            
        except Exception as e:
            self._record_error(f"Query execution error: {e}")
            raise
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_ttl:
                self._cache_hits += 1
                return value
            else:
                # Expired, remove from cache
                del self._cache[key]
        
        self._cache_misses += 1
        return None
    
    def _set_cached(self, key: str, value: Any) -> None:
        """Store value in cache with timestamp."""
        self._cache[key] = (value, datetime.now())
    
    def _record_error(self, error_msg: str) -> None:
        """Record error for health monitoring."""
        self._error_count += 1
        self._last_error = error_msg
        self._last_error_time = datetime.now()
        logger.error(f"Analytics error #{self._error_count}: {error_msg}")
    
    # ========================================================================
    # TOKEN DISTRIBUTION ANALYSIS
    # ========================================================================
    
    async def get_token_distribution(
        self,
        asset_code: str,
        use_cache: bool = True
    ) -> TokenDistribution:
        """
        Get comprehensive distribution metrics for a token.
        
        Args:
            asset_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            use_cache: Whether to use cached results
            
        Returns:
            TokenDistribution object with all metrics
            
        Example:
            dist = await analytics.get_token_distribution('UBEC')
            print(f"Holders: {dist.total_holders}")
            print(f"Supply: {dist.total_supply}")
            print(f"Top 10 hold: {dist.top_10_concentration}%")
        """
        cache_key = f"distribution_{asset_code}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Validate token code
            if asset_code not in [t.value for t in TokenCode]:
                raise AnalyticsException(f"Invalid token code: {asset_code}")
            
            # Get element for this token
            element = TOKEN_ELEMENT_MAP.get(TokenCode(asset_code), ElementType.AIR).value
            
            # FIXED: Query ubec_balances table (has element column)
            query = """
                SELECT 
                    COUNT(DISTINCT account_id) as total_holders,
                    COALESCE(SUM(balance), 0) as total_supply,
                    COALESCE(AVG(balance), 0) as average_balance,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance,
                    COALESCE(MIN(balance), 0) as min_balance,
                    COALESCE(MAX(balance), 0) as max_balance
                FROM ubec_balances
                WHERE token_code::text = $1
                AND balance > 0
            """
            
            row = await self._execute_query(query, (asset_code,))
            
            if not row:
                raise AnalyticsException(f"No distribution data found for {asset_code}")
            
            # Calculate concentration metrics
            top_10 = await self._calculate_top_n_concentration(asset_code, 10)
            top_100 = await self._calculate_top_n_concentration(asset_code, 100)
            gini = await self._calculate_gini_coefficient(asset_code)
            
            distribution = TokenDistribution(
                asset_code=asset_code,
                element=element,
                total_holders=row['total_holders'],
                total_supply=Decimal(str(row['total_supply'])),
                average_balance=Decimal(str(row['average_balance'])),
                median_balance=Decimal(str(row['median_balance'] or 0)),
                min_balance=Decimal(str(row['min_balance'])),
                max_balance=Decimal(str(row['max_balance'])),
                top_10_concentration=top_10,
                top_100_concentration=top_100,
                gini_coefficient=gini
            )
            
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
        
        Args:
            asset_code: Token code
            n: Number of top holders
            
        Returns:
            Percentage as Decimal
        """
        try:
            # FIXED: Use ubec_balances table
            query = """
                WITH top_n_supply AS (
                    SELECT COALESCE(SUM(balance), 0) as top_supply
                    FROM (
                        SELECT balance
                        FROM ubec_balances
                        WHERE token_code::text = $1 AND balance > 0
                        ORDER BY balance DESC
                        LIMIT $2
                    ) top_n
                ),
                total_supply AS (
                    SELECT COALESCE(SUM(balance), 0) as total
                    FROM ubec_balances
                    WHERE token_code::text = $1 AND balance > 0
                )
                SELECT 
                    CASE 
                        WHEN total_supply.total > 0 
                        THEN (top_n_supply.top_supply / total_supply.total) * 100
                        ELSE 0
                    END as percentage
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
            # FIXED: Use ubec_balances table
            query = """
                WITH sorted_balances AS (
                    SELECT 
                        balance,
                        ROW_NUMBER() OVER (ORDER BY balance) as rank,
                        COUNT(*) OVER () as total_count
                    FROM ubec_balances
                    WHERE token_code::text = $1 AND balance > 0
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
        Get distribution analysis for ALL UBEC tokens.
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            List of TokenDistribution objects for all 4 tokens
            
        Example:
            distributions = await analytics.get_all_token_distributions()
            for dist in distributions:
                print(f"{dist.asset_code}: {dist.total_holders} holders")
        """
        logger.info("Fetching distributions for all UBEC tokens...")
        
        distributions = []
        for token in TokenCode:
            try:
                dist = await self.get_token_distribution(token.value, use_cache)
                distributions.append(dist)
            except Exception as e:
                logger.warning(f"Could not get distribution for {token.value}: {e}")
        
        logger.info(f"✓ Retrieved {len(distributions)} token distributions")
        return distributions
    
    # ========================================================================
    # HOLDER CONCENTRATION ANALYSIS
    # ========================================================================
    
    async def analyze_holder_concentration(
        self,
        asset_code: str,
        whale_threshold: Optional[Decimal] = None,
        use_cache: bool = True
    ) -> HolderAnalysis:
        """
        Analyze holder concentration and identify whales.
        
        Args:
            asset_code: Token code
            whale_threshold: Balance threshold for whale classification (auto if None)
            use_cache: Whether to use cached results
            
        Returns:
            HolderAnalysis object
            
        Example:
            analysis = await analytics.analyze_holder_concentration('UBEC')
            print(f"Whales: {analysis.whale_count}")
            print(f"Whale holdings: {analysis.whale_percentage}%")
        """
        cache_key = f"concentration_{asset_code}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Get distribution first to determine threshold
            dist = await self.get_token_distribution(asset_code, use_cache)
            
            # Auto-calculate whale threshold if not provided
            # Whales = holders with > 1% of total supply
            if whale_threshold is None:
                whale_threshold = dist.total_supply * Decimal('0.01')
            
            # FIXED: Use ubec_balances table
            # Define tier thresholds
            mid_tier_threshold = whale_threshold / Decimal('10')  # 0.1% of supply
            
            # Get holder categories
            query = """
                WITH holder_tiers AS (
                    SELECT
                        account_id,
                        balance,
                        CASE
                            WHEN balance >= $2 THEN 'whale'
                            WHEN balance >= $3 THEN 'mid'
                            ELSE 'small'
                        END as tier
                    FROM ubec_balances
                    WHERE token_code::text = $1
                    AND balance > 0
                )
                SELECT
                    tier,
                    COUNT(*) as holder_count,
                    COALESCE(SUM(balance), 0) as total_holdings
                FROM holder_tiers
                GROUP BY tier
            """
            
            rows = await self._execute_query_all(
                query,
                (asset_code, float(whale_threshold), float(mid_tier_threshold))
            )
            
            # Initialize counters
            whale_count = 0
            whale_holdings = Decimal('0')
            mid_count = 0
            mid_holdings = Decimal('0')
            small_count = 0
            small_holdings = Decimal('0')
            
            # Process results
            for row in rows:
                tier = row['tier']
                count = row['holder_count']
                holdings = Decimal(str(row['total_holdings']))
                
                if tier == 'whale':
                    whale_count = count
                    whale_holdings = holdings
                elif tier == 'mid':
                    mid_count = count
                    mid_holdings = holdings
                else:
                    small_count = count
                    small_holdings = holdings
            
            # Calculate whale percentage
            whale_pct = (whale_holdings / dist.total_supply * 100) if dist.total_supply > 0 else Decimal('0')
            
            analysis = HolderAnalysis(
                asset_code=asset_code,
                total_holders=dist.total_holders,
                whale_count=whale_count,
                whale_holdings=whale_holdings,
                whale_percentage=whale_pct,
                mid_tier_count=mid_count,
                mid_tier_holdings=mid_holdings,
                small_holder_count=small_count,
                small_holder_holdings=small_holdings
            )
            
            self._set_cached(cache_key, analysis)
            
            logger.info(f"✓ Holder concentration analysis complete for {asset_code}")
            return analysis
            
        except Exception as e:
            self._record_error(f"Error analyzing holder concentration: {e}")
            raise AnalyticsException(f"Holder analysis failed: {e}")
    
    # ========================================================================
    # TRANSACTION METRICS
    # ========================================================================
    
    async def get_transaction_metrics(
        self,
        asset_code: str,
        period_days: int = 30,
        use_cache: bool = True
    ) -> TransactionMetrics:
        """
        Get transaction metrics for a token over a specified period.
        
        Args:
            asset_code: Token code
            period_days: Analysis period in days
            use_cache: Whether to use cached results
            
        Returns:
            TransactionMetrics object
            
        Example:
            metrics = await analytics.get_transaction_metrics('UBEC', period_days=7)
            print(f"7-day velocity: {metrics.velocity} tx/day")
        """
        cache_key = f"tx_metrics_{asset_code}_{period_days}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
            # FIXED: Query stellar_operations table (has amount, from_account, to_account, asset_code)
            # Group by transaction_hash to get transaction-level metrics
            query = """
                SELECT 
                    COUNT(DISTINCT transaction_hash) as total_transactions,
                    COUNT(DISTINCT COALESCE(from_account, source_account)) as unique_senders,
                    COUNT(DISTINCT to_account) as unique_receivers,
                    COALESCE(SUM(amount::numeric), 0) as total_volume,
                    COALESCE(AVG(amount::numeric), 0) as avg_transaction_size,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount::numeric) as median_transaction_size
                FROM stellar_operations
                WHERE created_at >= $1
                AND asset_code::text = $2
                AND amount IS NOT NULL
                AND amount > 0
            """
            
            row = await self._execute_query(query, (cutoff_date, asset_code))
            
            if not row:
                raise AnalyticsException(f"No transaction data for {asset_code}")
            
            # Get total supply for turnover calculation
            dist = await self.get_token_distribution(asset_code, use_cache)
            
            # Calculate velocity (transactions per day)
            velocity = Decimal(str(row['total_transactions'])) / Decimal(str(period_days))
            
            # Calculate turnover ratio (volume / supply)
            total_volume = Decimal(str(row['total_volume']))
            turnover = (total_volume / dist.total_supply) if dist.total_supply > 0 else Decimal('0')
            
            metrics = TransactionMetrics(
                asset_code=asset_code,
                period_days=period_days,
                total_transactions=row['total_transactions'],
                unique_senders=row['unique_senders'],
                unique_receivers=row['unique_receivers'],
                total_volume=total_volume,
                average_transaction_size=Decimal(str(row['avg_transaction_size'])),
                median_transaction_size=Decimal(str(row['median_transaction_size'] or 0)),
                velocity=velocity,
                turnover_ratio=turnover
            )
            
            self._set_cached(cache_key, metrics)
            
            logger.info(f"✓ Transaction metrics complete for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error getting transaction metrics: {e}")
            raise AnalyticsException(f"Transaction metrics failed: {e}")
    
    # ========================================================================
    # LIQUIDITY ANALYSIS
    # ========================================================================
    
    async def get_liquidity_metrics(
        self,
        asset_code: str,
        use_cache: bool = True
    ) -> LiquidityMetrics:
        """
        Get liquidity metrics for a token.
        
        Args:
            asset_code: Token code
            use_cache: Whether to use cached results
            
        Returns:
            LiquidityMetrics object
            
        Example:
            liquidity = await analytics.get_liquidity_metrics('UBEC')
            print(f"Liquidity ratio: {liquidity.liquidity_ratio}%")
        """
        cache_key = f"liquidity_{asset_code}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Get distribution first
            dist = await self.get_token_distribution(asset_code, use_cache)
            
            # FIXED: Query locked/administration accounts from ubec_balances
            # Administration and stewardship accounts are considered "locked"
            query = """
                SELECT 
                    COALESCE(SUM(balance), 0) as locked_supply
                FROM ubec_balances
                WHERE token_code::text = $1
                AND distribution_category IN ('administration', 'stewardship')
            """
            
            row = await self._execute_query(query, (asset_code,))
            locked = Decimal(str(row['locked_supply'])) if row else Decimal('0')
            
            # Calculate metrics
            circulating = dist.total_supply - locked
            available = circulating  # Simplified - could be refined
            liquidity_ratio = (available / dist.total_supply * 100) if dist.total_supply > 0 else Decimal('0')
            
            metrics = LiquidityMetrics(
                asset_code=asset_code,
                total_supply=dist.total_supply,
                circulating_supply=circulating,
                locked_supply=locked,
                available_liquidity=available,
                liquidity_ratio=liquidity_ratio
            )
            
            self._set_cached(cache_key, metrics)
            
            logger.info(f"✓ Liquidity metrics complete for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error getting liquidity metrics: {e}")
            raise AnalyticsException(f"Liquidity analysis failed: {e}")
    
    # ========================================================================
    # ECOSYSTEM HEALTH
    # ========================================================================
    
    async def get_ecosystem_health(
        self,
        use_cache: bool = True
    ) -> EcosystemHealth:
        """
        Get overall ecosystem health metrics.
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            EcosystemHealth object
            
        Example:
            health = await analytics.get_ecosystem_health()
            print(f"Active accounts (24h): {health.active_accounts_24h}")
            print(f"Element balance score: {health.element_balance_score}/100")
        """
        cache_key = "ecosystem_health"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Get total unique holders across all tokens
            holders_query = """
                SELECT COUNT(DISTINCT account_id) as total_holders
                FROM ubec_balances
                WHERE balance > 0
            """
            holders_row = await self._execute_query(holders_query)
            total_holders = holders_row['total_holders'] if holders_row else 0
            
            # Get total accounts (all Stellar accounts we track)
            accounts_query = """
                SELECT COUNT(*) as total_accounts
                FROM stellar_accounts
            """
            accounts_row = await self._execute_query(accounts_query)
            total_accounts = accounts_row['total_accounts'] if accounts_row else 0
            
            # Get total transactions (FIXED: from stellar_operations)
            tx_query = """
                SELECT COUNT(DISTINCT transaction_hash) as total_transactions
                FROM stellar_operations
                WHERE asset_code IS NOT NULL
            """
            tx_row = await self._execute_query(tx_query)
            total_transactions = tx_row['total_transactions'] if tx_row else 0
            
            # Get total supply across all tokens
            distributions = await self.get_all_token_distributions(use_cache)
            total_supply = sum(d.total_supply for d in distributions)
            
            # Get active accounts by period (FIXED: from stellar_operations)
            now = datetime.now()
            active_24h = await self._get_active_accounts(now - timedelta(hours=24))
            active_7d = await self._get_active_accounts(now - timedelta(days=7))
            active_30d = await self._get_active_accounts(now - timedelta(days=30))
            
            # Calculate element balance score
            balance_score = await self._calculate_element_balance_score(distributions)
            
            health = EcosystemHealth(
                timestamp=now,
                total_holders=total_holders,
                total_accounts=total_accounts,
                total_transactions=total_transactions,
                total_supply_all_tokens=total_supply,
                active_accounts_24h=active_24h,
                active_accounts_7d=active_7d,
                active_accounts_30d=active_30d,
                element_balance_score=balance_score
            )
            
            self._set_cached(cache_key, health)
            
            logger.info("✓ Ecosystem health metrics complete")
            return health
            
        except Exception as e:
            self._record_error(f"Error getting ecosystem health: {e}")
            raise AnalyticsException(f"Ecosystem health analysis failed: {e}")
    
    async def _get_active_accounts(self, since: datetime) -> int:
        """Get count of accounts active since a given time."""
        try:
            # FIXED: Query stellar_operations for activity
            query = """
                SELECT COUNT(DISTINCT COALESCE(from_account, source_account)) as active_count
                FROM stellar_operations
                WHERE created_at >= $1
                AND asset_code IS NOT NULL
            """
            
            row = await self._execute_query(query, (since,))
            return row['active_count'] if row else 0
            
        except Exception as e:
            logger.warning(f"Error getting active accounts: {e}")
            return 0
    
    async def _calculate_element_balance_score(
        self,
        distributions: List[TokenDistribution]
    ) -> Decimal:
        """
        Calculate how balanced the 4 elements are.
        
        Perfect balance = all elements have same supply = score of 100
        Imbalanced = significant differences = lower score
        
        Returns:
            Score from 0-100
        """
        try:
            if len(distributions) < 4:
                return Decimal('50')  # Not all elements present
            
            # Get supplies
            supplies = [float(d.total_supply) for d in distributions]
            
            # Calculate coefficient of variation (CV)
            # CV = (std_dev / mean) * 100
            import statistics
            mean = statistics.mean(supplies)
            if mean == 0:
                return Decimal('50')
            
            std_dev = statistics.stdev(supplies)
            cv = (std_dev / mean) * 100
            
            # Convert CV to balance score (inverse relationship)
            # CV of 0% = perfect balance = 100 score
            # CV of 100% = very imbalanced = 0 score
            score = max(0, 100 - cv)
            
            return Decimal(str(round(score, 2)))
            
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
            
            # Get unique account count (FIXED: use ubec_balances)
            unique_query = """
                SELECT COUNT(DISTINCT account_id) as unique_accounts
                FROM ubec_balances
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
    print("VERSION: 3.3.0 (Operations Table Fix - Proper Transaction Metrics)")
    print()
    print("CRITICAL FIX:")
    print("✅ Changed transaction metrics from stellar_transactions to stellar_operations")
    print("✅ Use from_account/to_account instead of non-existent destination column")
    print("✅ Added asset_code filter for token-specific metrics")
    print("✅ Proper grouping by transaction_hash for transaction counts")
    print("✅ All queries now reference only existing columns")
    print()
    print("USAGE:")
    print("------")
    print()
    print("  # Via service registry (RECOMMENDED - Principle #3)")
    print("  from core.service_registry import registry")
    print("  analytics = await registry.get('ubec_analytics_service')")
    print()
    print("  # CLI command interface (main.py)")
    print("  result = await analytics.analyze_token_distribution()  # All tokens")
    print("  result = await analytics.calculate_velocity()  # Velocity metrics")
    print("  result = await analytics.calculate_concentration()  # Concentration metrics")
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
    print("DESIGN PRINCIPLES:")
    print("------------------")
    print("✅ All 12 principles fully implemented")
    print("✅ Database schema alignment fixed - now queries stellar_operations")
    print("✅ Enhanced health check using ServiceHealthCheck utility")
    print("✅ CLI command methods properly implemented")
    print("✅ Interface contract aligned with main.py")
    print("✅ Comprehensive error tracking and reporting")
    print("✅ Cache performance monitoring")
    print()
    print("=" * 80)
