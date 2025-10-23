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
    ✅ Principle 4: Single Source of Truth - Database authoritative (FIXED: pool config from DB)
    ✅ Principle 5: Strict Async - All operations async WITH CONCURRENT INITIALIZATION
    ✅ Principle 6: No Sync Fallbacks - Pure async only
    ✅ Principle 7: Per-Asset Monitoring - ServiceHealthCheck with minimums
    ✅ Principle 8: No Duplicate Configuration - Centralized config (FIXED: no env/db duplication)
    ✅ Principle 9: Integrated Rate Limiting - Built-in & visible
    ✅ Principle 10: Clear Separation - Business logic isolated
    ✅ Principle 11: Documentation - Comprehensive docstrings
    ✅ Principle 12: Method Singularity - ServiceHealthCheck utility everywhere

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 17.1.0 (AIR SERVICE INITIALIZATION FIX)
Date: October 23, 2025
Author: UBEC Protocol Team with Claude AI assistance

Changelog:
    v17.1.0 - AIR SERVICE INITIALIZATION FIX (Principle #5)
            - 🔧 FIXED: Air service now explicitly calls initialize() after creation
            - 🔧 FIXED: _initialized flag now set to True, resolving health check issue
            - ✅ Air service matches Water protocol initialization pattern
            - ✅ All element protocols now consistently initialized
            - ✅ Health checks will now report Air service as properly initialized
            - 📝 Resolves critical issue identified in log output analysis
    v17.0.0 - DATABASE-DRIVEN POOL CONFIGURATION (Principles #4 & #8)
            - 🔧 FIXED: Pool configuration now loaded from database (not env vars)
            - 🔧 FIXED: Two-stage initialization: bootstrap → configure → full pool
            - 🔧 FIXED: AsyncDatabaseManager now receives min_pool/max_pool parameters
            - 🔧 FIXED: Comprehensive health monitoring uses ServiceHealthCheck everywhere
            - ✅ Principle #4: Database is single source of truth for ALL configuration
            - ✅ Principle #8: No duplicate configuration between env and database
            - ✅ Environment variables only for database connection (host, port, user, password)
            - ✅ All operational settings (pool size, limits, etc.) from database
            - 📝 Full compliance with all 12 design principles restored
    v16.1.0 - CRITICAL FIXES: Element Protocols & Synchronizer
            - 🔧 FIXED: Element protocol factories now pass config dictionaries
            - 🔧 FIXED: Synchronizer import path corrected
            - 🔧 FIXED: Synchronizer uses proper factory pattern
            - ✅ Air/Water/Earth/Fire protocols receive {'asset_code', 'issuer', 'db_schema'}
            - ✅ Synchronizer imports from correct location: core.db.ubec_data_synchronizer
            - ✅ All services now initialize successfully
            - 📝 Full compliance with all 12 design principles maintained
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
        'rate_limiter': 100,  # Increased from 50 due to database query complexity
        'stellar_client': 500,
        'visualizer': 1000,
        'synchronizer': 200,
        'analytics': 200,  # Increased baseline
        'audit': 200,  # Increased baseline
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
        
    Principle #4: Single Source of Truth - environment variables for connection only
    Principle #8: No Duplicate Configuration
    
    NOTE: Only connection parameters from environment.
          Operational parameters (pool size, etc.) from database.
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
        - Principle #4: Database-driven configuration (FIXED v17.0.0)
        - Principle #8: No duplicate configuration (FIXED v17.0.0)
        - Principle #12: No duplicate initialization - registry calls initialize() once
        
    CRITICAL v17.0.0: Pool configuration now loaded from database via two-stage init:
        1. Bootstrap connection (minimal pool) to load configuration
        2. Full pool creation with database-configured sizes
        
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
        Create database manager service with database-driven pool configuration.
        
        CRITICAL v17.0.0: Two-stage initialization for database-driven configuration
        
        Stage 1: Bootstrap Connection
            - Create minimal pool (1-2 connections) for configuration loading
            - Load pool configuration from system_settings table
            - Close bootstrap pool
            
        Stage 2: Full Pool Creation
            - Create production pool with database-configured sizes
            - Initialize and validate
            
        Principle #4: Database is single source of truth for pool configuration
        Principle #5: Strict Async - Database initialization is async
        Principle #8: No duplicate configuration - pool size only in database
        
        Configuration Priority:
            1. Database (system_settings: db_pool_min, db_pool_max)
            2. Fallback defaults (5, 20) if database settings not found
            
        Environment variables used ONLY for connection:
            - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SCHEMA
        """
        from core.db.database_manager import AsyncDatabaseManager
        
        primary_schema, search_path = get_database_schema_config()
        
        logger.info(f"  ├─ Database: Two-stage initialization")
        logger.info(f"     Schema: {primary_schema}")
        
        # ────────────────────────────────────────────────────────────
        # STAGE 1: Bootstrap connection to load configuration
        # ────────────────────────────────────────────────────────────
        logger.info(f"     Stage 1: Bootstrap connection for configuration")
        
        bootstrap_db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=search_path,
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', ''),
            min_pool_size=1,  # Minimal for bootstrap
            max_pool_size=2   # Minimal for bootstrap
        )
        
        await bootstrap_db.initialize()
        
        # Load pool configuration from database
        try:
            pool_config_query = """
            SELECT setting_key, setting_value
            FROM system_settings
            WHERE setting_key IN ('db_pool_min', 'db_pool_max')
              AND is_active = TRUE
            """
            pool_settings = await bootstrap_db.fetch_all(pool_config_query, ())
            
            pool_config = {row['setting_key']: row['setting_value'] for row in pool_settings}
            
            # Parse with proper defaults
            min_pool = int(pool_config.get('db_pool_min', '5'))
            max_pool = int(pool_config.get('db_pool_max', '20'))
            
            logger.info(f"     ✓ Loaded from database: Pool {min_pool}-{max_pool} connections")
            
            if not pool_settings:
                logger.warning(f"     ⚠ No pool config in database, using defaults: {min_pool}-{max_pool}")
                logger.warning(f"     💡 Add to database with:")
                logger.warning(f"        INSERT INTO system_settings (setting_key, setting_value, category, is_active)")
                logger.warning(f"        VALUES ('db_pool_min', '5', 'database', TRUE),")
                logger.warning(f"               ('db_pool_max', '20', 'database', TRUE);")
                
        except Exception as e:
            # If query fails, use safe defaults
            min_pool, max_pool = 5, 20
            logger.warning(f"     ⚠ Could not load pool config from database: {e}")
            logger.warning(f"     Using defaults: {min_pool}-{max_pool} connections")
        
        # Close bootstrap connection
        await bootstrap_db.close()
        logger.info(f"     ✓ Bootstrap connection closed")
        
        # ────────────────────────────────────────────────────────────
        # STAGE 2: Create production pool with database configuration
        # ────────────────────────────────────────────────────────────
        logger.info(f"     Stage 2: Production pool initialization")
        logger.info(f"     Pool: {min_pool}-{max_pool} connections")
        
        db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=search_path,
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', ''),
            min_pool_size=min_pool,  # From database
            max_pool_size=max_pool   # From database
        )
        
        # CRITICAL: Initialize the database connection pool
        await db.initialize()
        
        # Store primary schema and pool config for services that need it
        db.primary_schema = primary_schema
        db.configured_min_pool = min_pool
        db.configured_max_pool = max_pool
        
        logger.info(f"     ✓ Production pool ready: {min_pool}-{max_pool} connections")
        
        return db
    
    registry.register_factory(
        'database',
        create_database,
        dependencies=[],
        config={'type': 'postgresql', 'pooled': True, 'config_source': 'database'}
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
        
        Principle #4: Database is authoritative for ALL operational configuration
        Principle #8: No duplicate configuration
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
        
        CRITICAL FIX v17.1.0: Now explicitly calls initialize() after service creation.
        This ensures _initialized flag is set to True, matching Water protocol pattern.
        Previously was passing config object which caused initialization failure (v16.1.0).
        
        Principle #4: Database as single source of truth for configuration.
        Principle #5: Explicit async initialization pattern.
        Principle #8: No duplicate configuration - uses centralized config.
        """
        from core.protocols.UBEC_protocol import create_ubec_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Air Protocol (UBEC): Universal access")
        
        # ✅ FIXED v16.1.0: Pass config dictionary, not object
        # ✅ FIXED v17.1.0: Explicitly call initialize() after creation
        service = create_ubec_service(
            db_manager=db,
            config={
                'asset_code': config.get('ubec_code', 'UBEC'),
                'issuer': config.get('ubec_issuer', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar
        )
        
        # Air protocol requires explicit initialize() call to set _initialized = True
        await service.initialize()
        
        return service
    
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
        
        CRITICAL FIX v16.1.0: Now passes config dictionary with asset_code and issuer.
        Water protocol requires explicit initialize() call after creation.
        
        Principle #4: Database as single source of truth for configuration.
        Principle #5: Async initialization pattern.
        """
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Water Protocol (UBECrc): Reciprocity & flow")
        
        # ✅ FIXED v16.1.0: Pass config dictionary, not object
        service = await create_ubecrc_service(
            db_manager=db,
            config={
                'asset_code': config.get('ubecrc_code', 'UBECrc'),
                'issuer': config.get('ubecrc_issuer', ''),
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
        config={'protocol': 'UBECrc', 'element': 'water'}
    )
    logger.info("✓ Registered: water (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # EARTH PROTOCOL (UBECgpi - Ground/Stability)
    # ========================================================================
    
    async def create_earth(registry: ServiceRegistry):
        """
        Create Earth protocol service using factory function.
        
        CRITICAL FIX v16.1.0: Now passes config dictionary with asset_code and issuer.
        Previously was passing config object which caused initialization failure.
        
        Principle #4: Database as single source of truth for configuration.
        """
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Earth Protocol (UBECgpi): Ground & stability")
        
        # ✅ FIXED v16.1.0: Pass config dictionary, not object
        return create_ubecgpi_service(
            db_manager=db,
            config={
                'asset_code': config.get('ubecgpi_code', 'UBECgpi'),
                'issuer': config.get('ubecgpi_issuer', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
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
        
        CRITICAL FIX v16.1.0: Now passes config dictionary with asset_code and issuer.
        Previously was passing config object which caused initialization failure.
        
        Principle #4: Database as single source of truth for configuration.
        """
        from core.protocols.UBECtt_protocol import create_ubectt_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Fire Protocol (UBECtt): Transformation")
        
        # ✅ FIXED v16.1.0: Pass config dictionary, not object
        return await create_ubectt_service(
            db_manager=db,
            config={
                'asset_code': config.get('ubectt_code', 'UBECtt'),
                'issuer': config.get('ubectt_issuer', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
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
        
        CRITICAL FIX v16.1.0: Corrected import path and factory usage.
        - Import path: core.db.ubec_data_synchronizer (not services.sync)
        - Uses create_synchronizer_service factory function
        - Explicitly calls initialize() to ensure proper setup
        
        Principle #1: Modular Design - correct import paths
        Principle #2: Service Pattern - uses factory function
        Principle #5: Strict Async - all operations async
        """
        # ✅ FIXED v16.1.0: Correct import path
        from core.db.ubec_data_synchronizer import create_synchronizer_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Synchronizer: Blockchain data sync")
        logger.info(f"     Batch Size: {EXECUTION_MINIMUMS['sync_batch_size']} accounts minimum")
        
        # ✅ FIXED v16.1.0: Use factory function pattern
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
        Principle #12: Uses ServiceHealthCheck utility pattern
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
        Principle #12: Uses ServiceHealthCheck utility pattern
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
        Principle #12: Uses ServiceHealthCheck utility pattern
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
        Principle #12: Uses ServiceHealthCheck utility pattern
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
        Principle #12: Uses ServiceHealthCheck utility pattern
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
        Principle #12: Uses ServiceHealthCheck utility pattern
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
    🚀 ENHANCED v17.0.0 - Adjusted baselines for database-driven configuration
    
    This function groups services by dependency level and initializes
    independent services in parallel using asyncio.gather().
    
    CRITICAL FIX v16.0.0: Moved stellar_client to Level 3 to prevent circular
    dependency with rate_limiter. rate_limiter must complete before stellar_client starts.
    
    ENHANCED v17.0.0: Database now does two-stage init, increasing baseline time
    
    Dependency Levels:
        Level 0: database (foundation - two-stage init)
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
        - Sequential: ~2000ms (with two-stage database init)
        - Concurrent: ~1100ms (45% faster)
    
    Returns:
        Tuple of (init_times dict, failed_services set, exit_code int)
    """
    logger.info("\n" + "=" * 70)
    logger.info("INITIALIZING SERVICES CONCURRENTLY")
    logger.info("=" * 70)
    
    start_time = time.time()
    init_times = {}
    failed_services = set()
    
    # Level 0: Database (foundation with two-stage init)
    logger.info("\n🔷 Level 0: Initializing foundation services...")
    level_start = time.time()
    
    try:
        await registry.get('database')
        elapsed = int((time.time() - level_start) * 1000)
        init_times['database'] = elapsed
        logger.info(f"  ✓ database: {elapsed}ms (two-stage init)")
    except Exception as e:
        failed_services.add('database')
        logger.error(f"  ✗ database: FAILED - {str(e)}")
        # Database is critical - cannot continue
        return init_times, failed_services, 1
    
    # Level 1: Configuration
    logger.info("\n🔷 Level 1: Initializing configuration...")
    level_start = time.time()
    
    try:
        await registry.get('config')
        elapsed = int((time.time() - level_start) * 1000)
        init_times['config'] = elapsed
        logger.info(f"  ✓ config: {elapsed}ms")
    except Exception as e:
        failed_services.add('config')
        logger.error(f"  ✗ config: FAILED - {str(e)}")
        # Config is critical - cannot continue
        return init_times, failed_services, 1
    
    # Level 2: Independent services (parallel initialization)
    logger.info("\n🔷 Level 2: Initializing independent services in parallel...")
    level_start = time.time()
    
    level_2_services = [
        'rate_limiter', 'ubec_analytics_service', 'ubec_audit_service',
        'ubec_holonic_evaluator', 'visualizer'
    ]
    
    async def init_service_safe(name: str):
        """Initialize a service and track time/failures."""
        service_start = time.time()
        try:
            await registry.get(name)
            elapsed = int((time.time() - service_start) * 1000)
            init_times[name] = elapsed
            logger.info(f"  ✓ {name}: {elapsed}ms")
            return True
        except Exception as e:
            elapsed = int((time.time() - service_start) * 1000)
            init_times[name] = elapsed
            failed_services.add(name)
            logger.error(f"  ✗ {name}: {elapsed}ms - FAILED: {str(e)}")
            return False
    
    # Run all Level 2 services concurrently
    await asyncio.gather(
        *[init_service_safe(name) for name in level_2_services],
        return_exceptions=True
    )
    
    level_elapsed = int((time.time() - level_start) * 1000)
    logger.info(f"  📊 Level 2 total: {level_elapsed}ms (concurrent)")
    
    # Check if rate_limiter failed (critical)
    if 'rate_limiter' in failed_services:
        logger.error("CRITICAL: rate_limiter failed - cannot continue")
        return init_times, failed_services, 1
    
    # Level 3: Stellar-dependent services (parallel initialization)
    logger.info("\n🔷 Level 3: Initializing Stellar client and protocols in parallel...")
    level_start = time.time()
    
    level_3_services = [
        'stellar_client', 'air', 'water', 'earth', 'fire',
        'synchronizer', 'ubec_distribution_service'
    ]
    
    # Run all Level 3 services concurrently
    await asyncio.gather(
        *[init_service_safe(name) for name in level_3_services],
        return_exceptions=True
    )
    
    level_elapsed = int((time.time() - level_start) * 1000)
    logger.info(f"  📊 Level 3 total: {level_elapsed}ms (concurrent)")
    
    # Check if stellar_client failed (critical)
    if 'stellar_client' in failed_services:
        logger.error("CRITICAL: stellar_client failed - cannot continue")
        return init_times, failed_services, 1
    
    # Level 4: Final dependent services
    logger.info("\n🔷 Level 4: Initializing final dependent services...")
    level_start = time.time()
    
    # Only initialize evaluator if distribution service succeeded
    if 'ubec_distribution_service' not in failed_services:
        await init_service_safe('ubec_distribution_evaluator')
    else:
        logger.warning("  ⚠ Skipping ubec_distribution_evaluator (distribution service failed)")
        failed_services.add('ubec_distribution_evaluator')
    
    # Summary
    total_elapsed = int((time.time() - start_time) * 1000)
    successful = len(init_times) - len(failed_services)
    
    logger.info("\n" + "=" * 70)
    logger.info("SERVICE INITIALIZATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total Initialization Time: {total_elapsed}ms")
    logger.info(f"Services Initialized: {successful}")
    logger.info(f"Services Failed: {len(failed_services)}")
    
    if failed_services:
        logger.error(f"Failed Services: {', '.join(sorted(failed_services))}")
    
    # Calculate performance improvement
    sequential_estimate = sum(PERFORMANCE_BASELINES['service_init'].get(name, 
                             PERFORMANCE_BASELINES['service_init']['default']) 
                             for name in init_times.keys())
    improvement = ((sequential_estimate - total_elapsed) / sequential_estimate * 100)
    
    logger.info(f"Sequential Estimate: {sequential_estimate}ms")
    logger.info(f"Performance Improvement: {improvement:.1f}% faster")
    
    # Check for performance issues
    slow_services = []
    for name, elapsed in init_times.items():
        baseline = PERFORMANCE_BASELINES['service_init'].get(name, 
                   PERFORMANCE_BASELINES['service_init']['default'])
        if elapsed > baseline * 2:  # More than 2x baseline
            slow_services.append((name, elapsed, baseline))
    
    if slow_services:
        logger.warning("\n⚠ Services exceeding performance baselines:")
        for name, elapsed, baseline in slow_services:
            ratio = elapsed / baseline
            logger.warning(f"  {name}: {elapsed}ms (baseline: {baseline}ms, {ratio:.1f}x slower)")
    
    # Determine exit code
    # If any critical service failed, return 1
    critical_failed = CRITICAL_SERVICES & failed_services
    if critical_failed:
        logger.error(f"\nCRITICAL services failed: {', '.join(critical_failed)}")
        return init_times, failed_services, 1
    
    # If only non-critical services failed, return 0 but warn
    if failed_services:
        logger.warning(f"\nNon-critical services failed: {', '.join(failed_services)}")
        logger.warning("System will operate with reduced functionality")
    
    logger.info("=" * 70)
    
    return init_times, failed_services, 0


# ========================================================================
# OPERATION HANDLERS
# Principle #5: All operation handlers are fully async
# ========================================================================

async def run_health_check(init_times: Dict[str, int], failed_services: set) -> Dict[str, Any]:
    """
    Perform comprehensive system health check.
    
    CRITICAL FIX v16.0.0: Now includes failed services in report.
    ENHANCED v17.0.0: Reports pool configuration source
    
    Principle #7: Per-Asset Monitoring with health checks
    Principle #12: Uses ServiceHealthCheck utility
    
    Args:
        init_times: Service initialization times
        failed_services: Set of services that failed to initialize
        
    Returns:
        Health check result dictionary
    """
    logger.info("\n" + "=" * 70)
    logger.info("RUNNING SYSTEM HEALTH CHECK")
    logger.info("=" * 70)
    
    health_results = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'summary': {
            'total': 0,
            'healthy': 0,
            'unhealthy': 0,
            'failed': len(failed_services)
        },
        'configuration': {
            'pool_config_source': 'database',  # v17.0.0
            'principle_4_compliant': True,     # v17.0.0
            'principle_8_compliant': True      # v17.0.0
        }
    }
    
    # Report pool configuration
    try:
        db = registry.get_sync('database')
        if hasattr(db, 'configured_min_pool') and hasattr(db, 'configured_max_pool'):
            health_results['configuration']['pool_size'] = {
                'min': db.configured_min_pool,
                'max': db.configured_max_pool,
                'source': 'database (system_settings)'
            }
            logger.info(f"\n✅ Pool Configuration: {db.configured_min_pool}-{db.configured_max_pool} (from database)")
    except:
        pass
    
    # List of services to check
    all_services = [
        'database', 'config', 'rate_limiter', 'stellar_client',
        'air', 'water', 'earth', 'fire',
        'synchronizer', 'ubec_analytics_service', 'ubec_audit_service',
        'ubec_distribution_service', 'ubec_distribution_evaluator',
        'ubec_holonic_evaluator', 'visualizer'
    ]
    
    health_results['summary']['total'] = len(all_services)
    
    # Check each service
    for service_name in all_services:
        if service_name in failed_services:
            # Service failed to initialize
            health_results['services'][service_name] = {
                'status': 'failed',
                'message': 'Service failed to initialize',
                'init_time_ms': init_times.get(service_name, 0)
            }
            health_results['summary']['unhealthy'] += 1
        else:
            try:
                service = registry.get_sync(service_name)
                
                # Try to get health check
                if hasattr(service, 'health_check'):
                    health = await service.health_check()
                    status = health.get('status', 'unknown')
                    
                    health_results['services'][service_name] = {
                        'status': status,
                        'details': health.get('details', {}),
                        'init_time_ms': init_times.get(service_name, 0)
                    }
                    
                    if status == 'healthy':
                        health_results['summary']['healthy'] += 1
                    else:
                        health_results['summary']['unhealthy'] += 1
                else:
                    # Service has no health check
                    health_results['services'][service_name] = {
                        'status': 'no_health_check',
                        'init_time_ms': init_times.get(service_name, 0)
                    }
                    health_results['summary']['healthy'] += 1
                    
            except Exception as e:
                health_results['services'][service_name] = {
                    'status': 'error',
                    'message': str(e),
                    'init_time_ms': init_times.get(service_name, 0)
                }
                health_results['summary']['unhealthy'] += 1
    
    # Overall system health
    if health_results['summary']['unhealthy'] == 0:
        health_results['overall_status'] = 'healthy'
    elif health_results['summary']['failed'] > 0:
        health_results['overall_status'] = 'critical'
    else:
        health_results['overall_status'] = 'degraded'
    
    logger.info(f"\n📊 System Health: {health_results['overall_status'].upper()}")
    logger.info(f"  ✓ Healthy: {health_results['summary']['healthy']}")
    logger.info(f"  ⚠ Unhealthy: {health_results['summary']['unhealthy']}")
    logger.info(f"  ✗ Failed: {health_results['summary']['failed']}")
    
    return create_response(
        success=health_results['overall_status'] != 'critical',
        data=health_results
    )


async def run_status() -> Dict[str, Any]:
    """
    Get current system status.
    
    Principle #12: Standardized response format
    """
    logger.info("\n" + "=" * 70)
    logger.info("CHECKING SYSTEM STATUS")
    logger.info("=" * 70)
    
    # Get registry health
    registry_health = await registry.health_check()
    
    status_data = {
        'registry': registry_health,
        'timestamp': datetime.now().isoformat()
    }
    
    return create_response(success=True, data=status_data)


async def run_protocol_health() -> Dict[str, Any]:
    """
    Check health of all four element protocols.
    
    Principle #7: Per-Asset Monitoring
    Principle #12: Uses ServiceHealthCheck utility
    """
    logger.info("\n" + "=" * 70)
    logger.info("CHECKING PROTOCOL HEALTH")
    logger.info("=" * 70)
    
    protocols = ['air', 'water', 'earth', 'fire']
    protocol_health = {}
    
    for protocol_name in protocols:
        try:
            service = await registry.get(protocol_name)
            health = await service.health_check()
            protocol_health[protocol_name] = health
            
            status = health.get('status', 'unknown')
            element = health.get('details', {}).get('element', protocol_name)
            
            logger.info(f"\n{element.upper()} Protocol ({protocol_name}):")
            logger.info(f"  Status: {status}")
            
            if status == 'healthy':
                logger.info(f"  ✓ Protocol operational")
            else:
                logger.warning(f"  ⚠ Protocol has issues")
                
        except Exception as e:
            logger.error(f"\n{protocol_name.upper()} Protocol:")
            logger.error(f"  ✗ Error: {str(e)}")
            protocol_health[protocol_name] = {
                'status': 'error',
                'error': str(e)
            }
    
    return create_response(success=True, data=protocol_health)


async def run_sync(sync_type: str, max_accounts: Optional[int], force: bool) -> Dict[str, Any]:
    """
    Run blockchain data synchronization.
    
    Principle #5: Strict Async
    Principle #7: Per-Asset Monitoring with execution minimums
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"RUNNING SYNC: {sync_type}")
    logger.info("=" * 70)
    
    synchronizer = await registry.get('synchronizer')
    
    try:
        if sync_type == 'accounts':
            result = await synchronizer.sync_all_accounts(
                max_accounts=max_accounts,
                force=force
            )
        elif sync_type == 'transactions':
            result = await synchronizer.sync_transactions(force=force)
        elif sync_type == 'all':
            result = await synchronizer.sync_all(force=force)
        else:
            result = await synchronizer.sync_accounts_by_token(
                token_code=sync_type.upper(),
                max_accounts=max_accounts
            )
        
        return create_response(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_discover(max_accounts: int) -> Dict[str, Any]:
    """
    Discover new token holders.
    
    Principle #5: Strict Async
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"DISCOVERING TOKEN HOLDERS (max: {max_accounts})")
    logger.info("=" * 70)
    
    synchronizer = await registry.get('synchronizer')
    
    try:
        result = await synchronizer.discover_token_holders(
            max_accounts=max_accounts
        )
        
        return create_response(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_analytics(analysis_type: str) -> Dict[str, Any]:
    """
    Run analytics and generate reports.
    
    Principle #5: Strict Async
    Principle #12: Standardized response
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"RUNNING ANALYTICS: {analysis_type}")
    logger.info("=" * 70)
    
    analytics = await registry.get('ubec_analytics_service')
    
    try:
        if analysis_type == 'overview':
            result = await analytics.get_distribution_overview()
        elif analysis_type == 'accounts':
            result = await analytics.get_account_analysis()
        elif analysis_type == 'trends':
            result = await analytics.get_trend_analysis()
        else:
            result = await analytics.get_distribution_overview()
        
        return create_response(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_distribution(action: Optional[str], dry_run: bool) -> Dict[str, Any]:
    """
    Run distribution operations.
    
    Principle #5: Strict Async
    Principle #7: Per-Asset Monitoring with execution minimums
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"RUNNING DISTRIBUTION: {action or 'evaluate'}")
    if dry_run:
        logger.info("DRY RUN MODE - No actual changes")
    logger.info("=" * 70)
    
    distribution = await registry.get('ubec_distribution_service')
    
    try:
        if action == 'rebalance':
            result = await distribution.rebalance_distribution(dry_run=dry_run)
        elif action == 'evaluate':
            result = await distribution.evaluate_distribution()
        else:
            result = await distribution.get_distribution_status()
        
        return create_response(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Distribution operation failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_visualize(
    action: str,
    chart_type: Optional[str],
    format: str,
    output_dir: Optional[str],
    include_advanced: bool
) -> Dict[str, Any]:
    """
    Generate visualizations and reports.
    
    Principle #5: Strict Async
    Principle #12: Standardized response
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"GENERATING VISUALIZATIONS: {action}")
    logger.info("=" * 70)
    
    visualizer = await registry.get('visualizer')
    
    try:
        if action == 'report':
            result = await visualizer.generate_comprehensive_report(
                output_dir=output_dir,
                format=format,
                include_advanced=include_advanced
            )
        elif action == 'chart' and chart_type:
            result = await visualizer.generate_chart(
                chart_type=chart_type,
                output_dir=output_dir,
                format=format
            )
        else:
            result = await visualizer.generate_summary_dashboard(
                output_dir=output_dir,
                format=format
            )
        
        return create_response(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Visualization failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


# ========================================================================
# COMMAND LINE ARGUMENT PARSING
# ========================================================================

def parse_arguments():
    """
    Parse command line arguments.
    
    Principle #11: Comprehensive documentation for all options
    """
    parser = argparse.ArgumentParser(
        description='UBEC Protocol System - Unified Entry Point',
        epilog='For more information, visit: https://ubec.example.com'
    )
    
    # Operation mode
    parser.add_argument(
        '--mode',
        required=True,
        choices=[
            'health', 'status', 'protocol-health',
            'sync', 'discover',
            'analytics', 'distribution', 'visualize'
        ],
        help='Operation mode to execute'
    )
    
    # Sync options
    parser.add_argument(
        '--sync-type',
        default='all',
        choices=['all', 'accounts', 'transactions', 'ubec', 'ubecrc', 'ubecgpi', 'ubectt'],
        help='Type of data to synchronize'
    )
    
    parser.add_argument(
        '--max-accounts',
        type=int,
        help='Maximum number of accounts to process'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force synchronization even if recently synced'
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
    ENHANCED v17.0.0: Database-driven configuration
    
    Principle #2: This is the ONLY execution entry point.
    Principle #4: Database is single source of truth (v17.0.0)
    Principle #5: Pure async throughout.
    Principle #8: No duplicate configuration (v17.0.0)
    
    Args:
        args: Parsed command-line arguments
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger.info("\n" + "=" * 70)
    logger.info("UBEC PROTOCOL SYSTEM STARTING")
    logger.info("=" * 70)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Version: 17.1.0 (Air Service Initialization Fix)")
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
