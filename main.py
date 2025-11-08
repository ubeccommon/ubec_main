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
    
    # Discovery operations
    python main.py discover --max-accounts 100
    
    # Sync operations
    python main.py sync --sync-type all
    
    # Analytics operations
    python main.py analytics --analysis-type overview
    
    # Visualization
    python main.py visualize --action report --format html
    
    # Protocol health
    python main.py protocol-health
    
    # Scheduler status
    python main.py scheduler-status
    
    # API Server with Scheduler
    python main.py serve --host 0.0.0.0 --port 8000

Author: UBEC Protocol Development Team
Version: 3.1.4
Updated: 2025-11-08
CHANGELOG v3.1.4:
    - Enhanced scheduler error diagnostics in handle_serve()
    - Added scheduler initialization status logging
    - Improved error messages for troubleshooting
"""

import asyncio
import argparse
import logging
import sys
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
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
    
    registry = ServiceRegistry()
    
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
        3. Create production pool with database-driven config
        """
        logger.info("Creating database service...")
        
        # Get connection parameters from environment
        primary_schema, search_path = get_database_connection_config()
        
        # Get database connection parameters
        # Following Principle #8: No Duplicate Configuration
        # Uses environment variables with sensible defaults
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', '5432'))
        database = os.getenv('DB_NAME', 'ubec')
        user = os.getenv('DB_USER', 'ubec_admin')
        password = os.getenv('DB_PASSWORD', '')
        
        # Create database manager with production configuration
        # Pool configuration will be loaded FROM the database
        db = AsyncDatabaseManager(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            schema=primary_schema,
            search_path=search_path,
            min_pool_size=2,  # Conservative default - will be updated from DB
            max_pool_size=20  # Conservative default - will be updated from DB
        )
        
        # Initialize the connection pool
        await db.initialize()
        
        logger.info("✓ Database service created")
        return db
    
    registry.register_factory(
        'database',
        create_database,
        dependencies=[]
    )
    
    # ========================================================================
    # RATE LIMITER SERVICE
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
    
    # ========================================================================
    # CONFIGURATION SERVICE
    # ========================================================================
    
    async def create_config(registry: ServiceRegistry):
        """
        Create configuration service.
        
        Uses the factory pattern from config.config module to create
        a property-style configuration wrapper around ConfigurationService.
        
        Implements Principle #4: Database is single source of truth for all config.
        """
        logger.info("Creating configuration service...")
        
        # FIXED: Use the correct factory function from config.config
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
    # BIOREGION MANAGER SERVICE
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
    # API SERVICE
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
    # STELLAR CLIENT SERVICE
    # ========================================================================
    
    async def create_stellar(registry: ServiceRegistry):
        """
        Create Stellar client service.
        
        Direct instantiation pattern - similar to analytics service.
        
        Implements Principle #9: Integrated rate limiting for Stellar API.
        """
        logger.info("Creating Stellar client service...")
        
        # FIXED: Direct class import, not factory function
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
    # ANALYTICS SERVICE
    # ========================================================================
    
    async def create_analytics(registry: ServiceRegistry):
        """Create analytics service."""
        logger.info("Creating analytics service...")
        
        from services.analytics.ubec_analytics_service import UBECAnalyticsService
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        analytics = UBECAnalyticsService(db, config)
        await analytics.initialize()
        
        logger.info("✓ Analytics service created")
        return analytics
    
    registry.register_factory(
        'analytics',
        create_analytics,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # HOLONIC EVALUATOR SERVICE
    # ========================================================================
    
    async def create_holonic(registry: ServiceRegistry):
        """Create holonic evaluator service."""
        logger.info("  ├─ Holonic Evaluator: Ubuntu principles assessment")
        
        from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        holonic_evaluator = await create_holonic_evaluator(db, config)
        
        logger.info("✓ Holonic evaluator service created")
        return holonic_evaluator
    
    registry.register_factory(
        'holonic',
        create_holonic,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # HOLONIC VISUALIZER SERVICE
    # ========================================================================
    
    async def create_visualizer(registry: ServiceRegistry):
        """Create holonic visualizer service."""
        logger.info("  ├─ Holonic Visualizer: Charts and reports")
        
        from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        visualizer = await create_holonic_visualizer(db, config)
        
        logger.info("✓ Visualization service created")
        return visualizer
    
    registry.register_factory(
        'visualizer',
        create_visualizer,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # DATA SYNCHRONIZER SERVICE
    # ========================================================================
    
    async def create_sync(registry: ServiceRegistry):
        """Create data synchronization service."""
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
    # PROTOCOL SERVICES (Air, Water, Earth, Fire)
    # ========================================================================
    
    # Fire Protocol (UBECtt - Transformation & Regeneration)
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
    
    # Earth Protocol (UBECgpi - Ground & Mutualism)
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
    
    # Air Protocol (UBEC - Gateway & Universal Access)
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
    
    # Water Protocol (UBECrc - Flow & Reciprocity)
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
    
    # ========================================================================
    # SCHEDULER SERVICE
    # ========================================================================
    
    async def create_scheduler_service(registry: ServiceRegistry):
        """Create scheduler service for automated tasks."""
        from services.scheduler.ubec_scheduler_service import create_scheduler_service as create_scheduler
        
        logger.info("  ├─ Scheduler Service: Automated periodic tasks")
        
        # Use the factory function from scheduler service module
        scheduler_service = await create_scheduler(registry)
        
        logger.info("✓ Scheduler service created")
        return scheduler_service
    
    registry.register_factory(
        'scheduler',
        create_scheduler_service,
        dependencies=[
            'database',
            'config',
            'sync',
            'analytics',
            'holonic',
            'visualizer',
            'bioregion_manager'
        ]
    )
    
    logger.info("=" * 70)
    logger.info(f"✓ Registered {len(registry._factories)} services")
    logger.info("=" * 70)
    
    return registry


# ========================================================================
# COMMAND HANDLERS
# Principle #10: Separation of Concerns
# ========================================================================

async def handle_health_check(registry: ServiceRegistry, detailed: bool = False):
    """
    Perform comprehensive health check on all services.
    
    Args:
        registry: Service registry
        detailed: Show detailed health information
    """
    logger.info("=" * 70)
    logger.info("SYSTEM HEALTH CHECK")
    logger.info("=" * 70)
    
    # Check all registered services
    service_names = [
        'database', 'config', 'stellar', 'rate_limiter',
        'air_protocol', 'water_protocol', 'earth_protocol', 'fire_protocol',
        'sync', 'analytics', 'holonic', 'visualizer', 'bioregion_manager', 
        'api_service', 'scheduler'
    ]
    
    all_healthy = True
    
    for service_name in service_names:
        try:
            service = await registry.get(service_name)
            
            # Call the service's own health_check() method
            if hasattr(service, 'health_check'):
                health = await service.health_check()
            else:
                # Fallback for services without health_check method
                health = {
                    'status': 'unknown',
                    'message': f'{service_name} has no health_check method'
                }
            
            # Determine status symbol
            status_symbol = {
                'healthy': '✅',
                'degraded': '⚠️',
                'unhealthy': '❌',
                'not_started': '⏸️',
                'unknown': '❓'
            }.get(health.get('status', 'unknown'), '❓')
            
            logger.info(f"\n{status_symbol} {service_name}: {health.get('status', 'unknown')}")
            
            # Show message if present (especially for not_started status)
            if 'message' in health and health.get('status') == 'not_started':
                logger.info(f"  ℹ️  {health['message']}")
            
            if detailed and 'details' in health:
                for key, value in health['details'].items():
                    logger.info(f"  {key}: {value}")
            
            if health.get('status') not in ['healthy', 'unknown']:
                all_healthy = False
                
        except Exception as e:
            logger.error(f"\n❌ {service_name}: ERROR - {e}")
            all_healthy = False
    
    logger.info("\n" + "=" * 70)
    if all_healthy:
        logger.info("✅ ALL SYSTEMS HEALTHY")
    else:
        logger.info("⚠️  SOME SYSTEMS UNHEALTHY")
    logger.info("=" * 70)


async def handle_status(registry: ServiceRegistry):
    """
    Display system status information.
    
    Args:
        registry: Service registry
    """
    print("DEBUG: handle_status() called")
    logger.info("=" * 70)
    logger.info("SYSTEM STATUS")
    logger.info("=" * 70)
    
    # Get database service
    db = await registry.get('database')
    
    # Database status using explicit schema name (Principle #4)
    query = """
        SELECT 
            COUNT(*) as total_accounts,
            COUNT(DISTINCT asset_code) as active_tokens
        FROM ubec_main.account_balances
        WHERE balance > 0
    """
    
    try:
        result = await db.fetch_one(query)
        if result:
            logger.info(f"\nDatabase Status:")
            logger.info(f"  Total Accounts: {result['total_accounts']}")
            logger.info(f"  Active Tokens: {result['active_tokens']}")
    except Exception as e:
        logger.error(f"Error fetching status: {e}")
    
    # Check data freshness
    freshness_query = """
        SELECT 
            MAX(updated_at) as last_update,
            NOW() - MAX(updated_at) as data_age
        FROM ubec_main.account_balances
    """
    
    try:
        result = await db.fetch_one(freshness_query)
        if result and result['last_update']:
            logger.info(f"\nData Freshness:")
            logger.info(f"  Last Update: {result['last_update']}")
            logger.info(f"  Age: {result['data_age']}")
    except Exception as e:
        logger.error(f"Error checking data freshness: {e}")
    
    logger.info("\n" + "=" * 70)


async def handle_discover(registry: ServiceRegistry, max_accounts: int = 100):
    """
    Discover and track new token holders.
    
    Args:
        registry: Service registry
        max_accounts: Maximum accounts to discover
    """
    logger.info("=" * 70)
    logger.info("DISCOVERING TOKEN HOLDERS")
    logger.info(f"Max Accounts: {max_accounts}")
    logger.info("=" * 70)
    
    sync_service = await registry.get('sync')
    
    try:
        results = await sync_service.discover_holders(max_accounts=max_accounts)
        
        logger.info("\n✅ Discovery completed")
        logger.info(f"  New accounts found: {results.get('new_accounts', 0)}")
        logger.info(f"  Total accounts: {results.get('total_accounts', 0)}")
        
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
        sync_type: Type of sync (all, UBEC, UBECrc, UBECgpi, UBECtt)
        max_accounts: Maximum accounts to discover per token
        force: Force full resync (currently unused - reserved for future)
    """
    logger.info("=" * 70)
    logger.info("SYNCHRONIZING BLOCKCHAIN DATA")
    logger.info(f"Sync Type: {sync_type}")
    if max_accounts:
        logger.info(f"Max Accounts: {max_accounts}")
    if force:
        logger.info("Mode: FORCE RESYNC (note: sync service uses incremental by default)")
    logger.info("=" * 70)
    
    sync_service = await registry.get('sync')
    
    try:
        if sync_type == 'all':
            # Sync all tokens - sync_all() doesn't accept parameters
            # It uses configuration from database for limits
            logger.info("Synchronizing all UBEC protocol tokens...")
            results = await sync_service.sync_all()
            
            # Results format: dict with token-specific results
            logger.info("\n✅ Synchronization completed")
            
            # Display results for each token if available
            if isinstance(results, dict):
                total_accounts = 0
                for token, token_results in results.items():
                    if isinstance(token_results, dict):
                        accounts = token_results.get('accounts_discovered', 0)
                        total_accounts += accounts
                        logger.info(f"  {token}: {accounts} accounts")
                
                logger.info(f"  Total accounts: {total_accounts}")
            else:
                logger.info(f"  Results: {results}")
        else:
            # Discover holders for specific token
            # Use discover_accounts(asset_code, max_accounts) method
            logger.info(f"Discovering {sync_type} token holders...")
            
            # Call discover_accounts with proper parameters
            if max_accounts:
                results = await sync_service.discover_accounts(
                    asset_code=sync_type,
                    max_accounts=max_accounts
                )
            else:
                results = await sync_service.discover_accounts(
                    asset_code=sync_type,
                    max_accounts=5000  # Default limit
                )
            
            logger.info("\n✅ Discovery completed")
            logger.info(f"  Accounts discovered: {results.get('accounts_discovered', 0)}")
            logger.info(f"  New accounts: {results.get('new_accounts', 0)}")
            
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        raise


async def handle_analytics(registry: ServiceRegistry, analysis_type: str = 'overview'):
    """
    Run analytics on protocol data.
    
    Args:
        registry: Service registry
        analysis_type: Type of analysis
    """
    logger.info("=" * 70)
    logger.info("RUNNING ANALYTICS")
    logger.info(f"Analysis Type: {analysis_type}")
    logger.info("=" * 70)
    
    analytics_service = await registry.get('analytics')
    
    try:
        if analysis_type == 'overview':
            results = await analytics_service.generate_overview()
        elif analysis_type == 'holders':
            results = await analytics_service.analyze_holders()
        elif analysis_type == 'metrics':
            results = await analytics_service.calculate_metrics()
        else:
            logger.error(f"Unknown analysis type: {analysis_type}")
            return
        
        logger.info("\n✅ Analysis completed")
        logger.info(f"  Results: {results}")
        
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        raise


async def handle_visualize(
    registry: ServiceRegistry,
    action: str = 'report',
    format: str = 'html',
    include_advanced: bool = False
):
    """
    Generate visualizations.
    
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
            
            status_symbol = {
                'healthy': '✅',
                'degraded': '⚠️',
                'unhealthy': '❌'
            }.get(health.get('status', 'unknown'), '❓')
            
            logger.info(f"\n{status_symbol} {protocol_name}: {health.get('status')}")
            
            if 'details' in health:
                for key, value in health['details'].items():
                    logger.info(f"  {key}: {value}")
                    
        except Exception as e:
            logger.error(f"\n❌ {protocol_name}: ERROR - {e}")
    
    logger.info("\n" + "=" * 70)


async def handle_scheduler_status(registry: ServiceRegistry):
    """
    Display scheduler status.
    
    Args:
        registry: Service registry
    """
    logger.info("=" * 70)
    logger.info("SCHEDULER STATUS")
    logger.info("=" * 70)
    
    try:
        scheduler = await registry.get('scheduler')
        health = await scheduler.health_check()
        
        # Overall status
        status_symbol = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌',
            'not_started': '⏸️'
        }.get(health['status'], '❓')
        
        logger.info(f"\n{status_symbol} Status: {health['status'].upper()}")
        logger.info(f"Running: {'Yes' if health.get('running') else 'No'}")
        
        # Show message if present
        if 'message' in health:
            logger.info(f"\nℹ️  {health['message']}")
        
        # Metrics (if running)
        if 'metrics' in health:
            metrics = health['metrics']
            logger.info(f"\nMetrics:")
            logger.info(f"  Total Jobs: {metrics.get('total_jobs', 0)}")
            logger.info(f"  Enabled: {metrics.get('enabled_jobs', 0)}")
            logger.info(f"  Currently Running: {metrics.get('running_jobs', 0)}")
            logger.info(f"  Success Rate: {metrics.get('overall_success_rate', 0):.1%}")
        
        # Job details
        if 'jobs' in health:
            logger.info(f"\nJobs:")
            for job in health['jobs']:
                job_status = '✅' if job.get('enabled') else '❌'
                circuit = job.get('circuit_state', 'unknown')
                circuit_symbol = {
                    'closed': '✅',
                    'half_open': '⚠️',
                    'open': '❌'
                }.get(circuit, '❓')
                
                logger.info(f"\n  {job_status} {job.get('name', 'unknown')}")
                logger.info(f"     Next Run: {job.get('next_run', 'N/A')}")
                logger.info(f"     Success Rate: {job.get('success_rate', 0):.1%}")
                logger.info(f"     Avg Duration: {job.get('avg_duration_ms', 0):.0f}ms")
                logger.info(f"     Circuit: {circuit_symbol} {circuit}")
            
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
    
    logger.info("\n" + "=" * 70)


async def handle_serve(
    registry: ServiceRegistry,
    host: str = '0.0.0.0',
    port: int = 8000,
    reload: bool = False
):
    """
    Start the FastAPI backend server with scheduler.
    
    This exposes REST endpoints for the www server to consume and
    starts the background scheduler for automated tasks.
    
    Args:
        registry: Service registry
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
    """
    logger.info("=" * 70)
    logger.info(f"STARTING UBEC PROTOCOL SERVER")
    logger.info(f"API: http://{host}:{port}")
    logger.info("=" * 70)
    
    # Get the API service
    api_service = await registry.get('api_service')
    app = api_service.app
    
    # ═══════════════════════════════════════════════════════════════
    # ⭐ CRITICAL: Start Scheduler Service ⭐
    # ═══════════════════════════════════════════════════════════════
    scheduler = None
    try:
        logger.info("\n🔄 Initializing Scheduler Service...")
        
        # Get scheduler from registry (this calls initialize())
        scheduler = await registry.get('scheduler')
        logger.info("✓ Scheduler service retrieved from registry")
        
        # Check health before starting
        health = await scheduler.health_check()
        logger.info(f"Scheduler health status: {health.get('status')}")
        
        # Start the background loop
        await scheduler.start()
        logger.info("✓ Scheduler background loop started")
        
        # Verify it's actually running
        health = await scheduler.health_check()
        if health.get('running'):
            logger.info("✅ Scheduler started - automated tasks active")
        else:
            logger.warning("⚠️  Scheduler started but health check shows not running")
            logger.warning(f"Status: {health.get('status')}")
            if 'message' in health:
                logger.warning(f"Message: {health['message']}")
            
    except ImportError as e:
        logger.error(f"⚠️  Failed to import scheduler service: {e}")
        logger.error("Check that services/scheduler/ubec_scheduler_service.py exists")
        logger.warning("Server will continue without scheduler")
    except Exception as e:
        logger.error(f"⚠️  Failed to start scheduler: {e}", exc_info=True)
        logger.warning("Server will continue without scheduler")
        logger.warning("To diagnose: python main.py scheduler-status")
    # ═══════════════════════════════════════════════════════════════
    
    logger.info(f"\n✅ Server ready")
    logger.info(f"📊 Swagger docs: http://{host}:{port}/docs")
    logger.info(f"📖 ReDoc: http://{host}:{port}/redoc")
    logger.info(f"💚 Health: http://{host}:{port}/health")
    if scheduler:
        logger.info(f"⏰ Scheduler: Active (background tasks running)")
    else:
        logger.info(f"⏸️  Scheduler: NOT RUNNING (automated tasks disabled)")
    logger.info("\n👉 Press Ctrl+C to stop")
    logger.info("=" * 70)
    
    # Run the server
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=reload
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Shutting down...")
        
        # ═══════════════════════════════════════════════════════════════
        # ⭐ CRITICAL: Stop Scheduler Gracefully ⭐
        # ═══════════════════════════════════════════════════════════════
        if scheduler:
            try:
                logger.info("Stopping scheduler...")
                await scheduler.stop()
                logger.info("✅ Scheduler stopped")
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")
        # ═══════════════════════════════════════════════════════════════
        
        logger.info("✅ Server stopped")
        raise  # Re-raise to ensure proper cleanup

# ========================================================================
# MAIN ENTRY POINT
# Principle #2: Service Pattern - Single orchestrator
# ========================================================================

async def main():
    """
    Main entry point - orchestrates all system operations.
    
    This is the ONLY function that should be called from __main__.
    All operations flow through the service registry.
    """
    # Debug: Verify main() is being called
    print("DEBUG: main() function started")
    
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
    
    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Generate visualizations')
    visualize_parser.add_argument('--action', default='report',
                                 choices=['report', 'all', 'chart'],
                                 help='Visualization action')
    visualize_parser.add_argument('--format', default='html',
                                 choices=['html', 'pdf'],
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
                            help='Host to bind to')
    serve_parser.add_argument('--port', type=int, default=8000,
                            help='Port to bind to')
    serve_parser.add_argument('--reload', action='store_true',
                            help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    # Debug: Show what command was parsed
    print(f"DEBUG: Command parsed: {args.command}")
    
    # Display header
    print("DEBUG: About to display banner")
    logger.info("")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " " * 15 + "UBEC Protocol Suite v3.1.4" + " " * 26 + "║")
    logger.info("║" + " " * 18 + "Main Orchestrator" + " " * 33 + "║")
    logger.info("╚" + "═" * 68 + "╝")
    logger.info("")
    print("DEBUG: Banner displayed")
    
    # Register all services
    print("DEBUG: About to register services")
    registry = register_core_services()
    print("DEBUG: Services registered")
    
    try:
        # Initialize services using context manager
        print("DEBUG: About to enter async context manager")
        async with registry:
            print("DEBUG: Inside async context manager - services initialized")
            logger.info("\n✅ All services initialized successfully\n")
            
            # Execute command
            print(f"DEBUG: About to execute command: {args.command}")
            if args.command == 'health':
                await handle_health_check(registry, detailed=args.detailed)
                
            elif args.command == 'status':
                await handle_status(registry)
                print("DEBUG: handle_status() completed")
                
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
        
        print("DEBUG: About to print completion message")
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
