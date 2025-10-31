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
Version: 3.5.3 (SQL Aggregation Fix)
Date: October 31, 2025

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
        
        # Direct analysis methods
        dist = await analytics.get_token_distribution('UBEC')
        holders = await analytics.analyze_holder_concentration('UBEC')
        
        # Health check (Principle #7) - Uses ServiceHealthCheck utility!
        health = await analytics.health_check()
    """
    
    def __init__(self, db_manager, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analytics service.
        
        Args:
            db_manager: Database manager instance
            config: Optional configuration overrides
        """
        self.db_manager = db_manager
        self.config = config or {}
        
        # Service metadata
        self.service_name = "ubec_analytics_service"
        self.version = "3.5.3"
        
        # Get database schema (Principle #4: Single Source of Truth)
        # Try to get from config object if available, otherwise from dict
        if hasattr(config, 'get_setting'):
            # Config is a Settings object
            self.db_schema = config.get_setting('db_schema', 'ubec_main')
        elif isinstance(config, dict):
            # Config is a dictionary
            self.db_schema = config.get('db_schema', 'ubec_main')
        else:
            # Fallback to ubec_main as default
            self.db_schema = 'ubec_main'
        
        # Cache configuration (Principle #4: Single Source of Truth)
        if hasattr(config, 'get_setting'):
            # Config is a Settings object
            cache_ttl_min = config.get_setting('cache_ttl_minutes', 5)
        elif isinstance(config, dict):
            # Config is a dictionary
            cache_ttl_min = config.get('cache_ttl_minutes', 5)
        else:
            # Fallback default
            cache_ttl_min = 5
        
        self._cache_ttl = timedelta(minutes=cache_ttl_min)
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # Performance metrics tracking (Principle #7: Per-Asset Monitoring)
        self._query_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._last_query_time: Optional[datetime] = None
        
        # Error tracking (Principle #7: Per-Asset Monitoring)
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        logger.info(f"✓ {self.service_name} v{self.version} initialized")
    
    async def initialize(self) -> None:
        """
        Async initialization method required by service registry pattern.
        
        This method is called by main.py after __init__ to perform any
        async setup operations. For analytics service, all setup is
        synchronous and completed in __init__, so this is a no-op.
        
        Principle #2: Service Pattern - Required by main.py orchestrator
        """
        logger.info(f"{self.service_name} async initialization complete")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for analytics service.
        
        Principle #7 Compliance:
        - Uses ServiceHealthCheck utility (Principle #12: Method Singularity)
        - Monitors per-asset data freshness
        - Tracks cache performance
        - Reports error rates
        
        Returns:
            Dict with health status and detailed metrics
            
        Example:
            health = await analytics.health_check()
            if health['status'] == 'healthy':
                print(f"Cache hit rate: {health['details']['cache_hit_rate']:.1%}")
        """
        try:
            # Basic database connectivity check
            query = f"SELECT COUNT(*) as count FROM {self.db_schema}.ubec_balances"
            result = await self._execute_query(query)
            db_connected = result is not None
            
            # Calculate cache hit rate
            total_cache_ops = self._cache_hits + self._cache_misses
            cache_hit_rate = (self._cache_hits / total_cache_ops) if total_cache_ops > 0 else 0
            
            # Check data freshness
            freshness_query = f"""
                SELECT 
                    MAX(last_sync) as last_sync,
                    COUNT(DISTINCT token_code) as token_count
                FROM {self.db_schema}.ubec_balances
            """
            freshness_result = await self._execute_query(freshness_query)
            
            last_sync = freshness_result['last_sync'] if freshness_result else None
            token_count = freshness_result['token_count'] if freshness_result else 0
            
            # Calculate time since last sync
            if last_sync:
                time_since_sync = (datetime.now() - last_sync).total_seconds() / 60  # minutes
                data_fresh = time_since_sync < 60  # Fresh if within 1 hour
            else:
                data_fresh = False
                time_since_sync = None
            
            # Determine overall health status
            is_healthy = (
                db_connected and
                data_fresh and
                self._error_count < 10 and
                token_count == 4  # All 4 tokens present
            )
            
            # Use ServiceHealthCheck utility (Principle #12: Method Singularity)
            health_checker = ServiceHealthCheck(
                service_name=self.service_name,
                version=self.version
            )
            
            # Build comprehensive health report
            health_status = health_checker.create_health_status(
                is_healthy=is_healthy,
                details={
                    'database_connected': db_connected,
                    'data_fresh': data_fresh,
                    'last_sync_minutes_ago': time_since_sync,
                    'tokens_present': token_count,
                    'expected_tokens': 4,
                    'query_count': self._query_count,
                    'cache_hit_rate': cache_hit_rate,
                    'cache_hits': self._cache_hits,
                    'cache_misses': self._cache_misses,
                    'error_count': self._error_count,
                    'last_error': self._last_error,
                    'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None,
                    'last_query_time': self._last_query_time.isoformat() if self._last_query_time else None
                }
            )
            
            logger.info(f"Health check: {health_status['status']}")
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_checker = ServiceHealthCheck(
                service_name=self.service_name,
                version=self.version
            )
            return health_checker.create_health_status(
                is_healthy=False,
                details={'error': str(e)}
            )
    
    # ========================================================================
    # CLI COMMAND INTERFACE METHODS (For main.py)
    # ========================================================================
    
    async def analyze_token_distribution(self) -> Dict[str, Any]:
        """
        CLI command: Analyze distribution across all tokens.
        
        This method provides the 'distribution' analysis for main.py CLI.
        
        Called by main.py with:
            python main.py --mode analytics --analysis-type distribution
        
        Returns:
            Dict with distribution analysis for all 4 tokens
            
        Principle #12: Wraps existing get_all_token_distributions()
        """
        logger.info("CLI: Analyzing token distribution...")
        
        try:
            distributions = await self.get_all_token_distributions()
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'analysis_type': 'distribution',
                    'tokens': [asdict(d) for d in distributions]
                }
            }
            
            # Add aggregated statistics
            result['data']['summary'] = {
                'total_tokens': len(distributions),
                'total_holders': sum(d.total_holders for d in distributions),
                'total_supply': float(sum(d.total_supply for d in distributions)),
                'average_gini': sum(float(d.gini_coefficient or 0) for d in distributions) / len(distributions) if distributions else 0
            }
            
            logger.info(f"✓ Distribution analysis complete for {len(distributions)} tokens")
            return result
            
        except Exception as e:
            self._record_error(f"Distribution analysis failed: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def calculate_velocity(self, period_days: int = 30) -> Dict[str, Any]:
        """
        CLI command: Calculate transaction velocity for all tokens.
        
        This method provides the 'velocity' analysis for main.py CLI.
        
        Called by main.py with:
            python main.py --mode analytics --analysis-type velocity
        
        Args:
            period_days: Analysis period in days (default: 30)
            
        Returns:
            Dict with velocity metrics for all tokens
            
        Principle #12: Wraps existing get_transaction_metrics()
        """
        logger.info(f"CLI: Calculating velocity ({period_days} days)...")
        
        try:
            velocity_data = []
            
            for token in TokenCode:
                try:
                    metrics = await self.get_transaction_metrics(token.value, period_days)
                    velocity_data.append({
                        'token_code': metrics.asset_code,
                        'element': TOKEN_ELEMENT_MAP[TokenCode(metrics.asset_code)].value,
                        'period_days': metrics.period_days,
                        'total_transactions': metrics.total_transactions,
                        'velocity': float(metrics.velocity),
                        'average_tx_size': float(metrics.average_transaction_size),
                        'turnover_ratio': float(metrics.turnover_ratio)
                    })
                except Exception as e:
                    logger.warning(f"Could not calculate velocity for {token.value}: {e}")
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'analysis_type': 'velocity',
                    'period_days': period_days,
                    'tokens': velocity_data
                }
            }
            
            # Add aggregated velocity metrics
            if velocity_data:
                result['data']['summary'] = {
                    'average_velocity': sum(t['velocity'] for t in velocity_data) / len(velocity_data),
                    'total_transactions': sum(t['total_transactions'] for t in velocity_data),
                    'average_turnover': sum(t['turnover_ratio'] for t in velocity_data) / len(velocity_data)
                }
            
            logger.info(f"✓ Velocity calculation complete for {len(velocity_data)} tokens")
            return result
            
        except Exception as e:
            self._record_error(f"Velocity calculation failed: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def calculate_concentration(self) -> Dict[str, Any]:
        """
        CLI command: Calculate holder concentration for all tokens.
        
        This method provides the 'concentration' analysis for main.py CLI.
        
        Called by main.py with:
            python main.py --mode analytics --analysis-type concentration
        
        Returns:
            Dict with concentration metrics for all tokens
            
        Principle #12: Wraps existing analyze_holder_concentration()
        """
        logger.info("CLI: Calculating holder concentration...")
        
        try:
            concentration_data = []
            
            for token in TokenCode:
                try:
                    analysis = await self.analyze_holder_concentration(token.value)
                    concentration_data.append({
                        'token_code': analysis.asset_code,
                        'element': TOKEN_ELEMENT_MAP[TokenCode(analysis.asset_code)].value,
                        'total_holders': analysis.total_holders,
                        'whale_count': analysis.whale_count,
                        'whale_percentage': float(analysis.whale_percentage),
                        'mid_tier_count': analysis.mid_tier_count,
                        'small_holder_count': analysis.small_holder_count
                    })
                except Exception as e:
                    logger.warning(f"Could not calculate concentration for {token.value}: {e}")
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'analysis_type': 'concentration',
                    'tokens': concentration_data
                }
            }
            
            # Add aggregated concentration metrics
            if concentration_data:
                total_holders = sum(t['total_holders'] for t in concentration_data)
                total_whales = sum(t['whale_count'] for t in concentration_data)
                
                result['data']['summary'] = {
                    'total_holders': total_holders,
                    'total_whales': total_whales,
                    'average_whale_percentage': sum(t['whale_percentage'] for t in concentration_data) / len(concentration_data),
                    'overall_whale_percentage': (total_whales / total_holders * 100) if total_holders > 0 else 0
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
    # MAIN.PY INTERFACE METHODS (Added v3.4.0, Enhanced v3.5.0)
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
        
        Version 3.5.0 Enhancement:
        - Now includes transaction velocity metrics (30-day period)
        - Enhanced summary statistics with transaction data
        - Added velocity-based rankings
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
            
            # NEW v3.5.0: Get transaction velocity metrics for all tokens (30-day period)
            transaction_metrics = []
            for token in TokenCode:
                try:
                    metrics = await self.get_transaction_metrics(token.value, 30)
                    transaction_metrics.append(asdict(metrics))
                except Exception as e:
                    logger.warning(f"Could not get transaction metrics for {token.value}: {e}")
            
            result['data']['transaction_metrics'] = transaction_metrics
            
            # Add summary statistics (ENHANCED v3.5.0: now includes transaction data)
            total_holders = sum(d.total_holders for d in distributions)
            total_whales = sum(h['whale_count'] for h in holder_analyses)
            
            # Calculate transaction-related summaries
            total_transactions_30d = sum(m['total_transactions'] for m in transaction_metrics) if transaction_metrics else 0
            total_volume_30d = sum(float(m['total_volume']) for m in transaction_metrics) if transaction_metrics else 0
            avg_velocity = sum(float(m['velocity']) for m in transaction_metrics) / len(transaction_metrics) if transaction_metrics else 0
            
            result['data']['summary'] = {
                'total_tokens': len(distributions),
                'total_holders': total_holders,
                'total_supply': float(sum(d.total_supply for d in distributions)),
                'total_whales': total_whales,
                'whale_percentage': (total_whales / total_holders * 100) if total_holders > 0 else 0,
                'average_gini': sum(float(d.gini_coefficient or 0) for d in distributions) / len(distributions) if distributions else 0,
                'average_top10_concentration': sum(float(d.top_10_concentration) for d in distributions) / len(distributions) if distributions else 0,
                'total_circulating_supply': sum(float(m['circulating_supply']) for m in liquidity_metrics),
                'average_liquidity_ratio': sum(float(m['liquidity_ratio']) for m in liquidity_metrics) / len(liquidity_metrics) if liquidity_metrics else 0,
                # NEW v3.5.0: Transaction velocity summaries
                'total_transactions_30d': total_transactions_30d,
                'total_volume_30d': total_volume_30d,
                'average_velocity': avg_velocity,
                'average_transaction_size': total_volume_30d / total_transactions_30d if total_transactions_30d > 0 else 0
            }
            
            # Add token ranking by various metrics (ENHANCED v3.5.0: includes velocity)
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
                ),
                # NEW v3.5.0: Velocity-based rankings
                'by_velocity': sorted(
                    [{'token': m['asset_code'], 'velocity': float(m['velocity'])} for m in transaction_metrics],
                    key=lambda x: x['velocity'],
                    reverse=True
                ) if transaction_metrics else [],
                'by_volume': sorted(
                    [{'token': m['asset_code'], 'volume': float(m['total_volume'])} for m in transaction_metrics],
                    key=lambda x: x['volume'],
                    reverse=True
                ) if transaction_metrics else []
            }
            
            logger.info("✓ Distribution overview generated with transaction velocity metrics")
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
            
            # Query for distribution metrics
            query = f"""
                WITH token_balances AS (
                    SELECT balance
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code::text = $1
                      AND balance > 0
                ),
                sorted_balances AS (
                    SELECT 
                        balance,
                        ROW_NUMBER() OVER (ORDER BY balance DESC) as rank
                    FROM token_balances
                ),
                top_holders AS (
                    SELECT 
                        SUM(CASE WHEN rank <= 10 THEN balance ELSE 0 END) as top_10_sum,
                        SUM(CASE WHEN rank <= 100 THEN balance ELSE 0 END) as top_100_sum
                    FROM sorted_balances
                )
                SELECT 
                    COUNT(*) as total_holders,
                    COALESCE(SUM(tb.balance), 0) as total_supply,
                    COALESCE(AVG(tb.balance), 0) as average_balance,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tb.balance) as median_balance,
                    COALESCE(MIN(tb.balance), 0) as min_balance,
                    COALESCE(MAX(tb.balance), 0) as max_balance,
                    COALESCE(MAX(th.top_10_sum), 0) as top_10_sum,
                    COALESCE(MAX(th.top_100_sum), 0) as top_100_sum
                FROM token_balances tb
                CROSS JOIN top_holders th
            """
            
            row = await self._execute_query(query, (asset_code,))
            
            if not row or row['total_holders'] == 0:
                raise AnalyticsException(f"No balance data found for {asset_code}")
            
            # Calculate concentrations
            total_supply = Decimal(str(row['total_supply']))
            top_10_concentration = (Decimal(str(row['top_10_sum'])) / total_supply * 100) if total_supply > 0 else Decimal('0')
            top_100_concentration = (Decimal(str(row['top_100_sum'])) / total_supply * 100) if total_supply > 0 else Decimal('0')
            
            # Calculate Gini coefficient (simplified version)
            gini_query = f"""
                WITH sorted_balances AS (
                    SELECT 
                        balance,
                        ROW_NUMBER() OVER (ORDER BY balance) as rank
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code::text = $1
                      AND balance > 0
                )
                SELECT 
                    COUNT(*) as n,
                    SUM(balance) as total_sum,
                    SUM(rank * balance) as rank_weighted_sum
                FROM sorted_balances
            """
            
            gini_row = await self._execute_query(gini_query, (asset_code,))
            
            if gini_row and gini_row['n'] > 0:
                n = Decimal(str(gini_row['n']))
                total_sum = Decimal(str(gini_row['total_sum']))
                rank_weighted_sum = Decimal(str(gini_row['rank_weighted_sum']))
                
                # Gini = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
                gini = (2 * rank_weighted_sum) / (n * total_sum) - (n + 1) / n if total_sum > 0 else Decimal('0')
                gini_coefficient = max(Decimal('0'), min(Decimal('1'), gini))  # Clamp to [0, 1]
            else:
                gini_coefficient = None
            
            distribution = TokenDistribution(
                asset_code=asset_code,
                element=element,
                total_holders=row['total_holders'],
                total_supply=total_supply,
                average_balance=Decimal(str(row['average_balance'])),
                median_balance=Decimal(str(row['median_balance'])),
                min_balance=Decimal(str(row['min_balance'])),
                max_balance=Decimal(str(row['max_balance'])),
                top_10_concentration=top_10_concentration,
                top_100_concentration=top_100_concentration,
                gini_coefficient=gini_coefficient
            )
            
            self._set_cached(cache_key, distribution)
            
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
            use_cache: Whether to use cached results
            
        Returns:
            List of TokenDistribution objects for all 4 tokens
            
        Example:
            distributions = await analytics.get_all_token_distributions()
            for dist in distributions:
                print(f"{dist.asset_code}: {dist.total_holders} holders")
        """
        logger.info("Getting distributions for all tokens...")
        
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
        Analyze holder concentration and categorize holders.
        
        Args:
            asset_code: Token code
            whale_threshold: Balance threshold for whale classification
                           (default: top 5% of total supply)
            use_cache: Whether to use cached results
            
        Returns:
            HolderAnalysis object
            
        Example:
            analysis = await analytics.analyze_holder_concentration('UBEC')
            print(f"Whales: {analysis.whale_count} holding {analysis.whale_percentage}%")
        """
        cache_key = f"holder_concentration_{asset_code}_{whale_threshold}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Get distribution first
            dist = await self.get_token_distribution(asset_code, use_cache)
            
            # Calculate whale threshold if not provided (5% of total supply)
            if whale_threshold is None:
                whale_threshold = dist.total_supply * Decimal('0.05')
            
            # Query for holder categories
            query = f"""
                WITH holder_categories AS (
                    SELECT 
                        balance,
                        CASE
                            WHEN balance >= $2 THEN 'whale'
                            WHEN balance >= $2 / 10 THEN 'mid_tier'
                            ELSE 'small'
                        END as category
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code::text = $1
                      AND balance > 0
                )
                SELECT 
                    category,
                    COUNT(*) as count,
                    COALESCE(SUM(balance), 0) as total_balance
                FROM holder_categories
                GROUP BY category
            """
            
            rows = await self._execute_query_many(query, (asset_code, float(whale_threshold)))
            
            # Initialize counts and totals
            whale_count = 0
            whale_holdings = Decimal('0')
            mid_tier_count = 0
            mid_tier_holdings = Decimal('0')
            small_holder_count = 0
            small_holder_holdings = Decimal('0')
            
            # Process results
            for row in rows:
                category = row['category']
                count = row['count']
                total_balance = Decimal(str(row['total_balance']))
                
                if category == 'whale':
                    whale_count = count
                    whale_holdings = total_balance
                elif category == 'mid_tier':
                    mid_tier_count = count
                    mid_tier_holdings = total_balance
                elif category == 'small':
                    small_holder_count = count
                    small_holder_holdings = total_balance
            
            # Calculate whale percentage
            whale_percentage = (whale_holdings / dist.total_supply * 100) if dist.total_supply > 0 else Decimal('0')
            
            analysis = HolderAnalysis(
                asset_code=asset_code,
                total_holders=dist.total_holders,
                whale_count=whale_count,
                whale_holdings=whale_holdings,
                whale_percentage=whale_percentage,
                mid_tier_count=mid_tier_count,
                mid_tier_holdings=mid_tier_holdings,
                small_holder_count=small_holder_count,
                small_holder_holdings=small_holder_holdings
            )
            
            self._set_cached(cache_key, analysis)
            
            logger.info(f"✓ Holder concentration analysis complete for {asset_code}")
            return analysis
            
        except Exception as e:
            self._record_error(f"Error analyzing holder concentration for {asset_code}: {e}")
            raise AnalyticsException(f"Holder concentration analysis failed: {e}")
    
    # ========================================================================
    # TRANSACTION METRICS ANALYSIS
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
            print(f"Liquidity ratio: {metrics.liquidity_ratio:.2%}")
        """
        cache_key = f"liquidity_{asset_code}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Get distribution first
            dist = await self.get_token_distribution(asset_code, use_cache)
            
            # Query for locked/unavailable supply
            # (e.g., treasury accounts, vesting schedules, etc.)
            locked_query = f"""
                SELECT 
                    COALESCE(SUM(balance), 0) as locked_supply
                FROM {self.db_schema}.ubec_balances
                WHERE token_code::text = $1
                  AND (
                      account_id LIKE '%treasury%'
                      OR account_id LIKE '%vesting%'
                      OR account_id LIKE '%locked%'
                  )
            """
            
            locked_row = await self._execute_query(locked_query, (asset_code,))
            locked_supply = Decimal(str(locked_row['locked_supply'])) if locked_row else Decimal('0')
            
            # Calculate circulating and available supply
            total_supply = dist.total_supply
            circulating_supply = total_supply - locked_supply
            
            # Available liquidity (circulating minus very small balances)
            min_liquid_balance = total_supply * Decimal('0.0001')  # 0.01% of supply
            
            liquid_query = f"""
                SELECT 
                    COALESCE(SUM(balance), 0) as available_liquidity
                FROM {self.db_schema}.ubec_balances
                WHERE token_code::text = $1
                  AND balance >= $2
                  AND account_id NOT LIKE '%treasury%'
                  AND account_id NOT LIKE '%vesting%'
                  AND account_id NOT LIKE '%locked%'
            """
            
            liquid_row = await self._execute_query(liquid_query, (asset_code, float(min_liquid_balance)))
            available_liquidity = Decimal(str(liquid_row['available_liquidity'])) if liquid_row else Decimal('0')
            
            # Calculate liquidity ratio
            liquidity_ratio = (available_liquidity / total_supply) if total_supply > 0 else Decimal('0')
            
            metrics = LiquidityMetrics(
                asset_code=asset_code,
                total_supply=total_supply,
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
            raise AnalyticsException(f"Liquidity metrics failed: {e}")
    
    # ========================================================================
    # ECOSYSTEM HEALTH ANALYSIS
    # ========================================================================
    
    async def get_ecosystem_health(self) -> EcosystemHealth:
        """
        Analyze overall ecosystem health across all tokens.
        
        Returns:
            EcosystemHealth object with comprehensive metrics
            
        Example:
            health = await analytics.get_ecosystem_health()
            print(f"Active accounts (24h): {health.active_accounts_24h}")
            print(f"Element balance: {health.element_balance_score:.2f}")
        """
        try:
            # Get total holders and accounts
            holders_query = f"""
                SELECT 
                    COUNT(DISTINCT account_id) as total_accounts,
                    COUNT(*) as total_holders
                FROM {self.db_schema}.ubec_balances
                WHERE balance > 0
            """
            
            holders_row = await self._execute_query(holders_query)
            total_holders = holders_row['total_holders'] if holders_row else 0
            total_accounts = holders_row['total_accounts'] if holders_row else 0
            
            # Get total transaction count
            tx_query = f"""
                SELECT COUNT(*) as total_transactions
                FROM {self.db_schema}.stellar_operations
            """
            
            tx_row = await self._execute_query(tx_query)
            total_transactions = tx_row['total_transactions'] if tx_row else 0
            
            # Get total supply across all tokens
            distributions = await self.get_all_token_distributions()
            total_supply_all = sum(d.total_supply for d in distributions)
            
            # Get active accounts by time period
            now = datetime.now()
            
            active_24h_query = f"""
                SELECT COUNT(DISTINCT from_account) as active_accounts
                FROM {self.db_schema}.stellar_operations
                WHERE created_at >= $1
            """
            
            active_24h_row = await self._execute_query(active_24h_query, (now - timedelta(days=1),))
            active_accounts_24h = active_24h_row['active_accounts'] if active_24h_row else 0
            
            active_7d_row = await self._execute_query(active_24h_query, (now - timedelta(days=7),))
            active_accounts_7d = active_7d_row['active_accounts'] if active_7d_row else 0
            
            active_30d_row = await self._execute_query(active_24h_query, (now - timedelta(days=30),))
            active_accounts_30d = active_30d_row['active_accounts'] if active_30d_row else 0
            
            # Calculate element balance score (how evenly distributed are the 4 elements)
            # Perfect balance = 1.0, complete imbalance = 0.0
            if distributions:
                supplies = [float(d.total_supply) for d in distributions]
                mean_supply = sum(supplies) / len(supplies)
                variance = sum((s - mean_supply) ** 2 for s in supplies) / len(supplies)
                cv = (variance ** 0.5) / mean_supply if mean_supply > 0 else 0
                # Convert CV to balance score (lower CV = better balance)
                element_balance_score = Decimal(str(max(0, 1 - cv)))
            else:
                element_balance_score = Decimal('0')
            
            health = EcosystemHealth(
                timestamp=now,
                total_holders=total_holders,
                total_accounts=total_accounts,
                total_transactions=total_transactions,
                total_supply_all_tokens=total_supply_all,
                active_accounts_24h=active_accounts_24h,
                active_accounts_7d=active_accounts_7d,
                active_accounts_30d=active_accounts_30d,
                element_balance_score=element_balance_score
            )
            
            logger.info("✓ Ecosystem health analysis complete")
            return health
            
        except Exception as e:
            self._record_error(f"Error analyzing ecosystem health: {e}")
            raise AnalyticsException(f"Ecosystem health analysis failed: {e}")
    
    # ========================================================================
    # COMPARATIVE ANALYTICS
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
    print("VERSION: 3.5.3 (SQL Aggregation Fix)")
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
    print("  # Main.py interface methods (v3.4.0+, enhanced v3.5.3)")
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
    print("DESIGN PRINCIPLES:")
    print("------------------")
    print("✅ All 12 principles fully implemented")
    print("✅ Interface contract now aligned with main.py")
    print("✅ Transaction velocity metrics fully integrated")
    print("✅ Enhanced health check using ServiceHealthCheck utility")
    print("✅ All CLI command methods properly implemented")
    print("✅ Comprehensive error tracking and reporting")
    print("✅ Cache performance monitoring")
    print()
    print("=" * 80)
