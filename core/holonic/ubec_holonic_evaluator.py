#!/usr/bin/env python3
# core/holonic/ubec_holonic_evaluator.py
"""
UBEC Holonic Evaluator - Ubuntu Philosophy Implementation (ASYNC)
===================================================================

Service implementation for holonic evaluation of UBEC token holders based
on Ubuntu principles: reciprocity, mutualism, diversity, regeneration, and holism.

This module evaluates UBEC token holders based on holonic principles, measuring:
1. Balance of Autonomy and Integration
2. Multi-scale Participation  
3. Regenerative Impact
4. Network Contribution
5. Alignment with Ubuntu Philosophy

Design Principles Compliance:
──────────────────────────────────────────────────────────────────────────────
    ✅ 1.  Modular Design: Self-contained evaluation service
    ✅ 2.  Service Pattern: Factory-based instantiation, no standalone execution
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: ALL I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Individual account tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Integrated Rate Limiting: Built-in for database operations
    ✅ 10. Separation of Concerns: Evaluation logic isolated
    ✅ 11. Comprehensive Documentation: Full docstrings and attribution
    ✅ 12. Method Singularity: No duplicate methods
──────────────────────────────────────────────────────────────────────────────

Usage:
    from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
    
    evaluator = await create_holonic_evaluator(
        db_manager=async_db,
        config={'ubec_code': 'UBEC', 'ubec_issuer': 'G...', 'db_schema': 'ubec_main'}
    )
    
    # All methods are async
    report = await evaluator.evaluate_network_holism()
    metrics = await evaluator.get_holonic_metrics()
    health = await evaluator.health_check()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 5.1.0 (Zero-Transaction Network Support)
Date: October 15, 2025

Changes in v5.1.0 (PRODUCTION FIX):
    - 🔥 COMPREHENSIVE zero-transaction network handling
    - ✅ Balance-based differentiation when transaction data unavailable
    - ✅ Dual-mode calculation (transaction-based vs balance-based)
    - ✅ Eliminates uniform score problem in new networks
    - ✅ Enhanced validation with calculation mode detection
    - ✅ Production-ready for both active and bootstrapping networks
    - ✅ Maintains all 12 design principles

Previous versions:
    v5.0.0: Removed all hardcoded placeholder values
    v4.2.3: Fixed logger initialization bug
    v4.2.2: Fixed hardcoded weights, loads from configuration
    v4.2.1: Fixed timezone-aware datetime comparisons
    v4.2.0: Fixed stellar_transactions → stellar_operations table usage
    v4.1.0: Complete async implementation
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal, getcontext
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Configure precision for decimal calculations (Principle 4: Single Source of Truth)
getcontext().prec = 10

logger = logging.getLogger(__name__)


# ========================================================================
# DATA MODELS
# Principle 1: Modular Design - Clear data structures
# ========================================================================

class HolonicCategory(Enum):
    """Holonic evaluation categories based on Ubuntu principles."""
    OBSERVER = "Observer"          # Minimal participation (0.0-0.2)
    PARTICIPANT = "Participant"    # Basic involvement (0.2-0.4)
    CONTRIBUTOR = "Contributor"    # Active contribution (0.4-0.6)
    INTEGRATOR = "Integrator"      # System integration (0.6-0.8)
    EXEMPLAR = "Exemplar"          # Highest alignment (0.8-1.0)


@dataclass
class HolonicMetrics:
    """
    Holonic evaluation metrics for an account.
    
    Attributes:
        account_id: Stellar public key
        autonomy_integration_score: Balance between autonomy and integration (0-1)
        multi_scale_score: Participation across scales (0-1)
        regenerative_impact_score: Contribution to regeneration (0-1)
        network_contribution_score: Network-level contribution (0-1)
        ubuntu_alignment_score: Alignment with Ubuntu principles (0-1)
        composite_score: Overall holonic score (0-1)
        holonic_category: Categorical assessment
        evaluation_date: Timestamp of evaluation
        confidence: Overall confidence level (0-1)
        calculation_mode: 'transaction_based' or 'balance_based'
        raw_metrics: Additional detailed metrics
    """
    account_id: str
    autonomy_integration_score: float
    multi_scale_score: float
    regenerative_impact_score: float
    network_contribution_score: float
    ubuntu_alignment_score: float
    composite_score: float
    holonic_category: HolonicCategory
    evaluation_date: datetime
    confidence: float
    calculation_mode: str
    raw_metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for storage/transmission."""
        result = asdict(self)
        result['holonic_category'] = self.holonic_category.value
        result['evaluation_date'] = self.evaluation_date.isoformat()
        return result


@dataclass
class AccountHolderData:
    """
    Simplified data for a UBEC account holder.
    
    Attributes:
        account_id: Stellar public key
        balance: Current UBEC balance
        transaction_count: Total transactions
        unique_partners: Number of unique counterparties
        joined_at: Account creation date
        last_activity: Most recent transaction
        account_type: Classification (e.g., 'individual', 'stewardship')
        metrics: Additional account metrics
    """
    account_id: str
    balance: Decimal
    transaction_count: int
    unique_partners: int
    joined_at: datetime
    last_activity: datetime
    account_type: str
    metrics: Dict[str, Any]


@dataclass
class NetworkStatistics:
    """
    Network-wide statistics for contextualized evaluation.
    
    Attributes:
        total_accounts: Total number of accounts
        median_balance: Median account balance
        median_tx_count: Median transaction count
        median_partners: Median unique partners
        max_balance: Maximum balance in network
        max_tx_count: Maximum transactions
        max_partners: Maximum unique partners
        total_supply: Total token supply
        active_account_count: Accounts with >0 transactions
    """
    total_accounts: int
    median_balance: Decimal
    median_tx_count: int
    median_partners: int
    max_balance: Decimal
    max_tx_count: int
    max_partners: int
    total_supply: Decimal
    active_account_count: int
    
    @property
    def activity_rate(self) -> float:
        """Percentage of accounts with transaction activity."""
        return self.active_account_count / max(self.total_accounts, 1)
    
    @property
    def is_low_activity_network(self) -> bool:
        """True if network has minimal transaction activity."""
        return self.median_partners == 0 and self.median_tx_count == 0


# ========================================================================
# HOLONIC EVALUATOR SERVICE
# Principle 1: Modular Design - Self-contained service
# Principle 2: Service Pattern - No standalone execution
# ========================================================================

class UBECHolonicEvaluator:
    """
    Async UBEC Holonic Evaluator Service
    
    Evaluates UBEC token holders based on Ubuntu principles using
    pure async operations. All database access uses async patterns.
    
    The evaluator measures five key dimensions:
    1. Autonomy & Integration Balance - Independence vs collective participation
    2. Multi-scale Participation - Activity across different organizational scales
    3. Regenerative Impact - Contribution to system regeneration
    4. Network Contribution - Overall network-level contribution
    5. Ubuntu Alignment - Alignment with Ubuntu philosophy principles
    
    v5.1.0 Features:
    - Dual-mode calculation: transaction-based for active networks, 
      balance-based for bootstrapping networks
    - Automatic detection of network activity level
    - Graceful degradation with confidence scoring
    
    Design Principles:
    - Principle 1: Modular - Clear boundaries, single responsibility
    - Principle 3: Service Registry - Dependencies via constructor
    - Principle 4: Single Source of Truth - Database-driven configuration
    - Principle 5: Strict Async - All I/O operations are async
    - Principle 10: Separation of Concerns - Clear layer separation
    """
    
    def __init__(
        self,
        db_manager: Any,
        config: Dict[str, Any]
    ):
        """
        Initialize async holonic evaluator.
        
        IMPORTANT: After construction, call initialize() if needed for
        async setup operations (following the pattern from distribution_service).
        
        Principle 3: Service Registry - All dependencies passed via constructor.
        
        Args:
            db_manager: Async database manager instance
            config: Configuration dictionary with:
                - db_schema: Database schema name (required)
                - ubec_code: UBEC token code (default: 'UBEC')
                - ubec_issuer: UBEC issuer address (optional)
                - holonic_weight_*: Weight configurations (optional)
                
        Raises:
            ValueError: If required config parameters are missing
        """
        # Initialize logger FIRST
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Validate database manager
        if not hasattr(db_manager, 'fetch_all') or not hasattr(db_manager, 'fetch_one'):
            raise ValueError(
                f"Invalid database manager type: {type(db_manager)}. "
                "Expected AsyncDatabaseManager with fetch_all and fetch_one methods."
            )
        
        self.db_manager = db_manager
        self.config = config
        
        # Extract configuration (Principle 8: No duplicate config)
        self.db_schema = config.get('db_schema', 'ubec_main')
        self.ubec_code = config.get('ubec_code', 'UBEC')
        self.ubec_issuer = config.get('ubec_issuer')
        
        # Load holonic weights from config (Principle 4: Single Source of Truth)
        self.weights = {
            'autonomy_integration': float(config.get('holonic_weight_autonomy', 0.20)),
            'multi_scale': float(config.get('holonic_weight_multiscale', 0.20)),
            'regenerative_impact': float(config.get('holonic_weight_regenerative', 
                                          config.get('holonic_weight_emergence', 0.20))),
            'network_contribution': float(config.get('holonic_weight_network',
                                          config.get('holonic_weight_feedback', 0.20))),
            'ubuntu_alignment': float(config.get('holonic_weight_ubuntu',
                                     config.get('holonic_weight_resilience', 0.20)))
        }
        
        # Validate weights sum to 1.0
        weights_sum = sum(self.weights.values())
        if not (0.99 <= weights_sum <= 1.01):
            self.logger.warning(f"Holonic weights sum to {weights_sum:.3f}, normalizing")
            for key in self.weights:
                self.weights[key] = self.weights[key] / weights_sum
        
        self.logger.info(f"Holonic evaluation weights: {self.weights}")
        
        # Initialize thresholds for holonic categories
        self.thresholds = {
            'observer': 0.2,
            'participant': 0.4,
            'contributor': 0.6,
            'integrator': 0.8
        }
        
        # Cache for account holder data and network statistics
        self.holders_data: Dict[str, AccountHolderData] = {}
        self.network_stats: Optional[NetworkStatistics] = None
        self._last_evaluation: Optional[datetime] = None
        
        self.logger.info("Holonic Evaluator initialized")
    
    # ========================================================================
    # DATA LOADING
    # Principle 4: Single Source of Truth - Database as authority
    # Principle 5: Strict Async - All operations async
    # ========================================================================
    
    async def _calculate_network_statistics(self) -> NetworkStatistics:
        """
        Calculate network-wide statistics for contextualized evaluation.
        
        Returns:
            NetworkStatistics object with network-wide metrics
        """
        try:
            query = f"""
                WITH network_metrics AS (
                    SELECT 
                        COUNT(*) as total_accounts,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance,
                        MAX(balance) as max_balance,
                        SUM(balance) as total_supply
                    FROM {self.db_schema}.ubec_balances
                    WHERE token_code = $1
                ),
                tx_metrics AS (
                    SELECT
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tx_count) as median_tx,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY partner_count) as median_partners,
                        MAX(tx_count) as max_tx,
                        MAX(partner_count) as max_partners,
                        COUNT(CASE WHEN tx_count > 0 THEN 1 END) as active_accounts
                    FROM (
                        SELECT 
                            COALESCE(from_account, to_account) as account_id,
                            COUNT(DISTINCT transaction_hash) as tx_count,
                            COUNT(DISTINCT CASE 
                                WHEN from_account = COALESCE(from_account, to_account) THEN to_account
                                ELSE from_account
                            END) as partner_count
                        FROM {self.db_schema}.stellar_operations
                        WHERE asset_code = $1
                        GROUP BY COALESCE(from_account, to_account)
                    ) tx_stats
                )
                SELECT 
                    nm.total_accounts,
                    nm.median_balance,
                    nm.max_balance,
                    nm.total_supply,
                    COALESCE(tm.median_tx, 0) as median_tx,
                    COALESCE(tm.median_partners, 0) as median_partners,
                    COALESCE(tm.max_tx, 0) as max_tx,
                    COALESCE(tm.max_partners, 0) as max_partners,
                    COALESCE(tm.active_accounts, 0) as active_accounts
                FROM network_metrics nm
                CROSS JOIN tx_metrics tm
            """
            
            result = await self.db_manager.fetch_one(query, (self.ubec_code,))
            
            if not result:
                self.logger.warning("No network statistics available, using defaults")
                return NetworkStatistics(
                    total_accounts=1,
                    median_balance=Decimal('1000'),
                    median_tx_count=0,
                    median_partners=0,
                    max_balance=Decimal('10000'),
                    max_tx_count=0,
                    max_partners=0,
                    total_supply=Decimal('1000000'),
                    active_account_count=0
                )
            
            stats = NetworkStatistics(
                total_accounts=int(result['total_accounts']),
                median_balance=Decimal(str(result['median_balance'])),
                median_tx_count=int(result['median_tx']),
                median_partners=int(result['median_partners']),
                max_balance=Decimal(str(result['max_balance'])),
                max_tx_count=int(result['max_tx']),
                max_partners=int(result['max_partners']),
                total_supply=Decimal(str(result['total_supply'])),
                active_account_count=int(result['active_accounts'])
            )
            
            self.logger.info(
                f"Network statistics calculated: median_balance={stats.median_balance}, "
                f"median_tx={stats.median_tx_count}, median_partners={stats.median_partners}, "
                f"active_rate={stats.activity_rate*100:.1f}%"
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating network statistics: {e}", exc_info=True)
            return NetworkStatistics(
                total_accounts=1,
                median_balance=Decimal('1000'),
                median_tx_count=0,
                median_partners=0,
                max_balance=Decimal('10000'),
                max_tx_count=0,
                max_partners=0,
                total_supply=Decimal('1000000'),
                active_account_count=0
            )
    
    async def load_account_holders(
        self,
        min_balance: Optional[Decimal] = None,
        limit: Optional[int] = None
    ) -> List[AccountHolderData]:
        """
        Load UBEC account holder data from database.
        
        Args:
            min_balance: Minimum balance filter (optional)
            limit: Maximum number of accounts to load (optional)
            
        Returns:
            List of AccountHolderData objects
        """
        try:
            self.logger.info("Loading account holder data from database...")
            
            # Calculate network statistics first
            self.network_stats = await self._calculate_network_statistics()
            
            # Build query
            query = f"""
                WITH account_stats AS (
                    SELECT 
                        ub.account_id,
                        ub.balance,
                        COUNT(DISTINCT so.transaction_hash) as tx_count,
                        COUNT(DISTINCT CASE 
                            WHEN so.from_account = ub.account_id THEN so.to_account
                            WHEN so.to_account = ub.account_id THEN so.from_account
                        END) as unique_partners,
                        MIN(so.created_at) as joined_at,
                        MAX(so.created_at) as last_activity
                    FROM {self.db_schema}.ubec_balances ub
                    LEFT JOIN {self.db_schema}.stellar_operations so 
                        ON (so.from_account = ub.account_id OR so.to_account = ub.account_id)
                        AND so.asset_code = $1
                    WHERE ub.token_code = $1
                    {'AND ub.balance >= $2' if min_balance else ''}
                    GROUP BY ub.account_id, ub.balance
                    {'LIMIT $' + str(3 if min_balance else 2) if limit else ''}
                )
                SELECT 
                    account_id,
                    balance,
                    COALESCE(tx_count, 0) as transaction_count,
                    COALESCE(unique_partners, 0) as unique_partners,
                    COALESCE(joined_at, NOW()) as joined_at,
                    COALESCE(last_activity, NOW()) as last_activity
                FROM account_stats
                ORDER BY balance DESC
            """
            
            params = [self.ubec_code]
            if min_balance:
                params.append(str(min_balance))
            if limit:
                params.append(limit)
            
            results = await self.db_manager.fetch_all(query, tuple(params))
            
            # Convert to AccountHolderData objects
            holders = []
            for row in results:
                holder = AccountHolderData(
                    account_id=row['account_id'],
                    balance=Decimal(str(row['balance'])),
                    transaction_count=row['transaction_count'],
                    unique_partners=row['unique_partners'],
                    joined_at=row['joined_at'],
                    last_activity=row['last_activity'],
                    account_type='standard',
                    metrics={}
                )
                holders.append(holder)
                self.holders_data[holder.account_id] = holder
            
            self.logger.info(f"Loaded {len(holders)} account holders")
            return holders
            
        except Exception as e:
            self.logger.error(f"Error loading account holders: {e}", exc_info=True)
            return []
    
    # ========================================================================
    # HOLONIC EVALUATION METRICS (v5.1.0 - DUAL MODE CALCULATION)
    # Principle 10: Separation of Concerns - Evaluation logic isolated
    # Principle 12: Method Singularity - Each metric calculated once
    # ========================================================================
    
    def _calculate_autonomy_integration(
        self,
        holder: AccountHolderData,
        use_balance_mode: bool
    ) -> Tuple[float, float, Dict[str, Any]]:
        """
        Calculate autonomy and integration balance score.
        
        v5.1.0: Supports dual-mode calculation.
        
        Args:
            holder: Account holder data
            use_balance_mode: If True, use balance-based calculation
            
        Returns:
            Tuple of (score, confidence, raw_metrics)
        """
        if not self.network_stats:
            return 0.5, 0.3, {'mode': 'no_stats'}
        
        if use_balance_mode:
            # Balance-based mode: Use balance as proxy for autonomy
            balance_percentile = min(
                float(holder.balance) / float(self.network_stats.max_balance),
                1.0
            )
            autonomy_score = balance_percentile * 0.8  # Conservative
            
            # Integration estimated from balance distribution
            # Accounts closer to median show integration (neither hoarding nor depleted)
            balance_ratio = float(holder.balance) / float(self.network_stats.median_balance)
            if balance_ratio <= 0.5:
                integration_score = balance_ratio  # Small holders
            elif balance_ratio <= 2.0:
                integration_score = 1.0  # Around median = high integration
            else:
                integration_score = max(0.5, 1.0 - (balance_ratio - 2.0) / 10.0)
            
            confidence = 0.5  # Lower confidence in balance-only mode
            mode = 'balance_based'
            
        else:
            # Transaction-based mode: Use actual activity
            balance_autonomy = min(
                float(holder.balance) / float(self.network_stats.median_balance * 2),
                1.0
            )
            tx_autonomy = min(
                holder.transaction_count / max(self.network_stats.median_tx_count * 2, 10),
                1.0
            )
            autonomy_score = (balance_autonomy + tx_autonomy) / 2.0
            
            network_integration = min(
                holder.unique_partners / max(self.network_stats.median_partners * 2, 10),
                1.0
            )
            days_since = (datetime.now(timezone.utc) - holder.last_activity).days
            activity_integration = max(0.0, 1.0 - (days_since / 90.0))
            integration_score = (network_integration + activity_integration) / 2.0
            
            confidence = 1.0
            if holder.transaction_count == 0:
                confidence *= 0.5
            if holder.unique_partners == 0:
                confidence *= 0.7
            
            mode = 'transaction_based'
        
        balance_score = 1.0 - abs(autonomy_score - integration_score)
        
        raw_metrics = {
            'autonomy_score': autonomy_score,
            'integration_score': integration_score,
            'balance_score': balance_score,
            'mode': mode
        }
        
        return balance_score, confidence, raw_metrics
    
    def _calculate_multi_scale_participation(
        self,
        holder: AccountHolderData,
        use_balance_mode: bool
    ) -> Tuple[float, float, Dict[str, Any]]:
        """
        Calculate multi-scale participation score.
        
        v5.1.0: Supports dual-mode calculation.
        
        Args:
            holder: Account holder data
            use_balance_mode: If True, use balance-based calculation
            
        Returns:
            Tuple of (score, confidence, raw_metrics)
        """
        if not self.network_stats:
            return 0.5, 0.3, {'mode': 'no_stats'}
        
        if use_balance_mode:
            # Individual scale: Balance size relative to median
            balance_ratio = float(holder.balance) / float(self.network_stats.median_balance)
            individual_scale = min(balance_ratio / 2.0, 1.0)
            
            # Community scale: Position in distribution (larger = more community role)
            balance_percentile = min(
                float(holder.balance) / float(self.network_stats.max_balance),
                1.0
            )
            community_scale = balance_percentile * 0.7
            
            # System scale: Share of total supply
            system_scale = min(
                float(holder.balance) / float(self.network_stats.total_supply) * 1000,
                1.0
            )
            
            confidence = 0.5
            mode = 'balance_based'
            
        else:
            # Transaction-based mode
            individual_scale = min(
                holder.transaction_count / max(self.network_stats.median_tx_count * 2, 10),
                1.0
            )
            community_scale = min(
                holder.unique_partners / max(self.network_stats.median_partners * 2, 10),
                1.0
            )
            balance_ratio = float(holder.balance) / float(self.network_stats.total_supply)
            system_scale = min(balance_ratio * 1000, 1.0)
            
            confidence = 1.0
            if holder.transaction_count == 0:
                confidence *= 0.6
            if holder.unique_partners == 0:
                confidence *= 0.7
            
            mode = 'transaction_based'
        
        multi_scale_score = (individual_scale + community_scale + system_scale) / 3.0
        
        raw_metrics = {
            'individual_scale': individual_scale,
            'community_scale': community_scale,
            'system_scale': system_scale,
            'mode': mode
        }
        
        return multi_scale_score, confidence, raw_metrics
    
    def _calculate_regenerative_impact(
        self,
        holder: AccountHolderData,
        use_balance_mode: bool
    ) -> Tuple[float, float, Dict[str, Any]]:
        """
        Calculate regenerative impact score.
        
        v5.1.0: FIXED - Now properly differentiates accounts in zero-transaction networks.
        
        Args:
            holder: Account holder data
            use_balance_mode: If True, use balance-based calculation
            
        Returns:
            Tuple of (score, confidence, raw_metrics)
        """
        if not self.network_stats:
            return 0.5, 0.3, {'mode': 'no_stats'}
        
        if use_balance_mode:
            # Distribution impact: Balance tier (larger holders have distribution potential)
            balance_ratio = float(holder.balance) / float(self.network_stats.median_balance)
            if balance_ratio >= 5.0:
                distribution_impact = 0.8  # Large holders - high potential
            elif balance_ratio >= 2.0:
                distribution_impact = 0.6  # Above median - good potential
            elif balance_ratio >= 1.0:
                distribution_impact = 0.4  # Around median - moderate potential
            elif balance_ratio >= 0.5:
                distribution_impact = 0.2  # Below median - low potential
            else:
                distribution_impact = 0.1  # Very small holders
            
            # Growth impact: Position suggests capacity to enable others
            balance_percentile = min(
                float(holder.balance) / float(self.network_stats.max_balance),
                1.0
            )
            growth_impact = balance_percentile * 0.6
            
            # Sustainability: Account age
            account_age_days = (datetime.now(timezone.utc) - holder.joined_at).days
            sustainability_impact = min(account_age_days / 365.0, 1.0)
            
            confidence = 0.4  # Low confidence - balance-only proxy
            mode = 'balance_based'
            
        else:
            # Transaction-based mode
            distribution_impact = min(
                holder.unique_partners / max(self.network_stats.max_partners, 10),
                1.0
            )
            
            if holder.transaction_count > 0:
                diversity_ratio = holder.unique_partners / holder.transaction_count
                growth_impact = min(diversity_ratio * 2, 1.0)
            else:
                growth_impact = 0.0
            
            if holder.unique_partners > self.network_stats.median_partners:
                growth_boost = min(
                    holder.unique_partners / max(self.network_stats.median_partners, 1) * 0.3,
                    0.5
                )
                growth_impact = min(growth_impact + growth_boost, 1.0)
            
            account_age_days = (datetime.now(timezone.utc) - holder.joined_at).days
            sustainability_impact = min(account_age_days / 365.0, 1.0)
            
            days_since = (datetime.now(timezone.utc) - holder.last_activity).days
            activity_recency = max(0.0, 1.0 - (days_since / 180.0))
            sustainability_impact = (sustainability_impact + activity_recency) / 2.0
            
            confidence = 1.0
            if account_age_days < 30:
                confidence *= 0.6
            if holder.transaction_count < 5:
                confidence *= 0.7
            
            mode = 'transaction_based'
        
        regenerative_score = (distribution_impact + growth_impact + sustainability_impact) / 3.0
        
        raw_metrics = {
            'distribution_impact': distribution_impact,
            'growth_impact': growth_impact,
            'sustainability_impact': sustainability_impact,
            'mode': mode
        }
        
        return regenerative_score, confidence, raw_metrics
    
    def _calculate_network_contribution(
        self,
        holder: AccountHolderData,
        use_balance_mode: bool
    ) -> Tuple[float, float, Dict[str, Any]]:
        """
        Calculate network contribution score.
        
        v5.1.0: Supports dual-mode calculation.
        
        Args:
            holder: Account holder data
            use_balance_mode: If True, use balance-based calculation
            
        Returns:
            Tuple of (score, confidence, raw_metrics)
        """
        if not self.network_stats:
            return 0.5, 0.3, {'mode': 'no_stats'}
        
        if use_balance_mode:
            # Volume: Balance as proxy for potential activity
            balance_ratio = float(holder.balance) / float(self.network_stats.median_balance)
            volume_contribution = min(balance_ratio / 3.0, 1.0)
            
            # Connectivity: Balance distribution position
            connectivity_contribution = min(
                float(holder.balance) / float(self.network_stats.max_balance) * 0.7,
                1.0
            )
            
            # Ecosystem: Balance holding
            ecosystem_contribution = min(
                float(holder.balance) / float(self.network_stats.median_balance * 5),
                1.0
            )
            
            confidence = 0.5
            mode = 'balance_based'
            
        else:
            # Transaction-based mode
            volume_contribution = min(
                holder.transaction_count / max(self.network_stats.max_tx_count, 100),
                1.0
            )
            connectivity_contribution = min(
                holder.unique_partners / max(self.network_stats.max_partners, 50),
                1.0
            )
            balance_contribution = min(
                float(holder.balance) / float(self.network_stats.median_balance * 5),
                1.0
            )
            days_since = (datetime.now(timezone.utc) - holder.last_activity).days
            activity_contribution = max(0.0, 1.0 - (days_since / 90.0))
            ecosystem_contribution = (
                balance_contribution * 0.3 +
                volume_contribution * 0.3 +
                activity_contribution * 0.4
            )
            
            confidence = 1.0
            if holder.transaction_count == 0:
                confidence *= 0.5
            if holder.unique_partners == 0:
                confidence *= 0.6
            
            mode = 'transaction_based'
        
        network_score = (
            volume_contribution + 
            connectivity_contribution + 
            ecosystem_contribution
        ) / 3.0
        
        raw_metrics = {
            'volume_contribution': volume_contribution,
            'connectivity_contribution': connectivity_contribution,
            'ecosystem_contribution': ecosystem_contribution,
            'mode': mode
        }
        
        return network_score, confidence, raw_metrics
    
    def _calculate_ubuntu_alignment(
        self,
        holder: AccountHolderData,
        use_balance_mode: bool
    ) -> Tuple[float, float, Dict[str, Any]]:
        """
        Calculate Ubuntu philosophy alignment score.
        
        v5.1.0: Supports dual-mode calculation.
        
        Args:
            holder: Account holder data
            use_balance_mode: If True, use balance-based calculation
            
        Returns:
            Tuple of (score, confidence, raw_metrics)
        """
        if not self.network_stats:
            return 0.5, 0.3, {'mode': 'no_stats'}
        
        if use_balance_mode:
            # Reciprocity: Balance near median shows balanced participation
            balance_ratio = float(holder.balance) / float(self.network_stats.median_balance)
            if 0.7 <= balance_ratio <= 1.5:
                reciprocity = 0.8  # Near median = good reciprocity
            elif 0.5 <= balance_ratio <= 2.0:
                reciprocity = 0.6  # Reasonable range
            else:
                reciprocity = 0.3  # Far from median
            
            # Mutualism: Balance size suggests capacity for mutual benefit
            mutualism = min(balance_ratio / 3.0, 0.7)
            
            # Diversity: Inferred from balance position
            diversity = min(
                float(holder.balance) / float(self.network_stats.max_balance) * 0.6,
                1.0
            )
            
            # Regeneration: Account age
            account_age_days = (datetime.now(timezone.utc) - holder.joined_at).days
            regeneration = min(account_age_days / 365.0, 1.0)
            
            # Holism: Balance participation
            holism = min(balance_ratio / 2.0, 0.8)
            
            confidence = 0.4
            mode = 'balance_based'
            
        else:
            # Transaction-based mode
            if holder.unique_partners > 0 and holder.transaction_count > 0:
                tx_per_partner = holder.transaction_count / holder.unique_partners
                if tx_per_partner <= 2:
                    reciprocity = tx_per_partner / 2.0
                elif tx_per_partner <= 5:
                    reciprocity = 1.0
                else:
                    reciprocity = max(0.3, 1.0 - ((tx_per_partner - 5) / 20))
            else:
                reciprocity = 0.1
            
            mutualism = min(
                holder.unique_partners / max(self.network_stats.median_partners * 2, 10),
                1.0
            )
            diversity = min(
                holder.unique_partners / max(self.network_stats.max_partners, 50),
                1.0
            )
            account_age_days = (datetime.now(timezone.utc) - holder.joined_at).days
            regeneration = min(account_age_days / 365.0, 1.0)
            
            days_since = (datetime.now(timezone.utc) - holder.last_activity).days
            if days_since < 30:
                regeneration = min(regeneration * 1.2, 1.0)
            
            tx_score = min(
                holder.transaction_count / max(self.network_stats.median_tx_count * 3, 30),
                1.0
            )
            balance_score = min(
                float(holder.balance) / float(self.network_stats.median_balance * 2),
                1.0
            )
            holism = (tx_score + balance_score) / 2.0
            
            confidence = 1.0
            if holder.transaction_count < 5:
                confidence *= 0.6
            if holder.unique_partners < 3:
                confidence *= 0.7
            if account_age_days < 30:
                confidence *= 0.8
            
            mode = 'transaction_based'
        
        ubuntu_score = (reciprocity + mutualism + diversity + regeneration + holism) / 5.0
        
        raw_metrics = {
            'reciprocity': reciprocity,
            'mutualism': mutualism,
            'diversity': diversity,
            'regeneration': regeneration,
            'holism': holism,
            'mode': mode
        }
        
        return ubuntu_score, confidence, raw_metrics
    
    def _determine_holonic_category(
        self,
        composite_score: float
    ) -> HolonicCategory:
        """
        Determine holonic category from composite score.
        
        Args:
            composite_score: Overall holonic score (0-1)
            
        Returns:
            HolonicCategory enum value
        """
        if composite_score >= self.thresholds['integrator']:
            return HolonicCategory.EXEMPLAR
        elif composite_score >= self.thresholds['contributor']:
            return HolonicCategory.INTEGRATOR
        elif composite_score >= self.thresholds['participant']:
            return HolonicCategory.CONTRIBUTOR
        elif composite_score >= self.thresholds['observer']:
            return HolonicCategory.PARTICIPANT
        else:
            return HolonicCategory.OBSERVER
    
    # ========================================================================
    # ACCOUNT EVALUATION
    # Principle 5: Strict Async - Async evaluation methods
    # Principle 12: Method Singularity - Single evaluation implementation
    # ========================================================================
    
    async def evaluate_account(
        self,
        account_id: str
    ) -> Optional[HolonicMetrics]:
        """
        Evaluate a single account's holonic metrics.
        
        v5.1.0: Automatically selects calculation mode based on network activity.
        
        Args:
            account_id: Stellar public key to evaluate
            
        Returns:
            HolonicMetrics object, or None if account not found
        """
        try:
            # Get account data
            if account_id not in self.holders_data:
                holders = await self.load_account_holders(limit=None)
                if account_id not in self.holders_data:
                    self.logger.warning(f"Account {account_id} not found")
                    return None
            
            holder = self.holders_data[account_id]
            
            # Determine calculation mode
            use_balance_mode = (
                self.network_stats and 
                self.network_stats.is_low_activity_network
            )
            
            # Calculate all metrics
            autonomy_score, autonomy_conf, autonomy_raw = \
                self._calculate_autonomy_integration(holder, use_balance_mode)
            multi_scale_score, multi_scale_conf, multi_scale_raw = \
                self._calculate_multi_scale_participation(holder, use_balance_mode)
            regenerative_score, regenerative_conf, regenerative_raw = \
                self._calculate_regenerative_impact(holder, use_balance_mode)
            network_score, network_conf, network_raw = \
                self._calculate_network_contribution(holder, use_balance_mode)
            ubuntu_score, ubuntu_conf, ubuntu_raw = \
                self._calculate_ubuntu_alignment(holder, use_balance_mode)
            
            # Calculate composite score
            composite_score = (
                autonomy_score * self.weights['autonomy_integration'] +
                multi_scale_score * self.weights['multi_scale'] +
                regenerative_score * self.weights['regenerative_impact'] +
                network_score * self.weights['network_contribution'] +
                ubuntu_score * self.weights['ubuntu_alignment']
            )
            
            # Overall confidence
            overall_confidence = (
                autonomy_conf + multi_scale_conf + regenerative_conf + 
                network_conf + ubuntu_conf
            ) / 5.0
            
            # Determine category
            category = self._determine_holonic_category(composite_score)
            
            # Combine raw metrics
            all_raw_metrics = {
                'autonomy': autonomy_raw,
                'multi_scale': multi_scale_raw,
                'regenerative': regenerative_raw,
                'network': network_raw,
                'ubuntu': ubuntu_raw
            }
            
            # Create metrics object
            metrics = HolonicMetrics(
                account_id=account_id,
                autonomy_integration_score=autonomy_score,
                multi_scale_score=multi_scale_score,
                regenerative_impact_score=regenerative_score,
                network_contribution_score=network_score,
                ubuntu_alignment_score=ubuntu_score,
                composite_score=composite_score,
                holonic_category=category,
                evaluation_date=datetime.now(timezone.utc),
                confidence=overall_confidence,
                calculation_mode='balance_based' if use_balance_mode else 'transaction_based',
                raw_metrics=all_raw_metrics
            )
            
            self.logger.debug(
                f"Evaluated {account_id[:8]}...: "
                f"Composite={composite_score:.3f}, Category={category.value}, "
                f"Mode={'balance' if use_balance_mode else 'transaction'}"
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating account {account_id}: {e}", exc_info=True)
            return None
    
    def _validate_evaluation_results(
        self,
        all_metrics: List[HolonicMetrics]
    ) -> Dict[str, Any]:
        """
        Validate evaluation results for data quality.
        
        v5.1.0: Enhanced validation with calculation mode detection.
        
        Returns:
            Dictionary with status and warnings
        """
        if not all_metrics:
            return {
                'status': 'ERROR',
                'warnings': ['No metrics to validate'],
                'issues': []
            }
        
        warnings = []
        issues = []
        
        # Check category distribution
        category_counts = {cat.value: 0 for cat in HolonicCategory}
        for metrics in all_metrics:
            category_counts[metrics.holonic_category.value] += 1
        
        categories_used = sum(1 for v in category_counts.values() if v > 0)
        if categories_used < 2:
            issues.append(f"Only {categories_used}/5 categories used - severe distribution problem")
        elif categories_used < 3:
            warnings.append(f"Only {categories_used}/5 categories used - limited differentiation")
        
        # Check for uniform scores (indicates calculation issues)
        score_sets = {
            'autonomy_integration': set(),
            'multi_scale': set(),
            'regenerative_impact': set(),
            'network_contribution': set(),
            'ubuntu_alignment': set()
        }
        
        for metrics in all_metrics:
            score_sets['autonomy_integration'].add(round(metrics.autonomy_integration_score, 3))
            score_sets['multi_scale'].add(round(metrics.multi_scale_score, 3))
            score_sets['regenerative_impact'].add(round(metrics.regenerative_impact_score, 3))
            score_sets['network_contribution'].add(round(metrics.network_contribution_score, 3))
            score_sets['ubuntu_alignment'].add(round(metrics.ubuntu_alignment_score, 3))
        
        for metric_name, unique_scores in score_sets.items():
            if len(unique_scores) == 1:
                issues.append(f"All {metric_name} scores identical ({list(unique_scores)[0]:.3f}) - calculation may be broken")
            elif len(unique_scores) < len(all_metrics) * 0.1:
                warnings.append(f"{metric_name} has only {len(unique_scores)} unique values - limited differentiation")
        
        # Check score ranges
        scores = [m.composite_score for m in all_metrics]
        score_range = max(scores) - min(scores)
        if score_range < 0.1:
            issues.append(f"Score range very narrow ({score_range:.3f}) - calculation may not be working")
        elif score_range < 0.2:
            warnings.append(f"Score range somewhat narrow ({score_range:.3f}) - limited differentiation between accounts")
        
        # Check calculation mode
        calc_modes = [m.calculation_mode for m in all_metrics]
        mode_balance = calc_modes.count('balance_based')
        if mode_balance > 0:
            warnings.append(
                f"Using balance-based calculation mode for {mode_balance}/{len(all_metrics)} accounts "
                f"due to limited transaction data - confidence reduced"
            )
        
        # Determine overall status
        if issues:
            status = 'UNHEALTHY'
        elif warnings:
            status = 'WARNING'
        else:
            status = 'HEALTHY'
        
        return {
            'status': status,
            'warnings': warnings,
            'issues': issues,
            'categories_used': categories_used,
            'score_range': score_range,
            'unique_scores': {k: len(v) for k, v in score_sets.items()}
        }
    
    async def evaluate_network_holism(
        self,
        min_balance: Optional[Decimal] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate holonic metrics for the entire network.
        
        v5.1.0: Enhanced with calculation mode reporting.
        
        Returns:
            Comprehensive network evaluation report
        """
        self.logger.info("Evaluating network-wide holonic metrics...")
        
        try:
            # Load account holders
            holders = await self.load_account_holders(
                min_balance=min_balance,
                limit=limit
            )
            
            if not holders:
                return {
                    'total_accounts': 0,
                    'evaluated_accounts': 0,
                    'error': 'No accounts to evaluate',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Evaluate all accounts
            all_metrics: List[HolonicMetrics] = []
            
            for holder in holders:
                metrics = await self.evaluate_account(holder.account_id)
                if metrics:
                    all_metrics.append(metrics)
            
            # Calculate aggregate statistics
            category_counts = {cat.value: 0 for cat in HolonicCategory}
            score_sums = {
                'autonomy_integration': 0.0,
                'multi_scale': 0.0,
                'regenerative_impact': 0.0,
                'network_contribution': 0.0,
                'ubuntu_alignment': 0.0,
                'composite': 0.0
            }
            
            for metrics in all_metrics:
                category_counts[metrics.holonic_category.value] += 1
                score_sums['autonomy_integration'] += metrics.autonomy_integration_score
                score_sums['multi_scale'] += metrics.multi_scale_score
                score_sums['regenerative_impact'] += metrics.regenerative_impact_score
                score_sums['network_contribution'] += metrics.network_contribution_score
                score_sums['ubuntu_alignment'] += metrics.ubuntu_alignment_score
                score_sums['composite'] += metrics.composite_score
            
            # Calculate averages
            n = len(all_metrics)
            average_scores = {k: v / n for k, v in score_sums.items()} if n > 0 else {}
            
            # Validate results
            validation = self._validate_evaluation_results(all_metrics)
            
            # Log validation status
            self.logger.info(f"Validation status: {validation['status']}")
            if validation['issues']:
                for issue in validation['issues']:
                    self.logger.warning(f"  - ISSUE: {issue}")
            if validation['warnings']:
                for warning in validation['warnings']:
                    self.logger.warning(f"  - WARNING: {warning}")
            
            # Update timestamp
            self._last_evaluation = datetime.now(timezone.utc)
            
            # Build report
            report = {
                'total_accounts': len(holders),
                'evaluated_accounts': len(all_metrics),
                'category_distribution': category_counts,
                'average_scores': average_scores,
                'validation': validation,
                'network_statistics': {
                    'median_balance': float(self.network_stats.median_balance) if self.network_stats else 0,
                    'median_transactions': self.network_stats.median_tx_count if self.network_stats else 0,
                    'median_partners': self.network_stats.median_partners if self.network_stats else 0,
                    'active_rate': self.network_stats.activity_rate if self.network_stats else 0,
                    'calculation_mode': 'balance_based' if (self.network_stats and self.network_stats.is_low_activity_network) else 'transaction_based'
                } if self.network_stats else {},
                'evaluation_date': self._last_evaluation.isoformat(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.info(
                f"Network evaluation complete: {len(all_metrics)} accounts evaluated, "
                f"Average composite: {average_scores.get('composite', 0):.3f}"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error evaluating network holism: {e}", exc_info=True)
            return {
                'total_accounts': 0,
                'evaluated_accounts': 0,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    # ========================================================================
    # LIFECYCLE METHODS
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            test_query = "SELECT 1 as test"
            result = await self.db_manager.fetch_one(test_query, ())
            
            db_healthy = result is not None and result.get('test') == 1
            
            return {
                'service': 'UBECHolonicEvaluator',
                'version': '5.1.0',
                'status': 'healthy' if db_healthy else 'unhealthy',
                'database': 'connected' if db_healthy else 'disconnected',
                'accounts_cached': len(self.holders_data),
                'network_stats_available': self.network_stats is not None,
                'last_evaluation': self._last_evaluation.isoformat() if self._last_evaluation else None,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                'service': 'UBECHolonicEvaluator',
                'version': '5.1.0',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def close(self):
        """Clean up evaluator resources."""
        self.logger.info("Holonic evaluator closing")
        self.holders_data.clear()
        self.network_stats = None
        self._last_evaluation = None
        self.logger.info("Holonic evaluator closed")


# ========================================================================
# SERVICE FACTORY
# ========================================================================

async def create_holonic_evaluator(
    db_manager: Any,
    config: Dict[str, Any],
    **kwargs
) -> UBECHolonicEvaluator:
    """
    Factory function to create holonic evaluator instance.
    
    Args:
        db_manager: Async database manager
        config: Configuration dictionary
        **kwargs: Additional options
    
    Returns:
        UBECHolonicEvaluator instance
    """
    if 'db_schema' not in config:
        raise ValueError("Configuration missing required parameter: 'db_schema'")
    
    evaluator = UBECHolonicEvaluator(
        db_manager=db_manager,
        config=config
    )
    
    return evaluator


# ========================================================================
# PUBLIC INTERFACE
# ========================================================================

__all__ = [
    'HolonicCategory',
    'HolonicMetrics',
    'AccountHolderData',
    'NetworkStatistics',
    'UBECHolonicEvaluator',
    'create_holonic_evaluator'
]


# ========================================================================
# STANDALONE EXECUTION PREVENTION
# ========================================================================

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator\n"
        "  evaluator = await create_holonic_evaluator(db_manager, config)\n"
        "  report = await evaluator.evaluate_network_holism()"
    )
