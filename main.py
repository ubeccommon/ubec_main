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

# ========================================================================
# IMPORT CORE COMPONENTS
# Principle #3: Service Registry - Central orchestration
# ========================================================================

from core.service_registry import ServiceRegistry
from core.db.database_manager import DatabaseManager
from core.utils.health_check import ServiceHealthCheck
from core.utils.logger import setup_logging

# ========================================================================
# LOGGING SETUP
# Principle #11: Comprehensive Documentation
# ========================================================================

# Setup logging first thing
setup_logging()
logger = logging.getLogger(__name__)

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
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create database manager
        db = DatabaseManager(
            database_url=database_url,
            schema=primary_schema,
            search_path=search_path
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
        
        from core.config.config_manager import ConfigManager
        
        db = await registry.get('database')
        config = ConfigManager(db)
        await config.initialize()
        
        logger.info("✓ Configuration service created")
        return config
    
    registry.register_factory(
        'config',
        create_config,
        dependencies=['database']
    )
    
    # ========================================================================
    # STELLAR CLIENT SERVICE
    # ========================================================================
    
    async def create_stellar_client(registry: ServiceRegistry):
        """
        Create Stellar blockchain client with rate limiting.
        
        Principle #9: Integrated Rate Limiting
        """
        logger.info("Creating Stellar client service...")
        
        from core.stellar.stellar_client import StellarClient
        
        config = await registry.get('config')
        
        # Get Stellar network configuration
        network = await config.get('stellar_network', 'mainnet')
        horizon_url = await config.get('stellar_horizon_url', 
                                       'https://horizon.stellar.org')
        
        # Get rate limiting configuration from database
        rate_limit = await config.get('rate_limit_requests', 3000)
        rate_period = await config.get('rate_limit_period', 3600)
        
        stellar = StellarClient(
            network=network,
            horizon_url=horizon_url,
            rate_limit_requests=rate_limit,
            rate_limit_period=rate_period
        )
        
        await stellar.initialize()
        
        logger.info("✓ Stellar client service created")
        return stellar
    
    registry.register_factory(
        'stellar_client',
        create_stellar_client,
        dependencies=['config']
    )
    
    # ========================================================================
    # PROTOCOL SERVICES (4 Elements)
    # ========================================================================
    
    async def create_air_protocol(registry: ServiceRegistry):
        """Create Air Protocol service (UBEC - Diversity)"""
        logger.info("Creating Air Protocol service...")
        
        from core.protocols.UBEC_protocol import create_ubec_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        # Get Air token configuration from database
        air_config = {
            'asset_code': 'UBEC',
            'issuer': await config.get('ubec_issuer'),
            'element': 'Air',
            'ubuntu_principle': 'Diversity'
        }
        
        service = await create_ubec_service(
            db_manager=db,
            config=air_config,
            stellar_client=stellar
        )
        
        logger.info("✓ Air Protocol service created")
        return service
    
    registry.register_factory(
        'air_protocol',
        create_air_protocol,
        dependencies=['database', 'config', 'stellar_client']
    )
    
    async def create_water_protocol(registry: ServiceRegistry):
        """Create Water Protocol service (UBECrc - Reciprocity)"""
        logger.info("Creating Water Protocol service...")
        
        from core.protocols.water_protocol import create_water_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        water_config = {
            'asset_code': 'UBECrc',
            'issuer': await config.get('ubecrc_issuer'),
            'element': 'Water',
            'ubuntu_principle': 'Reciprocity'
        }
        
        service = await create_water_service(
            db_manager=db,
            config=water_config,
            stellar_client=stellar
        )
        
        logger.info("✓ Water Protocol service created")
        return service
    
    registry.register_factory(
        'water_protocol',
        create_water_protocol,
        dependencies=['database', 'config', 'stellar_client']
    )
    
    async def create_earth_protocol(registry: ServiceRegistry):
        """Create Earth Protocol service (UBECgpi - Mutualism)"""
        logger.info("Creating Earth Protocol service...")
        
        from core.protocols.earth_protocol import create_earth_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        earth_config = {
            'asset_code': 'UBECgpi',
            'issuer': await config.get('ubecgpi_issuer'),
            'element': 'Earth',
            'ubuntu_principle': 'Mutualism'
        }
        
        service = await create_earth_service(
            db_manager=db,
            config=earth_config,
            stellar_client=stellar
        )
        
        logger.info("✓ Earth Protocol service created")
        return service
    
    registry.register_factory(
        'earth_protocol',
        create_earth_protocol,
        dependencies=['database', 'config', 'stellar_client']
    )
    
    async def create_fire_protocol(registry: ServiceRegistry):
        """Create Fire Protocol service (UBECtt - Regeneration)"""
        logger.info("Creating Fire Protocol service...")
        
        from core.protocols.fire_protocol import create_fire_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        fire_config = {
            'asset_code': 'UBECtt',
            'issuer': await config.get('ubectt_issuer'),
            'element': 'Fire',
            'ubuntu_principle': 'Regeneration'
        }
        
        service = await create_fire_service(
            db_manager=db,
            config=fire_config,
            stellar_client=stellar
        )
        
        logger.info("✓ Fire Protocol service created")
        return service
    
    registry.register_factory(
        'fire_protocol',
        create_fire_protocol,
        dependencies=['database', 'config', 'stellar_client']
    )
    
    # ========================================================================
    # BIOREGION MANAGER SERVICE (Community Organization)
    # ========================================================================
    
    async def create_bioregion_manager(registry: ServiceRegistry):
        """
        Create Bioregion Manager service for tracking geographic communities.
        
        Principle #10: Clear Separation of Concerns - Community management isolated
        """
        logger.info("Creating Bioregion Manager service...")
        
        from core.services.community.bioregion_manager import create_bioregion_manager
        
        # Factory function already handles initialization
        service = await create_bioregion_manager(registry)
        
        logger.info("✓ Bioregion Manager service created")
        return service
    
    registry.register_factory(
        'bioregion_manager',
        create_bioregion_manager,
        dependencies=['database']
    )
    
    # ========================================================================
    # DATA SYNCHRONIZER SERVICE
    # ========================================================================
    
    async def create_data_synchronizer(registry: ServiceRegistry):
        """Create Data Synchronizer service (blockchain to database sync)"""
        logger.info("Creating Data Synchronizer service...")
        
        from core.services.sync.data_synchronizer import create_synchronizer
        
        service = await create_synchronizer(registry)
        
        logger.info("✓ Data Synchronizer service created")
        return service
    
    registry.register_factory(
        'synchronizer',
        create_data_synchronizer,
        dependencies=[
            'database', 
            'stellar_client',
            'air_protocol',
            'water_protocol',
            'earth_protocol',
            'fire_protocol'
        ]
    )
    
    # ========================================================================
    # ANALYTICS SERVICE
    # ========================================================================
    
    async def create_analytics_service(registry: ServiceRegistry):
        """Create Analytics service for token and network analysis"""
        logger.info("Creating Analytics service...")
        
        from core.services.analytics.analytics_service import create_analytics_service
        
        service = await create_analytics_service(registry)
        
        logger.info("✓ Analytics service created")
        return service
    
    registry.register_factory(
        'analytics',
        create_analytics_service,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # HOLONIC EVALUATOR SERVICE
    # ========================================================================
    
    async def create_holonic_evaluator(registry: ServiceRegistry):
        """Create Holonic Evaluator service (Ubuntu principles assessment)"""
        logger.info("Creating Holonic Evaluator service...")
        
        from core.services.holonic.holonic_evaluator import create_holonic_evaluator
        
        service = await create_holonic_evaluator(registry)
        
        logger.info("✓ Holonic Evaluator service created")
        return service
    
    registry.register_factory(
        'holonic_evaluator',
        create_holonic_evaluator,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # VISUALIZER SERVICE
    # ========================================================================
    
    async def create_visualizer(registry: ServiceRegistry):
        """Create Visualizer service (charts and reports)"""
        logger.info("Creating Visualizer service...")
        
        from core.services.visualization.visualizer import create_visualizer
        
        service = await create_visualizer(registry)
        
        logger.info("✓ Visualizer service created")
        return service
    
    registry.register_factory(
        'visualizer',
        create_visualizer,
        dependencies=['database', 'analytics']
    )
    
    # ========================================================================
    # DISTRIBUTION MANAGER SERVICE
    # ========================================================================
    
    async def create_distribution_manager(registry: ServiceRegistry):
        """Create Distribution Manager service"""
        logger.info("Creating Distribution Manager service...")
        
        from core.services.distribution.distribution_manager import create_distribution_manager
        
        service = await create_distribution_manager(registry)
        
        logger.info("✓ Distribution Manager service created")
        return service
    
    registry.register_factory(
        'distribution_manager',
        create_distribution_manager,
        dependencies=['database', 'config']
    )
    
    # ========================================================================
    # AUDIT SERVICE
    # ========================================================================
    
    async def create_audit_service(registry: ServiceRegistry):
        """Create Audit service for comprehensive change tracking"""
        logger.info("Creating Audit service...")
        
        from core.services.audit.audit_service import create_audit_service
        
        service = await create_audit_service(registry)
        
        logger.info("✓ Audit service created")
        return service
    
    registry.register_factory(
        'audit_service',
        create_audit_service,
        dependencies=['database']
    )
    
    # ========================================================================
    # API SERVICE (NEW - Backend API for www server)
    # ========================================================================
    
    async def create_api_service(registry: ServiceRegistry):
        """
        Create Backend API service for www server integration.
        
        This service provides REST endpoints for the public website,
        integrating real bioregion data and protocol metrics.
        
        Principle #2: Service Pattern - API as a service
        Principle #3: Service Registry - Dependency injection
        Principle #10: Separation of Concerns - API layer isolated
        """
        logger.info("Creating Backend API service...")
        
        from services.api.api_service import create_backend_api_service
        
        # Factory function handles initialization
        service = await create_backend_api_service(registry)
        
        logger.info("✓ Backend API service created")
        return service
    
    registry.register_factory(
        'api_service',
        create_api_service,
        dependencies=['database', 'bioregion_manager']
    )
    
    # ========================================================================
    # REGISTRATION COMPLETE
    # ========================================================================
    
    logger.info("=" * 70)
    logger.info(f"✓ REGISTERED {len(registry.list_services())} SERVICES")
    logger.info("=" * 70)
    
    return registry


# ========================================================================
# COMMAND HANDLERS
# Principle #2: Service Pattern - All operations through registry
# ========================================================================

async def handle_health_check(registry: ServiceRegistry, detailed: bool = False):
    """
    Check system health across all services.
    
    Principle #7: Per-Asset Monitoring - Individual service health checks
    """
    logger.info("=" * 70)
    logger.info("SYSTEM HEALTH CHECK")
    logger.info("=" * 70)
    
    health = await registry.health_check(detailed=detailed)
    
    # Display overall status
    status_symbol = "✅" if health['status'] == 'healthy' else "⚠️"
    logger.info(f"\nOverall Status: {status_symbol} {health['status'].upper()}")
    logger.info(f"Services Checked: {health['services_checked']}")
    logger.info(f"Healthy Services: {health['healthy_count']}")
    logger.info(f"Unhealthy Services: {health['unhealthy_count']}")
    
    # Display individual service health if detailed
    if detailed and 'service_health' in health:
        logger.info("\nService Health Details:")
        logger.info("-" * 70)
        
        for service_name, service_health in health['service_health'].items():
            status = service_health.get('status', 'unknown')
            status_symbol = "✅" if status == 'healthy' else "⚠️"
            
            logger.info(f"\n{status_symbol} {service_name}: {status}")
            
            if 'details' in service_health:
                for key, value in service_health['details'].items():
                    logger.info(f"  - {key}: {value}")
    
    logger.info("=" * 70)
    
    return health


async def handle_status(registry: ServiceRegistry):
    """
    Display system status information.
    
    Shows:
    - Service registry information
    - Initialized services
    - Dependencies
    - Overall system state
    """
    logger.info("=" * 70)
    logger.info("SYSTEM STATUS")
    logger.info("=" * 70)
    
    info = registry.get_info()
    
    logger.info(f"\nRegistry Status: {'✅ Initialized' if info['initialized'] else '⚠️ Not Initialized'}")
    logger.info(f"Total Services: {info['total_services']}")
    logger.info(f"Total Factories: {info['total_factories']}")
    
    logger.info("\nInitialization Order:")
    logger.info("-" * 70)
    for i, service in enumerate(info['initialization_order'], 1):
        logger.info(f"{i}. {service}")
    
    logger.info("\nService Details:")
    logger.info("-" * 70)
    for service_name, service_info in info['services'].items():
        status = service_info['status']
        status_symbol = "✅" if status == 'ready' else "⚠️"
        
        logger.info(f"\n{status_symbol} {service_name} ({status})")
        
        if service_info['dependencies']:
            logger.info(f"  Dependencies: {', '.join(service_info['dependencies'])}")
        
        if service_info['is_initialized']:
            logger.info(f"  Type: {service_info['service_type']}")
    
    logger.info("\n" + "=" * 70)


async def handle_discover(registry: ServiceRegistry, max_accounts: int = 100):
    """
    Discover token holders on the Stellar network.
    
    Args:
        registry: Service registry
        max_accounts: Maximum number of accounts to discover
    """
    logger.info("=" * 70)
    logger.info(f"DISCOVERING TOKEN HOLDERS (max: {max_accounts})")
    logger.info("=" * 70)
    
    synchronizer = await registry.get('synchronizer')
    
    # Discover for each protocol
    for protocol_name in ['air_protocol', 'water_protocol', 'earth_protocol', 'fire_protocol']:
        protocol = await registry.get(protocol_name)
        element = protocol.element
        asset_code = protocol.asset_code
        
        logger.info(f"\nDiscovering {element} ({asset_code}) holders...")
        
        try:
            holders = await synchronizer.discover_token_holders(
                asset_code=asset_code,
                issuer=protocol.issuer,
                max_accounts=max_accounts
            )
            
            logger.info(f"✓ Found {len(holders)} {element} holders")
            
        except Exception as e:
            logger.error(f"❌ Error discovering {element} holders: {e}")
    
    logger.info("\n" + "=" * 70)


async def handle_sync(registry: ServiceRegistry, sync_type: str = 'all', 
                      max_accounts: Optional[int] = None, force: bool = False):
    """
    Synchronize blockchain data to database.
    
    Args:
        registry: Service registry
        sync_type: Type of sync ('all', 'UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
        max_accounts: Maximum accounts to sync (None = all)
        force: Force full resync
    """
    logger.info("=" * 70)
    logger.info(f"SYNCHRONIZING DATA (type: {sync_type}, force: {force})")
    logger.info("=" * 70)
    
    synchronizer = await registry.get('synchronizer')
    
    if sync_type == 'all':
        # Sync all tokens
        logger.info("\nSyncing all tokens...")
        await synchronizer.sync_all_tokens(max_accounts=max_accounts, force=force)
    else:
        # Sync specific token
        logger.info(f"\nSyncing {sync_type}...")
        await synchronizer.sync_token(
            asset_code=sync_type,
            max_accounts=max_accounts,
            force=force
        )
    
    logger.info("\n✓ Synchronization complete")
    logger.info("=" * 70)


async def handle_analytics(registry: ServiceRegistry, analysis_type: str = 'overview'):
    """
    Run analytics and display results.
    
    Args:
        registry: Service registry
        analysis_type: Type of analysis ('overview', 'holders', 'metrics')
    """
    logger.info("=" * 70)
    logger.info(f"RUNNING ANALYTICS (type: {analysis_type})")
    logger.info("=" * 70)
    
    analytics = await registry.get('analytics')
    
    if analysis_type == 'overview':
        results = await analytics.get_overview()
    elif analysis_type == 'holders':
        results = await analytics.get_top_holders()
    elif analysis_type == 'metrics':
        results = await analytics.get_detailed_metrics()
    else:
        logger.error(f"Unknown analysis type: {analysis_type}")
        return
    
    # Display results
    logger.info("\nAnalytics Results:")
    logger.info("-" * 70)
    
    import json
    logger.info(json.dumps(results, indent=2, default=str))
    
    logger.info("\n" + "=" * 70)


async def handle_visualize(registry: ServiceRegistry, action: str = 'report',
                          format: str = 'html', include_advanced: bool = False):
    """
    Generate visualizations and reports.
    
    Args:
        registry: Service registry
        action: Visualization action ('report', 'all', 'chart')
        format: Output format ('html', 'pdf')
        include_advanced: Include advanced visualizations
    """
    logger.info("=" * 70)
    logger.info(f"GENERATING VISUALIZATIONS (action: {action}, format: {format})")
    logger.info("=" * 70)
    
    visualizer = await registry.get('visualizer')
    
    if action == 'report':
        output_path = await visualizer.generate_report(
            format=format,
            include_advanced=include_advanced
        )
        logger.info(f"\n✓ Report generated: {output_path}")
        
    elif action == 'all':
        output_paths = await visualizer.generate_all_charts(
            include_advanced=include_advanced
        )
        logger.info(f"\n✓ Generated {len(output_paths)} visualizations")
        
    elif action == 'chart':
        # Would need additional params for specific chart type
        logger.info("Chart generation requires chart_type parameter")
    
    logger.info("=" * 70)


async def handle_protocol_health(registry: ServiceRegistry):
    """
    Check health of all protocol services.
    """
    logger.info("=" * 70)
    logger.info("PROTOCOL HEALTH CHECK")
    logger.info("=" * 70)
    
    protocols = ['air_protocol', 'water_protocol', 'earth_protocol', 'fire_protocol']
    
    for protocol_name in protocols:
        protocol = await registry.get(protocol_name)
        health = await protocol.health_check()
        
        status_symbol = "✅" if health['status'] == 'healthy' else "⚠️"
        element = health['details']['element']
        
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
    
    # Display header
    logger.info("")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " " * 15 + "UBEC Protocol Suite v3.0.0" + " " * 27 + "║")
    logger.info("║" + " " * 18 + "Main Orchestrator" + " " * 33 + "║")
    logger.info("╚" + "═" * 68 + "╝")
    logger.info("")
    
    # Register all services
    registry = register_core_services()
    
    try:
        # Initialize services using context manager
        async with registry:
            logger.info("\n✅ All services initialized successfully\n")
            
            # Execute command
            if args.command == 'health':
                await handle_health_check(registry, detailed=args.detailed)
                
            elif args.command == 'status':
                await handle_status(registry)
                
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
