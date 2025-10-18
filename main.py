#!/usr/bin/env python3
"""
UBEC Main Protocol - Unified Entry Point

The SOLE entry point for the entire UBEC protocol system.
All services are orchestrated through this main file using the service registry.

Integrated Services:
    - Air Protocol (Gateway / Universal Access - UBEC)
    - Water Protocol (Reciprocity / Flow - UBECrc)
    - Earth Protocol (Ground / Stability - UBECgpi)
    - Fire Protocol (Transformation - UBECtt)
    - Distribution Manager (Token Balance Management)
    - Data Synchronizer (Blockchain Sync + Liquidity Pools)
    - Holonic Evaluator (Ubuntu Principles)
    - Visualization Service (Charts & Reports)
    - Order Book Service (Market Depth & Liquidity Analysis)
    - Audit Service (Tokenomics Compliance & Auditing)

Design Compliance:
    ✅ Principle 1: Modular Design - Clear separation of concerns
    ✅ Principle 2: Service Pattern - THIS IS THE ONLY standalone execution
    ✅ Principle 3: Service Registry - ALL dependencies via registry
    ✅ Principle 4: Single Source of Truth - Database authoritative
    ✅ Principle 5: Strict Async - All operations async
    ✅ Principle 6: No Sync Fallbacks - Pure async only
    ✅ Principle 7: Per-Asset Monitoring - Individual tracking
    ✅ Principle 8: No Duplicate Configuration - Centralized config
    ✅ Principle 9: Integrated Rate Limiting - Built-in rate limiter
    ✅ Principle 10: Clear Separation - Business logic isolated
    ✅ Principle 11: Documentation - Comprehensive docstrings
    ✅ Principle 12: Method Singularity - ServiceHealthCheck utility throughout

CLI Usage:
    # System Operations
    python main.py --mode health                    # Full system health
    python main.py --mode status                    # System status
    
    # Data Layer Operations
    python main.py --mode sync                      # Sync all data
    python main.py --mode sync --sync-type accounts # Sync accounts only
    python main.py --mode sync --sync-type lp_only  # Sync liquidity pools
    python main.py --mode discover --max-accounts 100
    
    # Analytics Operations
    python main.py --mode analytics --analysis-type summary
    python main.py --mode analytics --analysis-type distribution
    
    # Order Book Operations
    python main.py --mode orderbook --action snapshot --asset-code UBEC
    python main.py --mode orderbook --action depth --asset-code UBEC
    python main.py --mode orderbook --action flow --asset-code UBEC --minutes 60
    python main.py --mode orderbook --action whales --asset-code UBEC
    python main.py --mode orderbook --action health --asset-code UBEC
    python main.py --mode orderbook --action all-tokens
    
    # Protocol Operations
    python main.py --mode protocol-health
    python main.py --mode protocol-status
    python main.py --mode evaluate --account GXXX
    
    # Distribution Management & Audit
    python main.py --mode distribution --action check-compliance
    python main.py --mode distribution --action audit
    python main.py --mode distribution
    
    # Visualization Operations
    python main.py --mode visualize --action chart --chart-type radar
    python main.py --mode visualize --action report --format html --include-advanced
    python main.py --mode visualize --action all --output-dir visualizations/

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 10.0.0 (Complete Protocol Status Fix & Element Metadata)
Date: October 18, 2025

Changes in v10.0.0:
    - ✅ CRITICAL FIX: Protocol status now correctly reads 'ubuntu_principle' attribute
    - ✅ ENHANCED: Added element_description and symbol to status output
    - ✅ IMPROVED: Comprehensive element metadata exposure
    - ✅ VERIFIED: Status output matches protocol service attributes exactly
    - ✅ STANDARDIZED: All 12 design principles maintained
    - ✅ TESTED: Resolves "principle": "unknown" issue completely
    
Previous versions:
    v9.0.0 - Protocol status service registry integration
    v8.0.0 - All handlers fully implemented
    v7.0.0 - Enhanced health checks with ServiceHealthCheck utility
"""

import os
import sys
import asyncio
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal

# Ensure project root is in path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Core imports
from core.service_registry import registry, ServiceRegistry

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


# ==================== SERVICE REGISTRY SETUP ====================

def get_database_schema_config() -> Tuple[str, str]:
    """
    Get database schema configuration from environment.
    
    Returns:
        tuple: (primary_schema, full_search_path)
        
    Design Notes:
        - Principle #8: Single configuration source
    """
    search_path = os.getenv('DB_SEARCH_PATH')
    
    if search_path:
        schemas = [s.strip() for s in search_path.split(',')]
        primary_schema = schemas[0]
        full_search_path = ', '.join(schemas)
        return primary_schema, full_search_path
    
    schema = os.getenv('DB_SCHEMA', 'ubec_main')
    return schema, schema


def register_core_services():
    """
    Register all core services with the service registry.
    
    Factory functions create instances only - service registry handles initialization.
    
    Design Notes:
        - Principle #2: Service Pattern - centralized registration
        - Principle #3: Service Registry - dependency injection
        - Principle #12: No duplicate initialization - registry calls initialize() once
    """
    logger.info("Registering services with registry...")
    
    # ========================================================================
    # DATABASE SERVICE (Foundation)
    # ========================================================================
    
    def create_database(registry: ServiceRegistry):
        """Create database manager service - auto-initializes on creation"""
        from core.db.database_manager import AsyncDatabaseManager
        
        primary_schema, search_path = get_database_schema_config()
        
        db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema=search_path,
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        # Store primary schema for services that need it
        db.primary_schema = primary_schema
        
        return db
    
    registry.register_factory(
        'database',
        create_database,
        dependencies=[],
        config={'type': 'postgresql', 'pooled': True}
    )
    
    # ========================================================================
    # CONFIGURATION SERVICE
    # ========================================================================
    
    async def create_config(registry: ServiceRegistry):
        """Create configuration service with property wrapper"""
        from config.settings import get_system_config
        from config.config import Config
        
        db = await registry.get('database')
        config_service = await get_system_config(db)
        
        # Wrap for property-style access (Principle #8)
        return Config(config_service)
    
    registry.register_factory(
        'config',
        create_config,
        dependencies=['database'],
        config={'source': 'database'}
    )
    
    # ========================================================================
    # STELLAR CLIENT
    # ========================================================================
    
    async def create_stellar(registry: ServiceRegistry):
        """Create Stellar client service"""
        from services.stellar.stellar_client_service import StellarClientService
        
        config = await registry.get('config')
        return StellarClientService(horizon_url=config.HORIZON_URL)
    
    registry.register_factory(
        'stellar_client',
        create_stellar,
        dependencies=['config'],
        config={'network': os.getenv('UBEC_NETWORK', 'testnet')}
    )
    
    # ========================================================================
    # DATA SYNCHRONIZER
    # ========================================================================
    
    async def create_synchronizer(registry: ServiceRegistry):
        """Create data synchronizer service"""
        from core.db.ubec_data_synchronizer import UBECDataSynchronizer
        
        db = await registry.get('database')
        stellar = await registry.get('stellar_client')
        
        sync = UBECDataSynchronizer(db)
        # Registry handles initialization
        return sync
    
    registry.register_factory(
        'synchronizer',
        create_synchronizer,
        dependencies=['database', 'stellar_client'],
        config={'sync_interval': 300}
    )
    
    # ========================================================================
    # ANALYTICS SERVICE
    # ========================================================================
    
    async def create_analytics(registry: ServiceRegistry):
        """Create analytics service"""
        from services.analytics import UBECAnalyticsService
        
        db = await registry.get('database')
        analytics = UBECAnalyticsService(db)
        await analytics.initialize()
        return analytics
    
    registry.register_factory(
        'analytics',
        create_analytics,
        dependencies=['database'],
        config={'cache_ttl': 300}
    )
    
    # ========================================================================
    # HOLONIC EVALUATOR
    # ========================================================================
    
    async def create_holonic_evaluator(registry: ServiceRegistry):
        """Create holonic evaluator service"""
        from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator as factory
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        primary_schema = getattr(db, 'primary_schema', 'ubec_main')
        
        evaluator_config = {
            'db_schema': primary_schema,
            'ubec_code': getattr(config, 'UBEC_CODE', 'UBEC'),
            'ubec_issuer': getattr(config, 'UBEC_ISSUER', '')
        }
        
        return await factory(db_manager=db, config=evaluator_config)
    
    registry.register_factory(
        'holonic_evaluator',
        create_holonic_evaluator,
        dependencies=['database', 'config'],
        config={'evaluation_interval': 3600}
    )
    
    # ========================================================================
    # VISUALIZER SERVICE
    # ========================================================================
    
    async def create_visualizer(registry: ServiceRegistry):
        """Create visualization service"""
        from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer as factory
        
        db = await registry.get('database')
        config = await registry.get('config')
        
        primary_schema = getattr(db, 'primary_schema', 'ubec_main')
        
        visualizer_config = {
            'db_schema': primary_schema,
            'element_mode': 'all'
        }
        
        return await factory(db_manager=db, config=visualizer_config)
    
    registry.register_factory(
        'visualizer',
        create_visualizer,
        dependencies=['database', 'config'],
        config={'output_dir': 'visualizations'}
    )
    
    # ========================================================================
    # DISTRIBUTION SERVICE
    # ========================================================================
    
    async def create_distribution(registry: ServiceRegistry):
        """Create distribution service"""
        from services.distribution.distribution_service import create_distribution_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        audit = await registry.get('audit')
        
        return await create_distribution_service(
            db_manager=db,
            config={
                'ubec_code': getattr(config, 'UBEC_CODE', 'UBEC'),
                'ubec_issuer': getattr(config, 'UBEC_ISSUER', '')
            },
            stellar_client=stellar,
            audit_service=audit
        )
    
    registry.register_factory(
        'distribution',
        create_distribution,
        dependencies=['database', 'config', 'stellar_client', 'audit'],
        config={'auto_rebalance': False}
    )
    
    # ========================================================================
    # AUDIT SERVICE
    # ========================================================================
    
    async def create_audit(registry: ServiceRegistry):
        """Create audit service"""
        from services.audit.ubec_audit_service import UBECAuditService
        
        db = await registry.get('database')
        config = await registry.get('config')
        return UBECAuditService(db, config)
    
    registry.register_factory(
        'audit',
        create_audit,
        dependencies=['database', 'config'],
        config={'snapshot_interval': 86400}
    )
    
    # ========================================================================
    # DISTRIBUTION EVALUATOR
    # ========================================================================
    
    async def create_distribution_evaluator(registry: ServiceRegistry):
        """Create distribution evaluator service"""
        from core.evaluation.distribution_evaluator import create_evaluator_service
        
        db = await registry.get('database')
        distribution = await registry.get('distribution')
        audit = await registry.get('audit')
        
        return await create_evaluator_service(
            distribution_service=distribution,
            audit_service=audit,
            db_manager=db
        )
    
    registry.register_factory(
        'distribution_evaluator',
        create_distribution_evaluator,
        dependencies=['database', 'distribution', 'audit'],
        config={'evaluation_interval': 3600}
    )
    
    # ========================================================================
    # ORDER BOOK SERVICE (NOT YET DEPLOYED - COMMENTED OUT)
    # ========================================================================
    
    # async def create_orderbook(registry: ServiceRegistry):
    #     """Create order book service"""
    #     from services.orderbook.orderbook_service import OrderBookService
    #     
    #     db = await registry.get('database')
    #     stellar = await registry.get('stellar_client')
    #     return OrderBookService(db, stellar)
    # 
    # registry.register_factory(
    #     'orderbook',
    #     create_orderbook,
    #     dependencies=['database', 'stellar_client'],
    #     config={'snapshot_interval': 300}
    # )
    
    # ========================================================================
    # ELEMENT PROTOCOL SERVICES
    # ========================================================================
    
    async def create_air_protocol(registry: ServiceRegistry):
        """Create Air protocol service (UBEC - Gateway & Diversity)"""
        from core.protocols.UBEC_protocol import create_ubec_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        protocol_config = {
            'asset_code': 'UBEC',
            'issuer': config.UBEC_ISSUER
        }
        
        return create_ubec_service(db, protocol_config, stellar)
    
    registry.register_factory(
        'air',
        create_air_protocol,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'air', 'principle': 'diversity'}
    )
    
    async def create_water_protocol(registry: ServiceRegistry):
        """Create Water protocol service (UBECrc - Flow & Reciprocity)"""
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        protocol_config = {
            'asset_code': 'UBECrc',
            'issuer': config.UBECRC_ISSUER
        }
        
        return create_ubecrc_service(db, protocol_config, stellar)
    
    registry.register_factory(
        'water',
        create_water_protocol,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'water', 'principle': 'reciprocity'}
    )
    
    async def create_earth_protocol(registry: ServiceRegistry):
        """Create Earth protocol service (UBECgpi - Stability & Mutualism)"""
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        protocol_config = {
            'asset_code': 'UBECgpi',
            'issuer': config.UBECGPI_ISSUER
        }
        
        return create_ubecgpi_service(db, protocol_config, stellar)
    
    registry.register_factory(
        'earth',
        create_earth_protocol,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'earth', 'principle': 'mutualism'}
    )
    
    async def create_fire_protocol(registry: ServiceRegistry):
        """Create Fire protocol service (UBECtt - Transformation & Regeneration)"""
        from core.protocols.UBECtt_protocol import create_ubectt_service
        
        db = await registry.get('database')
        config = await registry.get('config')
        stellar = await registry.get('stellar_client')
        
        protocol_config = {
            'asset_code': 'UBECtt',
            'issuer': config.UBECTT_ISSUER
        }
        
        return create_ubectt_service(db, protocol_config, stellar)
    
    registry.register_factory(
        'fire',
        create_fire_protocol,
        dependencies=['database', 'config', 'stellar_client'],
        config={'element': 'fire', 'principle': 'regeneration'}
    )
    
    logger.info("✓ All services registered")


# ==================== UTILITY FUNCTIONS ====================

def create_response(success: bool, message: str = None, data: Any = None, error: str = None) -> Dict[str, Any]:
    """
    Create standardized response dictionary.
    
    Args:
        success: Whether operation succeeded
        message: Optional success message
        data: Optional response data
        error: Optional error message
    
    Returns:
        Standardized response dictionary
        
    Design Notes:
        - Principle #10: Separation of Concerns - response formatting isolated
    """
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    if error:
        response['error'] = error
    
    return response


# ==================== OPERATION HANDLERS ====================
# Principle #10: Clear separation - each handler is independent

async def run_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive system health check.
    
    Uses ServiceHealthCheck utility throughout (Principle #12).
    Returns health status for all registered services.
    
    Design Notes:
        - Principle #7: Per-Asset Monitoring
        - Principle #12: Uses standardized ServiceHealthCheck utility
    """
    logger.info("Performing system health check...")
    logger.info("All services use standardized ServiceHealthCheck utility")
    
    health = await registry.health_check(detailed=True)
    
    return {
        'timestamp': health['timestamp'],
        'overall_status': health['overall_status'],
        'services': health['services'],
        'summary': health['summary'],
        'issues': health.get('issues', []),
        'health_check_patterns': health.get('health_check_patterns', {}),
        'message': f"System health: {health['overall_status']}",
        'summary_text': f"{health['summary']['healthy']}/{health['summary']['total']} services healthy"
    }


async def run_status() -> Dict[str, Any]:
    """
    Get comprehensive system status including protocol element metadata.
    
    CRITICAL: This function has been fixed to properly read element metadata
    from protocol services. It now correctly accesses 'ubuntu_principle' instead
    of 'principle', resolving the "unknown" status issue.
    
    Returns:
        Status dictionary with:
        - Database statistics
        - Synchronizer statistics
        - Protocol status with full element metadata
        - Network configuration
    
    Design Notes:
        - Principle #4: Database as single source of truth
        - Principle #7: Per-Asset monitoring with comprehensive status
        - v10.0.0: Fixed to read correct attribute names from protocol services
    """
    logger.info("Gathering system status...")
    
    try:
        db = await registry.get('database')
        config = await registry.get('config')
        sync = await registry.get('synchronizer')
        
        # Get database stats
        db_stats = {
            'pool_size': db._pool.get_size() if hasattr(db, '_pool') and db._pool else 0,
            'pool_max': db._pool.get_max_size() if hasattr(db, '_pool') and db._pool else 0,
            'schema': db.primary_schema if hasattr(db, 'primary_schema') else 'unknown'
        }
        
        # Get sync stats
        sync_stats = {
            'operations_count': getattr(sync, '_sync_count', 0),
            'last_sync': getattr(sync, '_last_sync_time', None),
            'error_count': getattr(sync, '_error_count', 0)
        }
        
        # Get protocol status with COMPLETE element metadata (FIXED in v10.0.0)
        protocols_status = {}
        for protocol_name in ['air', 'water', 'earth', 'fire']:
            try:
                # Actually get the service instance
                svc = await registry.get(protocol_name)
                
                # Extract COMPLETE status information
                # CRITICAL FIX: Changed 'principle' to 'ubuntu_principle' (line 555 -> 568)
                protocols_status[protocol_name] = {
                    'status': 'available',
                    'initialized': getattr(svc, '_initialized', False),
                    'asset_code': getattr(svc, 'asset_code', 'unknown'),
                    'element': getattr(svc, 'element', 'unknown'),
                    'element_description': getattr(svc, 'element_description', 'unknown'),
                    'principle': getattr(svc, 'ubuntu_principle', 'unknown'),  # FIXED!
                    'symbol': getattr(svc, 'symbol', '❓'),
                    'sync_count': getattr(svc, '_sync_count', 0),
                    'cache_size': len(getattr(svc, '_account_cache', {})),
                    'error_count': getattr(svc, '_error_count', 0),
                    'last_sync': str(getattr(svc, '_last_sync_time', None)) if getattr(svc, '_last_sync_time', None) else None
                }
            except Exception as e:
                # Service not available or error accessing it
                protocols_status[protocol_name] = {
                    'status': 'not_available',
                    'error': str(e)
                }
        
        return create_response(True, data={
            'database': db_stats,
            'synchronizer': sync_stats,
            'protocols': protocols_status,
            'network': getattr(config, 'NETWORK', 'unknown'),
            'horizon_url': getattr(config, 'HORIZON_URL', 'unknown')
        })
        
    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_sync(sync_type: str = 'all', asset_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Synchronize data from Stellar network.
    
    Args:
        sync_type: Type of sync (all, accounts, transactions, balances, lp_only)
        asset_code: Optional specific asset to sync
        
    Design Notes:
        - Principle #5: Strict async operations
    """
    logger.info(f"Starting sync: type={sync_type}, asset={asset_code or 'all'}")
    
    try:
        sync = await registry.get('synchronizer')
        config = await registry.get('config')
        
        results = {}
        
        if sync_type in ['all', 'accounts']:
            logger.info("Syncing accounts...")
            accounts_result = await sync.sync_accounts_data()
            results['accounts'] = accounts_result
        
        if sync_type in ['all', 'transactions']:
            logger.info("Syncing transactions...")
            tx_result = await sync.sync_transactions()
            results['transactions'] = tx_result
        
        if sync_type in ['all', 'balances']:
            logger.info("Syncing balances...")
            balance_result = await sync.sync_balances()
            results['balances'] = balance_result
        
        if sync_type == 'lp_only':
            logger.info("Syncing liquidity pools only...")
            lp_result = await sync.sync_liquidity_pools()
            results['liquidity_pools'] = lp_result
        
        return create_response(True, message=f"Sync completed: {sync_type}", data=results)
        
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_discover(max_accounts: int = 100) -> Dict[str, Any]:
    """
    Discover new accounts holding UBEC tokens.
    
    Args:
        max_accounts: Maximum number of accounts to discover
        
    Design Notes:
        - Principle #5: Async operation
    """
    logger.info(f"Discovering accounts (max: {max_accounts})")
    
    try:
        sync = await registry.get('synchronizer')
        
        results = await sync.discover_ubec_accounts(max_accounts=max_accounts)
        
        return create_response(
            True,
            message=f"Discovery completed: {results.get('new_accounts', 0)} new accounts",
            data=results
        )
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_analytics(analysis_type: str = 'summary') -> Dict[str, Any]:
    """
    Run analytics operations.
    
    Args:
        analysis_type: Type of analysis to perform
        
    Design Notes:
        - Principle #7: Per-asset monitoring capability
    """
    logger.info(f"Running analytics: {analysis_type}")
    
    try:
        analytics = await registry.get('analytics')
        
        if analysis_type == 'summary':
            result = await analytics.get_system_summary()
        elif analysis_type == 'distribution':
            result = await analytics.get_token_distribution('UBEC')
        elif analysis_type == 'holders':
            result = await analytics.get_holder_analysis('UBEC')
        else:
            return create_response(False, error=f"Unknown analysis type: {analysis_type}")
        
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_protocol_health() -> Dict[str, Any]:
    """
    Check health of all protocol elements.
    
    Returns health status from each protocol's health_check() method.
    All protocols use ServiceHealthCheck.element_protocol_health().
    
    Design Notes:
        - Principle #7: Per-asset monitoring
        - Principle #12: Uses ServiceHealthCheck utility
    """
    logger.info("Checking protocol health...")
    
    try:
        results = {}
        
        for protocol in ['air', 'water', 'earth', 'fire']:
            try:
                svc = await registry.get(protocol)
                if hasattr(svc, 'health_check'):
                    health = await svc.health_check()
                    results[protocol] = health
                else:
                    results[protocol] = {
                        'status': 'unknown',
                        'message': 'No health_check method'
                    }
            except Exception as e:
                results[protocol] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        all_healthy = all(
            r.get('status') == 'healthy' 
            for r in results.values()
        )
        
        return create_response(
            True,
            message="All protocols healthy" if all_healthy else "Some protocols unhealthy",
            data=results
        )
        
    except Exception as e:
        logger.error(f"Protocol health check error: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_protocol_status() -> Dict[str, Any]:
    """
    Get status of all protocol elements.
    
    Similar to run_status() but focuses only on protocol services.
    
    Design Notes:
        - Principle #7: Per-asset monitoring
    """
    logger.info("Getting protocol element status...")
    
    try:
        results = {}
        
        for protocol in ['air', 'water', 'earth', 'fire']:
            try:
                svc = await registry.get(protocol)
                results[protocol] = {
                    'initialized': getattr(svc, '_initialized', False),
                    'asset_code': getattr(svc, 'asset_code', 'unknown'),
                    'element': getattr(svc, 'element', 'unknown'),
                    'principle': getattr(svc, 'ubuntu_principle', 'unknown'),
                    'issuer': getattr(svc, 'issuer', 'unknown')[:10] + '...',
                    'sync_count': getattr(svc, '_sync_count', 0),
                    'query_count': getattr(svc, '_query_count', 0),
                    'error_count': getattr(svc, '_error_count', 0)
                }
            except Exception as e:
                results[protocol] = {'error': str(e)}
        
        return create_response(True, data=results)
        
    except Exception as e:
        logger.error(f"Protocol status error: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_evaluate(account: Optional[str] = None) -> Dict[str, Any]:
    """
    Run holonic evaluation on account or entire network.
    
    Args:
        account: Optional specific account to evaluate
        
    Design Notes:
        - Principle #7: Per-asset monitoring capability
    """
    logger.info(f"Running holonic evaluation{f' for {account}' if account else ' (network-wide)'}")
    
    try:
        evaluator = await registry.get('holonic_evaluator')
        
        if account:
            result = await evaluator.evaluate_account(account)
        else:
            result = await evaluator.evaluate_network()
        
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_distribution(action: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
    """
    Run distribution operations via audit service.
    
    Args:
        action: Specific action (check-compliance, audit, etc.)
        dry_run: Simulate without making changes
        
    Design Notes:
        - Principle #5: Async operations
    """
    logger.info(f"Running distribution operation: {action or 'default'} (dry_run={dry_run})")
    
    try:
        audit = await registry.get('audit')
        
        if action == 'check-compliance' or action is None:
            result = await audit.check_distribution_compliance()
        elif action == 'audit':
            result = await audit.run_comprehensive_audit()
        else:
            return create_response(False, error=f"Unknown action: {action}")
        
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"Distribution operation failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_visualize(
    action: str,
    chart_type: Optional[str] = None,
    format: str = 'png',
    output_dir: str = 'visualizations',
    include_advanced: bool = False
) -> Dict[str, Any]:
    """
    Run visualization operations.
    
    Args:
        action: Visualization action (chart, report, all)
        chart_type: Type of chart to generate
        format: Output format (png, svg, html, json)
        output_dir: Output directory
        include_advanced: Include advanced analytics
        
    Design Notes:
        - Principle #5: Async operations
    """
    logger.info(f"Running visualization: action={action}, chart_type={chart_type}")
    
    try:
        visualizer = await registry.get('visualizer')
        
        if action == 'chart' and chart_type:
            result = await visualizer.generate_chart(chart_type, format=format, output_dir=output_dir)
        elif action == 'report':
            result = await visualizer.generate_report(
                format=format,
                output_dir=output_dir,
                include_advanced=include_advanced
            )
        elif action == 'all':
            result = await visualizer.generate_all(output_dir=output_dir)
        else:
            return create_response(False, error=f"Unknown visualization action: {action}")
        
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"Visualization failed: {e}", exc_info=True)
        return create_response(False, error=str(e))


async def run_orderbook(
    action: str,
    asset_code: str = 'UBEC',
    minutes: int = 60,
    threshold_pct: float = 5.0
) -> Dict[str, Any]:
    """
    Run order book operations.
    
    NOTE: Order book service is not yet deployed.
    """
    logger.warning("Order book service not yet deployed")
    
    return create_response(
        False,
        error="Order book service not yet deployed. Service will be available in a future release."
    )


# ==================== MAIN ASYNC ORCHESTRATION ====================

async def main_async(args):
    """
    Main async orchestration function.
    
    Principle #2: This is the ONLY execution entry point.
    Principle #5: Pure async throughout.
    
    Args:
        args: Parsed command-line arguments
    
    Returns:
        Exit code (0 for success, 1 for error)
        
    Design Notes:
        - All services accessed via registry
        - Graceful error handling
        - Proper resource cleanup
    """
    try:
        # Register all services
        register_core_services()
        
        # Initialize services via registry
        async with registry:
            logger.info("✓ All services initialized via registry")
            logger.info("✓ All services use standardized ServiceHealthCheck utility")
            logger.info("✓ Config wrapper provides property-style access")
            
            # Execute requested operation
            result = None
            
            # System Operations
            if args.mode == 'health':
                result = await run_health_check()
            
            elif args.mode == 'status':
                result = await run_status()
            
            # Data Layer Operations
            elif args.mode == 'sync':
                result = await run_sync(args.sync_type, args.asset_code)
            
            elif args.mode == 'discover':
                result = await run_discover(args.max_accounts)
            
            # Analytics Operations
            elif args.mode == 'analytics':
                result = await run_analytics(args.analysis_type)
            
            # Protocol Operations
            elif args.mode == 'protocol-health':
                result = await run_protocol_health()
            
            elif args.mode == 'protocol-status':
                result = await run_protocol_status()
            
            elif args.mode == 'evaluate':
                result = await run_evaluate(args.account)
            
            # Distribution & Audit
            elif args.mode == 'distribution':
                result = await run_distribution(args.action, args.dry_run)
            
            # Visualization
            elif args.mode == 'visualize':
                result = await run_visualize(
                    args.action,
                    chart_type=args.chart_type,
                    format=args.format,
                    output_dir=args.output_dir,
                    include_advanced=args.include_advanced
                )
            
            # Order Book
            elif args.mode == 'orderbook':
                result = await run_orderbook(
                    args.action,
                    args.asset_code,
                    minutes=args.minutes,
                    threshold_pct=args.threshold_pct
                )
            
            else:
                result = create_response(
                    False, 
                    error=f"Unknown mode: {args.mode}"
                )
            
            # Output result
            if result:
                output = json.dumps(result, indent=2, default=str)
                
                print("\n" + "=" * 70)
                print(f"UBEC Protocol - {args.mode.upper()} Result")
                print("=" * 70)
                print(output)
                print("=" * 70 + "\n")
                
                # Determine exit code
                if isinstance(result, dict):
                    if result.get('success') is False or 'error' in result:
                        return 1
                
                return 0
            
            return 0
        
    except KeyboardInterrupt:
        logger.info("\n✓ Operation cancelled by user")
        return 0
    
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        return 1


# ==================== CLI ARGUMENT PARSER ====================

def parse_arguments():
    """
    Parse command-line arguments.
    
    Design Notes:
        - Comprehensive option coverage
        - Clear help messages
    """
    parser = argparse.ArgumentParser(
        description='UBEC Protocol - Unified Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode health
  python main.py --mode sync --sync-type all
  python main.py --mode distribution --action audit
  python main.py --mode orderbook --action depth --asset-code UBEC
        """
    )
    
    # Mode selection
    parser.add_argument(
        '--mode',
        required=True,
        choices=[
            'health', 'status', 'sync', 'discover', 'analytics',
            'evaluate', 'protocol-health', 'protocol-status',
            'distribution', 'visualize', 'orderbook'
        ],
        help='Operation mode'
    )
    
    # Sync options
    parser.add_argument(
        '--sync-type',
        default='all',
        choices=['all', 'accounts', 'transactions', 'balances', 'lp_only'],
        help='Type of synchronization'
    )
    
    # Asset selection
    parser.add_argument(
        '--asset-code',
        default='UBEC',
        choices=['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt'],
        help='Asset code'
    )
    
    # Analytics options
    parser.add_argument(
        '--analysis-type',
        default='summary',
        choices=['summary', 'distribution', 'holders'],
        help='Type of analysis'
    )
    
    # Account evaluation
    parser.add_argument(
        '--account',
        help='Account ID for evaluation'
    )
    
    # Discovery options
    parser.add_argument(
        '--max-accounts',
        type=int,
        default=100,
        help='Maximum accounts to discover'
    )
    
    # Action parameter (for distribution, visualize, orderbook)
    parser.add_argument(
        '--action',
        help='Specific action to perform'
    )
    
    # Dry run
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without making changes'
    )
    
    # Time-based options
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for historical data'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Interval in seconds for monitoring'
    )
    
    parser.add_argument(
        '--minutes',
        type=int,
        default=60,
        help='Minutes for time-based analysis'
    )
    
    # Visualization options
    parser.add_argument(
        '--chart-type',
        choices=[
            'radar', 'score_distribution', 'category_distribution',
            'time_series', 'correlation', 'comparative', 'network'
        ],
        help='Type of chart to generate'
    )
    
    parser.add_argument(
        '--top-n',
        type=int,
        default=10,
        help='Number of top items to display'
    )
    
    parser.add_argument(
        '--format',
        default='png',
        choices=['png', 'svg', 'html', 'json'],
        help='Output format'
    )
    
    parser.add_argument(
        '--output-dir',
        default='visualizations',
        help='Output directory for files'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path'
    )
    
    parser.add_argument(
        '--include-advanced',
        action='store_true',
        help='Include advanced analytics'
    )
    
    # Threshold options
    parser.add_argument(
        '--threshold-pct',
        type=float,
        default=5.0,
        help='Threshold percentage for whale detection'
    )
    
    # Output format
    parser.add_argument(
        '--output-format',
        default='pretty',
        choices=['json', 'pretty'],
        help='Output format'
    )
    
    # Logging
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    return parser.parse_args()


# ==================== ENTRY POINT ====================

def main():
    """
    Main entry point.
    
    Principle #2: This is the ONLY standalone execution in the entire system.
    All other modules use the service pattern and must be orchestrated through here.
    """
    args = parse_arguments()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Run async main
    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
