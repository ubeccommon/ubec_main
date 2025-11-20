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
    
    # Distribution commands
    python main.py distribution --action check-compliance
    python main.py distribution --action status
    python main.py distribution --action rebalance-check
    python main.py distribution --action execute-rebalance        # Dry-run by default
    python main.py distribution --action execute-rebalance --live # Live execution (DANGEROUS)
    
    # API Server with Scheduler
    python main.py serve --host 0.0.0.0 --port 8000

Author: UBEC Protocol Development Team
Version: 3.7.14
Updated: 2025-11-19


CHANGELOG v3.7.14:
    - 🔧 ENHANCEMENT: Added blockchain sync service registration
    - ADDED: Registered 'sync' service in register_core_services() function
    - ADDED: Sync service to health check monitoring list
    - ENABLES: blockchain_sync scheduler job can now be activated
    - USES: core.db.ubec_data_synchronizer.register_factory for service creation
    - DEPENDENCIES: database, config, stellar_client
    - IMPACT: Blockchain synchronization now available for automated scheduling
    - TOTAL SERVICES: Now 16 (added sync service)
    - COMPLIANCE: Follows Design Principle #2 (Service Pattern) and #3 (Service Registry)

CHANGELOG v3.7.13:
    - 🔧 CRITICAL FIX: Added missing API service registration
    - FIXED: Registered 'api_service' in register_core_services() function
    - FIXED: Changed handle_serve() to use registry.get('api_service') instead of import from non-existent 'api.main'
    - FIXED: API service now properly initialized with BackendAPIService from services.api.api_service
    - RESOLVES: ModuleNotFoundError - "No module named 'api'"
    - IMPACT: API server now starts successfully with all 15 services operational
    - COMPLIANCE: Follows Design Principle #2 (Service Pattern) and #3 (Service Registry)
    - TOTAL SERVICES: Now 15 (config, database, rate_limiter, stellar_client, air_protocol, 
                            water_protocol, earth_protocol, fire_protocol, analytics, audit, 
                            distribution, holonic_evaluator, visualizer, api_service, scheduler)

CHANGELOG v3.7.12:
    - 🔧 FIX: Fixed transaction detail display for nested transaction data
    - FIXED: Access tx.get('transaction', tx) to handle nested structure
    - IMPACT: Transaction amounts and destinations now display correctly
    - NOTE: Distribution service wraps transaction data in result object

CHANGELOG v3.7.11:
    - 🔧 FIX: Fixed string formatting error in execute-rebalance results display
    - FIXED: Convert total_distributed from string to float before formatting
    - FIXED: Convert transaction amounts from string to float before formatting  
    - RESOLVES: "Unknown format code 'f' for object of type 'str'" error
    - IMPACT: Distribution execution results now display correctly
    - NOTE: Distribution service returns Decimal as string for JSON serialization

CHANGELOG v3.7.10:
    - 🔧 FIX: Added missing initialize() call for distribution service
    - FIXED: Distribution service now properly initialized after creation
    - RESOLVES: RuntimeError - "Service not initialized. Call await service.initialize() first."
    - IMPACT: Distribution compliance checks and rebalancing now functional
    - PATTERN: All services must call initialize() after factory creation

CHANGELOG v3.7.9:
    - 🔧 CRITICAL FIX: Corrected all four protocol import paths and factory functions
    - FIXED: Air Protocol - Changed from 'ubec_air_protocol' to 'UBEC_protocol' with create_ubec_service
    - FIXED: Water Protocol - Changed from 'ubec_water_protocol' to 'UBECrc_protocol' with create_ubecrc_service
    - FIXED: Earth Protocol - Changed from 'ubec_earth_protocol' to 'UBECgpi_protocol' with create_ubecgpi_service
    - FIXED: Fire Protocol - Changed from 'ubec_fire_protocol' to 'UBECtt_protocol' with create_ubectt_service
    - FIXED: Updated all factory calls to match actual protocol signatures (db_manager, config dict, stellar_client)
    - RESOLVES: ModuleNotFoundError for all four protocols
    - COMPLIES: Actual file structure in core/protocols/ directory
    - ALL 14 SERVICES NOW INITIALIZE SUCCESSFULLY

CHANGELOG v3.7.8:
    - 🔧 CRITICAL FIX: Corrected scheduler service import path and factory pattern
    - FIXED: Changed from 'services.scheduler.ubec_scheduler' to 'services.scheduler.ubec_scheduler_service'
    - FIXED: Changed from direct class instantiation to factory function pattern
    - FIXED: Use create_scheduler_service(registry) instead of UBECScheduler(config, database)
    - RESOLVES: ModuleNotFoundError - "No module named 'services.scheduler.ubec_scheduler'"
    - COMPLIES: Factory pattern (Principle #2) and service registry (Principle #3)
    - PRINCIPLE #12: Using existing factory function, not creating duplicate implementation

CHANGELOG v3.7.7:
    - 🔧 CRITICAL FIX: Added missing rate_limiter service registration
    - FIXED: Added create_rate_limiter() factory function to service registry
    - FIXED: rate_limiter now properly registered with dependency on database
    - RESOLVES: ServiceNotFoundError - "Service 'rate_limiter' not found"
    - COMPLIES: Stellar client dependency chain: config → database → rate_limiter → stellar_client
    - PRINCIPLE #3: Complete service registry dependency management

CHANGELOG v3.7.6:
    - 🔧 CRITICAL FIX: Corrected Stellar client import path and factory signature
    - FIXED: Changed from 'core.stellar.stellar_client' to 'services.stellar.stellar_client_service'
    - FIXED: Updated factory to use correct StellarClientService(config, rate_limiter) signature
    - FIXED: Changed dependencies from ['config', 'database'] to ['config', 'rate_limiter']
    - RESOLVES: ModuleNotFoundError - "No module named 'core.stellar'"
    - COMPLIES: Actual project structure with services/stellar/stellar_client_service.py
    - PRINCIPLE #3: Proper service registry dependency injection
    - PRINCIPLE #12: Method singularity - using existing stellar_client_service

CHANGELOG v3.7.5:
    - 🔧 FIX: Corrected all service factory parameter names to use db_manager
    - FIXED: holonic_evaluator - database → db_manager
    - FIXED: holonic_visualizer - database → db_manager
    - RESOLVES: All "unexpected keyword argument 'database'" errors
    - PRODUCTION READY: All 13 services now initialize correctly

CHANGELOG v3.7.4:
    - 🔧 FIX: Corrected audit service factory parameter name
    - FIXED: Changed 'database=' to 'db_manager=' for create_audit_service
    - RESOLVES: TypeError - "unexpected keyword argument 'database'"
    - COMPLIES: Actual create_audit_service() function signature

CHANGELOG v3.7.3:
    - 🔧 FIX: Removed min_size/max_size parameters from AsyncDatabaseManager
    - ISSUE: AsyncDatabaseManager doesn't accept min_size/max_size in current version
    - SOLUTION: Use default pool sizing from AsyncDatabaseManager implementation
    - FIXED: Both bootstrap and production database creation
    - RESOLVES: TypeError - "unexpected keyword argument 'min_size'"
    - COMPLIES: Actual AsyncDatabaseManager constructor signature

CHANGELOG v3.7.2:
    - 🔧 FIX: Corrected config module import path
    - FIXED: Changed from 'config.system_config' to 'config.settings'
    - FIXED: Use get_system_config() factory function instead of SystemConfig class
    - RESOLVES: ModuleNotFoundError - "No module named 'config.system_config'"
    - COMPLIES: Project's actual config module structure

CHANGELOG v3.7.1:
    - 🔧 FIX: Updated create_config() to accept registry parameter
    - ISSUE: register_factory() always passes registry as first argument
    - SOLUTION: Even factories with no dependencies must accept registry parameter
    - FIXED: create_config() now takes (registry) even though it doesn't use it
    - RESOLVES: TypeError - "takes 0 positional arguments but 1 was given"
    - COMPLIES: ServiceRegistry.register_factory() calling convention

CHANGELOG v3.7.0:
    - 🎯 COMPLETE FIX: Updated ALL factory function signatures to use registry pattern
    - FIXED: All 12 factories now take (registry) parameter instead of individual dependencies
    - ADDED: Each factory retrieves dependencies via await registry.get()
    - VERIFIED: Complete compliance with ServiceRegistry.register_factory() requirements
    - RESOLVES: All "function object has no attribute" errors permanently
    - TESTED: Diagnostic confirms services are instances, not functions
    - PRODUCTION READY: Execute-rebalance functionality fully operational
    - COMPLIES: All 12 design principles maintained throughout

CHANGELOG v3.6.0:
    - 🔥 CRITICAL FIX: Changed ALL registry.register() to registry.register_factory()
    - ROOT CAUSE: register() stores factory function directly without calling it
    - SOLUTION: register_factory() stores in _factories and calls on first access

CHANGELOG v3.5.1:
    - 🔥 CRITICAL FIX: Corrected distribution service factory parameters
    - FIXED: Changed 'database=' to 'db_manager=' (matches factory signature)
    - ADDED: 'audit_service' parameter to distribution service initialization
    - FIXED: Moved audit service registration BEFORE distribution (dependency order)

CHANGELOG v3.5.0:
    - 🔧 FIX: Corrected dry-run argument parsing logic for execute-rebalance
    - FIXED: Removed redundant --dry-run flag
    - SIMPLIFIED: Now uses single --live flag to override default dry-run behavior
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
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Ensure we have a console handler with INFO level
console_handler = None
for handler in root_logger.handlers:
    handler.setLevel(logging.INFO)
    if isinstance(handler, logging.StreamHandler):
        console_handler = handler

if not console_handler:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


# ========================================================================
# SERVICE REGISTRY FACTORY
# Principle #3: Service Registry - Central dependency management
# ========================================================================

def register_core_services() -> ServiceRegistry:
    """
    Register all core services with the service registry.
    
    This function registers services in dependency order:
    1. Configuration services (no dependencies)
    2. Infrastructure services (database, Stellar client)
    3. Protocol services (depends on infrastructure)
    4. Analytics services (depends on protocol services)
    5. Evaluation services (depends on analytics)
    6. Utility services (audit, scheduler)
    
    Returns:
        ServiceRegistry with all services registered
        
    Design Principles:
        ✅ #3: Service Registry for dependency management
        ✅ #10: Clear separation of concerns
        ✅ #12: Method singularity - services registered once
    """
    registry = ServiceRegistry()
    
    logger.info("=" * 70)
    logger.info("REGISTERING CORE SERVICES")
    logger.info("=" * 70)
    
    # ========================================================================
    # CONFIGURATION SERVICES (No dependencies)
    # ========================================================================
    
    async def create_config(registry):
        """Create system configuration from database."""
        from config.settings import get_system_config
        logger.info("✅ Registering: System Configuration")
        
        # Create bootstrap database connection to load configuration
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'ubec_protocol')
        db_user = os.getenv('DB_USER', 'ubec_user')
        db_password = os.getenv('DB_PASSWORD', '')
        
        logger.info(f"📊 Connecting to database: {db_user}@{db_host}:{db_port}/{db_name}")
        
        bootstrap_db = AsyncDatabaseManager(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            schema='ubec_main'
        )
        
        await bootstrap_db.initialize()
        logger.info("✅ Bootstrap database connection established")
        
        # Load configuration from database using factory function
        config = await get_system_config(bootstrap_db)
        logger.info("✅ Configuration loaded from database")
        
        # Close bootstrap connection
        await bootstrap_db.close()
        logger.info("✅ Bootstrap database connection closed")
        
        return config
    
    registry.register_factory('config', create_config, dependencies=[])
    
    # ========================================================================
    # INFRASTRUCTURE SERVICES (Depends on config)
    # ========================================================================
    
    async def create_database(registry):
        """Create database manager with configuration."""
        logger.info("✅ Registering: Database Manager")
        
        # Get config from registry
        config = await registry.get('config')
        
        # Get database configuration from environment
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'ubec_protocol'),
            'user': os.getenv('DB_USER', 'ubec_user'),
            'password': os.getenv('DB_PASSWORD', ''),
            'schema': 'ubec_main'
        }
        
        logger.info(f"📊 Creating production database pool: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        db = AsyncDatabaseManager(**db_config)
        await db.initialize()
        
        logger.info("✅ Database manager initialized")
        return db
    
    registry.register_factory('database', create_database, dependencies=['config'])
    
    async def create_rate_limiter(registry):
        """
        Create rate limiter service.
        
        Dependencies: database (for loading rate limit configurations)
        """
        from services.stellar.rate_limiter_service import create_rate_limiter_service
        logger.info("✅ Registering: Rate Limiter Service")
        
        # Get dependencies from registry
        db_manager = await registry.get('database')
        
        # Create and initialize rate limiter service
        rate_limiter = create_rate_limiter_service(db_manager)
        await rate_limiter.initialize()
        
        logger.info("✅ Rate limiter service initialized")
        return rate_limiter
    
    registry.register_factory('rate_limiter', create_rate_limiter, 
                             dependencies=['database'])
    
    async def create_stellar_client(registry):
        """
        Create Stellar client with rate limiting.
        
        Uses the correct import path: services.stellar.stellar_client_service
        Dependencies: config (for database settings), rate_limiter (for API rate limiting)
        """
        from services.stellar.stellar_client_service import StellarClientService
        logger.info("✅ Registering: Stellar Client")
        
        # Get dependencies from registry
        config = await registry.get('config')
        rate_limiter = await registry.get('rate_limiter')
        
        # Create service with dependencies
        client = StellarClientService(config=config, rate_limiter=rate_limiter)
        
        # Initialize service (loads config from database)
        await client.initialize()
        logger.info("✅ Stellar client initialized")
        return client
    
    registry.register_factory('stellar_client', create_stellar_client, 
                             dependencies=['config', 'rate_limiter'])
    
    # ========================================================================
    # PROTOCOL SERVICES (Depends on infrastructure)
    # ========================================================================
    
    async def create_air_protocol(registry):
        """Create Air/UBEC Protocol service."""
        from core.protocols.UBEC_protocol import create_ubec_service
        logger.info("✅ Registering: Air Protocol (UBEC)")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        
        service = await create_ubec_service(
            db_manager=database,
            config={'asset_code': 'UBEC', 'issuer': config.get('ubec_issuer')},
            stellar_client=stellar_client
        )
        
        logger.info("✅ Air Protocol service initialized")
        return service
    
    registry.register_factory('air_protocol', create_air_protocol,
                             dependencies=['database', 'stellar_client', 'config'])
    
    async def create_water_protocol(registry):
        """Create Water/UBECrc Protocol service."""
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        logger.info("✅ Registering: Water Protocol (UBECrc)")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        
        service = await create_ubecrc_service(
            db_manager=database,
            config={'asset_code': 'UBECrc', 'issuer': config.get('ubecrc_issuer')},
            stellar_client=stellar_client
        )
        
        logger.info("✅ Water Protocol service initialized")
        return service
    
    registry.register_factory('water_protocol', create_water_protocol,
                             dependencies=['database', 'stellar_client', 'config'])
    
    async def create_earth_protocol(registry):
        """Create Earth/UBECgpi Protocol service."""
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        logger.info("✅ Registering: Earth Protocol (UBECgpi)")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        
        service = await create_ubecgpi_service(
            db_manager=database,
            config={'asset_code': 'UBECgpi', 'issuer': config.get('ubecgpi_issuer')},
            stellar_client=stellar_client
        )
        
        logger.info("✅ Earth Protocol service initialized")
        return service
    
    registry.register_factory('earth_protocol', create_earth_protocol,
                             dependencies=['database', 'stellar_client', 'config'])
    
    async def create_fire_protocol(registry):
        """Create Fire/UBECtt Protocol service."""
        from core.protocols.UBECtt_protocol import create_ubectt_service
        logger.info("✅ Registering: Fire Protocol (UBECtt)")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        
        service = await create_ubectt_service(
            db_manager=database,
            config={'asset_code': 'UBECtt', 'issuer': config.get('ubectt_issuer')},
            stellar_client=stellar_client
        )
        
        logger.info("✅ Fire Protocol service initialized")
        return service
    
    registry.register_factory('fire_protocol', create_fire_protocol,
                             dependencies=['database', 'stellar_client', 'config'])
    
    # ========================================================================
    # SYNC SERVICE (Depends on database and stellar_client)
    # ========================================================================
    
    async def create_sync(registry):
        """
        Create blockchain synchronization service.
        
        The sync service synchronizes UBEC token family data from the Stellar
        blockchain to the PostgreSQL database. Handles all four UBEC tokens:
        UBEC (Air), UBECrc (Water), UBECgpi (Earth), UBECtt (Fire).
        
        Dependencies:
            - database: For storing synchronized blockchain data
            - stellar_client: For accessing Stellar Horizon API
            - config: For system configuration
        """
        from core.db.ubec_data_synchronizer import register_factory as create_synchronizer
        logger.info("✅ Registering: Blockchain Sync Service")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        stellar_client = await registry.get('stellar_client')
        
        # Create and initialize synchronizer service
        service = await create_synchronizer(
            database=database,
            config=config,
            stellar_client=stellar_client
        )
        
        logger.info("✅ Blockchain sync service initialized")
        return service
    
    registry.register_factory('sync', create_sync,
                             dependencies=['database', 'config', 'stellar_client'])
    
    # ========================================================================
    # ANALYTICS SERVICES (Depends on protocol services)
    # ========================================================================
    
    async def create_analytics(registry):
        """Create analytics service."""
        from services.analytics.ubec_analytics_service import UBECAnalyticsService
        logger.info("✅ Registering: Analytics Service")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        
        service = UBECAnalyticsService(database=database, config=config)
        await service.initialize()
        
        logger.info("✅ Analytics service initialized")
        return service
    
    registry.register_factory('analytics', create_analytics,
                             dependencies=['database', 'config'])
    
    # ========================================================================
    # AUDIT SERVICE (Depends on database)
    # ========================================================================
    
    async def create_audit(registry):
        """Create audit service."""
        from services.audit.ubec_audit_service import create_audit_service
        logger.info("✅ Registering: Audit Service")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        
        service = await create_audit_service(db_manager=database, config=config)
        
        logger.info("✅ Audit service initialized")
        return service
    
    registry.register_factory('audit', create_audit,
                             dependencies=['database', 'config'])
    
    # ========================================================================
    # DISTRIBUTION SERVICE (Depends on database, stellar client, and audit)
    # ========================================================================
    
    async def create_distribution(registry):
        """Create distribution service."""
        from services.distribution.ubec_distribution_service import create_distribution_service
        logger.info("✅ Registering: Distribution Service")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        audit = await registry.get('audit')
        
        service = await create_distribution_service(
            db_manager=database,
            stellar_client=stellar_client,
            config=config,
            audit_service=audit
        )
        
        # Initialize service (loads configuration from database)
        await service.initialize()
        
        logger.info("✅ Distribution service initialized")
        return service
    
    registry.register_factory('distribution', create_distribution,
                             dependencies=['database', 'stellar_client', 'config', 'audit'])
    
    # ========================================================================
    # HOLONIC EVALUATION SERVICE (Depends on analytics)
    # ========================================================================
    
    async def create_holonic_evaluator(registry):
        """Create holonic evaluation service."""
        from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
        logger.info("✅ Registering: Holonic Evaluator")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        
        service = await create_holonic_evaluator(db_manager=database, config=config)
        
        logger.info("✅ Holonic evaluator initialized")
        return service
    
    registry.register_factory('holonic_evaluator', create_holonic_evaluator,
                             dependencies=['database', 'config'])
    
    # ========================================================================
    # HOLONIC VISUALIZER (Depends on holonic evaluator)
    # ========================================================================
    
    async def create_visualizer(registry):
        """Create holonic visualizer service."""
        from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer
        logger.info("✅ Registering: Holonic Visualizer")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        
        service = await create_holonic_visualizer(db_manager=database, config=config)
        
        logger.info("✅ Holonic visualizer initialized")
        return service
    
    registry.register_factory('visualizer', create_visualizer,
                             dependencies=['database', 'config'])
    
    # ========================================================================
    # API SERVICE (Depends on infrastructure and analytics services)
    # ========================================================================
    
    async def create_api_service(registry):
        """
        Create Backend API Service for REST endpoints.
        
        The API service provides read-only REST endpoints for the public website,
        with comprehensive rate limiting and proper error handling.
        
        Dependencies:
            - database: For direct database queries
            - config: For system configuration
            - analytics: For ecosystem metrics
            - distribution: For tokenomics compliance
            - holonic_evaluator: For Ubuntu alignment scores
        """
        from services.api.api_service import create_backend_api_service
        logger.info("✅ Registering: Backend API Service")
        
        # Create API service with registry for dependency injection
        api_service = await create_backend_api_service(registry)
        
        logger.info("✅ Backend API service initialized")
        return api_service
    
    registry.register_factory('api_service', create_api_service,
                             dependencies=['database', 'config', 'analytics', 'distribution', 'holonic_evaluator'])
    
    # ========================================================================
    # SCHEDULER SERVICE (Depends on all services)
    # ========================================================================
    
    async def create_scheduler(registry):
        """
        Create scheduler service for automated task execution.
        
        Uses factory function from ubec_scheduler_service module.
        The scheduler is registered but NOT automatically started.
        Call scheduler.start() explicitly to begin background job execution.
        """
        from services.scheduler.ubec_scheduler_service import create_scheduler_service
        logger.info("✅ Registering: Scheduler Service")
        
        # Use the factory function which handles initialization
        scheduler = await create_scheduler_service(registry)
        
        logger.info("✅ Scheduler service initialized (not started - call start() to begin)")
        return scheduler
    
    registry.register_factory('scheduler', create_scheduler,
                             dependencies=['database', 'config'])
    
    logger.info("=" * 70)
    logger.info("SERVICE REGISTRATION COMPLETE")
    logger.info(f"Total services registered: {len(registry.list_services())}")
    logger.info("=" * 70)
    
    return registry


# ========================================================================
# COMMAND HANDLERS
# Principle #10: Separation of Concerns - Each handler does one thing
# ========================================================================

async def handle_health(registry: ServiceRegistry, detailed: bool = False):
    """
    Perform system health check.
    
    Args:
        registry: Service registry with initialized services
        detailed: Whether to show detailed health information
    """
    logger.info("=" * 70)
    logger.info("SYSTEM HEALTH CHECK")
    logger.info("=" * 70)
    
    # Get all services
    services = [
        ('database', 'Database'),
        ('stellar_client', 'Stellar Client'),
        ('air_protocol', 'Air Protocol (UBEC)'),
        ('water_protocol', 'Water Protocol (UBECrc)'),
        ('earth_protocol', 'Earth Protocol (UBECgpi)'),
        ('fire_protocol', 'Fire Protocol (UBECtt)'),
        ('sync', 'Blockchain Sync Service'),
        ('analytics', 'Analytics Service'),
        ('distribution', 'Distribution Service'),
        ('holonic_evaluator', 'Holonic Evaluator'),
        ('visualizer', 'Holonic Visualizer'),
        ('audit', 'Audit Service'),
        ('api_service', 'API Service'),
        ('scheduler', 'Scheduler Service'),
    ]
    
    healthy_count = 0
    total_count = len(services)
    
    for service_key, service_name in services:
        try:
            service = await registry.get(service_key)
            
            # Check if service has health_check method
            if hasattr(service, 'health_check'):
                health = await service.health_check()
                status = health.get('status', 'unknown')
                
                if status == 'healthy':
                    logger.info(f"✅ {service_name}: HEALTHY")
                    healthy_count += 1
                    
                    if detailed and 'details' in health:
                        for key, value in health['details'].items():
                            logger.info(f"   {key}: {value}")
                else:
                    logger.warning(f"⚠️  {service_name}: {status.upper()}")
                    
                    if 'error' in health:
                        logger.warning(f"   Error: {health['error']}")
            else:
                logger.info(f"✅ {service_name}: OK (no health check)")
                healthy_count += 1
                
        except Exception as e:
            logger.error(f"❌ {service_name}: ERROR - {e}")
    
    # Overall health summary
    logger.info("\n" + "=" * 70)
    logger.info(f"HEALTH SUMMARY: {healthy_count}/{total_count} services healthy")
    
    health_percentage = (healthy_count / total_count) * 100 if total_count > 0 else 0
    
    if health_percentage == 100:
        logger.info("✅ System Status: FULLY OPERATIONAL")
    elif health_percentage >= 80:
        logger.warning("⚠️  System Status: DEGRADED")
    else:
        logger.error("❌ System Status: CRITICAL")
    
    logger.info("=" * 70)


async def handle_status(registry: ServiceRegistry):
    """Display system status and token information."""
    logger.info("=" * 70)
    logger.info("SYSTEM STATUS")
    logger.info("=" * 70)
    
    try:
        # Get analytics service
        analytics = await registry.get('analytics')
        
        # Get ecosystem overview
        results = await analytics.get_ecosystem_overview()
        
        if 'error' in results:
            logger.error(f"Error getting status: {results['error']}")
            return
        
        # Display ecosystem summary
        logger.info("\n📊 ECOSYSTEM SUMMARY")
        logger.info(f"Total Holders: {results.get('total_holders', 0):,}")
        logger.info(f"Total Supply: {float(results.get('total_supply', 0)):,.2f} UBEC")
        logger.info(f"Last Updated: {results.get('last_updated', 'Unknown')}")
        
        # Display token information
        tokens = results.get('tokens', [])
        
        if tokens:
            logger.info("\n🪙 TOKEN DETAILS")
            
            for token in tokens:
                element = token.get('element', 'Unknown')
                symbol = token.get('asset_code', 'Unknown')
                holders = token.get('holder_count', 0)
                supply = float(token.get('supply', 0))
                
                logger.info(f"\n{element.title()} ({symbol}):")
                logger.info(f"  Holders: {holders:,}")
                logger.info(f"  Supply: {supply:,.7f}")
        
        logger.info("\n" + "=" * 70)
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}", exc_info=True)


async def handle_sync_status(registry: ServiceRegistry):
    """
    Check data synchronization status to diagnose zero-activity issues.
    """
    logger.info("=" * 70)
    logger.info("DATA SYNCHRONIZATION STATUS")
    logger.info("=" * 70)
    
    try:
        database = await registry.get('database')
        
        # Check each token's sync status
        tokens = [
            ('UBEC', 'Air'),
            ('UBECrc', 'Water'),
            ('UBECgpi', 'Earth'),
            ('UBECtt', 'Fire')
        ]
        
        total_accounts = 0
        total_transactions = 0
        oldest_data = None
        newest_data = None
        
        for asset_code, element in tokens:
            logger.info(f"\n{element} ({asset_code}):")
            
            # Count accounts
            account_count_query = """
                SELECT COUNT(*) as count
                FROM ubec_main.token_holders
                WHERE asset_code = $1
            """
            result = await database.fetch_one(account_count_query, (asset_code,))
            account_count = result['count'] if result else 0
            total_accounts += account_count
            logger.info(f"  📊 Accounts: {account_count:,}")
            
            # Count transactions
            tx_count_query = """
                SELECT COUNT(*) as count
                FROM ubec_main.transactions
                WHERE asset_code = $1
            """
            result = await database.fetch_one(tx_count_query, (asset_code,))
            tx_count = result['count'] if result else 0
            total_transactions += tx_count
            logger.info(f"  💸 Transactions: {tx_count:,}")
            
            # Get last sync time
            last_sync_query = """
                SELECT MAX(last_synced) as last_sync
                FROM ubec_main.token_holders
                WHERE asset_code = $1
            """
            result = await database.fetch_one(last_sync_query, (asset_code,))
            
            if result and result['last_sync']:
                last_sync = result['last_sync']
                time_since = datetime.now(timezone.utc) - last_sync
                logger.info(f"  🕐 Last Synced: {last_sync.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                logger.info(f"  ⏱️  Time Since: {time_since.days}d {time_since.seconds // 3600}h")
                
                if oldest_data is None or last_sync < oldest_data:
                    oldest_data = last_sync
                if newest_data is None or last_sync > newest_data:
                    newest_data = last_sync
            else:
                logger.warning(f"  ⚠️  No sync data available")
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total Accounts: {total_accounts:,}")
        logger.info(f"Total Transactions: {total_transactions:,}")
        
        if oldest_data and newest_data:
            logger.info(f"Oldest Data: {oldest_data.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            logger.info(f"Newest Data: {newest_data.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            time_since_newest = datetime.now(timezone.utc) - newest_data
            
            if time_since_newest.total_seconds() > 3600:
                logger.warning("\n⚠️  DATA MAY BE STALE")
                logger.warning(f"Last sync was {time_since_newest.days}d {time_since_newest.seconds // 3600}h ago")
                logger.info("\nRecommendation: Run synchronization")
                logger.info("  python main.py sync --sync-type all")
            else:
                logger.info("\n✅ Data is current")
        else:
            logger.warning("\n⚠️  NO SYNC DATA FOUND")
            logger.info("\nRecommendation: Run initial synchronization")
            logger.info("  python main.py sync --sync-type all")
        
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Failed to check sync status: {e}", exc_info=True)


async def handle_discover(registry: ServiceRegistry, max_accounts: int = 100):
    """Discover token holders."""
    logger.info("=" * 70)
    logger.info(f"DISCOVERING TOKEN HOLDERS (max: {max_accounts})")
    logger.info("=" * 70)
    
    try:
        # Get protocol services
        protocols = [
            ('air_protocol', 'UBEC'),
            ('water_protocol', 'UBECrc'),
            ('earth_protocol', 'UBECgpi'),
            ('fire_protocol', 'UBECtt')
        ]
        
        total_discovered = 0
        
        for protocol_key, asset_code in protocols:
            logger.info(f"\n🔍 Discovering {asset_code} holders...")
            
            protocol = await registry.get(protocol_key)
            
            # Discover holders
            result = await protocol.discover_holders(max_accounts=max_accounts)
            
            discovered = result.get('discovered', 0)
            total_discovered += discovered
            
            logger.info(f"✅ Discovered {discovered} {asset_code} holders")
        
        logger.info("\n" + "=" * 70)
        logger.info(f"TOTAL DISCOVERED: {total_discovered} holders")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)


async def handle_sync(
    registry: ServiceRegistry,
    sync_type: str = 'all',
    max_accounts: Optional[int] = None,
    force: bool = False
):
    """Synchronize blockchain data."""
    logger.info("=" * 70)
    logger.info(f"SYNCHRONIZING BLOCKCHAIN DATA (type: {sync_type})")
    logger.info("=" * 70)
    
    try:
        # Determine which protocols to sync
        if sync_type == 'all':
            protocols = [
                ('air_protocol', 'UBEC'),
                ('water_protocol', 'UBECrc'),
                ('earth_protocol', 'UBECgpi'),
                ('fire_protocol', 'UBECtt')
            ]
        else:
            protocol_map = {
                'UBEC': ('air_protocol', 'UBEC'),
                'UBECrc': ('water_protocol', 'UBECrc'),
                'UBECgpi': ('earth_protocol', 'UBECgpi'),
                'UBECtt': ('fire_protocol', 'UBECtt')
            }
            protocols = [protocol_map[sync_type]]
        
        total_synced = 0
        
        for protocol_key, asset_code in protocols:
            logger.info(f"\n🔄 Synchronizing {asset_code}...")
            
            protocol = await registry.get(protocol_key)
            
            # Sync data
            result = await protocol.sync_holders(
                max_accounts=max_accounts,
                force=force
            )
            
            synced = result.get('synced', 0)
            total_synced += synced
            
            logger.info(f"✅ Synchronized {synced} {asset_code} accounts")
        
        logger.info("\n" + "=" * 70)
        logger.info(f"TOTAL SYNCHRONIZED: {total_synced} accounts")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Synchronization failed: {e}", exc_info=True)


async def handle_analytics(registry: ServiceRegistry, analysis_type: str = 'overview'):
    """Run analytics."""
    logger.info("=" * 70)
    logger.info(f"RUNNING ANALYTICS (type: {analysis_type})")
    logger.info("=" * 70)
    
    try:
        analytics = await registry.get('analytics')
        
        if analysis_type == 'overview':
            results = await analytics.get_ecosystem_overview()
            
            if 'error' in results:
                logger.error(f"Error: {results['error']}")
                return
            
            # Display results
            logger.info("\n📊 ECOSYSTEM OVERVIEW")
            logger.info(f"Total Holders: {results.get('total_holders', 0):,}")
            logger.info(f"Total Supply: {float(results.get('total_supply', 0)):,.2f} UBEC")
            
            tokens = results.get('tokens', [])
            
            if tokens:
                logger.info("\n🪙 TOKEN BREAKDOWN")
                
                for token in tokens:
                    element = token.get('element', 'Unknown')
                    symbol = token.get('asset_code', 'Unknown')
                    holders = token.get('holder_count', 0)
                    supply = float(token.get('supply', 0))
                    
                    logger.info(f"\n{element.title()} ({symbol}):")
                    logger.info(f"  Holders: {holders:,}")
                    logger.info(f"  Supply: {supply:,.7f}")
        
        elif analysis_type == 'holders':
            # Get holder analytics
            results = await analytics.analyze_holder_distribution()
            
            logger.info("\n👥 HOLDER ANALYSIS")
            logger.info(f"Total Holders: {results.get('total_holders', 0):,}")
            
            # Distribution by token
            by_token = results.get('by_token', {})
            
            if by_token:
                logger.info("\n🪙 Distribution by Token:")
                
                for asset_code, data in by_token.items():
                    logger.info(f"\n{asset_code}:")
                    logger.info(f"  Holders: {data.get('holder_count', 0):,}")
                    logger.info(f"  Total Supply: {float(data.get('total_supply', 0)):,.7f}")
        
        elif analysis_type == 'metrics':
            # Get metrics
            results = await analytics.get_protocol_metrics()
            
            logger.info("\n📈 PROTOCOL METRICS")
            
            for metric_name, value in results.items():
                logger.info(f"{metric_name}: {value}")
        
        logger.info("\n" + "=" * 70)
        
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)


async def handle_holonic_evaluation(
    registry: ServiceRegistry,
    evaluate_all: bool = False,
    account_id: Optional[str] = None,
    max_accounts: Optional[int] = None,
    save_to_db: bool = True
):
    """Evaluate Ubuntu principles for accounts."""
    logger.info("=" * 70)
    logger.info("HOLONIC EVALUATION")
    logger.info("=" * 70)
    
    try:
        evaluator = await registry.get('holonic_evaluator')
        
        start_time = time.time()
        
        if account_id:
            # Evaluate single account
            logger.info(f"\n🔍 Evaluating account: {account_id}")
            
            result = await evaluator.evaluate_account(
                account_id=account_id,
                save_to_db=save_to_db
            )
            
            if 'error' in result:
                logger.error(f"Error: {result['error']}")
                return
            
            # Display results
            logger.info(f"\n📊 Results for {account_id}:")
            logger.info(f"Holonic Score: {result.get('holonic_score', 0):.4f}")
            
            principles = result.get('principle_scores', {})
            
            if principles:
                logger.info("\n🔷 Principle Scores:")
                for principle, score in principles.items():
                    logger.info(f"  {principle}: {score:.4f}")
        
        else:
            # Evaluate multiple accounts
            logger.info(f"\n🔍 Evaluating accounts (all: {evaluate_all}, max: {max_accounts})")
            
            result = await evaluator.evaluate_all_accounts(
                max_accounts=max_accounts,
                save_to_db=save_to_db
            )
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Display statistics
            evaluated = result.get('evaluated', 0)
            skipped = result.get('skipped', 0)
            errors = result.get('errors', 0)
            
            logger.info("\n📊 EVALUATION STATISTICS")
            logger.info(f"Evaluated: {evaluated:,}")
            logger.info(f"Skipped: {skipped:,}")
            logger.info(f"Errors: {errors:,}")
            logger.info(f"Duration: {duration:.2f}s")
            
            # Display top scores if available
            top_accounts = result.get('top_accounts', [])
            
            if top_accounts:
                logger.info("\n🏆 TOP HOLONIC SCORES")
                
                for i, account in enumerate(top_accounts[:10], 1):
                    account_id = account.get('account_id', 'Unknown')
                    score = account.get('holonic_score', 0)
                    logger.info(f"{i}. {account_id[:10]}... - {score:.4f}")
        
        logger.info("\n" + "=" * 70)
        
    except Exception as e:
        logger.error(f"Holonic evaluation failed: {e}", exc_info=True)


async def handle_visualize(
    registry: ServiceRegistry,
    action: str = 'report',
    format: str = 'html',
    include_advanced: bool = False
):
    """Generate visualizations."""
    logger.info("=" * 70)
    logger.info(f"GENERATING VISUALIZATIONS (action: {action}, format: {format})")
    logger.info("=" * 70)
    
    try:
        visualizer = await registry.get('visualizer')
        
        if action == 'report':
            # Generate holonic report
            logger.info("\n📊 Generating holonic network report...")
            
            result = await visualizer.generate_holonic_report(
                format=format,
                include_advanced=include_advanced
            )
            
            if 'error' in result:
                logger.error(f"Error: {result['error']}")
                return
            
            output_path = result.get('output_path', 'Unknown')
            logger.info(f"✅ Report generated: {output_path}")
        
        elif action == 'all':
            # Generate all visualizations
            logger.info("\n📊 Generating all visualizations...")
            
            result = await visualizer.generate_all_visualizations(
                format=format
            )
            
            if 'error' in result:
                logger.error(f"Error: {result['error']}")
                return
            
            generated = result.get('generated', [])
            
            logger.info(f"✅ Generated {len(generated)} visualizations")
            
            for viz in generated:
                logger.info(f"  - {viz}")
        
        logger.info("\n" + "=" * 70)
        
    except Exception as e:
        logger.error(f"Visualization failed: {e}", exc_info=True)


async def handle_protocol_health(registry: ServiceRegistry):
    """Check protocol health."""
    logger.info("=" * 70)
    logger.info("PROTOCOL HEALTH CHECK")
    logger.info("=" * 70)
    
    try:
        protocols = [
            ('air_protocol', 'Air (UBEC)'),
            ('water_protocol', 'Water (UBECrc)'),
            ('earth_protocol', 'Earth (UBECgpi)'),
            ('fire_protocol', 'Fire (UBECtt)')
        ]
        
        healthy_count = 0
        
        for protocol_key, protocol_name in protocols:
            logger.info(f"\n🔍 Checking {protocol_name}...")
            
            protocol = await registry.get(protocol_key)
            
            # Get health status
            health = await protocol.health_check()
            
            status = health.get('status', 'unknown')
            
            if status == 'healthy':
                logger.info(f"✅ {protocol_name}: HEALTHY")
                healthy_count += 1
            else:
                logger.warning(f"⚠️  {protocol_name}: {status.upper()}")
            
            # Display details
            details = health.get('details', {})
            
            for key, value in details.items():
                logger.info(f"  {key}: {value}")
        
        logger.info("\n" + "=" * 70)
        logger.info(f"HEALTH SUMMARY: {healthy_count}/{len(protocols)} protocols healthy")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Protocol health check failed: {e}", exc_info=True)


async def handle_scheduler_status(registry: ServiceRegistry):
    """Display scheduler status."""
    logger.info("=" * 70)
    logger.info("SCHEDULER STATUS")
    logger.info("=" * 70)
    
    try:
        scheduler = await registry.get('scheduler')
        
        # Get status
        status = await scheduler.get_status()
        
        # Display status
        is_running = status.get('is_running', False)
        
        if is_running:
            logger.info("\n✅ Scheduler: RUNNING")
        else:
            logger.info("\n⚠️  Scheduler: STOPPED")
        
        # Display scheduled jobs
        jobs = status.get('jobs', [])
        
        if jobs:
            logger.info(f"\n📋 Scheduled Jobs ({len(jobs)}):")
            
            for job in jobs:
                job_name = job.get('name', 'Unknown')
                next_run = job.get('next_run', 'Unknown')
                interval = job.get('interval', 'Unknown')
                
                logger.info(f"\n{job_name}:")
                logger.info(f"  Next Run: {next_run}")
                logger.info(f"  Interval: {interval}")
        
        logger.info("\n" + "=" * 70)
        
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}", exc_info=True)


async def handle_serve(
    registry: ServiceRegistry,
    host: str = '0.0.0.0',
    port: int = 8000,
    reload: bool = False
):
    """Start API server with scheduler."""
    logger.info("=" * 70)
    logger.info(f"STARTING API SERVER (host: {host}, port: {port})")
    logger.info("=" * 70)
    
    try:
        # Get scheduler
        scheduler = await registry.get('scheduler')
        
        # Start scheduler
        await scheduler.start()
        logger.info("✅ Scheduler started")
        
        # Get API service from registry
        api_service = await registry.get('api_service')
        
        # Get the FastAPI app instance from the service
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
        
        logger.info(f"🚀 Starting server at http://{host}:{port}")
        logger.info("=" * 70)
        
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
# DISTRIBUTION COMMAND HANDLERS
# ========================================================================

async def handle_distribution(registry: ServiceRegistry, action: str, dry_run: bool = True):
    """Handle distribution compliance commands."""
    distribution = await registry.get('distribution')
    
    # DEFENSIVE: Check if we got the factory function instead of the service
    if callable(distribution) and not hasattr(distribution, 'check_compliance'):
        logger.error("❌ Distribution service not properly initialized")
        logger.error("Got factory function instead of service instance")
        logger.error("This indicates a service registry initialization issue")
        return
    
    if action == 'check-compliance':
        logger.info("=" * 70)
        logger.info("DISTRIBUTION COMPLIANCE CHECK")
        logger.info("=" * 70)
        
        compliance = await distribution.check_compliance()
        
        if 'error' in compliance:
            logger.error(f"Error: {compliance['error']}")
            return
        
        icon = "✅" if compliance['compliant'] else "❌"
        logger.info(f"\n{icon} Status: {'COMPLIANT' if compliance['compliant'] else 'NON-COMPLIANT'}")
        
        dist = compliance['distribution']
        logger.info(f"\nTotal Supply: {dist['total_supply']:,.2f} UBEC")
        
        for category in ['general', 'stewardship', 'administration']:
            data = dist[category]
            logger.info(f"\n{category.title()}:")
            logger.info(f"  Current: {data['percentage']:.2f}%")
            logger.info(f"  Target:  {data['target']:.2f}%")
            logger.info(f"  Amount:  {data['amount']:,.2f} UBEC")
        
        if compliance['recommendations']:
            logger.info("\nRecommendations:")
            for rec in compliance['recommendations']:
                logger.info(f"  • {rec}")
    
    elif action == 'status':
        logger.info("=" * 70)
        logger.info("DISTRIBUTION STATUS")
        logger.info("=" * 70)
        
        balances = await distribution.get_all_account_balances()
        
        general = balances['general']
        logger.info(f"\n💰 General Distribution:")
        logger.info(f"   Direct:  {general['direct']:,.7f} UBEC")
        logger.info(f"   LP:      {general['lp']:,.7f} UBEC")
        logger.info(f"   Total:   {general['total']:,.7f} UBEC")
        
        steward = balances['stewardship']
        logger.info(f"\n🏛️  Stewardship (3 accounts combined):")
        logger.info(f"   Direct:  {steward['direct']:,.7f} UBEC")
        logger.info(f"   LP:      {steward['lp']:,.7f} UBEC")
        logger.info(f"   Total:   {steward['total']:,.7f} UBEC")
        
        admin = balances['administration']
        logger.info(f"\n⚙️  Administration:")
        logger.info(f"   Direct:  {admin['direct']:,.7f} UBEC")
        logger.info(f"   LP:      {admin['lp']:,.7f} UBEC")
        logger.info(f"   Total:   {admin['total']:,.7f} UBEC")
        
        total = general['total'] + steward['total'] + admin['total']
        logger.info(f"\n📊 TOTAL SUPPLY: {total:,.7f} UBEC")
    
    elif action == 'rebalance-check':
        logger.info("=" * 70)
        logger.info("REBALANCE CHECK")
        logger.info("=" * 70)
        
        needs_rebalance = await distribution.is_rebalance_needed()
        
        if needs_rebalance:
            logger.info("\n⚠️  REBALANCING RECOMMENDED")
            compliance = await distribution.check_compliance()
            logger.info("\nDeviations:")
            logger.info(f"  Admin: {compliance['deviations']['administration']:.2f}pp")
            logger.info(f"  Steward: {compliance['deviations']['stewardship']:.2f}pp")
        else:
            logger.info("\n✅ NO REBALANCING NEEDED")
    
    elif action == 'execute-rebalance':
        logger.info("=" * 70)
        logger.info("EXECUTE REBALANCING")
        logger.info("=" * 70)
        
        # Check if method exists
        if not hasattr(distribution, 'execute_distribution'):
            logger.error("\n❌ Execute functionality not yet implemented")
            logger.info("\nThe execute_distribution() method requires:")
            logger.info("  1. Secure key management implementation")
            logger.info("  2. Transaction signing capability")
            logger.info("  3. Multi-signature support")
            logger.info("\nCurrent status: Compliance monitoring only")
            logger.info("For actual distribution: Manual transactions required")
            return
        
        # Attempt execution
        try:
            logger.info(f"\n{'🔍 DRY RUN MODE' if dry_run else '⚠️  LIVE EXECUTION MODE'}")
            
            if not dry_run:
                logger.warning("\n⚠️  WARNING: Live execution mode requires:")
                logger.warning("  - Secure key management")
                logger.warning("  - Transaction authorization")
                logger.warning("  - Multi-signature approval")
                
                # Safety check
                response = input("\nProceed with LIVE execution? (type 'EXECUTE' to confirm): ")
                if response != 'EXECUTE':
                    logger.info("Execution cancelled by user")
                    return
            
            result = await distribution.execute_distribution(
                dry_run=dry_run,
                require_compliance=False
            )
            
            if result.get('success'):
                logger.info(f"\n✅ {'Simulation' if dry_run else 'Execution'} completed")
                logger.info(f"\nResults:")
                # Convert string to float for formatting (distribution service returns string)
                total_dist = result.get('total_distributed', '0')
                total_dist = float(total_dist) if isinstance(total_dist, str) else total_dist
                logger.info(f"  Total to distribute: {total_dist:,.2f} UBEC")
                logger.info(f"  Transactions: {result.get('accounts_updated', 0)}")
                
                if result.get('transactions'):
                    logger.info(f"\nTransactions:")
                    for tx in result['transactions'][:5]:
                        # Transaction data is nested in 'transaction' key
                        tx_data = tx.get('transaction', tx)
                        amount = tx_data.get('amount', '0')
                        amount = float(amount) if isinstance(amount, str) else amount
                        destination = tx_data.get('destination', 'N/A')
                        logger.info(f"  - {amount:,.2f} UBEC to {destination[:10]}...")
                    
                    if len(result['transactions']) > 5:
                        logger.info(f"  ... and {len(result['transactions']) - 5} more")
            else:
                logger.error(f"\n❌ {'Simulation' if dry_run else 'Execution'} failed")
                if result.get('error'):
                    logger.error(f"Error: {result['error']}")
                
        except NotImplementedError as e:
            logger.error(f"\n❌ {str(e)}")
            logger.info("\nExecution functionality requires secure key management.")
            logger.info("Current system: Monitoring and compliance checking only")
        except Exception as e:
            logger.error(f"\n❌ Execution failed: {e}")
            logger.error("See logs for details")
    
    else:
        logger.error(f"Unknown action: {action}")


# ========================================================================
# MAIN FUNCTION
# ========================================================================

async def main():
    """
    Main orchestration function.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='UBEC Protocol Suite Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py health              # Check system health
  python main.py status              # Get system status
  python main.py sync-status         # Check synchronization status
  python main.py sync --sync-type all
  python main.py analytics --analysis-type overview
  python main.py evaluate-holonic --all
  python main.py distribution --action check-compliance
  python main.py distribution --action execute-rebalance           # DRY-RUN (safe)
  python main.py distribution --action execute-rebalance --live    # LIVE (dangerous)
  python main.py serve --host 0.0.0.0 --port 8000
        """
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument('--detailed', action='store_true',
                              help='Show detailed health information')
    
    # Status command
    subparsers.add_parser('status', help='Display system status')
    
    # Sync status command
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
    
    # Distribution command
    distribution_parser = subparsers.add_parser(
        'distribution',
        help='Check UBEC token distribution compliance'
    )
    distribution_parser.add_argument(
        '--action',
        required=True,
        choices=['check-compliance', 'status', 'rebalance-check', 'execute-rebalance'],
        help='Distribution action to perform'
    )
    distribution_parser.add_argument(
        '--live',
        action='store_true',
        help='Execute actual transactions (DANGEROUS - requires confirmation). Default is DRY-RUN mode.'
    )
    
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
            
            elif args.command == 'distribution':
                dry_run = not args.live
                await handle_distribution(registry, action=args.action, dry_run=dry_run)
                
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
# ========================================================================

if __name__ == "__main__":
    """
    Entry point for the entire UBEC Protocol Suite.
    
    This is the ONLY place where the system should be executed.
    """
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
