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
Version: 3.4.0 (Main.py Interface Alignment)
Date: October 30, 2025

Changes from v3.3:
- ✅ ADDED: get_distribution_overview() for main.py 'overview' analytics
- ✅ ADDED: get_top_holders(limit) for main.py 'holders' analytics
- ✅ ADDED: get_network_metrics() for main.py 'metrics' analytics
- ✅ FIXED: Interface contract mismatch with main.py orchestrator
- Maintained all existing CLI command methods and core functionality
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
        
        # CLI command interface - main.py interface methods
        result = await analytics.get_distribution_overview()  # Overview analytics
        result = await analytics.get_top_holders(limit=50)    # Holder rankings
        result = await analytics.get_network_metrics()        # Network metrics
        
        # Alternative CLI methods
        result = await analytics.analyze_token_distribution()  # Distribution
        result = await analytics.calculate_velocity()          # Velocity
        result = await analytics.calculate_concentration()     # Concentration
        
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
        
        # Get database schema from db_manager
        self.db_schema = getattr(db_manager, 'schema', 'ubec_main')
        
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
        
        try:
            # Clear cache
            self._cache.clear()
            
            self._initialized = False
            logger.info("Analytics service closed")
            
        except Exception as e:
            logger.error(f"Error closing analytics service: {e}")
    
    # ========================================================================
    # HEALTH MONITORING (Principle #7)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for analytics service.
        
        Uses ServiceHealthCheck utility (Principle #12: Method Singularity).
        
        Returns:
            Dict with health status and metrics
        """
        # Use standardized health check utility
        health = ServiceHealthCheck.create_health_response(
            service_name='ubec_analytics_service',
            is_healthy=self._initialized and self._error_count < 10,
            details={
                'initialized': self._initialized,
                'query_count': self._query_count,
                'error_count': self._error_count,
                'cache_hits': self._cache_hits,
                'cache_misses': self._cache_misses,
                'cache_hit_rate': self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0,
                'cached_items': len(self._cache),
                'last_query_time': self._last_query_time.isoformat() if self._last_query_time else None,
                'last_error': self._last_error,
                'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None
            }
        )
        
        # Additional validation: Check if we can query data
        issues = []
        try:
            # Test query to verify data access
            test_query = f"""
                SELECT COUNT(*) as count 
                FROM {self.db_schema}.ubec_balances 
                WHERE balance > 0
            """
            result = await self._execute_query(test_query)
            if result and result['count'] > 0:
                health['details']['data_available'] = True
                health['details']['balance_records'] = result['count']
            else:
                issues.append("No balance data found")
                health['details']['data_available'] = False
        except Exception as e:
            issues.append(f"Data query failed: {e}")
            health['details']['data_available'] = False
        
        # Update health status based on issues
        if issues:
            health['status'] = 'degraded' if health['status'] == 'healthy' else health['status']
            health['details']['issues'] = issues
        
        return health
    
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
    # MAIN.PY INTERFACE METHODS (Added v3.4.0)
    # ========================================================================
    
    async def get_distribution_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive distribution overview across all tokens.
        
        This method provides the 'overview' analysis type for main.py CLI.
        Wraps existing methods to provide expected interface.
        
        Called by main.py with:
            python main.py --mode analytics --analysis-type overview
        
        Returns:
            Dict with comprehensive ecosystem and token distribution data
            
        Principle #12: Method wraps existing functionality, no duplication
        """
        logger.info("Generating distribution overview...")
        
        try:
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'analysis_type': 'overview'
                }
            }
            
            # Get ecosystem health metrics
            ecosystem = await self.get_ecosystem_health()
            result['data']['ecosystem_health'] = asdict(ecosystem)
            
            # Get all token distributions
            distributions = await self.get_all_token_distributions()
            result['data']['token_distributions'] = [asdict(d) for d in distributions]
            
            # Get holder analysis for all tokens
            holder_analyses = []
            for token in TokenCode:
                try:
                    analysis = await self.analyze_holder_concentration(token.value)
                    holder_analyses.append(asdict(analysis))
                except Exception as e:
                    logger.warning(f"Could not get holder analysis for {token.value}: {e}")
            
            result['data']['holder_analyses'] = holder_analyses
            
            # Get liquidity metrics for all tokens
            liquidity_metrics = []
            for token in TokenCode:
                try:
                    metrics = await self.get_liquidity_metrics(token.value)
                    liquidity_metrics.append(asdict(metrics))
                except Exception as e:
                    logger.warning(f"Could not get liquidity metrics for {token.value}: {e}")
            
            result['data']['liquidity_metrics'] = liquidity_metrics
            
            # Add summary statistics
            total_holders = sum(d.total_holders for d in distributions)
            total_whales = sum(h['whale_count'] for h in holder_analyses)
            
            result['data']['summary'] = {
                'total_tokens': len(distributions),
                'total_holders': total_holders,
                'total_supply': float(sum(d.total_supply for d in distributions)),
                'total_whales': total_whales,
                'whale_percentage': (total_whales / total_holders * 100) if total_holders > 0 else 0,
                'average_gini': sum(float(d.gini_coefficient or 0) for d in distributions) / len(distributions) if distributions else 0,
                'average_top10_concentration': sum(float(d.top_10_concentration) for d in distributions) / len(distributions) if distributions else 0,
                'total_circulating_supply': sum(float(m['circulating_supply']) for m in liquidity_metrics),
                'average_liquidity_ratio': sum(float(m['liquidity_ratio']) for m in liquidity_metrics) / len(liquidity_metrics) if liquidity_metrics else 0
            }
            
            # Add token ranking by various metrics
            result['data']['rankings'] = {
                'by_holders': sorted(
                    [{'token': d.asset_code, 'holders': d.total_holders} for d in distributions],
                    key=lambda x: x['holders'],
                    reverse=True
                ),
                'by_gini': sorted(
                    [{'token': d.asset_code, 'gini': float(d.gini_coefficient or 1.0)} for d in distributions],
                    key=lambda x: x['gini']
                ),
                'by_concentration': sorted(
                    [{'token': d.asset_code, 'top10': float(d.top_10_concentration)} for d in distributions],
                    key=lambda x: x['top10']
                )
            }
            
            logger.info("✓ Distribution overview generated")
            return result
            
        except Exception as e:
            self._record_error(f"Distribution overview failed: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def get_top_holders(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get top holders analysis across all tokens.
        
        This method provides the 'holders' analysis type for main.py CLI.
        
        Called by main.py with:
            python main.py --mode analytics --analysis-type holders
        
        Args:
            limit: Maximum number of top holders to return per token (default: 50)
            
        Returns:
            Dict with top holder information for all tokens including:
            - Whale counts and percentages
            - Top holder rankings
            - Distribution tier analysis
            
        Principle #12: Wraps existing holder analysis functionality
        """
        logger.info(f"Getting top {limit} holders for all tokens...")
        
        try:
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'analysis_type': 'holders',
                    'limit': limit,
                    'tokens': []
                }
            }
            
            # Get holder concentration for each token
            for token in TokenCode:
                try:
                    # Get holder analysis
                    holder_analysis = await self.analyze_holder_concentration(token.value)
                    
                    # Get top holders from database
                    query = f"""
                        SELECT 
                            account_id,
                            balance,
                            balance_usd,
                            (balance / NULLIF((
                                SELECT SUM(balance) 
                                FROM {self.db_schema}.ubec_balances 
                                WHERE token_code::text = $1 AND balance > 0
                            ), 0) * 100) as percentage_of_supply
                        FROM {self.db_schema}.ubec_balances
                        WHERE token_code::text = $1
                          AND balance > 0
                        ORDER BY balance DESC
                        LIMIT $2
                    """
                    
                    top_holders = await self._execute_query_many(query, (token.value, limit))
                    
                    token_data = {
                        'token_code': token.value,
                        'element': TOKEN_ELEMENT_MAP[token].value,
                        'total_holders': holder_analysis.total_holders,
                        'whales': {
                            'count': holder_analysis.whale_count,
                            'holdings': float(holder_analysis.whale_holdings),
                            'percentage': float(holder_analysis.whale_percentage)
                        },
                        'mid_tier': {
                            'count': holder_analysis.mid_tier_count,
                            'holdings': float(holder_analysis.mid_tier_holdings)
                        },
                        'small_holders': {
                            'count': holder_analysis.small_holder_count,
                            'holdings': float(holder_analysis.small_holder_holdings)
                        },
                        'top_holders': [
                            {
                                'rank': idx + 1,
                                'account_id': h['account_id'],
                                'balance': float(h['balance']),
                                'balance_usd': float(h['balance_usd']) if h['balance_usd'] else None,
                                'percentage_of_supply': float(h['percentage_of_supply']) if h['percentage_of_supply'] else 0
                            }
                            for idx, h in enumerate(top_holders)
                        ]
                    }
                    
                    result['data']['tokens'].append(token_data)
                    
                except Exception as e:
                    logger.warning(f"Could not get top holders for {token.value}: {e}")
            
            # Add cross-token summary
            total_holders = sum(t['total_holders'] for t in result['data']['tokens'])
            total_whales = sum(t['whales']['count'] for t in result['data']['tokens'])
            
            result['data']['summary'] = {
                'total_tokens_analyzed': len(result['data']['tokens']),
                'total_holders': total_holders,
                'total_whales': total_whales,
                'whale_percentage': (total_whales / total_holders * 100) if total_holders > 0 else 0,
                'average_whales_per_token': total_whales / len(result['data']['tokens']) if result['data']['tokens'] else 0
            }
            
            logger.info(f"✓ Top holders analysis complete for {len(result['data']['tokens'])} tokens")
            return result
            
        except Exception as e:
            self._record_error(f"Top holders analysis failed: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def get_network_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive network metrics and health indicators.
        
        This method provides the 'metrics' analysis type for main.py CLI.
        
        Called by main.py with:
            python main.py --mode analytics --analysis-type metrics
        
        Returns:
            Dict with network-wide metrics across all tokens including:
            - Ecosystem health indicators
            - Transaction metrics (30-day period)
            - Liquidity metrics
            - Network-wide aggregated statistics
            
        Principle #12: Aggregates existing metrics functionality
        """
        logger.info("Calculating network metrics...")
        
        try:
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'analysis_type': 'metrics'
                }
            }
            
            # Get ecosystem health
            ecosystem = await self.get_ecosystem_health()
            result['data']['ecosystem_health'] = asdict(ecosystem)
            
            # Get transaction metrics for all tokens (30-day period)
            transaction_metrics = []
            for token in TokenCode:
                try:
                    metrics = await self.get_transaction_metrics(token.value, 30)
                    transaction_metrics.append(asdict(metrics))
                except Exception as e:
                    logger.warning(f"Could not get transaction metrics for {token.value}: {e}")
            
            result['data']['transaction_metrics'] = transaction_metrics
            
            # Get liquidity metrics for all tokens
            liquidity_metrics = []
            for token in TokenCode:
                try:
                    metrics = await self.get_liquidity_metrics(token.value)
                    liquidity_metrics.append(asdict(metrics))
                except Exception as e:
                    logger.warning(f"Could not get liquidity metrics for {token.value}: {e}")
            
            result['data']['liquidity_metrics'] = liquidity_metrics
            
            # Add aggregated network metrics
            total_transactions = sum(m['total_transactions'] for m in transaction_metrics)
            total_volume = sum(float(m['total_volume']) for m in transaction_metrics)
            
            result['data']['network_summary'] = {
                'total_transaction_volume_30d': total_volume,
                'total_transactions_30d': total_transactions,
                'average_transaction_size': total_volume / total_transactions if total_transactions > 0 else 0,
                'average_velocity': sum(float(m['velocity']) for m in transaction_metrics) / len(transaction_metrics) if transaction_metrics else 0,
                'total_unique_senders': sum(m['unique_senders'] for m in transaction_metrics),
                'total_unique_receivers': sum(m['unique_receivers'] for m in transaction_metrics),
                'total_circulating_supply': sum(float(m['circulating_supply']) for m in liquidity_metrics),
                'total_locked_supply': sum(float(m['locked_supply']) for m in liquidity_metrics),
                'average_liquidity_ratio': sum(float(m['liquidity_ratio']) for m in liquidity_metrics) / len(liquidity_metrics) if liquidity_metrics else 0
            }
            
            # Add per-token rankings by activity
            result['data']['activity_rankings'] = {
                'by_volume': sorted(
                    [{'token': m['asset_code'], 'volume': float(m['total_volume'])} for m in transaction_metrics],
                    key=lambda x: x['volume'],
                    reverse=True
                ),
                'by_transactions': sorted(
                    [{'token': m['asset_code'], 'count': m['total_transactions']} for m in transaction_metrics],
                    key=lambda x: x['count'],
                    reverse=True
                ),
                'by_velocity': sorted(
                    [{'token': m['asset_code'], 'velocity': float(m['velocity'])} for m in transaction_metrics],
                    key=lambda x: x['velocity'],
                    reverse=True
                ),
                'by_liquidity': sorted(
                    [{'token': m['asset_code'], 'ratio': float(m['liquidity_ratio'])} for m in liquidity_metrics],
                    key=lambda x: x['ratio'],
                    reverse=True
                )
            }
            
            logger.info("✓ Network metrics calculated")
            return result
            
        except Exception as e:
            self._record_error(f"Network metrics calculation failed: {e}")
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
    
    async def _execute_query_many(
        self,
        query: str,
        params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return multiple rows.
        
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
            query = f"""
                SELECT 
                    COUNT(DISTINCT account_id) as total_holders,
                    COALESCE(SUM(balance), 0) as total_supply,
                    COALESCE(AVG(balance), 0) as average_balance,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance,
                    COALESCE(MIN(balance), 0) as min_balance,
                    COALESCE(MAX(balance), 0) as max_balance
                FROM {self.db_schema}.ubec_balances
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
            query = f"""
                WITH top_n_supply AS (
                    SELECT COALESCE(SUM(balance), 0) as top_supply
                    FROM (
                        SELECT balance
                        FROM {self.db_schema}.ubec_balances
                        WHERE token_code::text = $1 AND balance > 0
                        ORDER BY balance DESC
                        LIMIT $2
                    ) top_n
                ),
                total_supply AS (
                    SELECT COALESCE(SUM(balance), 0) as total
                    FROM {self.db_schema}.ubec_balances
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
            query = f"""
                WITH sorted_balances AS (
                    SELECT 
                        balance,
                        ROW_NUMBER() OVER (ORDER BY balance) as rank,
                        COUNT(*) OVER () as total_count
                    FROM {self.db_schema}.ubec_balances
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
            print(f"Whale %: {analysis.whale_percentage}%")
        """
        cache_key = f"holder_analysis_{asset_code}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Validate token code
            if asset_code not in [t.value for t in TokenCode]:
                raise AnalyticsException(f"Invalid token code: {asset_code}")
            
            # Get total supply for percentage calculations
            dist = await self.get_token_distribution(asset_code, use_cache)
            
            # Auto-calculate whale threshold (top 1% of average balance)
            if whale_threshold is None:
                whale_threshold = dist.average_balance * Decimal('10')  # 10x average
            
            # Define tiers
            mid_tier_threshold = dist.average_balance
            
            # FIXED: Query ubec_balances table
            query = f"""
                WITH holder_tiers AS (
                    SELECT 
                        account_id,
                        balance,
                        CASE 
                            WHEN balance >= $2 THEN 'whale'
                            WHEN balance >= $3 THEN 'mid_tier'
                            ELSE 'small'
                        END as tier
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code::text = $1 AND balance > 0
                )
                SELECT 
                    tier,
                    COUNT(*) as holder_count,
                    COALESCE(SUM(balance), 0) as total_holdings
                FROM holder_tiers
                GROUP BY tier
            """
            
            rows = await self._execute_query_many(
                query, 
                (asset_code, float(whale_threshold), float(mid_tier_threshold))
            )
            
            # Parse results by tier
            tiers = {row['tier']: row for row in rows}
            
            whale_data = tiers.get('whale', {'holder_count': 0, 'total_holdings': 0})
            mid_data = tiers.get('mid_tier', {'holder_count': 0, 'total_holdings': 0})
            small_data = tiers.get('small', {'holder_count': 0, 'total_holdings': 0})
            
            whale_holdings = Decimal(str(whale_data['total_holdings']))
            whale_percentage = (whale_holdings / dist.total_supply * 100) if dist.total_supply > 0 else Decimal('0')
            
            analysis = HolderAnalysis(
                asset_code=asset_code,
                total_holders=dist.total_holders,
                whale_count=whale_data['holder_count'],
                whale_holdings=whale_holdings,
                whale_percentage=whale_percentage,
                mid_tier_count=mid_data['holder_count'],
                mid_tier_holdings=Decimal(str(mid_data['total_holdings'])),
                small_holder_count=small_data['holder_count'],
                small_holder_holdings=Decimal(str(small_data['total_holdings']))
            )
            
            self._set_cached(cache_key, analysis)
            
            logger.info(f"✓ Holder concentration analysis complete for {asset_code}")
            return analysis
            
        except Exception as e:
            self._record_error(f"Error analyzing holder concentration for {asset_code}: {e}")
            raise AnalyticsException(f"Holder concentration analysis failed: {e}")
    
    # ========================================================================
    # TRANSACTION & VELOCITY ANALYSIS
    # ========================================================================
    
    async def get_transaction_metrics(
        self,
        asset_code: str,
        period_days: int = 30,
        use_cache: bool = True
    ) -> TransactionMetrics:
        """
        Analyze transaction patterns and velocity.
        
        Args:
            asset_code: Token code
            period_days: Analysis period in days
            use_cache: Whether to use cached results
            
        Returns:
            TransactionMetrics object
            
        Example:
            metrics = await analytics.get_transaction_metrics('UBEC', 30)
            print(f"Velocity: {metrics.velocity} tx/day")
            print(f"Volume: {metrics.total_volume}")
        """
        cache_key = f"tx_metrics_{asset_code}_{period_days}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Validate token code
            if asset_code not in [t.value for t in TokenCode]:
                raise AnalyticsException(f"Invalid token code: {asset_code}")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # FIXED v3.3: Query stellar_operations table with proper columns
            query = f"""
                WITH token_operations AS (
                    SELECT 
                        transaction_hash,
                        from_account,
                        to_account,
                        amount,
                        created_at
                    FROM {self.db_schema}.stellar_operations
                    WHERE asset_code = $1
                      AND created_at >= $2
                      AND created_at <= $3
                      AND amount > 0
                )
                SELECT 
                    COUNT(DISTINCT transaction_hash) as total_transactions,
                    COUNT(DISTINCT from_account) as unique_senders,
                    COUNT(DISTINCT to_account) as unique_receivers,
                    COALESCE(SUM(amount), 0) as total_volume,
                    COALESCE(AVG(amount), 0) as average_tx_size,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median_tx_size
                FROM token_operations
            """
            
            row = await self._execute_query(query, (asset_code, start_date, end_date))
            
            if not row:
                raise AnalyticsException(f"No transaction data found for {asset_code}")
            
            # Get total supply for turnover calculation
            dist = await self.get_token_distribution(asset_code, use_cache)
            
            # Calculate velocity (transactions per day)
            velocity = Decimal(str(row['total_transactions'])) / Decimal(str(period_days)) if period_days > 0 else Decimal('0')
            
            # Calculate turnover ratio
            total_volume = Decimal(str(row['total_volume']))
            turnover = (total_volume / dist.total_supply) if dist.total_supply > 0 else Decimal('0')
            
            metrics = TransactionMetrics(
                asset_code=asset_code,
                period_days=period_days,
                total_transactions=row['total_transactions'],
                unique_senders=row['unique_senders'],
                unique_receivers=row['unique_receivers'],
                total_volume=total_volume,
                average_transaction_size=Decimal(str(row['average_tx_size'])),
                median_transaction_size=Decimal(str(row['median_tx_size'] or 0)),
                velocity=velocity,
                turnover_ratio=turnover
            )
            
            self._set_cached(cache_key, metrics)
            
            logger.info(f"✓ Transaction metrics complete for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error analyzing transactions for {asset_code}: {e}")
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
        Analyze token liquidity and supply distribution.
        
        Args:
            asset_code: Token code
            use_cache: Whether to use cached results
            
        Returns:
            LiquidityMetrics object
            
        Example:
            metrics = await analytics.get_liquidity_metrics('UBEC')
            print(f"Circulating: {metrics.circulating_supply}")
            print(f"Liquidity ratio: {metrics.liquidity_ratio}%")
        """
        cache_key = f"liquidity_{asset_code}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Validate token code
            if asset_code not in [t.value for t in TokenCode]:
                raise AnalyticsException(f"Invalid token code: {asset_code}")
            
            # Get distribution for total supply
            dist = await self.get_token_distribution(asset_code, use_cache)
            
            # FIXED: Query ubec_balances table for supply breakdown
            query = f"""
                WITH account_types AS (
                    SELECT 
                        ub.account_id,
                        ub.balance,
                        COALESCE(ma.account_type, 'general') as account_type
                    FROM {self.db_schema}.ubec_balances ub
                    LEFT JOIN {self.db_schema}.monitored_accounts ma ON ub.account_id = ma.account_id
                    WHERE ub.token_code::text = $1 AND ub.balance > 0
                )
                SELECT 
                    account_type,
                    COALESCE(SUM(balance), 0) as type_supply
                FROM account_types
                GROUP BY account_type
            """
            
            rows = await self._execute_query_many(query, (asset_code,))
            
            # Parse supply by account type
            supply_by_type = {row['account_type']: Decimal(str(row['type_supply'])) for row in rows}
            
            # Calculate locked supply (administration + stewardship)
            locked_supply = supply_by_type.get('administration', Decimal('0')) + \
                          supply_by_type.get('stewardship', Decimal('0'))
            
            # Circulating supply = total - locked
            circulating_supply = dist.total_supply - locked_supply
            
            # Available liquidity (estimate: 80% of circulating)
            available_liquidity = circulating_supply * Decimal('0.8')
            
            # Liquidity ratio
            liquidity_ratio = (available_liquidity / dist.total_supply * 100) if dist.total_supply > 0 else Decimal('0')
            
            metrics = LiquidityMetrics(
                asset_code=asset_code,
                total_supply=dist.total_supply,
                circulating_supply=circulating_supply,
                locked_supply=locked_supply,
                available_liquidity=available_liquidity,
                liquidity_ratio=liquidity_ratio
            )
            
            self._set_cached(cache_key, metrics)
            
            logger.info(f"✓ Liquidity metrics complete for {asset_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error analyzing liquidity for {asset_code}: {e}")
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
            EcosystemHealth object with ecosystem-wide metrics
            
        Example:
            health = await analytics.get_ecosystem_health()
            print(f"Total holders: {health.total_holders}")
            print(f"Balance score: {health.element_balance_score}")
        """
        cache_key = "ecosystem_health"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Get unique account count
            account_query = f"""
                SELECT COUNT(DISTINCT account_id) as total_accounts
                FROM {self.db_schema}.ubec_balances
                WHERE balance > 0
            """
            account_row = await self._execute_query(account_query)
            total_accounts = account_row['total_accounts'] if account_row else 0
            
            # Get total holder count across all tokens
            holder_query = f"""
                SELECT 
                    COUNT(*) as total_holders,
                    COALESCE(SUM(balance), 0) as total_supply
                FROM {self.db_schema}.ubec_balances
                WHERE balance > 0
            """
            holder_row = await self._execute_query(holder_query)
            
            # Get total transaction count
            tx_query = f"""
                SELECT COUNT(DISTINCT transaction_hash) as total_transactions
                FROM {self.db_schema}.stellar_operations
                WHERE asset_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
            """
            tx_row = await self._execute_query(tx_query)
            
            # Get active accounts by time period
            now = datetime.now()
            active_24h_query = f"""
                SELECT COUNT(DISTINCT from_account) as active_accounts
                FROM {self.db_schema}.stellar_operations
                WHERE created_at >= $1
                  AND asset_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
            """
            
            active_24h = await self._execute_query(active_24h_query, (now - timedelta(days=1),))
            active_7d = await self._execute_query(active_24h_query, (now - timedelta(days=7),))
            active_30d = await self._execute_query(active_24h_query, (now - timedelta(days=30),))
            
            # Calculate element balance score
            distributions = await self.get_all_token_distributions(use_cache)
            if len(distributions) == 4:
                holder_counts = [d.total_holders for d in distributions]
                avg_holders = sum(holder_counts) / 4
                # Calculate coefficient of variation (lower = more balanced)
                variance = sum((h - avg_holders) ** 2 for h in holder_counts) / 4
                std_dev = variance ** 0.5
                cv = (std_dev / avg_holders) if avg_holders > 0 else 0
                # Convert to score (0-100, where 100 = perfectly balanced)
                balance_score = max(0, 100 - (cv * 100))
            else:
                balance_score = 0
            
            health = EcosystemHealth(
                timestamp=datetime.now(),
                total_holders=holder_row['total_holders'] if holder_row else 0,
                total_accounts=total_accounts,
                total_transactions=tx_row['total_transactions'] if tx_row else 0,
                total_supply_all_tokens=Decimal(str(holder_row['total_supply'])) if holder_row else Decimal('0'),
                active_accounts_24h=active_24h['active_accounts'] if active_24h else 0,
                active_accounts_7d=active_7d['active_accounts'] if active_7d else 0,
                active_accounts_30d=active_30d['active_accounts'] if active_30d else 0,
                element_balance_score=Decimal(str(balance_score))
            )
            
            self._set_cached(cache_key, health)
            
            logger.info("✓ Ecosystem health metrics complete")
            return health
            
        except Exception as e:
            self._record_error(f"Error calculating ecosystem health: {e}")
            raise AnalyticsException(f"Ecosystem health calculation failed: {e}")
    
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
            unique_query = f"""
                SELECT COUNT(DISTINCT account_id) as unique_accounts
                FROM {self.db_schema}.ubec_balances
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
    print("VERSION: 3.4.0 (Main.py Interface Alignment)")
    print()
    print("CHANGES FROM v3.3:")
    print("✅ ADDED: get_distribution_overview() for 'overview' analytics")
    print("✅ ADDED: get_top_holders(limit) for 'holders' analytics")
    print("✅ ADDED: get_network_metrics() for 'metrics' analytics")
    print("✅ FIXED: Interface contract mismatch with main.py")
    print()
    print("USAGE:")
    print("------")
    print()
    print("  # Via service registry (RECOMMENDED - Principle #3)")
    print("  from core.service_registry import registry")
    print("  analytics = await registry.get('ubec_analytics_service')")
    print()
    print("  # Main.py interface methods (v3.4.0+)")
    print("  result = await analytics.get_distribution_overview()  # Overview")
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
    print("DESIGN PRINCIPLES:")
    print("------------------")
    print("✅ All 12 principles fully implemented")
    print("✅ Interface contract now aligned with main.py")
    print("✅ Three new wrapper methods maintain Principle #12 (Method Singularity)")
    print("✅ Enhanced health check using ServiceHealthCheck utility")
    print("✅ All CLI command methods properly implemented")
    print("✅ Comprehensive error tracking and reporting")
    print("✅ Cache performance monitoring")
    print()
    print("=" * 80)
