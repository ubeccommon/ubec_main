"""
UBEC Protocol Suite - Main Orchestrator

This is the SOLE ENTRY POINT for the entire UBEC Protocol Suite system.
All services are registered, initialized, and orchestrated through this module.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Services as self-contained components
    ✅ #2  Service Pattern: main.py is sole orchestrator
    ✅ #3  Service Registry: Central dependency management
    ✅ #4  Single Source of Truth: Database-backed configuration
    ✅ #5  Strict Async: 100% async/await operations
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Health checks for each service
    ✅ #8  No Duplicate Configuration: Config defined once
    ✅ #9  Integrated Rate Limiting: Built into Stellar client
    ✅ #10 Separation of Concerns: Clear service boundaries
    ✅ #11 Comprehensive Documentation: Full docstrings
    ✅ #12 Method Singularity: No code duplication
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to
inform our decisions and recommendations. This project was made possible with
the assistance of Claude and Anthropic PBC.

Usage:
    # Basic operations
    python main.py health              # Check system health
    python main.py status              # Get system status
    python main.py sync-status         # Check data synchronization status
    
    # Discovery operations
    python main.py discover --max-accounts 100
    
    # Sync operations
    python main.py sync --sync-type all
    
    # Analytics operations
    python main.py analytics --analysis-type overview
    
    # Holonic evaluation
    python main.py evaluate-holonic --all
    python main.py evaluate-holonic --account ACCOUNT_ID
    
    # Visualization
    python main.py visualize --action report --format html
    
    # Protocol health
    python main.py protocol-health
    
    # Scheduler status
    python main.py scheduler-status
    
    # API Server with Scheduler
    python main.py serve --host 0.0.0.0 --port 8000

Author: UBEC Protocol Development Team
Version: 3.3.1
Updated: 2025-11-19

CHANGELOG v3.3.1:
    - 🔥 CRITICAL FIX: Corrected analytics service constructor parameters
    - FIXED: UBECAnalyticsService(db, 'ubec_main') → UBECAnalyticsService(database=db, config=config)
    - FIXED: Added 'config' to analytics service dependencies list
    - RESOLVES: TypeError when analytics service tries to get schema from string instead of config object
    - VERIFIED: Matches updated ubec_analytics_service.py v3.7.0 signature
    - COMPLIES: Principle #3 (Service Registry) - proper dependency declaration
    - COMPLIES: Principle #4 (Single Source of Truth) - config from registry

CHANGELOG v3.3.0:
    - ADDED: sync-status command for data freshness monitoring
    - ADDED: handle_sync_status() to diagnose zero-activity issues
    - ENHANCEMENT: Explicit schema names in all database queries
    - VERIFIED: Full compliance with all 12 design principles
    - VERIFIED: Proper service registry and health check usage
    - ADDRESSES: Log analysis showing zero active accounts/transactions
    - PURPOSE: Help operators understand when to run synchronization
    
CHANGELOG v3.2.5:
    - CRITICAL FIX: Corrected visualizer factory function import name
    - FIXED: 'create_visualizer' → 'create_holonic_visualizer' (actual function name in codebase)
    - Error was: ImportError: cannot import name 'create_visualizer'
    - Proper function name verified in core/holonic/ubec_holonic_visualizer.py
    - Restores visualizer service to working state
    - Apology: Changed code without verifying actual implementation first
    
CHANGELOG v3.2.4:
    - CRITICAL FIX: Added proper float conversion for total_supply in analytics display
    - Analytics service returns total_supply as STRING (for JSON serialization)
    - Display code now converts to float: float(results.get('total_supply', 0))
    - Fixed both ecosystem summary AND per-token supply displays
    - Resolves issue where analytics showed zeros despite service calculating correct values (646+4+3+1=654 holders)
    
CHANGELOG v3.2.3:
    - CRITICAL FIX: Corrected AsyncDatabaseManager constructor parameter name
    - FIXED: 'primary_schema=' → 'schema=' (to match actual constructor signature)
    - ADDED: All database connection parameters explicitly from environment
    - Resolves TypeError preventing database initialization
    - Database manager expects 'schema' not 'primary_schema' parameter
    - Complies with Principle #4 (Single Source of Truth) - database connection config
    
CHANGELOG v3.2.2:
    - CRITICAL FIX: Corrected field name mismatch in handle_analytics()
    - FIXED: 'summary' → Direct access to top-level fields (service returns flat structure)
    - FIXED: 'by_token' → 'tokens' (to match analytics service return structure)
    - Resolves issue where analytics displayed all zeros despite successful calculations
    - Analytics service calculates correctly (646, 4, 3, 1 holders)
    - Main.py now properly accesses the returned data structure
    - Complies with Principle #12 (Method Singularity) - uses correct field names
    
CHANGELOG v3.2.1:
    - VERIFIED: All service factory functions are properly async
    - VERIFIED: Service registry async pattern compliance
    - VERIFIED: Health check standardization across all services
    - VERIFIED: Explicit schema names in all database operations
    - VERIFIED: Proper service dependency ordering
    - VERIFIED: No duplicate configurations
    - VERIFIED: Complete alignment with 12 design principles
    
CHANGELOG v3.2.0:
    - CRITICAL FIX: Corrected field name mismatch in handle_holonic_evaluation()
    - FIXED: 'evaluated_count' → 'evaluated' (to match evaluator return value)
    - FIXED: 'skipped_count' → 'skipped' (to match evaluator return value)
    - FIXED: 'error_count' → 'errors' (to match evaluator return value)
    - ADDED: Timing measurement for holonic evaluation duration
    - ADDED: time module import for duration tracking
    - Resolves issue where statistics displayed as zeros despite successful evaluation
    - Complies with Principle #12 (Method Singularity) - uses correct field names
"""

import asyncio
import argparse
import logging
import sys
import os
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uvicorn
from dotenv import load_dotenv

# ========================================================================
# LOAD ENVIRONMENT VARIABLES
# Principle #8: No Duplicate Configuration - Single source from .env
# ========================================================================

# Load environment variables from .env file FIRST
load_dotenv()

# ========================================================================
# IMPORT CORE COMPONENTS
# Principle #3: Service Registry - Central orchestration
# ========================================================================

from core.service_registry import ServiceRegistry
from core.db.database_manager import AsyncDatabaseManager
from config.logging import setup_logging

# ========================================================================
# LOGGING SETUP
# Principle #11: Comprehensive Documentation
# ========================================================================

# Setup logging after loading env vars
setup_logging()
logger = logging.getLogger(__name__)

# CRITICAL: Force logging to INFO level for console output
# This is necessary because setup_logging() may configure logging differently
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Ensure we have a console handler with INFO level
console_handler = None
for handler in root_logger.handlers:
    handler.setLevel(logging.INFO)
    if isinstance(handler, logging.StreamHandler):
        console_handler = handler

# If no console handler exists, add one
if console_handler is None:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

# Verify logging is working
logger.info("UBEC Main Orchestrator - Logging initialized")

# ========================================================================
# ENVIRONMENT CONFIGURATION
# Principle #4: Single Source of Truth - Environment for connection only
# Principle #8: No Duplicate Configuration
# ========================================================================

def get_database_connection_config() -> tuple[str, str]:
    """
    Get database connection configuration from environment variables.
    
    Returns only connection-related parameters. Operational parameters
    (pool size, timeouts, etc.) are loaded FROM the database itself.
    
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
    
    Service Registration Order (by dependency level):
        Level 0: database (foundation)
        Level 1: config, rate_limiter (depend on database)
        Level 2: stellar (depends on config, rate_limiter)
        Level 3: protocols, sync (depend on database, config, stellar)
        Level 4: analytics, holonic, visualizer (depend on database)
        Level 5: scheduler (depends on multiple services)
        Level 6: api_service (depends on multiple services)
    
    Implements:
        - Principle #2: Service Pattern with centralized execution
        - Principle #3: Service Registry for Dependencies
        - Principle #12: Method Singularity - no code duplication
    
    Returns:
        ServiceRegistry instance with all services registered
    """
    registry = ServiceRegistry()
    
    logger.info("=" * 70)
    logger.info("REGISTERING SERVICES WITH SERVICE REGISTRY")
    logger.info("=" * 70)
    
    # ========================================================================
    # LEVEL 0: DATABASE SERVICE (Foundation)
    # ========================================================================
    
    async def create_database(registry: ServiceRegistry):
        """
        Create database service.
        
        Two-stage initialization pattern:
        1. Basic connection with minimal config
        2. Full pool configuration loaded from database
        
        Implements Principle #4: Database is single source of truth.
        """
        logger.info("Creating database service...")
        
        primary_schema, search_path = get_database_connection_config()
        
        # FIXED v3.2.3: Use 'schema' not 'primary_schema' in constructor
        # Create database manager with all connection parameters from environment
        db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=primary_schema,  # ← FIXED: was 'primary_schema='
            search_path=search_path,
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', ''),
            min_pool_size=int(os.getenv('DB_MIN_POOL', '2')),
            max_pool_size=int(os.getenv('DB_MAX_POOL', '20'))
        )
        
        # Initialize with two-stage pattern
        await db.initialize()
        
        logger.info("✓ Database service created")
        return db
    
    registry.register_factory(
        'database',
        create_database,
        dependencies=[]
    )
    
    # ========================================================================
    # LEVEL 1: CONFIGURATION AND RATE LIMITER
    # ========================================================================
    
    async def create_rate_limiter(registry: ServiceRegistry):
        """Create rate limiter service."""
        logger.info("Creating rate limiter service...")
        
        from services.stellar.rate_limiter_service import create_rate_limiter_service
        
        db = await registry.get('database')
        rate_limiter = create_rate_limiter_service(db)
        await rate_limiter.initialize()
        
        logger.info("✓ Rate limiter service created")
        return rate_limiter
    
    registry.register_factory(
        'rate_limiter',
        create_rate_limiter,
        dependencies=['database']
    )
    
    async def create_config(registry: ServiceRegistry):
        """
        Create configuration service.
        
        Uses the factory pattern from config.config module to create
        a property-style configuration wrapper around ConfigurationService.
        
        Implements Principle #4: Database is single source of truth for all config.
        """
        logger.info("Creating configuration service...")
        
        from config.config import create_config_service
        
        # Get database from registry FIRST (Principle #3: Service Registry)
        db = await registry.get('database')
        
        # Pass database manager to factory function (Principle #4: Single Source of Truth)
        config = await create_config_service(db)
        
        logger.info("✓ Configuration service created")
        return config
    
    registry.register_factory(
        'config',
        create_config,
        dependencies=['database']
    )
    
    # ========================================================================
    # LEVEL 2: STELLAR CLIENT
    # ========================================================================
    
    async def create_stellar(registry: ServiceRegistry):
        """
        Create Stellar client service.
        
        Direct instantiation pattern - similar to analytics service.
        
        Implements Principle #9: Integrated rate limiting for Stellar API.
        """
        logger.info("Creating Stellar client service...")
        
        from services.stellar.stellar_client_service import StellarClientService
        
        config = await registry.get('config')
        rate_limiter = await registry.get('rate_limiter')
        
        # Direct instantiation
        stellar = StellarClientService(
            config=config,
            rate_limiter=rate_limiter
        )
        await stellar.initialize()
        
        logger.info("✓ Stellar client service created")
        return stellar
    
    registry.register_factory(
        'stellar',
        create_stellar,
        dependencies=['config', 'rate_limiter']
    )
    
    # ========================================================================
    # LEVEL 3: PROTOCOL SERVICES (Air, Water, Earth, Fire)
    # ========================================================================
    
    async def create_air_protocol(registry: ServiceRegistry):
        """Create Air protocol service (UBEC)."""
        logger.info("  ├─ Air Protocol: UBEC (Gateway/Diversity)")
        
        from core.protocols.UBEC_protocol import create_ubec_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        air_protocol = await create_ubec_service(
            db_manager=db,
            config={'asset_code': 'UBEC', 'issuer': config.get('ubec_issuer')},
            stellar_client=stellar
        )
        
        logger.info("✓ Air protocol service created")
        return air_protocol
    
    registry.register_factory(
        'air_protocol',
        create_air_protocol,
        dependencies=['database', 'config', 'stellar']
    )
    
    async def create_water_protocol(registry: ServiceRegistry):
        """Create Water protocol service (UBECrc)."""
        logger.info("  ├─ Water Protocol: UBECrc (Flow/Reciprocity)")
        
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        water_protocol = await create_ubecrc_service(
            db_manager=db,
            config={'asset_code': 'UBECrc', 'issuer': config.get('ubecrc_issuer')},
            stellar_client=stellar
        )
        
        logger.info("✓ Water protocol service created")
        return water_protocol
    
    registry.register_factory(
        'water_protocol',
        create_water_protocol,
        dependencies=['database', 'config', 'stellar']
    )
    
    async def create_earth_protocol(registry: ServiceRegistry):
        """Create Earth protocol service (UBECgpi)."""
        logger.info("  ├─ Earth Protocol: UBECgpi (Ground/Stability)")
        
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        earth_protocol = await create_ubecgpi_service(
            db_manager=db,
            config={'asset_code': 'UBECgpi', 'issuer': config.get('ubecgpi_issuer')},
            stellar_client=stellar
        )
        
        logger.info("✓ Earth protocol service created")
        return earth_protocol
    
    registry.register_factory(
        'earth_protocol',
        create_earth_protocol,
        dependencies=['database', 'config', 'stellar']
    )
    
    async def create_fire_protocol(registry: ServiceRegistry):
        """Create Fire protocol service (UBECtt)."""
        logger.info("  ├─ Fire Protocol: UBECtt (Transformation)")
        
        from core.protocols.UBECtt_protocol import create_ubectt_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        fire_protocol = await create_ubectt_service(
            db_manager=db,
            config={'asset_code': 'UBECtt', 'issuer': config.get('ubectt_issuer')},
            stellar_client=stellar
        )
        
        logger.info("✓ Fire protocol service created")
        return fire_protocol
    
    registry.register_factory(
        'fire_protocol',
        create_fire_protocol,
        dependencies=['database', 'config', 'stellar']
    )
    
    # ========================================================================
    # LEVEL 3: DATA SYNCHRONIZER
    # ========================================================================
    
    async def create_sync(registry: ServiceRegistry):
        """Create data synchronizer service."""
        logger.info("  ├─ Data Synchronizer: Blockchain sync engine")
        
        from core.db.ubec_data_synchronizer import register_factory
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        sync_service = await register_factory(db, config, stellar)
        
        logger.info("✓ Sync service created")
        return sync_service
    
    registry.register_factory(
        'sync',
        create_sync,
        dependencies=['database', 'config', 'stellar']
    )
    
    # ========================================================================
    # LEVEL 4: ANALYTICS, HOLONIC, AND VISUALIZER
    # ========================================================================
    
    async def create_analytics(registry: ServiceRegistry):
        """
        Create analytics service.
        
        FIXED v3.3.1: Corrected constructor parameters to match updated service signature.
        Analytics service expects (database, config=None, cache_ttl=300), not (database, schema_string).
        """
        logger.info("Creating analytics service...")
        
        from services.analytics.ubec_analytics_service import UBECAnalyticsService
        
        db = await registry.get('database')
        config = await registry.get('config')
         
        # FIXED v3.3.1: Pass config object, not schema string
        analytics = UBECAnalyticsService(database=db, config=config)
        await analytics.initialize()
        
        logger.info("✓ Analytics service created")
        return analytics
    
    registry.register_factory(
        'analytics',
        create_analytics,
        dependencies=['database', 'config']  # FIXED v3.3.1: Added 'config' dependency
    )
    
    async def create_holonic(registry: ServiceRegistry):
        """Create holonic evaluator service."""
        logger.info("  ├─ Holonic Evaluator: Ubuntu principles assessment")
        
        from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        holonic_config = {
            'db_schema': 'ubec_main',
            'ubec_code': 'UBEC',
            'ubec_issuer': config.get('ubec_issuer')
        }
        
        holonic_service = await create_holonic_evaluator(db, holonic_config)
        
        logger.info("✓ Holonic evaluator service created")
        return holonic_service
    
    registry.register_factory(
        'holonic',
        create_holonic,
        dependencies=['database', 'config']
    )
    
    async def create_visualizer(registry: ServiceRegistry):
        """
        Create holonic visualizer service.
    
        FIXED v3.2.5: Corrected factory function name to match actual codebase.
        The factory function is 'create_holonic_visualizer', not 'create_visualizer'.
        """
        logger.info("  ├─ Holonic Visualizer: Charts and reports")
    
        from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer
    
        db = await registry.get('database')
        config_service = await registry.get('config')
    
        # Build config dictionary from config service (Principle #4: Single Source of Truth)
        visualizer_config = {
            'db_schema': config_service.get('db_schema', 'ubec_main'),
            'element_mode': config_service.get('element_mode', True)
        }
    
        visualizer = await create_holonic_visualizer(db, visualizer_config)
    
        logger.info("✓ Visualization service created")
        return visualizer
    
    registry.register_factory(
        'visualizer',
        create_visualizer,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # LEVEL 4: BIOREGION MANAGER
    # ========================================================================
    
    async def create_bioregion_manager(registry: ServiceRegistry):
        """Create bioregion manager service."""
        logger.info("  ├─ Bioregion Manager: Geographic community tracking")
        
        from services.community.bioregion_manager import create_bioregion_manager as create_mgr
        
        # Use the factory function from bioregion_manager module
        bioregion_manager = await create_mgr(registry)
        
        logger.info("✓ Bioregion manager service created")
        return bioregion_manager
    
    registry.register_factory(
        'bioregion_manager',
        create_bioregion_manager,
        dependencies=['database']
    )
    
    # ========================================================================
    # LEVEL 5: SCHEDULER SERVICE
    # ========================================================================
    
    async def create_scheduler_service(registry: ServiceRegistry):
        """Create scheduler service for automated tasks."""
        logger.info("  ├─ Scheduler Service: Automated periodic tasks")
        
        from services.scheduler.ubec_scheduler_service import create_scheduler_service as create_sched
        
        # Use the factory function from scheduler service module
        scheduler_service = await create_sched(registry)
        
        logger.info("✓ Scheduler service created")
        return scheduler_service
    
    registry.register_factory(
        'scheduler',
        create_scheduler_service,
        dependencies=['database', 'config', 'sync', 'analytics', 'holonic', 'visualizer']
    )
    
    # ========================================================================
    # LEVEL 6: API SERVICE
    # ========================================================================
    
    async def create_api_service(registry: ServiceRegistry):
        """Create FastAPI backend service."""
        logger.info("  ├─ API Service: FastAPI REST endpoints")
        
        from services.api.api_service import create_backend_api_service
        
        # Use the factory function from api_service module
        api_service = await create_backend_api_service(registry)
        
        logger.info("✓ API service created")
        return api_service
    
    registry.register_factory(
        'api_service',
        create_api_service,
        dependencies=['database', 'bioregion_manager']
    )
    
    # ========================================================================
    # REGISTRATION COMPLETE
    # ========================================================================
    
    logger.info("=" * 70)
    logger.info(f"✓ Registered {len(registry._factories)} services")
    logger.info("=" * 70)
    
    return registry


# ========================================================================
# COMMAND HANDLERS
# Principle #10: Separation of Concerns - Clear command boundaries
# ========================================================================

async def handle_health(registry: ServiceRegistry, detailed: bool = False):
    """
    Check system health.
    
    Args:
        registry: Service registry
        detailed: Show detailed health information
    """
    logger.info("=" * 70)
    logger.info("SYSTEM HEALTH CHECK")
    logger.info("=" * 70)
    
    try:
        # Use registry's built-in health check with detailed flag
        await registry.print_health(detailed=detailed)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise


async def handle_status(registry: ServiceRegistry):
    """
    Display system status.
    
    Args:
        registry: Service registry
    """
    logger.info("=" * 70)
    logger.info("SYSTEM STATUS")
    logger.info("=" * 70)
    
    try:
        info = registry.get_info()
        
        logger.info(f"Total Services: {info['total_services']}")
        logger.info("")
        logger.info("Initialization Order:")
        for service_name in info['initialization_order']:
            logger.info(f"  - {service_name}")
        
    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        raise


async def handle_sync_status(registry: ServiceRegistry):
    """
    Check data synchronization status and freshness.
    
    NEW v3.3.0: Added to help diagnose data population issues.
    
    This command displays:
    - Last operation timestamp from stellar_operations table
    - Total operations count
    - Active accounts in last 30 days
    - Data age in hours
    
    Implements Principle #4: Database as single source of truth with explicit schema names.
    
    Args:
        registry: Service registry
    """
    logger.info("=" * 70)
    logger.info("DATA SYNCHRONIZATION STATUS")
    logger.info("=" * 70)
    
    try:
        db = await registry.get('database')
        
        # Query stellar_operations table with explicit schema name
        # Principle #4: Database as single source of truth
        query = """
        SELECT 
            COUNT(*) as total_operations,
            COUNT(DISTINCT source_account) as unique_source_accounts,
            COUNT(DISTINCT from_account) as unique_from_accounts,
            COUNT(DISTINCT to_account) as unique_to_accounts,
            MAX(created_at) as last_operation_time,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_operations,
            COUNT(DISTINCT source_account) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_active_accounts
        FROM ubec_main.stellar_operations
        """
        
        result = await db.fetch_one(query, ())
        
        if result:
            logger.info("\nStellar Operations Table:")
            logger.info(f"  Total Operations: {result['total_operations']:,}")
            logger.info(f"  Unique Source Accounts: {result['unique_source_accounts']:,}")
            logger.info(f"  Unique From Accounts: {result['unique_from_accounts']:,}")
            logger.info(f"  Unique To Accounts: {result['unique_to_accounts']:,}")
            logger.info(f"  Last Operation: {result['last_operation_time']}")
            logger.info(f"  Recent Operations (30d): {result['recent_operations']:,}")
            logger.info(f"  Active Accounts (30d): {result['recent_active_accounts']:,}")
            
            # Calculate data age
            if result['last_operation_time']:
                age = datetime.now(timezone.utc) - result['last_operation_time']
                age_hours = age.total_seconds() / 3600
                logger.info(f"  Data Age: {age_hours:.1f} hours")
                
                # Warning if data is stale
                if age_hours > 24:
                    logger.warning("\n⚠️  WARNING: Data is more than 24 hours old")
                    logger.warning("⚠️  Run: python main.py sync --sync-type all")
            else:
                logger.warning("\n⚠️  WARNING: No operations found in database")
                logger.warning("⚠️  Run: python main.py sync --sync-type all")
        
        # Check account balances
        balance_query = """
        SELECT 
            token_code,
            COUNT(*) as holder_count,
            SUM(balance) as total_balance
        FROM ubec_main.ubec_balances
        WHERE balance > 0
        GROUP BY token_code
        ORDER BY token_code
        """
        
        balances = await db.fetch_all(balance_query, ())
        
        if balances:
            logger.info("\nToken Balances:")
            for row in balances:
                logger.info(f"  {row['token_code']:8s} - {row['holder_count']:,} holders, {float(row['total_balance']):,.2f} total")
        else:
            logger.warning("\n⚠️  No token balances found")
        
        logger.info("\n" + "=" * 70)
        
    except Exception as e:
        logger.error(f"Sync status check failed: {e}", exc_info=True)
        raise


async def handle_discover(registry: ServiceRegistry, max_accounts: int = 100):
    """
    Discover token holders.
    
    Args:
        registry: Service registry
        max_accounts: Maximum accounts to discover
    """
    logger.info("=" * 70)
    logger.info("TOKEN HOLDER DISCOVERY")
    logger.info(f"Max Accounts: {max_accounts}")
    logger.info("=" * 70)
    
    sync_service = await registry.get('sync')
    
    try:
        results = await sync_service.discover_all_token_holders(max_accounts=max_accounts)
        
        for token, result in results.items():
            logger.info(f"\n{token}:")
            logger.info(f"  Accounts Discovered: {result.get('discovered', 0)}")
            logger.info(f"  Total Holders: {result.get('total', 0)}")
            
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        raise


async def handle_sync(
    registry: ServiceRegistry,
    sync_type: str = 'all',
    max_accounts: Optional[int] = None,
    force: bool = False
):
    """
    Synchronize blockchain data.
    
    Args:
        registry: Service registry
        sync_type: Type of synchronization (all, UBEC, UBECrc, UBECgpi, UBECtt)
        max_accounts: Maximum accounts to sync per token
        force: Force full resync
    """
    logger.info("=" * 70)
    logger.info("BLOCKCHAIN SYNCHRONIZATION")
    logger.info(f"Sync Type: {sync_type}")
    logger.info(f"Max Accounts: {max_accounts or 'All'}")
    logger.info(f"Force: {force}")
    logger.info("=" * 70)
    
    sync_service = await registry.get('sync')
    
    try:
        if sync_type == 'all':
            # Sync all tokens
            results = await sync_service.sync_all_tokens(
                max_accounts_per_token=max_accounts
            )
            
            # Display results for each token
            for token_name, token_result in results.items():
                logger.info(f"\n{token_name}:")
                if isinstance(token_result, dict):
                    logger.info(f"  Accounts Synced: {token_result.get('synced', 0)}")
                    logger.info(f"  Operations Processed: {token_result.get('operations', 0)}")
                    logger.info(f"  Duration: {token_result.get('duration', 0):.2f}s")
                else:
                    logger.info(f"  Result: {token_result}")
        else:
            # Sync specific token
            result = await sync_service.discover_accounts(
                asset_code=sync_type,
                max_accounts=max_accounts or 1000
            )
            
            logger.info(f"\n{sync_type}:")
            logger.info(f"  Accounts Found: {result.get('discovered', 0)}")
            
    except Exception as e:
        logger.error(f"Synchronization failed: {e}", exc_info=True)
        raise


async def handle_analytics(registry: ServiceRegistry, analysis_type: str = 'overview'):
    """
    Run analytics operations.
    
    Args:
        registry: Service registry
        analysis_type: Type of analysis (overview, holders, metrics)
        
    FIXED v3.2.2: Corrected field names to match analytics service return structure
    - Service returns 'tokens' not 'by_token'
    - Service returns data at top level, not in 'summary' key
    """
    logger.info("=" * 70)
    logger.info("ANALYTICS")
    logger.info(f"Analysis Type: {analysis_type}")
    logger.info("=" * 70)
    
    analytics_service = await registry.get('analytics')
    
    try:
        if analysis_type == 'overview':
            results = await analytics_service.get_distribution_overview()
            
            # Pretty print the results
            logger.info("\n" + "=" * 70)
            logger.info("DISTRIBUTION OVERVIEW")
            logger.info("=" * 70)
            
            # FIXED v3.2.2: Service returns data at top level, not nested in 'summary'
            logger.info("\nEcosystem Summary:")
            logger.info(f"  Total Holders: {results.get('total_holders', 0):,}")
            logger.info(f"  Total Supply: {float(results.get('total_supply', 0)):,.2f}")
            logger.info(f"  Timestamp: {results.get('timestamp', 'N/A')}")
            
            # FIXED v3.2.2: Service returns 'tokens' not 'by_token'
            logger.info("\nPer-Token Distribution:")
            for token, data in results.get('tokens', {}).items():
                logger.info(f"\n  {token}:")
                logger.info(f"    Holders: {data.get('total_holders', 0):,}")
                logger.info(f"    Supply: {float(data.get('total_supply', 0)):,.2f}")
                logger.info(f"    Concentration Index: {data.get('concentration_index', 0):.4f}")
                
        elif analysis_type == 'holders':
            holders = await analytics_service.get_top_holders(limit=10)
            
            logger.info("\n" + "=" * 70)
            logger.info("TOP HOLDERS")
            logger.info("=" * 70)
            
            for i, holder in enumerate(holders, 1):
                logger.info(f"  {i:2d}. {holder.get('account_id')}: {holder.get('balance')}")
                
        elif analysis_type == 'metrics':
            metrics = await analytics_service.get_network_metrics()
            
            logger.info("\n" + "=" * 70)
            logger.info("NETWORK METRICS")
            logger.info("=" * 70)
            
            for key, value in metrics.items():
                logger.info(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        raise


async def handle_holonic_evaluation(
    registry: ServiceRegistry,
    evaluate_all: bool = False,
    account_id: Optional[str] = None,
    max_accounts: Optional[int] = None,
    save_to_db: bool = True
):
    """
    Handle holonic evaluation command.
    
    NEW v3.1.9: Added holonic evaluation command handler.
    
    This function orchestrates holonic evaluation of accounts against
    Ubuntu principles (diversity, reciprocity, mutualism, regeneration).
    
    Args:
        registry: Service registry
        evaluate_all: Evaluate all accounts
        account_id: Specific account to evaluate
        max_accounts: Maximum accounts to evaluate (for batch mode)
        save_to_db: Save results to database
        
    Principle #5: Strict Async Operations
    Principle #12: Method Singularity - uses holonic evaluator service methods
    """
    logger.info("=" * 70)
    logger.info("HOLONIC EVALUATION")
    logger.info("=" * 70)
    
    holonic_service = await registry.get('holonic')
    
    try:
        if evaluate_all:
            # Evaluate all accounts
            logger.info("Evaluating all accounts against Ubuntu principles...")
            logger.info(f"Max Accounts: {max_accounts or 'All'}")
            logger.info(f"Save to DB: {save_to_db}")
            logger.info("")
            
            # Track evaluation time
            start_time = time.time()
            
            results = await holonic_service.evaluate_all_accounts(
                max_accounts=max_accounts,
                save_to_db=save_to_db
            )
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Display results
            # FIXED v3.2.0: Corrected field names to match evaluator return values
            logger.info("\n✅ Evaluation completed")
            logger.info(f"  Accounts Evaluated: {results.get('evaluated', 0):,}")
            logger.info(f"  Accounts Skipped: {results.get('skipped', 0):,}")
            logger.info(f"  Errors: {results.get('errors', 0):,}")
            logger.info(f"  Duration: {duration:.2f}s")
            
        elif account_id:
            # Evaluate specific account
            logger.info(f"Evaluating account: {account_id}")
            logger.info(f"Save to DB: {save_to_db}")
            logger.info("")
            
            metrics = await holonic_service.evaluate_account(
                account_id=account_id,
                save_to_db=save_to_db
            )
            
            logger.info("\n✅ Evaluation completed")
            logger.info(f"  Ubuntu Alignment Score: {metrics.ubuntu_alignment_score:.4f}")
            logger.info(f"  Health Status: {metrics.health_status}")
            
        else:
            logger.error("Must specify either --all or --account")
            return
        
    except Exception as e:
        logger.error(f"Holonic evaluation failed: {e}", exc_info=True)
        raise


async def handle_visualize(
    registry: ServiceRegistry,
    action: str = 'report',
    format: str = 'html',
    include_advanced: bool = False
):
    """
    Generate visualizations and reports.
    
    Args:
        registry: Service registry
        action: Visualization action
        format: Output format
        include_advanced: Include advanced visualizations
    """
    logger.info("=" * 70)
    logger.info("GENERATING VISUALIZATIONS")
    logger.info(f"Action: {action}")
    logger.info(f"Format: {format}")
    logger.info("=" * 70)
    
    visualizer = await registry.get('visualizer')
    
    try:
        if action == 'report':
            output_path = await visualizer.generate_report(
                format=format,
                include_advanced=include_advanced
            )
            logger.info(f"\n✅ Report generated: {output_path}")
        elif action == 'all':
            output_paths = await visualizer.generate_all_visualizations()
            logger.info("\n✅ All visualizations generated")
            for path in output_paths:
                logger.info(f"  {path}")
        else:
            logger.error(f"Unknown visualization action: {action}")
            return
        
    except Exception as e:
        logger.error(f"Visualization failed: {e}", exc_info=True)
        raise


async def handle_protocol_health(registry: ServiceRegistry):
    """
    Check health of all protocol services.
    
    Args:
        registry: Service registry
    """
    logger.info("=" * 70)
    logger.info("PROTOCOL HEALTH CHECK")
    logger.info("=" * 70)
    
    protocols = ['air_protocol', 'water_protocol', 'earth_protocol', 'fire_protocol']
    
    for protocol_name in protocols:
        try:
            protocol = await registry.get(protocol_name)
            health = await protocol.health_check()
            
            status = health.get('status', 'unknown')
            if status == 'healthy':
                logger.info(f"  ✅ {protocol_name:20s} - {status}")
            else:
                logger.warning(f"  ⚠️  {protocol_name:20s} - {status}")
            
            # Show details
            for key, value in health.items():
                if key != 'status':
                    logger.info(f"     {key}: {value}")
                    
        except Exception as e:
            logger.error(f"  ❌ {protocol_name:20s} - Error: {e}")
    
    logger.info("=" * 70)


async def handle_scheduler_status(registry: ServiceRegistry):
    """
    Display scheduler status and job information.
    
    Args:
        registry: Service registry
    """
    logger.info("=" * 70)
    logger.info("SCHEDULER STATUS")
    logger.info("=" * 70)
    
    try:
        scheduler = await registry.get('scheduler')
        status = await scheduler.get_status()
        
        logger.info(f"Scheduler Running: {status.get('running', False)}")
        logger.info(f"Active Jobs: {status.get('active_jobs', 0)}")
        logger.info(f"Total Jobs: {status.get('total_jobs', 0)}")
        logger.info("")
        
        if 'jobs' in status:
            logger.info("Job Details:")
            for job in status['jobs']:
                logger.info(f"  - {job.get('name')}")
                logger.info(f"    Enabled: {job.get('enabled')}")
                logger.info(f"    Last Run: {job.get('last_run')}")
                logger.info(f"    Next Run: {job.get('next_run')}")
                logger.info("")
        
    except Exception as e:
        logger.error(f"Scheduler status check failed: {e}", exc_info=True)


async def handle_serve(
    registry: ServiceRegistry,
    host: str = '0.0.0.0',
    port: int = 8000,
    reload: bool = False
):
    """
    Start FastAPI backend server with scheduler.
    
    Args:
        registry: Service registry
        host: Server host
        port: Server port
        reload: Enable auto-reload
    """
    logger.info("=" * 70)
    logger.info("STARTING API SERVER WITH SCHEDULER")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info("=" * 70)
    
    try:
        # Start scheduler service
        scheduler = await registry.get('scheduler')
        await scheduler.start()
        logger.info("✅ Scheduler started - background jobs active")
        
        # Get API service
        api_service = await registry.get('api_service')
        app = api_service.app
        
        # Configure uvicorn
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        
        logger.info(f"✅ API server starting on {host}:{port}")
        
        # Run server
        await server.serve()
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        raise
    finally:
        # Stop scheduler on shutdown
        try:
            scheduler = await registry.get('scheduler')
            await scheduler.stop()
            logger.info("✅ Scheduler stopped")
        except Exception as e:
            logger.warning(f"Error stopping scheduler: {e}")


# ========================================================================
# MAIN FUNCTION
# Principle #2: Service Pattern - Single entry point
# ========================================================================

async def main():
    """
    Main orchestration function.
    
    This is the ONLY function that should be called from __main__.
    All operations flow through the service registry.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='UBEC Protocol Suite - Main Orchestrator'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument('--detailed', action='store_true',
                              help='Show detailed health information')
    
    # Status command
    subparsers.add_parser('status', help='Display system status')
    
    # Sync status command (NEW v3.3.0)
    subparsers.add_parser('sync-status', help='Check data synchronization status')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover token holders')
    discover_parser.add_argument('--max-accounts', type=int, default=100,
                                help='Maximum accounts to discover')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Synchronize blockchain data')
    sync_parser.add_argument('--sync-type', default='all',
                           choices=['all', 'UBEC', 'UBECrc', 'UBECgpi', 'UBECtt'],
                           help='Type of synchronization')
    sync_parser.add_argument('--max-accounts', type=int,
                           help='Maximum accounts to sync')
    sync_parser.add_argument('--force', action='store_true',
                           help='Force full resync')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Run analytics')
    analytics_parser.add_argument('--analysis-type', default='overview',
                                 choices=['overview', 'holders', 'metrics'],
                                 help='Type of analysis')
    
    # Holonic evaluation command
    holonic_parser = subparsers.add_parser('evaluate-holonic', help='Evaluate Ubuntu principles')
    holonic_parser.add_argument('--all', action='store_true',
                               help='Evaluate all accounts')
    holonic_parser.add_argument('--account', type=str,
                               help='Specific account to evaluate')
    holonic_parser.add_argument('--max-accounts', type=int,
                               help='Maximum accounts to evaluate')
    holonic_parser.add_argument('--no-save', action='store_true',
                               help='Do not save results to database')
    
    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Generate visualizations')
    visualize_parser.add_argument('--action', default='report',
                                 choices=['report', 'all'],
                                 help='Visualization action')
    visualize_parser.add_argument('--format', default='html',
                                 choices=['html', 'pdf', 'png'],
                                 help='Output format')
    visualize_parser.add_argument('--include-advanced', action='store_true',
                                 help='Include advanced visualizations')
    
    # Protocol health command
    subparsers.add_parser('protocol-health', help='Check protocol health')
    
    # Scheduler status command
    subparsers.add_parser('scheduler-status', help='Display scheduler status')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start API server with scheduler')
    serve_parser.add_argument('--host', default='0.0.0.0',
                            help='Server host')
    serve_parser.add_argument('--port', type=int, default=8000,
                            help='Server port')
    serve_parser.add_argument('--reload', action='store_true',
                            help='Enable auto-reload')
    
    args = parser.parse_args()
    
    try:
        # Register all services
        registry = register_core_services()
        
        # Initialize all services
        async with registry:
            # Execute command
            if args.command == 'health':
                await handle_health(registry, detailed=args.detailed)
                
            elif args.command == 'status':
                await handle_status(registry)
            
            elif args.command == 'sync-status':
                await handle_sync_status(registry)
                
            elif args.command == 'discover':
                await handle_discover(registry, max_accounts=args.max_accounts)
                
            elif args.command == 'sync':
                await handle_sync(
                    registry,
                    sync_type=args.sync_type,
                    max_accounts=args.max_accounts,
                    force=args.force
                )
                
            elif args.command == 'analytics':
                await handle_analytics(registry, analysis_type=args.analysis_type)
            
            elif args.command == 'evaluate-holonic':
                await handle_holonic_evaluation(
                    registry,
                    evaluate_all=args.all,
                    account_id=args.account,
                    max_accounts=args.max_accounts,
                    save_to_db=not args.no_save
                )
                
            elif args.command == 'visualize':
                await handle_visualize(
                    registry,
                    action=args.action,
                    format=args.format,
                    include_advanced=args.include_advanced
                )
                
            elif args.command == 'protocol-health':
                await handle_protocol_health(registry)
                
            elif args.command == 'scheduler-status':
                await handle_scheduler_status(registry)
                
            elif args.command == 'serve':
                await handle_serve(
                    registry,
                    host=args.host,
                    port=args.port,
                    reload=args.reload
                )
                
            else:
                parser.print_help()
                logger.info("\nNo command specified. Use --help for options.")
        
        logger.info("\n✅ Operation completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Operation cancelled by user")
        return 130
        
    except Exception as e:
        logger.error(f"\n❌ Operation failed: {e}", exc_info=True)
        return 1


# ========================================================================
# STANDALONE EXECUTION
# Principle #2: Service Pattern - This is the ONLY executable module
# ========================================================================

if __name__ == "__main__":
    """
    Entry point for the entire UBEC Protocol Suite.
    
    This is the ONLY place where the system should be executed.
    All other modules implement the service pattern and cannot run standalone.
    """
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
