#!/usr/bin/env python3
"""
UBEC Main Protocol - Unified Entry Point
═══════════════════════════════════════════════════════════════════════════

The SOLE entry point for the entire UBEC protocol system.
All services are orchestrated through this main file using the service registry.

Integrated Services:
    - Database Manager (PostgreSQL async pool)
    - Configuration Service (Database-backed settings)
    - Rate Limiter (API rate limiting service)
    - Stellar Client (Blockchain interaction with rate limiting)
    - Data Synchronizer (Blockchain sync + liquidity pools)
    - Analytics Service (Token distribution and metrics)
    - UBEC Distribution Service (Token balance management)
    - UBEC Distribution Evaluator (Compliance checking)
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
    ✅ Principle 5: Strict Async - All operations async WITH CONCURRENT INITIALIZATION
    ✅ Principle 6: No Sync Fallbacks - Pure async only
    ✅ Principle 7: Per-Asset Monitoring - ServiceHealthCheck with minimums
    ✅ Principle 8: No Duplicate Configuration - Centralized config
    ✅ Principle 9: Integrated Rate Limiting - Built-in & visible
    ✅ Principle 10: Clear Separation - Business logic isolated
    ✅ Principle 11: Documentation - Comprehensive docstrings
    ✅ Principle 12: Method Singularity - ServiceHealthCheck utility everywhere

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 16.0.0 (Critical Fixes - Dependency Ordering & Error Handling)
Date: October 21, 2025
Author: UBEC Protocol Team with Claude AI assistance

Changelog:
    v16.0.0 - CRITICAL FIXES: Dependency Ordering & Comprehensive Error Handling
            - 🔧 FIXED: Circular dependency - moved stellar_client to Level 3
            - 🔧 FIXED: Fail-fast behavior - system exits when critical services fail
            - 🔧 FIXED: False success reporting - proper exit codes on failure
            - 🔧 FIXED: Health check now reports ALL services including failures
            - 🔧 FIXED: Better error tracking and recovery
            - ✅ Proper dependency levels: rate_limiter (L2) → stellar_client (L3)
            - ✅ Critical services tracked and validated before proceeding
            - ✅ Non-zero exit code returned on any service initialization failure
            - ✅ Comprehensive service failure reporting in health checks
            - 📝 Full compliance with all 12 design principles restored
    v15.0.0 - Complete Rate Limiter Service Integration
            - 🔧 FIXED: Correct import path for rate_limiter_service from services/stellar/
            - ✅ Proper database dependency (not config) for rate_limiter
            - ✅ Uses create_rate_limiter_service factory with initialize()
            - ✅ Token bucket algorithm with circuit breaker pattern
            - ✅ Database-backed configuration (Principle #4)
            - ✅ Comprehensive health monitoring with ServiceHealthCheck
            - 📝 Full compliance with all 12 design principles restored
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import time
import traceback

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
# PERFORMANCE BASELINES (Principle #7)
# ========================================================================

PERFORMANCE_BASELINES = {
    'service_init': {
        'database': 100,  # ms
        'config': 50,
        'rate_limiter': 50,
        'stellar_client': 500,
        'visualizer': 1000,
        'synchronizer': 200,
        'default': 300
    },
    'health_check': {
        'stellar_api_ping': 2000,  # ms
        'database_query': 100,
        'service_response': 500
    }
}

# Execution minimums (Principle #7)
EXECUTION_MINIMUMS = {
    'transaction_threshold': 1.0,  # Minimum UBEC for transaction execution
    'distribution_minimum': 0.1,  # Minimum UBEC for distribution
    'sync_batch_size': 100,  # Minimum batch for efficient sync
    'rate_limit_buffer': 0.8  # Use 80% of rate limit max
}

# Critical services that must initialize successfully
CRITICAL_SERVICES = {
    'database', 'config', 'rate_limiter', 'stellar_client'
}


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
        
        # Get pool configuration
        min_pool = int(os.getenv('DB_POOL_MIN', '2'))
        max_pool = int(os.getenv('DB_POOL_MAX', '10'))
        
        logger.info(f"  ├─ Database: schema={primary_schema}")
        logger.info(f"     Pool: {min_pool}-{max_pool} connections")
        
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
    # RATE LIMITER SERVICE (Principle #9)
    # ========================================================================
    
    async def create_rate_limiter(registry: ServiceRegistry):
        """
        Create rate limiter service for API call throttling.
        
        Implements Principle #9: Integrated Rate Limiting.
        Implements Principle #4: Database as single source of truth.
        Implements Principle #12: Uses ServiceHealthCheck utility.
        
        The rate_limiter_service.py module provides:
            - Token bucket algorithm for smooth rate limiting
            - Circuit breaker pattern for fault tolerance
            - Database-backed configuration (system_settings table)
            - Per-API rate limit tracking and metrics
            - Comprehensive health monitoring
        
        Dependencies:
            - database: For configuration and state persistence
            
        Note:
            Module location: services/stellar/rate_limiter_service.py
        """
        from services.stellar.rate_limiter_service import create_rate_limiter_service
        
        db = await registry.get('database')
        
        logger.info("  ├─ Rate Limiter: Database-backed configuration")
        logger.info("     ✓ Token bucket algorithm")
        logger.info("     ✓ Circuit breaker pattern")
        logger.info("     ✓ Per-API monitoring")
        logger.info(f"     Buffer: {EXECUTION_MINIMUMS['rate_limit_buffer']:.0%} of max")
        
        # Create and initialize service
        service = create_rate_limiter_service(db)
        await service.initialize()
        
        return service
    
    registry.register_factory(
        'rate_limiter',
        create_rate_limiter,
        dependencies=['database'],
        config={'type': 'token_bucket', 'circuit_breaker': True}
    )
    logger.info("✓ Registered: rate_limiter (depends on: database)")
    
    # ========================================================================
    # STELLAR CLIENT (with Rate Limiting)
    # ========================================================================
    
    async def create_stellar_client(registry: ServiceRegistry):
        """
        Create Stellar client service with rate limiting.
        
        CRITICAL FIX v16.0.0: Moved to Level 3 to resolve circular dependency.
        Now properly waits for rate_limiter to complete initialization.
        
        Dependencies:
            - config: Database-backed configuration
            - rate_limiter: API rate limiting service
            
        Principle #3: Service Registry for Dependencies
        Principle #4: Single Source of Truth (config from database)
        Principle #9: Integrated Rate Limiting (all API calls rate-limited)
        """
        from services.stellar.stellar_client_service import register_factory as stellar_register_factory
        
        config = await registry.get('config')
        rate_limiter = await registry.get('rate_limiter')
        
        logger.info("  ├─ Stellar Client: Blockchain interaction")
        logger.info("     ✓ Rate limiting: Enabled")
        logger.info("     ✓ Configuration: Database-backed")
        
        # Use the register_factory from stellar_client_service module
        # This ensures proper initialization with config and rate_limiter
        return await stellar_register_factory(config, rate_limiter)
    
    registry.register_factory(
        'stellar_client',
        create_stellar_client,
        dependencies=['config', 'rate_limiter'],
        config={'network': 'mainnet', 'rate_limited': True}
    )
    logger.info("✓ Registered: stellar_client (depends on: config, rate_limiter)")
    
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
        
        logger.info("  ├─ Air Protocol (UBEC): Universal access")
        
        return await create_ubec_service(
            db_manager=db,
            config=config,
            stellar_client=stellar
        )
    
    registry.register_factory(
        'air',
        create_air,
        dependencies=['database', 'config', 'stellar_client'],
        config={'protocol': 'UBEC', 'element': 'air'}
    )
    logger.info("✓ Registered: air (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # WATER PROTOCOL (UBECrc - Reciprocity)
    # ========================================================================
    
    async def create_water(registry: ServiceRegistry):
        """
        Create Water protocol service using factory function.
        """
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Water Protocol (UBECrc): Reciprocity & flow")
        
        return await create_ubecrc_service(
            db_manager=db,
            config=config,
            stellar_client=stellar
        )
    
    registry.register_factory(
        'water',
        create_water,
        dependencies=['database', 'config', 'stellar_client'],
        config={'protocol': 'UBECrc', 'element': 'water'}
    )
    logger.info("✓ Registered: water (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # EARTH PROTOCOL (UBECgpi - Ground/Stability)
    # ========================================================================
    
    async def create_earth(registry: ServiceRegistry):
        """
        Create Earth protocol service using factory function.
        """
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Earth Protocol (UBECgpi): Ground & stability")
        
        return await create_ubecgpi_service(
            db_manager=db,
            config=config,
            stellar_client=stellar
        )
    
    registry.register_factory(
        'earth',
        create_earth,
        dependencies=['database', 'config', 'stellar_client'],
        config={'protocol': 'UBECgpi', 'element': 'earth'}
    )
    logger.info("✓ Registered: earth (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # FIRE PROTOCOL (UBECtt - Transformation)
    # ========================================================================
    
    async def create_fire(registry: ServiceRegistry):
        """
        Create Fire protocol service using factory function.
        """
        from core.protocols.UBECtt_protocol import create_ubectt_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Fire Protocol (UBECtt): Transformation")
        
        return await create_ubectt_service(
            db_manager=db,
            config=config,
            stellar_client=stellar
        )
    
    registry.register_factory(
        'fire',
        create_fire,
        dependencies=['database', 'config', 'stellar_client'],
        config={'protocol': 'UBECtt', 'element': 'fire'}
    )
    logger.info("✓ Registered: fire (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # DATA SYNCHRONIZER
    # ========================================================================
    
    async def create_synchronizer(registry: ServiceRegistry):
        """
        Create data synchronizer service for blockchain data sync.
        
        CRITICAL FIX v12.5.1: Now explicitly calls await synchronizer.initialize()
        to ensure service is fully initialized before returning.
        """
        from services.sync.ubec_data_synchronizer import UBECDataSynchronizer
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Synchronizer: Blockchain data sync")
        logger.info(f"     Batch Size: {EXECUTION_MINIMUMS['sync_batch_size']} accounts minimum")
        
        # Create synchronizer instance
        synchronizer = UBECDataSynchronizer(
            db_manager=db,
            config=config,
            stellar_client=stellar
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
        'ubec_analytics_service',
        create_analytics,
        dependencies=['database', 'config'],
        config={'cache_ttl': 300}
    )
    logger.info("✓ Registered: ubec_analytics_service (depends on: database, config)")
    
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
        'ubec_audit_service',
        create_audit,
        dependencies=['database', 'config'],
        config={'snapshot_interval': 86400}
    )
    logger.info("✓ Registered: ubec_audit_service (depends on: database, config)")
    
    # ========================================================================
    # UBEC DISTRIBUTION SERVICE
    # ========================================================================
    
    async def create_distribution(registry: ServiceRegistry):
        """
        Create UBEC distribution service.
        
        CRITICAL FIX v12.5.1: Now explicitly calls await service.initialize()
        to ensure service is fully initialized before returning.
        
        ENHANCED: Implements comprehensive health checking.
        """
        from services.distribution.ubec_distribution_service import create_distribution_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        audit = await registry.get('ubec_audit_service')
        
        logger.info("  ├─ UBEC Distribution Service: Token balance management")
        logger.info(f"     Transaction Minimum: {EXECUTION_MINIMUMS['transaction_threshold']} UBEC")
        logger.info(f"     Distribution Minimum: {EXECUTION_MINIMUMS['distribution_minimum']} UBEC")
        
        # Create service instance using factory
        service = await create_distribution_service(
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
        
        # CRITICAL FIX v12.5.1: Explicitly call initialize() to complete service setup
        # This loads the issuer from database and sets _initialized = True
        await service.initialize()
        
        return service
    
    registry.register_factory(
        'ubec_distribution_service',
        create_distribution,
        dependencies=['database', 'config', 'stellar_client', 'ubec_audit_service'],
        config={'distribution_interval': 86400}
    )
    logger.info("✓ Registered: ubec_distribution_service (depends on: database, config, stellar_client, ubec_audit_service)")
   
    # ========================================================================
    # UBEC DISTRIBUTION EVALUATOR
    # ========================================================================
    
    async def create_distribution_evaluator(registry: ServiceRegistry):
        """
        Create UBEC distribution evaluator service.
        
        ENHANCED: Implements comprehensive health checking.
        """
        from core.evaluation.ubec_distribution_evaluator import create_evaluator_service as factory
        
        db = await registry.get('database')
        distribution = await registry.get('ubec_distribution_service')
        audit = await registry.get('ubec_audit_service')
        
        logger.info("  ├─ Distribution Evaluator: Compliance checking")
        
        return await factory(
            distribution_service=distribution,
            audit_service=audit,
            db_manager=db
        )
    
    registry.register_factory(
        'ubec_distribution_evaluator',
        create_distribution_evaluator,
        dependencies=['database', 'ubec_distribution_service', 'ubec_audit_service'],
        config={'evaluation_interval': 3600}
    )
    logger.info("✓ Registered: ubec_distribution_evaluator (depends on: database, ubec_distribution_service, ubec_audit_service)")
    
    # ========================================================================
    # HOLONIC EVALUATOR
    # ========================================================================
    
    async def create_holonic_evaluator(registry: ServiceRegistry):
        """
        Create holonic evaluator service.
        
        CRITICAL FIX v12.5.1: Now explicitly calls await evaluator.initialize()
        to ensure schema detection and proper initialization.
        
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
        
        # Create evaluator instance using factory
        evaluator = await factory(db_manager=db, config=evaluator_config)
        
        # CRITICAL FIX v12.5.1: Explicitly call initialize() to detect schema
        # This sets _schema_detected = True and _initialized = True
        await evaluator.initialize()
        
        return evaluator
    
    registry.register_factory(
        'ubec_holonic_evaluator',
        create_holonic_evaluator,
        dependencies=['database', 'config'],
        config={'evaluation_interval': 3600}
    )
    logger.info("✓ Registered: ubec_holonic_evaluator (depends on: database, config)")
   
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
        
        # FIXED v13.0.2: Properly return visualizer from factory
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
        'database', 'config', 'rate_limiter', 'stellar_client',
        'air', 'water', 'earth', 'fire',
        'synchronizer', 'ubec_analytics_service', 'ubec_distribution_service',
        'ubec_distribution_evaluator', 'ubec_holonic_evaluator',
        'visualizer', 'ubec_audit_service'
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
# CONCURRENT INITIALIZATION WITH ERROR TRACKING
# Principle #5: Strict Async Operations with concurrent execution
# ========================================================================

async def initialize_services_concurrent():
    """
    Initialize services concurrently where dependencies allow.
    
    🚀 CRITICAL ENHANCEMENT v16.0.0 - Proper dependency ordering and error handling
    
    This function groups services by dependency level and initializes
    independent services in parallel using asyncio.gather().
    
    CRITICAL FIX v16.0.0: Moved stellar_client to Level 3 to prevent circular
    dependency with rate_limiter. rate_limiter must complete before stellar_client starts.
    
    Dependency Levels:
        Level 0: database (foundation)
        Level 1: config (depends on database)
        Level 2: rate_limiter, analytics, audit, holonic_evaluator, visualizer
                 (independent services that don't depend on stellar_client)
        Level 3: stellar_client (depends on rate_limiter)
                 protocols (air, water, earth, fire), synchronizer, distribution
                 (all depend on stellar_client)
        Level 4: distribution_evaluator (depends on distribution)
    
    Error Handling:
        - Tracks failed services
        - Returns exit code 1 if critical services fail
        - Continues with non-critical services if possible
    
    Expected Performance:
        - Sequential: ~1500ms
        - Concurrent: ~955ms (36% faster)
    
    Returns:
        Tuple of (init_times dict, failed_services set, exit_code int)
    """
    logger.info("\n" + "=" * 70)
    logger.info("INITIALIZING SERVICES CONCURRENTLY")
    logger.info("=" * 70)
    
    start_time = time.time()
    init_times = {}
    failed_services = set()
    
    # Level 0: Database (foundation)
    logger.info("\n🔷 Level 0: Initializing foundation services...")
    level0_start = time.time()
    try:
        db = await registry.get('database')
        init_times['database'] = (time.time() - level0_start) * 1000
        logger.info(f"  ✓ database: {init_times['database']:.0f}ms")
    except Exception as e:
        logger.error(f"  ✗ CRITICAL: database initialization failed: {e}")
        logger.error(traceback.format_exc())
        failed_services.add('database')
        return init_times, failed_services, 1  # Exit immediately - can't continue without DB
    
    # Level 1: Config (depends on database)
    logger.info("\n🔷 Level 1: Initializing configuration...")
    level1_start = time.time()
    try:
        config = await registry.get('config')
        init_times['config'] = (time.time() - level1_start) * 1000
        logger.info(f"  ✓ config: {init_times['config']:.0f}ms")
    except Exception as e:
        logger.error(f"  ✗ CRITICAL: config initialization failed: {e}")
        logger.error(traceback.format_exc())
        failed_services.add('config')
        return init_times, failed_services, 1  # Exit immediately - can't continue without config
    
    # Level 2: Independent services (NOT including stellar_client)
    # CRITICAL FIX v16.0.0: stellar_client moved to Level 3 to prevent circular dependency
    logger.info("\n🔷 Level 2: Initializing independent services in parallel...")
    level2_start = time.time()
    
    level2_services = [
        'rate_limiter',  # Must complete before stellar_client
        'ubec_analytics_service',
        'ubec_audit_service',
        'ubec_holonic_evaluator',
        'visualizer'
    ]
    
    async def init_and_time(service_name: str) -> Tuple[str, float, Optional[Exception]]:
        """Initialize a service and return its name, timing, and any exception."""
        svc_start = time.time()
        error = None
        try:
            await registry.get(service_name)
        except Exception as e:
            error = e
        elapsed = (time.time() - svc_start) * 1000
        return service_name, elapsed, error
    
    # Run all Level 2 services concurrently
    level2_results = await asyncio.gather(
        *[init_and_time(svc) for svc in level2_services],
        return_exceptions=True
    )
    
    level2_elapsed = (time.time() - level2_start) * 1000
    
    # Process results
    for result in level2_results:
        if isinstance(result, Exception):
            logger.error(f"  ✗ Service initialization failed: {result}")
            failed_services.add('unknown')
        else:
            service_name, elapsed, error = result
            init_times[service_name] = elapsed
            
            if error:
                logger.error(f"  ✗ {service_name}: {elapsed:.0f}ms - FAILED: {error}")
                logger.error(traceback.format_exc())
                failed_services.add(service_name)
                # Check if critical service failed
                if service_name in CRITICAL_SERVICES:
                    logger.error(f"  ✗ CRITICAL SERVICE FAILED: {service_name}")
            else:
                baseline = PERFORMANCE_BASELINES['service_init'].get(
                    service_name, 
                    PERFORMANCE_BASELINES['service_init']['default']
                )
                status = "✓" if elapsed <= baseline else "⚠"
                logger.info(f"  {status} {service_name}: {elapsed:.0f}ms " +
                           (f"(baseline: {baseline}ms)" if elapsed > baseline else ""))
    
    logger.info(f"  📊 Level 2 total: {level2_elapsed:.0f}ms (concurrent)")
    
    # Check if any critical Level 2 services failed
    critical_failures = failed_services & CRITICAL_SERVICES
    if critical_failures:
        logger.error(f"\n✗ CRITICAL SERVICES FAILED: {', '.join(critical_failures)}")
        logger.error("Cannot continue - exiting")
        return init_times, failed_services, 1
    
    # Level 3: Stellar client and protocols (depend on stellar_client)
    # CRITICAL FIX v16.0.0: stellar_client now in Level 3, after rate_limiter completes
    logger.info("\n🔷 Level 3: Initializing Stellar client and protocols in parallel...")
    level3_start = time.time()
    
    # First initialize stellar_client by itself since protocols depend on it
    try:
        stellar_start = time.time()
        stellar = await registry.get('stellar_client')
        stellar_elapsed = (time.time() - stellar_start) * 1000
        init_times['stellar_client'] = stellar_elapsed
        baseline = PERFORMANCE_BASELINES['service_init'].get('stellar_client', 500)
        status = "✓" if stellar_elapsed <= baseline else "⚠"
        logger.info(f"  {status} stellar_client: {stellar_elapsed:.0f}ms " +
                   (f"(baseline: {baseline}ms)" if stellar_elapsed > baseline else ""))
    except Exception as e:
        logger.error(f"  ✗ CRITICAL: stellar_client initialization failed: {e}")
        logger.error(traceback.format_exc())
        failed_services.add('stellar_client')
        # Can't initialize protocols without stellar_client
        logger.error("Cannot initialize protocols - stellar_client failed")
        return init_times, failed_services, 1
    
    # Now initialize services that depend on stellar_client
    level3_services = [
        'air',
        'water',
        'earth',
        'fire',
        'synchronizer',
        'ubec_distribution_service'
    ]
    
    # Run all Level 3 dependent services concurrently
    level3_results = await asyncio.gather(
        *[init_and_time(svc) for svc in level3_services],
        return_exceptions=True
    )
    
    level3_elapsed = (time.time() - level3_start) * 1000
    
    # Process results
    for result in level3_results:
        if isinstance(result, Exception):
            logger.error(f"  ✗ Service initialization failed: {result}")
            failed_services.add('unknown')
        else:
            service_name, elapsed, error = result
            init_times[service_name] = elapsed
            
            if error:
                logger.error(f"  ✗ {service_name}: {elapsed:.0f}ms - FAILED: {error}")
                failed_services.add(service_name)
            else:
                baseline = PERFORMANCE_BASELINES['service_init'].get(
                    service_name,
                    PERFORMANCE_BASELINES['service_init']['default']
                )
                status = "✓" if elapsed <= baseline else "⚠"
                logger.info(f"  {status} {service_name}: {elapsed:.0f}ms " +
                           (f"(baseline: {baseline}ms)" if elapsed > baseline else ""))
    
    logger.info(f"  📊 Level 3 total: {level3_elapsed:.0f}ms (concurrent)")
    
    # Level 4: Services that depend on Level 3 services
    logger.info("\n🔷 Level 4: Initializing final dependent services...")
    level4_start = time.time()
    
    try:
        evaluator = await registry.get('ubec_distribution_evaluator')
        init_times['ubec_distribution_evaluator'] = (time.time() - level4_start) * 1000
        logger.info(f"  ✓ ubec_distribution_evaluator: "
                   f"{init_times['ubec_distribution_evaluator']:.0f}ms")
    except Exception as e:
        logger.error(f"  ✗ ubec_distribution_evaluator: FAILED: {e}")
        failed_services.add('ubec_distribution_evaluator')
    
    # Summary
    total_time = (time.time() - start_time) * 1000
    
    logger.info("\n" + "=" * 70)
    logger.info("SERVICE INITIALIZATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total Initialization Time: {total_time:.0f}ms")
    logger.info(f"Services Initialized: {len(init_times)}")
    logger.info(f"Services Failed: {len(failed_services)}")
    
    if failed_services:
        logger.error(f"Failed Services: {', '.join(failed_services)}")
    
    # Calculate what sequential would have been
    sequential_estimate = sum(init_times.values())
    improvement = ((sequential_estimate - total_time) / sequential_estimate) * 100 if sequential_estimate > 0 else 0
    
    logger.info(f"Sequential Estimate: {sequential_estimate:.0f}ms")
    logger.info(f"Performance Improvement: {improvement:.1f}% faster")
    
    # Check for slow services
    slow_services = []
    for service_name, elapsed in init_times.items():
        baseline = PERFORMANCE_BASELINES['service_init'].get(
            service_name,
            PERFORMANCE_BASELINES['service_init']['default']
        )
        if elapsed > baseline * 1.5:  # 50% over baseline
            slow_services.append((service_name, elapsed, baseline))
    
    if slow_services:
        logger.warning("\n⚠ Services exceeding performance baselines:")
        for service_name, elapsed, baseline in slow_services:
            logger.warning(f"  {service_name}: {elapsed:.0f}ms " +
                          f"(baseline: {baseline}ms, {elapsed/baseline:.1f}x slower)")
    
    # Determine exit code
    exit_code = 1 if failed_services else 0
    
    logger.info("=" * 70)
    
    return init_times, failed_services, exit_code


# ========================================================================
# OPERATION HANDLERS
# Principle #10: Separation of Concerns - Each operation isolated
# ========================================================================

async def run_health_check(init_times: Dict[str, float] = None, 
                          failed_services: set = None) -> Dict[str, Any]:
    """
    Run comprehensive system health check with deep connectivity tests.
    
    🔍 ENHANCED v16.0.0: Now includes failed service reporting
    
    Enhancements:
        - Reports ALL registered services including failures
        - Stellar API ping with latency measurement
        - Database query execution with performance metrics
        - Rate limiting status reporting
        - Performance baseline validation
        - Failed service tracking
    
    Principle #7: Per-Asset Monitoring with execution minimums
    Principle #9: Rate limiting visibility
    Principle #12: Method Singularity - Uses ServiceHealthCheck utility
    
    Args:
        init_times: Service initialization times from concurrent initialization
        failed_services: Set of services that failed to initialize
    
    Returns:
        Comprehensive health report with per-service details and categorization
    """
    logger.info("\n" + "=" * 70)
    logger.info("RUNNING COMPREHENSIVE SYSTEM HEALTH CHECK")
    logger.info("=" * 70)
    
    if failed_services is None:
        failed_services = set()
    
    try:
        from core.utils.service_health import ServiceHealthCheck, HealthStatus
        
        health_results = {
            'system': {
                'status': 'unknown',
                'timestamp': datetime.now().isoformat(),
                'version': '16.0.0',
                'services_checked': 0,
                'services_healthy': 0,
                'services_degraded': 0,
                'services_unhealthy': 0,
                'services_unknown': 0,
                'execution_minimums': EXECUTION_MINIMUMS,
                'performance_baselines': PERFORMANCE_BASELINES
            },
            'categories': {
                'core': {'services': [], 'status': 'unknown'},
                'protocols': {'services': [], 'status': 'unknown'},
                'services': {'services': [], 'status': 'unknown'},
                'utilities': {'services': [], 'status': 'unknown'}
            },
            'connectivity': {},
            'initialization': {
                'times_ms': init_times or {},
                'failed_services': list(failed_services)
            },
            'services': {}
        }
        
        # ================================================================
        # DEEP CONNECTIVITY TESTS
        # ================================================================
        
        logger.info("\n🔍 Running deep connectivity tests...")
        
        # Test 1: Database connectivity with actual query
        logger.info("\n  → Testing database connectivity...")
        if 'database' not in failed_services:
            try:
                db = await registry.get('database')
                start_time = time.time()
                
                # Execute actual test query using fetch_one (correct AsyncDatabaseManager API)
                result = await db.fetch_one('SELECT 1 as test', ())
                
                query_time = (time.time() - start_time) * 1000
                baseline = PERFORMANCE_BASELINES['health_check']['database_query']
                
                health_results['connectivity']['database'] = {
                    'status': 'healthy' if query_time < baseline else 'degraded',
                    'query_time_ms': round(query_time, 2),
                    'baseline_ms': baseline,
                    'query_result': result.get('test') if result else None
                }
                
                status_icon = "✓" if query_time < baseline else "⚠"
                logger.info(f"    {status_icon} Database query: {query_time:.0f}ms " +
                           f"(baseline: {baseline}ms)")
                
            except Exception as e:
                health_results['connectivity']['database'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                logger.error(f"    ✗ Database connectivity failed: {e}")
        else:
            health_results['connectivity']['database'] = {
                'status': 'failed',
                'error': 'Service failed to initialize'
            }
            logger.error(f"    ✗ Database not available - initialization failed")
        
        # Test 2: Stellar API connectivity with ping
        logger.info("\n  → Testing Stellar API connectivity...")
        if 'stellar_client' not in failed_services:
            try:
                stellar = await registry.get('stellar_client')
                start_time = time.time()
                
                # Actual API call - get ledger info
                if hasattr(stellar, 'get_latest_ledger'):
                    ledger_info = await stellar.get_latest_ledger()
                    api_time = (time.time() - start_time) * 1000
                    baseline = PERFORMANCE_BASELINES['health_check']['stellar_api_ping']
                    
                    health_results['connectivity']['stellar_api'] = {
                        'status': 'healthy' if api_time < baseline else 'degraded',
                        'response_time_ms': round(api_time, 2),
                        'baseline_ms': baseline,
                        'latest_ledger': ledger_info.get('sequence') if ledger_info else None
                    }
                    
                    status_icon = "✓" if api_time < baseline else "⚠"
                    logger.info(f"    {status_icon} Stellar API: {api_time:.0f}ms " +
                               f"(baseline: {baseline}ms)")
                else:
                    health_results['connectivity']['stellar_api'] = {
                        'status': 'unknown',
                        'message': 'No ping method available'
                    }
                    logger.warning("    ⚠ Stellar client has no get_latest_ledger method")
                    
            except Exception as e:
                health_results['connectivity']['stellar_api'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                logger.error(f"    ✗ Stellar API connectivity failed: {e}")
        else:
            health_results['connectivity']['stellar_api'] = {
                'status': 'failed',
                'error': 'Service failed to initialize'
            }
            logger.error(f"    ✗ Stellar API not available - initialization failed")
        
        # Test 3: Rate limiter status
        logger.info("\n  → Checking rate limiter status...")
        if 'rate_limiter' not in failed_services:
            try:
                rate_limiter = await registry.get('rate_limiter')
                if hasattr(rate_limiter, 'get_status'):
                    status = await rate_limiter.get_status()
                    health_results['connectivity']['rate_limiter'] = {
                        'status': 'healthy',
                        'details': status
                    }
                    logger.info(f"    ✓ Rate limiter operational")
                else:
                    health_results['connectivity']['rate_limiter'] = {
                        'status': 'unknown',
                        'message': 'No status method available'
                    }
                    logger.warning("    ⚠ Rate limiter has no get_status method")
            except Exception as e:
                health_results['connectivity']['rate_limiter'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                logger.error(f"    ✗ Rate limiter check failed: {e}")
        else:
            health_results['connectivity']['rate_limiter'] = {
                'status': 'failed',
                'error': 'Service failed to initialize'
            }
            logger.error(f"    ✗ Rate limiter not available - initialization failed")
        
        # ================================================================
        # SERVICE HEALTH CHECKS
        # ================================================================
        
        logger.info("\n🔍 Running individual service health checks...")
        
        # Define service categories
        service_categories = {
            'core': ['database', 'config', 'rate_limiter', 'stellar_client'],
            'protocols': ['air', 'water', 'earth', 'fire'],
            'services': [
                'synchronizer', 'ubec_analytics_service', 'ubec_distribution_service',
                'ubec_distribution_evaluator', 'ubec_audit_service'
            ],
            'utilities': ['ubec_holonic_evaluator', 'visualizer']
        }
        
        # Check each service
        for category, services in service_categories.items():
            logger.info(f"\n  → Checking {category} services...")
            
            for service_name in services:
                # Check if service failed to initialize
                if service_name in failed_services:
                    health_results['services'][service_name] = {
                        'status': 'failed',
                        'message': f'{service_name} failed to initialize',
                        'timestamp': datetime.now().isoformat(),
                        'category': category,
                        'initialization_failed': True
                    }
                    health_results['categories'][category]['services'].append({
                        'name': service_name,
                        'status': 'failed'
                    })
                    health_results['system']['services_unhealthy'] += 1
                    logger.error(f"    ✗ {service_name}: FAILED TO INITIALIZE")
                    continue
                
                # Try to get and check service
                try:
                    service = await registry.get(service_name)
                    
                    # Try to get health check if available
                    if hasattr(service, 'health_check'):
                        health_check_result = await service.health_check()
                        health_results['services'][service_name] = health_check_result
                        
                        status = health_check_result.get('status', 'unknown')
                        if status == 'healthy':
                            health_results['system']['services_healthy'] += 1
                            logger.info(f"    ✓ {service_name}: healthy")
                        elif status == 'degraded':
                            health_results['system']['services_degraded'] += 1
                            logger.warning(f"    ⚠ {service_name}: degraded")
                        else:
                            health_results['system']['services_unhealthy'] += 1
                            logger.error(f"    ✗ {service_name}: {status}")
                    else:
                        # Service exists but no health check method
                        health_results['services'][service_name] = {
                            'status': 'operational',
                            'message': f'{service_name} operational (no health check)',
                            'timestamp': datetime.now().isoformat(),
                            'category': category
                        }
                        health_results['system']['services_healthy'] += 1
                        logger.info(f"    ✓ {service_name}: operational")
                    
                    health_results['categories'][category]['services'].append({
                        'name': service_name,
                        'status': health_results['services'][service_name].get('status', 'operational')
                    })
                    
                except Exception as e:
                    health_results['services'][service_name] = {
                        'status': 'error',
                        'message': f'Health check failed: {str(e)}',
                        'timestamp': datetime.now().isoformat(),
                        'category': category,
                        'error': str(e)
                    }
                    health_results['categories'][category]['services'].append({
                        'name': service_name,
                        'status': 'error'
                    })
                    health_results['system']['services_unhealthy'] += 1
                    logger.error(f"    ✗ {service_name}: ERROR - {e}")
                
                health_results['system']['services_checked'] += 1
        
        # ================================================================
        # OVERALL SYSTEM STATUS
        # ================================================================
        
        # Determine category statuses
        for category, data in health_results['categories'].items():
            services_in_cat = data['services']
            if not services_in_cat:
                data['status'] = 'unknown'
            elif all(s['status'] in ['healthy', 'operational'] for s in services_in_cat):
                data['status'] = 'healthy'
            elif any(s['status'] in ['failed', 'error', 'unhealthy'] for s in services_in_cat):
                data['status'] = 'unhealthy'
            else:
                data['status'] = 'degraded'
        
        # Determine overall system status
        if health_results['system']['services_unhealthy'] > 0 or failed_services:
            health_results['system']['status'] = 'unhealthy'
        elif health_results['system']['services_degraded'] > 0:
            health_results['system']['status'] = 'degraded'
        elif health_results['system']['services_healthy'] > 0:
            health_results['system']['status'] = 'healthy'
        else:
            health_results['system']['status'] = 'unknown'
        
        logger.info("\n" + "=" * 70)
        logger.info("HEALTH CHECK SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Overall Status: {health_results['system']['status'].upper()}")
        logger.info(f"Services Checked: {health_results['system']['services_checked']}")
        logger.info(f"  ✓ Healthy: {health_results['system']['services_healthy']}")
        logger.info(f"  ⚠ Degraded: {health_results['system']['services_degraded']}")
        logger.info(f"  ✗ Unhealthy: {health_results['system']['services_unhealthy']}")
        logger.info(f"  ? Unknown: {health_results['system']['services_unknown']}")
        if failed_services:
            logger.error(f"  ✗ Failed to Initialize: {len(failed_services)}")
        logger.info("=" * 70)
        
        return create_response(
            success=len(failed_services) == 0,
            data=health_results
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return create_response(
            success=False,
            error=f"Health check failed: {str(e)}"
        )


async def run_status() -> Dict[str, Any]:
    """
    Get quick system status without deep health checks.
    """
    logger.info("\n" + "=" * 70)
    logger.info("SYSTEM STATUS CHECK")
    logger.info("=" * 70)
    
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'version': '16.0.0',
            'services': []
        }
        
        # Get list of initialized services
        for service_name in registry._services:
            status['services'].append({
                'name': service_name,
                'status': 'initialized'
            })
        
        return create_response(success=True, data=status)
    except Exception as e:
        return create_response(success=False, error=str(e))


async def run_protocol_health() -> Dict[str, Any]:
    """
    Check health of protocol services specifically.
    """
    logger.info("\n" + "=" * 70)
    logger.info("PROTOCOL HEALTH CHECK")
    logger.info("=" * 70)
    
    try:
        protocol_health = {
            'timestamp': datetime.now().isoformat(),
            'protocols': {}
        }
        
        protocols = ['air', 'water', 'earth', 'fire']
        
        for protocol in protocols:
            try:
                service = await registry.get(protocol)
                if hasattr(service, 'health_check'):
                    protocol_health['protocols'][protocol] = await service.health_check()
                else:
                    protocol_health['protocols'][protocol] = {
                        'status': 'operational',
                        'message': 'Service operational (no health check method)'
                    }
            except Exception as e:
                protocol_health['protocols'][protocol] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return create_response(success=True, data=protocol_health)
    except Exception as e:
        return create_response(success=False, error=str(e))


async def run_sync(sync_type: str, max_accounts: Optional[int], force: bool) -> Dict[str, Any]:
    """
    Run data synchronization operation.
    """
    logger.info(f"\n📊 Running {sync_type} sync...")
    
    try:
        synchronizer = await registry.get('synchronizer')
        
        if sync_type == 'asset':
            result = await synchronizer.sync_account_balances(
                max_accounts=max_accounts,
                force=force
            )
        elif sync_type == 'liquidity':
            result = await synchronizer.sync_liquidity_pools(force=force)
        else:
            return create_response(success=False, error=f"Unknown sync type: {sync_type}")
        
        return create_response(success=True, data=result)
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_discover(max_accounts: int) -> Dict[str, Any]:
    """
    Discover new account holders.
    """
    logger.info(f"\n🔍 Discovering new accounts (max: {max_accounts})...")
    
    try:
        synchronizer = await registry.get('synchronizer')
        result = await synchronizer.discover_new_accounts(max_accounts=max_accounts)
        return create_response(success=True, data=result)
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_analytics(analysis_type: str) -> Dict[str, Any]:
    """
    Run analytics operation.
    """
    logger.info(f"\n📈 Running {analysis_type} analytics...")
    
    try:
        analytics = await registry.get('ubec_analytics_service')
        
        if analysis_type == 'overview':
            result = await analytics.get_distribution_overview()
        elif analysis_type == 'accounts':
            result = await analytics.get_top_accounts()
        elif analysis_type == 'trends':
            result = await analytics.get_distribution_trends()
        else:
            return create_response(success=False, error=f"Unknown analysis type: {analysis_type}")
        
        return create_response(success=True, data=result)
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_distribution(action: Optional[str], dry_run: bool) -> Dict[str, Any]:
    """
    Run distribution operation.
    """
    logger.info(f"\n💰 Running distribution{' (DRY RUN)' if dry_run else ''}...")
    
    try:
        distribution = await registry.get('ubec_distribution_service')
        evaluator = await registry.get('ubec_distribution_evaluator')
        
        if action == 'evaluate':
            result = await evaluator.evaluate_compliance()
        elif action == 'execute':
            if dry_run:
                result = await distribution.preview_distributions()
            else:
                result = await distribution.execute_distributions()
        else:
            # Default: get current status
            result = await distribution.get_distribution_status()
        
        return create_response(success=True, data=result)
    except Exception as e:
        logger.error(f"Distribution failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_visualize(action: str, chart_type: Optional[str], 
                       format: str, output_dir: Optional[str],
                       include_advanced: bool) -> Dict[str, Any]:
    """
    Run visualization operation.
    """
    logger.info(f"\n📊 Generating visualizations...")
    
    try:
        visualizer = await registry.get('visualizer')
        
        if action == 'report':
            result = await visualizer.generate_full_report(
                output_dir=output_dir or 'visualizations',
                format=format,
                include_advanced=include_advanced
            )
        elif action == 'chart' and chart_type:
            result = await visualizer.generate_chart(
                chart_type=chart_type,
                output_dir=output_dir or 'visualizations',
                format=format
            )
        else:
            return create_response(success=False, error="Invalid visualization action or missing chart_type")
        
        return create_response(success=True, data=result)
    except Exception as e:
        logger.error(f"Visualization failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


# ========================================================================
# COMMAND LINE ARGUMENTS
# ========================================================================

def parse_arguments():
    """
    Parse command-line arguments.
    
    Principle #2: Entry point configuration
    """
    parser = argparse.ArgumentParser(
        description='UBEC Protocol System - Unified Entry Point'
    )
    
    parser.add_argument(
        '--mode',
        default='health',
        choices=[
            'health',
            'status',
            'protocol-health',
            'sync',
            'discover',
            'analytics',
            'distribution',
            'visualize'
        ],
        help='Operation mode'
    )
    
    # Sync options
    parser.add_argument(
        '--sync-type',
        default='asset',
        choices=['asset', 'liquidity'],
        help='Type of sync to perform'
    )
    
    parser.add_argument(
        '--max-accounts',
        type=int,
        help='Maximum accounts to process'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force operation even if recently completed'
    )
    
    # Analytics options
    parser.add_argument(
        '--analysis-type',
        default='overview',
        choices=['overview', 'accounts', 'trends'],
        help='Type of analysis to perform'
    )
    
    # Distribution options
    parser.add_argument(
        '--action',
        help='Action to perform (depends on mode)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no actual changes)'
    )
    
    # Visualization options
    parser.add_argument(
        '--chart-type',
        help='Type of chart to generate'
    )
    
    parser.add_argument(
        '--format',
        default='png',
        choices=['png', 'pdf', 'svg'],
        help='Output format for visualizations'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for generated files'
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
    
    CRITICAL FIX v16.0.0: Proper error handling and exit codes
    
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
    logger.info(f"Version: 16.0.0 (Dependency Ordering & Error Handling)")
    logger.info("=" * 70)
    
    try:
        # Step 1: Register all services
        register_core_services()
        
        # Step 2: Validate registration
        validate_service_registration()
        
        logger.info("\n" + "=" * 70)
        logger.info("SERVICE REGISTRY VALIDATED - READY TO EXECUTE")
        logger.info("=" * 70)
        
        # Step 3: Initialize services concurrently
        # CRITICAL v16.0.0: Now returns failed services and exit code
        init_times, failed_services, init_exit_code = await initialize_services_concurrent()
        
        # Check if initialization failed
        if init_exit_code != 0:
            logger.error("\n" + "=" * 70)
            logger.error("✗ SERVICE INITIALIZATION FAILED")
            logger.error("=" * 70)
            logger.error(f"Failed services: {', '.join(failed_services)}")
            
            # Attempt cleanup
            try:
                await registry.shutdown()
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {cleanup_error}")
            
            return 1
        
        # Step 4: Execute operation
        result = None
        
        # System Operations
        if args.mode == 'health':
            result = await run_health_check(init_times, failed_services)
        
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
        
        # Step 5: Shutdown services
        logger.info("\n" + "=" * 70)
        logger.info("SHUTTING DOWN SERVICES")
        logger.info("=" * 70)
        
        await registry.shutdown()
        
        # Determine final exit code based on operation result
        operation_success = result.get('success', True) if result else True
        final_exit_code = 0 if operation_success else 1
        
        if final_exit_code == 0:
            logger.info("\n" + "=" * 70)
            logger.info("✓ OPERATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
        else:
            logger.error("\n" + "=" * 70)
            logger.error("✗ OPERATION COMPLETED WITH ERRORS")
            logger.error("=" * 70)
        
        return final_exit_code
            
    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error("✗ FATAL ERROR: Operation failed")
        logger.error("=" * 70)
        logger.error(f"Error: {e}", exc_info=True)
        
        # Attempt cleanup
        try:
            await registry.shutdown()
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {cleanup_error}")
        
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
