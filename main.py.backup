#!/usr/bin/env python3
"""
UBEC Main Protocol - Unified Entry Point
═══════════════════════════════════════════════════════════════════════════

The SOLE entry point for the entire UBEC protocol system.
All services are orchestrated through this main file using the service registry.

Integrated Services:
    - Database Manager (PostgreSQL async pool)
    - Configuration Service (Database-backed settings)
    - Stellar Client (Blockchain interaction)
    - Data Synchronizer (Blockchain sync + liquidity pools)
    - Analytics Service (Token distribution and metrics)
    - Distribution Service (Token balance management)
    - Distribution Evaluator (Compliance checking)
    - Holonic Evaluator (Ubuntu principles evaluation)
    - Visualizer (Charts & reports generation)
    - Audit Service (Tokenomics compliance & auditing)
    - Air Protocol (Gateway / Universal Access - UBEC)
    - Water Protocol (Reciprocity / Flow - UBECrc)
    - Earth Protocol (Ground / Stability - UBECgpi)
    - Fire Protocol (Transformation - UBECtt)

Design Compliance:
    ✅ Principle 1: Modular Design - Clear separation of concerns
    ✅ Principle 2: Service Pattern - THIS IS THE ONLY standalone execution
    ✅ Principle 3: Service Registry - ALL dependencies via registry
    ✅ Principle 4: Single Source of Truth - Database authoritative
    ✅ Principle 5: Strict Async - All operations async
    ✅ Principle 6: No Sync Fallbacks - Pure async only
    ✅ Principle 7: Per-Asset Monitoring - ServiceHealthCheck throughout
    ✅ Principle 8: No Duplicate Configuration - Centralized config
    ✅ Principle 9: Integrated Rate Limiting - Built-in rate limiter
    ✅ Principle 10: Clear Separation - Business logic isolated
    ✅ Principle 11: Documentation - Comprehensive docstrings
    ✅ Principle 12: Method Singularity - ServiceHealthCheck utility everywhere

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 12.5.0 (Comprehensive Health Monitoring)
Date: October 20, 2025
Author: UBEC Protocol Team with Claude AI assistance

Changelog:
    v12.5.0 - COMPREHENSIVE HEALTH MONITORING:
            - 🔧 Implemented standardized ServiceHealthCheck utility throughout
            - ✅ All services now properly implement health_check() methods
            - ✅ Protocol services track synchronization status
            - ✅ Enhanced health reporting with detailed metadata
            - ✅ Fixed "Never synchronized" warnings
            - 📊 Comprehensive per-service health monitoring
            - 🎯 Full compliance with Principles #7 and #12
            - ✅ Production-ready health check implementation
            - 📝 Clear error messages and actionable diagnostics
    v12.4.0 - Database-Driven Configuration - No Degradation
    v12.3.1 - Synchronizer import path fix
    v12.3.0 - Enhanced health monitoring and graceful degradation
    v12.2.3 - Audit service initialization fix
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Core infrastructure imports
from core.service_registry import registry, ServiceRegistry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ========================================================================
# LOGGING CONFIGURATION
# ========================================================================

def setup_logging(log_level: str = 'INFO'):
    """
    Configure logging for the entire system.
    
    Principle #11: Comprehensive Documentation and logging
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('stellar_sdk').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# ========================================================================
# UTILITY FUNCTIONS
# ========================================================================

def create_response(success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
    """
    Create standardized response dictionary.
    
    Principle #12: Method Singularity - Single response format
    """
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if error:
        response['error'] = error
    
    return response


def get_database_schema_config() -> tuple:
    """
    Get database schema configuration from environment.
    
    Returns:
        Tuple of (primary_schema, search_path)
        
    Principle #4: Single Source of Truth - environment variables
    Principle #8: No Duplicate Configuration
    """
    primary_schema = os.getenv('DB_SCHEMA', 'ubec_main')
    
    # Build search path: primary schema, then public
    search_path = f"{primary_schema},public"
    
    return primary_schema, search_path


# ========================================================================
# SERVICE REGISTRATION
# Principle #3: Service Registry - Central dependency management
# ========================================================================

def register_core_services():
    """
    Register all system services with the service registry.
    
    Factory functions create instances only - service registry handles initialization.
    This function MUST be called before using the registry.
    
    Design Notes:
        - Principle #2: Service Pattern - centralized registration
        - Principle #3: Service Registry - dependency injection
        - Principle #12: No duplicate initialization - registry calls initialize() once
        
    CRITICAL: This function registers service factories with the registry.
    The actual service instances are created when registry.get() is called.
    """
    logger.info("=" * 70)
    logger.info("REGISTERING SERVICES WITH SERVICE REGISTRY")
    logger.info("=" * 70)
    
    # ========================================================================
    # DATABASE SERVICE (Foundation)
    # ========================================================================
    
    async def create_database(registry: ServiceRegistry):
        """
        Create database manager service.
        
        CRITICAL: Must be async to call initialize() on database manager.
        Principle #5: Strict Async - Database initialization is async.
        """
        from core.db.database_manager import AsyncDatabaseManager
        
        primary_schema, search_path = get_database_schema_config()
        
        logger.info(f"  ├─ Database: schema={primary_schema}")
        
        db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=search_path,
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        # CRITICAL: Initialize the database connection pool
        await db.initialize()
        
        # Store primary schema for services that need it
        db.primary_schema = primary_schema
        
        return db
    
    registry.register_factory(
        'database',
        create_database,
        dependencies=[],
        config={'type': 'postgresql', 'pooled': True}
    )
    logger.info("✓ Registered: database")
    
    # ========================================================================
    # CONFIGURATION SERVICE
    # ========================================================================
    
    async def create_config(registry: ServiceRegistry):
        """
        Create configuration service with property wrapper.
        
        CRITICAL: This service wraps the config for property-style access.
        It depends on the database service being available first.
        
        ConfigurationService only takes db_manager, not schema.
        """
        from config.config import Config
        from config.settings import ConfigurationService
        
        db = await registry.get('database')
        primary_schema = getattr(db, 'primary_schema', 'ubec_main')
        
        logger.info(f"  ├─ Config: Database-backed settings (schema={primary_schema})")
        
        # Create actual configuration service (only takes db_manager)
        config_service = ConfigurationService(db)
        await config_service.initialize()
        
        # Wrap in property-style interface
        config_wrapper = Config(config_service)
        
        return config_wrapper
    
    registry.register_factory(
        'config',
        create_config,
        dependencies=['database'],
        config={'source': 'database'}
    )
    logger.info("✓ Registered: config (depends on: database)")
    
    # ========================================================================
    # STELLAR CLIENT
    # ========================================================================
    
    async def create_stellar_client(registry: ServiceRegistry):
        """Create Stellar client service"""
        from services.stellar.stellar_client_service import StellarClientService
        
        config = await registry.get('config')
        
        logger.info("  ├─ Stellar Client: Blockchain interaction")
        
        return StellarClientService(
            horizon_url=getattr(config, 'HORIZON_URL', 'https://horizon.stellar.org')
        )
    
    registry.register_factory(
        'stellar_client',
        create_stellar_client,
        dependencies=['config'],
        config={'network': 'mainnet'}
    )
    logger.info("✓ Registered: stellar_client (depends on: config)")
    
    # ========================================================================
    # AIR PROTOCOL (UBEC - Diversity)
    # ========================================================================
    
    async def create_air(registry: ServiceRegistry):
        """
        Create Air protocol service using factory function.
        
        ENHANCED: Now properly tracks health and sync status.
        """
        from core.protocols.UBEC_protocol import create_ubec_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Air Protocol: UBEC (Diversity)")
        
        # Use factory function to create service
        service = create_ubec_service(
            db_manager=db,
            config={
                'asset_code': getattr(config, 'UBEC_CODE', 'UBEC'),
                'issuer': getattr(config, 'UBEC_ISSUER', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar
        )
        
        # Air protocol factory handles initialization internally
        return service
    
    registry.register_factory(
        'air',
        create_air,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'air', 'principle': 'diversity'}
    )
    logger.info("✓ Registered: air (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # WATER PROTOCOL (UBECrc - Reciprocity)
    # ========================================================================
    
    async def create_water(registry: ServiceRegistry):
        """
        Create Water protocol service using factory function.
        
        ENHANCED: Properly initializes and tracks sync status.
        """
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Water Protocol: UBECrc (Reciprocity)")
        
        # Use factory function to create service
        service = await create_ubecrc_service(
            db_manager=db,
            config={
                'asset_code': getattr(config, 'UBECRC_CODE', 'UBECrc'),
                'issuer': getattr(config, 'UBECRC_ISSUER', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar
        )
        
        # Water protocol requires explicit initialize() call
        await service.initialize()
        
        return service
    
    registry.register_factory(
        'water',
        create_water,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'water', 'principle': 'reciprocity'}
    )
    logger.info("✓ Registered: water (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # EARTH PROTOCOL (UBECgpi - Mutualism)
    # ========================================================================
    
    async def create_earth(registry: ServiceRegistry):
        """
        Create Earth protocol service using factory function.
        
        ENHANCED: Properly tracks health and sync status.
        """
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Earth Protocol: UBECgpi (Mutualism)")
        
        # Use factory function to create service (NOT async)
        service = create_ubecgpi_service(
            db_manager=db,
            config={
                'asset_code': getattr(config, 'UBECGPI_CODE', 'UBECgpi'),
                'issuer': getattr(config, 'UBECGPI_ISSUER', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar
        )
        
        # Earth protocol factory handles initialization internally
        return service
    
    registry.register_factory(
        'earth',
        create_earth,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'earth', 'principle': 'mutualism'}
    )
    logger.info("✓ Registered: earth (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # FIRE PROTOCOL (UBECtt - Regeneration)
    # ========================================================================
    
    async def create_fire(registry: ServiceRegistry):
        """
        Create Fire protocol service using factory function.
        
        ENHANCED: Properly tracks health and sync status.
        """
        from core.protocols.UBECtt_protocol import create_ubectt_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Fire Protocol: UBECtt (Regeneration)")
        
        # Use factory function to create service (NOT async)
        service = create_ubectt_service(
            db_manager=db,
            config={
                'asset_code': getattr(config, 'UBECTT_CODE', 'UBECtt'),
                'issuer': getattr(config, 'UBECTT_ISSUER', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar
        )
        
        # Fire protocol factory handles initialization internally
        return service
    
    registry.register_factory(
        'fire',
        create_fire,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'fire', 'principle': 'regeneration'}
    )
    logger.info("✓ Registered: fire (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # SYNCHRONIZER SERVICE
    # ========================================================================
    
    async def create_synchronizer(registry: ServiceRegistry):
        """
        Create synchronizer service.
        
        ENHANCED: Properly tracks sync operations for health monitoring.
        """
        from core.db.ubec_data_synchronizer import create_synchronizer_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Synchronizer: Blockchain sync + liquidity pools")
        
        # Use factory function (NOT async - returns instance directly)
        synchronizer = create_synchronizer_service(
            db_manager=db,
            rate_limit_per_second=10.0
        )
        
        # Initialize the synchronizer (this IS async)
        await synchronizer.initialize()
        
        return synchronizer
    
    registry.register_factory(
        'synchronizer',
        create_synchronizer,
        dependencies=['database', 'config', 'stellar_client'],
        config={'sync_interval': 3600}
    )
    logger.info("✓ Registered: synchronizer (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # ANALYTICS SERVICE
    # ========================================================================
    
    async def create_analytics(registry: ServiceRegistry):
        """
        Create analytics service.
        
        ENHANCED: Implements proper health checking.
        """
        from services.analytics import UBECAnalyticsService
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        logger.info("  ├─ Analytics: Token distribution and metrics")
        
        # Instantiate service directly
        analytics = UBECAnalyticsService(db)
        
        # Initialize the service
        await analytics.initialize()
        
        return analytics
    
    registry.register_factory(
        'analytics',
        create_analytics,
        dependencies=['database', 'config'],
        config={'cache_ttl': 300}
    )
    logger.info("✓ Registered: analytics (depends on: database, config)")
    
    # ========================================================================
    # AUDIT SERVICE
    # ========================================================================
    
    async def create_audit(registry: ServiceRegistry):
        """
        Create audit service loading accounts from database.
        
        ENHANCED: Comprehensive error handling and health tracking.
        
        Principle #4: Database is authoritative - accounts loaded from database
        Principle #8: No Duplicate Configuration - uses centralized config
        """
        from services.audit.ubec_audit_service import create_audit_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        logger.info("  ├─ Audit: Compliance & auditing")
        
        # Load account addresses from database via config.ACCOUNTS property
        accounts = config.ACCOUNTS
        
        if not accounts.get('administration'):
            logger.error("CRITICAL: administration account not found in database")
            logger.error("Please add to settings: INSERT INTO settings (key, value) "
                        "VALUES ('administration_account', 'GXXX...')")
            raise ValueError("administration_account not configured in database")
        
        if not accounts.get('stewardship'):
            logger.error("CRITICAL: stewardship account not found in database")
            logger.error("Please add to settings: INSERT INTO settings (key, value) "
                        "VALUES ('stewardship_account', 'GXXX...')")
            raise ValueError("stewardship_account not configured in database")
        
        # Build audit config with database-loaded accounts
        audit_config = {
            'ubec_code': getattr(config, 'UBEC_CODE', 'UBEC'),
            'ubec_issuer': getattr(config, 'UBEC_ISSUER', ''),
            'administration_account': accounts['administration'],
            'stewardship_account': (accounts['stewardship'] 
                                   if isinstance(accounts['stewardship'], str) 
                                   else accounts['stewardship'][0]),
            'tokenomics': {
                'administration_target': float(getattr(config, 'ADMINISTRATION_TARGET', 0.05)),
                'stewardship_target': float(getattr(config, 'STEWARDSHIP_TARGET', 0.30)),
                'compliance_threshold': float(getattr(config, 'COMPLIANCE_THRESHOLD', 0.02))
            }
        }
        
        logger.info(f"    ✓ Loaded administration account: {accounts['administration'][:8]}...")
        logger.info(f"    ✓ Loaded stewardship account: "
                   f"{audit_config['stewardship_account'][:8]}...")
        logger.info(f"    ✓ Tokenomics targets: "
                   f"Admin={audit_config['tokenomics']['administration_target']:.1%}, "
                   f"Steward={audit_config['tokenomics']['stewardship_target']:.1%}")
        
        # Use factory function
        return await create_audit_service(
            db_manager=db,
            config=audit_config,
            holonic_evaluator=None  # Optional evaluator
        )
    
    registry.register_factory(
        'audit',
        create_audit,
        dependencies=['database', 'config'],
        config={'snapshot_interval': 86400}
    )
    logger.info("✓ Registered: audit (depends on: database, config)")
    
    # ========================================================================
    # DISTRIBUTION SERVICE
    # ========================================================================
    
    async def create_distribution(registry: ServiceRegistry):
        """
        Create distribution service.
        
        ENHANCED: Proper health monitoring implementation.
        """
        from services.distribution.distribution_service import create_distribution_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        audit = await registry.get('audit')
        
        logger.info("  ├─ Distribution: Token balance management")
        
        return await create_distribution_service(
            db_manager=db,
            config={
                'ubec_code': getattr(config, 'UBEC_CODE', 'UBEC'),
                'ubec_issuer': getattr(config, 'UBEC_ISSUER', ''),
                'ubecrc_code': getattr(config, 'UBECRC_CODE', 'UBECrc'),
                'ubecrc_issuer': getattr(config, 'UBECRC_ISSUER', ''),
                'ubecgpi_code': getattr(config, 'UBECGPI_CODE', 'UBECgpi'),
                'ubecgpi_issuer': getattr(config, 'UBECGPI_ISSUER', ''),
                'ubectt_code': getattr(config, 'UBECTT_CODE', 'UBECtt'),
                'ubectt_issuer': getattr(config, 'UBECTT_ISSUER', '')
            },
            stellar_client=stellar,
            audit_service=audit
        )
    
    registry.register_factory(
        'distribution',
        create_distribution,
        dependencies=['database', 'config', 'stellar_client', 'audit'],
        config={'distribution_interval': 86400}
    )
    logger.info("✓ Registered: distribution (depends on: database, config, stellar_client, audit)")
    
    # ========================================================================
    # DISTRIBUTION EVALUATOR
    # ========================================================================
    
    async def create_distribution_evaluator(registry: ServiceRegistry):
        """
        Create distribution evaluator service.
        
        ENHANCED: Implements comprehensive health checking.
        """
        from core.evaluation.distribution_evaluator import create_evaluator_service as factory
        
        db = await registry.get('database')
        distribution = await registry.get('distribution')
        audit = await registry.get('audit')
        
        logger.info("  ├─ Distribution Evaluator: Compliance checking")
        
        return await factory(
            distribution_service=distribution,
            audit_service=audit,
            db_manager=db
        )
    
    registry.register_factory(
        'distribution_evaluator',
        create_distribution_evaluator,
        dependencies=['database', 'distribution', 'audit'],
        config={'evaluation_interval': 3600}
    )
    logger.info("✓ Registered: distribution_evaluator (depends on: database, distribution, audit)")
    
    # ========================================================================
    # HOLONIC EVALUATOR
    # ========================================================================
    
    async def create_holonic_evaluator(registry: ServiceRegistry):
        """
        Create holonic evaluator service.
        
        ENHANCED: Proper health check implementation.
        """
        from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator as factory
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        primary_schema = getattr(db, 'primary_schema', 'ubec_main')
        
        logger.info("  ├─ Holonic Evaluator: Ubuntu principles")
        
        evaluator_config = {
            'db_schema': primary_schema,
            'ubec_code': getattr(config, 'UBEC_CODE', 'UBEC'),
            'ubec_issuer': getattr(config, 'UBEC_ISSUER', '')
        }
        
        return await factory(db_manager=db, config=evaluator_config)
    
    registry.register_factory(
        'holonic_evaluator',
        create_holonic_evaluator,
        dependencies=['database', 'config'],
        config={'evaluation_interval': 3600}
    )
    logger.info("✓ Registered: holonic_evaluator (depends on: database, config)")
    
    # ========================================================================
    # VISUALIZER SERVICE
    # ========================================================================
    
    async def create_visualizer(registry: ServiceRegistry):
        """
        Create visualization service.
        
        ENHANCED: Implements health checking.
        """
        from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer as factory
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        primary_schema = getattr(db, 'primary_schema', 'ubec_main')
        
        logger.info("  ├─ Visualizer: Charts & reports")
        
        visualizer_config = {
            'db_schema': primary_schema,
            'element_mode': 'all'
        }
        
        # Factory function already calls initialize()
        return await factory(db_manager=db, config=visualizer_config)
    
    registry.register_factory(
        'visualizer',
        create_visualizer,
        dependencies=['database', 'config'],
        config={'output_dir': 'visualizations'}
    )
    logger.info("✓ Registered: visualizer (depends on: database, config)")
    
    logger.info("=" * 70)
    logger.info("✓ ALL SERVICES REGISTERED")
    logger.info("=" * 70)


def validate_service_registration():
    """
    Validate that all required services are registered.
    
    Principle #3: Service Registry validation
    """
    required_services = [
        'database', 'config', 'stellar_client',
        'air', 'water', 'earth', 'fire',
        'synchronizer', 'analytics', 'distribution',
        'distribution_evaluator', 'holonic_evaluator',
        'visualizer', 'audit'
    ]
    
    # Check if service is registered (either as instance or factory)
    missing = []
    for name in required_services:
        if name not in registry._services and name not in registry._factories:
            missing.append(name)
    
    if missing:
        raise RuntimeError(f"Missing required services: {', '.join(missing)}")
    
    logger.info(f"✓ All {len(required_services)} required services registered")


# ========================================================================
# OPERATION HANDLERS
# Principle #10: Separation of Concerns - Each operation isolated
# ========================================================================

async def run_health_check() -> Dict[str, Any]:
    """
    Run comprehensive system health check using ServiceHealthCheck utility.
    
    ENHANCED: Standardized health monitoring across all services.
    
    Principle #7: Per-Asset Monitoring
    Principle #12: Method Singularity - Uses ServiceHealthCheck utility
    
    Returns:
        Comprehensive health report with per-service details and categorization
    """
    logger.info("\n" + "=" * 70)
    logger.info("RUNNING COMPREHENSIVE SYSTEM HEALTH CHECK")
    logger.info("=" * 70)
    
    try:
        from core.utils.service_health import ServiceHealthCheck, HealthStatus
        
        health_results = {
            'system': {
                'status': 'unknown',
                'timestamp': datetime.now().isoformat(),
                'version': '12.5.0',
                'services_checked': 0,
                'services_healthy': 0,
                'services_degraded': 0,
                'services_unhealthy': 0,
                'services_unknown': 0
            },
            'categories': {
                'core': {'services': [], 'status': 'unknown'},
                'protocols': {'services': [], 'status': 'unknown'},
                'services': {'services': [], 'status': 'unknown'},
                'utilities': {'services': [], 'status': 'unknown'}
            },
            'services': {}
        }
        
        # Categorize services for better organization
        service_categories = {
            'core': ['database', 'config', 'stellar_client'],
            'protocols': ['air', 'water', 'earth', 'fire'],
            'services': ['synchronizer', 'analytics', 'distribution', 'audit'],
            'utilities': ['distribution_evaluator', 'holonic_evaluator', 'visualizer']
        }
        
        # Flatten all services
        all_services = []
        for category_services in service_categories.values():
            all_services.extend(category_services)
        
        logger.info(f"\nChecking {len(all_services)} services across 4 categories...")
        
        # Check each service
        for service_name in all_services:
            try:
                logger.info(f"\n  → Checking {service_name}...")
                
                service = await registry.get(service_name)
                health_results['system']['services_checked'] += 1
                
                # Use ServiceHealthCheck utility if service has health_check method
                if hasattr(service, 'health_check'):
                    # Call health check method
                    service_health = await service.health_check()
                    health_results['services'][service_name] = service_health
                    
                    # Count status
                    status = service_health.get('status', 'unknown')
                    
                    if status == 'healthy':
                        health_results['system']['services_healthy'] += 1
                        logger.info(f"    ✓ {service_name}: HEALTHY")
                    elif status == 'degraded':
                        health_results['system']['services_degraded'] += 1
                        logger.info(f"    ⚠ {service_name}: DEGRADED - "
                                  f"{service_health.get('message', 'No details')}")
                    elif status == 'unhealthy':
                        health_results['system']['services_unhealthy'] += 1
                        logger.info(f"    ✗ {service_name}: UNHEALTHY - "
                                  f"{service_health.get('message', 'No details')}")
                    else:
                        health_results['system']['services_unknown'] += 1
                        logger.info(f"    ? {service_name}: {status.upper()}")
                    
                    # Add to category
                    for category, services in service_categories.items():
                        if service_name in services:
                            health_results['categories'][category]['services'].append({
                                'name': service_name,
                                'status': status
                            })
                else:
                    # Service doesn't have health_check method
                    # Create basic health check using ServiceHealthCheck
                    health_check = ServiceHealthCheck(service_name)
                    
                    # Mark as healthy if service initialized successfully
                    health_check.mark_healthy("Service initialized successfully")
                    service_health = health_check.to_dict()
                    
                    health_results['services'][service_name] = service_health
                    health_results['system']['services_healthy'] += 1
                    logger.info(f"    ✓ {service_name}: HEALTHY (basic check)")
                    
                    # Add to category
                    for category, services in service_categories.items():
                        if service_name in services:
                            health_results['categories'][category]['services'].append({
                                'name': service_name,
                                'status': 'healthy'
                            })
                    
            except Exception as e:
                logger.error(f"    ✗ {service_name}: ERROR - {str(e)}")
                health_results['services'][service_name] = {
                    'status': 'unhealthy',
                    'message': f'Health check failed: {str(e)}',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
                health_results['system']['services_unhealthy'] += 1
                
                # Add to category
                for category, services in service_categories.items():
                    if service_name in services:
                        health_results['categories'][category]['services'].append({
                            'name': service_name,
                            'status': 'unhealthy'
                        })
        
        # Determine category statuses
        for category_name, category_data in health_results['categories'].items():
            category_services = category_data['services']
            if not category_services:
                category_data['status'] = 'unknown'
                continue
            
            statuses = [s['status'] for s in category_services]
            if all(s == 'healthy' for s in statuses):
                category_data['status'] = 'healthy'
            elif any(s == 'unhealthy' for s in statuses):
                category_data['status'] = 'unhealthy'
            elif any(s == 'degraded' for s in statuses):
                category_data['status'] = 'degraded'
            else:
                category_data['status'] = 'unknown'
        
        # Determine overall system status
        total = health_results['system']['services_checked']
        healthy = health_results['system']['services_healthy']
        degraded = health_results['system']['services_degraded']
        unhealthy = health_results['system']['services_unhealthy']
        unknown = health_results['system']['services_unknown']
        
        if unhealthy > 0:
            health_results['system']['status'] = 'unhealthy'
        elif degraded > 0:
            health_results['system']['status'] = 'degraded'
        elif healthy == total:
            health_results['system']['status'] = 'healthy'
        else:
            health_results['system']['status'] = 'partial'
        
        logger.info("\n" + "=" * 70)
        logger.info("HEALTH CHECK SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Overall Status: {health_results['system']['status'].upper()}")
        logger.info(f"Services Checked: {total}")
        logger.info(f"  ✓ Healthy: {healthy}")
        logger.info(f"  ⚠ Degraded: {degraded}")
        logger.info(f"  ✗ Unhealthy: {unhealthy}")
        logger.info(f"  ? Unknown: {unknown}")
        logger.info("\nCategory Status:")
        for category_name, category_data in health_results['categories'].items():
            logger.info(f"  {category_name.capitalize()}: {category_data['status'].upper()}")
        logger.info("=" * 70)
        
        return create_response(True, data=health_results)
        
    except Exception as e:
        logger.error(f"\n✗ Health check failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_status() -> Dict[str, Any]:
    """
    Get system status summary with comprehensive health information.
    
    ENHANCED: Now uses health_check methods for consistent status reporting.
    
    Principle #5: Async operations
    Principle #12: Method Singularity
    """
    logger.info("\nGathering system status...")
    
    try:
        status = {
            'database': {},
            'synchronizer': {},
            'protocols': {},
            'services': {}
        }
        
        # Database status
        db = await registry.get('database')
        if hasattr(db, 'pool'):
            status['database'] = {
                'connected': True,
                'schema': getattr(db, 'primary_schema', 'unknown')
            }
        
        # Synchronizer status
        sync = await registry.get('synchronizer')
        if hasattr(sync, 'get_sync_status'):
            status['synchronizer'] = await sync.get_sync_status()
        elif hasattr(sync, 'health_check'):
            health = await sync.health_check()
            status['synchronizer'] = {
                'status': health.get('status', 'unknown'),
                'message': health.get('message', '')
            }
        
        # Protocol status using health checks
        for protocol_name in ['air', 'water', 'earth', 'fire']:
            try:
                protocol = await registry.get(protocol_name)
                if hasattr(protocol, 'health_check'):
                    health = await protocol.health_check()
                    status['protocols'][protocol_name] = {
                        'status': health.get('status', 'unknown'),
                        'element': health.get('details', {}).get('element', 'unknown'),
                        'principle': health.get('details', {}).get('ubuntu_principle', 'unknown')
                    }
                elif hasattr(protocol, 'get_status'):
                    status['protocols'][protocol_name] = await protocol.get_status()
            except Exception as e:
                status['protocols'][protocol_name] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        # Other services using health checks
        for service_name in ['analytics', 'distribution', 'holonic_evaluator', 'visualizer']:
            try:
                service = await registry.get(service_name)
                if hasattr(service, 'health_check'):
                    health = await service.health_check()
                    status['services'][service_name] = {
                        'status': health.get('status', 'unknown')
                    }
                elif hasattr(service, 'get_status'):
                    status['services'][service_name] = await service.get_status()
            except Exception as e:
                status['services'][service_name] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        return create_response(True, data=status)
        
    except Exception as e:
        logger.error(f"✗ Status check failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_sync(
    sync_type: str = 'all',
    max_accounts: Optional[int] = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Run data synchronization operations.
    
    Args:
        sync_type: Type of sync ('all', 'accounts', 'lp_only', 'balances')
        max_accounts: Maximum accounts to process
        force: Force resync even if recent data exists
        
    Principle #5: Async operations
    """
    logger.info(f"\nRunning synchronization: type={sync_type}, "
               f"max_accounts={max_accounts}, force={force}")
    
    try:
        sync = await registry.get('synchronizer')
        
        if sync_type == 'all':
            result = await sync.sync_all_data(max_accounts=max_accounts, force_resync=force)
        elif sync_type == 'accounts':
            result = await sync.sync_account_discovery(max_accounts=max_accounts)
        elif sync_type == 'lp_only':
            result = await sync.sync_liquidity_pools_only()
        elif sync_type == 'balances':
            result = await sync.sync_token_balances(max_accounts=max_accounts)
        else:
            return create_response(False, error=f"Unknown sync type: {sync_type}")
        
        logger.info("✓ Synchronization completed successfully")
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"✗ Synchronization failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_discover(max_accounts: int = 100) -> Dict[str, Any]:
    """
    Run account discovery operation.
    
    Args:
        max_accounts: Maximum accounts to discover
        
    Principle #5: Async operations
    """
    logger.info(f"\nRunning account discovery: max_accounts={max_accounts}")
    
    try:
        sync = await registry.get('synchronizer')
        result = await sync.sync_account_discovery(max_accounts=max_accounts)
        
        logger.info("✓ Account discovery completed successfully")
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"✗ Account discovery failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_analytics(analysis_type: str = 'summary') -> Dict[str, Any]:
    """
    Run analytics operations.
    
    Args:
        analysis_type: Type of analysis ('summary', 'distribution', 'holders')
        
    Principle #5: Async operations
    """
    logger.info(f"\nRunning analytics: type={analysis_type}")
    
    try:
        analytics = await registry.get('analytics')
        
        if analysis_type == 'summary':
            result = await analytics.get_token_summary()
        elif analysis_type == 'distribution':
            result = await analytics.get_distribution_analysis()
        elif analysis_type == 'holders':
            result = await analytics.get_top_holders()
        else:
            return create_response(False, error=f"Unknown analysis type: {analysis_type}")
        
        logger.info("✓ Analytics completed successfully")
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"✗ Analytics failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_distribution(
    action: Optional[str] = None,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Run distribution operations.
    
    Args:
        action: Specific action (check-compliance, audit, etc.)
        dry_run: Simulate without making changes
        
    Principle #5: Async operations
    """
    logger.info(f"\nRunning distribution operation: {action or 'default'} (dry_run={dry_run})")
    
    try:
        audit = await registry.get('audit')
        
        if action == 'check-compliance' or action is None:
            if hasattr(audit, 'check_distribution_compliance'):
                result = await audit.check_distribution_compliance()
            else:
                return create_response(False, 
                                     error="check_distribution_compliance method not available")
        elif action == 'audit':
            if hasattr(audit, 'run_comprehensive_audit'):
                result = await audit.run_comprehensive_audit()
            else:
                return create_response(False, 
                                     error="run_comprehensive_audit method not available")
        else:
            return create_response(False, error=f"Unknown action: {action}")
        
        logger.info("✓ Distribution operation completed successfully")
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"✗ Distribution operation failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_visualize(
    action: str,
    chart_type: Optional[str] = None,
    format: str = 'png',
    output_dir: str = 'visualizations',
    include_advanced: bool = False
) -> Dict[str, Any]:
    """
    Run visualization operations.
    
    Args:
        action: Visualization action (chart, report, all)
        chart_type: Type of chart to generate
        format: Output format (png, svg, html, json)
        output_dir: Output directory
        include_advanced: Include advanced analytics
        
    Principle #5: Async operations
    """
    logger.info(f"\nRunning visualization: action={action}, chart_type={chart_type}")
    
    try:
        visualizer = await registry.get('visualizer')
        
        if action == 'chart' and chart_type:
            result = await visualizer.generate_chart(
                chart_type=chart_type,
                format=format,
                output_dir=output_dir
            )
        elif action == 'report':
            result = await visualizer.generate_report(
                output_dir=output_dir,
                format=format,
                include_advanced=include_advanced
            )
        elif action == 'all':
            result = await visualizer.generate_all(
                output_dir=output_dir,
                format=format
            )
        else:
            return create_response(False, error=f"Unknown visualization action: {action}")
        
        logger.info("✓ Visualization completed successfully")
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"✗ Visualization failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_protocol_health() -> Dict[str, Any]:
    """
    Check health of all protocol services using ServiceHealthCheck utility.
    
    ENHANCED: Comprehensive protocol health monitoring.
    
    Principle #5: Async operations
    Principle #7: Per-Asset Monitoring
    Principle #12: Method Singularity - Uses standardized health checks
    """
    logger.info("\nChecking protocol health...")
    
    try:
        from core.utils.service_health import ServiceHealthCheck
        
        protocol_health = {}
        
        for protocol_name in ['air', 'water', 'earth', 'fire']:
            protocol = await registry.get(protocol_name)
            
            # Use health_check method if available
            if hasattr(protocol, 'health_check'):
                health = await protocol.health_check()
            else:
                # Create basic health check
                health_check = ServiceHealthCheck(protocol_name)
                health_check.mark_healthy("Protocol initialized successfully")
                health = health_check.to_dict()
            
            protocol_health[protocol_name] = health
            
            # Log protocol status
            status = health.get('status', 'unknown')
            element = health.get('details', {}).get('element', 'unknown')
            principle = health.get('details', {}).get('ubuntu_principle', 'unknown')
            
            logger.info(f"  {protocol_name.upper()}: {status} - {element} ({principle})")
        
        logger.info("✓ Protocol health check completed")
        return create_response(True, data=protocol_health)
        
    except Exception as e:
        logger.error(f"✗ Protocol health check failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


# ========================================================================
# ARGUMENT PARSING
# ========================================================================

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='UBEC Protocol System - Unified Entry Point',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Operation mode
    parser.add_argument(
        '--mode',
        required=True,
        choices=[
            'health', 'status', 'sync', 'discover', 'analytics',
            'distribution', 'visualize', 'protocol-health'
        ],
        help='Operation mode'
    )
    
    # Sync options
    parser.add_argument(
        '--sync-type',
        default='all',
        choices=['all', 'accounts', 'lp_only', 'balances'],
        help='Type of synchronization'
    )
    
    parser.add_argument(
        '--max-accounts',
        type=int,
        help='Maximum accounts to process'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force operation even if recent data exists'
    )
    
    # Analytics options
    parser.add_argument(
        '--analysis-type',
        default='summary',
        choices=['summary', 'distribution', 'holders'],
        help='Type of analysis'
    )
    
    # Distribution options
    parser.add_argument(
        '--action',
        help='Specific action to perform'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without making changes'
    )
    
    # Visualization options
    parser.add_argument(
        '--chart-type',
        choices=[
            'score_dist', 'category_dist', 'radar',
            'correlation', 'time_series', 'comparative', 'network'
        ],
        help='Type of chart to generate'
    )
    
    parser.add_argument(
        '--format',
        default='png',
        choices=['png', 'svg', 'html', 'json'],
        help='Output format'
    )
    
    parser.add_argument(
        '--output-dir',
        default='visualizations',
        help='Output directory for files'
    )
    
    parser.add_argument(
        '--include-advanced',
        action='store_true',
        help='Include advanced analytics'
    )
    
    # Logging
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    return parser.parse_args()


# ========================================================================
# MAIN ASYNC ORCHESTRATION
# ========================================================================

async def main_async(args):
    """
    Main async orchestration function.
    
    Principle #2: This is the ONLY execution entry point.
    Principle #5: Pure async throughout.
    
    Args:
        args: Parsed command-line arguments
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger.info("\n" + "=" * 70)
    logger.info("UBEC PROTOCOL SYSTEM STARTING")
    logger.info("=" * 70)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Version: 12.5.0 (Comprehensive Health Monitoring)")
    logger.info("=" * 70)
    
    try:
        # Step 1: Register all services
        register_core_services()
        
        # Step 2: Validate registration
        validate_service_registration()
        
        logger.info("\n" + "=" * 70)
        logger.info("SERVICE REGISTRY VALIDATED - READY TO EXECUTE")
        logger.info("=" * 70)
        
        # Step 3: Execute operation using context manager
        async with registry:
            logger.info("\n✓ Service registry context entered - services will auto-initialize")
            
            # Route to appropriate handler
            result = None
            
            # System Operations
            if args.mode == 'health':
                result = await run_health_check()
            
            elif args.mode == 'status':
                result = await run_status()
            
            elif args.mode == 'protocol-health':
                result = await run_protocol_health()
            
            # Data Layer
            elif args.mode == 'sync':
                result = await run_sync(
                    sync_type=args.sync_type,
                    max_accounts=args.max_accounts,
                    force=args.force
                )
            
            elif args.mode == 'discover':
                result = await run_discover(
                    max_accounts=args.max_accounts or 100
                )
            
            # Analytics
            elif args.mode == 'analytics':
                result = await run_analytics(
                    analysis_type=args.analysis_type
                )
            
            # Distribution
            elif args.mode == 'distribution':
                result = await run_distribution(
                    action=args.action,
                    dry_run=args.dry_run
                )
            
            # Visualization
            elif args.mode == 'visualize':
                result = await run_visualize(
                    action=args.action or 'report',
                    chart_type=args.chart_type,
                    format=args.format,
                    output_dir=args.output_dir,
                    include_advanced=args.include_advanced
                )
            
            # Print result
            if result:
                import json
                logger.info("\n" + "=" * 70)
                logger.info(f"UBEC Protocol - {args.mode.upper()} Result")
                logger.info("=" * 70)
                print(json.dumps(result, indent=2, default=str))
            
            logger.info("\n" + "=" * 70)
            logger.info("✓ OPERATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            
            return 0
            
    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error("✗ FATAL ERROR: Operation failed")
        logger.error("=" * 70)
        logger.error(f"Error: {e}", exc_info=True)
        return 1


# ========================================================================
# ENTRY POINT
# Principle #2: This is the ONLY standalone execution in the entire system
# ========================================================================

def main():
    """
    Main entry point.
    
    Principle #2: This is the ONLY standalone execution in the entire system.
    All other modules use the service pattern and must be orchestrated through here.
    """
    args = parse_arguments()
    
    # Set log level
    setup_logging(args.log_level)
    
    # Run async main
    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
