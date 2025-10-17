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
- Comprehensive health monitoring using ServiceHealthCheck utility

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
    ✅ 12. Method Singularity: No duplicate methods, uses ServiceHealthCheck utility
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

Version: 2.2.0 (Standardized Health Check Pattern)
Date: October 17, 2025

Changelog:
    v2.2.0 - MAJOR: Standardized health check using ServiceHealthCheck utility
           - Implements Principle #12: Method Singularity with shared utility
           - Removed custom health_check() implementation
           - Now uses ServiceHealthCheck.api_dependent_health()
           - Cleaner, more maintainable code with consistent patterns
           - Full compliance with health check implementation guide
    v2.1.0 - Enhanced health_check() method for comprehensive monitoring
           - Implements Principle #7: Per-Asset Monitoring with detailed checks
           - Added initialization tracking
           - Improved error handling and validation
           - Added operation statistics tracking
    v2.0.0 - Complete async service architecture
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

# Import standardized health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck


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
    """Distribution categories for UBEC tokenomics"""
    GENERAL = "general_distribution"           # 65%
    STEWARDSHIP = "stewardship"                # 30%
    ADMINISTRATION = "administration"          # 5%


class ComplianceStatus(Enum):
    """Compliance status for distribution categories"""
    COMPLIANT = "compliant"                    # Within acceptable range
    WARNING = "warning"                         # Approaching limits
    VIOLATION = "violation"                     # Outside acceptable range
    UNKNOWN = "unknown"                         # Cannot determine


@dataclass
class DistributionState:
    """
    Current state of a distribution category.
    
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
        - Principle 12: Method Singularity - Uses ServiceHealthCheck utility
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
        
        # Service identification
        self.asset_code = config.get('asset_code', 'UBECgpi')
        self.issuer = config.get('issuer')
        
        # Distribution targets (official UBEC tokenomics)
        self.distribution_targets = {
            DistributionCategory.GENERAL: Decimal('0.65'),      # 65%
            DistributionCategory.STEWARDSHIP: Decimal('0.30'),  # 30%
            DistributionCategory.ADMINISTRATION: Decimal('0.05') # 5%
        }
        
        # Logging setup
        self.logger = logging.getLogger(f'UBECProtocol.{self.asset_code}')
        self.logger.info(
            f"Earth Protocol Service initialized for {self.asset_code} "
            f"(Element: Stability & Mutualism)"
        )
        
        # Rate limiting
        self.rate_limiter = RateLimiter(calls_per_second=rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._distribution_cache: Dict[DistributionCategory, DistributionState] = {}
        self._stability_cache: Optional[StabilityMetrics] = None
        self._mutualism_cache: List[MutualismRelationship] = []
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Operation tracking for health checks
        self._initialized = False
        self._last_sync_time: Optional[datetime] = None
        self._sync_count = 0
        self._query_count = 0
        self._last_query_time: Optional[datetime] = None
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
    
    # ==================== CACHE MANAGEMENT ====================
    # Principle 10: Separation of Concerns - Cache logic isolated
    
    def _is_cache_valid(self) -> bool:
        """
        Check if current cache is still valid.
        
        Returns:
            True if cache is valid, False if expired
        """
        if self._cache_timestamp is None:
            return False
        
        age = datetime.now() - self._cache_timestamp
        return age < self._cache_ttl
    
    async def _ensure_cache_loaded(self) -> None:
        """
        Ensure cache is loaded and valid.
        Reloads from database if cache is expired.
        
        Principle 5: Async operation
        """
        if not self._is_cache_valid():
            await self.sync_stability_data()
    
    def _clear_cache(self) -> None:
        """Clear all cached data"""
        self._distribution_cache.clear()
        self._stability_cache = None
        self._mutualism_cache.clear()
        self._cache_timestamp = None
    
    # ==================== CORE FUNCTIONALITY ====================
    # Principle 5: All I/O operations are async
    
    async def sync_stability_data(self) -> None:
        """
        Synchronize stability and distribution data from database.
        
        This is the primary data loading method that populates the cache
        with current stability metrics, distribution states, and mutualism data.
        
        Principle 4: Database as single source of truth
        Principle 5: Async operation
        Principle 7: Per-asset monitoring
        
        Raises:
            Exception: If database query fails
        """
        try:
            self.logger.info(f"Syncing stability data for {self.asset_code}...")
            
            # Track operation for health checks
            self._last_sync_time = datetime.now()
            self._sync_count += 1
            
            # Use rate limiter for database queries
            await self.rate_limiter.acquire()
            
            # Query distribution state from database
            distribution_query = """
                SELECT 
                    category,
                    current_amount,
                    target_amount,
                    target_percentage,
                    actual_percentage,
                    (actual_percentage - target_percentage) as deviation,
                    compliance_status
                FROM ubec_main.distribution_state
                WHERE asset_code = $1
                ORDER BY category
            """
            
            distribution_rows = await self.db_manager.fetch(
                distribution_query,
                self.asset_code
            )
            
            # Update distribution cache
            self._distribution_cache.clear()
            for row in distribution_rows:
                category = DistributionCategory(row['category'])
                state = DistributionState(
                    category=category,
                    current_amount=Decimal(str(row['current_amount'])),
                    target_amount=Decimal(str(row['target_amount'])),
                    target_percentage=Decimal(str(row['target_percentage'])),
                    actual_percentage=Decimal(str(row['actual_percentage'])),
                    deviation=Decimal(str(row['deviation'])),
                    compliance_status=ComplianceStatus(row['compliance_status'])
                )
                self._distribution_cache[category] = state
            
            # Query stability metrics from database
            stability_query = """
                SELECT 
                    total_supply,
                    circulating_supply,
                    distribution_health,
                    balance_concentration,
                    holder_count,
                    median_balance,
                    stability_index,
                    compliance_score
                FROM ubec_main.stability_metrics
                WHERE asset_code = $1
                ORDER BY calculated_at DESC
                LIMIT 1
            """
            
            stability_row = await self.db_manager.fetchrow(
                stability_query,
                self.asset_code
            )
            
            if stability_row:
                self._stability_cache = StabilityMetrics(
                    total_supply=Decimal(str(stability_row['total_supply'])),
                    circulating_supply=Decimal(str(stability_row['circulating_supply'])),
                    distribution_health=float(stability_row['distribution_health']),
                    balance_concentration=float(stability_row['balance_concentration']),
                    holder_count=int(stability_row['holder_count']),
                    median_balance=Decimal(str(stability_row['median_balance'])),
                    stability_index=float(stability_row['stability_index']),
                    compliance_score=float(stability_row['compliance_score'])
                )
            
            # Query mutualism relationships from database
            mutualism_query = """
                SELECT 
                    account_a,
                    account_b,
                    interaction_count,
                    mutual_benefit_score,
                    relationship_strength,
                    last_interaction
                FROM ubec_main.mutualism_relationships
                WHERE asset_code = $1
                    AND relationship_strength > 0.5
                ORDER BY relationship_strength DESC
                LIMIT 100
            """
            
            mutualism_rows = await self.db_manager.fetch(
                mutualism_query,
                self.asset_code
            )
            
            self._mutualism_cache = [
                MutualismRelationship(
                    account_a=row['account_a'],
                    account_b=row['account_b'],
                    interaction_count=int(row['interaction_count']),
                    mutual_benefit_score=float(row['mutual_benefit_score']),
                    relationship_strength=float(row['relationship_strength']),
                    last_interaction=row['last_interaction']
                )
                for row in mutualism_rows
            ]
            
            # Update cache timestamp
            self._cache_timestamp = datetime.now()
            self._initialized = True
            
            self.logger.info(
                f"✓ Stability data synced: "
                f"{len(self._distribution_cache)} categories, "
                f"{len(self._mutualism_cache)} relationships"
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error syncing stability data: {e}")
            raise
    
    async def check_distribution_compliance(self) -> Dict[DistributionCategory, DistributionState]:
        """
        Check compliance of current distribution against targets.
        
        Returns:
            Dictionary mapping categories to their distribution states
            
        Example:
            >>> compliance = await service.check_distribution_compliance()
            >>> for category, state in compliance.items():
            ...     print(f"{category.value}: {state.compliance_status.value}")
            ...     print(f"  Deviation: {state.deviation:.2%}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            return dict(self._distribution_cache)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error checking distribution compliance: {e}")
            raise
    
    async def get_stability_metrics(self) -> Optional[StabilityMetrics]:
        """
        Get current stability metrics for the Earth element.
        
        Returns:
            StabilityMetrics object with current metrics, or None if unavailable
            
        Example:
            >>> metrics = await service.get_stability_metrics()
            >>> if metrics:
            ...     print(f"Stability Index: {metrics.stability_index:.2%}")
            ...     print(f"Holder Count: {metrics.holder_count}")
            ...     print(f"Compliance Score: {metrics.compliance_score:.2%}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Comprehensive monitoring
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            return self._stability_cache
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error getting stability metrics: {e}")
            raise
    
    async def get_mutualism_relationships(
        self,
        min_strength: float = 0.5
    ) -> List[MutualismRelationship]:
        """
        Get mutualistic relationships between accounts.
        
        Args:
            min_strength: Minimum relationship strength to include (0.0 - 1.0)
            
        Returns:
            List of mutualism relationships above the minimum strength
            
        Example:
            >>> relationships = await service.get_mutualism_relationships(min_strength=0.7)
            >>> for rel in relationships:
            ...     print(f"{rel.account_a} <-> {rel.account_b}")
            ...     print(f"  Strength: {rel.relationship_strength:.2%}")
            ...     print(f"  Benefit: {rel.mutual_benefit_score:.2%}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Relationship monitoring
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            # Filter by minimum strength
            return [
                rel for rel in self._mutualism_cache
                if rel.relationship_strength >= min_strength
            ]
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error getting mutualism relationships: {e}")
            raise
    
    async def calculate_account_stability(self, account_id: str) -> Dict[str, Any]:
        """
        Calculate stability metrics for a specific account.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            Dictionary with stability metrics for the account
            
        Example:
            >>> stability = await service.calculate_account_stability('GXXX...')
            >>> print(f"Balance: {stability['balance']}")
            >>> print(f"Stability Score: {stability['stability_score']:.2%}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            await self.rate_limiter.acquire()
            
            # Query account-specific stability from database
            query = """
                SELECT 
                    balance,
                    balance_percentile,
                    transaction_count,
                    last_transaction_date,
                    stability_score,
                    mutualism_score
                FROM ubec_main.account_stability
                WHERE account_id = $1 AND asset_code = $2
            """
            
            row = await self.db_manager.fetchrow(query, account_id, self.asset_code)
            
            if not row:
                return {
                    'account_id': account_id,
                    'balance': Decimal('0'),
                    'stability_score': 0.0,
                    'found': False
                }
            
            return {
                'account_id': account_id,
                'balance': Decimal(str(row['balance'])),
                'balance_percentile': float(row['balance_percentile']),
                'transaction_count': int(row['transaction_count']),
                'last_transaction_date': row['last_transaction_date'],
                'stability_score': float(row['stability_score']),
                'mutualism_score': float(row['mutualism_score']),
                'found': True
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error calculating account stability: {e}")
            raise
    
    # ==================== HEALTH CHECK ====================
    # Principle 12: Method Singularity - Uses shared ServiceHealthCheck utility
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check using standardized ServiceHealthCheck utility.
        
        This method implements Principle #12 (Method Singularity) by delegating
        to the shared ServiceHealthCheck utility instead of implementing custom
        health check logic.
        
        Returns:
            Health status dictionary with standardized format
            
        Example:
            >>> health = await service.health_check()
            >>> print(f"Status: {health['status']}")
            >>> print(f"Initialized: {health['checks']['initialized']}")
        
        Design Notes:
            - Principle 12: Uses ServiceHealthCheck.api_dependent_health()
            - Principle 7: Comprehensive monitoring through standard checks
            - Principle 10: Separation of concerns - health logic in utility
        """
        return await ServiceHealthCheck.api_dependent_health(
            service=self,
            service_name="Earth Protocol (UBECgpi)",
            required_attributes={
                'db_manager': 'Database manager',
                'config': 'Configuration',
                'asset_code': 'Asset code',
                'issuer': 'Issuer address'
            },
            optional_attributes={
                'stellar_client': 'Stellar client'
            }
        )
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    # Principle 10: Clear Separation of Concerns
    
    async def close(self) -> None:
        """
        Clean up service resources.
        
        Called during shutdown to release resources and cleanup caches.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("Closing Earth protocol service...")
        self._clear_cache()
        self._initialized = False
        self.logger.info("Earth protocol service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

def create_ubecgpi_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECgpiProtocolService:
    """
    Factory function to create UBECgpi Earth protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    
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
        >>> service = create_ubecgpi_service(
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
        "  service = create_ubecgpi_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  await service.sync_stability_data()\n\n"
        "Version 2.2.0 - Standardized Health Check Pattern:\n"
        "  - Uses ServiceHealthCheck.api_dependent_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Consistent health checks across all services\n"
        "  - Cleaner, more maintainable code\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
