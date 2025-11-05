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
    
    # API Server (NEW)
    python main.py serve --host 0.0.0.0 --port 8000

Author: UBEC Protocol Development Team
Version: 3.0.0
Updated: 2025-11-04
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
from core.utils.service_health import ServiceHealthCheck
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
        user = os.getenv('DB_USER', 'ubec_app')
        password = os.getenv('DB_PASSWORD', '')
        min_pool_size = int(os.getenv('DB_MIN_POOL', '2'))
        max_pool_size = int(os.getenv('DB_MAX_POOL', '10'))
        
        # Create database manager
        db = AsyncDatabaseManager(
            host=host,
            port=port,
            database=database,
            schema=primary_schema,
            search_path=search_path,
            user=user,
            password=password,
            min_pool_size=min_pool_size,
            max_pool_size=max_pool_size
        )
        
        # Initialize with two-stage bootstrap
        await db.initialize()
        
        logger.info(f"✓ Database service created (Schema: {primary_schema})")
        return db
    
    registry.register_factory(
        'database',
        create_database,
        dependencies=[]
    )
    
    # ========================================================================
    # CONFIGURATION SERVICE
    # ========================================================================
    
    async def create_config(registry: ServiceRegistry):
        """
        Create configuration service (database-backed).
        
        Principle #4: Database as single source of truth
        Principle #8: No duplicate configuration
        """
        logger.info("Creating configuration service...")
        
        from config.config import Config
        from config.settings import ConfigurationService
        
        db = await registry.get('database')
        
        # Create actual configuration service
        config_service = ConfigurationService(db)
        await config_service.initialize()
        
        # Wrap in property-style interface
        config = Config(config_service)
        
        logger.info("✓ Configuration service created")
        return config
    
    registry.register_factory(
        'config',
        create_config,
        dependencies=['database']
    )
    
    # ========================================================================
    # RATE LIMITER SERVICE
    # ========================================================================
    
    async def create_rate_limiter(registry: ServiceRegistry):
        """
        Create rate limiter service with database-backed configuration.
        
        Principle #4: Single Source of Truth - Database configuration
        Principle #9: Integrated Rate Limiting
        """
        logger.info("Creating rate limiter service...")
        
        from services.stellar.rate_limiter_service import RateLimiterService
        
        db = await registry.get('database')
        
        rate_limiter = RateLimiterService(db_manager=db)
        await rate_limiter.initialize()
        
        logger.info("✓ Rate limiter service created")
        return rate_limiter
    
    registry.register_factory(
        'rate_limiter',
        create_rate_limiter,
        dependencies=['database']
    )
    
    # ========================================================================
    # STELLAR CLIENT SERVICE
    # ========================================================================
    
    async def create_stellar_client(registry: ServiceRegistry):
        """
        Create Stellar network client with rate limiting.
        
        Principle #9: Integrated rate limiting for Stellar API
        """
        logger.info("Creating Stellar client service...")
        
        from services.stellar.stellar_client_service import StellarClientService
        
        config = await registry.get('config')
        rate_limiter = await registry.get('rate_limiter')
        
        stellar = StellarClientService(
            config=config,
            rate_limiter=rate_limiter
        )
        await stellar.initialize()
        
        logger.info("✓ Stellar client service created")
        return stellar
    
    registry.register_factory(
        'stellar',
        create_stellar_client,
        dependencies=['config', 'rate_limiter']
    )
    
    # ========================================================================
    # PROTOCOL SERVICES (Air, Water, Earth, Fire)
    # ========================================================================
    
    async def create_air_protocol(registry: ServiceRegistry):
        """
        Create Air protocol service (UBEC).
        
        Principle #5: Async factory pattern
        Principle #12: Explicit initialization
        """
        from core.protocols.UBEC_protocol import create_ubec_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        logger.info("  ├─ Air Protocol: UBEC (Gateway/Diversity)")
        
        # Use async factory
        service = await create_ubec_service(
            db_manager=db,
            config={
                'asset_code': getattr(config, 'UBEC_CODE', 'UBEC'),
                'issuer': getattr(config, 'UBEC_ISSUER', '')
            },
            stellar_client=stellar
        )
        
        # Explicitly initialize
        await service.initialize()
        
        logger.info("✓ Air protocol service created")
        return service
    
    registry.register_factory(
        'air_protocol',
        create_air_protocol,
        dependencies=['database', 'config', 'stellar']
    )
    
    async def create_water_protocol(registry: ServiceRegistry):
        """
        Create Water protocol service (UBECrc).
        
        Principle #5: Async factory pattern
        Principle #12: Explicit initialization
        """
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        logger.info("  ├─ Water Protocol: UBECrc (Reciprocity/Flow)")
        
        # Use async factory
        service = await create_ubecrc_service(
            db_manager=db,
            config={
                'asset_code': getattr(config, 'UBECRC_CODE', 'UBECrc'),
                'issuer': getattr(config, 'UBECRC_ISSUER', '')
            },
            stellar_client=stellar
        )
        
        # Explicitly initialize
        await service.initialize()
        
        logger.info("✓ Water protocol service created")
        return service
    
    registry.register_factory(
        'water_protocol',
        create_water_protocol,
        dependencies=['database', 'config', 'stellar']
    )
    
    async def create_earth_protocol(registry: ServiceRegistry):
        """
        Create Earth protocol service (UBECgpi).
        
        Principle #5: Async factory pattern
        Principle #12: Explicit initialization
        """
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        logger.info("  ├─ Earth Protocol: UBECgpi (Ground/Stability)")
        
        # Use async factory (MUST await)
        service = await create_ubecgpi_service(
            db_manager=db,
            config={
                'asset_code': getattr(config, 'UBECGPI_CODE', 'UBECgpi'),
                'issuer': getattr(config, 'UBECGPI_ISSUER', '')
            },
            stellar_client=stellar
        )
        
        # Explicitly initialize
        await service.initialize()
        
        logger.info("✓ Earth protocol service created")
        return service
    
    registry.register_factory(
        'earth_protocol',
        create_earth_protocol,
        dependencies=['database', 'config', 'stellar']
    )
    
    async def create_fire_protocol(registry: ServiceRegistry):
        """
        Create Fire protocol service (UBECtt).
        
        Principle #5: Async factory pattern
        Principle #12: Explicit initialization
        """
        from core.protocols.UBECtt_protocol import create_ubectt_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        logger.info("  ├─ Fire Protocol: UBECtt (Transformation)")
        
        # Use async factory
        service = await create_ubectt_service(
            db_manager=db,
            config={
                'asset_code': getattr(config, 'UBECTT_CODE', 'UBECtt'),
                'issuer': getattr(config, 'UBECTT_ISSUER', '')
            },
            stellar_client=stellar
        )
        
        # Explicitly initialize
        await service.initialize()
        
        logger.info("✓ Fire protocol service created")
        return service
    
    registry.register_factory(
        'fire_protocol',
        create_fire_protocol,
        dependencies=['database', 'config', 'stellar']
    )
    
    # ========================================================================
    # NOTE: Discovery functionality is integrated into the sync service
    # No separate discovery service needed
    # ========================================================================
    
    # ========================================================================
    # SYNC SERVICE
    # ========================================================================
    
    async def create_sync(registry: ServiceRegistry):
        """
        Create blockchain synchronization service.
        
        Principle #5: Async factory pattern
        Principle #12: Uses standardized factory function
        """
        from core.db.ubec_data_synchronizer import register_factory
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar')
        
        logger.info("  ├─ Data Synchronizer: Blockchain sync engine")
        
        # Use async factory
        sync = await register_factory(
            database=db,
            config=config,
            stellar_client=stellar
        )
        
        logger.info("✓ Sync service created")
        return sync
    
    registry.register_factory(
        'sync',
        create_sync,
        dependencies=['database', 'config', 'stellar']
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
        """
        Create holonic evaluation service.
        
        Principle #5: Async factory pattern
        Principle #12: Uses standardized factory function
        """
        from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        logger.info("  ├─ Holonic Evaluator: Ubuntu principles assessment")
        
        # Use async factory
        holonic = await create_holonic_evaluator(
            db_manager=db,
            config={
                'db_schema': getattr(config, 'DB_SCHEMA', 'ubec_main'),
                'ubec_code': getattr(config, 'UBEC_CODE', 'UBEC'),
                'ubec_issuer': getattr(config, 'UBEC_ISSUER', ''),
                'auto_save_evaluations': True
            }
        )
        
        logger.info("✓ Holonic evaluator service created")
        return holonic
    
    registry.register_factory(
        'holonic',
        create_holonic,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # VISUALIZATION SERVICE
    # ========================================================================
    
    async def create_visualizer(registry: ServiceRegistry):
        """
        Create visualization service.
        
        Principle #5: Async factory pattern
        Principle #12: Uses standardized factory function
        """
        from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        logger.info("  ├─ Holonic Visualizer: Charts and reports")
        
        # Use async factory
        visualizer = await create_holonic_visualizer(
            db_manager=db,
            config={
                'db_schema': getattr(config, 'DB_SCHEMA', 'ubec_main')
            }
        )
        
        logger.info("✓ Visualization service created")
        return visualizer
    
    registry.register_factory(
        'visualizer',
        create_visualizer,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # BIOREGION MANAGER SERVICE
    # ========================================================================
    
    async def create_bioregion_manager(registry: ServiceRegistry):
        """
        Create bioregion manager service.
        
        Manages bioregional holons - geographic economic communities.
        
        Principle #5: Async factory pattern
        Principle #12: Uses standardized factory function
        """
        from services.community.bioregion_manager import create_bioregion_manager as create_mgr
        
        logger.info("  ├─ Bioregion Manager: Geographic community tracking")
        
        # Use the factory function from bioregion_manager module
        bioregion_mgr = await create_mgr(registry)
        
        logger.info("✓ Bioregion manager service created")
        return bioregion_mgr
    
    registry.register_factory(
        'bioregion_manager',
        create_bioregion_manager,
        dependencies=['database']
    )
    
    # ========================================================================
    # API SERVICE (FastAPI Backend)
    # ========================================================================
    
    async def create_api_service(registry: ServiceRegistry):
        """
        Create FastAPI backend service.
        
        Principle #5: Async factory pattern
        Principle #12: Uses standardized factory function
        """
        from services.api.api_service import create_backend_api_service
        
        logger.info("  ├─ API Service: FastAPI REST endpoints")
        
        # Use the factory function from api_service module
        api_service = await create_backend_api_service(registry)
        
        logger.info("✓ API service created")
        return api_service
    
    registry.register_factory(
        'api_service',
        create_api_service,
        dependencies=['database', 'config', 'bioregion_manager']
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
    
    health_checker = ServiceHealthCheck()
    
    # Check all registered services
    service_names = [
        'database', 'config', 'stellar',
        'air_protocol', 'water_protocol', 'earth_protocol', 'fire_protocol',
        'sync', 'analytics', 'holonic', 'visualizer', 'bioregion_manager', 'api_service'
    ]
    
    all_healthy = True
    
    for service_name in service_names:
        try:
            service = await registry.get(service_name)
            health = await health_checker.check_service_health(
                service_name, 
                service
            )
            
            status_symbol = "✅" if health['status'] == 'healthy' else "❌"
            logger.info(f"\n{status_symbol} {service_name}: {health['status']}")
            
            if detailed and 'details' in health:
                for key, value in health['details'].items():
                    logger.info(f"  {key}: {value}")
            
            if health['status'] != 'healthy':
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
    
    db = await registry.get('database')
    config = await registry.get('config')
    
    # Database status
    logger.info("\n📊 Database:")
    logger.info(f"  Schema: {db.schema}")
    logger.info(f"  Search Path: {db.search_path}")
    logger.info(f"  Initialized: {db._initialized}")
    
    # Configuration status
    logger.info("\n⚙️  Configuration:")
    try:
        # Try to access a config value to verify it's working
        test_value = getattr(config, 'DB_SCHEMA', None)
        logger.info(f"  Status: Operational")
        logger.info(f"  Schema: {test_value if test_value else 'N/A'}")
    except Exception as e:
        logger.info(f"  Status: Error - {e}")
    
    # Protocol status
    protocols = [
        ('air_protocol', 'Air (UBEC)'),
        ('water_protocol', 'Water (UBECrc)'),
        ('earth_protocol', 'Earth (UBECgpi)'),
        ('fire_protocol', 'Fire (UBECtt)')
    ]
    
    logger.info("\n🌟 Protocols:")
    for service_name, display_name in protocols:
        try:
            protocol = await registry.get(service_name)
            logger.info(f"  {display_name}: Initialized")
        except Exception as e:
            logger.info(f"  {display_name}: Not available")
    
    # Additional services status
    additional_services = [
        ('sync', 'Synchronization'),
        ('analytics', 'Analytics'),
        ('holonic', 'Holonic Evaluator'),
        ('visualizer', 'Visualizer'),
        ('bioregion_manager', 'Bioregion Manager'),
        ('api_service', 'API Service')
    ]
    
    logger.info("\n🔧 Services:")
    for service_name, display_name in additional_services:
        try:
            service = await registry.get(service_name)
            logger.info(f"  {display_name}: Initialized")
        except Exception as e:
            logger.info(f"  {display_name}: Not available")
    
    logger.info("\n" + "=" * 70)


async def handle_discover(registry: ServiceRegistry, max_accounts: int):
    """
    Discover token holders using the synchronizer service.
    
    Discovery functionality is integrated into the sync service.
    
    Args:
        registry: Service registry
        max_accounts: Maximum accounts to discover
    """
    logger.info("=" * 70)
    logger.info(f"DISCOVERING TOKEN HOLDERS (Max: {max_accounts})")
    logger.info("=" * 70)
    
    # Discovery is handled by the sync service
    sync = await registry.get('sync')
    
    # Use the synchronizer's discover_accounts method
    results = await sync.discover_accounts(max_accounts=max_accounts)
    
    logger.info(f"\n✅ Discovery complete:")
    logger.info(f"  Total discovered: {results.get('accounts_discovered', 0)}")
    logger.info(f"  Accounts processed: {results.get('accounts_processed', 0)}")
    logger.info("=" * 70)


async def handle_sync(
    registry: ServiceRegistry,
    sync_type: str,
    max_accounts: Optional[int],
    force: bool
):
    """
    Synchronize blockchain data.
    
    Args:
        registry: Service registry
        sync_type: Type of sync (all, UBEC, UBECrc, UBECgpi, UBECtt)
        max_accounts: Maximum accounts to sync
        force: Force full resync
    """
    logger.info("=" * 70)
    logger.info(f"SYNCHRONIZING BLOCKCHAIN DATA (Type: {sync_type})")
    logger.info("=" * 70)
    
    sync = await registry.get('sync')
    
    if sync_type == 'all':
        results = await sync.sync_all(
            max_accounts=max_accounts,
            force=force
        )
    else:
        results = await sync.sync_protocol(
            protocol=sync_type,
            max_accounts=max_accounts,
            force=force
        )
    
    logger.info(f"\n✅ Sync complete:")
    logger.info(f"  Accounts synced: {results.get('accounts_synced', 0)}")
    logger.info(f"  Transactions: {results.get('transactions', 0)}")
    logger.info(f"  Duration: {results.get('duration', 'N/A')}")
    logger.info("=" * 70)


async def handle_analytics(registry: ServiceRegistry, analysis_type: str):
    """
    Run analytics.
    
    Args:
        registry: Service registry
        analysis_type: Type of analysis
    """
    logger.info("=" * 70)
    logger.info(f"RUNNING ANALYTICS (Type: {analysis_type})")
    logger.info("=" * 70)
    
    analytics = await registry.get('analytics')
    
    if analysis_type == 'overview':
        results = await analytics.generate_overview()
    elif analysis_type == 'holders':
        results = await analytics.analyze_holders()
    elif analysis_type == 'metrics':
        results = await analytics.calculate_metrics()
    else:
        results = {'error': f'Unknown analysis type: {analysis_type}'}
    
    logger.info("\n📊 Analytics Results:")
    for key, value in results.items():
        logger.info(f"  {key}: {value}")
    logger.info("=" * 70)


async def handle_visualize(
    registry: ServiceRegistry,
    action: str,
    format: str,
    include_advanced: bool
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
    logger.info(f"GENERATING VISUALIZATIONS (Action: {action}, Format: {format})")
    logger.info("=" * 70)
    
    visualizer = await registry.get('visualizer')
    
    if action == 'report':
        output_file = await visualizer.generate_report(
            format=format,
            include_advanced=include_advanced
        )
        logger.info(f"\n✅ Report generated: {output_file}")
    elif action == 'all':
        results = await visualizer.generate_all(format=format)
        logger.info(f"\n✅ Generated {len(results)} visualizations")
    elif action == 'chart':
        chart_file = await visualizer.generate_chart()
        logger.info(f"\n✅ Chart generated: {chart_file}")
    
    logger.info("=" * 70)


async def handle_protocol_health(registry: ServiceRegistry):
    """
    Check protocol health.
    
    Args:
        registry: Service registry
    """
    logger.info("=" * 70)
    logger.info("PROTOCOL HEALTH CHECK")
    logger.info("=" * 70)
    
    protocols = [
        ('air_protocol', 'Air'),
        ('water_protocol', 'Water'),
        ('earth_protocol', 'Earth'),
        ('fire_protocol', 'Fire')
    ]
    
    for service_name, element in protocols:
        protocol = await registry.get(service_name)
        health = await protocol.check_health()
        
        status_symbol = "✅" if health['status'] == 'healthy' else "❌"
        
        logger.info(f"\n{status_symbol} {element} Protocol ({protocol.asset_code}):")
        logger.info(f"  Status: {health['status']}")
        logger.info(f"  Accounts: {health['details'].get('cached_accounts', 0)}")
        logger.info(f"  Initialized: {health['details'].get('initialized', False)}")
    
    logger.info("\n" + "=" * 70)


async def handle_serve(registry: ServiceRegistry, host: str = '0.0.0.0', 
                      port: int = 8000, reload: bool = False):
    """
    Start the FastAPI backend server.
    
    This exposes REST endpoints for the www server to consume.
    
    Args:
        registry: Service registry
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
    """
    logger.info("=" * 70)
    logger.info(f"STARTING API SERVER (http://{host}:{port})")
    logger.info("=" * 70)
    
    # Get the API service
    api_service = await registry.get('api_service')
    
    # The FastAPI app is available at api_service.app
    app = api_service.app
    
    logger.info(f"\n✅ API Server ready")
    logger.info(f"Swagger docs: http://{host}:{port}/docs")
    logger.info(f"ReDoc: http://{host}:{port}/redoc")
    logger.info(f"Health: http://{host}:{port}/health")
    logger.info("\nPress Ctrl+C to stop")
    logger.info("=" * 70)
    
    # Run the server
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


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
    
    # Serve command (NEW)
    serve_parser = subparsers.add_parser('serve', help='Start API server')
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
    logger.info("║" + " " * 15 + "UBEC Protocol Suite v3.0.0" + " " * 27 + "║")
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
