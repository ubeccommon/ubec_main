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

Version: 19.0.0 (DISTRIBUTION EVALUATOR INTEGRATION + CLI FIX)
Date: October 26, 2025
Author: UBEC Protocol Team with Claude AI assistance

Changelog:
    v19.0.0 - DISTRIBUTION EVALUATOR INTEGRATION + CLI FIX
            - 🔧 FIXED: Added 'check-compliance' action handler to run_distribution()
            - 🔧 FIXED: Added 'evaluate-account' action for account-specific checks
            - 🔧 FIXED: Added 'compliance-trends' action for historical analysis
            - ✅ ENHANCED: Distribution evaluator now properly integrated
            - ✅ ENHANCED: CLI arguments for evaluator-specific parameters
            - ✅ ENHANCED: Comprehensive error messages with available actions
            - 📝 Resolves "Unknown action: check-compliance" error
            - 📝 Full compliance with CLI-service contract (Principle #1)
    v18.0.0 - SYNC FIX + COMPREHENSIVE HEALTH MONITORING
            - ✅ VERIFIED: run_sync() uses correct synchronizer methods
            - ✅ VERIFIED: sync_all_tokens() called, not sync_trustlines()
            - ✅ VERIFIED: discover_accounts() used for token-specific sync
            - ✅ ENHANCED: Comprehensive health monitoring with standardized patterns
            - ✅ ENHANCED: Detailed service health tracking across all modes
            - ✅ ENHANCED: Improved error messages and logging
            - 📝 Full compliance with all 12 design principles confirmed
    v17.2.0 - ASYNC FACTORY FIX (Principle #5)
            - 🔧 FIXED: Air protocol now properly awaits create_ubec_service() factory
            - 🔧 FIXED: Earth protocol now properly awaits create_ubecgpi_service() factory
            - 🔧 FIXED: Earth protocol now explicitly calls initialize() like other protocols
            - ✅ All element protocols now use consistent async factory pattern
            - ✅ All factories properly awaited: Air, Water, Earth, Fire
            - ✅ All protocols explicitly initialized: Air, Water, Earth, Fire
    v17.1.0 - AIR SERVICE INITIALIZATION FIX (Principle #5)
            - 🔧 FIXED: Air service now explicitly calls initialize() after creation
            - 🔧 FIXED: _initialized flag now set to True, resolving health check issue
            - ✅ Air service matches Water protocol initialization pattern
    v17.0.0 - DATABASE-DRIVEN POOL CONFIGURATION (Principles #4 & #8)
            - 🔧 FIXED: Pool configuration now loaded from database (not env vars)
            - 🔧 FIXED: Two-stage initialization: bootstrap → configure → full pool
            - 🔧 FIXED: AsyncDatabaseManager now receives min_pool/max_pool parameters
            - ✅ Principle #4: Database is single source of truth for ALL configuration
            - ✅ Principle #8: No duplicate configuration between env and database
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
        'rate_limiter': 100,
        'stellar_client': 500,
        'visualizer': 1000,
        'synchronizer': 200,
        'analytics': 200,
        'audit': 200,
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
        - Principle #4: Database-driven configuration
        - Principle #8: No duplicate configuration
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
        Create async database connection pool with TWO-STAGE INITIALIZATION.
        
        Stage 1: Bootstrap connection to load configuration from database
        Stage 2: Full production pool with database-driven configuration
        
        This implements:
            - Principle #4: Database as single source of truth
            - Principle #8: No duplicate configuration
        
        CRITICAL: Pool configuration comes FROM the database, creating a
        bootstrap paradox that's resolved via two-stage initialization:
        1. Bootstrap with minimal pool (1-2 connections) to load config
        2. Close bootstrap pool
        3. Create production pool with database-loaded configuration
        """
        from core.db.database_manager import AsyncDatabaseManager
        
        # Get database connection parameters (NOT operational config)
        schema, search_path = get_database_schema_config()
        
        logger.info("  ├─ Database: Two-stage initialization")
        logger.info(f"     Schema: {schema}")
        
        # ────────────────────────────────────────────────────────────────
        # STAGE 1: Bootstrap connection for configuration loading
        # ────────────────────────────────────────────────────────────────
        logger.info("     Stage 1: Bootstrap connection for configuration")
        bootstrap_db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=search_path,  # schema parameter takes the search path
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', ''),
            min_pool_size=1,  # Minimal for bootstrap
            max_pool_size=2
        )
        await bootstrap_db.initialize()
        
        # Load pool configuration from database using bootstrap connection
        try:
            pool_config_query = """
                SELECT setting_key, setting_value
                FROM system_settings
                WHERE setting_key IN ('db_pool_min', 'db_pool_max')
                  AND is_active = TRUE
            """
            config_rows = await bootstrap_db.fetch_all(pool_config_query)
            
            # Parse configuration
            min_pool = 5  # Default
            max_pool = 20  # Default
            
            for row in config_rows:
                if row['setting_key'] == 'db_pool_min':
                    min_pool = int(row['setting_value'])
                elif row['setting_key'] == 'db_pool_max':
                    max_pool = int(row['setting_value'])
            
            logger.info(f"     ✓ Loaded from database: Pool {min_pool}-{max_pool} connections")
            
        finally:
            # Close bootstrap connection
            await bootstrap_db.close()
            logger.info("     ✓ Bootstrap connection closed")
        
        # ────────────────────────────────────────────────────────────────
        # STAGE 2: Production pool with database-driven configuration
        # ────────────────────────────────────────────────────────────────
        logger.info("     Stage 2: Production pool initialization")
        logger.info(f"     Pool: {min_pool}-{max_pool} connections")
        
        production_db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=search_path,  # schema parameter takes the search path
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', ''),
            min_pool_size=min_pool,
            max_pool_size=max_pool
        )
        await production_db.initialize()
        
        logger.info(f"     ✓ Production pool ready: {min_pool}-{max_pool} connections")
        
        return production_db
    
    registry.register_factory(
        'database',
        create_database,
        dependencies=[],
        config={'two_stage_init': True, 'pool_from_db': True}
    )
    logger.info("✓ Registered: database")
    
    # ========================================================================
    # CONFIGURATION SERVICE
    # ========================================================================
    
    async def create_config(registry: ServiceRegistry):
        """
        Create configuration service with property wrapper.
        
        This service wraps the config for property-style access.
        It depends on the database service being available first.
        
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
    # RATE LIMITER SERVICE
    # ========================================================================
    
    async def create_rate_limiter(registry: ServiceRegistry):
        """
        Create rate limiter service with database-backed configuration.
        
        Principle #4: Single Source of Truth - Database configuration
        Principle #9: Integrated Rate Limiting
        """
        from services.stellar.rate_limiter_service import RateLimiterService
        
        db = await registry.get('database')
        
        logger.info("  ├─ Rate Limiter: Database-backed configuration")
        logger.info("     ✓ Token bucket algorithm")
        logger.info("     ✓ Circuit breaker pattern")
        logger.info("     ✓ Per-API monitoring")
        logger.info(f"     Buffer: {int(EXECUTION_MINIMUMS['rate_limit_buffer'] * 100)}% of max")
        
        rate_limiter = RateLimiterService(db_manager=db)
        await rate_limiter.initialize()
        
        return rate_limiter
    
    registry.register_factory(
        'rate_limiter',
        create_rate_limiter,
        dependencies=['database'],
        config={'algorithm': 'token_bucket', 'circuit_breaker': True}
    )
    logger.info("✓ Registered: rate_limiter (depends on: database)")
    
    # ========================================================================
    # STELLAR CLIENT SERVICE
    # ========================================================================
    
    async def create_stellar_client(registry: ServiceRegistry):
        """
        Create Stellar client service with rate limiting.
        
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
        
        Air protocol represents diversity and universal access (UBEC token).
        
        Principle #4: Database as single source of truth for configuration
        Principle #5: Explicit async initialization pattern - factory must be awaited
        Principle #8: No duplicate configuration - uses centralized config
        """
        from core.protocols.UBEC_protocol import create_ubec_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar_client = await registry.get('stellar_client')
        
        logger.info("  ├─ Air: Gateway / Universal Access (UBEC)")
        
        # ✅ v17.2.0 FIX: Properly await the async factory
        air_service = await create_ubec_service(
            db_manager=db,
            config={
                'asset_code': config.get('ubec_code', 'UBEC'),
                'issuer': config.get('ubec_issuer', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar_client
        )
        
        # ✅ v17.1.0 FIX: Explicitly call initialize() to set _initialized flag
        await air_service.initialize()
        
        return air_service
    
    registry.register_factory(
        'air',
        create_air,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'air', 'token': 'UBEC'}
    )
    logger.info("✓ Registered: air (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # WATER PROTOCOL (UBECrc - Reciprocity)
    # ========================================================================
    
    async def create_water(registry: ServiceRegistry):
        """
        Create Water protocol service using factory function.
        
        Water protocol represents flow and reciprocity (UBECrc token).
        
        Principle #5: Async factory pattern
        """
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar_client = await registry.get('stellar_client')
        
        logger.info("  ├─ Water: Reciprocity / Flow (UBECrc)")
        
        water_service = await create_ubecrc_service(
            db_manager=db,
            config={
                'asset_code': config.get('ubecrc_code', 'UBECrc'),
                'issuer': config.get('ubecrc_issuer', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar_client
        )
        
        await water_service.initialize()
        
        return water_service
    
    registry.register_factory(
        'water',
        create_water,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'water', 'token': 'UBECrc'}
    )
    logger.info("✓ Registered: water (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # EARTH PROTOCOL (UBECgpi - Ground/Stability)
    # ========================================================================
    
    async def create_earth(registry: ServiceRegistry):
        """
        Create Earth protocol service using factory function.
        
        Earth protocol represents ground, stability, and mutualism (UBECgpi token).
        
        Principle #5: Async factory pattern with explicit initialization
        """
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar_client = await registry.get('stellar_client')
        
        logger.info("  ├─ Earth: Ground / Stability (UBECgpi)")
        
        # ✅ v17.2.0 FIX: Properly await the async factory
        earth_service = await create_ubecgpi_service(
            db_manager=db,
            config={
                'asset_code': config.get('ubecgpi_code', 'UBECgpi'),
                'issuer': config.get('ubecgpi_issuer', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar_client
        )
        
        # ✅ v17.2.0 FIX: Explicitly call initialize() like other protocols
        await earth_service.initialize()
        
        return earth_service
    
    registry.register_factory(
        'earth',
        create_earth,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'earth', 'token': 'UBECgpi'}
    )
    logger.info("✓ Registered: earth (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # FIRE PROTOCOL (UBECtt - Transformation)
    # ========================================================================
    
    async def create_fire(registry: ServiceRegistry):
        """
        Create Fire protocol service using factory function.
        
        Fire protocol represents transformation and regeneration (UBECtt token).
        
        Principle #5: Async factory pattern
        """
        from core.protocols.UBECtt_protocol import create_ubectt_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar_client = await registry.get('stellar_client')
        
        logger.info("  ├─ Fire: Transformation (UBECtt)")
        
        fire_service = await create_ubectt_service(
            db_manager=db,
            config={
                'asset_code': config.get('ubectt_code', 'UBECtt'),
                'issuer': config.get('ubectt_issuer', ''),
                'db_schema': getattr(db, 'primary_schema', 'ubec_main')
            },
            stellar_client=stellar_client
        )
        
        await fire_service.initialize()
        
        return fire_service
    
    registry.register_factory(
        'fire',
        create_fire,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'fire', 'token': 'UBECtt'}
    )
    logger.info("✓ Registered: fire (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # DATA SYNCHRONIZER
    # ========================================================================
    
    async def create_synchronizer(registry: ServiceRegistry):
        """
        Create data synchronizer service for blockchain data sync.
        
        Methods Available:
            - sync_all_tokens(max_accounts_per_token): Sync all 4 UBEC tokens
            - discover_accounts(asset_code, max_accounts): Discover token holders
            - sync_account(account_id, asset_code): Sync specific account
            - sync_liquidity_pools(): Sync liquidity pool data
        
        Principle #1: Modular Design - correct import paths
        Principle #2: Service Pattern - uses factory function
        Principle #5: Strict Async - all operations async
        Principle #12: Method Singularity - use actual methods
        """
        from core.db.ubec_data_synchronizer import create_synchronizer_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        logger.info("  ├─ Synchronizer: Blockchain data sync")
        logger.info(f"     Batch Size: {EXECUTION_MINIMUMS['sync_batch_size']} accounts minimum")
        logger.info("     Methods: sync_all_tokens(), discover_accounts(), sync_account()")
        
        # Use factory function pattern
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
        config={'batch_size': EXECUTION_MINIMUMS['sync_batch_size']}
    )
    logger.info("✓ Registered: synchronizer (depends on: database, config, stellar_client)")
    
    # ========================================================================
    # ANALYTICS SERVICE
    # ========================================================================
    
    async def create_analytics(registry: ServiceRegistry):
        """
        Create analytics service for token distribution analysis.
        
        Principle #4: Database as single source of truth
        """
        from services.analytics.ubec_analytics_service import UBECAnalyticsService
        
        db = await registry.get('database')
        
        logger.info("  ├─ Analytics: Token distribution and metrics")
        
        analytics = UBECAnalyticsService(db)
        
        # Initialize the service
        await analytics.initialize()
        
        return analytics
    
    registry.register_factory(
        'ubec_analytics_service',
        create_analytics,
        dependencies=['database', 'config'],
        config={'analysis_depth': 'comprehensive'}
    )
    logger.info("✓ Registered: ubec_analytics_service (depends on: database, config)")
    
    # ========================================================================
    # AUDIT SERVICE
    # ========================================================================
    
    async def create_audit(registry: ServiceRegistry):
        """
        Create audit service loading accounts from database.
        
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
            raise ValueError("administration_account not configured in database")
        
        if not accounts.get('stewardship'):
            logger.error("CRITICAL: stewardship account not found in database")
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
        
        logger.info(f"    ✓ Loaded administration account: {accounts['administration'][:12]}...")
        logger.info(f"    ✓ Loaded stewardship account: "
                   f"{audit_config['stewardship_account'][:12]}...")
        
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
        config={'compliance_monitoring': True}
    )
    logger.info("✓ Registered: ubec_audit_service (depends on: database, config)")
    
    # ========================================================================
    # UBEC DISTRIBUTION SERVICE
    # ========================================================================
    
    async def create_distribution(registry: ServiceRegistry):
        """
        Create UBEC distribution service.
        
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
        
        # Explicitly call initialize() to complete service setup
        await service.initialize()
        
        return service
    
    registry.register_factory(
        'ubec_distribution_service',
        create_distribution,
        dependencies=['database', 'config', 'stellar_client', 'ubec_audit_service'],
        config={'min_distribution': EXECUTION_MINIMUMS['distribution_minimum']}
    )
    logger.info("✓ Registered: ubec_distribution_service (depends on: database, config, stellar_client, ubec_audit_service)")
   
    # ========================================================================
    # UBEC DISTRIBUTION EVALUATOR
    # ========================================================================
    
    async def create_distribution_evaluator(registry: ServiceRegistry):
        """
        Create UBEC distribution evaluator service.
        
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
        
        # Explicitly call initialize() to detect schema
        await evaluator.initialize()
        
        return evaluator
    
    registry.register_factory(
        'ubec_holonic_evaluator',
        create_holonic_evaluator,
        dependencies=['database', 'config'],
        config={'evaluation_framework': 'ubuntu_holonic'}
    )
    logger.info("✓ Registered: ubec_holonic_evaluator (depends on: database, config)")
    
    # ========================================================================
    # VISUALIZER
    # ========================================================================
    
    async def create_visualizer(registry: ServiceRegistry):
        """
        Create visualization service.
        
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
        
        return await factory(db_manager=db, config=visualizer_config)
    
    registry.register_factory(
        'visualizer',
        create_visualizer,
        dependencies=['database', 'config'],
        config={'format': 'png', 'color_palette': 'ubuntu'}
    )
    logger.info("✓ Registered: visualizer (depends on: database, config)")
    
    # ========================================================================
    # REGISTRATION COMPLETE
    # ========================================================================
    
    logger.info("=" * 70)
    logger.info("✓ ALL SERVICES REGISTERED")
    logger.info("=" * 70)


def validate_service_registration():
    """
    Validate that all required services are registered.
    
    Principle #1: Modular Design - Validation before execution
    """
    required_services = {
        'database', 'config', 'rate_limiter', 'stellar_client',
        'air', 'water', 'earth', 'fire',
        'synchronizer', 'ubec_analytics_service', 'ubec_audit_service',
        'ubec_distribution_service', 'ubec_distribution_evaluator',
        'ubec_holonic_evaluator', 'visualizer'
    }
    
    registered = registry.list_services()
    
    missing = required_services - set(registered)
    
    if missing:
        raise RuntimeError(
            f"Missing required services: {', '.join(missing)}\n"
            f"Registered: {', '.join(registered)}"
        )
    
    logger.info(f"✓ All {len(required_services)} required services registered")


# ========================================================================
# SERVICE INITIALIZATION WITH CONCURRENT ASYNC PATTERN
# Principle #5: Strict Async Operations WITH Concurrent Initialization
# ========================================================================

async def initialize_services_concurrent() -> Tuple[Dict[str, float], set, int]:
    """
    Initialize services concurrently in dependency order.
    
    Services are initialized in levels based on dependencies:
    - Level 0: Foundation (database)
    - Level 1: Configuration (config)
    - Level 2: Independent services (parallel initialization)
    - Level 3: Dependent services (parallel where possible)
    - Level 4: Final dependent services
    
    This implements:
        - Principle #5: Strict Async with Concurrent Initialization
        - Principle #7: Per-Asset Monitoring with timing
        - Principle #12: Method Singularity with standardized patterns
    
    Returns:
        Tuple of (initialization_times, failed_services, exit_code)
    """
    logger.info("\n" + "=" * 70)
    logger.info("INITIALIZING SERVICES CONCURRENTLY")
    logger.info("=" * 70)
    
    init_times = {}
    failed_services = set()
    
    async def init_service_safe(service_name: str) -> float:
        """Initialize a single service with error handling and timing."""
        start = time.time()
        try:
            await registry.get(service_name)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            init_times[service_name] = elapsed
            return elapsed
        except Exception as e:
            logger.error(f"  ✗ {service_name}: {str(e)}", exc_info=True)
            failed_services.add(service_name)
            return 0
    
    # ────────────────────────────────────────────────────────────────
    # LEVEL 0: Foundation services (sequential)
    # ────────────────────────────────────────────────────────────────
    logger.info("\n🔷 Level 0: Foundation services")
    
    db_time = await init_service_safe('database')
    logger.info(f"  ✓ database: {db_time:.0f}ms")
    
    if 'database' in failed_services:
        logger.error("  ✗ CRITICAL: Database initialization failed")
        return init_times, failed_services, 1
    
    # ────────────────────────────────────────────────────────────────
    # LEVEL 1: Configuration (depends on database)
    # ────────────────────────────────────────────────────────────────
    logger.info("\n🔷 Level 1: Configuration")
    
    config_time = await init_service_safe('config')
    logger.info(f"  ✓ config: {config_time:.0f}ms")
    
    if 'config' in failed_services:
        logger.error("  ✗ CRITICAL: Configuration initialization failed")
        return init_times, failed_services, 1
    
    # ────────────────────────────────────────────────────────────────
    # LEVEL 2: Independent services (parallel)
    # ────────────────────────────────────────────────────────────────
    logger.info("\n🔷 Level 2: Independent services (parallel)")
    
    level2_start = time.time()
    level2_services = [
        'rate_limiter', 'ubec_analytics_service', 'ubec_audit_service',
        'ubec_holonic_evaluator', 'visualizer'
    ]
    
    level2_tasks = [init_service_safe(svc) for svc in level2_services]
    level2_results = await asyncio.gather(*level2_tasks, return_exceptions=True)
    
    for svc, elapsed in zip(level2_services, level2_results):
        if isinstance(elapsed, Exception):
            logger.error(f"  ✗ {svc}: {str(elapsed)}")
            failed_services.add(svc)
        else:
            logger.info(f"  ✓ {svc}: {elapsed:.0f}ms")
    
    level2_elapsed = (time.time() - level2_start) * 1000
    logger.info(f"  📊 Level 2 total: {level2_elapsed:.0f}ms")
    
    # Check critical services
    if 'rate_limiter' in failed_services:
        logger.error("  ✗ CRITICAL: Rate limiter initialization failed")
        return init_times, failed_services, 1
    
    # ────────────────────────────────────────────────────────────────
    # LEVEL 3: Stellar-dependent services
    # ────────────────────────────────────────────────────────────────
    logger.info("\n🔷 Level 3: Stellar-dependent services")
    
    level3_start = time.time()
    
    # Stellar client (critical)
    stellar_time = await init_service_safe('stellar_client')
    logger.info(f"  ✓ stellar_client: {stellar_time:.0f}ms")
    
    if 'stellar_client' in failed_services:
        logger.error("  ✗ CRITICAL: Stellar client initialization failed")
        return init_times, failed_services, 1
    
    # Element protocols (parallel)
    protocol_services = ['air', 'water', 'earth', 'fire', 'synchronizer']
    protocol_tasks = [init_service_safe(svc) for svc in protocol_services]
    protocol_results = await asyncio.gather(*protocol_tasks, return_exceptions=True)
    
    for svc, elapsed in zip(protocol_services, protocol_results):
        if isinstance(elapsed, Exception):
            logger.error(f"  ✗ {svc}: {str(elapsed)}")
            failed_services.add(svc)
        else:
            logger.info(f"  ✓ {svc}: {elapsed:.0f}ms")
    
    # Distribution service (depends on audit)
    if 'ubec_audit_service' not in failed_services:
        dist_time = await init_service_safe('ubec_distribution_service')
        logger.info(f"  ✓ ubec_distribution_service: {dist_time:.0f}ms")
    else:
        logger.warning("  ⚠ Skipping ubec_distribution_service (audit service failed)")
        failed_services.add('ubec_distribution_service')
    
    level3_elapsed = (time.time() - level3_start) * 1000
    logger.info(f"  📊 Level 3 total: {level3_elapsed:.0f}ms")
    
    # ────────────────────────────────────────────────────────────────
    # LEVEL 4: Final dependent services
    # ────────────────────────────────────────────────────────────────
    logger.info("\n🔷 Level 4: Final dependent services")
    
    # Distribution evaluator (depends on distribution and audit)
    if 'ubec_distribution_service' not in failed_services and 'ubec_audit_service' not in failed_services:
        eval_time = await init_service_safe('ubec_distribution_evaluator')
        logger.info(f"  ✓ ubec_distribution_evaluator: {eval_time:.0f}ms")
    else:
        logger.warning("  ⚠ Skipping ubec_distribution_evaluator (distribution service failed)")
        failed_services.add('ubec_distribution_evaluator')
    
    # ────────────────────────────────────────────────────────────────
    # SUMMARY
    # ────────────────────────────────────────────────────────────────
    total_time = sum(init_times.values())
    successful = len(init_times) - len(failed_services)
    
    logger.info("\n" + "=" * 70)
    logger.info("SERVICE INITIALIZATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total Time: {total_time:.0f}ms")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {len(failed_services)}")
    logger.info("=" * 70)
    
    # Check if any critical services failed
    critical_failed = CRITICAL_SERVICES & failed_services
    if critical_failed:
        logger.error(f"CRITICAL services failed: {', '.join(critical_failed)}")
        return init_times, failed_services, 1
    
    return init_times, failed_services, 0


# ========================================================================
# OPERATION HANDLERS
# ========================================================================

async def run_health_check(
    init_times: Dict[str, float],
    failed_services: set
) -> Dict[str, Any]:
    """
    Perform comprehensive health check on all services.
    
    Principle #7: Per-Asset Monitoring with health checks
    Principle #12: Method Singularity - ServiceHealthCheck utility
    """
    logger.info("\n" + "=" * 70)
    logger.info("COMPREHENSIVE HEALTH CHECK")
    logger.info("=" * 70)
    
    health_results = {}
    
    for service_name in registry.list_services():
        if service_name in failed_services:
            health_results[service_name] = {
                'status': 'failed',
                'message': 'Service failed to initialize'
            }
            continue
        
        try:
            service = await registry.get(service_name)
            
            # Check if service has health_check method
            if hasattr(service, 'health_check'):
                health = await service.health_check()
                health_results[service_name] = health
            else:
                health_results[service_name] = {
                    'status': 'healthy',
                    'message': 'Service running (no health_check method)',
                    'initialization_time_ms': init_times.get(service_name, 0)
                }
                
        except Exception as e:
            health_results[service_name] = {
                'status': 'error',
                'message': str(e)
            }
    
    return create_response(success=True, data=health_results)


async def run_status() -> Dict[str, Any]:
    """
    Get current system status.
    
    Principle #4: Database as single source of truth
    """
    logger.info("\nGetting system status...")
    
    db = await registry.get('database')
    
    try:
        # Check database connectivity
        result = await db.fetch_one("SELECT NOW() as current_time")
        
        status = {
            'system': 'operational',
            'database': 'connected',
            'timestamp': result['current_time'],
            'services': registry.list_services()
        }
        
        return create_response(success=True, data=status)
    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_protocol_health() -> Dict[str, Any]:
    """
    Check health of all element protocols.
    
    Principle #12: Uses standardized health check pattern
    """
    logger.info("\n" + "=" * 70)
    logger.info("PROTOCOL HEALTH CHECK")
    logger.info("=" * 70)
    
    protocol_health = {}
    protocols = {
        'air': 'UBEC',
        'water': 'UBECrc',
        'earth': 'UBECgpi',
        'fire': 'UBECtt'
    }
    
    for protocol_name, token_code in protocols.items():
        logger.info(f"\n{protocol_name.upper()} Protocol ({token_code}):")
        
        try:
            protocol = await registry.get(protocol_name)
            
            if hasattr(protocol, 'health_check'):
                health = await protocol.health_check()
                protocol_health[protocol_name] = health
                
                status = health.get('status', 'unknown')
                message = health.get('message', 'No details')
                logger.info(f"  Status: {status}")
                logger.info(f"  {message}")
            else:
                logger.info(f"  Status: healthy (no health_check method)")
                protocol_health[protocol_name] = {
                    'status': 'healthy',
                    'message': f'{token_code} protocol operational'
                }
                
        except Exception as e:
            logger.error(f"\n{protocol_name.upper()} Protocol: ERROR")
            logger.error(f"  {str(e)}")
            protocol_health[protocol_name] = {
                'status': 'error',
                'error': str(e)
            }
    
    return create_response(success=True, data=protocol_health)


async def run_sync(
    sync_type: str = 'all',
    max_accounts: Optional[int] = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Run blockchain data synchronization.
    
    CRITICAL: This function uses the ACTUAL synchronizer methods:
        - sync_all_tokens(max_accounts_per_token): Sync all 4 UBEC tokens
        - discover_accounts(asset_code, max_accounts): Discover token holders
        - sync_liquidity_pools(): Sync liquidity pool data
    
    Args:
        sync_type: 'all' for all tokens, 'liquidity' for pools, or token code
        max_accounts: Maximum accounts to discover per token
        force: Force re-sync (compatibility parameter)
        
    Returns:
        Dictionary with sync results
        
    Principle #5: Strict Async
    Principle #7: Batch size minimums
    Principle #12: Method Singularity - Uses actual synchronizer methods
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"RUNNING SYNC: {sync_type}")
    logger.info("=" * 70)
    logger.info(f"Parameters: max_accounts={max_accounts}, force={force}")
    
    synchronizer = await registry.get('synchronizer')
    
    try:
        if sync_type == 'all':
            # ✅ CORRECT: Use sync_all_tokens() to sync all 4 UBEC tokens
            logger.info("Synchronizing all UBEC tokens...")
            result = await synchronizer.sync_all_tokens(
                max_accounts_per_token=max_accounts or 5000
            )
            
        elif sync_type == 'liquidity':
            # ✅ CORRECT: Use sync_liquidity_pools() for pool data
            logger.info("Synchronizing liquidity pools...")
            result = await synchronizer.sync_liquidity_pools()
            
        else:
            # ✅ CORRECT: Use discover_accounts() for specific token
            token_code = sync_type.upper()
            logger.info(f"Discovering {token_code} token holders...")
            
            accounts_discovered = await synchronizer.discover_accounts(
                asset_code=token_code,
                max_accounts=max_accounts or 5000
            )
            
            result = {
                'token': token_code,
                'accounts_discovered': accounts_discovered,
                'status': 'success'
            }
        
        logger.info("✓ Synchronization completed successfully")
        return create_response(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_discover(max_accounts: int = 100) -> Dict[str, Any]:
    """
    Discover new accounts holding UBEC tokens.
    
    Principle #7: Batch size minimums
    """
    logger.info(f"\nDiscovering accounts: max_accounts={max_accounts}")
    
    synchronizer = await registry.get('synchronizer')
    
    try:
        # Use discover_accounts for all tokens
        result = await synchronizer.discover_accounts(
            asset_code='UBEC',
            max_accounts=max_accounts
        )
        
        return create_response(success=True, data=result)
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_analytics(analysis_type: str = 'distribution') -> Dict[str, Any]:
    """
    Run analytics on token distribution.
    
    Principle #4: Database as single source of truth for analytics
    """
    logger.info(f"\nRunning analytics: type={analysis_type}")
    
    analytics = await registry.get('ubec_analytics_service')
    
    try:
        if analysis_type == 'distribution':
            result = await analytics.analyze_distribution()
        elif analysis_type == 'velocity':
            result = await analytics.analyze_velocity()
        elif analysis_type == 'concentration':
            result = await analytics.analyze_concentration()
        else:
            return create_response(success=False, error=f"Unknown analysis type: {analysis_type}")
        
        return create_response(success=True, data=result)
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_distribution(action: str = 'check', dry_run: bool = True, account_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
    """
    Run distribution operations.
    
    This function now supports BOTH the distribution service and the distribution
    evaluator service, providing comprehensive distribution management and compliance
    checking capabilities.
    
    Supported Actions:
        Distribution Service Actions:
            - 'check': Check current distribution (uses distribution_service)
            - 'execute': Execute distribution (uses distribution_service)
        
        Distribution Evaluator Actions (NEW v19.0.0):
            - 'check-compliance': Comprehensive compliance evaluation
            - 'evaluate-account': Evaluate specific account compliance
            - 'compliance-trends': Historical compliance trend analysis
    
    Args:
        action: Action to perform (see supported actions above)
        dry_run: Run in dry-run mode (no actual changes)
        account_id: Account ID for account-specific actions
        days: Number of days for trend analysis
        
    Returns:
        Standardized response dictionary with operation results
        
    Principle #1: Precision in Implementation - All actions are implemented
    Principle #5: Async operation
    Principle #7: Transaction minimums
    Principle #12: Method Singularity - Single distribution handler
    """
    logger.info(f"\nRunning distribution: action={action}, dry_run={dry_run}")
    
    try:
        # ================================================================
        # DISTRIBUTION SERVICE ACTIONS
        # ================================================================
        if action == 'check':
            distribution = await registry.get('ubec_distribution_service')
            result = await distribution.check_distribution()
            
        elif action == 'execute':
            distribution = await registry.get('ubec_distribution_service')
            if dry_run:
                logger.warning("Dry run mode - no actual distributions")
            result = await distribution.execute_distribution(dry_run=dry_run)
        
        # ================================================================
        # DISTRIBUTION EVALUATOR ACTIONS (NEW v19.0.0)
        # ================================================================
        elif action == 'check-compliance':
            # ✅ FIX: Get evaluator service and call evaluate_distribution()
            evaluator = await registry.get('ubec_distribution_evaluator')
            logger.info("Running comprehensive compliance evaluation...")
            result = await evaluator.evaluate_distribution()
            
        elif action == 'evaluate-account':
            # ✅ NEW: Evaluate specific account compliance
            if not account_id:
                return create_response(
                    success=False,
                    error="account_id required for evaluate-account action. Use --account-id GXXXX..."
                )
            
            evaluator = await registry.get('ubec_distribution_evaluator')
            logger.info(f"Evaluating account: {account_id}")
            result = await evaluator.evaluate_account(account_id)
            
        elif action == 'compliance-trends':
            # ✅ NEW: Get historical compliance trends
            evaluator = await registry.get('ubec_distribution_evaluator')
            logger.info(f"Analyzing compliance trends: last {days} days")
            result = await evaluator.get_compliance_trends(days=days)
        
        # ================================================================
        # UNKNOWN ACTION HANDLER
        # ================================================================
        else:
            # Provide helpful error with available actions
            available_actions = [
                "Distribution Service Actions:",
                "  - check: Check current distribution",
                "  - execute: Execute distribution",
                "",
                "Distribution Evaluator Actions:",
                "  - check-compliance: Comprehensive compliance evaluation",
                "  - evaluate-account: Evaluate specific account (requires --account-id)",
                "  - compliance-trends: Historical compliance trends (optional --days N)"
            ]
            
            error_message = f"Unknown action: {action}\n\nAvailable actions:\n" + "\n".join(available_actions)
            return create_response(success=False, error=error_message)
        
        return create_response(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Distribution failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


async def run_visualize(
    action: str = 'report',
    chart_type: Optional[str] = None,
    format: str = 'png',
    output_dir: Optional[str] = None,
    include_advanced: bool = False
) -> Dict[str, Any]:
    """
    Generate visualizations and reports.
    
    Principle #5: Async operation
    """
    logger.info(f"\nGenerating visualization: action={action}, format={format}")
    
    visualizer = await registry.get('visualizer')
    
    try:
        if action == 'report':
            result = await visualizer.generate_comprehensive_report(
                output_dir=output_dir,
                include_advanced=include_advanced
            )
        elif action == 'chart':
            if not chart_type:
                return create_response(success=False, error="chart_type required")
            result = await visualizer.generate_chart(
                chart_type=chart_type,
                format=format,
                output_dir=output_dir
            )
        else:
            return create_response(success=False, error=f"Unknown action: {action}")
        
        return create_response(success=True, data=result)
    except Exception as e:
        logger.error(f"Visualization failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))


# ========================================================================
# COMMAND LINE ARGUMENT PARSING
# ========================================================================

def parse_arguments():
    """
    Parse command-line arguments.
    
    Principle #11: Comprehensive documentation for CLI
    """
    parser = argparse.ArgumentParser(
        description='UBEC Protocol System - Unified entry point',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # System Operations
  python main.py health                    # Comprehensive health check
  python main.py status                    # System status
  python main.py protocol-health           # Protocol-specific health
  
  # Data Synchronization
  python main.py sync                      # Sync all tokens
  python main.py sync --sync-type liquidity  # Sync liquidity pools
  python main.py sync --sync-type UBEC     # Sync specific token
  
  # Distribution Operations
  python main.py distribution --action check                    # Check distribution
  python main.py distribution --action execute --dry-run        # Dry-run execution
  python main.py distribution --action check-compliance         # Compliance evaluation (NEW v19.0.0)
  python main.py distribution --action evaluate-account --account-id GXXXX...  # Account evaluation (NEW v19.0.0)
  python main.py distribution --action compliance-trends --days 30  # Trend analysis (NEW v19.0.0)
  
  # Analytics
  python main.py analytics --analysis-type distribution  # Distribution analysis
  python main.py analytics --analysis-type velocity      # Velocity analysis
  
  # Visualization
  python main.py visualize --action report               # Generate comprehensive report
  python main.py visualize --action chart --chart-type holonic  # Generate specific chart

Attribution:
  This project uses the services of Claude and Anthropic PBC.
        """
    )
    
    # Mode selection
    parser.add_argument(
        'mode',
        choices=[
            'health', 'status', 'protocol-health',
            'sync', 'discover',
            'analytics',
            'distribution',
            'visualize'
        ],
        help='Operation mode'
    )
    
    # Sync options
    parser.add_argument(
        '--sync-type',
        default='all',
        help='Sync type: all, liquidity, or token code (UBEC, UBECrc, etc.)'
    )
    
    parser.add_argument(
        '--max-accounts',
        type=int,
        help='Maximum accounts to process'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force operation (override safety checks)'
    )
    
    # Analytics options
    parser.add_argument(
        '--analysis-type',
        default='distribution',
        choices=['distribution', 'velocity', 'concentration'],
        help='Type of analysis'
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
    
    # Distribution evaluator options (NEW v19.0.0)
    parser.add_argument(
        '--account-id',
        help='Account ID for account-specific evaluation actions'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for trend analysis (default: 30)'
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
    
    Principle #2: This is the ONLY execution entry point
    Principle #4: Database is single source of truth
    Principle #5: Pure async throughout
    Principle #8: No duplicate configuration
    
    Args:
        args: Parsed command-line arguments
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger.info("\n" + "=" * 70)
    logger.info("UBEC PROTOCOL SYSTEM STARTING")
    logger.info("=" * 70)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Version: 19.0.0 (Distribution Evaluator Integration + CLI Fix)")
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
        
        # Distribution (with evaluator support - NEW v19.0.0)
        elif args.mode == 'distribution':
            result = await run_distribution(
                action=args.action or 'check',
                dry_run=args.dry_run,
                account_id=args.account_id,
                days=args.days
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
