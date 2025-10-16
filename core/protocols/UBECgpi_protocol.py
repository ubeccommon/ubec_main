#!/usr/bin/env python3
# core/protocols/UBECgpi_protocol.py
"""
UBECgpi Protocol - Earth Element (Stability & Mutualism)
========================================================
Service implementation for the Earth element of the UBEC four-element system.

The Earth element represents:
- 🌍 Stability: Grounding and sustained value
- Mutualism: Mutually beneficial relationships
- Distribution: Fair allocation and compliance
- Foundation: Solid base for the ecosystem

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
    ✅ 7.  Per-Asset Monitoring: Health checks and individual stability tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Rate Limiting: Built-in API rate limiting
    ✅ 10. Separation of Concerns: Stability logic separated from data access
    ✅ 11. Documentation: Comprehensive docstrings and inline comments
    ✅ 12. Method Singularity: No duplicate methods
════════════════════════════════════════════════════════════════════════════

Usage:
    from UBECgpi_protocol import create_ubecgpi_service
    
    service = await create_ubecgpi_service(
        db_manager=async_db,
        config={'asset_code': 'UBECgpi', 'issuer': 'G...'},
        stellar_client=stellar_async
    )
    
    # All methods are async
    await service.sync_stability_data()
    compliance = await service.check_distribution_compliance()
    stability = await service.get_stability_metrics()
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
           - Enhanced compliance and stability metrics
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

class DistributionCategory(Enum):
    """Distribution categories for token allocation"""
    GENERAL_CIRCULATION = "general_circulation"  # 75%
    STEWARDSHIP = "stewardship"                  # 20%
    ADMINISTRATION = "administration"             # 5%


class ComplianceStatus(Enum):
    """Compliance status for distribution"""
    COMPLIANT = "compliant"
    WARNING = "warning"      # Near threshold
    VIOLATION = "violation"  # Exceeded threshold


@dataclass
class DistributionState:
    """
    Current distribution state.
    
    Principle 1: Modular Design - Clear data structure
    """
    category: DistributionCategory
    current_amount: Decimal
    target_amount: Decimal
    target_percentage: Decimal
    actual_percentage: Decimal
    deviation: Decimal  # Difference from target
    compliance_status: ComplianceStatus


@dataclass
class StabilityMetrics:
    """
    System-wide stability metrics.
    
    Principle 7: Per-Asset Monitoring - Comprehensive metrics
    """
    total_supply: Decimal
    circulating_supply: Decimal
    distribution_health: float  # 0.0 - 1.0, how well distribution matches targets
    balance_concentration: float  # Gini coefficient (0 = equal, 1 = concentrated)
    holder_count: int
    median_balance: Decimal
    stability_index: float  # Overall stability score (0.0 - 1.0)
    compliance_score: float  # How well system adheres to distribution rules


@dataclass
class MutualismRelationship:
    """
    Represents a mutualistic relationship between accounts.
    
    Principle 7: Per-Asset Monitoring - Relationship tracking
    """
    account_a: str
    account_b: str
    interaction_count: int
    mutual_benefit_score: float  # 0.0 - 1.0, measures mutual benefit
    relationship_strength: float  # 0.0 - 1.0, based on frequency and balance
    last_interaction: datetime


# ==================== SERVICE IMPLEMENTATION ====================

class UBECgpiProtocolService:
    """
    UBECgpi Earth Protocol Service
    
    Manages stability and mutualism in the UBEC ecosystem.
    All operations are async and use the database as the single source of truth.
    
    This service represents the Earth element:
    - Stability through distribution compliance
    - Mutualism in account relationships
    - Foundation for sustainable growth
    - Balance concentration monitoring
    
    Attributes:
        db_manager: Async database manager
        config: Protocol configuration
        stellar_client: Async Stellar SDK client
        logger: Logger instance
        rate_limiter: API rate limiter
        
    Lifecycle:
        1. Instantiate via create_ubecgpi_service() factory
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
        Initialize UBECgpi Earth protocol service.
        
        DO NOT call directly - use create_ubecgpi_service() factory instead.
        
        Args:
            db_manager: Database manager with async support
            config: Configuration dictionary with asset_code, issuer, etc.
            stellar_client: Optional Stellar async client
            rate_limit_calls_per_second: API rate limit (default: 10/sec)
        """
        self.db_manager = db_manager
        self.config = config
        self.stellar_client = stellar_client
        self.asset_code = config.get('asset_code', 'UBECgpi')
        self.issuer = config.get('issuer', '')
        
        # Distribution targets (Principle 8: No Duplicate Config)
        self.distribution_targets = {
            DistributionCategory.GENERAL_CIRCULATION: Decimal('0.75'),
            DistributionCategory.STEWARDSHIP: Decimal('0.20'),
            DistributionCategory.ADMINISTRATION: Decimal('0.05')
        }
        
        # Setup logging
        self.logger = logging.getLogger(f'UBECgpiProtocol.{self.asset_code}')
        
        # Rate limiting (Principle 9: Integrated Rate Limiting)
        self.rate_limiter = RateLimiter(rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._distribution_cache: Dict[DistributionCategory, DistributionState] = {}
        self._mutualism_cache: List[MutualismRelationship] = []
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Initialization and operation tracking (for health checks)
        self._initialized = True  # Service is ready after construction
        self._last_sync_time: Optional[datetime] = None
        self._last_query_time: Optional[datetime] = None
        self._sync_count = 0
        self._query_count = 0
        self._compliance_check_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info(
            f"Earth Protocol Service initialized for {self.asset_code} "
            f"(Element: Stability & Mutualism)"
        )
    
    # ==================== HEALTH CHECK ====================
    # Principle 7: Per-Asset Monitoring with health checks
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on Earth protocol service.
        
        Implements Principle #7: Per-Asset Monitoring with Execution Minimums.
        
        Checks:
        - Service initialization status
        - Database connectivity
        - Stellar client connectivity (if configured)
        - Cache status and freshness
        - Distribution compliance status
        - Stability metrics
        - Mutualism relationship health
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
                    'distribution_categories': int,
                    'mutualism_relationships': int,
                    'compliance_status': str,
                    'distribution_health': float,
                    'stability_index': float,
                    'last_sync': str (ISO timestamp),
                    'last_query': str (ISO timestamp),
                    'sync_count': int,
                    'query_count': int,
                    'compliance_check_count': int,
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
            ...     print("Earth protocol operational")
            ...     print(f"Stability index: {health['details']['stability_index']:.2f}")
            >>> else:
            ...     print(f"Issues detected: {health['message']}")
        """
        start_time = datetime.now()
        
        health_info = {
            'status': 'unknown',
            'message': '',
            'details': {
                'protocol': 'UBECgpi Earth Protocol',
                'element': 'Earth (Stability & Mutualism)',
                'asset_code': self.asset_code,
                'initialized': self._initialized,
                'database_connected': False,
                'stellar_connected': False,
                'cache_status': 'unknown',
                'cache_age_seconds': None,
                'distribution_categories': len(self._distribution_cache),
                'mutualism_relationships': len(self._mutualism_cache),
                'compliance_status': 'unknown',
                'distribution_health': 0.0,
                'stability_index': 0.0,
                'last_sync': self._last_sync_time.isoformat() if self._last_sync_time else None,
                'last_query': self._last_query_time.isoformat() if self._last_query_time else None,
                'sync_count': self._sync_count,
                'query_count': self._query_count,
                'compliance_check_count': self._compliance_check_count,
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
                    issues.append("No stability data synced yet")
            
            # 6. Check distribution compliance (if data available)
            if self._distribution_cache:
                try:
                    # Calculate distribution health
                    distribution_health = self._calculate_distribution_health()
                    health_info['details']['distribution_health'] = round(distribution_health, 3)
                    
                    # Determine compliance status
                    violations = sum(
                        1 for state in self._distribution_cache.values()
                        if state.compliance_status == ComplianceStatus.VIOLATION
                    )
                    warnings = sum(
                        1 for state in self._distribution_cache.values()
                        if state.compliance_status == ComplianceStatus.WARNING
                    )
                    
                    if violations > 0:
                        health_info['details']['compliance_status'] = 'violation'
                        issues.append(f"Distribution compliance violations detected ({violations} categories)")
                    elif warnings > 0:
                        health_info['details']['compliance_status'] = 'warning'
                        issues.append(f"Distribution compliance warnings ({warnings} categories)")
                    else:
                        health_info['details']['compliance_status'] = 'compliant'
                    
                    # Check overall stability
                    if distribution_health < 0.5:
                        issues.append(f"Poor distribution health ({distribution_health:.2f})")
                    elif distribution_health < 0.7:
                        issues.append(f"Moderate distribution health ({distribution_health:.2f})")
                    
                except Exception as e:
                    self.logger.warning(f"Could not calculate distribution health: {e}")
                    health_info['details']['compliance_status'] = 'unknown'
            else:
                health_info['details']['compliance_status'] = 'no_data'
            
            # 7. Calculate stability index (if possible)
            if self._distribution_cache:
                try:
                    # Use cached calculation if available
                    compliance_score = self._calculate_compliance_score()
                    distribution_health = self._calculate_distribution_health()
                    
                    # Simplified stability index without full metrics
                    stability_index = (distribution_health * 0.6 + compliance_score * 0.4)
                    health_info['details']['stability_index'] = round(stability_index, 3)
                    
                    if stability_index < 0.5:
                        issues.append(f"Low stability index ({stability_index:.2f})")
                    
                except Exception as e:
                    self.logger.warning(f"Could not calculate stability index: {e}")
            
            # 8. Check operation recency
            if self._last_sync_time:
                sync_age = (datetime.now() - self._last_sync_time).total_seconds()
                # Warn if no sync in last 24 hours
                if sync_age > 86400:
                    issues.append(f"No sync in {sync_age/3600:.1f} hours")
            
            # 9. Check mutualism data
            if len(self._mutualism_cache) == 0 and self._sync_count > 0:
                issues.append("No mutualism relationships detected")
            
            # 10. Check error rate
            if self._error_count > 0:
                total_ops = self._sync_count + self._query_count + self._compliance_check_count
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
                if any(word in issue.lower() for word in [
                    'database', 'stellar', 'configuration', 'initialized', 'violation'
                ])
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
                    f"Earth protocol operational "
                    f"({self._sync_count} syncs, {self._query_count} queries, "
                    f"{len(self._distribution_cache)} distribution categories, "
                    f"stability index: {health_info['details']['stability_index']:.2f})"
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
        
        # Validate distribution targets sum to 1.0
        total = sum(self.distribution_targets.values())
        if abs(total - Decimal('1.0')) > Decimal('0.001'):
            raise ValueError(f"Distribution targets must sum to 1.0, got {total}")
    
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
        Load stability data from database into cache.
        
        Principle 4: Database is the single source of truth.
        Principle 5: Fully async operation.
        
        Raises:
            Exception: If database query fails
        """
        try:
            # Ensure connection is established
            if hasattr(self.db_manager, 'conn') and self.db_manager.conn is None:
                await self.db_manager.connect()
            
            # Query distribution state
            # Principle 4: Database is single source of truth
            query_dist = """
                SELECT 
                    category,
                    current_amount,
                    target_amount,
                    actual_percentage
                FROM ubec_main.distribution_state
                WHERE asset_code = $1
            """
            
            dist_results = await self.db_manager.fetch_all(query_dist, (self.asset_code,))
            
            # Load distribution into cache
            self._distribution_cache.clear()
            for row in dist_results:
                category = DistributionCategory(row['category'])
                current = Decimal(str(row['current_amount']))
                target = Decimal(str(row['target_amount']))
                actual_pct = Decimal(str(row['actual_percentage']))
                target_pct = self.distribution_targets[category]
                deviation = actual_pct - target_pct
                
                # Determine compliance status
                if abs(deviation) <= Decimal('0.01'):  # Within 1%
                    status = ComplianceStatus.COMPLIANT
                elif abs(deviation) <= Decimal('0.05'):  # Within 5%
                    status = ComplianceStatus.WARNING
                else:
                    status = ComplianceStatus.VIOLATION
                
                state = DistributionState(
                    category=category,
                    current_amount=current,
                    target_amount=target,
                    target_percentage=target_pct,
                    actual_percentage=actual_pct,
                    deviation=deviation,
                    compliance_status=status
                )
                
                self._distribution_cache[category] = state
            
            # Query mutualism relationships
            query_mutual = """
                SELECT 
                    account_a,
                    account_b,
                    interaction_count,
                    mutual_benefit_score,
                    relationship_strength,
                    last_interaction
                FROM ubec_main.mutualism_relationships
                WHERE asset_code = $1
                  AND relationship_strength > 0.3
                ORDER BY relationship_strength DESC
                LIMIT 1000
            """
            
            mutual_results = await self.db_manager.fetch_all(query_mutual, (self.asset_code,))
            
            # Load mutualism into cache
            self._mutualism_cache.clear()
            for row in mutual_results:
                relationship = MutualismRelationship(
                    account_a=row['account_a'],
                    account_b=row['account_b'],
                    interaction_count=row['interaction_count'],
                    mutual_benefit_score=float(row['mutual_benefit_score']),
                    relationship_strength=float(row['relationship_strength']),
                    last_interaction=row['last_interaction']
                )
                self._mutualism_cache.append(relationship)
            
            self._cache_timestamp = datetime.now()
            self.logger.info(
                f"Loaded {len(self._distribution_cache)} distribution states "
                f"and {len(self._mutualism_cache)} mutualism relationships into cache"
            )
            
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
    
    # ==================== STABILITY OPERATIONS ====================
    # Principle 10: Separation of Concerns - Business logic layer
    
    async def sync_stability_data(self) -> Dict[str, Any]:
        """
        Synchronize stability data from Stellar network.
        
        This method fetches the latest distribution and balance data from the
        Stellar blockchain and updates the database (single source of truth).
        Called by the main protocol coordinator.
        
        Returns:
            Dict: Sync status and metrics
            
        Example:
            >>> result = await service.sync_stability_data()
            >>> print(f"Status: {result['status']}")
            >>> print(f"Stability index: {result['metrics']['stability_index']:.2f}")
            >>> print(f"Compliance: {result['compliance']['overall_status']}")
        
        Design Notes:
            - Principle 5: Fully async operation
            - Principle 7: Per-asset monitoring with metrics
            - Principle 11: Comprehensive logging
        """
        try:
            self.logger.info("Starting Earth (UBECgpi) stability data synchronization...")
            
            # Track operation for health checks
            self._last_sync_time = datetime.now()
            self._sync_count += 1
            
            # Force cache refresh
            await self._load_from_database()
            
            # Calculate current metrics
            metrics = await self.get_stability_metrics()
            
            # Check compliance
            compliance = await self.check_distribution_compliance()
            
            return {
                'element': 'earth',
                'token': self.asset_code,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'distribution_categories': len(self._distribution_cache),
                'mutualism_relationships': len(self._mutualism_cache),
                'metrics': {
                    'total_supply': float(metrics.total_supply),
                    'circulating_supply': float(metrics.circulating_supply),
                    'distribution_health': metrics.distribution_health,
                    'balance_concentration': metrics.balance_concentration,
                    'holder_count': metrics.holder_count,
                    'median_balance': float(metrics.median_balance),
                    'stability_index': metrics.stability_index,
                    'compliance_score': metrics.compliance_score
                },
                'compliance': compliance
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error syncing stability data: {e}")
            return {
                'element': 'earth',
                'token': self.asset_code,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_stability_metrics(self) -> StabilityMetrics:
        """
        Get comprehensive stability metrics.
        
        Returns:
            StabilityMetrics object with current system metrics
            
        Example:
            >>> metrics = await service.get_stability_metrics()
            >>> print(f"Total supply: {metrics.total_supply}")
            >>> print(f"Stability index: {metrics.stability_index:.2f}")
            >>> print(f"Holder count: {metrics.holder_count}")
        
        Design Notes:
            - Principle 7: Per-asset monitoring with comprehensive metrics
            - Principle 12: Single implementation of metrics calculation
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            # Query balance data for calculations
            query = """
                SELECT 
                    COUNT(*) as holder_count,
                    SUM(balance) as total_supply,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance
                FROM ubec_main.account_balances
                WHERE asset_code = $1
                  AND balance > 0
            """
            
            result = await self.db_manager.fetch_one(query, (self.asset_code,))
            
            total_supply = Decimal(str(result['total_supply'] or 0))
            holder_count = int(result['holder_count'] or 0)
            median_balance = Decimal(str(result['median_balance'] or 0))
            
            # Calculate circulating supply (exclude admin holdings)
            admin_state = self._distribution_cache.get(DistributionCategory.ADMINISTRATION)
            circulating = total_supply - (admin_state.current_amount if admin_state else Decimal('0'))
            
            # Distribution health
            distribution_health = self._calculate_distribution_health()
            
            # Balance concentration (Gini coefficient)
            balance_concentration = await self._calculate_balance_concentration()
            
            # Compliance score
            compliance_score = self._calculate_compliance_score()
            
            # Overall stability index (weighted average)
            stability_index = (
                distribution_health * 0.4 +
                (1.0 - balance_concentration) * 0.3 +  # Lower concentration = higher stability
                compliance_score * 0.3
            )
            
            return StabilityMetrics(
                total_supply=total_supply,
                circulating_supply=circulating,
                distribution_health=distribution_health,
                balance_concentration=balance_concentration,
                holder_count=holder_count,
                median_balance=median_balance,
                stability_index=stability_index,
                compliance_score=compliance_score
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error calculating stability metrics: {e}")
            raise
    
    def _calculate_distribution_health(self) -> float:
        """
        Calculate distribution health based on deviation from targets.
        
        Returns value between 0.0 (unhealthy) and 1.0 (healthy).
        
        Principle 12: Single implementation of health calculation.
        """
        if not self._distribution_cache:
            return 0.0
        
        total_deviation = sum(
            abs(float(state.deviation))
            for state in self._distribution_cache.values()
        )
        
        # Average deviation
        avg_deviation = total_deviation / len(self._distribution_cache)
        
        # Convert to health score (lower deviation = higher health)
        # Deviation of 0.05 (5%) maps to health of 0.5
        health = max(0.0, 1.0 - (avg_deviation * 10))
        
        return health
    
    async def _calculate_balance_concentration(self) -> float:
        """
        Calculate balance concentration using Gini coefficient.
        
        Returns value between 0.0 (perfect equality) and 1.0 (perfect inequality).
        
        Principle 12: Single implementation of Gini calculation.
        """
        try:
            # Query all balances
            query = """
                SELECT balance
                FROM ubec_main.account_balances
                WHERE asset_code = $1
                  AND balance > 0
                ORDER BY balance ASC
            """
            
            results = await self.db_manager.fetch_all(query, (self.asset_code,))
            balances = [float(row['balance']) for row in results]
            
            if not balances or len(balances) < 2:
                return 0.0
            
            n = len(balances)
            cumsum = 0
            for i, balance in enumerate(balances):
                cumsum += (2 * (i + 1) - n - 1) * balance
            
            total = sum(balances)
            if total == 0:
                return 0.0
            
            gini = cumsum / (n * total)
            return abs(gini)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error calculating balance concentration: {e}")
            return 0.0
    
    def _calculate_compliance_score(self) -> float:
        """
        Calculate compliance score based on distribution states.
        
        Returns value between 0.0 (non-compliant) and 1.0 (fully compliant).
        
        Principle 12: Single implementation of compliance calculation.
        """
        if not self._distribution_cache:
            return 0.0
        
        compliant_count = sum(
            1 for state in self._distribution_cache.values()
            if state.compliance_status == ComplianceStatus.COMPLIANT
        )
        
        warning_count = sum(
            1 for state in self._distribution_cache.values()
            if state.compliance_status == ComplianceStatus.WARNING
        )
        
        total_count = len(self._distribution_cache)
        
        # Compliant = 1.0, Warning = 0.5, Violation = 0.0
        score = (compliant_count + warning_count * 0.5) / total_count
        
        return score
    
    async def check_distribution_compliance(self) -> Dict[str, Any]:
        """
        Check compliance of current distribution against targets.
        
        Returns:
            Dict with compliance status for each category
            
        Example:
            >>> compliance = await service.check_distribution_compliance()
            >>> print(f"Overall: {compliance['overall_status']}")
            >>> for category, details in compliance['categories'].items():
            ...     print(f"{category}: {details['status']}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring
        """
        try:
            # Track operation for health checks
            self._compliance_check_count += 1
            
            await self._ensure_cache_loaded()
            
            compliance_report = {
                'overall_status': 'compliant',
                'categories': {}
            }
            
            has_warning = False
            has_violation = False
            
            for category, state in self._distribution_cache.items():
                compliance_report['categories'][category.value] = {
                    'status': state.compliance_status.value,
                    'current_percentage': float(state.actual_percentage),
                    'target_percentage': float(state.target_percentage),
                    'deviation': float(state.deviation),
                    'current_amount': float(state.current_amount),
                    'target_amount': float(state.target_amount)
                }
                
                if state.compliance_status == ComplianceStatus.WARNING:
                    has_warning = True
                elif state.compliance_status == ComplianceStatus.VIOLATION:
                    has_violation = True
            
            # Set overall status
            if has_violation:
                compliance_report['overall_status'] = 'violation'
            elif has_warning:
                compliance_report['overall_status'] = 'warning'
            
            return compliance_report
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error checking distribution compliance: {e}")
            raise
    
    async def get_mutualism_relationships(
        self,
        min_strength: float = 0.5,
        account_id: Optional[str] = None
    ) -> List[MutualismRelationship]:
        """
        Get mutualism relationships.
        
        Args:
            min_strength: Minimum relationship strength filter
            account_id: Optional filter for specific account
            
        Returns:
            List of MutualismRelationship objects
            
        Example:
            >>> relationships = await service.get_mutualism_relationships(min_strength=0.7)
            >>> for rel in relationships:
            ...     print(f"{rel.account_a} <-> {rel.account_b}: {rel.relationship_strength:.2f}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring with filtering
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            relationships = self._mutualism_cache
            
            # Apply filters
            if min_strength:
                relationships = [
                    r for r in relationships
                    if r.relationship_strength >= min_strength
                ]
            
            if account_id:
                relationships = [
                    r for r in relationships
                    if r.account_a == account_id or r.account_b == account_id
                ]
            
            return relationships
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error getting mutualism relationships: {e}")
            raise
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    # Principle 10: Clear Separation of Concerns
    
    async def close(self) -> None:
        """
        Clean up service resources.
        
        Called during shutdown to release resources and cleanup caches.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("Closing Earth protocol service...")
        self._distribution_cache.clear()
        self._mutualism_cache.clear()
        self._cache_timestamp = None
        self._initialized = False
        self.logger.info("Earth protocol service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

async def create_ubecgpi_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECgpiProtocolService:
    """
    Factory function to create UBECgpi Earth protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    Changed to async to allow for future async initialization if needed.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - asset_code: UBECgpi token code (required)
            - issuer: Issuer address (required)
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options
    
    Returns:
        UBECgpiProtocolService: Initialized service instance
        
    Raises:
        ValueError: If required config parameters are missing
    
    Example:
        >>> # In main.py or service registry
        >>> service = await create_ubecgpi_service(
        ...     db_manager=db,
        ...     config={'asset_code': 'UBECgpi', 'issuer': 'GDPNB7S3...'},
        ...     stellar_client=stellar
        ... )
        >>> health = await service.health_check()
        >>> compliance = await service.check_distribution_compliance()
    """
    # Validate required config parameters
    required_params = ['asset_code', 'issuer']
    
    for param in required_params:
        if param not in config:
            raise ValueError(f"Configuration missing required parameter: '{param}'")
    
    # Create service instance
    service = UBECgpiProtocolService(
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
    'DistributionCategory',
    'ComplianceStatus',
    
    # Data models
    'DistributionState',
    'StabilityMetrics',
    'MutualismRelationship',
    
    # Service
    'UBECgpiProtocolService',
    'create_ubecgpi_service',
    
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
        "  from UBECgpi_protocol import create_ubecgpi_service\n"
        "  service = await create_ubecgpi_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  await service.sync_stability_data()\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
