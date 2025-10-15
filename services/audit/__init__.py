#!/usr/bin/env python3
# services/audit/__init__.py
"""
UBEC Audit Services Package
============================

Comprehensive auditing services for UBEC token distribution, tokenomics
compliance verification, and holonic evaluation integration.

This package provides:
    - Token distribution analysis and reporting
    - Tokenomics compliance monitoring (5% admin, 30% stewardship)
    - Liquidity pool tracking and ownership calculation
    - Historical audit trail persistence
    - Anomaly detection and alerting
    - Integration with holonic evaluation system

Core Services:
    UBECAuditService: Main async audit service for comprehensive auditing

Data Models:
    ComplianceStatus: Enum for compliance states
    AccountBalance: Individual account balance information
    LiquidityPoolInfo: Liquidity pool tracking data
    DistributionSnapshot: Point-in-time distribution state
    ComplianceReport: Tokenomics compliance analysis
    AuditReport: Comprehensive audit report

Usage:
    ```python
    from services.audit import create_audit_service, ComplianceStatus
    
    # Create audit service
    audit = await create_audit_service(
        db_manager=db,
        config={
            'ubec_code': 'UBEC',
            'ubec_issuer': 'GDPNB7S3...',
            'db_schema': 'ubec_main',
            'administration_account': 'GC5X...',
            'stewardship_account': 'GDBK...',
            'tokenomics': {
                'administration_target': 0.05,
                'stewardship_target': 0.30,
                'compliance_threshold': 0.01
            }
        }
    )
    
    # Perform comprehensive audit
    report = await audit.perform_comprehensive_audit()
    
    # Check compliance
    if not report.compliance.overall_compliant:
        print("Compliance issues detected!")
        for rec in report.compliance.recommendations:
            print(f"  - {rec}")
    
    # Get distribution snapshot
    snapshot = await audit.get_distribution_snapshot()
    print(f"Total holders: {snapshot.total_holders}")
    
    # Cleanup
    await audit.close()
    ```

Design Principles:
    ✅ Modular Design - Clear package structure
    ✅ Service Pattern - Factory-based instantiation
    ✅ Service Registry - Ready for centralized registry
    ✅ Single Source of Truth - Database-driven
    ✅ Strict Async - 100% async operations
    ✅ Comprehensive Documentation - Full docstrings

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 3.0.0
Date: October 15, 2025
"""

from .ubec_audit_service import (
    # Core service
    UBECAuditService,
    create_audit_service,
    
    # Enumerations
    ComplianceStatus,
    
    # Data models
    AccountBalance,
    LiquidityPoolInfo,
    DistributionSnapshot,
    ComplianceReport,
    AuditReport,
)

# Version information
__version__ = '3.0.0'
__author__ = 'UBEC Protocol Team'
__date__ = 'October 15, 2025'

# Public interface
__all__ = [
    # Core service (primary interface)
    'UBECAuditService',
    'create_audit_service',
    
    # Enumerations
    'ComplianceStatus',
    
    # Data models (for type hints and direct usage)
    'AccountBalance',
    'LiquidityPoolInfo',
    'DistributionSnapshot',
    'ComplianceReport',
    'AuditReport',
    
    # Package metadata
    '__version__',
    '__author__',
    '__date__',
]


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_version() -> str:
    """
    Get the package version.
    
    Returns:
        str: Package version string
        
    Example:
        >>> from services.audit import get_version
        >>> print(get_version())
        3.0.0
    """
    return __version__


def get_package_info() -> dict:
    """
    Get comprehensive package information.
    
    Returns:
        dict: Package metadata including version, author, and capabilities
        
    Example:
        >>> from services.audit import get_package_info
        >>> info = get_package_info()
        >>> print(f"Version: {info['version']}")
        >>> print(f"Services: {', '.join(info['services'])}")
    """
    return {
        'name': 'services.audit',
        'version': __version__,
        'author': __author__,
        'date': __date__,
        'services': ['UBECAuditService'],
        'capabilities': [
            'token_distribution_analysis',
            'tokenomics_compliance',
            'liquidity_pool_tracking',
            'holonic_integration',
            'historical_audit_trail',
            'anomaly_detection'
        ],
        'data_models': [
            'AccountBalance',
            'LiquidityPoolInfo',
            'DistributionSnapshot',
            'ComplianceReport',
            'AuditReport'
        ]
    }


# ============================================================================
# PACKAGE VALIDATION
# ============================================================================

def _validate_package() -> None:
    """
    Validate package imports and dependencies.
    
    This function is called on package import to ensure all required
    dependencies are available and properly configured.
    
    Raises:
        ImportError: If required dependencies are missing
    """
    # Verify all exports are available
    required_exports = [
        'UBECAuditService',
        'create_audit_service',
        'ComplianceStatus',
        'AccountBalance',
        'LiquidityPoolInfo',
        'DistributionSnapshot',
        'ComplianceReport',
        'AuditReport'
    ]
    
    for export in required_exports:
        if export not in globals():
            raise ImportError(
                f"Required export '{export}' not available in services.audit package. "
                "This indicates a packaging or import error."
            )


# Run validation on import
try:
    _validate_package()
except ImportError as e:
    import logging
    logging.error(f"Audit package validation failed: {e}")
    raise


# ============================================================================
# DEPRECATION WARNINGS
# ============================================================================

def _check_deprecated_imports() -> None:
    """
    Check for and warn about deprecated import patterns.
    
    This helps users migrate from old audit module to new service.
    """
    import sys
    import warnings
    
    # Check if old module is being imported
    if 'audit.ubec_token_audit' in sys.modules:
        warnings.warn(
            "The 'audit.ubec_token_audit' module is deprecated and will be removed in v4.0.0. "
            "Please migrate to 'services.audit.ubec_audit_service'. "
            "See IMPLEMENTATION_GUIDE.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2
        )


# Run deprecation check
_check_deprecated_imports()


# ============================================================================
# MODULE DOCSTRING ENHANCEMENT
# ============================================================================

# Add dynamic information to module docstring
_module_doc_addendum = f"""

Package Information:
    Version: {__version__}
    Author: {__author__}
    Date: {__date__}
    
Available Services:
    - UBECAuditService: Comprehensive token audit service
    
Factory Functions:
    - create_audit_service(): Async factory for audit service instantiation
    
Data Models:
    - ComplianceStatus: Compliance state enumeration
    - AccountBalance: Account balance information
    - LiquidityPoolInfo: Liquidity pool tracking
    - DistributionSnapshot: Distribution state snapshot
    - ComplianceReport: Tokenomics compliance report
    - AuditReport: Comprehensive audit report
    
Quick Start:
    from services.audit import create_audit_service
    
    audit = await create_audit_service(db_manager, config)
    report = await audit.perform_comprehensive_audit()
    await audit.close()
"""

__doc__ += _module_doc_addendum
