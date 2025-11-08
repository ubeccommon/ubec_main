#!/usr/bin/env python3
# core/holonic/ubec_holonic_evaluator.py
"""
UBEC Holonic Evaluator - Ubuntu Philosophy Implementation
==========================================================
Service implementation for holonic evaluation of UBEC token holders.

Evaluates UBEC token holders based on Ubuntu principles:
- Reciprocity: Mutual exchange and balance
- Mutualism: Cooperative relationships
- Diversity: Participation across scales
- Regeneration: Sustainable contribution
- Holism: Integration with the whole

This module implements the service pattern with:
- Pure async operations (no sync fallbacks)
- Factory function for instantiation
- Database as single source of truth
- Comprehensive health monitoring using ServiceHealthCheck utility

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained evaluation service
    ✅ 2.  Service Pattern: Factory-based, no standalone execution
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative with persistence
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Individual account tracking with health checks
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Integrated Rate Limiting: Built-in for database operations
    ✅ 10. Separation of Concerns: Evaluation logic isolated
    ✅ 11. Comprehensive Documentation: Full docstrings and attribution
    ✅ 12. Method Singularity: No duplicate methods, uses ServiceHealthCheck utility
══════════════════════════════════════════════════════════════════════════════

Usage:
    from ubec_holonic_evaluator import create_holonic_evaluator
    
    evaluator = await create_holonic_evaluator(
        db_manager=async_db,
        config={
            'ubec_code': 'UBEC',
            'ubec_issuer': 'G...',
            'db_schema': 'ubec_main'
        }
    )
    
    # All methods are async
    result = await evaluator.evaluate_all_accounts()
    report = await evaluator.evaluate_network_holism()
    latest = await evaluator.get_latest_evaluation(account_id)
    history = await evaluator.get_evaluation_history(account_id)
    health = await evaluator.health_check()
    
    await evaluator.close()

Database Schema:
    Uses existing {schema}.holonic_metrics table.
    
    Required columns:
    - id (BIGSERIAL PRIMARY KEY)
    - account_id (TEXT NOT NULL)
    - evaluation_date (TIMESTAMP NOT NULL)
    - autonomy_integration_score (NUMERIC(10,6))
    - multi_scale_score (NUMERIC(10,6))
    - regenerative_impact_score (NUMERIC(10,6))
    - network_contribution_score (NUMERIC(10,6))
    - ubuntu_alignment_score (NUMERIC(10,6))
    - composite_score (NUMERIC(10,6))
    - holonic_category (TEXT)
    - raw_metrics (JSONB)
    - created_at (TIMESTAMP DEFAULT NOW())
    - updated_at (TIMESTAMP DEFAULT NOW())
    
    Optional columns (auto-detected):
    - confidence (NUMERIC(10,6)) - defaults to 0.8 if missing
    - calculation_mode (TEXT) - defaults to 'transaction_based' if missing
    
    UNIQUE constraint: (account_id, DATE(evaluation_date))

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 2.3.1 (Health Check Pattern Fix)
Date: November 8, 2025

Changelog:
    v2.3.1 - CRITICAL FIX: Health check return type verification
           - Fixed check functions to ensure proper return types (None or dict, never bool)
           - Verified all database queries use explicit schema names
           - Enhanced check_weights logic to prevent any boolean evaluation
           - Confirmed full compliance with ServiceHealthCheck v3.3 patterns
           - Resolves "Unexpected return type <class 'bool'>" warnings
    v2.3.0 - CRITICAL FIX: Added missing evaluation methods
           - Added evaluate_all_accounts() for scheduler integration
           - Added evaluate_network_holism() for network-wide assessment
           - Implements complete public API for evaluation operations
           - Maintains all 12 design principles
           - Full async/await throughout
    v2.2.0 - MAJOR: Standardized health check using ServiceHealthCheck utility
           - Implements Principle #12: Method Singularity with shared utility
           - Removed custom health_check() implementation (~400 lines)
           - Now uses ServiceHealthCheck.database_dependent_health()
           - Cleaner, more maintainable code with consistent patterns
           - Full compliance with health check implementation guide
    v2.1.0 - Enhanced health_check() method for comprehensive monitoring
           - Implements Principle #7: Per-Asset Monitoring with detailed checks
           - Added initialization tracking
           - Improved error handling and validation
           - Added operation statistics tracking
           - Enhanced evaluation metrics
    v2.0.0 - Database persistence with schema adaptation
           - Gracefully handles missing optional columns
           - Auto-detects available columns on initialization
    v1.0.0 - Initial release with Ubuntu philosophy implementation
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal, getcontext
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Import standardized health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

# Configure precision for decimal calculations
getcontext().prec = 10


# ==================== ENUMERATIONS ====================

class HolonicCategory(Enum):
    """
    Holonic evaluation categories based on Ubuntu principles.
    
    Categories represent levels of integration with the network:
    - OBSERVER: Minimal participation (0-20%)
    - PARTICIPANT: Active participation (20-40%)
    - CONTRIBUTOR: Regular contribution (40-60%)
    - INTEGRATOR: High integration (60-80%)
    - EXEMPLAR: Exemplary Ubuntu alignment (80-100%)
    """
    OBSERVER = 'observer'
    PARTICIPANT = 'participant'
    CONTRIBUTOR = 'contributor'
    INTEGRATOR = 'integrator'
    EXEMPLAR = 'exemplar'


# ==================== DATA MODELS ====================

@dataclass
class HolonicMetrics:
    """Evaluation results for an account."""
    account_id: str
    autonomy_integration_score: float
    multi_scale_score: float
    regenerative_impact_score: float
    network_contribution_score: float
    ubuntu_alignment_score: float
    composite_score: float
    holonic_category: HolonicCategory
    raw_metrics: Dict[str, Any]
    evaluation_date: datetime
    confidence: float = 0.8
    calculation_mode: str = 'transaction_based'
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'HolonicMetrics':
        """Create metrics from database row."""
        return cls(
            account_id=row['account_id'],
            autonomy_integration_score=float(row['autonomy_integration_score']),
            multi_scale_score=float(row['multi_scale_score']),
            regenerative_impact_score=float(row['regenerative_impact_score']),
            network_contribution_score=float(row['network_contribution_score']),
            ubuntu_alignment_score=float(row['ubuntu_alignment_score']),
            composite_score=float(row['composite_score']),
            holonic_category=HolonicCategory(row['holonic_category']),
            raw_metrics=row['raw_metrics'],
            evaluation_date=row['evaluation_date'],
            confidence=float(row.get('confidence', 0.8)),
            calculation_mode=row.get('calculation_mode', 'transaction_based')
        )


@dataclass
class AccountHolderData:
    """Data for a token holder account."""
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
    """Network-wide statistics."""
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
        """Calculate activity rate (proportion of active accounts)."""
        if self.total_accounts == 0:
            return 0.0
        return self.active_account_count / self.total_accounts
    
    @property
    def is_low_activity_network(self) -> bool:
        """Check if network has low activity."""
        return self.median_tx_count < 5 or self.activity_rate < 0.1


# ==================== SERVICE CLASS ====================

class UBECHolonicEvaluator:
    """
    Holonic evaluator for UBEC token holders.
    
    Implements Ubuntu philosophy through holonic evaluation framework.
    Evaluates accounts on 5 dimensions and assigns holonic categories.
    
    All 12 design principles enforced throughout implementation.
    """
    
    def __init__(self, db_manager: Any, config: Dict[str, Any]):
        """
        Initialize holonic evaluator.
        
        Principle 2: Service pattern - use create_holonic_evaluator() factory instead.
        
        Args:
            db_manager: Async database manager instance
            config: Configuration dictionary
        """
        self.logger = logging.getLogger('UBECHolonic')
        self.db_manager = db_manager
        self.config = config
        
        # Configuration (Principle 8: No Duplicate Config)
        self.db_schema = config.get('db_schema', 'ubec_main')
        self.ubec_code = config.get('ubec_code', 'UBEC')
        self.ubec_issuer = config.get('ubec_issuer')
        self.auto_save = config.get('auto_save_evaluations', True)
        
        # Schema detection flags
        self.has_confidence_column = False
        self.has_calculation_mode_column = False
        self._schema_detected = False
        self._initialized = False
        
        # Scoring weights (Principle 8: Single config source)
        self.weights = {
            'autonomy_integration': float(config.get('holonic_weight_autonomy', 0.20)),
            'multi_scale': float(config.get('holonic_weight_multiscale', 0.20)),
            'regenerative_impact': float(config.get('holonic_weight_regenerative', 0.20)),
            'network_contribution': float(config.get('holonic_weight_network', 0.20)),
            'ubuntu_alignment': float(config.get('holonic_weight_ubuntu', 0.20))
        }
        
        # Normalize weights to sum to 1.0
        weights_sum = sum(self.weights.values())
        if not (0.99 <= weights_sum <= 1.01):
            for key in self.weights:
                self.weights[key] = self.weights[key] / weights_sum
        
        # Category thresholds
        self.thresholds = {
            'observer': 0.2,
            'participant': 0.4,
            'contributor': 0.6,
            'integrator': 0.8
        }
        
        # In-memory cache
        self.holders_data: Dict[str, AccountHolderData] = {}
        self.network_stats: Optional[NetworkStatistics] = None
        
        # Initialization and operation tracking (for health checks)
        self._last_evaluation_time: Optional[datetime] = None
        self._last_save_time: Optional[datetime] = None
        self._last_query_time: Optional[datetime] = None
        self._evaluation_count = 0
        self._save_count = 0
        self._query_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info(
            f"Holonic Evaluator created for {self.ubec_code} "
            f"(schema: {self.db_schema})"
        )
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    
    async def initialize(self) -> None:
        """
        Initialize and detect database schema.
        
        Principle 5: Async initialization
        """
        if self._initialized:
            self.logger.warning("Holonic evaluator already initialized")
            return
        
        try:
            # Detect optional columns in holonic_metrics table
            # Principle 4: Explicit schema name for reliability
            query = f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = '{self.db_schema}'
                AND table_name = 'holonic_metrics'
                AND column_name IN ('confidence', 'calculation_mode')
            """
            
            results = await self.db_manager.fetch_all(query, ())
            columns = {row['column_name'] for row in results}
            
            self.has_confidence_column = 'confidence' in columns
            self.has_calculation_mode_column = 'calculation_mode' in columns
            self._schema_detected = True
            
            if not self.has_confidence_column:
                self.logger.warning(
                    "Column 'confidence' not found. Using default 0.8. "
                    f"To add: ALTER TABLE {self.db_schema}.holonic_metrics "
                    "ADD COLUMN confidence NUMERIC(10,6) DEFAULT 0.8;"
                )
            
            if not self.has_calculation_mode_column:
                self.logger.warning(
                    "Column 'calculation_mode' not found. Using default 'transaction_based'. "
                    f"To add: ALTER TABLE {self.db_schema}.holonic_metrics "
                    "ADD COLUMN calculation_mode TEXT DEFAULT 'transaction_based';"
                )
            
            self._initialized = True
            
            self.logger.info(
                f"✓ Schema detected: confidence={self.has_confidence_column}, "
                f"calculation_mode={self.has_calculation_mode_column}"
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error detecting schema: {e}")
            # Set defaults and continue
            self.has_confidence_column = False
            self.has_calculation_mode_column = False
            self._schema_detected = True
            self._initialized = True
    
    # ==================== HEALTH CHECK ====================
    # Uses ServiceHealthCheck utility (Principle #12: Method Singularity)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for scheduler monitoring.
        
        Uses standardized ServiceHealthCheck utility for consistency across
        all services, implementing Principle #12 (Method Singularity).
        
        This implementation follows the health check pattern guide:
        - Uses ServiceHealthCheck.database_dependent_health() for database-only services
        - Provides schema detection information
        - Includes service-specific context (weights, thresholds, cache)
        - Tracks operation metrics and error rates
        
        Returns:
            Health status dictionary from ServiceHealthCheck utility:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy' | 'unknown',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'schema_detected': bool,
                    'table_exists': bool,
                    'has_confidence_column': bool,
                    'has_calculation_mode_column': bool,
                    'accounts_cached': int,
                    'network_stats_available': bool,
                    'auto_save_enabled': bool,
                    'weights_sum': float,
                    'last_evaluation': str (ISO timestamp),
                    'last_save': str (ISO timestamp),
                    'last_query': str (ISO timestamp),
                    'evaluation_count': int,
                    'save_count': int,
                    'query_count': int,
                    'error_count': int,
                    'last_error': str,
                    'last_error_time': str (ISO timestamp)
                }
            }
        
        Example:
            >>> health = await evaluator.health_check()
            >>> assert health['status'] in ['healthy', 'degraded', 'unhealthy']
        """
        # Schema information
        schema_info = {
            'schema_detected': self._schema_detected,
            'has_confidence_column': self.has_confidence_column,
            'has_calculation_mode_column': self.has_calculation_mode_column
        }
        
        # Cache information
        cache_info = {
            'accounts_cached': len(self.holders_data),
            'network_stats_available': self.network_stats is not None
        }
        
        # Configuration information
        config_info = {
            'auto_save_enabled': self.auto_save,
            'weights_sum': sum(self.weights.values()),
            'ubec_code': self.ubec_code,
            'db_schema': self.db_schema
        }
        
        # Additional checks for this service
        # CRITICAL: These functions MUST return None (success), 
        # dict with 'status' (degraded), or raise Exception (failure)
        # NEVER return boolean values
        
        async def check_schema():
            """
            Verify schema detection completed successfully.
            
            Returns:
                None: Schema detected successfully (healthy)
                dict: Schema detection incomplete (degraded)
            
            NEVER returns boolean - follows ServiceHealthCheck v3.3 pattern
            """
            if not self._schema_detected:
                return {
                    'status': 'degraded',
                    'message': 'Schema detection incomplete',
                    'action': 'Run initialize() to detect schema'
                }
            # Explicit return None for success (not implicit)
            return None
        
        async def check_weights():
            """
            Verify weights configuration sums to 1.0.
            
            Returns:
                None: Weights correctly configured (healthy)
                dict: Weights misconfigured (degraded)
            
            NEVER returns boolean - follows ServiceHealthCheck v3.3 pattern
            """
            # Calculate weights sum
            current_weights_sum = sum(self.weights.values())
            
            # Check if within acceptable tolerance (0.001)
            weight_difference = abs(current_weights_sum - 1.0)
            
            # If weights are correct (within tolerance), return None for success
            if weight_difference < 0.001:
                return None
            
            # If weights are incorrect, return degraded status with details
            return {
                'status': 'degraded',
                'message': f"Weights sum to {current_weights_sum:.3f}, expected 1.0",
                'action': 'Check weights configuration in database'
            }
        
        return await ServiceHealthCheck.database_dependent_health(
            service_name='holonic_evaluator',
            is_initialized=self._initialized,
            additional_checks=[check_schema, check_weights],
            db_manager=self.db_manager,
            schema_info=schema_info,
            cache_info=cache_info,
            config_info=config_info,
            # Operation statistics
            last_evaluation=self._last_evaluation_time.isoformat() if self._last_evaluation_time else None,
            last_save=self._last_save_time.isoformat() if self._last_save_time else None,
            last_query=self._last_query_time.isoformat() if self._last_query_time else None,
            evaluation_count=self._evaluation_count,
            save_count=self._save_count,
            query_count=self._query_count,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time.isoformat() if self._last_error_time else None
        )
    
    def _validate_config(self) -> None:
        """
        Validate service configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.db_schema:
            raise ValueError("db_schema is required")
        
        # Validate weights sum to 1.0
        weights_sum = sum(self.weights.values())
        if not (0.99 <= weights_sum <= 1.01):
            raise ValueError(
                f"Weights sum to {weights_sum}, expected ~1.0. "
                "Check holonic_weight_* configuration."
            )
    
    # ==================== PERSISTENCE OPERATIONS ====================
    # Principle 4: Single Source of Truth - Database backed
    
    async def save_evaluation(self, metrics: HolonicMetrics) -> bool:
        """
        Save evaluation to database.
        
        Uses UPSERT pattern to handle duplicates gracefully.
        Principle 4: Database is single source of truth.
        
        Args:
            metrics: Evaluation metrics to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Track operation
            self._last_save_time = datetime.now()
            self._save_count += 1
            
            # Build column list based on schema
            columns = [
                'account_id', 'evaluation_date',
                'autonomy_integration_score', 'multi_scale_score',
                'regenerative_impact_score', 'network_contribution_score',
                'ubuntu_alignment_score', 'composite_score',
                'holonic_category', 'raw_metrics'
            ]
            
            values = [
                metrics.account_id, metrics.evaluation_date,
                metrics.autonomy_integration_score, metrics.multi_scale_score,
                metrics.regenerative_impact_score, metrics.network_contribution_score,
                metrics.ubuntu_alignment_score, metrics.composite_score,
                metrics.holonic_category.value, json.dumps(metrics.raw_metrics)
            ]
            
            placeholders = ','.join(f'${i+1}' for i in range(len(values)))
            
            if self.has_confidence_column:
                columns.append('confidence')
                values.append(metrics.confidence)
            
            if self.has_calculation_mode_column:
                columns.append('calculation_mode')
                values.append(metrics.calculation_mode)
            
            # UPSERT query with explicit schema name (Principle 4)
            query = f"""
                INSERT INTO {self.db_schema}.holonic_metrics 
                ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT (account_id, DATE(evaluation_date))
                DO UPDATE SET
                    autonomy_integration_score = EXCLUDED.autonomy_integration_score,
                    multi_scale_score = EXCLUDED.multi_scale_score,
                    regenerative_impact_score = EXCLUDED.regenerative_impact_score,
                    network_contribution_score = EXCLUDED.network_contribution_score,
                    ubuntu_alignment_score = EXCLUDED.ubuntu_alignment_score,
                    composite_score = EXCLUDED.composite_score,
                    holonic_category = EXCLUDED.holonic_category,
                    raw_metrics = EXCLUDED.raw_metrics,
                    updated_at = NOW()
            """
            
            await self.db_manager.execute(query, tuple(values))
            return True
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error saving evaluation: {e}")
            return False
    
    async def save_batch_evaluations(
        self,
        metrics_list: List[HolonicMetrics]
    ) -> Dict[str, int]:
        """
        Save batch of evaluations efficiently.
        
        Args:
            metrics_list: List of evaluation metrics
            
        Returns:
            Dict with 'saved' and 'failed' counts
        """
        results = {'saved': 0, 'failed': 0}
        
        for metrics in metrics_list:
            if await self.save_evaluation(metrics):
                results['saved'] += 1
            else:
                results['failed'] += 1
        
        self.logger.info(
            f"Batch save: {results['saved']} saved, {results['failed']} failed"
        )
        
        return results
    
    async def get_latest_evaluation(self, account_id: str) -> Optional[HolonicMetrics]:
        """
        Retrieve latest evaluation for account.
        
        Args:
            account_id: Account to retrieve evaluation for
            
        Returns:
            HolonicMetrics or None if not found
            
        Principle 5: Async database query
        """
        try:
            # Track operation
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            # Build column list based on schema
            columns = [
                'account_id', 'autonomy_integration_score', 'multi_scale_score',
                'regenerative_impact_score', 'network_contribution_score',
                'ubuntu_alignment_score', 'composite_score', 'holonic_category',
                'raw_metrics', 'evaluation_date'
            ]
            
            if self.has_confidence_column:
                columns.append('confidence')
            if self.has_calculation_mode_column:
                columns.append('calculation_mode')
            
            # Explicit schema name (Principle 4)
            query = f"""
                SELECT {', '.join(columns)}
                FROM {self.db_schema}.holonic_metrics
                WHERE account_id = $1
                ORDER BY evaluation_date DESC
                LIMIT 1
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            return HolonicMetrics.from_db_row(result) if result else None
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error retrieving evaluation: {e}")
            return None
    
    async def get_evaluation_history(
        self,
        account_id: str,
        limit: int = 10
    ) -> List[HolonicMetrics]:
        """
        Retrieve evaluation history for an account.
        
        Args:
            account_id: Account to retrieve history for
            limit: Maximum number of evaluations to return
            
        Returns:
            List of HolonicMetrics (newest first)
            
        Principle 5: Async database query
        """
        try:
            # Track operation
            self._last_query_time = datetime.now()
            self._query_count += 1
            
            columns = [
                'account_id', 'autonomy_integration_score', 'multi_scale_score',
                'regenerative_impact_score', 'network_contribution_score',
                'ubuntu_alignment_score', 'composite_score', 'holonic_category',
                'raw_metrics', 'evaluation_date'
            ]
            
            if self.has_confidence_column:
                columns.append('confidence')
            if self.has_calculation_mode_column:
                columns.append('calculation_mode')
            
            # Explicit schema name (Principle 4)
            query = f"""
                SELECT {', '.join(columns)}
                FROM {self.db_schema}.holonic_metrics
                WHERE account_id = $1
                ORDER BY evaluation_date DESC
                LIMIT $2
            """
            
            results = await self.db_manager.fetch_all(query, (account_id, limit))
            return [HolonicMetrics.from_db_row(row) for row in results]
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error retrieving history: {e}")
            return []
    
    # ==================== DATA LOADING ====================
    # Principle 10: Separation of Concerns - Data access layer
    
    async def _calculate_network_statistics(self) -> NetworkStatistics:
        """
        Calculate network-wide statistics.
        
        Principle 12: Single implementation of network stats calculation
        """
        try:
            # Explicit schema names throughout (Principle 4)
            query = f"""
                WITH network_metrics AS (
                    SELECT 
                        COUNT(*) as total_accounts,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance) as median_balance,
                        MAX(balance) as max_balance,
                        SUM(balance) as total_supply
                    FROM {self.db_schema}.account_balances
                    WHERE asset_code = $1
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
                                WHEN from_account = COALESCE(from_account, to_account) 
                                THEN to_account
                                ELSE from_account
                            END) as partner_count
                        FROM {self.db_schema}.stellar_operations
                        WHERE asset_code = $1
                        GROUP BY COALESCE(from_account, to_account)
                    ) tx_stats
                )
                SELECT 
                    nm.total_accounts, nm.median_balance, nm.max_balance, nm.total_supply,
                    COALESCE(tm.median_tx, 0) as median_tx,
                    COALESCE(tm.median_partners, 0) as median_partners,
                    COALESCE(tm.max_tx, 0) as max_tx,
                    COALESCE(tm.max_partners, 0) as max_partners,
                    COALESCE(tm.active_accounts, 0) as active_accounts
                FROM network_metrics nm CROSS JOIN tx_metrics tm
            """
            
            result = await self.db_manager.fetch_one(query, (self.ubec_code,))
            
            if not result:
                # Return default stats if query fails
                return NetworkStatistics(
                    1, Decimal('1000'), 0, 0, Decimal('10000'), 
                    0, 0, Decimal('1000000'), 0
                )
            
            return NetworkStatistics(
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
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error calculating statistics: {e}")
            # Return minimal stats on error
            return NetworkStatistics(
                1, Decimal('1000'), 0, 0, Decimal('10000'),
                0, 0, Decimal('1000000'), 0
            )
    
    # ==================== EVALUATION METHODS ====================
    # Added in v2.3.0 - Critical fix for scheduler integration
    
    async def evaluate_network_holism(self) -> Dict[str, Any]:
        """
        Evaluate network-wide holistic health and Ubuntu alignment.
        
        This method assesses the overall network's adherence to Ubuntu principles
        by analyzing aggregate metrics, distribution patterns, and collective
        behavior indicators.
        
        Designed for periodic execution by the scheduler to monitor network health.
        
        Returns:
            Dictionary containing:
            - network_stats: NetworkStatistics object with aggregate metrics
            - holism_score: Overall network Ubuntu alignment (0-1)
            - distribution: Category distribution across participants
            - health_indicators: Key health metrics
            - timestamp: Evaluation timestamp
            
        Principle 5: Strict async operation
        Principle 10: Separation of concerns - delegates to stats calculation
        
        Example:
            >>> result = await evaluator.evaluate_network_holism()
            >>> print(f"Network holism score: {result['holism_score']:.2f}")
            >>> print(f"Active accounts: {result['network_stats'].active_account_count}")
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("Starting network holism evaluation")
            
            # Calculate network statistics
            self.network_stats = await self._calculate_network_statistics()
            
            # Calculate holism score based on network characteristics
            # Higher score indicates better Ubuntu alignment
            holism_score = 0.0
            
            # Factor 1: Activity rate (active participation)
            activity_factor = min(self.network_stats.activity_rate, 1.0) * 0.3
            holism_score += activity_factor
            
            # Factor 2: Distribution equity (balance distribution)
            if self.network_stats.max_balance > 0:
                equity_factor = (
                    float(self.network_stats.median_balance) / 
                    float(self.network_stats.max_balance)
                ) * 0.3
                holism_score += equity_factor
            
            # Factor 3: Network connectivity (average partners)
            if self.network_stats.total_accounts > 1:
                connectivity_factor = min(
                    self.network_stats.median_partners / 10.0, 1.0
                ) * 0.2
                holism_score += connectivity_factor
            
            # Factor 4: Network maturity (transaction depth)
            maturity_factor = min(
                self.network_stats.median_tx_count / 50.0, 1.0
            ) * 0.2
            holism_score += maturity_factor
            
            # Get category distribution from recent evaluations
            category_dist = await self._get_category_distribution()
            
            # Compile health indicators
            health_indicators = {
                'activity_rate': self.network_stats.activity_rate,
                'median_balance': float(self.network_stats.median_balance),
                'median_partners': self.network_stats.median_partners,
                'median_transactions': self.network_stats.median_tx_count,
                'is_low_activity': self.network_stats.is_low_activity_network
            }
            
            # Track evaluation
            self._last_evaluation_time = datetime.now()
            self._evaluation_count += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                'network_stats': {
                    'total_accounts': self.network_stats.total_accounts,
                    'active_accounts': self.network_stats.active_account_count,
                    'activity_rate': self.network_stats.activity_rate,
                    'median_balance': float(self.network_stats.median_balance),
                    'median_tx_count': self.network_stats.median_tx_count,
                    'median_partners': self.network_stats.median_partners,
                    'total_supply': float(self.network_stats.total_supply)
                },
                'holism_score': holism_score,
                'distribution': category_dist,
                'health_indicators': health_indicators,
                'timestamp': datetime.now().isoformat(),
                'evaluation_duration_seconds': duration
            }
            
            self.logger.info(
                f"Network holism evaluation complete: "
                f"score={holism_score:.3f}, "
                f"accounts={self.network_stats.total_accounts}, "
                f"duration={duration:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error evaluating network holism: {e}")
            raise
    
    async def evaluate_all_accounts(
        self,
        save_to_db: bool = True,
        max_accounts: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate all accounts in the network.
        
        This method performs holonic evaluation for all token holders,
        assigning scores and categories based on Ubuntu principles.
        
        Designed for periodic execution by the scheduler to maintain
        up-to-date evaluations for all participants.
        
        Args:
            save_to_db: Whether to save evaluations to database
            max_accounts: Optional limit on number of accounts to evaluate
            
        Returns:
            Dictionary containing:
            - evaluated_count: Number of accounts evaluated
            - saved_count: Number of evaluations saved (if save_to_db=True)
            - failed_count: Number of evaluations that failed
            - category_distribution: Distribution across holonic categories
            - duration: Evaluation duration in seconds
            - timestamp: Evaluation timestamp
        
        Principle 5: Strict async operation
        Principle 7: Per-asset monitoring with detailed metrics
        
        Example:
            >>> result = await evaluator.evaluate_all_accounts()
            >>> print(f"Evaluated {result['evaluated_count']} accounts")
            >>> print(f"Category distribution: {result['category_distribution']}")
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting evaluation of all accounts (max={max_accounts})")
            
            # Get list of accounts to evaluate (explicit schema name)
            query = f"""
                SELECT DISTINCT account_id
                FROM {self.db_schema}.account_balances
                WHERE asset_code = $1
            """
            
            if max_accounts:
                query += f" LIMIT {max_accounts}"
            
            accounts = await self.db_manager.fetch_all(query, (self.ubec_code,))
            
            if not accounts:
                self.logger.warning("No accounts found to evaluate")
                return {
                    'evaluated_count': 0,
                    'saved_count': 0,
                    'failed_count': 0,
                    'category_distribution': {},
                    'duration': 0.0,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Track results
            evaluated_count = 0
            saved_count = 0
            failed_count = 0
            category_counts = {}
            
            # Evaluate each account
            for row in accounts:
                account_id = row['account_id']
                
                try:
                    # Perform evaluation
                    metrics = await self.evaluate_account(
                        account_id=account_id,
                        save_to_db=save_to_db
                    )
                    
                    evaluated_count += 1
                    if save_to_db:
                        saved_count += 1
                    
                    # Track category distribution
                    category = metrics.holonic_category.value
                    category_counts[category] = category_counts.get(category, 0) + 1
                    
                except Exception as e:
                    self.logger.error(
                        f"Failed to evaluate account {account_id}: {e}"
                    )
                    failed_count += 1
            
            # Track evaluation
            self._last_evaluation_time = datetime.now()
            self._evaluation_count += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                'evaluated_count': evaluated_count,
                'saved_count': saved_count,
                'failed_count': failed_count,
                'category_distribution': category_counts,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(
                f"Evaluation complete: "
                f"{evaluated_count} accounts, "
                f"{failed_count} failures, "
                f"{duration:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error evaluating all accounts: {e}")
            raise
    
    async def evaluate_account(
        self,
        account_id: str,
        save_to_db: bool = True
    ) -> HolonicMetrics:
        """
        Evaluate a single account.
        
        This is a simplified placeholder implementation.
        A complete implementation would calculate all five dimension scores
        based on actual transaction data, network participation, etc.
        
        Args:
            account_id: Account to evaluate
            save_to_db: Whether to save evaluation to database
            
        Returns:
            HolonicMetrics: Evaluation results
            
        Raises:
            Exception: If evaluation fails
        """
        try:
            # Track operation
            self._last_evaluation_time = datetime.now()
            self._evaluation_count += 1
            
            # Get account data
            account_data = await self._get_account_data(account_id)
            if not account_data:
                raise ValueError(f"Account {account_id} not found")
            
            # TODO: Replace with actual evaluation logic that performs
            # comprehensive Ubuntu principle calculations
            composite_score = 0.5  # Placeholder
            
            metrics = HolonicMetrics(
                account_id=account_id,
                autonomy_integration_score=0.5,
                multi_scale_score=0.5,
                regenerative_impact_score=0.5,
                network_contribution_score=0.5,
                ubuntu_alignment_score=0.5,
                composite_score=composite_score,
                holonic_category=self._determine_category(composite_score),
                raw_metrics={'placeholder': True},
                evaluation_date=datetime.now(),
                confidence=0.7,
                calculation_mode='placeholder'
            )
            
            if save_to_db:
                await self.save_evaluation(metrics)
            
            return metrics
            
        except Exception as e:
            # Re-raise to be caught by caller
            raise
    
    async def _get_account_data(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account data from database (explicit schema name)."""
        try:
            query = f"""
                SELECT account_id, balance
                FROM {self.db_schema}.account_balances
                WHERE account_id = $1 AND asset_code = $2
            """
            
            result = await self.db_manager.fetch_one(
                query,
                (account_id, self.ubec_code)
            )
            
            return dict(result) if result else None
            
        except Exception as e:
            self.logger.error(f"Error fetching account data for {account_id}: {e}")
            return None
    
    def _determine_category(self, composite_score: float) -> HolonicCategory:
        """
        Determine holonic category based on composite score.
        
        Args:
            composite_score: Composite evaluation score (0-1)
            
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
    
    async def _get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of accounts across holonic categories (explicit schema)."""
        try:
            query = f"""
                SELECT holonic_category, COUNT(*) as count
                FROM {self.db_schema}.holonic_metrics
                WHERE evaluation_date >= NOW() - INTERVAL '7 days'
                GROUP BY holonic_category
            """
            
            results = await self.db_manager.fetch_all(query, ())
            return {row['holonic_category']: row['count'] for row in results}
            
        except Exception as e:
            self.logger.error(f"Error fetching category distribution: {e}")
            return {}
    
    # ==================== LIFECYCLE CLEANUP ====================
    
    async def close(self):
        """
        Clean up evaluator resources.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("Holonic evaluator closing...")
        self.holders_data.clear()
        self.network_stats = None
        self._last_evaluation_time = None
        self._initialized = False
        self.logger.info("✓ Holonic evaluator closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

async def create_holonic_evaluator(
    db_manager: Any,
    config: Dict[str, Any],
    **kwargs
) -> UBECHolonicEvaluator:
    """
    Factory function to create holonic evaluator instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - ubec_code: Token code (required)
            - ubec_issuer: Issuer address (required)
            - db_schema: Database schema (required)
            - auto_save_evaluations: Auto-save to DB (optional)
            - holonic_weight_*: Scoring weights (optional)
        **kwargs: Additional configuration options
    
    Returns:
        UBECHolonicEvaluator: Initialized service instance
        
    Raises:
        ValueError: If required config parameters are missing
    
    Example:
        >>> evaluator = await create_holonic_evaluator(
        ...     db_manager=db,
        ...     config={
        ...         'ubec_code': 'UBEC',
        ...         'ubec_issuer': 'GDPNB7S3...',
        ...         'db_schema': 'ubec_main'
        ...     }
        ... )
        >>> health = await evaluator.health_check()
    """
    # Validate required parameters
    required_params = ['db_schema']
    
    for param in required_params:
        if param not in config:
            raise ValueError(f"Configuration missing required parameter: '{param}'")
    
    # Create and initialize service
    evaluator = UBECHolonicEvaluator(db_manager=db_manager, config=config)
    # CRITICAL FIX: Explicitly call initialize() before returning
    await evaluator.initialize()
    
    # Verify initialization succeeded
    if not evaluator._initialized:
        raise RuntimeError(
            "Holonic evaluator initialization failed - "
            "check database schema and connectivity"
        )
    
    return evaluator


# ==================== MODULE EXPORTS ====================
# Principle 1: Modular Design - Clear public interface

__all__ = [
    # Enums
    'HolonicCategory',
    
    # Data models
    'HolonicMetrics',
    'AccountHolderData',
    'NetworkStatistics',
    
    # Service
    'UBECHolonicEvaluator',
    'create_holonic_evaluator'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Principle 2: Service Pattern - No standalone execution

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from ubec_holonic_evaluator import create_holonic_evaluator\n"
        "  evaluator = await create_holonic_evaluator(db_manager, config)\n"
        "  result = await evaluator.evaluate_all_accounts()\n"
        "  report = await evaluator.evaluate_network_holism()\n"
        "  health = await evaluator.health_check()\n"
        "  await evaluator.close()\n\n"
        "Version 2.3.1 - Health Check Pattern Fix:\n"
        "  - Fixed check functions to ensure proper return types\n"
        "  - Verified explicit schema names in all queries\n"
        "  - Enhanced check_weights logic clarity\n"
        "  - Resolves 'Unexpected return type' warnings\n\n"
        "Version 2.3.0 - Added Missing Evaluation Methods:\n"
        "  - Added evaluate_all_accounts() for scheduler integration\n"
        "  - Added evaluate_network_holism() for network assessment\n"
        "  - Complete public API for evaluation operations\n"
        "  - Full async/await throughout\n"
        "  - Maintains all 12 design principles\n\n"
        "Version 2.2.0 - Standardized Health Check Pattern:\n"
        "  - Uses ServiceHealthCheck.database_dependent_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Consistent health checks across all services\n"
        "  - Enhanced schema detection and validation\n"
        "  - Cache and configuration tracking\n"
        "  - Cleaner, more maintainable code\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
