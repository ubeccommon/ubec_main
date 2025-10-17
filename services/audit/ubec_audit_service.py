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
    
    # Check health
    health = await audit.health_check()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 4.0.0 (ServiceHealthCheck Integration)
Date: October 17, 2025
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
        admin_target: Target % for administration (0-1)
        steward_target: Target % for stewardship (0-1)
        threshold: Compliance threshold for deviations
        holonic_evaluator: Optional holonic evaluator for account scoring
        
    Design Notes:
        - Principle 2: Factory pattern via create_audit_service()
        - Principle 4: Database is single source of truth
        - Principle 5: All operations async
        - Principle 12: Uses ServiceHealthCheck utility
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
        
        # Tokenomics targets
        tokenomics = config.get('tokenomics', {})
        self.admin_target = tokenomics.get('administration_target', 0.05)
        self.steward_target = tokenomics.get('stewardship_target', 0.30)
        self.threshold = tokenomics.get('compliance_threshold', 0.02)
        
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
        if self._initialized:
            self.logger.warning("Audit service already initialized")
            return
        
        self.logger.info("Initializing audit service...")
        
        # Verify database connection
        try:
            await self.db.execute("SELECT 1")
            self.logger.info("✓ Database connection verified")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
        
        # Validate configuration
        self._validate_config()
        
        self._initialized = True
        self.logger.info("✓ Audit service initialized")
    
    def _validate_config(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.ubec_code:
            raise ValueError("ubec_code not configured")
        
        if not self.ubec_issuer:
            raise ValueError("ubec_issuer not configured")
        
        if not self.admin_account:
            raise ValueError("administration_account not configured")
        
        if not self.steward_account:
            raise ValueError("stewardship_account not configured")
        
        if self.admin_target <= 0 or self.admin_target >= 1:
            raise ValueError(f"Invalid administration_target: {self.admin_target}")
        
        if self.steward_target <= 0 or self.steward_target >= 1:
            raise ValueError(f"Invalid stewardship_target: {self.steward_target}")
        
        self.logger.info(
            f"✓ Configuration valid: {self.ubec_code}, "
            f"targets: {self.admin_target:.1%}/{self.steward_target:.1%}"
        )
    
    # ==================== SNAPSHOT OPERATIONS ====================
    
    def _is_snapshot_fresh(self) -> bool:
        """Check if cached snapshot is still fresh"""
        if not self._last_snapshot_time:
            return False
        age = (datetime.now() - self._last_snapshot_time).total_seconds()
        return age < self._cache_ttl
    
    async def get_distribution_snapshot(
        self,
        force_refresh: bool = False
    ) -> DistributionSnapshot:
        """
        Get current distribution snapshot.
        
        Uses cached snapshot if fresh, otherwise queries database.
        Principle 4: Database is single source of truth.
        
        Args:
            force_refresh: Force database query ignoring cache
            
        Returns:
            DistributionSnapshot with current distribution
            
        Example:
            snapshot = await audit.get_distribution_snapshot()
            print(f"Admin: {snapshot.admin_percentage:.2%}")
            print(f"Steward: {snapshot.steward_percentage:.2%}")
        """
        # Return cached if fresh and not forcing refresh
        if not force_refresh and self._is_snapshot_fresh():
            self.logger.debug("Returning cached snapshot")
            return self._last_snapshot
        
        self.logger.info("Querying database for distribution snapshot...")
        
        # Query total supply
        supply_query = """
            SELECT COALESCE(SUM(balance), 0) as total_supply
            FROM ubec_main.ubec_balances
            WHERE asset_code = $1
        """
        supply_result = await self.db.fetch_one(supply_query, self.ubec_code)
        total_supply = Decimal(str(supply_result['total_supply']))
        
        # Query admin balance
        admin_query = """
            SELECT COALESCE(balance, 0) as balance
            FROM ubec_main.ubec_balances
            WHERE account_id = $1 AND asset_code = $2
        """
        admin_result = await self.db.fetch_one(
            admin_query, self.admin_account, self.ubec_code
        )
        admin_balance = Decimal(str(admin_result['balance'])) if admin_result else Decimal('0')
        
        # Query steward balance
        steward_result = await self.db.fetch_one(
            admin_query, self.steward_account, self.ubec_code
        )
        steward_balance = Decimal(str(steward_result['balance'])) if steward_result else Decimal('0')
        
        # Calculate circulation (total - admin - steward)
        circulation_balance = total_supply - admin_balance - steward_balance
        
        # Calculate percentages
        if total_supply > 0:
            admin_pct = float(admin_balance / total_supply)
            steward_pct = float(steward_balance / total_supply)
            circulation_pct = float(circulation_balance / total_supply)
        else:
            admin_pct = steward_pct = circulation_pct = 0.0
        
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
        
        # Cache it
        self._last_snapshot = snapshot
        self._last_snapshot_time = datetime.now()
        
        self.logger.info(
            f"✓ Snapshot captured: Admin={admin_pct:.2%}, "
            f"Steward={steward_pct:.2%}, Circulation={circulation_pct:.2%}"
        )
        
        return snapshot
    
    # ==================== COMPLIANCE CHECKING ====================
    
    async def check_compliance(
        self,
        snapshot: Optional[DistributionSnapshot] = None
    ) -> ComplianceStatus:
        """
        Check tokenomics compliance against targets.
        
        Args:
            snapshot: Optional snapshot to check, otherwise gets fresh one
            
        Returns:
            ComplianceStatus with compliance results
            
        Example:
            status = await audit.check_compliance()
            if not status.is_compliant:
                print(f"Deviations: Admin={status.admin_deviation:.2%}")
                for rec in status.recommendations:
                    print(f"  - {rec}")
        """
        if snapshot is None:
            snapshot = await self.get_distribution_snapshot()
        
        # Calculate deviations from targets
        admin_deviation = snapshot.admin_percentage - self.admin_target
        steward_deviation = snapshot.steward_percentage - self.steward_target
        
        # Check if within threshold
        admin_compliant = abs(admin_deviation) <= self.threshold
        steward_compliant = abs(steward_deviation) <= self.threshold
        is_compliant = admin_compliant and steward_compliant
        
        # Determine if rebalancing required
        requires_rebalance = not is_compliant
        
        # Generate recommendations
        recommendations = []
        
        if not admin_compliant:
            if admin_deviation > 0:
                recommendations.append(
                    f"Administration account {admin_deviation:.2%} over target - "
                    f"reduce by {abs(admin_deviation * float(snapshot.total_supply)):.2f} UBEC"
                )
            else:
                recommendations.append(
                    f"Administration account {abs(admin_deviation):.2%} under target - "
                    f"increase by {abs(admin_deviation * float(snapshot.total_supply)):.2f} UBEC"
                )
        
        if not steward_compliant:
            if steward_deviation > 0:
                recommendations.append(
                    f"Stewardship account {steward_deviation:.2%} over target - "
                    f"reduce by {abs(steward_deviation * float(snapshot.total_supply)):.2f} UBEC"
                )
            else:
                recommendations.append(
                    f"Stewardship account {abs(steward_deviation):.2%} under target - "
                    f"increase by {abs(steward_deviation * float(snapshot.total_supply)):.2f} UBEC"
                )
        
        return ComplianceStatus(
            is_compliant=is_compliant,
            admin_compliant=admin_compliant,
            steward_compliant=steward_compliant,
            admin_deviation=admin_deviation,
            steward_deviation=steward_deviation,
            requires_rebalance=requires_rebalance,
            recommendations=recommendations
        )
    
    # ==================== AUDIT OPERATIONS ====================
    
    async def perform_comprehensive_audit(self) -> Dict[str, Any]:
        """
        Perform comprehensive audit of token distribution.
        
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
    
    # ==================== HEALTH CHECK ====================
    # Principle 7: Per-Asset Monitoring
    # Principle 12: Uses ServiceHealthCheck utility
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on audit service.
        
        Uses ServiceHealthCheck utility (Principle #12: Method Singularity)
        for standardized health reporting across all services.
        
        Implements Principle #7 (Per-Asset Monitoring) with detailed metrics:
        - Database connectivity
        - Configuration validation
        - Cache freshness monitoring
        - Audit recency tracking
        - Tokenomics account verification
        
        Returns:
            Dict with health status and comprehensive metrics
            
        Example:
            health = await audit.health_check()
            if health['status'] == 'healthy':
                print("✓ Audit service operational")
            else:
                print(f"Issues: {health['message']}")
        """
        async def check_config_validity():
            """Verify all required configuration is present and valid"""
            errors = []
            
            if not self.ubec_code:
                errors.append("ubec_code not configured")
            if not self.ubec_issuer:
                errors.append("ubec_issuer not configured")
            if not self.admin_account:
                errors.append("administration_account not configured")
            if not self.steward_account:
                errors.append("stewardship_account not configured")
            if self.admin_target <= 0 or self.admin_target >= 1:
                errors.append(f"Invalid administration_target: {self.admin_target}")
            if self.steward_target <= 0 or self.steward_target >= 1:
                errors.append(f"Invalid stewardship_target: {self.steward_target}")
            
            if errors:
                raise Exception(f"Configuration validation failed: {', '.join(errors)}")
            
            return f"Configuration valid (ubec_code={self.ubec_code}, targets: {self.admin_target:.1%}/{self.steward_target:.1%})"
        
        async def check_tokenomics_accounts():
            """Verify tokenomics accounts exist in database"""
            admin_query = """
                SELECT account_id, balance
                FROM ubec_main.ubec_balances
                WHERE account_id = $1 AND asset_code = $2
            """
            
            # Check admin account
            admin_result = await self.db.fetch_one(admin_query, self.admin_account, self.ubec_code)
            if not admin_result:
                raise Exception(f"Administration account {self.admin_account[:8]}... not found in database")
            
            # Check steward account
            steward_result = await self.db.fetch_one(admin_query, self.steward_account, self.ubec_code)
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
        "  health = await audit.health_check()\n\n"
        "Version 4.0.0 - ServiceHealthCheck Integration:\n"
        "  - Uses ServiceHealthCheck.database_dependent_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Four custom health checks for comprehensive monitoring\n"
        "  - Standardized health response format\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
