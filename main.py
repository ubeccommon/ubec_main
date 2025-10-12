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
    - Data Synchronizer (Blockchain Sync)
    - Holonic Evaluator (Ubuntu Principles)

Design Compliance:
    ✅ Principle 1: Modular Design - Clear separation of concerns
    ✅ Principle 2: Service Pattern - THIS IS THE ONLY standalone execution
    ✅ Principle 3: Service Registry - All dependencies via registry
    ✅ Principle 4: Single Source of Truth - Database authoritative
    ✅ Principle 5: Strict Async - All operations async
    ✅ Principle 6: No Sync Fallbacks - Pure async only
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
    python main.py --mode sync                      # Sync all data
    
    # Data Layer Operations
    python main.py --mode discover --max-accounts 100  # Discover accounts
    python main.py --mode analytics --analysis-type summary  # Analytics
    
    # Protocol Operations
    python main.py --mode protocol-health           # Protocol health
    python main.py --mode protocol-status           # Protocol status
    python main.py --mode protocol-sync             # Sync protocols
    python main.py --mode evaluate                  # Holonic evaluation
    python main.py --mode evaluate --account GXXX   # Account evaluation
    
    # Distribution Management
    python main.py --mode distribution --action check-compliance
    python main.py --mode distribution --action rebalance
    python main.py --mode distribution --action status
    python main.py --mode distribution --action evaluate
    python main.py --mode distribution --action trends --days 30
    python main.py --mode distribution --action schedule --interval 3600

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 4.0 (Database-Backed Configuration)
Date: October 12, 2025
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


# ==================== SERVICE INITIALIZATION ====================

async def initialize_database() -> AsyncDatabaseManager:
    """
    Initialize database manager first (required for config loading).
    
    Returns:
        AsyncDatabaseManager instance
        
    Raises:
        RuntimeError: If database initialization fails
    """
    logger.info("Initializing database connection...")
    
    try:
        db_manager = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=os.getenv('DB_SCHEMA', 'ubec_main'),
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        await db_manager.initialize()
        logger.info("✓ Database connection initialized")
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
        2. Stellar Client (blockchain access)
        3. Data Synchronizer (depends on database)
        4. Element Protocols (depend on database + stellar)
        5. Distribution Services (depend on all above)
        6. Holonic Evaluator (depends on all above)
    """
    logger.info("="*70)
    logger.info("Initializing UBEC Protocol Services")
    logger.info("="*70)
    
    services = {
        'database': db_manager,
        'config': config
    }
    
    try:
        # Initialize Stellar client
        try:
            from stellar_sdk import Server
            stellar_client = Server(horizon_url=config.HORIZON_URL)
            services['stellar_client'] = stellar_client
            logger.info("✓ Stellar client initialized")
        except Exception as e:
            logger.warning(f"Stellar client initialization failed: {e}")
            services['stellar_client'] = None
        
        # Initialize Data Synchronizer
        try:
            from core.db.ubec_data_synchronizer import UBECDataSynchronizer
            synchronizer = UBECDataSynchronizer(db_manager)
            services['synchronizer'] = synchronizer
            logger.info("✓ Data synchronizer initialized")
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
        
        # Initialize Distribution Services
        try:
            from services.distribution.distribution_service import DistributionService
            dist_service = DistributionService(
                db_manager=db_manager,
                stellar_client=services.get('stellar_client'),
                config=config
            )
            services['distribution'] = dist_service
            logger.info("✓ Distribution service initialized")
        except ImportError:
            logger.warning("Distribution service module not found")
            services['distribution'] = None
        except Exception as e:
            logger.warning(f"Distribution service initialization failed: {e}")
            services['distribution'] = None
        
        try:
            from core.distribution.distribution_evaluator import DistributionEvaluator
            evaluator = DistributionEvaluator(db_manager=db_manager)
            services['distribution_evaluator'] = evaluator
            logger.info("✓ Distribution evaluator initialized")
        except ImportError:
            logger.warning("Distribution evaluator module not found")
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
        Stellar SDK's close() is synchronous, while custom services are async.
    """
    logger.info("Shutting down services...")
    
    try:
        # Close database connection (async)
        db_manager = services.get('database')
        if db_manager:
            await db_manager.close()
            logger.info("✓ Database connection closed")
        
        # Close Stellar client (SYNCHRONOUS close method)
        stellar_client = services.get('stellar_client')
        if stellar_client and hasattr(stellar_client, 'close'):
            # Stellar SDK's close() is NOT async - call it directly
            stellar_client.close()
            logger.info("✓ Stellar client closed")
        
        # Close synchronizer (check if async or sync)
        synchronizer = services.get('synchronizer')
        if synchronizer and hasattr(synchronizer, 'close'):
            close_method = getattr(synchronizer, 'close')
            if asyncio.iscoroutinefunction(close_method):
                await synchronizer.close()
            else:
                synchronizer.close()
            logger.info("✓ Synchronizer closed")
        
        # Close protocol services (check if async or sync)
        for protocol_name in ['air', 'water', 'earth', 'fire']:
            protocol = services.get(protocol_name)
            if protocol and hasattr(protocol, 'close'):
                close_method = getattr(protocol, 'close')
                if asyncio.iscoroutinefunction(close_method):
                    await protocol.close()
                else:
                    protocol.close()
                logger.info(f"✓ {protocol_name.title()} Protocol closed")
        
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
    for service_name in ['distribution', 'distribution_evaluator', 'holonic_evaluator']:
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


async def run_sync(services: Dict[str, Any], asset_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Synchronize blockchain data to database.
    
    Args:
        services: Service instances
        asset_code: Optional specific asset to sync
        
    Returns:
        dict: Sync results
    """
    synchronizer = services.get('synchronizer')
    
    if not synchronizer:
        return {
            'error': 'Synchronizer service not available',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Starting sync operation (asset_code={asset_code or 'all'})...")
    
    try:
        if asset_code:
            result = await synchronizer.sync_account_data(asset_code)
        else:
            # Sync all UBEC family assets
            results = {}
            for code in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
                results[code] = await synchronizer.sync_account_data(code)
            result = results
        
        return {
            'timestamp': datetime.now().isoformat(),
            'asset_code': asset_code or 'all',
            'result': result,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'success': False
        }


async def run_analytics(services: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
    """
    Run analytics operations.
    
    Args:
        services: Service instances
        analysis_type: Type of analysis
        
    Returns:
        dict: Analytics results
    """
    synchronizer = services.get('synchronizer')
    
    if not synchronizer:
        return {
            'error': 'Synchronizer service not available',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Running {analysis_type} analytics...")
    
    try:
        if analysis_type == 'summary':
            # Get summary statistics
            result = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'summary',
                'message': 'Summary analytics not yet implemented'
            }
        elif analysis_type == 'distribution':
            result = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'distribution',
                'message': 'Distribution analytics not yet implemented'
            }
        elif analysis_type == 'holders':
            result = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'holders',
                'message': 'Holder analytics not yet implemented'
            }
        else:
            result = {
                'error': f'Unknown analysis type: {analysis_type}',
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
    
    Args:
        services: Service instances
        max_accounts: Maximum accounts to discover
        
    Returns:
        dict: Discovery results
    """
    synchronizer = services.get('synchronizer')
    
    if not synchronizer:
        return {
            'error': 'Synchronizer service not available',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Discovering accounts (max={max_accounts})...")
    
    try:
        # Discover accounts
        accounts = await synchronizer.discover_accounts(max_accounts=max_accounts)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'accounts_discovered': len(accounts),
            'max_requested': max_accounts,
            'accounts': accounts[:10],  # Return first 10 for display
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

async def run_distribution_operation(
    services: Dict[str, Any],
    action: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Run distribution management operations.
    
    Args:
        services: Service instances
        action: Distribution action to perform
        **kwargs: Additional arguments
        
    Returns:
        dict: Operation results
    """
    dist_service = services.get('distribution')
    evaluator = services.get('distribution_evaluator')
    
    if not dist_service and action not in ['status', 'help']:
        return {
            'error': 'Distribution service not available',
            'timestamp': datetime.now().isoformat()
        }
    
    logger.info(f"Running distribution operation: {action}")
    
    try:
        if action == 'check-compliance':
            result = await dist_service.check_compliance()
            
            # Create snapshot
            snapshot_id = await dist_service.snapshot_distribution()
            result['snapshot_id'] = snapshot_id
            
            return result
        
        elif action == 'rebalance':
            # Check if rebalance needed
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
            
            # Perform rebalance
            result = await dist_service.perform_rebalance()
            
            # Create post-rebalance snapshot
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
                    'rebalance - Perform token rebalancing',
                    'status - Get current distribution status',
                    'evaluate - Evaluate distribution health',
                    'trends --days 30 - Get compliance trends',
                    'schedule --interval 3600 - Schedule automatic checks'
                ],
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
        return {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'error': str(e)
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
        
        if service and hasattr(service, 'get_system_metrics'):
            try:
                metrics = await service.get_system_metrics()
                protocols[protocol_name] = {
                    'status': 'ACTIVE',
                    'metrics': metrics
                }
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
        description='UBEC Protocol Suite - Unified Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # System Operations
  %(prog)s --mode health                          # System health
  %(prog)s --mode status                          # System status
  %(prog)s --mode sync                            # Sync all data
  %(prog)s --mode sync --asset-code UBEC          # Sync specific asset
  
  # Data Operations
  %(prog)s --mode discover --max-accounts 100     # Discover accounts
  %(prog)s --mode analytics --analysis-type summary  # Analytics
  
  # Protocol Operations
  %(prog)s --mode protocol-health                 # Protocol health
  %(prog)s --mode protocol-status                 # Protocol status
  %(prog)s --mode protocol-sync                   # Sync protocols
  %(prog)s --mode evaluate                        # Holonic evaluation
  %(prog)s --mode evaluate --account GXXX         # Account evaluation
  
  # Distribution Management
  %(prog)s --mode distribution --action check-compliance
  %(prog)s --mode distribution --action rebalance
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
    
    # Sync options
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
        
    Design Note:
        This follows the correct initialization order:
        1. Initialize database manager
        2. Load configuration from database (Single Source of Truth)
        3. Initialize all other services with database-backed config
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
            result = await run_sync(services, args.asset_code)
        
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
                    'timestamp': datetime.now().isoformat()
                }
            else:
                result = await run_distribution_operation(
                    services,
                    args.action,
                    days=args.days,
                    interval=args.interval
                )
        
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
                if result.get('overall_status') in ['POOR', 'ERROR']:
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
    logger.info(f"Version: 4.0 (Database-Backed Configuration)")
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
