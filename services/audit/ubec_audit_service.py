#!/usr/bin/env python3
"""
UBEC Audit Service - Tokenomics Compliance and Balance Monitoring
==================================================================

Monitors and audits UBEC token distribution to ensure compliance with
tokenomics targets for administration and stewardship accounts.

Core Functionality:
- Snapshot current distribution state
- Compare against tokenomics targets
- Identify compliance deviations
- Track audit history
- Provide rebalancing recommendations

Design Principles Compliance:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ 1.  Modular Design: Self-contained audit service
    ✅ 2.  Service Pattern: Factory-based instantiation only
    ✅ 3.  Service Registry: Accessed through registry
    ✅ 4.  Single Source of Truth: Database authoritative
    ✅ 5.  Strict Async: All I/O operations async
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Comprehensive health checks
    ✅ 8.  No Duplicate Configuration: Centralized config
    ✅ 9.  Rate Limiting: Built-in for external calls
    ✅ 10. Separation of Concerns: Clear layer separation
    ✅ 11. Documentation: Comprehensive docstrings
    ✅ 12. Method Singularity: Uses ServiceHealthCheck utility
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
    from services.audit.ubec_audit_service import create_audit_service
    
    audit = await create_audit_service(
        db_manager=db,
        config={
            'ubec_code': 'UBEC',
            'ubec_issuer': 'G...',
            'administration_account': 'G...',
            'stewardship_account': 'G...',
            'tokenomics': {
                'administration_target': 0.05,
                'stewardship_target': 0.30,
                'compliance_threshold': 0.02
            }
        },
        holonic_evaluator=evaluator
    )
    
    # Perform audit
    result = await audit.perform_comprehensive_audit()
    
    # Check distribution compliance (for evaluator integration)
    compliance = await audit.check_distribution_compliance()
    
    # Check health
    health = await audit.health_check()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 4.4.0 (Float Type Consistency Fix)
Date: October 28, 2025

Changelog:
    v4.4.0 - CRITICAL FIX: Float type consistency throughout
           - Ensures all numeric values from database config are converted to float
           - Fixed TypeError: unsupported operand type(s) for /: 'float' and 'decimal.Decimal'
           - Converts admin_target, steward_target, threshold to float in __init__
           - All values in check_distribution_compliance guaranteed to be float
           - Implements Principle #12: Centralized type conversion
           - Resolves division errors in distribution evaluator calculations
    v4.3.0 - CRITICAL FIX: Data structure alignment with evaluator
           - Fixed deviations structure in check_distribution_compliance()
           - Added nested dict with actual/target/deviation_percent keys
           - Resolves TypeError: 'float' object is not subscriptable
           - Evaluator now receives correctly structured compliance data
    v4.2.0 - CRITICAL FIX: Database schema alignment
           - Fixed get_distribution_snapshot() query to match actual schema
           - Removed asset_issuer from WHERE clause (column doesn't exist)
           - account_balances table only has: id, account_id, asset_code, balance
           - Query now correctly filters by asset_code only
           - Resolves "column asset_issuer does not exist" error
    v4.1.0 - CRITICAL FIX: Added check_distribution_compliance() method
           - Fixes AttributeError in distribution evaluator integration
           - Implements proper interface for evaluator service dependency
           - Maintains all existing functionality
           - Follows Principle #12: Method Singularity (wraps existing methods)
    v4.0.0 - ServiceHealthCheck Integration
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
from dataclasses import dataclass

# ServiceHealthCheck utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck


# ==================== DATA MODELS ====================

@dataclass
class DistributionSnapshot:
    """Snapshot of token distribution at a point in time"""
    timestamp: datetime
    total_supply: Decimal
    admin_balance: Decimal
    steward_balance: Decimal
    circulation_balance: Decimal
    admin_percentage: float
    steward_percentage: float
    circulation_percentage: float


@dataclass
class ComplianceStatus:
    """Tokenomics compliance status"""
    is_compliant: bool
    admin_compliant: bool
    steward_compliant: bool
    admin_deviation: float
    steward_deviation: float
    requires_rebalance: bool
    recommendations: List[str]


# ==================== AUDIT SERVICE ====================

class UBECAuditService:
    """
    UBEC Audit Service
    
    Monitors token distribution and ensures tokenomics compliance.
    
    Attributes:
        db: Database manager
        ubec_code: UBEC token code
        ubec_issuer: UBEC issuer address
        admin_account: Administration account address
        steward_account: Stewardship account address
        admin_target: Target % for administration (0-1) - ALWAYS FLOAT
        steward_target: Target % for stewardship (0-1) - ALWAYS FLOAT
        threshold: Compliance threshold for deviations - ALWAYS FLOAT
        holonic_evaluator: Optional holonic evaluator for account scoring
        
    Design Notes:
        - Principle 2: Factory pattern via create_audit_service()
        - Principle 4: Database is single source of truth
        - Principle 5: All operations async
        - Principle 12: Uses ServiceHealthCheck utility + centralized type conversion
    """
    
    def __init__(
        self,
        db_manager,
        config: Dict[str, Any],
        holonic_evaluator=None
    ):
        """
        Initialize audit service.
        
        DO NOT call directly - use create_audit_service() factory.
        
        Args:
            db_manager: Async database manager
            config: Configuration with tokenomics parameters
            holonic_evaluator: Optional holonic evaluator service
        """
        self.db = db_manager
        self.holonic_evaluator = holonic_evaluator
        
        # Configuration
        self.ubec_code = config.get('ubec_code', 'UBEC')
        self.ubec_issuer = config.get('ubec_issuer', '')
        self.admin_account = config.get('administration_account', '')
        self.steward_account = config.get('stewardship_account', '')
        
        # Tokenomics targets - CRITICAL: Convert to float to prevent Decimal/float mixing
        # Principle #12: Centralized type conversion ensures consistency
        tokenomics = config.get('tokenomics', {})
        self.admin_target = float(tokenomics.get('administration_target', 0.05))
        self.steward_target = float(tokenomics.get('stewardship_target', 0.30))
        self.threshold = float(tokenomics.get('compliance_threshold', 0.02))
        
        # Cache settings (Principle 7: Per-Asset Monitoring)
        self._cache_ttl = 300  # 5 minutes
        self._last_snapshot: Optional[DistributionSnapshot] = None
        self._last_snapshot_time: Optional[datetime] = None
        self._last_audit_time: Optional[datetime] = None
        self._audit_count = 0
        
        # Initialization flag
        self._initialized = False
        
        # Setup logging
        self.logger = logging.getLogger('UBECAuditService')
        self.logger.info(f"Audit service created for {self.ubec_code}")
    
    async def initialize(self) -> None:
        """
        Initialize the audit service.
        
        Verifies database connectivity and configuration.
        Principle 5: Async initialization.
        """
        self.logger.info("Initializing audit service...")
        
        # Verify database connection
        try:
            await self.db.execute("SELECT 1")
            self.logger.info("✓ Database connection verified")
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")
        
        # Validate configuration
        if not self.admin_account or not self.steward_account:
            raise ValueError("Both administration and stewardship accounts must be configured")
        
        if not 0 < self.admin_target < 1 or not 0 < self.steward_target < 1:
            raise ValueError("Target percentages must be between 0 and 1")
        
        if self.admin_target + self.steward_target >= 1:
            raise ValueError("Combined admin and steward targets cannot exceed 100%")
        
        self.logger.info(
            f"✓ Configuration valid: {self.ubec_code}, "
            f"targets: {self.admin_target:.1%}/{self.steward_target:.1%}"
        )
        
        self._initialized = True
        self.logger.info("✓ Audit service initialized")
    
    # ==================== DISTRIBUTION SNAPSHOT ====================
    
    async def get_distribution_snapshot(
        self,
        force_refresh: bool = False
    ) -> DistributionSnapshot:
        """
        Get current distribution snapshot.
        
        Uses cached snapshot if fresh, otherwise fetches from database.
        
        Args:
            force_refresh: Force fresh snapshot even if cache is valid
            
        Returns:
            DistributionSnapshot with current distribution state
            
        Principle 4: Database is single source of truth
        Principle 5: Async database operations
        """
        # Return cached snapshot if fresh and not forcing refresh
        if not force_refresh and self._is_snapshot_fresh():
            self.logger.debug("Using cached snapshot")
            return self._last_snapshot
        
        self.logger.info("Capturing fresh distribution snapshot...")
        
        # Query for total supply
        total_query = """
            SELECT COALESCE(SUM(balance), 0) as total_supply
            FROM account_balances
            WHERE asset_code = $1
        """
        
        total_result = await self.db.fetch_one(total_query, (self.ubec_code,))
        total_supply = total_result['total_supply']
        
        if total_supply == 0:
            raise Exception(f"No supply found for {self.ubec_code}")
        
        # Query for specific account balances
        # v4.2.0 FIX: Removed asset_issuer from WHERE clause (column doesn't exist)
        account_query = """
            SELECT balance
            FROM account_balances
            WHERE account_id = $1 AND asset_code = $2
        """
        
        admin_result = await self.db.fetch_one(
            account_query, 
            (self.admin_account, self.ubec_code)
        )
        admin_balance = admin_result['balance'] if admin_result else Decimal('0')
        
        steward_result = await self.db.fetch_one(
            account_query,
            (self.steward_account, self.ubec_code)
        )
        steward_balance = steward_result['balance'] if steward_result else Decimal('0')
        
        # Calculate circulation (everything not in admin or steward)
        circulation_balance = total_supply - admin_balance - steward_balance
        
        # Calculate percentages (as float for consistency)
        admin_pct = float(admin_balance / total_supply) if total_supply > 0 else 0.0
        steward_pct = float(steward_balance / total_supply) if total_supply > 0 else 0.0
        circulation_pct = float(circulation_balance / total_supply) if total_supply > 0 else 0.0
        
        # Create snapshot
        snapshot = DistributionSnapshot(
            timestamp=datetime.now(),
            total_supply=total_supply,
            admin_balance=admin_balance,
            steward_balance=steward_balance,
            circulation_balance=circulation_balance,
            admin_percentage=admin_pct,
            steward_percentage=steward_pct,
            circulation_percentage=circulation_pct
        )
        
        # Update cache
        self._last_snapshot = snapshot
        self._last_snapshot_time = datetime.now()
        
        self.logger.info(
            f"✓ Snapshot captured - Supply: {total_supply}, "
            f"Admin: {admin_pct:.2%}, Steward: {steward_pct:.2%}"
        )
        
        return snapshot
    
    def _is_snapshot_fresh(self) -> bool:
        """Check if cached snapshot is still fresh"""
        if not self._last_snapshot or not self._last_snapshot_time:
            return False
        
        age_seconds = (datetime.now() - self._last_snapshot_time).total_seconds()
        return age_seconds < self._cache_ttl
    
    # ==================== COMPLIANCE OPERATIONS ====================
    
    async def check_compliance(
        self,
        snapshot: Optional[DistributionSnapshot] = None
    ) -> ComplianceStatus:
        """
        Check compliance status against tokenomics targets.
        
        Args:
            snapshot: Optional snapshot to check. If None, gets fresh snapshot.
            
        Returns:
            ComplianceStatus with compliance details
            
        Principle 5: Async operation.
        """
        # Get snapshot if not provided
        if snapshot is None:
            snapshot = await self.get_distribution_snapshot()
        
        # Calculate deviations (all float operations - consistent types)
        admin_deviation = abs(snapshot.admin_percentage - self.admin_target)
        steward_deviation = abs(snapshot.steward_percentage - self.steward_target)
        
        # Check compliance (within threshold)
        admin_compliant = admin_deviation <= self.threshold
        steward_compliant = steward_deviation <= self.threshold
        is_compliant = admin_compliant and steward_compliant
        
        # Determine if rebalance needed
        requires_rebalance = not is_compliant
        
        # Generate recommendations
        recommendations = []
        if not admin_compliant:
            direction = "increase" if snapshot.admin_percentage < self.admin_target else "decrease"
            recommendations.append(
                f"Administration balance needs adjustment: {direction} by "
                f"{admin_deviation:.2%} to reach target {self.admin_target:.1%}"
            )
        
        if not steward_compliant:
            direction = "increase" if snapshot.steward_percentage < self.steward_target else "decrease"
            recommendations.append(
                f"Stewardship balance needs adjustment: {direction} by "
                f"{steward_deviation:.2%} to reach target {self.steward_target:.1%}"
            )
        
        if is_compliant:
            recommendations.append("Distribution is compliant - no action needed")
        
        return ComplianceStatus(
            is_compliant=is_compliant,
            admin_compliant=admin_compliant,
            steward_compliant=steward_compliant,
            admin_deviation=admin_deviation,
            steward_deviation=steward_deviation,
            requires_rebalance=requires_rebalance,
            recommendations=recommendations
        )
    
    async def get_rebalancing_recommendations(
        self,
        snapshot: Optional[DistributionSnapshot] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detailed rebalancing recommendations.
        
        Args:
            snapshot: Optional snapshot. If None, gets fresh snapshot.
            
        Returns:
            List of rebalancing actions with amounts
            
        Principle 5: Async operation.
        """
        # Get snapshot if not provided
        if snapshot is None:
            snapshot = await self.get_distribution_snapshot()
        
        recommendations = []
        
        # Calculate required adjustments
        target_admin = snapshot.total_supply * Decimal(str(self.admin_target))
        target_steward = snapshot.total_supply * Decimal(str(self.steward_target))
        
        admin_diff = target_admin - snapshot.admin_balance
        steward_diff = target_steward - snapshot.steward_balance
        
        # Check if adjustments exceed threshold
        if abs(float(admin_diff / snapshot.total_supply)) > self.threshold:
            recommendations.append({
                'account': 'administration',
                'account_id': self.admin_account,
                'current_balance': float(snapshot.admin_balance),
                'target_balance': float(target_admin),
                'adjustment_needed': float(admin_diff),
                'adjustment_type': 'increase' if admin_diff > 0 else 'decrease'
            })
        
        if abs(float(steward_diff / snapshot.total_supply)) > self.threshold:
            recommendations.append({
                'account': 'stewardship',
                'account_id': self.steward_account,
                'current_balance': float(snapshot.steward_balance),
                'target_balance': float(target_steward),
                'adjustment_needed': float(steward_diff),
                'adjustment_type': 'increase' if steward_diff > 0 else 'decrease'
            })
        
        return recommendations
    
    # ==================== COMPREHENSIVE AUDIT ====================
    
    async def perform_comprehensive_audit(self) -> Dict[str, Any]:
        """
        Perform comprehensive audit of token distribution.
        
        This is the main audit method that:
        1. Captures current distribution snapshot
        2. Checks compliance against targets
        3. Generates recommendations if needed
        4. Tracks audit history
        
        Returns:
            Dict with audit results:
            {
                'timestamp': str,
                'snapshot': {...},
                'compliance': {...},
                'is_compliant': bool,
                'requires_action': bool
            }
            
        Example:
            result = await audit.perform_comprehensive_audit()
            if result['requires_action']:
                print("Action required!")
                for rec in result['compliance']['recommendations']:
                    print(f"  {rec}")
        """
        self.logger.info("Performing comprehensive audit...")
        
        # Get fresh snapshot
        snapshot = await self.get_distribution_snapshot(force_refresh=True)
        
        # Check compliance
        compliance = await self.check_compliance(snapshot)
        
        # Update audit tracking
        self._last_audit_time = datetime.now()
        self._audit_count += 1
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'audit_number': self._audit_count,
            'snapshot': {
                'total_supply': float(snapshot.total_supply),
                'admin_balance': float(snapshot.admin_balance),
                'steward_balance': float(snapshot.steward_balance),
                'circulation_balance': float(snapshot.circulation_balance),
                'admin_percentage': snapshot.admin_percentage,
                'steward_percentage': snapshot.steward_percentage,
                'circulation_percentage': snapshot.circulation_percentage
            },
            'compliance': {
                'is_compliant': compliance.is_compliant,
                'admin_compliant': compliance.admin_compliant,
                'steward_compliant': compliance.steward_compliant,
                'admin_deviation': compliance.admin_deviation,
                'steward_deviation': compliance.steward_deviation,
                'admin_target': self.admin_target,
                'steward_target': self.steward_target,
                'threshold': self.threshold,
                'requires_rebalance': compliance.requires_rebalance,
                'recommendations': compliance.recommendations
            },
            'is_compliant': compliance.is_compliant,
            'requires_action': compliance.requires_rebalance
        }
        
        self.logger.info(
            f"✓ Audit #{self._audit_count} complete - "
            f"Compliant: {compliance.is_compliant}"
        )
        
        return result
    
    # ==================== DISTRIBUTION EVALUATOR INTERFACE ====================
    # v4.1.0 Addition: Interface method for distribution evaluator integration
    
    async def check_distribution_compliance(self) -> Dict[str, Any]:
        """
        Check distribution compliance for evaluator integration.
        
        This method provides the interface expected by UBECDistributionEvaluator.
        It wraps perform_comprehensive_audit() with a standardized response format.
        
        v4.4.0 ENHANCEMENT: All numeric values guaranteed to be float type
        to prevent TypeError in distribution evaluator calculations.
        
        Returns:
            Dict with compliance check results:
            {
                'overall_compliant': bool,
                'compliance_details': {
                    'administration': {...},
                    'stewardship': {...}
                },
                'deviations': {...},
                'recommendations': [...],
                'timestamp': str
            }
        
        Design Notes:
            - Principle #12: Method Singularity - wraps existing functionality
            - Principle #3: Service Registry - provides expected interface
            - v4.4.0: Ensures all numeric values are float (not Decimal)
            - Added in v4.1.0 to fix AttributeError in distribution evaluator
        
        Example:
            # Called by distribution evaluator
            compliance = await audit_service.check_distribution_compliance()
            if not compliance['overall_compliant']:
                print("Distribution non-compliant!")
        """
        self.logger.debug("Checking distribution compliance for evaluator...")
        
        # Perform comprehensive audit
        audit_result = await self.perform_comprehensive_audit()
        
        # Transform to evaluator-expected format
        # v4.4.0 CRITICAL: Ensure ALL numeric values are float, not Decimal
        # This prevents TypeError: unsupported operand type(s) for /: 'float' and 'decimal.Decimal'
        compliance_result = {
            'overall_compliant': audit_result['is_compliant'],
            'compliance_details': {
                'administration': {
                    'compliant': audit_result['compliance']['admin_compliant'],
                    'current_percentage': float(audit_result['snapshot']['admin_percentage']),
                    'target_percentage': float(audit_result['compliance']['admin_target']),
                    'deviation': float(audit_result['compliance']['admin_deviation']),
                    'balance': float(audit_result['snapshot']['admin_balance'])
                },
                'stewardship': {
                    'compliant': audit_result['compliance']['steward_compliant'],
                    'current_percentage': float(audit_result['snapshot']['steward_percentage']),
                    'target_percentage': float(audit_result['compliance']['steward_target']),
                    'deviation': float(audit_result['compliance']['steward_deviation']),
                    'balance': float(audit_result['snapshot']['steward_balance'])
                }
            },
            'deviations': {
                'administration': {
                    'actual': float(audit_result['snapshot']['admin_percentage']),
                    'target': float(audit_result['compliance']['admin_target']),
                    'deviation_percent': float(abs(audit_result['compliance']['admin_deviation']) * 100)
                },
                'stewardship': {
                    'actual': float(audit_result['snapshot']['steward_percentage']),
                    'target': float(audit_result['compliance']['steward_target']),
                    'deviation_percent': float(abs(audit_result['compliance']['steward_deviation']) * 100)
                },
                'general': {
                    'actual': float(audit_result['snapshot']['circulation_percentage']),
                    'target': float(1.0 - audit_result['compliance']['admin_target'] - audit_result['compliance']['steward_target']),
                    'deviation_percent': 0.0  # General is derived, not directly checked
                }
            },
            'compliance': {
                'administration': audit_result['compliance']['admin_compliant'],
                'stewardship': audit_result['compliance']['steward_compliant']
            },
            'recommendations': audit_result['compliance']['recommendations'],
            'requires_rebalance': audit_result['requires_action'],
            'timestamp': audit_result['timestamp'],
            'audit_number': audit_result['audit_number']
        }
        
        self.logger.debug(
            f"✓ Compliance check complete: {'PASS' if compliance_result['overall_compliant'] else 'FAIL'}"
        )
        
        return compliance_result
    
    # ==================== HEALTH CHECK ====================
    # Principle 7: Per-Asset Monitoring
    # Principle 12: Uses ServiceHealthCheck utility
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on audit service.
        
        Uses ServiceHealthCheck utility (Principle #12: Method Singularity)
        for standardized health reporting across all services.
        
        Returns:
            Health status dictionary with:
            - status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown'
            - message: Human-readable status message
            - timestamp: ISO timestamp
            - details: Service-specific health metrics
            
        Principle 7: Comprehensive per-service monitoring
        Principle 12: Uses shared ServiceHealthCheck utility
        """
        async def check_config_validity():
            """Verify configuration is valid"""
            if not self.admin_account or not self.steward_account:
                raise Exception("Missing tokenomics account configuration")
            
            if not 0 < self.admin_target < 1 or not 0 < self.steward_target < 1:
                raise Exception(f"Invalid targets: admin={self.admin_target}, steward={self.steward_target}")
            
            if self.admin_target + self.steward_target >= 1:
                raise Exception(
                    f"Combined targets exceed 100%: "
                    f"{self.admin_target:.1%} + {self.steward_target:.1%}"
                )
            
            return f"Valid targets: admin={self.admin_target:.1%}, steward={self.steward_target:.1%}"
        
        async def check_tokenomics_accounts():
            """Verify tokenomics accounts exist and have balances"""
            # v4.2.0 FIX: Removed asset_issuer from WHERE clause (column doesn't exist)
            admin_query = """
                SELECT balance
                FROM account_balances
                WHERE account_id = $1 AND asset_code = $2
            """
            
            # Check admin account
            admin_result = await self.db.fetch_one(admin_query, (self.admin_account, self.ubec_code))
            if not admin_result:
                raise Exception(f"Administration account {self.admin_account[:8]}... not found in database")
            
            # Check steward account
            steward_result = await self.db.fetch_one(admin_query, (self.steward_account, self.ubec_code))
            if not steward_result:
                raise Exception(f"Stewardship account {self.steward_account[:8]}... not found in database")
            
            admin_balance = admin_result['balance']
            steward_balance = steward_result['balance']
            
            return f"Tokenomics accounts verified (admin: {admin_balance}, steward: {steward_balance})"
        
        async def check_audit_recency():
            """Verify audits are being run regularly"""
            if not self._last_audit_time:
                raise Exception("No audits performed yet")
            
            audit_age_seconds = (datetime.now() - self._last_audit_time).total_seconds()
            audit_age_hours = audit_age_seconds / 3600
            
            if audit_age_hours > 24:
                raise Exception(f"Last audit was {audit_age_hours:.1f} hours ago (threshold: 24 hours)")
            
            return f"Last audit {audit_age_hours:.1f} hours ago (within threshold)"
        
        async def check_cache_health():
            """Verify snapshot cache is functioning properly"""
            if not self._last_snapshot:
                return "No snapshot cache yet (service starting up)"
            
            if not self._last_snapshot_time:
                raise Exception("Snapshot exists but no timestamp (cache corrupted?)")
            
            cache_age_seconds = (datetime.now() - self._last_snapshot_time).total_seconds()
            cache_age_minutes = cache_age_seconds / 60
            
            if cache_age_seconds > self._cache_ttl * 2:
                raise Exception(
                    f"Snapshot cache very stale ({cache_age_minutes:.1f} minutes old, "
                    f"TTL: {self._cache_ttl/60:.1f} minutes)"
                )
            
            is_fresh = cache_age_seconds < self._cache_ttl
            freshness = "fresh" if is_fresh else "stale but acceptable"
            return f"Cache {freshness} ({cache_age_minutes:.1f} minutes old)"
        
        # Determine cache freshness for details
        cache_fresh = self._is_snapshot_fresh()
        
        # Use ServiceHealthCheck utility (Principle #12: Method Singularity)
        return await ServiceHealthCheck.database_dependent_health(
            service_name='audit',
            db_manager=self.db,
            is_initialized=self._initialized,
            additional_checks=[
                check_config_validity,
                check_tokenomics_accounts,
                check_cache_health,
                check_audit_recency
            ],
            # Additional context for health response
            cache_fresh=cache_fresh,
            last_snapshot=self._last_snapshot_time.isoformat() if self._last_snapshot_time else None,
            last_audit=self._last_audit_time.isoformat() if self._last_audit_time else None,
            audit_count=self._audit_count,
            ubec_code=self.ubec_code,
            admin_account_configured=bool(self.admin_account),
            steward_account_configured=bool(self.steward_account),
            admin_target=str(self.admin_target),
            steward_target=str(self.steward_target),
            cache_ttl_seconds=self._cache_ttl
        )
    
    # ==================== LIFECYCLE ====================
    
    async def close(self) -> None:
        """
        Close audit service and cleanup resources.
        
        Principle 5: Async cleanup.
        """
        self.logger.info("Closing audit service...")
        self._last_snapshot = None
        self._last_snapshot_time = None
        self._initialized = False
        self.logger.info("Audit service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

async def create_audit_service(
    db_manager,
    config: Dict[str, Any],
    holonic_evaluator=None
) -> UBECAuditService:
    """
    Factory function to create UBEC audit service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - ubec_code: UBEC token code
            - ubec_issuer: Issuer address
            - administration_account: Admin account address
            - stewardship_account: Steward account address
            - tokenomics: Dict with targets and thresholds
        holonic_evaluator: Optional holonic evaluator service
    
    Returns:
        UBECAuditService: Initialized service instance
        
    Example:
        audit = await create_audit_service(
            db_manager=db,
            config={
                'ubec_code': 'UBEC',
                'ubec_issuer': 'G...',
                'administration_account': 'G...',
                'stewardship_account': 'G...',
                'tokenomics': {
                    'administration_target': 0.05,
                    'stewardship_target': 0.30,
                    'compliance_threshold': 0.02
                }
            }
        )
        
        result = await audit.perform_comprehensive_audit()
        compliance = await audit.check_distribution_compliance()
    """
    # Create service instance
    service = UBECAuditService(
        db_manager=db_manager,
        config=config,
        holonic_evaluator=holonic_evaluator
    )
    
    # Initialize it
    await service.initialize()
    
    return service


# ==================== MODULE EXPORTS ====================
# Principle 1: Modular Design - Clear public interface

__all__ = [
    # Service
    'UBECAuditService',
    'create_audit_service',
    
    # Data models
    'DistributionSnapshot',
    'ComplianceStatus'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Principle 2: Service Pattern - No standalone execution

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from services.audit.ubec_audit_service import create_audit_service\n"
        "  audit = await create_audit_service(db_manager, config)\n"
        "  result = await audit.perform_comprehensive_audit()\n"
        "  compliance = await audit.check_distribution_compliance()\n"
        "  health = await audit.health_check()\n\n"
        "Version 4.4.0 - Float Type Consistency Fix:\n"
        "  - CRITICAL FIX: All numeric values now guaranteed to be float type\n"
        "  - Converts admin_target, steward_target, threshold to float in __init__\n"
        "  - Prevents TypeError: unsupported operand type(s) for /: 'float' and 'decimal.Decimal'\n"
        "  - All values in check_distribution_compliance() explicitly converted to float\n"
        "  - Implements Principle #12: Centralized type conversion pattern\n\n"
        "Version 4.3.0 - Data Structure Alignment Fix:\n"
        "  - CRITICAL FIX: Fixed deviations structure in check_distribution_compliance()\n"
        "  - Added nested dict format expected by distribution evaluator\n"
        "  - Each deviation now includes: actual, target, deviation_percent\n"
        "  - Resolves TypeError: 'float' object is not subscriptable\n\n"
        "Version 4.2.0 - Database Schema Alignment Fix:\n"
        "  - CRITICAL FIX: Corrected get_distribution_snapshot() database query\n"
        "  - Removed asset_issuer column reference (doesn't exist in account_balances)\n"
        "  - Query now correctly filters by asset_code only\n"
        "  - Resolves asyncpg.exceptions.UndefinedColumnError\n\n"
        "Version 4.1.0 - Distribution Evaluator Interface Fix:\n"
        "  - CRITICAL FIX: Added check_distribution_compliance() method\n"
        "  - Fixes AttributeError in distribution evaluator integration\n"
        "  - Wraps perform_comprehensive_audit() with evaluator-expected format\n"
        "  - Implements Principle #12: Method Singularity (wraps, not duplicates)\n"
        "  - Maintains all existing functionality\n\n"
        "Version 4.0.0 - ServiceHealthCheck Integration:\n"
        "  - Uses ServiceHealthCheck.database_dependent_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Four custom health checks for comprehensive monitoring\n"
        "  - Standardized health response format\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
