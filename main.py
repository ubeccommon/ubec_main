#!/usr/bin/env python3
"""
UBEC Main Protocol - Unified Entry Point

The SOLE entry point for the entire UBEC protocol system.
All services are orchestrated through this main file.

Integrated Services:
    - Air Protocol (Gateway / Universal Access - UBEC)
    - Water Protocol (Reciprocity / Flow - UBECrc)
    - Earth Protocol (Ground / Stability - UBECgpi)
    - Fire Protocol (Transformation - UBECtt)
    - Distribution Manager (Token Balance Management)
    - Data Synchronizer (Blockchain Sync + Liquidity Pools)
    - Holonic Evaluator (Ubuntu Principles)
    - Visualization Service (Charts & Reports) ⭐ NEW in v4.7

Design Compliance:
    ✅ Principle 1: Modular Design - Clear separation of concerns
    ✅ Principle 2: Service Pattern - THIS IS THE ONLY standalone execution
    ✅ Principle 3: Service Registry - All dependencies via registry
    ✅ Principle 4: Single Source of Truth - Database authoritative
    ✅ Principle 5: Strict Async - All operations async
    ✅ Principle 6: No Sync Fallbacks - Pure async only (FIXED: ServerAsync)
    ✅ Principle 7: Per-Asset Monitoring - Individual tracking
    ✅ Principle 8: No Duplicate Configuration - Centralized config
    ✅ Principle 9: Integrated Rate Limiting - Built-in rate limiter
    ✅ Principle 10: Clear Separation - Business logic isolated
    ✅ Principle 11: Documentation - Comprehensive docstrings
    ✅ Principle 12: Method Singularity - No redundant methods

CLI Usage:
    # System Operations
    python main.py --mode health                    # Full system health
    python main.py --mode status                    # System status
    
    # Data Layer Operations - ENHANCED WITH GRANULAR SYNC
    python main.py --mode sync                      # Sync all data (default)
    python main.py --mode sync --sync-type accounts # Sync accounts only
    python main.py --mode sync --sync-type transactions  # Sync transactions only
    python main.py --mode sync --sync-type operations    # Sync operations only
    python main.py --mode sync --sync-type effects       # Sync effects only
    python main.py --mode sync --sync-type balances      # Sync balances only
    python main.py --mode sync --sync-type lp_only       # Sync liquidity pools only
    python main.py --mode sync --sync-type lp_only --asset-code UBEC  # Sync UBEC LPs
    python main.py --mode discover --max-accounts 100    # Discover accounts
    python main.py --mode analytics --analysis-type summary  # Analytics
    
    # Protocol Operations
    python main.py --mode protocol-health           # Protocol health
    python main.py --mode protocol-status           # Protocol status
    python main.py --mode protocol-sync             # Sync protocols
    python main.py --mode evaluate                  # Holonic evaluation
    python main.py --mode evaluate --account GXXX   # Account evaluation
    
    # Distribution Management (with dry-run support)
    python main.py --mode distribution --action check-compliance
    python main.py --mode distribution --action rebalance --dry-run  # PREVIEW ONLY
    python main.py --mode distribution --action rebalance             # EXECUTE
    python main.py --mode distribution --action status
    python main.py --mode distribution --action evaluate
    python main.py --mode distribution --action trends --days 30
    python main.py --mode distribution --action schedule --interval 3600
    
    # Visualization Operations ⭐ NEW in v4.7
    python main.py --mode visualize --action chart --chart-type radar --top-n 10
    python main.py --mode visualize --action chart --chart-type bar --metric supply
    python main.py --mode visualize --action chart --chart-type line --days 30
    python main.py --mode visualize --action chart --chart-type pie --category distribution
    python main.py --mode visualize --action chart --chart-type network --min-connections 5
    python main.py --mode visualize --action report --format html --output report.html
    python main.py --mode visualize --action report --format json --output report.json
    python main.py --mode visualize --action all --output-dir visualizations/

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 4.7.0 (Added integrated visualization service)
Date: October 14, 2025

Changes in v4.7.0:
    - ⭐ NEW: Integrated visualization service with factory pattern (Principle #2)
    - ⭐ NEW: Added --mode visualize with comprehensive chart types
    - ⭐ NEW: Support for radar, bar, line, pie, and network charts
    - ⭐ NEW: HTML and JSON report generation
    - ⭐ NEW: Multi-schema database support via DB_SEARCH_PATH
    - ✅ IMPROVED: Database manager now supports schema search paths
    - ✅ MAINTAINED: All previous fixes from v4.6, v4.5, and v4.4
    - ✅ MAINTAINED: All 12 design principles strictly enforced

Changes in v4.6.0:
    - ✅ FIXED: Holonic evaluator now uses proper factory function (Principle #2)
    - ✅ FIXED: Changed db_conn to db_manager for consistency (Principle #8)
    - ✅ FIXED: Added required config parameter to holonic evaluator
    - ✅ IMPROVED: All service initializations now follow identical factory pattern
    - ✅ MAINTAINED: All previous fixes from v4.5 and v4.4
    - ✅ MAINTAINED: All 12 design principles strictly enforced

Changes in v4.5:
    - FIXED: Made snapshot_distribution() calls optional (defensive programming)
    - IMPROVED: System gracefully handles missing optional features
    - MAINTAINED: All previous fixes from v4.4

Changes in v4.4:
    - FIXED: Synchronizer now properly initialized with stellar_client
    - FIXED: discover_accounts return type handling (returns int, not list)
    - IMPROVED: Better error handling for synchronizer initialization
"""

import os
import sys
import asyncio
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Ensure project root is in path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Core imports
from core.db.database_manager import AsyncDatabaseManager
from config.settings import get_system_config, SystemConfig

# Configure logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ubec_main.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== UTILITY FUNCTIONS ====================

def get_database_schema_config() -> tuple[str, str]:
    """
    Get database schema configuration from environment.
    
    Supports both DB_SEARCH_PATH (new, preferred) and DB_SCHEMA (legacy).
    
    Returns:
        tuple: (primary_schema, full_search_path)
            - primary_schema: First schema in path (for operational use)
            - full_search_path: Complete search path for PostgreSQL
            
    Examples:
        DB_SEARCH_PATH="ubec_main, phenomenal, topology, public"
        → Returns: ("ubec_main", "ubec_main, phenomenal, topology, public")
        
        DB_SCHEMA="ubec_main"
        → Returns: ("ubec_main", "ubec_main")
        
    Design Note (v4.7):
        - DB_SEARCH_PATH takes precedence over DB_SCHEMA
        - Maintains backward compatibility with single-schema setup
        - Follows PostgreSQL search_path conventions
        - Enables multi-schema phenomenological extensions
    """
    # Try new DB_SEARCH_PATH first (comma-separated list)
    search_path = os.getenv('DB_SEARCH_PATH')
    
    if search_path:
        # Clean up whitespace and split by comma
        schemas = [s.strip() for s in search_path.split(',')]
        primary_schema = schemas[0]  # First schema is primary
        full_search_path = ', '.join(schemas)  # Rejoin with consistent spacing
        
        logger.info(f"Using DB_SEARCH_PATH: {full_search_path}")
        logger.info(f"Primary schema: {primary_schema}")
        
        return primary_schema, full_search_path
    
    # Fall back to legacy DB_SCHEMA (single schema)
    schema = os.getenv('DB_SCHEMA', 'ubec_main')
    
    logger.info(f"Using DB_SCHEMA (legacy): {schema}")
    
    return schema, schema



# ==================== SERVICE INITIALIZATION ====================

async def initialize_database() -> AsyncDatabaseManager:
    """
    Initialize database manager first (required for config loading).
    
    Returns:
        AsyncDatabaseManager instance
        
    Raises:
        RuntimeError: If database initialization fails
        
    Design Note (v4.7):
        Now supports multi-schema search paths via DB_SEARCH_PATH.
        The AsyncDatabaseManager will use the full search path when
        executing `SET search_path TO ...` commands, enabling queries
        to search across multiple schemas in priority order.
        
        This enables phenomenological extensions (quantum gravity, topology)
        to coexist with core UBEC data in separate schemas.
    """
    logger.info("Initializing database connection...")
    
    try:
        # Get schema configuration
        primary_schema, search_path = get_database_schema_config()
        
        # Create database manager with search path support
        # Note: AsyncDatabaseManager.schema will be set to the full search_path
        db_manager = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=search_path,  # Use full search path here
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        await db_manager.initialize()
        logger.info("✓ Database connection initialized")
        logger.info(f"  Primary schema: {primary_schema}")
        logger.info(f"  Search path: {search_path}")
        
        # Store primary schema as an attribute for services that need it
        db_manager.primary_schema = primary_schema
        
        return db_manager
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise RuntimeError(f"Database initialization failed: {e}")

async def initialize_services(config: SystemConfig, db_manager: AsyncDatabaseManager) -> Dict[str, Any]:
    """
    Initialize all system services via the service registry.
    
    Args:
        config: System configuration (loaded from database)
        db_manager: Database manager instance
        
    Returns:
        dict: Dictionary of initialized services
    
    Design Note:
        This function initializes services in dependency order:
        1. Database Manager (already initialized)
        2. Stellar Client (blockchain access) - ASYNC ServerAsync
        3. Data Synchronizer (depends on database + stellar)
        4. Element Protocols (depend on database + stellar)
        5. Distribution Services (depend on all above)
        6. Holonic Evaluator (depends on all above)
        7. Visualization Service (depends on holonic evaluator) ⭐ NEW in v4.7
        
    Fixes in v4.7.0:
        - Added visualization service with factory pattern (Principle #2)
        - Visualization service receives holonic evaluator as dependency
        
    Fixes in v4.6.0:
        - Holonic evaluator now uses create_holonic_evaluator factory (Principle #2)
        - Changed db_conn to db_manager for consistency (Principle #8)
        - Added required config parameter with proper schema handling
        
    Fixes in v4.4:
        - Synchronizer now properly initialized with stellar_client via initialize() method
        - Better error handling if stellar_client unavailable
    """
    logger.info("="*70)
    logger.info("Initializing UBEC Protocol Services")
    logger.info("="*70)
    
    services = {
        'database': db_manager,
        'config': config
    }
    
    try:
        # CRITICAL FIX: Use ServerAsync for async operations (Principle #6)
        try:
            from stellar_sdk import ServerAsync
            
            stellar_client = ServerAsync(horizon_url=config.HORIZON_URL)
            services['stellar_client'] = stellar_client
            
            # Validation logging
            logger.info(f"✓ Stellar client initialized (type: {type(stellar_client).__name__})")
            
        except Exception as e:
            logger.warning(f"Stellar client initialization failed: {e}")
            services['stellar_client'] = None
        
        # Initialize Data Synchronizer
        # FIXED v4.4: Now properly initializes with stellar_client
        try:
            from core.db.ubec_data_synchronizer import UBECDataSynchronizer
            synchronizer = UBECDataSynchronizer(db_manager)
            
            # CRITICAL FIX: Initialize synchronizer with stellar client
            stellar_client = services.get('stellar_client')
            if stellar_client:
                await synchronizer.initialize(stellar_client)
                logger.info("✓ Data synchronizer initialized with Stellar client")
            else:
                logger.warning("⚠ Stellar client not available - synchronizer has limited functionality")
                logger.warning("  Blockchain queries will not work until stellar_client is available")
            
            services['synchronizer'] = synchronizer
            
        except Exception as e:
            logger.warning(f"Data synchronizer initialization failed: {e}")
            services['synchronizer'] = None
        
        # Initialize Element Protocols
        protocol_configs = {
            'air': {
                'asset_code': config.UBEC_CODE,
                'issuer': config.UBEC_ISSUER,
                'element': 'air',
                'principle': 'diversity'
            },
            'water': {
                'asset_code': config.get('ubecrc_code', 'UBECrc'),
                'issuer': config.get('ubecrc_issuer', ''),
                'element': 'water',
                'principle': 'reciprocity'
            },
            'earth': {
                'asset_code': config.get('ubecgpi_code', 'UBECgpi'),
                'issuer': config.get('ubecgpi_issuer', ''),
                'element': 'earth',
                'principle': 'mutualism'
            },
            'fire': {
                'asset_code': config.get('ubectt_code', 'UBECtt'),
                'issuer': config.get('ubectt_issuer', ''),
                'element': 'fire',
                'principle': 'regeneration'
            }
        }
        
        for protocol_name, protocol_config in protocol_configs.items():
            try:
                # Try to import protocol factory function
                if protocol_name == 'air':
                    from core.protocols.UBEC_protocol import create_ubec_service
                    protocol = create_ubec_service(
                        db_manager=db_manager,
                        config=protocol_config,
                        stellar_client=services.get('stellar_client')
                    )
                elif protocol_name == 'water':
                    from core.protocols.UBECrc_protocol import create_ubecrc_service
                    protocol = create_ubecrc_service(
                        db_manager=db_manager,
                        config=protocol_config,
                        stellar_client=services.get('stellar_client')
                    )
                elif protocol_name == 'earth':
                    from core.protocols.UBECgpi_protocol import create_ubecgpi_service
                    protocol = create_ubecgpi_service(
                        db_manager=db_manager,
                        config=protocol_config,
                        stellar_client=services.get('stellar_client')
                    )
                elif protocol_name == 'fire':
                    from core.protocols.UBECtt_protocol import create_ubectt_service
                    protocol = create_ubectt_service(
                        db_manager=db_manager,
                        config=protocol_config,
                        stellar_client=services.get('stellar_client')
                    )
                
                services[protocol_name] = protocol
                logger.info(f"✓ {protocol_name.title()} Protocol initialized")
                
            except ImportError as e:
                logger.warning(f"{protocol_name.title()} Protocol module not found: {e}")
                services[protocol_name] = None
            except Exception as e:
                logger.warning(f"{protocol_name.title()} Protocol initialization failed: {e}")
                services[protocol_name] = None
        
        # Initialize Audit Service (optional - required by distribution services)
        try:
            from core.audit.ubec_token_audit import UBECTokenAudit
            audit_service = UBECTokenAudit(
                data_source="hybrid",
                db_manager=db_manager
            )
            services['audit'] = audit_service
            logger.info("✓ Audit service initialized")
        except ImportError:
            logger.warning("Audit service module not found - distribution features may be limited")
            services['audit'] = None
        except Exception as e:
            logger.warning(f"Audit service initialization failed: {e} - distribution features may be limited")
            services['audit'] = None
        
        # Initialize Distribution Service
        try:
            from services.distribution.distribution_service import create_distribution_service
            
            # Validate service instances before passing to distribution service
            logger.info("="*70)
            logger.info("SERVICE INSTANCE VALIDATION")
            logger.info("="*70)
            
            # Validate db_manager
            logger.info(f"db_manager type: {type(db_manager).__name__}")
            logger.info(f"db_manager has fetch_one: {hasattr(db_manager, 'fetch_one')}")
            logger.info(f"db_manager primary_schema: {getattr(db_manager, 'primary_schema', 'N/A')}")
            logger.info(f"db_manager search_path: {db_manager.schema}")
            
            # Validate stellar_client
            stellar_client = services.get('stellar_client')
            if stellar_client:
                logger.info(f"stellar_client type: {type(stellar_client).__name__}")
                logger.info(f"stellar_client has accounts: {hasattr(stellar_client, 'accounts')}")
                
                # CRITICAL: Verify it's ServerAsync, not Server
                if type(stellar_client).__name__ == 'Server':
                    logger.error("✗ CRITICAL: stellar_client is sync Server, not async ServerAsync!")
                    raise TypeError("stellar_client must be ServerAsync for async operations")
                else:
                    logger.info(f"✓ stellar_client is async: {type(stellar_client).__name__}")
            else:
                logger.warning("stellar_client is None - distribution service may have limited functionality")
            
            logger.info("="*70)
            
            # Build distribution config from system config
            # Use primary_schema for distribution config (operational schema)
            primary_schema = getattr(db_manager, 'primary_schema', db_manager.schema.split(',')[0].strip())
            
            dist_config = {
                'db_schema': primary_schema,  # Use primary schema for operations
                'ubec_issuer': config.UBEC_ISSUER,
                'ubec_code': config.UBEC_CODE,
                'accounts': config.ACCOUNTS,
                'target_distribution': config.TARGET_DISTRIBUTION,
                'rebalance_threshold': config.REBALANCE_THRESHOLD,
                'secret_keys': {
                    'general': os.getenv('GENERAL_SECRET_KEY'),
                    'administration': os.getenv('ADMIN_SECRET_KEY'),
                    'stewardship': [
                        os.getenv('STEWARD_MGMT_SECRET_KEY'),
                        os.getenv('STEWARD_INFRA_SECRET_KEY'),
                        os.getenv('STEWARD_LIQUIDITY_SECRET_KEY')
                    ]
                },
                'check_interval': config.get('check_interval', 3600)
            }
            
            # Create distribution service with validated instances
            dist_service = await create_distribution_service(
                db_manager=db_manager,
                config=dist_config,
                stellar_client=services.get('stellar_client'),
                audit_service=services.get('audit'),
                rate_limit_calls_per_second=5.0
            )
            services['distribution'] = dist_service
            logger.info("✓ Distribution service initialized")
            
        except ImportError as e:
            logger.warning(f"Distribution service module not found: {e}")
            services['distribution'] = None
        except TypeError as e:
            logger.error(f"Distribution service initialization failed - type error: {e}")
            services['distribution'] = None
            raise
        except Exception as e:
            logger.warning(f"Distribution service initialization failed: {e}")
            services['distribution'] = None
        
        # Initialize Distribution Evaluator
        try:
            from core.evaluation.distribution_evaluator import create_evaluator_service
            
            evaluator = create_evaluator_service(
                distribution_service=services.get('distribution'),
                audit_service=services.get('audit'),
                db_manager=db_manager
            )
            services['distribution_evaluator'] = evaluator
            logger.info("✓ Distribution evaluator initialized")
        except ImportError as e:
            logger.warning(f"Distribution evaluator module not found: {e}")
            services['distribution_evaluator'] = None
        except Exception as e:
            logger.warning(f"Distribution evaluator initialization failed: {e}")
            services['distribution_evaluator'] = None
        
        # Initialize Holonic Evaluator
        # FIXED v4.6.0: Now uses factory function with proper parameters
        try:
            from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
            
            # Build holonic config (Principle #8: No Duplicate Config)
            primary_schema = getattr(db_manager, 'primary_schema', db_manager.schema.split(',')[0].strip())
            
            holonic_config = {
                'db_schema': primary_schema,  # Use primary schema for operations
                'ubec_code': config.UBEC_CODE,
                'ubec_issuer': config.UBEC_ISSUER
            }
            
            # Use factory function (Principle #2: Service Pattern)
            holonic_eval = await create_holonic_evaluator(
                db_manager=db_manager,  # Correct parameter name (Principle #8)
                config=holonic_config    # Required config parameter
            )
            services['holonic_evaluator'] = holonic_eval
            logger.info("✓ Holonic evaluator initialized")
            
        except ImportError:
            logger.warning("Holonic evaluator module not found")
            services['holonic_evaluator'] = None
        except Exception as e:
            logger.warning(f"Holonic evaluator initialization failed: {e}")
            services['holonic_evaluator'] = None
        
        # Initialize Analytics Service
        try:
            from services.analytics.ubec_analytics_service import UBECAnalyticsService
            analytics_service = UBECAnalyticsService(db_manager)
            await analytics_service.initialize()
            services['analytics'] = analytics_service
            logger.info("✓ Analytics service initialized")
        except ImportError:
            logger.warning("Analytics service module not found")
            services['analytics'] = None
        except Exception as e:
            logger.warning(f"Analytics service initialization failed: {e}")
            services['analytics'] = None
        
        # ⭐ NEW in v4.7: Initialize Visualization Service
        try:
            from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer
            
            # Build visualizer config (Principle #8: No Duplicate Config)
            primary_schema = getattr(db_manager, 'primary_schema', db_manager.schema.split(',')[0].strip())
            
            visualizer_config = {
                'db_schema': primary_schema  # Use primary schema for operations
            }
            
            # Use factory function (Principle #2: Service Pattern)
            visualizer = await create_holonic_visualizer(
                db_manager=db_manager,
                config=visualizer_config
            )
            
            services['visualizer'] = visualizer
            logger.info("✓ Visualization service initialized")
                
        except ImportError as e:
            logger.warning(f"Visualization service module not found: {e}")
            services['visualizer'] = None
        except Exception as e:
            logger.warning(f"Visualization service initialization failed: {e}")
            services['visualizer'] = None
        
        logger.info("✓ All available services initialized")
        logger.info("="*70)
        
        return services
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise RuntimeError(f"Service initialization failed: {e}")


async def shutdown_services(services: Dict[str, Any]):
    """
    Gracefully shutdown all services.
    
    Args:
        services: Dictionary of service instances
        
    Design Note:
        Handles both sync and async close methods properly.
        ServerAsync's close() is async (changed from sync Server).
    """
    logger.info("Shutting down services...")
    
    try:
        # Close database connection (async)
        db_manager = services.get('database')
        if db_manager:
            await db_manager.close()
            logger.info("✓ Database connection closed")
        
        # Close Stellar client (ASYNC for ServerAsync)
        stellar_client = services.get('stellar_client')
        if stellar_client and hasattr(stellar_client, 'close'):
            close_method = getattr(stellar_client, 'close')
            if asyncio.iscoroutinefunction(close_method):
                await stellar_client.close()
            else:
                stellar_client.close()
            logger.info("✓ Stellar client closed")
        
        # Close synchronizer
        synchronizer = services.get('synchronizer')
        if synchronizer and hasattr(synchronizer, 'close'):
            close_method = getattr(synchronizer, 'close')
            if asyncio.iscoroutinefunction(close_method):
                await synchronizer.close()
            else:
                synchronizer.close()
            logger.info("✓ Synchronizer closed")
        
        # Close protocol services
        for protocol_name in ['air', 'water', 'earth', 'fire']:
            protocol = services.get(protocol_name)
            if protocol and hasattr(protocol, 'close'):
                close_method = getattr(protocol, 'close')
                if asyncio.iscoroutinefunction(close_method):
                    await protocol.close()
                else:
                    protocol.close()
                logger.info(f"✓ {protocol_name.title()} Protocol closed")
        
        # Close analytics service
        analytics = services.get('analytics')
        if analytics and hasattr(analytics, 'close'):
            await analytics.close()
            logger.info("✓ Analytics service closed")
        
        # Close audit service
        audit = services.get('audit')
        if audit and hasattr(audit, 'close'):
            close_method = getattr(audit, 'close')
            if asyncio.iscoroutinefunction(close_method):
                await audit.close()
            else:
                audit.close()
            logger.info("✓ Audit service closed")
        
        # Close distribution service
        distribution = services.get('distribution')
        if distribution and hasattr(distribution, 'cleanup'):
            await distribution.cleanup()
            logger.info("✓ Distribution service closed")
        
        # Close distribution evaluator
        dist_evaluator = services.get('distribution_evaluator')
        if dist_evaluator and hasattr(dist_evaluator, 'cleanup'):
            await dist_evaluator.cleanup()
            logger.info("✓ Distribution evaluator closed")
        
        # Close holonic evaluator
        holonic_evaluator = services.get('holonic_evaluator')
        if holonic_evaluator and hasattr(holonic_evaluator, 'close'):
            close_method = getattr(holonic_evaluator, 'close')
            if asyncio.iscoroutinefunction(close_method):
                await holonic_evaluator.close()
            else:
                holonic_evaluator.close()
            logger.info("✓ Holonic evaluator closed")
        
        # ⭐ NEW in v4.7: Close visualization service
        visualizer = services.get('visualizer')
        if visualizer and hasattr(visualizer, 'close'):
            close_method = getattr(visualizer, 'close')
            if asyncio.iscoroutinefunction(close_method):
                await visualizer.close()
            else:
                visualizer.close()
            logger.info("✓ Visualization service closed")
        
        logger.info("✓ All services shut down gracefully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ==================== OPERATION HANDLERS ====================

async def run_health_check(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform comprehensive system health check.
    
    Returns:
        dict: Health check results
    """
    logger.info("Performing system health check...")
    
    health_report = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'protocols': {},
        'overall_status': 'UNKNOWN'
    }
    
    # Check core services
    healthy_count = 0
    total_count = 0
    
    for service_name in ['database', 'stellar_client', 'synchronizer']:
        total_count += 1
        service = services.get(service_name)
        
        if service:
            health_report['services'][service_name] = {
                'status': 'AVAILABLE',
                'type': type(service).__name__
            }
            healthy_count += 1
        else:
            health_report['services'][service_name] = {
                'status': 'NOT_AVAILABLE'
            }
    
    # Check protocol services
    for protocol_name in ['air', 'water', 'earth', 'fire']:
        total_count += 1
        service = services.get(protocol_name)
        
        if service:
            health_report['protocols'][protocol_name] = {
                'status': 'AVAILABLE',
                'type': type(service).__name__
            }
            healthy_count += 1
        else:
            health_report['protocols'][protocol_name] = {
                'status': 'NOT_AVAILABLE'
            }
    
    # Check distribution services
    for service_name in ['audit', 'distribution', 'distribution_evaluator', 'holonic_evaluator', 'analytics', 'visualizer']:
        total_count += 1
        service = services.get(service_name)
        
        if service:
            health_report['services'][service_name] = {
                'status': 'AVAILABLE',
                'type': type(service).__name__
            }
            healthy_count += 1
        else:
            health_report['services'][service_name] = {
                'status': 'NOT_AVAILABLE'
            }
    
    # Calculate overall status
    health_percentage = (healthy_count / total_count) * 100
    
    if health_percentage >= 90:
        health_report['overall_status'] = 'EXCELLENT'
    elif health_percentage >= 70:
        health_report['overall_status'] = 'GOOD'
    elif health_percentage >= 50:
        health_report['overall_status'] = 'FAIR'
    else:
        health_report['overall_status'] = 'POOR'
    
    health_report['health_percentage'] = health_percentage
    health_report['services_healthy'] = healthy_count
    health_report['services_total'] = total_count
    
    logger.info(f"Health check complete: {health_report['overall_status']} ({health_percentage:.1f}%)")
    
    return health_report


async def run_sync(
    services: Dict[str, Any],
    sync_type: str = 'all',
    asset_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synchronize blockchain data to database with granular control.
    
    Args:
        services: Service instances
        sync_type: Type of sync operation:
            - 'all': Sync all data types (default)
            - 'accounts': Sync account data only
            - 'transactions': Sync transactions only
            - 'operations': Sync operations only
            - 'effects': Sync effects only
            - 'balances': Sync balances only
            - 'lp_only': Sync liquidity pool data only
        asset_code: Optional specific asset to sync (e.g., 'UBEC', 'UBECrc')
        
    Returns:
        dict: Sync results containing:
            - timestamp: When sync was performed
            - sync_type: Type of sync executed
            - asset_code: Asset(s) synced
            - result: Detailed sync results
            - success: Boolean indicating overall success
    """
    synchronizer = services.get('synchronizer')
    
    if not synchronizer:
        return {
            'error': 'Synchronizer service not available',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Starting sync operation (type={sync_type}, asset={asset_code or 'all'})...")
    
    try:
        result = {}
        
        # Liquidity pool sync
        if sync_type == 'lp_only':
            result = await run_sync_liquidity_pools(services, asset_code)
            
        elif sync_type == 'accounts':
            # Sync account data only
            if asset_code:
                result = await synchronizer.sync_account_data(asset_code)
            else:
                results = {}
                for code in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
                    results[code] = await synchronizer.sync_account_data(code)
                result = results
                
        elif sync_type == 'transactions':
            # Sync transactions only
            if asset_code:
                result = await synchronizer.sync_transaction_data(asset_code)
            else:
                results = {}
                for code in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
                    results[code] = await synchronizer.sync_transaction_data(code)
                result = results
                
        elif sync_type == 'operations':
            # Sync operations only
            logger.warning("Operations sync not yet implemented - placeholder")
            result = {'message': 'Operations sync not yet implemented'}
                
        elif sync_type == 'effects':
            # Sync effects only
            logger.warning("Effects sync not yet implemented - placeholder")
            result = {'message': 'Effects sync not yet implemented'}
                
        elif sync_type == 'balances':
            # Sync balances only
            if asset_code:
                result = await synchronizer.sync_balance_data(asset_code)
            else:
                results = {}
                for code in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
                    results[code] = await synchronizer.sync_balance_data(code)
                result = results
                
        elif sync_type == 'all':
            # Sync everything (original behavior)
            if asset_code:
                result = await synchronizer.sync_account_data(asset_code)
            else:
                results = {}
                for code in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
                    results[code] = await synchronizer.sync_account_data(code)
                result = results
        
        else:
            return {
                'error': f'Unknown sync type: {sync_type}',
                'available_types': ['all', 'accounts', 'transactions', 'operations', 
                                   'effects', 'balances', 'lp_only'],
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'sync_type': sync_type,
            'asset_code': asset_code or 'all',
            'result': result,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Sync error: {e}")
        logger.exception("Full traceback:")
        return {
            'timestamp': datetime.now().isoformat(),
            'sync_type': sync_type,
            'error': str(e),
            'success': False
        }


async def run_sync_liquidity_pools(
    services: Dict[str, Any],
    asset_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synchronize liquidity pool data from Stellar network.
    
    Args:
        services: Service instances
        asset_code: Optional specific asset code (e.g., 'UBEC', 'UBECrc')
        
    Returns:
        dict: Liquidity pool sync results
    """
    synchronizer = services.get('synchronizer')
    stellar_client = services.get('stellar_client')
    config = services.get('config')
    
    if not synchronizer:
        return {
            'error': 'Synchronizer service not available',
            'hint': 'Check that UBECDataSynchronizer initialized properly',
            'timestamp': datetime.now().isoformat()
        }
    
    if not stellar_client:
        return {
            'error': 'Stellar client not available - required for LP sync',
            'hint': 'Check that ServerAsync initialized properly in initialize_services()',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info("="*70)
    logger.info("LIQUIDITY POOL SYNCHRONIZATION")
    logger.info("="*70)
    
    try:
        # Check if synchronizer has LP sync method
        if not hasattr(synchronizer, 'sync_liquidity_pools'):
            return {
                'error': 'Liquidity pool sync not implemented in synchronizer',
                'message': 'Please add sync_liquidity_pools() method to UBECDataSynchronizer',
                'timestamp': datetime.now().isoformat()
            }
        
        # Determine which assets to sync
        assets_to_sync = []
        if asset_code:
            assets_to_sync = [asset_code]
        else:
            # Sync all UBEC family tokens
            assets_to_sync = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']
        
        # Initialize aggregate metrics
        results = {}
        total_pools = 0
        total_participants = 0
        total_tvl = 0.0
        
        # Sync each asset's liquidity pools
        for code in assets_to_sync:
            logger.info(f"Syncing liquidity pools for {code}...")
            
            try:
                # Get issuer from config
                if code == 'UBEC':
                    issuer = config.UBEC_ISSUER
                else:
                    issuer = config.get(f'{code.lower()}_issuer', config.UBEC_ISSUER)
                
                # Call synchronizer's LP sync method
                lp_result = await synchronizer.sync_liquidity_pools(
                    asset_code=code,
                    asset_issuer=issuer
                )
                
                results[code] = lp_result
                
                # Aggregate metrics
                if isinstance(lp_result, dict) and lp_result.get('success'):
                    total_pools += lp_result.get('pools_synced', 0)
                    total_participants += lp_result.get('participants_synced', 0)
                    total_tvl += float(lp_result.get('total_tvl', 0))
                    
                    logger.info(f"✓ {code} LP sync complete: "
                              f"{lp_result.get('pools_synced', 0)} pools, "
                              f"{lp_result.get('participants_synced', 0)} participants")
                else:
                    logger.warning(f"LP sync for {code} returned unexpected result")
                
            except Exception as e:
                logger.error(f"Failed to sync {code} liquidity pools: {e}")
                results[code] = {
                    'error': str(e),
                    'success': False
                }
        
        # Build summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'sync_type': 'liquidity_pools',
            'assets_synced': len([r for r in results.values() if isinstance(r, dict) and r.get('success')]),
            'total_pools': total_pools,
            'total_participants': total_participants,
            'total_tvl': total_tvl,
            'results': results,
            'success': True
        }
        
        logger.info("="*70)
        logger.info(f"✓ LP SYNC COMPLETE")
        logger.info(f"  Assets: {summary['assets_synced']}/{len(assets_to_sync)}")
        logger.info(f"  Pools: {total_pools}")
        logger.info(f"  Participants: {total_participants}")
        logger.info(f"  Total Value Locked: {total_tvl:,.2f}")
        logger.info("="*70)
        
        return summary
        
    except Exception as e:
        logger.error(f"Liquidity pool sync error: {e}")
        logger.exception("Full traceback:")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'success': False
        }


async def run_analytics(services: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
    """
    Run analytics operations using the UBEC Analytics Service.
    
    Args:
        services: Service instances
        analysis_type: Type of analysis (summary, distribution, holders)
        
    Returns:
        dict: Analytics results
    """
    analytics = services.get('analytics')
    
    if not analytics:
        return {
            'error': 'Analytics service not available',
            'message': 'Please ensure services/analytics/ubec_analytics_service.py is in place',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Running {analysis_type} analytics...")
    
    try:
        if analysis_type == 'summary':
            health = await analytics.get_ecosystem_health()
            distributions = await analytics.get_all_token_distributions()
            comparison = await analytics.compare_tokens()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'summary',
                'ecosystem_health': {
                    'total_holders': health.total_holders,
                    'total_accounts': health.total_accounts,
                    'total_transactions': health.total_transactions,
                    'total_supply_all_tokens': float(health.total_supply_all_tokens),
                    'active_accounts_24h': health.active_accounts_24h,
                    'active_accounts_7d': health.active_accounts_7d,
                    'active_accounts_30d': health.active_accounts_30d,
                    'element_balance_score': float(health.element_balance_score)
                },
                'token_summary': {
                    token.token_code: {
                        'element': token.element,
                        'holders': token.total_holders,
                        'supply': float(token.total_supply),
                        'avg_balance': float(token.average_balance),
                        'median_balance': float(token.median_balance),
                        'top_10_concentration': float(token.top_10_concentration),
                        'gini_coefficient': float(token.gini_coefficient) if token.gini_coefficient else None
                    }
                    for token in distributions
                },
                'token_comparison': comparison.get('tokens', {}),
                'totals': comparison.get('totals', {}),
                'rankings': comparison.get('rankings', {})
            }
            
            logger.info("✓ Summary analytics complete")
            
        elif analysis_type == 'distribution':
            distributions = await analytics.get_all_token_distributions()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'distribution',
                'tokens': []
            }
            
            for dist in distributions:
                result['tokens'].append({
                    'token_code': dist.token_code,
                    'element': dist.element,
                    'total_holders': dist.total_holders,
                    'total_supply': float(dist.total_supply),
                    'average_balance': float(dist.average_balance),
                    'median_balance': float(dist.median_balance),
                    'min_balance': float(dist.min_balance),
                    'max_balance': float(dist.max_balance),
                    'concentration': {
                        'top_10': float(dist.top_10_concentration),
                        'top_100': float(dist.top_100_concentration),
                        'gini': float(dist.gini_coefficient) if dist.gini_coefficient else None
                    }
                })
            
            logger.info("✓ Distribution analysis complete")
            
        elif analysis_type == 'holders':
            from decimal import Decimal
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'holders',
                'tokens': []
            }
            
            for token_code in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
                try:
                    holder_analysis = await analytics.analyze_holder_concentration(
                        token_code,
                        whale_threshold=Decimal('50000'),
                        mid_tier_threshold=Decimal('5000')
                    )
                    
                    whales = await analytics.identify_whales(
                        token_code,
                        threshold=Decimal('50000'),
                        limit=10
                    )
                    
                    result['tokens'].append({
                        'token_code': holder_analysis.token_code,
                        'total_holders': holder_analysis.total_holders,
                        'whales': {
                            'count': holder_analysis.whale_count,
                            'holdings': float(holder_analysis.whale_holdings),
                            'percentage': float(holder_analysis.whale_percentage),
                            'top_10': [
                                {
                                    'account': whale['account_id'],
                                    'balance': float(whale['balance'])
                                }
                                for whale in whales[:10]
                            ]
                        },
                        'mid_tier': {
                            'count': holder_analysis.mid_tier_count,
                            'holdings': float(holder_analysis.mid_tier_holdings)
                        },
                        'small_holders': {
                            'count': holder_analysis.small_holder_count,
                            'holdings': float(holder_analysis.small_holder_holdings)
                        }
                    })
                except Exception as e:
                    logger.warning(f"Could not analyze {token_code} holders: {e}")
            
            logger.info("✓ Holder analysis complete")
            
        else:
            result = {
                'error': f'Unknown analysis type: {analysis_type}',
                'available_types': ['summary', 'distribution', 'holders'],
                'timestamp': datetime.now().isoformat()
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }


async def run_evaluate(services: Dict[str, Any], account_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Run holonic evaluation.
    
    Args:
        services: Service instances
        account_id: Optional specific account
        
    Returns:
        dict: Evaluation results
    """
    evaluator = services.get('holonic_evaluator')
    
    if not evaluator:
        return {
            'error': 'Holonic evaluator not available',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Running holonic evaluation (account={account_id or 'system-wide'})...")
    
    try:
        if account_id:
            result = await evaluator.evaluate_account(account_id)
            # Convert to dict if it's a HolonicMetrics object
            if hasattr(result, 'to_dict'):
                result = result.to_dict()
        else:
            result = await evaluator.evaluate_network_holism()
        
        return result
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }


async def run_discover(services: Dict[str, Any], max_accounts: int = 100) -> Dict[str, Any]:
    """
    Discover UBEC token holders.
    
    Args:
        services: Service instances
        max_accounts: Maximum accounts to discover
        
    Returns:
        dict: Discovery results containing account count
    """
    synchronizer = services.get('synchronizer')
    
    if not synchronizer:
        return {
            'error': 'Synchronizer service not available',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Discovering accounts (max={max_accounts})...")
    
    try:
        # discover_accounts() returns int (count), not list
        accounts_count = await synchronizer.discover_accounts(max_accounts=max_accounts)
        
        # Verify we got an int
        if not isinstance(accounts_count, int):
            logger.warning(f"Unexpected return type from discover_accounts: {type(accounts_count)}")
            accounts_count = 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'accounts_discovered': accounts_count,
            'max_requested': max_accounts,
            'message': f'Discovered {accounts_count} account(s). Data stored in database.',
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'success': False
        }


# ==================== DISTRIBUTION OPERATIONS ====================

def display_rebalance_preview(preview: Dict[str, Any]) -> None:
    """
    Display rebalance preview in user-friendly format.
    
    Args:
        preview: Preview data from distribution service
    """
    print("\n" + "="*70)
    print("REBALANCE OPERATION PREVIEW")
    print("="*70)
    
    # Current state
    current = preview.get('current_state', {})
    if current:
        print("\n📊 CURRENT STATE:")
        compliance = current.get('compliance', {})
        print(f"   Compliance: {'✓ COMPLIANT' if compliance.get('overall') else '✗ NON-COMPLIANT'}")
        
        dist = current.get('distribution', {})
        if dist:
            print(f"   General:        {dist.get('general', 0)*100:6.2f}%")
            print(f"   Administration: {dist.get('administration', 0)*100:6.2f}%")
            print(f"   Stewardship:    {dist.get('stewardship', 0)*100:6.2f}%")
    
    # Proposed operations
    operations = preview.get('transfers', preview.get('proposed_operations', []))
    print(f"\n🔄 PROPOSED OPERATIONS ({len(operations)} transfers):")
    for i, op in enumerate(operations, 1):
        print(f"\n   {i}. Transfer {op['amount']:,.2f} UBEC")
        print(f"      From: {op['from']} ({op['from_address'][:8]}...)")
        print(f"      To:   {op['to']} ({op['to_address'][:8]}...)")
        if op.get('reason'):
            print(f"      Reason: {op['reason']}")
    
    # Projected state
    projected = preview.get('projected_state', {})
    if projected:
        print("\n📈 PROJECTED STATE (after rebalance):")
        proj_compliance = projected.get('compliance', {})
        print(f"   Compliance: {'✓ COMPLIANT' if proj_compliance.get('overall') else '✗ STILL NON-COMPLIANT'}")
        
        proj_dist = projected.get('distribution', {})
        if proj_dist:
            print(f"   General:        {proj_dist.get('general', 0)*100:6.2f}%")
            print(f"   Administration: {proj_dist.get('administration', 0)*100:6.2f}%")
            print(f"   Stewardship:    {proj_dist.get('stewardship', 0)*100:6.2f}%")
    
    # Cost estimate
    cost = preview.get('estimated_cost', {})
    if cost:
        print("\n💰 ESTIMATED COST:")
        print(f"   Operations: {cost.get('operations', 0)}")
        print(f"   Total Fee:  {cost.get('total_fee_xlm', 'N/A')}")
    
    print("\n" + "="*70)


async def get_user_confirmation() -> bool:
    """
    Get user confirmation for executing rebalance.
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    print("\n⚠️ WARNING: This will execute REAL blockchain transactions")
    print("   These operations are IRREVERSIBLE once submitted to the network")
    print()
    
    try:
        # Get user input
        confirmation = input("Type 'yes' to execute these operations: ").strip().lower()
        
        if confirmation == 'yes':
            print("\n✓ Confirmed - Proceeding with rebalance operation")
            return True
        else:
            print("\n✗ Operation cancelled")
            return False
            
    except (KeyboardInterrupt, EOFError):
        print("\n\n✗ Operation cancelled by user")
        return False


async def run_distribution_operation(
    services: Dict[str, Any],
    action: str,
    dry_run: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Run distribution management operations with dry-run support.
    
    Args:
        services: Service instances
        action: Distribution action to perform
        dry_run: If True, preview operations without executing
        **kwargs: Additional arguments (days, interval, etc.)
        
    Returns:
        dict: Operation results
    """
    dist_service = services.get('distribution')
    evaluator = services.get('distribution_evaluator')
    
    # Some actions don't require distribution service
    if not dist_service and action not in ['status', 'help']:
        return {
            'error': 'Distribution service not available',
            'message': 'Distribution service failed to initialize. Check logs for details.',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Running distribution operation: {action} (dry_run={dry_run})")
    
    try:
        if action == 'check-compliance':
            result = await dist_service.check_compliance()
            
            # Create snapshot (optional feature - only if implemented)
            if hasattr(dist_service, 'snapshot_distribution'):
                snapshot_id = await dist_service.snapshot_distribution()
                result['snapshot_id'] = snapshot_id
            
            return result
        
        elif action == 'rebalance':
            # Check if rebalance is needed
            needs_rebalance, current_dist = await dist_service.is_rebalance_needed()
            
            if not needs_rebalance:
                return {
                    'message': 'Distribution is compliant, no rebalance needed',
                    'current_distribution': {
                        'general': float(current_dist['general']),
                        'administration': float(current_dist['administration']),
                        'stewardship': float(current_dist['stewardship'])
                    },
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check if perform_rebalance supports dry_run parameter
            import inspect
            rebalance_sig = inspect.signature(dist_service.perform_rebalance)
            supports_dry_run = 'dry_run' in rebalance_sig.parameters
            
            if supports_dry_run:
                # Service supports dry-run natively
                if dry_run:
                    # Just get preview
                    preview = await dist_service.perform_rebalance(dry_run=True)
                    display_rebalance_preview(preview)
                    return preview
                else:
                    # Get preview first, then confirm and execute
                    preview = await dist_service.perform_rebalance(dry_run=True)
                    display_rebalance_preview(preview)
                    
                    # Get user confirmation
                    if not await get_user_confirmation():
                        return {
                            'status': 'cancelled',
                            'message': 'Rebalance operation cancelled by user',
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    # Execute rebalance
                    print("\n📡 Executing rebalance operations...")
                    result = await dist_service.perform_rebalance(dry_run=False)
                    
                    # Create post-rebalance snapshot (optional feature)
                    if hasattr(dist_service, 'snapshot_distribution'):
                        snapshot_id = await dist_service.snapshot_distribution()
                        result['snapshot_id'] = snapshot_id
                    
                    print("✓ Rebalance complete")
                    return result
            else:
                # Service doesn't support dry-run yet
                if dry_run:
                    return {
                        'error': 'Dry-run mode not yet implemented in distribution service',
                        'message': 'Please update distribution_service.py to support dry_run parameter',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # Legacy behavior - direct execution (NOT RECOMMENDED)
                    logger.warning("⚠️ Executing rebalance without dry-run support - this is not recommended!")
                    
                    print("\n⚠️ WARNING: Dry-run mode not available in distribution service")
                    print("   Rebalance will execute immediately without preview")
                    print()
                    
                    confirmation = input("Type 'yes' to proceed WITHOUT preview: ").strip().lower()
                    if confirmation != 'yes':
                        return {
                            'status': 'cancelled',
                            'message': 'Operation cancelled - dry-run mode recommended',
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    result = await dist_service.perform_rebalance()
                    
                    # Create post-rebalance snapshot (optional feature)
                    if hasattr(dist_service, 'snapshot_distribution'):
                        snapshot_id = await dist_service.snapshot_distribution()
                        result['snapshot_id'] = snapshot_id
                    
                    return result
        
        elif action == 'status':
            result = await dist_service.get_distribution_status()
            return result
        
        elif action == 'evaluate':
            if not evaluator:
                return {
                    'error': 'Distribution evaluator not available',
                    'timestamp': datetime.now().isoformat()
                }
            
            result = await evaluator.evaluate_distribution()
            return result
        
        elif action == 'trends':
            if not evaluator:
                return {
                    'error': 'Distribution evaluator not available',
                    'timestamp': datetime.now().isoformat()
                }
            
            days = kwargs.get('days', 30)
            result = await evaluator.get_compliance_trends(days=days)
            return result
        
        elif action == 'schedule':
            interval = kwargs.get('interval', 3600)
            success = await dist_service.schedule_next_check(interval)
            
            if success:
                return {
                    'message': f'Distribution checks scheduled every {interval} seconds',
                    'interval_seconds': interval,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'error': 'Failed to schedule checks',
                    'timestamp': datetime.now().isoformat()
                }
        
        elif action == 'help':
            return {
                'available_actions': [
                    'check-compliance - Check if distribution meets targets',
                    'rebalance --dry-run - Preview rebalancing operations (RECOMMENDED FIRST)',
                    'rebalance - Execute token rebalancing (with confirmation)',
                    'status - Get current distribution status',
                    'evaluate - Evaluate distribution health',
                    'trends --days 30 - Get compliance trends',
                    'schedule --interval 3600 - Schedule automatic checks'
                ],
                'safety_note': 'Always use --dry-run first to preview operations',
                'timestamp': datetime.now().isoformat()
            }
        
        else:
            return {
                'error': f'Unknown distribution action: {action}',
                'available_actions': ['check-compliance', 'rebalance', 'status', 'evaluate', 'trends', 'schedule', 'help'],
                'timestamp': datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Distribution operation error: {e}")
        logger.exception("Full traceback:")
        return {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'error': str(e),
            'traceback': 'See logs for full traceback'
        }


# ==================== PROTOCOL OPERATIONS ====================

async def run_protocol_health(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check health of all protocol services.
    
    Args:
        services: Service instances
        
    Returns:
        dict: Protocol health status
    """
    logger.info("Checking protocol health...")
    
    protocols = {}
    
    for protocol_name in ['air', 'water', 'earth', 'fire']:
        service = services.get(protocol_name)
        
        if service and hasattr(service, 'health_check'):
            try:
                health = await service.health_check()
                protocols[protocol_name] = health
            except Exception as e:
                protocols[protocol_name] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
        else:
            protocols[protocol_name] = {
                'status': 'NOT_AVAILABLE'
            }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'protocols': protocols
    }


async def run_protocol_status(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get status of all protocol services.
    
    Args:
        services: Service instances
        
    Returns:
        dict: Protocol status
    """
    logger.info("Getting protocol status...")
    
    protocols = {}
    
    for protocol_name in ['air', 'water', 'earth', 'fire']:
        service = services.get(protocol_name)
        
        if service and hasattr(service, 'get_status'):
            try:
                status = await service.get_status()
                protocols[protocol_name] = {
                    'status': 'ACTIVE',
                    'data': status
                }
            except Exception as e:
                protocols[protocol_name] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
        elif service:
            protocols[protocol_name] = {
                'status': 'AVAILABLE',
                'message': 'Service initialized but get_status() method not implemented',
                'service_type': type(service).__name__
            }
        else:
            protocols[protocol_name] = {
                'status': 'NOT_AVAILABLE'
            }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'protocols': protocols
    }


async def run_protocol_sync(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronize all protocol services.
    
    Args:
        services: Service instances
        
    Returns:
        dict: Sync results
    """
    logger.info("Synchronizing protocols...")
    
    results = {}
    
    # Sync each protocol concurrently
    tasks = {}
    for protocol_name in ['air', 'water', 'earth', 'fire']:
        service = services.get(protocol_name)
        
        if service and hasattr(service, 'sync_protocol_data'):
            tasks[protocol_name] = service.sync_protocol_data()
    
    if tasks:
        sync_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for (protocol_name, _), result in zip(tasks.items(), sync_results):
            if isinstance(result, Exception):
                results[protocol_name] = {
                    'status': 'ERROR',
                    'error': str(result)
                }
            else:
                results[protocol_name] = {
                    'status': 'SUCCESS',
                    'data': result
                }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'total': len(results),
            'successful': sum(1 for r in results.values() if r.get('status') == 'SUCCESS'),
            'failed': sum(1 for r in results.values() if r.get('status') == 'ERROR')
        }
    }


# ==================== VISUALIZATION OPERATIONS ⭐ NEW in v4.7 ====================

async def run_visualize(
    services: Dict[str, Any],
    action: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Run visualization operations.
    
    ⭐ NEW in v4.7: Comprehensive visualization service integration
    
    Args:
        services: Service instances
        action: Visualization action ('chart', 'report', 'all')
        **kwargs: Additional arguments:
            - chart_type: Type of chart (radar, bar, line, pie, network)
            - top_n: Number of top accounts to include
            - metric: Specific metric to visualize
            - days: Time range for trend charts
            - category: Category filter
            - min_connections: Minimum connections for network charts
            - format: Output format (png, svg, html, json)
            - output: Output file path
            - output_dir: Output directory for multiple files
            
    Returns:
        dict: Visualization results
        
    Design Notes:
        - Implements Principle #2: Uses service pattern (no standalone execution)
        - Implements Principle #5: All operations async
        - Implements Principle #12: No redundant methods (single visualization point)
        - Implements Principle #10: Clear separation (viz logic in service)
        
    Examples:
        >>> # Radar chart of top 10 accounts
        >>> await run_visualize(services, 'chart', chart_type='radar', top_n=10)
        
        >>> # Bar chart of token supply
        >>> await run_visualize(services, 'chart', chart_type='bar', metric='supply')
        
        >>> # Network visualization
        >>> await run_visualize(services, 'chart', chart_type='network', min_connections=5)
        
        >>> # HTML report
        >>> await run_visualize(services, 'report', format='html', output='report.html')
    """
    visualizer = services.get('visualizer')
    holonic_evaluator = services.get('holonic_evaluator')
    
    if not visualizer:
        return {
            'error': 'Visualization service not available',
            'message': 'Visualization service failed to initialize. Check logs for details.',
            'hint': 'Ensure core/holonic/ubec_holonic_visualizer.py is present',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Running visualization operation: {action}")
    
    try:
        if action == 'chart':
            chart_type = kwargs.get('chart_type', 'radar')
            
            # Ensure we have data to visualize
            if holonic_evaluator:
                logger.info("Loading evaluation data from database...")
                # Load fresh data from database
                await visualizer.load_evaluation_data()
            else:
                logger.warning("⚠️ Holonic evaluator not available - loading data directly from database")
                await visualizer.load_evaluation_data()
            
            # Generate chart based on type
            if chart_type == 'radar':
                top_n = kwargs.get('top_n', 10)
                
                # Provide default output path if not specified
                if not kwargs.get('output'):
                    output = f'visualizations/radar_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                else:
                    output = kwargs.get('output')
                
                logger.info(f"Generating radar chart (top {top_n} accounts)...")
                
                # Create output directory if needed
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Generate chart
                result_path = await visualizer.create_radar_chart(
                    output_file=str(output_path),
                    top_n=top_n
                )
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'chart',
                    'chart_type': 'radar',
                    'output': str(result_path) if result_path else None,
                    'top_n': top_n,
                    'success': result_path is not None,
                    'message': f'Radar chart saved to {result_path}' if result_path else 'Chart generation failed'
                }
            
            elif chart_type == 'bar':
                metric = kwargs.get('metric', 'composite_score')
                
                # Provide default output path if not specified
                if not kwargs.get('output'):
                    output = f'visualizations/bar_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                else:
                    output = kwargs.get('output')
                
                logger.info(f"Generating bar chart (metric: {metric})...")
                
                # Create output directory if needed
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if visualizer has bar chart method
                if hasattr(visualizer, 'create_bar_chart'):
                    result_path = await visualizer.create_bar_chart(
                        output_file=str(output_path),
                        metric=metric
                    )
                else:
                    return {
                        'error': 'Bar chart not yet implemented in visualizer',
                        'hint': 'Add create_bar_chart() method to UBECHolonicVisualizer',
                        'timestamp': datetime.now().isoformat()
                    }
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'chart',
                    'chart_type': 'bar',
                    'output': str(result_path) if result_path else None,
                    'metric': metric,
                    'success': result_path is not None
                }
            
            elif chart_type == 'line':
                days = kwargs.get('days', 30)
                
                # Provide default output path if not specified
                if not kwargs.get('output'):
                    output = f'visualizations/line_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                else:
                    output = kwargs.get('output')
                
                logger.info(f"Generating line chart (last {days} days)...")
                
                # Create output directory if needed
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if visualizer has line chart method
                if hasattr(visualizer, 'create_trend_chart'):
                    result_path = await visualizer.create_trend_chart(
                        output_file=str(output_path),
                        days=days
                    )
                else:
                    return {
                        'error': 'Line chart not yet implemented in visualizer',
                        'hint': 'Add create_trend_chart() method to UBECHolonicVisualizer',
                        'timestamp': datetime.now().isoformat()
                    }
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'chart',
                    'chart_type': 'line',
                    'output': str(result_path) if result_path else None,
                    'days': days,
                    'success': result_path is not None
                }
            
            elif chart_type == 'pie':
                category = kwargs.get('category', 'holonic_category')
                
                # Provide default output path if not specified
                if not kwargs.get('output'):
                    output = f'visualizations/pie_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                else:
                    output = kwargs.get('output')
                
                logger.info(f"Generating pie chart (category: {category})...")
                
                # Create output directory if needed
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Use category distribution chart
                result_path = await visualizer.create_category_distribution_chart(
                    output_file=str(output_path)
                )
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'chart',
                    'chart_type': 'pie',
                    'output': str(result_path) if result_path else None,
                    'category': category,
                    'success': result_path is not None
                }
            
            elif chart_type == 'network':
                min_connections = kwargs.get('min_connections', 1)
                
                # Provide default output path if not specified
                if not kwargs.get('output'):
                    output = f'visualizations/network_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                else:
                    output = kwargs.get('output')
                
                logger.info(f"Generating network chart (min connections: {min_connections})...")
                
                # Create output directory if needed
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if visualizer has network method
                if hasattr(visualizer, 'create_network_visualization'):
                    result_path = await visualizer.create_network_visualization(
                        output_file=str(output_path),
                        min_connections=min_connections
                    )
                else:
                    return {
                        'error': 'Network visualization not yet implemented',
                        'hint': 'Add create_network_visualization() method to UBECHolonicVisualizer',
                        'timestamp': datetime.now().isoformat()
                    }
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'chart',
                    'chart_type': 'network',
                    'output': str(result_path) if result_path else None,
                    'min_connections': min_connections,
                    'success': result_path is not None
                }
            
            else:
                return {
                    'error': f'Unknown chart type: {chart_type}',
                    'available_types': ['radar', 'bar', 'line', 'pie', 'network'],
                    'timestamp': datetime.now().isoformat()
                }
        
        elif action == 'report':
            output_format = kwargs.get('format', 'html')
            output = kwargs.get('output')
            output_dir = kwargs.get('output_dir', 'visualizations')
            
            # Ensure we have data
            if holonic_evaluator:
                await visualizer.load_evaluation_data()
            
            if output_format == 'html':
                logger.info("Generating HTML report...")
                
                # Create output directory
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
                # Generate HTML report
                report_path = await visualizer.generate_html_report(
                    output_dir=output_dir
                )
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'report',
                    'format': 'html',
                    'output': report_path,
                    'success': report_path is not None,
                    'message': f'HTML report generated at {report_path}' if report_path else 'Report generation failed'
                }
            
            elif output_format == 'json':
                logger.info("Generating JSON report...")
                
                # Get evaluation data
                if not visualizer.report_data:
                    await visualizer.load_evaluation_data()
                
                report_data = visualizer.report_data
                
                if output:
                    # Save to file
                    output_path = Path(output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, 'w') as f:
                        json.dump(report_data, f, indent=2, default=str)
                    
                    return {
                        'timestamp': datetime.now().isoformat(),
                        'action': 'report',
                        'format': 'json',
                        'output': str(output_path),
                        'success': True
                    }
                else:
                    # Return data directly
                    return {
                        'timestamp': datetime.now().isoformat(),
                        'action': 'report',
                        'format': 'json',
                        'data': report_data,
                        'success': True
                    }
            
            else:
                return {
                    'error': f'Unknown report format: {output_format}',
                    'available_formats': ['html', 'json'],
                    'timestamp': datetime.now().isoformat()
                }
        
        elif action == 'all':
            output_dir = kwargs.get('output_dir', 'visualizations')
            
            logger.info(f"Generating all visualizations in {output_dir}...")
            
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Ensure we have data
            if holonic_evaluator:
                await visualizer.load_evaluation_data()
            
            # Generate timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            results = {}
            
            # Radar chart
            try:
                radar_path = Path(output_dir) / f"radar_chart_{timestamp}.png"
                await visualizer.create_radar_chart(output_file=str(radar_path))
                results['radar'] = str(radar_path)
            except Exception as e:
                logger.warning(f"Failed to generate radar chart: {e}")
                results['radar'] = None
            
            # Score distribution
            try:
                score_dist_path = Path(output_dir) / f"score_distribution_{timestamp}.png"
                await visualizer.create_score_distribution_chart(output_file=str(score_dist_path))
                results['score_distribution'] = str(score_dist_path)
            except Exception as e:
                logger.warning(f"Failed to generate score distribution: {e}")
                results['score_distribution'] = None
            
            # Category distribution
            try:
                category_path = Path(output_dir) / f"category_distribution_{timestamp}.png"
                await visualizer.create_category_distribution_chart(output_file=str(category_path))
                results['category_distribution'] = str(category_path)
            except Exception as e:
                logger.warning(f"Failed to generate category distribution: {e}")
                results['category_distribution'] = None
            
            # Network visualization
            if hasattr(visualizer, 'create_network_visualization'):
                try:
                    network_path = Path(output_dir) / f"network_{timestamp}.png"
                    await visualizer.create_network_visualization(output_file=str(network_path))
                    results['network'] = str(network_path)
                except Exception as e:
                    logger.warning(f"Failed to generate network visualization: {e}")
                    results['network'] = None
            
            # HTML report
            try:
                html_report = await visualizer.generate_html_report(output_dir=output_dir)
                results['html_report'] = html_report
            except Exception as e:
                logger.warning(f"Failed to generate HTML report: {e}")
                results['html_report'] = None
            
            return {
                'timestamp': datetime.now().isoformat(),
                'action': 'all',
                'output_dir': output_dir,
                'results': results,
                'success': any(v is not None for v in results.values()),
                'message': f'Generated {sum(1 for v in results.values() if v is not None)} visualizations'
            }
        
        else:
            return {
                'error': f'Unknown visualization action: {action}',
                'available_actions': ['chart', 'report', 'all'],
                'timestamp': datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        logger.exception("Full traceback:")
        return {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'error': str(e),
            'traceback': 'See logs for full traceback'
        }


# ==================== CLI ====================

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='UBEC Protocol Suite - Unified Management System (v4.7)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # System Operations
  %(prog)s --mode health                          # System health
  %(prog)s --mode status                          # System status
  
  # Data Sync Operations - ENHANCED WITH GRANULAR CONTROL
  %(prog)s --mode sync                            # Sync all data (default)
  %(prog)s --mode sync --sync-type accounts       # Sync accounts only
  %(prog)s --mode sync --sync-type transactions   # Sync transactions only
  %(prog)s --mode sync --sync-type operations     # Sync operations only
  %(prog)s --mode sync --sync-type effects        # Sync effects only
  %(prog)s --mode sync --sync-type balances       # Sync balances only
  %(prog)s --mode sync --sync-type lp_only        # Sync liquidity pools only
  %(prog)s --mode sync --sync-type lp_only --asset-code UBEC  # Sync UBEC LPs
  %(prog)s --mode sync --asset-code UBECrc        # Sync specific asset (all data)
  
  # Data Operations
  %(prog)s --mode discover --max-accounts 100     # Discover accounts
  %(prog)s --mode analytics --analysis-type summary  # Analytics
  
  # Protocol Operations
  %(prog)s --mode protocol-health                 # Protocol health
  %(prog)s --mode protocol-status                 # Protocol status
  %(prog)s --mode protocol-sync                   # Sync protocols
  %(prog)s --mode evaluate                        # Holonic evaluation
  %(prog)s --mode evaluate --account GXXX         # Account evaluation
  
  # Distribution Management (with dry-run support)
  %(prog)s --mode distribution --action check-compliance
  %(prog)s --mode distribution --action rebalance --dry-run    # PREVIEW
  %(prog)s --mode distribution --action rebalance              # EXECUTE
  %(prog)s --mode distribution --action status
  %(prog)s --mode distribution --action evaluate
  %(prog)s --mode distribution --action trends --days 30
  %(prog)s --mode distribution --action schedule --interval 3600
  
  # Visualization Operations ⭐ NEW in v4.7
  %(prog)s --mode visualize --action chart --chart-type radar --top-n 10
  %(prog)s --mode visualize --action chart --chart-type bar --metric supply
  %(prog)s --mode visualize --action chart --chart-type line --days 30
  %(prog)s --mode visualize --action chart --chart-type pie
  %(prog)s --mode visualize --action chart --chart-type network --min-connections 5
  %(prog)s --mode visualize --action report --format html --output report.html
  %(prog)s --mode visualize --action report --format json --output report.json
  %(prog)s --mode visualize --action all --output-dir visualizations/
        """
    )
    
    # Main mode
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=[
            'health', 'status', 'sync', 'discover', 'analytics', 'evaluate',
            'protocol-health', 'protocol-status', 'protocol-sync',
            'distribution', 'visualize'
        ],
        help='Operation mode'
    )
    
    # Sync options
    parser.add_argument(
        '--sync-type',
        type=str,
        choices=['all', 'accounts', 'transactions', 'operations', 'effects', 'balances', 'lp_only'],
        default='all',
        help='Type of data to sync (default: all)'
    )
    
    parser.add_argument(
        '--asset-code',
        type=str,
        choices=['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt'],
        help='Specific asset code (for sync mode)'
    )
    
    # Analytics options
    parser.add_argument(
        '--analysis-type',
        type=str,
        choices=['summary', 'distribution', 'holders'],
        default='summary',
        help='Type of analysis (for analytics mode)'
    )
    
    # Evaluation options
    parser.add_argument(
        '--account',
        type=str,
        help='Specific account ID (for evaluate mode)'
    )
    
    # Discovery options
    parser.add_argument(
        '--max-accounts',
        type=int,
        default=100,
        help='Maximum accounts to discover (for discover mode)'
    )
    
    # Distribution options
    parser.add_argument(
        '--action',
        type=str,
        choices=[
            'check-compliance', 'rebalance', 'status', 'evaluate',
            'trends', 'schedule', 'help', 'chart', 'report', 'all'
        ],
        help='Action (for distribution or visualization mode)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for trend analysis'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='Check interval in seconds (for schedule action)'
    )
    
    # Dry-run flag for safe preview
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview operations without executing (RECOMMENDED for rebalance)'
    )
    
    # ⭐ NEW in v4.7: Visualization options
    parser.add_argument(
        '--chart-type',
        type=str,
        choices=['radar', 'bar', 'line', 'pie', 'network'],
        help='Type of chart to generate'
    )
    
    parser.add_argument(
        '--top-n',
        type=int,
        default=10,
        help='Number of top accounts to include in charts'
    )
    
    parser.add_argument(
        '--metric',
        type=str,
        help='Specific metric to visualize'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Category filter for charts'
    )
    
    parser.add_argument(
        '--min-connections',
        type=int,
        default=1,
        help='Minimum connections for network visualization'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['png', 'svg', 'html', 'json'],
        default='png',
        help='Output format for visualizations'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for multiple visualizations'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (for charts and reports)'
    )
    
    parser.add_argument(
        '--output-format',
        type=str,
        choices=['json', 'pretty', 'summary'],
        default='pretty',
        help='CLI output format (default: pretty)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    return parser.parse_args()


def format_output(data: Any, output_format: str) -> str:
    """
    Format output based on specified format.
    
    Args:
        data: Data to format
        output_format: Format type
        
    Returns:
        Formatted string
    """
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)
    elif output_format == 'summary':
        if isinstance(data, dict):
            lines = []
            lines.append(f"Timestamp: {data.get('timestamp', 'N/A')}")
            lines.append(f"Status: {data.get('overall_status', data.get('success', 'N/A'))}")
            return '\n'.join(lines)
        return str(data)
    else:  # pretty
        return json.dumps(data, indent=2, default=str)


# ==================== ASYNC MAIN ====================

async def main_async(args: argparse.Namespace) -> int:
    """
    Async main function - the actual orchestrator.
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        Exit code
    """
    services = None
    
    try:
        # Step 1: Initialize database manager FIRST
        db_manager = await initialize_database()
        
        # Step 2: Load configuration from database (Principle #4: Single Source of Truth)
        logger.info("Loading configuration from database...")
        config = await get_system_config(db_manager)
        logger.info(f"✓ Configuration loaded from database: {len(config._settings)} settings")
        
        # Step 3: Initialize all services with database-backed config
        services = await initialize_services(config, db_manager)
        
        # Execute requested operation
        result = None
        
        if args.mode == 'health':
            result = await run_health_check(services)
        
        elif args.mode == 'sync':
            result = await run_sync(
                services,
                sync_type=args.sync_type,
                asset_code=args.asset_code
            )
        
        elif args.mode == 'analytics':
            result = await run_analytics(services, args.analysis_type)
        
        elif args.mode == 'evaluate':
            result = await run_evaluate(services, args.account)
        
        elif args.mode == 'discover':
            result = await run_discover(services, args.max_accounts)
        
        elif args.mode == 'protocol-health':
            result = await run_protocol_health(services)
        
        elif args.mode == 'protocol-status':
            result = await run_protocol_status(services)
        
        elif args.mode == 'protocol-sync':
            result = await run_protocol_sync(services)
        
        elif args.mode == 'distribution':
            if not args.action:
                result = {
                    'error': 'Distribution mode requires --action parameter',
                    'available_actions': ['check-compliance', 'rebalance', 'status', 'evaluate', 'trends', 'schedule', 'help'],
                    'hint': 'Try: python main.py --mode distribution --action help',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                result = await run_distribution_operation(
                    services,
                    args.action,
                    dry_run=args.dry_run,
                    days=args.days,
                    interval=args.interval
                )
        
        # ⭐ NEW in v4.7: Visualization mode
        elif args.mode == 'visualize':
            if not args.action:
                result = {
                    'error': 'Visualize mode requires --action parameter',
                    'available_actions': ['chart', 'report', 'all'],
                    'hint': 'Try: python main.py --mode visualize --action chart --chart-type radar --top-n 10',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                result = await run_visualize(
                    services,
                    args.action,
                    chart_type=args.chart_type,
                    top_n=args.top_n,
                    metric=args.metric,
                    days=args.days,
                    category=args.category,
                    min_connections=args.min_connections,
                    format=args.format,
                    output=args.output,
                    output_dir=args.output_dir
                )
        
        else:
            logger.error(f"Unknown mode: {args.mode}")
            return 1
        
        # Output result
        if result:
            # Special handling for certain modes
            skip_output = (
                (args.mode == 'distribution' and args.action == 'rebalance' and args.dry_run) or
                (args.mode == 'visualize' and args.action in ['chart', 'all'])
            )
            
            if not skip_output:
                output = format_output(result, args.output_format)
                print("\n" + "=" * 70)
                print(f"UBEC Protocol - {args.mode.upper()} Result")
                if args.mode == 'sync':
                    print(f"Sync Type: {args.sync_type}")
                elif args.mode == 'visualize':
                    print(f"Action: {args.action}")
                print("=" * 70)
                print(output)
                print("=" * 70 + "\n")
            
            # Determine exit code
            if isinstance(result, dict):
                if result.get('success') is False or 'error' in result:
                    return 1
                if result.get('overall_status') in ['POOR', 'ERROR']:
                    return 1
                if result.get('status') == 'cancelled':
                    return 0  # Cancellation is not an error
            
            return 0
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n✓ Operation cancelled by user")
        return 0
    
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        return 1
    
    finally:
        # Always cleanup
        if services:
            await shutdown_services(services)


# ==================== MAIN ENTRY POINT ====================

def main() -> int:
    """
    Synchronous main entry point.
    
    This is the ONLY standalone execution in the entire system.
    Per Design Principle #2: Only main.py has standalone execution.
    
    Returns:
        Exit code
    """
    # Parse arguments
    args = parse_arguments()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Log startup
    logger.info("=" * 70)
    logger.info("UBEC Protocol - Unified Main Orchestrator")
    logger.info(f"Mode: {args.mode}")
    if args.mode == 'sync':
        logger.info(f"Sync Type: {args.sync_type}")
        if args.asset_code:
            logger.info(f"Asset Code: {args.asset_code}")
    elif args.mode == 'visualize':
        logger.info(f"Action: {args.action}")
        if args.chart_type:
            logger.info(f"Chart Type: {args.chart_type}")
    logger.info(f"Version: 4.7.0 (Added visualization service)")
    logger.info(f"Python: {sys.version.split()[0]}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # Run async main
    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 0
    except Exception as e:
        logger.critical(f"Critical error in main: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    """
    Entry point guard - ensures this is the ONLY file with standalone execution.
    
    Following Principle #2: Service Pattern with Centralized Execution
    - ALL other modules are services
    - ALL services accessed via proper initialization
    - NO other files have if __name__ == "__main__"
    
    This is a critical design principle that:
    - Prevents circular dependencies
    - Enables proper dependency injection
    - Facilitates testing
    - Ensures consistent initialization order
    """
    sys.exit(main())
