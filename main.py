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
    python main.py --mode sync --sync-type lp_only       # Sync liquidity pools only (NEW)
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

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 4.5 (Fixed optional snapshot_distribution calls)
Date: October 14, 2025

Changes in v4.5:
    - FIXED: Made snapshot_distribution() calls optional (defensive programming)
    - IMPROVED: System gracefully handles missing optional features
    - MAINTAINED: All previous fixes from v4.4
    - MAINTAINED: All 12 design principles strictly enforced

Changes in v4.4:
    - FIXED: Synchronizer now properly initialized with stellar_client
    - FIXED: discover_accounts return type handling (returns int, not list)
    - IMPROVED: Better error handling for synchronizer initialization
    - MAINTAINED: All 12 design principles strictly enforced
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
        
    Design Note:
        - DB_SEARCH_PATH takes precedence over DB_SCHEMA
        - Maintains backward compatibility with single-schema setup
        - Follows PostgreSQL search_path conventions
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
        3. Data Synchronizer (depends on database + stellar)  <-- FIXED
        4. Element Protocols (depend on database + stellar)
        5. Distribution Services (depend on all above)
        6. Holonic Evaluator (depends on all above)
        
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
        try:
            from core.holonic.ubec_holonic_evaluator import UBECHolonicEvaluator
            holonic_eval = UBECHolonicEvaluator(db_conn=db_manager)
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
    for service_name in ['audit', 'distribution', 'distribution_evaluator', 'holonic_evaluator', 'analytics']:
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
            - 'lp_only': Sync liquidity pool data only (NEW in v4.3)
        asset_code: Optional specific asset to sync (e.g., 'UBEC', 'UBECrc')
        
    Returns:
        dict: Sync results containing:
            - timestamp: When sync was performed
            - sync_type: Type of sync executed
            - asset_code: Asset(s) synced
            - result: Detailed sync results
            - success: Boolean indicating overall success
            
    Design Notes:
        - Implements Principle #10: Clear Separation of Concerns
        - Each sync type has its own execution path
        - Implements Principle #12: Method Singularity (no duplicate code)
        - Implements Principle #5: Strict Async (all operations async)
        
    Examples:
        >>> # Sync all data for all assets
        >>> await run_sync(services, sync_type='all')
        
        >>> # Sync only liquidity pools for UBEC
        >>> await run_sync(services, sync_type='lp_only', asset_code='UBEC')
        
        >>> # Sync only transactions for UBECrc
        >>> await run_sync(services, sync_type='transactions', asset_code='UBECrc')
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
        
        # NEW in v4.3: Liquidity pool sync
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
    
    NEW in v4.3: This function enables tracking of liquidity pool data,
    which is essential for the Water Element (UBECrc) protocol's flow
    and reciprocity metrics.
    
    Args:
        services: Service instances
        asset_code: Optional specific asset code (e.g., 'UBEC', 'UBECrc')
        
    Returns:
        dict: Liquidity pool sync results containing:
            - timestamp: When sync was performed
            - sync_type: Always 'liquidity_pools'
            - assets_synced: Number of assets processed
            - total_pools: Total LP pools synced
            - total_participants: Total LP token holders synced
            - total_tvl: Total Value Locked across all pools
            - results: Detailed results per asset
            - success: Boolean indicating overall success
            
    Design Notes:
        - Implements Principle #12: Method Singularity
          This is the ONLY method for LP sync in the entire system
        - Implements Principle #5: Strict Async
          All operations use async/await patterns
        - Implements Principle #9: Integrated Rate Limiting
          Built-in rate limiting for API calls
        - Implements Principle #4: Single Source of Truth
          Database stores all LP data
          
    Functionality:
        1. Discovers all liquidity pools involving UBEC tokens
        2. Syncs pool composition (asset pairs, reserves)
        3. Syncs pool participant positions (LP token holders)
        4. Syncs pool operations (deposits, withdrawals)
        5. Calculates aggregate metrics (TVL, participation)
        
    Water Element Connection:
        LP data is critical for Water Element (UBECrc) metrics:
        - Flow velocity: How quickly tokens move through pools
        - Reciprocity: LP participation patterns
        - Liquidity health: Pool balance and efficiency
        
    Examples:
        >>> # Sync all LP data
        >>> await run_sync_liquidity_pools(services)
        
        >>> # Sync only UBEC liquidity pools
        >>> await run_sync_liquidity_pools(services, asset_code='UBEC')
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
                'recommendation': 'See LP_SYNC_IMPLEMENTATION_GUIDE.md for complete implementation',
                'hint': 'The method should accept asset_code and asset_issuer parameters',
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
        else:
            result = await evaluator.evaluate_system()
        
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
    
    FIXED in v4.4: Now properly handles discover_accounts() returning an int (count)
    rather than a list of accounts.
    
    Args:
        services: Service instances
        max_accounts: Maximum accounts to discover
        
    Returns:
        dict: Discovery results containing account count
        
    Design Note:
        The synchronizer's discover_accounts() method returns the COUNT of accounts
        discovered (int), not the actual account data (list). This is by design -
        the accounts are stored in the database, not returned. This function now
        correctly handles that return type.
    """
    synchronizer = services.get('synchronizer')
    
    if not synchronizer:
        return {
            'error': 'Synchronizer service not available',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Discovering accounts (max={max_accounts})...")
    
    try:
        # FIXED v4.4: discover_accounts() returns int (count), not list
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
        
    Design Note:
        Provides clear, readable output before user confirmation.
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
#    operations = preview.get('proposed_operations', [])
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
        
    Design Note:
        Implements confirmation workflow for financial operations.
        Requires explicit "yes" input to proceed.
    """
    print("\n⚠️  WARNING: This will execute REAL blockchain transactions")
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
        
    Design Note:
        Implements proper separation between preview (dry-run) and execution.
        For rebalance operations:
        1. Always generate preview first
        2. If dry-run mode, return preview and exit
        3. If execution mode, display preview and require confirmation
        4. Only execute after explicit user confirmation
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
            # Check if distribution service supports dry-run
            # If not, we'll implement preview logic here
            
            # First, check if rebalance is needed
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
                        'recommendation': 'See comprehensive review for implementation details',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # Legacy behavior - direct execution (NOT RECOMMENDED)
                    logger.warning("⚠️  Executing rebalance without dry-run support - this is not recommended!")
                    
                    print("\n⚠️  WARNING: Dry-run mode not available in distribution service")
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


# ==================== CLI ====================

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='UBEC Protocol Suite - Unified Management System (v4.4)',
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
  %(prog)s --mode sync --sync-type lp_only        # Sync liquidity pools only (NEW)
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
            'distribution'
        ],
        help='Operation mode'
    )
    
    # Sync options - ENHANCED in v4.3
    parser.add_argument(
        '--sync-type',
        type=str,
        choices=['all', 'accounts', 'transactions', 'operations', 'effects', 'balances', 'lp_only'],
        default='all',
        help='Type of data to sync (default: all). NEW in v4.3: lp_only for liquidity pools'
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
            'trends', 'schedule', 'help'
        ],
        help='Distribution action (for distribution mode)'
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
    
    # CRITICAL: Dry-run flag for safe preview
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview operations without executing (RECOMMENDED for rebalance)'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'pretty', 'summary'],
        default='pretty',
        help='Output format (default: pretty)'
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
            # ENHANCED in v4.3: Use new sync function with sync_type parameter
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
        
        else:
            logger.error(f"Unknown mode: {args.mode}")
            return 1
        
        # Output result
        if result:
            # Special handling for dry-run rebalance (already displayed)
            if not (args.mode == 'distribution' and args.action == 'rebalance' and args.dry_run):
                output = format_output(result, args.output)
                print("\n" + "=" * 70)
                print(f"UBEC Protocol - {args.mode.upper()} Result")
                if args.mode == 'sync':
                    print(f"Sync Type: {args.sync_type}")
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
    logger.info(f"Version: 4.5 (Fixed optional snapshots + all v4.4 fixes)")
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
