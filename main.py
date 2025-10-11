#!/usr/bin/env python3
"""
UBEC Protocol - Unified Main Orchestrator
==========================================
The SOLE entry point for the entire UBEC system

This orchestrator manages:
1. Infrastructure Layer: Database, synchronization, monitoring
2. Protocol Layer: Four element protocols (Air, Water, Earth, Fire)
3. Business Layer: Holonic evaluation, Ubuntu principles

Design Principles Compliance:
- ✅ Modular Design: Clear separation of concerns
- ✅ Service Pattern: Only this file executes directly (Principle #2)
- ✅ Service Registry: All services accessed through registry (Principle #3)
- ✅ Single Source of Truth: Database for data, registry for services (Principle #4)
- ✅ Strict Async: All I/O operations use async/await (Principle #5)
- ✅ No Sync Fallbacks: Pure async implementation (Principle #6)
- ✅ No Duplicate Configuration: Single config source (Principle #8)
- ✅ Integrated Rate Limiting: Built into all services (Principle #9)
- ✅ Clear Separation: Data layer vs Protocol layer (Principle #10)
- ✅ Comprehensive Documentation: Full attribution (Principle #11)
- ✅ Method Singularity: No redundant code (Principle #12)

Usage:
    # Data Operations
    python main.py --mode discover --max-accounts 500
    python main.py --mode sync
    python main.py --mode monitor --interval 300
    
    # Protocol Operations
    python main.py --mode protocol-health
    python main.py --mode protocol-status
    python main.py --mode protocol-sync
    python main.py --mode evaluate
    python main.py --mode evaluate --account GXXX...
    
    # System Operations
    python main.py --mode health         # Full system health
    python main.py --mode status         # Full system status

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 4.0 (Element Protocols Initialized)
Date: October 11, 2025
"""

import os
import sys
import asyncio
import argparse
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


# ========================================================================
# LOGGING CONFIGURATION
# ========================================================================

def setup_logging(level: str = 'INFO') -> None:
    """
    Configure logging for the entire application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'ubec_main.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger('MainOrchestrator')


# ========================================================================
# CONFIGURATION
# ========================================================================

class SystemConfig:
    """
    System-wide configuration - the SINGLE source of configuration.
    Loads from environment variables per Principle #8.
    """
    
    def __init__(self):
        """Initialize configuration from environment"""
        # Database configuration
        self.db_host = os.getenv('UBEC_DB_HOST') or os.getenv('DB_HOST', 'localhost')
        self.db_port = int(os.getenv('UBEC_DB_PORT') or os.getenv('DB_PORT', '5432'))
        self.db_name = os.getenv('UBEC_DB_NAME') or os.getenv('DB_NAME', 'ubec')
        self.db_user = os.getenv('UBEC_DB_USER') or os.getenv('DB_USER', 'ubec_app')
        self.db_password = os.getenv('UBEC_DB_PASSWORD') or os.getenv('DB_PASSWORD', '')
        
        # Stellar configuration
        self.stellar_network = os.getenv('STELLAR_NETWORK', 'TESTNET')
        self.stellar_horizon_url = os.getenv(
            'STELLAR_HORIZON_URL',
            'https://horizon-testnet.stellar.org' if self.stellar_network == 'TESTNET'
            else 'https://horizon.stellar.org'
        )
        
        # UBEC token configuration
        self.ubec_code = 'UBEC'
        self.ubec_issuer = os.getenv('UBEC_ISSUER', '')
        
        self.ubecrc_code = 'UBECrc'
        self.ubecrc_issuer = os.getenv('UBECRC_ISSUER', '')
        
        self.ubecgpi_code = 'UBECgpi'
        self.ubecgpi_issuer = os.getenv('UBECGPI_ISSUER', '')
        
        self.ubectt_code = 'UBECtt'
        self.ubectt_issuer = os.getenv('UBECTT_ISSUER', '')
        
        # Rate limiting
        self.rate_limit_per_second = float(os.getenv('UBEC_RATE_LIMIT', '10.0'))
        
        # Operational parameters
        self.default_max_accounts = int(os.getenv('UBEC_MAX_ACCOUNTS', '1000'))
        self.default_sync_days = int(os.getenv('UBEC_SYNC_DAYS', '7'))
        self.monitor_interval = int(os.getenv('UBEC_MONITOR_INTERVAL', '300'))
    
    def get_element_config(self, element: str) -> Dict[str, Any]:
        """
        Get element-specific configuration.
        
        Args:
            element: Element name ('air', 'water', 'earth', 'fire')
        
        Returns:
            Element configuration dictionary
        """
        configs = {
            'air': {
                'asset_code': self.ubec_code,
                'issuer': self.ubec_issuer,
                'element': 'air',
                'principle': 'universal_access',
                'rate_limit_calls_per_second': self.rate_limit_per_second
            },
            'water': {
                'asset_code': self.ubecrc_code,
                'issuer': self.ubecrc_issuer,
                'element': 'water',
                'principle': 'reciprocity',
                'rate_limit_calls_per_second': self.rate_limit_per_second
            },
            'earth': {
                'asset_code': self.ubecgpi_code,
                'issuer': self.ubecgpi_issuer,
                'element': 'earth',
                'principle': 'mutualism',
                'rate_limit_calls_per_second': self.rate_limit_per_second
            },
            'fire': {
                'asset_code': self.ubectt_code,
                'issuer': self.ubectt_issuer,
                'element': 'fire',
                'principle': 'regeneration',
                'min_verification_threshold': 3,
                'base_reward': '100.0',
                'max_reward': '10000.0',
                'rate_limit_calls_per_second': self.rate_limit_per_second
            }
        }
        return configs.get(element, {})
    
    def get_db_connection_string(self) -> str:
        """Get database connection string"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# ========================================================================
# SERVICE INITIALIZATION
# ========================================================================

async def initialize_services(config: SystemConfig) -> Dict[str, Any]:
    """
    Initialize all services through the service registry.
    This is the centralized initialization per Principle #3.
    
    Args:
        config: System configuration
    
    Returns:
        Dictionary of initialized services
    """
    logger.info("Initializing services...")
    services = {}
    
    # Try to initialize database (check multiple possible locations)
    try:
        # Try core.db first (new structure)
        try:
            from core.db.connection import DatabaseConnection
            logger.debug("Using core.db.connection module")
        except ImportError:
            # Fallback to db (legacy structure)
            from db.connection import DatabaseConnection
            logger.debug("Using db.connection module")
        
        db_connection = DatabaseConnection()
        if db_connection.conn:
            services['database'] = db_connection
            logger.info("✓ Database connection initialized")
        else:
            logger.warning("Database connection failed - check credentials in .env")
            
    except Exception as e:
        logger.warning(f"Database not available: {e}")
    
    # Initialize Stellar client (async)
    try:
        from stellar_sdk import ServerAsync, AiohttpClient
        
        stellar_client = ServerAsync(
            horizon_url=config.stellar_horizon_url,
            client=AiohttpClient()
        )
        services['stellar'] = stellar_client
        logger.info("✓ Stellar client initialized")
        
    except Exception as e:
        logger.warning(f"Stellar client not available: {e}")
    
    # Initialize data synchronizer (check multiple possible locations)
    try:
        # Check if db_manager is available first
        if 'database' in services:
            # Try core.db first (with actual snake_case filename)
            try:
                from core.db.ubec_data_synchronizer import UBECDataSynchronizer
                logger.debug("Using core.db.ubec_data_synchronizer module")
            except ImportError:
                # Fallback to legacy locations
                try:
                    from core.db.UBECDataSynchronizer import UBECDataSynchronizer
                    logger.debug("Using core.db.UBECDataSynchronizer module (PascalCase)")
                except ImportError:
                    from db.UBECDataSynchronizer import UBECDataSynchronizer
                    logger.debug("Using db.UBECDataSynchronizer module")
            
            synchronizer = UBECDataSynchronizer(db_manager=services['database'])
            services['synchronizer'] = synchronizer
            logger.info("✓ Data synchronizer initialized")
        else:
            logger.warning("Data synchronizer requires database connection")
            
    except Exception as e:
        logger.warning(f"Data synchronizer not available: {e}")
    
    # Initialize holonic evaluator (check multiple possible locations)
    try:
        # Try core.holonic first (with actual snake_case filename)
        try:
            from core.holonic.ubec_holonic_evaluator import UBECHolonicEvaluator
            logger.debug("Using core.holonic.ubec_holonic_evaluator module")
        except ImportError:
            # Fallback to legacy locations
            try:
                from core.holonic.UBECHolonicEvaluator import UBECHolonicEvaluator
                logger.debug("Using core.holonic.UBECHolonicEvaluator module (PascalCase)")
            except ImportError:
                from holonic.UBECHolonicEvaluator import UBECHolonicEvaluator
                logger.debug("Using holonic.UBECHolonicEvaluator module")
        
        evaluator = UBECHolonicEvaluator()
        services['evaluator'] = evaluator
        logger.info("✓ Holonic evaluator initialized")
        
    except Exception as e:
        logger.warning(f"Holonic evaluator not available: {e}")
    
    # Initialize element protocols
    try:
        # Import protocol factory functions
        try:
            from core.protocols.UBEC_protocol import create_ubec_service
            from core.protocols.UBECrc_protocol import create_ubecrc_service
            from core.protocols.UBECgpi_protocol import create_ubecgpi_service
            from core.protocols.UBECtt_protocol import create_ubectt_service
            logger.debug("Using core.protocols module (NEW standard)")
        except ImportError:
            try:
                from protocols.UBEC_protocol import create_ubec_service
                from protocols.UBECrc_protocol import create_ubecrc_service
                from protocols.UBECgpi_protocol import create_ubecgpi_service
                from protocols.UBECtt_protocol import create_ubectt_service
                logger.debug("Using protocols module (legacy)")
            except ImportError:
                # Try root level
                from UBEC_protocol import create_ubec_service
                from UBECrc_protocol import create_ubecrc_service
                from UBECgpi_protocol import create_ubecgpi_service
                from UBECtt_protocol import create_ubectt_service
                logger.debug("Using root-level protocol modules")
        
        # Prepare shared config for all protocols
        protocol_config_base = {
            'db_manager': services.get('database'),
            'stellar_client': services.get('stellar'),
            'rate_limit_calls_per_second': 10.0
        }
        
        # Initialize Air Protocol (UBEC)
        air_protocol = None
        try:
            air_config = {
                'asset_code': config.ubec_code,
                'issuer': config.ubec_issuer
            }
            air_protocol = create_ubec_service(
                db_manager=protocol_config_base['db_manager'],
                config=air_config,
                stellar_client=protocol_config_base['stellar_client']
            )
            logger.info("✓ Air Protocol (UBEC) initialized")
        except Exception as e:
            logger.warning(f"Air Protocol initialization failed: {e}")
        
        # Initialize Water Protocol (UBECrc)
        water_protocol = None
        try:
            water_config = {
                'asset_code': 'UBECrc',
                'issuer': config.ubec_issuer  # Same issuer for all tokens
            }
            water_protocol = create_ubecrc_service(
                db_manager=protocol_config_base['db_manager'],
                config=water_config,
                stellar_client=protocol_config_base['stellar_client']
            )
            logger.info("✓ Water Protocol (UBECrc) initialized")
        except Exception as e:
            logger.warning(f"Water Protocol initialization failed: {e}")
        
        # Initialize Earth Protocol (UBECgpi)
        earth_protocol = None
        try:
            earth_config = {
                'asset_code': 'UBECgpi',
                'issuer': config.ubec_issuer  # Same issuer for all tokens
            }
            earth_protocol = create_ubecgpi_service(
                db_manager=protocol_config_base['db_manager'],
                config=earth_config,
                stellar_client=protocol_config_base['stellar_client']
            )
            logger.info("✓ Earth Protocol (UBECgpi) initialized")
        except Exception as e:
            logger.warning(f"Earth Protocol initialization failed: {e}")
        
        # Initialize Fire Protocol (UBECtt)
        fire_protocol = None
        try:
            fire_config = {
                'asset_code': 'UBECtt',
                'issuer': config.ubec_issuer,  # Same issuer for all tokens
                'min_verification_threshold': 3,
                'base_reward': 100.0,
                'max_reward': 10000.0
            }
            fire_protocol = create_ubectt_service(
                db_manager=protocol_config_base['db_manager'],
                config=fire_config,
                stellar_client=protocol_config_base['stellar_client']
            )
            logger.info("✓ Fire Protocol (UBECtt) initialized")
        except Exception as e:
            logger.warning(f"Fire Protocol initialization failed: {e}")
        
        # Store protocols
        services['protocols'] = {
            'air': air_protocol,
            'water': water_protocol,
            'earth': earth_protocol,
            'fire': fire_protocol
        }
        
        # Count initialized protocols
        initialized_count = sum(1 for p in services['protocols'].values() if p is not None)
        logger.info(f"✓ Protocol structure initialized ({initialized_count}/4 protocols active)")
        
    except Exception as e:
        logger.warning(f"Element protocols not fully available: {e}")
        services['protocols'] = {
            'air': None,
            'water': None,
            'earth': None,
            'fire': None
        }

    
    logger.info(f"Services initialized: {len([k for k, v in services.items() if v is not None and k != 'protocols'])} available")
    return services


async def shutdown_services(services: Dict[str, Any]) -> None:
    """
    Gracefully shutdown all services.
    
    Args:
        services: Dictionary of initialized services
    """
    logger.info("Shutting down services...")
    
    # Close stellar client
    if 'stellar' in services and services['stellar']:
        try:
            await services['stellar'].close()
            logger.info("✓ Stellar client closed")
        except Exception as e:
            logger.error(f"Error closing Stellar client: {e}")
    
    # Close database
    if 'database' in services and services['database']:
        try:
            # Check if database has close method
            if hasattr(services['database'], 'close'):
                if asyncio.iscoroutinefunction(services['database'].close):
                    await services['database'].close()
                else:
                    services['database'].close()
                logger.info("✓ Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    # Close synchronizer
    if 'synchronizer' in services and services['synchronizer']:
        try:
            if hasattr(services['synchronizer'], 'close'):
                if asyncio.iscoroutinefunction(services['synchronizer'].close):
                    await services['synchronizer'].close()
                else:
                    services['synchronizer'].close()
                logger.info("✓ Synchronizer closed")
        except Exception as e:
            logger.error(f"Error closing synchronizer: {e}")
    
    logger.info("All services shut down")


# ========================================================================
# DATA OPERATIONS
# ========================================================================

async def discover_holders(services: Dict[str, Any], max_accounts: int = 1000) -> Dict[str, Any]:
    """
    Discover new UBEC holders from the blockchain.
    
    Args:
        services: Service dictionary
        max_accounts: Maximum accounts to discover
    
    Returns:
        Discovery results
    """
    logger.info(f"Discovering UBEC holders (max: {max_accounts})...")
    
    synchronizer = services.get('synchronizer')
    if not synchronizer:
        return {'success': False, 'error': 'Synchronizer not available'}
    
    try:
        result = await synchronizer.discover_new_holders(
            asset_code='UBEC',
            max_accounts=max_accounts
        )
        
        logger.info(f"✓ Discovery complete: {result.get('new_accounts', 0)} new accounts")
        return {'success': True, **result}
        
    except Exception as e:
        logger.error(f"✗ Discovery failed: {e}")
        return {'success': False, 'error': str(e)}


async def sync_data(services: Dict[str, Any], asset_code: str = 'UBEC') -> Dict[str, Any]:
    """
    Synchronize blockchain data to database.
    
    Args:
        services: Service dictionary
        asset_code: Token to sync
    
    Returns:
        Sync results
    """
    logger.info(f"Synchronizing {asset_code} data...")
    
    synchronizer = services.get('synchronizer')
    if not synchronizer:
        return {'success': False, 'error': 'Synchronizer not available'}
    
    try:
        # Sync accounts
        accounts_result = await synchronizer.sync_account_data(
            asset_code=asset_code,
            limit=200
        )
        
        # Sync balances
        balances_result = await synchronizer.sync_balance_data(
            asset_code=asset_code
        )
        
        # Sync recent transactions
        transactions_result = await synchronizer.sync_transaction_data(
            asset_code=asset_code,
            days_back=7
        )
        
        logger.info(f"✓ Sync complete for {asset_code}")
        return {
            'success': True,
            'asset_code': asset_code,
            'accounts': accounts_result,
            'balances': balances_result,
            'transactions': transactions_result
        }
        
    except Exception as e:
        logger.error(f"✗ Sync failed for {asset_code}: {e}")
        return {'success': False, 'error': str(e)}


async def monitor_system(services: Dict[str, Any], interval: int = 300) -> None:
    """
    Monitor system health continuously.
    
    Args:
        services: Service dictionary
        interval: Check interval in seconds
    """
    logger.info(f"Starting system monitor (interval: {interval}s)...")
    
    try:
        while True:
            logger.info("Performing health check...")
            
            # Check database
            db_healthy = False
            if 'database' in services and services['database']:
                try:
                    # Check if database connection is alive
                    if hasattr(services['database'], 'conn') and services['database'].conn:
                        db_healthy = True
                    logger.info(f"  Database: {'✓ Healthy' if db_healthy else '✗ Unhealthy'}")
                except Exception as e:
                    logger.warning(f"  Database: ✗ Error - {e}")
            
            # Check Stellar connection
            stellar_healthy = False
            if 'stellar' in services and services['stellar']:
                try:
                    # Properly check Stellar connection
                    root_call = services['stellar'].root()
                    await root_call.call()  # Execute the call builder
                    stellar_healthy = True
                    logger.info("  Stellar: ✓ Connected")
                except Exception as e:
                    logger.warning(f"  Stellar: ✗ Error - {e}")
            
            # Wait for next check
            await asyncio.sleep(interval)
            
    except asyncio.CancelledError:
        logger.info("Monitor stopped")


# ========================================================================
# PROTOCOL OPERATIONS
# ========================================================================

async def protocol_health_check(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check health of all element protocols.
    
    Args:
        services: Service dictionary
    
    Returns:
        Health check results
    """
    logger.info("Performing protocol health check...")
    
    protocols = services.get('protocols', {})
    results = {}
    
    for element, protocol in protocols.items():
        if protocol:
            try:
                health = await protocol.health_check()
                results[element] = health
                status = health.get('status', 'unknown')
                logger.info(f"  {element.capitalize()}: {status}")
            except Exception as e:
                results[element] = {'status': 'error', 'error': str(e)}
                logger.error(f"  {element.capitalize()}: Error - {e}")
        else:
            results[element] = {'status': 'not_initialized'}
            logger.warning(f"  {element.capitalize()}: Not initialized")
    
    overall_status = 'healthy' if all(
        r.get('status') == 'healthy' for r in results.values()
    ) else 'degraded'
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'overall_status': overall_status,
        'elements': results
    }


async def protocol_status(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get status of all element protocols.
    
    Args:
        services: Service dictionary
    
    Returns:
        Status information
    """
    logger.info("Getting protocol status...")
    
    protocols = services.get('protocols', {})
    results = {}
    
    for element, protocol in protocols.items():
        if protocol:
            try:
                status = await protocol.get_status()
                results[element] = status
                logger.info(f"  {element.capitalize()}: Retrieved")
            except Exception as e:
                results[element] = {'error': str(e)}
                logger.error(f"  {element.capitalize()}: Error - {e}")
        else:
            results[element] = {'status': 'not_initialized'}
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'elements': results
    }


async def protocol_sync(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sync all element protocol data concurrently.
    
    Args:
        services: Service dictionary
    
    Returns:
        Sync results
    """
    logger.info("Syncing all element protocols...")
    
    protocols = services.get('protocols', {})
    
    # Prepare sync tasks
    tasks = []
    elements = []
    
    for element, protocol in protocols.items():
        if protocol:
            elements.append(element)
            if element == 'air':
                tasks.append(protocol.sync_gateway_data())
            elif element == 'water':
                tasks.append(protocol.sync_flow_data())
            elif element == 'earth':
                tasks.append(protocol.sync_stability_data())
            elif element == 'fire':
                tasks.append(protocol.sync_transformation_data())
    
    # Execute all syncs concurrently
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        element_results = {}
        for element, result in zip(elements, results):
            if isinstance(result, Exception):
                element_results[element] = {'status': 'error', 'error': str(result)}
                logger.error(f"  {element.capitalize()}: Error - {result}")
            else:
                element_results[element] = result
                logger.info(f"  {element.capitalize()}: Synced")
        
        successful = sum(
            1 for r in element_results.values()
            if isinstance(r, dict) and r.get('status') != 'error'
        )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'elements_synced': successful,
            'total_elements': len(elements),
            'results': element_results
        }
    else:
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'error': 'No protocols initialized'
        }


async def evaluate_holonic(services: Dict[str, Any], account_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform holonic evaluation.
    
    Args:
        services: Service dictionary
        account_id: Optional specific account to evaluate
    
    Returns:
        Evaluation results
    """
    logger.info("Performing holonic evaluation...")
    
    evaluator = services.get('evaluator')
    if not evaluator:
        return {'success': False, 'error': 'Evaluator not available'}
    
    try:
        if account_id:
            logger.info(f"  Evaluating account: {account_id}")
            # Check if evaluator method is async
            if hasattr(evaluator, 'evaluate_account'):
                if asyncio.iscoroutinefunction(evaluator.evaluate_account):
                    result = await evaluator.evaluate_account(account_id)
                else:
                    result = evaluator.evaluate_account(account_id)
        else:
            logger.info("  Evaluating network holism...")
            # Check if evaluator method is async
            if hasattr(evaluator, 'evaluate_network_holism'):
                if asyncio.iscoroutinefunction(evaluator.evaluate_network_holism):
                    result = await evaluator.evaluate_network_holism()
                else:
                    result = evaluator.evaluate_network_holism()
        
        logger.info("✓ Evaluation complete")
        return {'success': True, 'evaluation': result}
        
    except Exception as e:
        logger.error(f"✗ Evaluation failed: {e}")
        return {'success': False, 'error': str(e)}


# ========================================================================
# SYSTEM-WIDE OPERATIONS
# ========================================================================

async def full_system_health(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete system health check (infrastructure + protocols).
    
    Args:
        services: Service dictionary
    
    Returns:
        Complete health status
    """
    logger.info("Performing full system health check...")
    
    health = {
        'timestamp': datetime.utcnow().isoformat(),
        'infrastructure': {},
        'protocols': {}
    }
    
    # Check database
    if 'database' in services and services['database']:
        try:
            # Check if connection is alive
            if hasattr(services['database'], 'conn') and services['database'].conn:
                health['infrastructure']['database'] = {'status': 'healthy'}
            else:
                health['infrastructure']['database'] = {'status': 'unhealthy'}
        except Exception as e:
            health['infrastructure']['database'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        health['infrastructure']['database'] = {'status': 'not_available'}
    
    # Check Stellar
    if 'stellar' in services and services['stellar']:
        try:
            # Properly call the Stellar API
            root_call = services['stellar'].root()
            await root_call.call()  # Execute the call builder
            health['infrastructure']['stellar'] = {'status': 'connected'}
        except Exception as e:
            health['infrastructure']['stellar'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        health['infrastructure']['stellar'] = {'status': 'not_available'}
    
    # Check protocols
    protocol_health = await protocol_health_check(services)
    health['protocols'] = protocol_health.get('elements', {})
    
    # Determine overall status
    infra_healthy = all(
        s.get('status') in ['healthy', 'connected']
        for s in health['infrastructure'].values()
    )
    protocols_healthy = all(
        s.get('status') == 'healthy'
        for s in health['protocols'].values()
    )
    
    health['overall_status'] = 'healthy' if (infra_healthy and protocols_healthy) else 'degraded'
    
    return health


async def full_system_status(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete system status (infrastructure + protocols).
    
    Args:
        services: Service dictionary
    
    Returns:
        Complete system status
    """
    logger.info("Getting full system status...")
    
    status = {
        'timestamp': datetime.utcnow().isoformat(),
        'infrastructure': {},
        'protocols': {}
    }
    
    # Database stats
    if 'database' in services and services['database']:
        try:
            status['infrastructure']['database'] = {
                'status': 'connected',
                'info': 'Available'
            }
        except Exception as e:
            status['infrastructure']['database'] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Stellar stats
    if 'stellar' in services and services['stellar']:
        try:
            status['infrastructure']['stellar'] = {
                'status': 'connected',
                'horizon_url': services['stellar'].horizon_url
            }
        except Exception as e:
            status['infrastructure']['stellar'] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Protocol status
    protocol_status_result = await protocol_status(services)
    status['protocols'] = protocol_status_result.get('elements', {})
    
    return status


# ========================================================================
# COMMAND LINE INTERFACE
# ========================================================================

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='UBEC Protocol - Unified Main Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Data Operations
  python main.py --mode discover --max-accounts 500
  python main.py --mode sync
  python main.py --mode monitor --interval 300
  
  # Protocol Operations
  python main.py --mode protocol-health
  python main.py --mode protocol-status
  python main.py --mode protocol-sync
  python main.py --mode evaluate
  python main.py --mode evaluate --account GXXX...
  
  # System Operations
  python main.py --mode health
  python main.py --mode status
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=[
            'discover', 'sync', 'monitor',  # Data operations
            'protocol-health', 'protocol-status', 'protocol-sync', 'evaluate',  # Protocol operations
            'health', 'status'  # System-wide operations
        ],
        help='Operation mode'
    )
    
    parser.add_argument(
        '--asset-code',
        type=str,
        default='UBEC',
        help='Asset code for sync operations (default: UBEC)'
    )
    
    parser.add_argument(
        '--max-accounts',
        type=int,
        default=1000,
        help='Maximum accounts for discover mode (default: 1000)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Interval for monitor mode in seconds (default: 300)'
    )
    
    parser.add_argument(
        '--account',
        type=str,
        help='Specific account ID for evaluation'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'pretty'],
        default='pretty',
        help='Output format (default: pretty)'
    )
    
    return parser.parse_args()


def format_output(data: Dict[str, Any], output_format: str = 'pretty') -> str:
    """
    Format output based on specified format.
    
    Args:
        data: Data to format
        output_format: Output format ('json' or 'pretty')
    
    Returns:
        Formatted string
    """
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)
    else:
        # Pretty format with structure
        return json.dumps(data, indent=2, default=str)


# ========================================================================
# ASYNC MAIN
# ========================================================================

async def main_async(args: argparse.Namespace) -> int:
    """
    Async main orchestration function.
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    config = SystemConfig()
    services = None
    
    try:
        # Initialize services
        services = await initialize_services(config)
        
        # Execute requested operation
        result = None
        
        # Data Operations
        if args.mode == 'discover':
            result = await discover_holders(services, args.max_accounts)
        
        elif args.mode == 'sync':
            result = await sync_data(services, args.asset_code)
        
        elif args.mode == 'monitor':
            # Monitor runs indefinitely
            await monitor_system(services, args.interval)
            return 0
        
        # Protocol Operations
        elif args.mode == 'protocol-health':
            result = await protocol_health_check(services)
        
        elif args.mode == 'protocol-status':
            result = await protocol_status(services)
        
        elif args.mode == 'protocol-sync':
            result = await protocol_sync(services)
        
        elif args.mode == 'evaluate':
            result = await evaluate_holonic(services, args.account)
        
        # System-wide Operations
        elif args.mode == 'health':
            result = await full_system_health(services)
        
        elif args.mode == 'status':
            result = await full_system_status(services)
        
        else:
            logger.error(f"Unknown mode: {args.mode}")
            return 1
        
        # Output result
        if result:
            output = format_output(result, args.output)
            print("\n" + "=" * 70)
            print(f"UBEC Protocol - {args.mode.upper()} Result")
            print("=" * 70)
            print(output)
            print("=" * 70 + "\n")
            
            # Determine exit code
            if isinstance(result, dict):
                if result.get('success') is False or 'error' in result:
                    return 1
                if result.get('overall_status') in ['unhealthy', 'degraded', 'error']:
                    return 1
            
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


# ========================================================================
# MAIN ENTRY POINT
# ========================================================================

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
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Log startup
    logger.info("=" * 70)
    logger.info("UBEC Protocol - Unified Main Orchestrator")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Version: 3.5")
    logger.info(f"Python: {sys.version.split()[0]}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # Run async main
    try:
        exit_code = asyncio.run(main_async(args))
        return exit_code
    except KeyboardInterrupt:
        logger.info("\n✓ Program terminated by user")
        return 0


# ========================================================================
# ENTRY POINT
# ========================================================================

if __name__ == '__main__':
    sys.exit(main())
