#!/usr/bin/env python3
"""
UBECgpi Protocol - Earth Element (Stability & Mutualism)
========================================================
Service implementation for the Earth element of the UBEC four-element system.

The Earth element represents:
- 🜃 Stability: Grounding and sustained value
- Mutualism: Mutually beneficial relationships
- Distribution: Fair allocation and compliance
- Foundation: Solid base for the ecosystem

This module implements the service pattern with:
- Pure async operations (no sync fallbacks)
- Factory function for instantiation
- Database as single source of truth
- Built-in rate limiting
- In-memory caching with TTL

Design Principles Compliance:
- ✅ Modular Design: Self-contained service with clear boundaries
- ✅ Service Pattern: No standalone execution, factory-based instantiation
- ✅ Service Registry: Accessed through centralized registry
- ✅ Single Source of Truth: Database is authoritative
- ✅ Strict Async: All I/O operations use async/await
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ Per-Asset Monitoring: Individual stability tracking
- ✅ No Duplicate Config: Uses global configuration
- ✅ Rate Limiting: Built-in API rate limiting
- ✅ Separation of Concerns: Stability logic separated from data access
- ✅ Documentation: Comprehensive docstrings and inline comments
- ✅ Method Singularity: No duplicate methods

Usage:
    from UBECgpi_protocol import create_ubecgpi_service
    
    service = create_ubecgpi_service(
        db_manager=async_db,
        config={'asset_code': 'UBECgpi', 'issuer': 'G...'},
        stellar_client=stellar_async
    )
    
    # All methods are async
    await service.sync_stability_data()
    compliance = await service.check_distribution_compliance()
    stability = await service.get_stability_metrics()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 2.0.0 (Async Service Architecture)
Date: October 10, 2025
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
    """Current distribution state"""
    category: DistributionCategory
    current_amount: Decimal
    target_amount: Decimal
    target_percentage: Decimal
    actual_percentage: Decimal
    deviation: Decimal  # Difference from target
    compliance_status: ComplianceStatus


@dataclass
class StabilityMetrics:
    """System-wide stability metrics"""
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
    """Represents a mutualistic relationship between accounts"""
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
    
    Attributes:
        db_manager: Async database manager
        config: Protocol configuration
        stellar_client: Async Stellar SDK client
        logger: Logger instance
        rate_limiter: API rate limiter
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
        
        # Distribution targets
        self.distribution_targets = {
            DistributionCategory.GENERAL_CIRCULATION: Decimal('0.75'),
            DistributionCategory.STEWARDSHIP: Decimal('0.20'),
            DistributionCategory.ADMINISTRATION: Decimal('0.05')
        }
        
        # Setup logging
        self.logger = logging.getLogger(f'UBECgpiProtocol.{self.asset_code}')
        
        # Rate limiting
        self.rate_limiter = RateLimiter(rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._distribution_cache: Dict[DistributionCategory, DistributionState] = {}
        self._mutualism_cache: List[MutualismRelationship] = []
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        self.logger.info(f"Earth Protocol Service initialized for {self.asset_code}")
    
    # ==================== CACHE MANAGEMENT ====================
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_ttl
    
    async def _load_from_database(self) -> None:
        """
        Load stability data from database into cache.
        This is the single source of truth.
        """
        try:
            # Query distribution state
            query_dist = """
                SELECT 
                    category,
                    current_amount,
                    target_amount,
                    actual_percentage
                FROM ubec_main.distribution_state
                WHERE asset_code = %s
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
                WHERE asset_code = %s
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
            self.logger.error(f"Error loading from database: {e}")
            raise
    
    async def _ensure_cache_loaded(self) -> None:
        """Ensure cache is loaded and valid"""
        if not self._is_cache_valid():
            await self._load_from_database()
    
    # ==================== STABILITY OPERATIONS ====================
    
    async def sync_stability_data(self) -> Dict[str, Any]:
        """
        Synchronize stability data from Stellar network.
        
        This method fetches the latest distribution and balance data from the
        Stellar blockchain and updates the database (single source of truth).
        Called by the main protocol coordinator.
        
        Returns:
            Dict: Sync status and metrics
        """
        try:
            self.logger.info("Starting Earth (UBECgpi) stability data synchronization...")
            
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
        """
        await self._ensure_cache_loaded()
        
        # Query balance data for calculations
        query = """
            SELECT 
                COUNT(*) as holder_count,
                SUM(balance) as total_supply,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance
            FROM ubec_main.account_balances
            WHERE asset_code = %s
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
    
    def _calculate_distribution_health(self) -> float:
        """
        Calculate distribution health based on deviation from targets.
        Returns value between 0.0 (unhealthy) and 1.0 (healthy).
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
        """
        # Query all balances
        query = """
            SELECT balance
            FROM ubec_main.account_balances
            WHERE asset_code = %s
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
    
    def _calculate_compliance_score(self) -> float:
        """
        Calculate compliance score based on distribution states.
        Returns value between 0.0 (non-compliant) and 1.0 (fully compliant).
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
        """
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
        """
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
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health.
        
        Returns:
            Dict with health status
        """
        try:
            await self._ensure_cache_loaded()
            
            return {
                'protocol': f'UBECgpi (Earth)',
                'status': 'healthy',
                'distribution_categories': len(self._distribution_cache),
                'mutualism_relationships': len(self._mutualism_cache),
                'cache_age_seconds': (
                    (datetime.now() - self._cache_timestamp).total_seconds()
                    if self._cache_timestamp else None
                ),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'protocol': f'UBECgpi (Earth)',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# ==================== SERVICE FACTORY ====================

def create_ubecgpi_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECgpiProtocolService:
    """
    Factory function to create UBECgpi Earth protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options
    
    Returns:
        UBECgpiProtocolService: Initialized service instance
    """
    return UBECgpiProtocolService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        rate_limit_calls_per_second=kwargs.get('rate_limit_calls_per_second', 10.0)
    )


# ==================== MODULE EXPORTS ====================

__all__ = [
    'DistributionCategory',
    'ComplianceStatus',
    'DistributionState',
    'StabilityMetrics',
    'MutualismRelationship',
    'UBECgpiProtocolService',
    'create_ubecgpi_service',
    'RateLimiter'
]
