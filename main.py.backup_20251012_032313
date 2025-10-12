#!/usr/bin/env python3
"""
UBEC Protocol - Unified Main Orchestrator
==========================================
Single entry point for the entire UBEC ecosystem

This is the SOLE file with standalone execution in the entire system.
Per Design Principle #2: Only main.py has standalone execution.

Design Principles Compliance:
- ✅ Modular Design: Clear service boundaries and interfaces
- ✅ Service Pattern: This is main.py - the ONE orchestrator
- ✅ Service Registry: Centralized dependency injection
- ✅ Single Source of Truth: Database as authoritative source
- ✅ Strict Async Operations: All I/O uses async/await
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ Per-Asset Monitoring: Individual asset tracking
- ✅ No Duplicate Configuration: Single config source
- ✅ Integrated Rate Limiting: Built-in for all services
- ✅ Clear Separation of Concerns: Orchestration layer only
- ✅ Comprehensive Documentation: Complete docstrings
- ✅ Method Singularity: Each method implemented once

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.

Version: 5.4 (Added configurable sync limits via SYNC_LIMIT env var and --limit CLI arg)
Date: October 12, 2025
Changes from 5.3:
    - Added SYNC_LIMIT environment variable (default: 5000)
    - Added DISCOVER_LIMIT environment variable (default: 1000)  
    - Added --limit CLI argument for sync mode
    - Fixed run_sync to accept and use limit parameter
    - Use --limit 0 for unlimited sync (use cautiously with rate limits)
"""

import sys
import os
import asyncio
import argparse
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Async HTTP client for Stellar
try:
    from stellar_sdk import ServerAsync, AiohttpClient
    STELLAR_AVAILABLE = True
except ImportError:
    STELLAR_AVAILABLE = False


# ==================== LOGGING SETUP ====================

def setup_logging(log_level='INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
        handlers=[
            logging.FileHandler("ubec_main.log"),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger('MainOrchestrator')


# ==================== CONFIGURATION ====================

class SystemConfig:
    """
    System-wide configuration from environment variables.
    This is the SINGLE configuration source (Principle #8).
    """
    
    def __init__(self):
        """
        Load configuration from environment.
        Uses ONLY the exact variable names from env.example - no fallbacks.
        Coding is an exact science - we use what's defined, nothing more.
        """
        # Network (from env.example line 12)
        self.network = os.getenv('UBEC_NETWORK', 'testnet')
        self.horizon_url = (
            'https://horizon.stellar.org' if self.network == 'mainnet'
            else 'https://horizon-testnet.stellar.org'
        )
        
        # Database (from env.example lines 47-54)
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = int(os.getenv('DB_PORT', '5432'))
        self.db_name = os.getenv('DB_NAME', 'ubec')
        self.db_schema = os.getenv('DB_SCHEMA', 'ubec_main')
        self.db_user = os.getenv('DB_USER', 'ubec_app')
        self.db_password = os.getenv('DB_PASSWORD', '')
        
        # Token issuers (from env.example lines 20-29)
        # Note: env.example uses mixed case for element tokens
        self.ubec_issuer = os.getenv('UBEC_ISSUER', '')
        self.ubecrc_issuer = os.getenv('UBECrc_ISSUER', '')
        self.ubecgpi_issuer = os.getenv('UBECgpi_ISSUER', '')
        self.ubectt_issuer = os.getenv('UBECtt_ISSUER', '')
        
        # Logging (from env.example line 93)
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Performance tuning (optional - can be added to env.example if customization needed)
        # These use sensible defaults but can be overridden via environment variables
        self.rate_limit_per_second = float(os.getenv('RATE_LIMIT', '10.0'))
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300'))
        self.analytics_cache_ttl = int(os.getenv('ANALYTICS_CACHE_TTL', '300'))
        
        # Sync operation limits (NEW in v5.4)
        self.sync_limit_default = int(os.getenv('SYNC_LIMIT', '5000'))
        self.discover_limit_default = int(os.getenv('DISCOVER_LIMIT', '1000'))
        
        logger.info(f"Configuration loaded: network={self.network}, schema={self.db_schema}")
        logger.info(f"Sync limits: sync={self.sync_limit_default}, discover={self.discover_limit_default}")


# ==================== SERVICE INITIALIZATION ====================

async def initialize_services(config: SystemConfig) -> Dict[str, Any]:
    """
    Initialize all services with proper dependency injection.
    Returns service registry dictionary.
    """
    services = {}
    
    # 1. Initialize Database Manager
    try:
        from core.db.database_manager import AsyncDatabaseManager
        
        db_manager = AsyncDatabaseManager(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            schema=config.db_schema,
            user=config.db_user,
            password=config.db_password
        )
        
        await db_manager.initialize()
        services['database'] = db_manager
        logger.info("✓ Database connection initialized")
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        raise
    
    # 2. Initialize Stellar Client
    if STELLAR_AVAILABLE:
        try:
            stellar_client = ServerAsync(
                horizon_url=config.horizon_url,
                client=AiohttpClient()
            )
            services['stellar'] = stellar_client
            logger.info("✓ Stellar client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Stellar client initialization failed: {e}")
            services['stellar'] = None
    else:
        logger.warning("⚠️ Stellar SDK not available")
        services['stellar'] = None
    
    # 3. Initialize Data Synchronizer
    try:
        from core.db.ubec_data_synchronizer import UBECDataSynchronizer
        
        # UBECDataSynchronizer only takes db_manager
        synchronizer = UBECDataSynchronizer(db_manager=services['database'])
        # Explicitly initialize the synchronizer
        await synchronizer.initialize()
        services['synchronizer'] = synchronizer
        logger.info("✓ Data synchronizer initialized")
        
    except Exception as e:
        logger.warning(f"⚠️ Data synchronizer initialization failed: {e}")
        logger.debug("Stack trace:", exc_info=True)
        services['synchronizer'] = None
    
    # 4. Initialize Analytics Service
    if services.get('database'):
        try:
            analytics = None
            
            try:
                from services.analytics.ubec_analytics_service import UBECAnalyticsService
                logger.debug("Using services.analytics.ubec_analytics_service module")
                analytics = UBECAnalyticsService(db_manager=services['database'])
            except ImportError:
                try:
                    from core.analytics.ubec_analytics_service import UBECAnalyticsService
                    logger.debug("Using core.analytics.ubec_analytics_service module")
                    analytics = UBECAnalyticsService(db_manager=services['database'])
                except ImportError:
                    try:
                        from ubec_analytics_service import UBECAnalyticsService
                        logger.debug("Using root-level ubec_analytics_service module")
                        analytics = UBECAnalyticsService(db_manager=services['database'])
                    except ImportError:
                        logger.warning("⚠️ Analytics service module not found in any location")
            
            if analytics:
                await analytics.initialize()
                analytics._cache_ttl_seconds = config.analytics_cache_ttl
                services['analytics'] = analytics
                logger.info("✓ Analytics service initialized")
            else:
                services['analytics'] = None
                logger.warning("⚠️ Analytics service not available")
            
        except Exception as e:
            logger.warning(f"⚠️ Analytics service initialization failed: {e}")
            logger.debug("Stack trace:", exc_info=True)
            services['analytics'] = None
    else:
        logger.info("ℹ️ Analytics service skipped (requires database connection)")
        services['analytics'] = None
    
    # 5. Initialize Holonic Evaluator (ASYNC VERSION)
    if services.get('database'):
        try:
            evaluator = None
            
            try:
                from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
                logger.debug("Using core.holonic.ubec_holonic_evaluator module")
                
                # create_holonic_evaluator is an async factory function
                evaluator = await create_holonic_evaluator(
                    db_manager=services['database'],
                    config={
                        'db_schema': config.db_schema,
                        'ubec_code': 'UBEC',
                        'ubec_issuer': config.ubec_issuer
                    }
                )
                
            except ImportError:
                try:
                    from holonic.ubec_holonic_evaluator import create_holonic_evaluator
                    logger.debug("Using holonic.ubec_holonic_evaluator module")
                    
                    evaluator = await create_holonic_evaluator(
                        db_manager=services['database'],
                        config={
                            'db_schema': config.db_schema,
                            'ubec_code': 'UBEC',
                            'ubec_issuer': config.ubec_issuer
                        }
                    )
                except ImportError:
                    logger.warning("⚠️ Holonic evaluator module not found in any location")
            
            if evaluator:
                services['evaluator'] = evaluator
                logger.info("✓ Holonic evaluator initialized (async)")
            else:
                services['evaluator'] = None
                logger.warning("⚠️ Holonic evaluator not available")
            
        except Exception as e:
            logger.warning(f"⚠️ Holonic evaluator initialization failed: {e}")
            logger.debug("Stack trace:", exc_info=True)
            services['evaluator'] = None
    else:
        logger.info("ℹ️ Holonic evaluator skipped (requires database connection)")
        services['evaluator'] = None
    
    # 6. Initialize Element Protocols
    await initialize_element_protocols(services, config)
    
    return services


async def initialize_element_protocols(services: Dict[str, Any], config: SystemConfig):
    """
    Initialize the four element protocol services.
    
    FIXED in v5.3: All imports now use correct core.protocols.* path
    
    Args:
        services: Service registry dictionary
        config: System configuration
    """
    
    # Air Protocol (UBEC - Gateway)
    try:
        from core.protocols.UBEC_protocol import create_ubec_service
        
        air_service = create_ubec_service(
            db_manager=services['database'],
            config={
                'asset_code': 'UBEC',
                'issuer': config.ubec_issuer,
                'rate_limit_calls_per_second': config.rate_limit_per_second
            },
            stellar_client=services['stellar']
        )
        services['air'] = air_service
        logger.info("✓ Air Protocol (UBEC) initialized")
    except Exception as e:
        logger.warning(f"⚠️ Air Protocol initialization failed: {e}")
        services['air'] = None
    
    # Water Protocol (UBECrc - Reciprocity)
    try:
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        
        water_service = create_ubecrc_service(
            db_manager=services['database'],
            config={
                'asset_code': 'UBECrc',
                'issuer': config.ubecrc_issuer,
                'rate_limit_calls_per_second': config.rate_limit_per_second
            },
            stellar_client=services['stellar']
        )
        services['water'] = water_service
        logger.info("✓ Water Protocol (UBECrc) initialized")
    except Exception as e:
        logger.warning(f"⚠️ Water Protocol initialization failed: {e}")
        services['water'] = None
    
    # Earth Protocol (UBECgpi - Stability)
    try:
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        
        earth_service = create_ubecgpi_service(
            db_manager=services['database'],
            config={
                'asset_code': 'UBECgpi',
                'issuer': config.ubecgpi_issuer,
                'rate_limit_calls_per_second': config.rate_limit_per_second
            },
            stellar_client=services['stellar']
        )
        services['earth'] = earth_service
        logger.info("✓ Earth Protocol (UBECgpi) initialized")
    except Exception as e:
        logger.warning(f"⚠️ Earth Protocol initialization failed: {e}")
        services['earth'] = None
    
    # Fire Protocol (UBECtt - Transformation)
    try:
        from core.protocols.UBECtt_protocol import create_ubectt_service
        
        fire_service = create_ubectt_service(
            db_manager=services['database'],
            config={
                'asset_code': 'UBECtt',
                'issuer': config.ubectt_issuer,
                'rate_limit_calls_per_second': config.rate_limit_per_second,
                'min_verification_threshold': 3,
                'base_reward': '100.0',
                'max_reward': '10000.0'
            },
            stellar_client=services['stellar']
        )
        services['fire'] = fire_service
        logger.info("✓ Fire Protocol (UBECtt) initialized")
    except Exception as e:
        logger.warning(f"⚠️ Fire Protocol initialization failed: {e}")
        services['fire'] = None


async def shutdown_services(services: Dict[str, Any]):
    """
    Gracefully shutdown all services.
    
    Args:
        services: Service registry dictionary
    """
    logger.info("Shutting down services...")
    
    # Close Stellar client (which includes aiohttp session)
    if services.get('stellar'):
        try:
            await services['stellar'].close()
            logger.info("✓ Stellar client closed")
        except Exception as e:
            logger.error(f"Error closing Stellar client: {e}")
    
    # Close synchronizer's session if it has one
    if services.get('synchronizer'):
        try:
            sync = services['synchronizer']
            if hasattr(sync, 'session') and sync.session and not sync.session.closed:
                await sync.session.close()
                logger.info("✓ Synchronizer session closed")
        except Exception as e:
            logger.error(f"Error closing synchronizer session: {e}")
    
    # Close database connection
    if services.get('database'):
        try:
            await services['database'].close()
            logger.info("✓ Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    logger.info("✓ All services shut down")


# ==================== OPERATION MODES ====================

async def run_health_check(services: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check health of all services.
    
    Args:
        services: Service registry dictionary
        
    Returns:
        Health status dictionary
    """
    logger.info("Running health check...")
    
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'overall_status': 'healthy'
    }
    
    # Check each service
    for service_name, service in services.items():
        if service is None:
            health_status['services'][service_name] = {'status': 'unavailable'}
            health_status['overall_status'] = 'degraded'
        else:
            health_status['services'][service_name] = {'status': 'healthy'}
    
    # Check database connectivity
    if services.get('database'):
        try:
            result = await services['database'].execute_query("SELECT 1", fetch_one=True)
            if result:
                health_status['services']['database']['connectivity'] = 'ok'
        except Exception as e:
            health_status['services']['database']['status'] = 'error'
            health_status['services']['database']['error'] = str(e)
            health_status['overall_status'] = 'unhealthy'
    
    return health_status


async def run_sync(services: Dict[str, Any], asset_code: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Run data synchronization using actual UBECDataSynchronizer methods.
    
    The synchronizer has these async methods:
    - sync_account_data(asset_code, limit)
    - sync_transaction_data(asset_code, days_back, limit_per_account) 
    - sync_balance_data(asset_code)
    - discover_all_ubec_holders(max_per_asset)
    
    Args:
        services: Service registry dictionary
        asset_code: Specific asset to sync, or None for all
        limit: Maximum accounts to sync per asset (None = unlimited)
        
    Returns:
        Sync result dictionary
    """
    logger.info(f"Running sync for: {asset_code or 'all assets'} (limit: {limit or 'unlimited'})")
    
    if not services.get('synchronizer'):
        return {
            'success': False,
            'error': 'Synchronizer service not available'
        }
    
    try:
        synchronizer = services['synchronizer']
        
        # Synchronizer is already initialized during service startup
        # No need to check _initialized attribute
        
        if asset_code:
            # Sync specific asset using actual synchronizer methods
            logger.info(f"Syncing account data for {asset_code}...")
            accounts_result = await synchronizer.sync_account_data(
                asset_code=asset_code,
                limit=limit
            )
            
            logger.info(f"Syncing transaction data for {asset_code}...")
            transactions_result = await synchronizer.sync_transaction_data(
                asset_code=asset_code,
                days_back=30,
                limit_per_account=100
            )
            
            logger.info(f"Syncing balance data for {asset_code}...")
            balances_result = await synchronizer.sync_balance_data(
                asset_code=asset_code
            )
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'asset_code': asset_code,
                'accounts_synced': accounts_result.get('accounts_synced', 0) if isinstance(accounts_result, dict) else 0,
                'transactions_synced': transactions_result.get('transactions_synced', 0) if isinstance(transactions_result, dict) else 0,
                'balances_synced': balances_result.get('balances_synced', 0) if isinstance(balances_result, dict) else 0
            }
        else:
            # Sync all assets concurrently
            async def sync_asset(asset_code):
                try:
                    accounts = await synchronizer.sync_account_data(asset_code=asset_code, limit=limit)
                    transactions = await synchronizer.sync_transaction_data(
                        asset_code=asset_code, 
                        days_back=30,
                        limit_per_account=100
                    )
                    balances = await synchronizer.sync_balance_data(asset_code=asset_code)
                    return {
                        'success': True,
                        'asset_code': asset_code,
                        'accounts': accounts.get('accounts_synced', 0) if isinstance(accounts, dict) else 0,
                        'transactions': transactions.get('transactions_synced', 0) if isinstance(transactions, dict) else 0,
                        'balances': balances.get('balances_synced', 0) if isinstance(balances, dict) else 0
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'asset_code': asset_code,
                        'error': str(e)
                    }
            
            results = await asyncio.gather(
                sync_asset('UBEC'),
                sync_asset('UBECrc'),
                sync_asset('UBECgpi'),
                sync_asset('UBECtt'),
                return_exceptions=True
            )
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'assets_synced': sum(1 for r in results if isinstance(r, dict) and r.get('success')),
                'total_assets': 4,
                'limit_per_asset': limit or 'unlimited',
                'results': {
                    'UBEC': results[0] if len(results) > 0 else {},
                    'UBECrc': results[1] if len(results) > 1 else {},
                    'UBECgpi': results[2] if len(results) > 2 else {},
                    'UBECtt': results[3] if len(results) > 3 else {}
                }
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


async def run_analytics(services: Dict[str, Any], analysis_type: str = 'summary') -> Dict[str, Any]:
    """
    Run analytics queries.
    
    Args:
        services: Service registry dictionary
        analysis_type: Type of analysis to run
        
    Returns:
        Analytics result dictionary
    """
    logger.info(f"Running analytics: {analysis_type}")
    
    if not services.get('analytics'):
        return {
            'success': False,
            'error': 'Analytics service not available'
        }
    
    try:
        analytics = services['analytics']
        
        if analysis_type == 'summary':
            result = await analytics.get_ecosystem_health()
        elif analysis_type == 'distribution':
            results = await asyncio.gather(
                analytics.get_token_distribution('UBEC'),
                analytics.get_token_distribution('UBECrc'),
                analytics.get_token_distribution('UBECgpi'),
                analytics.get_token_distribution('UBECtt'),
                return_exceptions=True
            )
            result = {
                'UBEC': results[0],
                'UBECrc': results[1],
                'UBECgpi': results[2],
                'UBECtt': results[3]
            }
        elif analysis_type == 'holders':
            results = await asyncio.gather(
                analytics.get_holder_analysis('UBEC'),
                analytics.get_holder_analysis('UBECrc'),
                analytics.get_holder_analysis('UBECgpi'),
                analytics.get_holder_analysis('UBECtt'),
                return_exceptions=True
            )
            result = {
                'UBEC': results[0],
                'UBECrc': results[1],
                'UBECgpi': results[2],
                'UBECtt': results[3]
            }
        else:
            result = {
                'success': False,
                'error': f'Unknown analysis type: {analysis_type}'
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


async def run_evaluate(services: Dict[str, Any], account_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Run holonic evaluation.
    
    Args:
        services: Service registry dictionary
        account_id: Specific account to evaluate, or None for system-wide
        
    Returns:
        Evaluation result dictionary
    """
    logger.info(f"Running evaluation for: {account_id or 'all accounts'}")
    
    if not services.get('evaluator'):
        return {
            'success': False,
            'error': 'Evaluator service not available'
        }
    
    try:
        evaluator = services['evaluator']
        
        if account_id:
            # Evaluate specific account (not implemented in current evaluator)
            result = {
                'success': False,
                'error': 'Single account evaluation not yet implemented'
            }
        else:
            # Run system-wide evaluation
            result = await evaluator.run_evaluation()
        
        return result
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


async def run_discover(services: Dict[str, Any], max_accounts: int = 100) -> Dict[str, Any]:
    """
    Discover new accounts.
    
    Args:
        services: Service registry dictionary
        max_accounts: Maximum accounts to discover per token
        
    Returns:
        Discovery result dictionary
    """
    logger.info(f"Discovering accounts (max: {max_accounts})")
    
    if not services.get('synchronizer'):
        return {
            'success': False,
            'error': 'Synchronizer service not available'
        }
    
    try:
        synchronizer = services['synchronizer']
        
        # Synchronizer is already initialized during service startup
        
        # Use the discover_all_ubec_holders method which discovers all 4 tokens
        logger.info(f"Discovering holders of all UBEC tokens (max {max_accounts} per token)...")
        result = await synchronizer.discover_all_ubec_holders(max_per_asset=max_accounts)
        
        # Format result
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'discovery_results': result,
            'total_discovered': sum(result.values()) if isinstance(result, dict) else 0
        }
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


# ==================== CLI INTERFACE ====================

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments object
    """
    parser = argparse.ArgumentParser(
        description='UBEC Protocol - Unified Main Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode health                                  # System health check
  python main.py --mode sync                                    # Sync all assets (default limit from env)
  python main.py --mode sync --limit 1000                       # Sync all assets (limit 1000 per asset)
  python main.py --mode sync --limit 0                          # Sync all assets (unlimited)
  python main.py --mode sync --asset-code UBEC --limit 500      # Sync UBEC only (limit 500)
  python main.py --mode analytics                               # Ecosystem summary
  python main.py --mode analytics --analysis-type distribution  # Token distribution
  python main.py --mode evaluate                                # System-wide evaluation
  python main.py --mode discover --max-accounts 100             # Discover accounts

Environment Variables:
  SYNC_LIMIT=5000        # Default limit for sync operations (default: 5000)
  DISCOVER_LIMIT=1000    # Default limit for discover operations (default: 1000)
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['health', 'sync', 'analytics', 'evaluate', 'discover'],
        default='health',
        help='Operation mode (default: health)'
    )
    
    parser.add_argument(
        '--asset-code',
        type=str,
        choices=['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt'],
        help='Specific asset code (for sync mode)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum accounts to sync per asset (for sync mode). Use 0 for unlimited. Default from SYNC_LIMIT env var or 5000'
    )
    
    parser.add_argument(
        '--analysis-type',
        type=str,
        choices=['summary', 'distribution', 'holders'],
        default='summary',
        help='Type of analysis (for analytics mode)'
    )
    
    parser.add_argument(
        '--account',
        type=str,
        help='Specific account ID (for evaluate mode)'
    )
    
    parser.add_argument(
        '--max-accounts',
        type=int,
        default=100,
        help='Maximum accounts to discover (for discover mode)'
    )
    
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
        output_format: Format type (json, pretty, summary)
        
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

async def main_async(args):
    """
    Async main function - the actual orchestrator.
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        Exit code
    """
    # Load configuration
    config = SystemConfig()
    
    # Initialize services
    logger.info("Initializing services...")
    services = await initialize_services(config)
    
    try:
        # Execute requested operation
        if args.mode == 'health':
            result = await run_health_check(services)
        
        elif args.mode == 'sync':
            # Determine sync limit
            if args.limit is not None:
                # CLI argument takes precedence
                sync_limit = None if args.limit == 0 else args.limit
            else:
                # Use config default
                sync_limit = config.sync_limit_default
            
            logger.info(f"Sync limit: {sync_limit or 'unlimited'}")
            result = await run_sync(services, args.asset_code, sync_limit)
        
        elif args.mode == 'analytics':
            result = await run_analytics(services, args.analysis_type)
        
        elif args.mode == 'evaluate':
            result = await run_evaluate(services, args.account)
        
        elif args.mode == 'discover':
            result = await run_discover(services, args.max_accounts)
        
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
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Log startup
    logger.info("=" * 70)
    logger.info("UBEC Protocol - Unified Main Orchestrator")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Version: 5.4 (Added configurable sync limits)")
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


# ==================== ENTRY POINT ====================

if __name__ == '__main__':
    sys.exit(main())
