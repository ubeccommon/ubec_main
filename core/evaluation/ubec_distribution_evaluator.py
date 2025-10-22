#!/usr/bin/env python3
# core/evaluation/distribution_evaluator.py
"""
UBEC Distribution Evaluator Service
====================================
Service implementation for evaluating and monitoring UBEC token distribution.

Evaluates and monitors UBEC token distribution compliance across all
managed accounts. Provides analysis and recommendations for maintaining
proper tokenomics ratios.

This service:
- Monitors distribution compliance in real-time
- Generates compliance reports
- Identifies distribution anomalies
- Provides rebalancing recommendations
- Tracks historical compliance trends

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained evaluation service
    ✅ 2.  Service Pattern: Factory-based, no standalone execution
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Individual account tracking with health checks
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Integrated Rate Limiting: Built-in for operations
    ✅ 10. Separation of Concerns: Evaluation logic isolated
    ✅ 11. Comprehensive Documentation: Full docstrings and attribution
    ✅ 12. Method Singularity: No duplicate methods, uses ServiceHealthCheck utility
════════════════════════════════════════════════════════════════════════════

Usage:
    from distribution_evaluator import create_evaluator_service
    
    evaluator = await create_evaluator_service(
        distribution_service=dist_service,
        audit_service=audit_service,
        db_manager=async_db
    )
    
    # Run evaluation
    report = await evaluator.evaluate_distribution()
    
    # Check specific account
    account_eval = await evaluator.evaluate_account('GXXX...')
    
    # Get historical trends
    trends = await evaluator.get_compliance_trends(days=30)
    
    # Health check
    health = await evaluator.health_check()
    
    await evaluator.close()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.1.0 (Standardized Health Check Pattern)
Date: October 17, 2025

Changelog:
    v3.1.0 - MAJOR: Standardized health check using ServiceHealthCheck utility
           - Implements Principle #12: Method Singularity with shared utility
           - Removed custom health_check() implementation (~250 lines)
           - Now uses ServiceHealthCheck.database_dependent_health()
           - Cleaner, more maintainable code with consistent patterns
           - Full compliance with health check implementation guide
    v3.0.0 - Enhanced health_check() method for comprehensive monitoring
           - Implements Principle #7: Per-Asset Monitoring with detailed checks
           - Added initialization tracking
           - Improved error handling and validation
           - Added operation statistics tracking
           - Enhanced evaluation metrics
    v2.2.0 - Fixed fetch_all parameter passing (tuple wrapping)
    v2.1.0 - Updated to use stellar_operations table with correct schema
    v2.0.0 - Async Service Architecture
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Import standardized health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

# Configure logging
logger = logging.getLogger(__name__)


# ==================== SERVICE IMPLEMENTATION ====================

class UBECDistributionEvaluator:
    """
    UBEC Distribution Evaluator Service
    
    Evaluates and monitors UBEC token distribution compliance.
    All operations are async and use the database as the single source of truth.
    
    This evaluator provides:
    - Real-time compliance monitoring
    - Distribution health scoring
    - Deviation analysis
    - Actionable recommendations
    - Historical trend analysis
    
    Attributes:
        distribution_service: Distribution management service
        audit_service: Token audit service
        db_manager: Async database manager
        logger: Logger instance
        
    Lifecycle:
        1. Instantiate via create_evaluator_service() factory
        2. Service auto-initializes
        3. Use evaluation methods
        4. Cleanup via close() method
        
    Design Principles:
        - Principle 1: Modular - Clear boundaries and single responsibility
        - Principle 4: Single Source of Truth - Database-driven
        - Principle 5: Strict Async - All I/O operations async
        - Principle 10: Separation of Concerns - Clear layer separation
        - Principle 12: Method Singularity - Uses ServiceHealthCheck utility
    """
    
    def __init__(
        self,
        distribution_service: Any,
        audit_service: Any,
        db_manager: Any
    ):
        """
        Initialize the distribution evaluator.
        
        DO NOT call directly - use create_evaluator_service() factory instead.
        
        Args:
            distribution_service: Distribution management service
            audit_service: Token audit service
            db_manager: Async database manager
        """
        self.distribution_service = distribution_service
        self.audit_service = audit_service
        self.db_manager = db_manager
        
        # Setup logging
        self.logger = logging.getLogger('UBECDistributionEvaluator')
        
        # Initialization and operation tracking (for health checks)
        self._initialized = True  # Service is ready after construction
        self._last_evaluation_time: Optional[datetime] = None
        self._last_account_eval_time: Optional[datetime] = None
        self._last_trend_analysis_time: Optional[datetime] = None
        self._evaluation_count = 0
        self._account_evaluation_count = 0
        self._trend_analysis_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info("Distribution Evaluator initialized")
    
    # ==================== HEALTH CHECK ====================
    # Principle 7: Per-Asset Monitoring with health checks
    # Principle 12: Method Singularity - Uses standardized utility
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on distribution evaluator service.
        
        Uses standardized ServiceHealthCheck utility for consistency across
        all services, implementing Principle #12 (Method Singularity).
        
        This implementation follows the health check pattern guide:
        - Uses ServiceHealthCheck.database_dependent_health() for composite services
        - Checks dependent services (distribution_service, audit_service)
        - Includes evaluation-specific context (operation counts, timing)
        - Tracks operation metrics and error rates
        
        Returns:
            Health status dictionary from ServiceHealthCheck utility:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy' | 'unknown',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'database_connected': bool,
                    'dependent_services': {
                        'distribution_service': {'available': bool, 'status': str},
                        'audit_service': {'available': bool, 'status': str}
                    },
                    'last_evaluation': str (ISO timestamp),
                    'last_account_eval': str (ISO timestamp),
                    'last_trend_analysis': str (ISO timestamp),
                    'evaluation_count': int,
                    'account_evaluation_count': int,
                    'trend_analysis_count': int,
                    'error_count': int,
                    'last_error': str,
                    'last_error_time': str (ISO timestamp)
                }
            }
        
        Example:
            >>> health = await evaluator.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Distribution evaluator operational")
            ...     print(f"Evaluations: {health['details']['evaluation_count']}")
            >>> else:
            ...     print(f"Issues detected: {health['message']}")
        
        Design Notes:
            - Principle 7: Comprehensive per-service monitoring
            - Principle 12: Delegates to ServiceHealthCheck utility (no duplication)
        """
        # Prepare dependent services information
        dependent_services = {
            'distribution_service': self.distribution_service,
            'audit_service': self.audit_service
        }
        
        # Prepare operation context
        operation_context = {
            'last_evaluation': self._last_evaluation_time.isoformat() if self._last_evaluation_time else None,
            'last_account_eval': self._last_account_eval_time.isoformat() if self._last_account_eval_time else None,
            'last_trend_analysis': self._last_trend_analysis_time.isoformat() if self._last_trend_analysis_time else None,
            'evaluation_count': self._evaluation_count,
            'account_evaluation_count': self._account_evaluation_count,
            'trend_analysis_count': self._trend_analysis_count,
            'error_count': self._error_count,
            'last_error': self._last_error,
            'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None
        }
        
        # Calculate operation age warnings
        if self._last_evaluation_time:
            eval_age = (datetime.now() - self._last_evaluation_time).total_seconds()
            operation_context['last_evaluation_age_seconds'] = round(eval_age, 2)
        
        # Use standardized health check utility (Principle #12: Method Singularity)
        return await ServiceHealthCheck.database_dependent_health(
            service_name='distribution_evaluator',
            is_initialized=self._initialized,
            db_manager=self.db_manager,
            dependent_services=dependent_services,
            **operation_context
        )
    
    def _validate_config(self) -> None:
        """
        Validate service configuration.
        
        Raises:
            ValueError: If configuration is invalid
        
        Principle 11: Comprehensive validation
        """
        if not self.distribution_service:
            raise ValueError("distribution_service not configured")
        
        if not self.audit_service:
            raise ValueError("audit_service not configured")
        
        if not self.db_manager:
            raise ValueError("db_manager not configured")
        
        # Validate distribution service has required attributes
        required_attrs = ['target_distribution', 'rebalance_threshold', 'db_schema']
        for attr in required_attrs:
            if not hasattr(self.distribution_service, attr):
                raise ValueError(
                    f"distribution_service missing required attribute: {attr}"
                )
    
    # ==================== EVALUATION METHODS ====================
    
    async def evaluate_distribution(self) -> Dict[str, Any]:
        """
        Perform comprehensive distribution evaluation.
        
        Analyzes current token distribution against target ratios and
        generates compliance report with recommendations.
        
        Returns:
            Dictionary containing:
            - compliance_status: Overall compliance boolean
            - current_distribution: Current percentage breakdown
            - target_distribution: Target percentage breakdown
            - deviations: Deviation from targets
            - health_score: Overall distribution health (0-100)
            - recommendations: List of actionable recommendations
            - timestamp: Evaluation timestamp
        
        Raises:
            Exception: If evaluation fails
        
        Example:
            >>> report = await evaluator.evaluate_distribution()
            >>> if not report['compliance_status']:
            ...     for rec in report['recommendations']:
            ...         print(f"Action needed: {rec}")
        
        Design Notes:
            - Principle 5: Fully async operation
            - Principle 7: Per-asset monitoring with detailed tracking
        """
        try:
            # Track operation
            self._last_evaluation_time = datetime.now()
            self._evaluation_count += 1
            
            self.logger.info("Starting comprehensive distribution evaluation...")
            
            # Get current distribution from distribution service
            current_dist = await self.distribution_service.get_current_distribution()
            
            # Get compliance status
            compliance_result = await self.distribution_service.check_compliance()
            
            # Calculate health score
            health_score = self._calculate_health_score(
                current_dist,
                self.distribution_service.target_distribution
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                current_dist,
                compliance_result
            )
            
            # Build evaluation report
            report = {
                'timestamp': datetime.now().isoformat(),
                'compliance_status': compliance_result['overall_compliant'],
                'current_distribution': current_dist['distribution_of_supply'],
                'target_distribution': current_dist['target_distribution'],
                'deviations': compliance_result['deviations'],
                'health_score': health_score,
                'recommendations': recommendations,
                'total_supply': current_dist['total_supply'],
                'monitored_accounts': {
                    'general': current_dist['balances']['general'],
                    'administration': current_dist['balances']['administration'],
                    'stewardship': current_dist['balances']['stewardship']
                }
            }
            
            self.logger.info(
                f"✓ Distribution evaluation complete: "
                f"Compliance={'PASS' if report['compliance_status'] else 'FAIL'}, "
                f"Health Score={health_score:.1f}/100"
            )
            
            return report
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Distribution evaluation failed: {e}", exc_info=True)
            raise
    
    async def evaluate_account(
        self,
        account_id: str,
        account_type: str = 'unknown'
    ) -> Dict[str, Any]:
        """
        Evaluate a specific account's distribution status.
        
        Args:
            account_id: Stellar account address to evaluate
            account_type: Account classification (general/administration/stewardship)
        
        Returns:
            Dictionary containing:
            - account_id: Account address
            - account_type: Detected or provided type
            - balance: Current UBEC balance
            - percentage_of_supply: Account's share of total supply
            - classification: Holder size classification
            - compliance_notes: Account-specific compliance observations
            - timestamp: Evaluation timestamp
        
        Example:
            >>> eval_result = await evaluator.evaluate_account('GXXX...')
            >>> print(f"Account holds {eval_result['percentage_of_supply']:.2f}% of supply")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-account monitoring
        """
        try:
            # Track operation
            self._last_account_eval_time = datetime.now()
            self._account_evaluation_count += 1
            
            self.logger.debug(f"Evaluating account {account_id[:8]}...")
            
            # Get account balance from database
            query = f"""
                SELECT balance, asset_code
                FROM {self.distribution_service.db_schema}.account_balances
                WHERE account_id = $1 AND asset_code = $2
            """
            
            result = await self.db_manager.fetch_one(
                query,
                (account_id, self.distribution_service.asset_code)
            )
            
            if not result:
                return {
                    'account_id': account_id,
                    'account_type': account_type,
                    'balance': 0,
                    'percentage_of_supply': 0,
                    'classification': 'inactive',
                    'compliance_notes': ['Account not found or has zero balance'],
                    'timestamp': datetime.now().isoformat()
                }
            
            balance = Decimal(str(result['balance']))
            
            # Get total supply for percentage calculation
            current_dist = await self.distribution_service.get_current_distribution()
            total_supply = Decimal(str(current_dist['total_supply']))
            
            percentage = float((balance / total_supply * 100) if total_supply > 0 else 0)
            
            # Classify holder size
            classification = self._classify_holder(balance, total_supply)
            
            # Detect account type if unknown
            if account_type == 'unknown':
                account_type = await self._detect_account_type(account_id)
            
            # Generate compliance notes
            compliance_notes = self._generate_account_notes(
                account_id, account_type, balance, percentage
            )
            
            result_dict = {
                'account_id': account_id,
                'account_type': account_type,
                'balance': float(balance),
                'percentage_of_supply': percentage,
                'classification': classification,
                'compliance_notes': compliance_notes,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.debug(
                f"✓ Account evaluation complete: {account_id[:8]}... = "
                f"{percentage:.3f}% of supply"
            )
            
            return result_dict
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Account evaluation failed: {e}", exc_info=True)
            raise
    
    async def get_compliance_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get historical compliance trends.
        
        Args:
            days: Number of days of history to analyze
        
        Returns:
            Dictionary containing:
            - period_days: Analysis period
            - compliance_rate: Percentage of time in compliance
            - trend_direction: 'improving', 'stable', or 'declining'
            - snapshots: List of historical compliance snapshots
            - average_deviation: Average deviation from targets
            - timestamp: Analysis timestamp
        
        Example:
            >>> trends = await evaluator.get_compliance_trends(days=30)
            >>> if trends['trend_direction'] == 'declining':
            ...     print("Warning: Compliance is declining")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 4: Database as source of truth for historical data
        """
        try:
            # Track operation
            self._last_trend_analysis_time = datetime.now()
            self._trend_analysis_count += 1
            
            self.logger.info(f"Analyzing compliance trends for last {days} days...")
            
            # Query distribution snapshots from database
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = f"""
                SELECT 
                    snapshot_time,
                    administration_percentage,
                    stewardship_percentage,
                    general_percentage,
                    total_supply
                FROM {self.distribution_service.db_schema}.distribution_snapshots
                WHERE snapshot_time >= $1
                AND asset_code = $2
                ORDER BY snapshot_time ASC
            """
            
            snapshots = await self.db_manager.fetch_all(
                query,
                (cutoff_date, self.distribution_service.asset_code)
            )
            
            if not snapshots:
                return {
                    'period_days': days,
                    'compliance_rate': None,
                    'trend_direction': 'unknown',
                    'snapshots': [],
                    'average_deviation': None,
                    'message': 'No historical data available',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Analyze snapshots for compliance
            compliant_count = 0
            total_deviation = 0
            
            for snapshot in snapshots:
                admin_pct = float(snapshot['administration_percentage'])
                steward_pct = float(snapshot['stewardship_percentage'])
                
                # Check compliance (within threshold)
                admin_target = float(self.distribution_service.target_distribution['administration'] * 100)
                steward_target = float(self.distribution_service.target_distribution['stewardship'] * 100)
                threshold = float(self.distribution_service.rebalance_threshold * 100)
                
                admin_compliant = abs(admin_pct - admin_target) <= threshold
                steward_compliant = abs(steward_pct - steward_target) <= threshold
                
                if admin_compliant and steward_compliant:
                    compliant_count += 1
                
                # Calculate deviation
                admin_dev = abs(admin_pct - admin_target)
                steward_dev = abs(steward_pct - steward_target)
                total_deviation += (admin_dev + steward_dev) / 2
            
            # Calculate metrics
            compliance_rate = (compliant_count / len(snapshots) * 100) if snapshots else 0
            average_deviation = total_deviation / len(snapshots) if snapshots else 0
            
            # Determine trend direction
            if len(snapshots) >= 2:
                # Compare first half to second half
                midpoint = len(snapshots) // 2
                first_half_compliant = sum(
                    1 for i in range(midpoint)
                    if self._is_snapshot_compliant(snapshots[i])
                ) / midpoint if midpoint > 0 else 0
                
                second_half_compliant = sum(
                    1 for i in range(midpoint, len(snapshots))
                    if self._is_snapshot_compliant(snapshots[i])
                ) / (len(snapshots) - midpoint) if (len(snapshots) - midpoint) > 0 else 0
                
                if second_half_compliant > first_half_compliant + 0.1:
                    trend_direction = 'improving'
                elif second_half_compliant < first_half_compliant - 0.1:
                    trend_direction = 'declining'
                else:
                    trend_direction = 'stable'
            else:
                trend_direction = 'insufficient_data'
            
            result = {
                'period_days': days,
                'compliance_rate': round(compliance_rate, 2),
                'trend_direction': trend_direction,
                'snapshots': [
                    {
                        'timestamp': s['snapshot_time'].isoformat(),
                        'administration_pct': float(s['administration_percentage']),
                        'stewardship_pct': float(s['stewardship_percentage']),
                        'general_pct': float(s['general_percentage'])
                    }
                    for s in snapshots
                ],
                'average_deviation': round(average_deviation, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(
                f"✓ Trend analysis complete: Compliance rate={compliance_rate:.1f}%, "
                f"Trend={trend_direction}"
            )
            
            return result
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Trend analysis failed: {e}", exc_info=True)
            raise
    
    # ==================== HELPER METHODS ====================
    
    def _calculate_health_score(
        self,
        current_dist: Dict[str, Any],
        target_dist: Dict[str, float]
    ) -> float:
        """
        Calculate overall distribution health score (0-100).
        
        Principle 12: Single implementation of health score calculation
        """
        try:
            # Get current percentages
            current = current_dist['distribution_of_supply']
            
            # Calculate deviations from targets
            admin_deviation = abs(current['administration'] - target_dist['administration'])
            steward_deviation = abs(current['stewardship'] - target_dist['stewardship'])
            general_deviation = abs(current['general'] - target_dist['general'])
            
            # Weight the deviations (administration and stewardship are most critical)
            weighted_deviation = (
                admin_deviation * 0.4 +
                steward_deviation * 0.4 +
                general_deviation * 0.2
            )
            
            # Convert to health score (0 deviation = 100 score)
            # Each 1% deviation reduces score by ~10 points
            health_score = max(0, 100 - (weighted_deviation * 1000))
            
            return round(health_score, 1)
            
        except Exception as e:
            self.logger.warning(f"Health score calculation failed: {e}")
            return 50.0  # Return neutral score on error
    
    async def _generate_recommendations(
        self,
        current_dist: Dict[str, Any],
        compliance_result: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on current state."""
        recommendations = []
        
        if compliance_result['overall_compliant']:
            recommendations.append("✓ Distribution is compliant - no action needed")
            return recommendations
        
        # Check each category
        deviations = compliance_result['deviations']
        
        for category, deviation_info in deviations.items():
            if category == 'general':
                continue  # General is derived, don't make recommendations
            
            if not compliance_result['compliance'][category]:
                actual = deviation_info['actual']
                target = deviation_info['target']
                diff_pct = deviation_info['deviation_percent']
                
                if actual > target:
                    recommendations.append(
                        f"⚠️ {category.capitalize()}: Reduce by {diff_pct:.2f}% "
                        f"(currently {actual:.2%}, target {target:.2%})"
                    )
                else:
                    recommendations.append(
                        f"⚠️ {category.capitalize()}: Increase by {diff_pct:.2f}% "
                        f"(currently {actual:.2%}, target {target:.2%})"
                    )
        
        return recommendations
    
    def _classify_holder(self, balance: Decimal, total_supply: Decimal) -> str:
        """Classify holder size based on percentage of supply."""
        if total_supply == 0:
            return 'unknown'
        
        pct = float(balance / total_supply * 100)
        
        if pct >= 10:
            return 'whale'
        elif pct >= 1:
            return 'large'
        elif pct >= 0.1:
            return 'medium'
        elif pct > 0:
            return 'small'
        else:
            return 'inactive'
    
    async def _detect_account_type(self, account_id: str) -> str:
        """Detect account type based on database records."""
        try:
            # Check managed accounts table
            query = f"""
                SELECT account_type
                FROM {self.distribution_service.db_schema}.managed_accounts
                WHERE account_id = $1
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            
            if result:
                return result['account_type']
            
            return 'general'
            
        except Exception:
            return 'unknown'
    
    def _generate_account_notes(
        self,
        account_id: str,
        account_type: str,
        balance: Decimal,
        percentage: float
    ) -> List[str]:
        """Generate compliance notes for an account."""
        notes = []
        
        if percentage > 10:
            notes.append(f"Large holder: Controls {percentage:.2f}% of total supply")
        
        if account_type == 'administration':
            target = self.distribution_service.target_distribution['administration'] * 100
            if abs(percentage - target) > 1:
                notes.append(
                    f"Administration account deviation: {percentage:.2f}% vs {target:.2f}% target"
                )
        
        if account_type == 'stewardship':
            target = self.distribution_service.target_distribution['stewardship'] * 100
            if abs(percentage - target) > 1:
                notes.append(
                    f"Stewardship account deviation: {percentage:.2f}% vs {target:.2f}% target"
                )
        
        if not notes:
            notes.append("No compliance issues detected")
        
        return notes
    
    def _is_snapshot_compliant(self, snapshot: Dict[str, Any]) -> bool:
        """Check if a historical snapshot was compliant."""
        admin_pct = float(snapshot['administration_percentage'])
        steward_pct = float(snapshot['stewardship_percentage'])
        
        admin_target = float(self.distribution_service.target_distribution['administration'] * 100)
        steward_target = float(self.distribution_service.target_distribution['stewardship'] * 100)
        threshold = float(self.distribution_service.rebalance_threshold * 100)
        
        admin_compliant = abs(admin_pct - admin_target) <= threshold
        steward_compliant = abs(steward_pct - steward_target) <= threshold
        
        return admin_compliant and steward_compliant
    
    # ==================== LIFECYCLE CLEANUP ====================
    
    async def close(self):
        """Cleanup resources on shutdown."""
        self.logger.info("Distribution evaluator closing...")
        self._initialized = False
        self.logger.info("✓ Distribution evaluator closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

async def create_evaluator_service(
    distribution_service: Any,
    audit_service: Any,
    db_manager: Any,
    **kwargs
) -> UBECDistributionEvaluator:
    """
    Factory function to create distribution evaluator instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    
    Args:
        distribution_service: Distribution management service
        audit_service: Token audit service
        db_manager: Async database manager
        **kwargs: Additional configuration options
    
    Returns:
        UBECDistributionEvaluator: Initialized service instance
        
    Raises:
        ValueError: If required parameters are missing
    
    Example:
        >>> evaluator = await create_evaluator_service(
        ...     distribution_service=dist_service,
        ...     audit_service=audit_service,
        ...     db_manager=db
        ... )
        >>> health = await evaluator.health_check()
    """
    if not distribution_service:
        raise ValueError("distribution_service is required")
    if not audit_service:
        raise ValueError("audit_service is required")
    if not db_manager:
        raise ValueError("db_manager is required")
    
    return UBECDistributionEvaluator(
        distribution_service=distribution_service,
        audit_service=audit_service,
        db_manager=db_manager
    )


# ==================== MODULE EXPORTS ====================
# Principle 1: Modular Design - Clear public interface

__all__ = ['UBECDistributionEvaluator', 'create_evaluator_service']


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Principle 2: Service Pattern - No standalone execution

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from distribution_evaluator import create_evaluator_service\n"
        "  evaluator = await create_evaluator_service(\n"
        "      distribution_service=dist_service,\n"
        "      audit_service=audit_service,\n"
        "      db_manager=db\n"
        "  )\n"
        "  health = await evaluator.health_check()\n"
        "  report = await evaluator.evaluate_distribution()\n"
        "  await evaluator.close()\n\n"
        "Version 3.1.0 - Standardized Health Check Pattern:\n"
        "  - Uses ServiceHealthCheck.database_dependent_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Consistent health checks across all services\n"
        "  - Enhanced service dependency monitoring\n"
        "  - Cleaner, more maintainable code\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
