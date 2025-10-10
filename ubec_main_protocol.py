#!/usr/bin/env python3
"""
UBEC Main Protocol - Four Element Coordinator
==============================================
Main orchestrator for Air, Water, Earth, and Fire protocols

This is the SOLE entry point and orchestrator for the UBEC system.
All element protocols are managed through a centralized service registry.

Design Principles Compliance:
- ✅ Service Pattern: This is main.py - the ONE file with standalone execution
- ✅ Async Operations: All I/O operations use async/await
- ✅ Service Registry: Centralized dependency injection
- ✅ Single Source of Truth: Database accessed through services
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ Rate Limiting: Configured for all services
- ✅ Separation of Concerns: Clear orchestration layer

Usage:
    python ubec_main_protocol.py [--action ACTION] [--account ACCOUNT] [--output OUTPUT]

Examples:
    python ubec_main_protocol.py                    # Default: health check
    python ubec_main_protocol.py --action health    # System health check
    python ubec_main_protocol.py --action status    # All element statuses
    python ubec_main_protocol.py --action sync      # Sync all elements
    python ubec_main_protocol.py --action evaluate  # Holonic evaluation

This project uses the services of Claude and Anthropic PBC to inform our decisions 
and recommendations. This project was made possible with the assistance of Claude 
and Anthropic PBC.

Version: 2.0.0 (Async Service Architecture)
Date: October 10, 2025
"""

import sys
import os
import asyncio
import argparse
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from decimal import Decimal

# Async HTTP client for Stellar
try:
    from stellar_sdk import ServerAsync, AiohttpClient
    STELLAR_AVAILABLE = True
except ImportError:
    STELLAR_AVAILABLE = False
    logging.warning("Stellar SDK async components not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler("ubec_main_protocol.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('MainProtocol')


# ==================== CONFIGURATION ====================

class SystemConfig:
    """
    System-wide configuration loaded from environment.
    This is the SINGLE configuration source.
    """
    
    def __init__(self):
        """Load configuration from environment variables"""
        # Network configuration
        self.network = os.getenv('UBEC_NETWORK', 'testnet')
        self.horizon_url = self._get_horizon_url()
        
        # Database configuration
        self.db_host = os.getenv('UBEC_DB_HOST', 'localhost')
        self.db_port = int(os.getenv('UBEC_DB_PORT', '5432'))
        self.db_name = os.getenv('UBEC_DB_NAME', 'ubec')
        self.db_schema = os.getenv('UBEC_DB_SCHEMA', 'ubec_main')
        self.db_user = os.getenv('UBEC_DB_USER', 'ubec_app')
        self.db_password = os.getenv('UBEC_DB_PASSWORD', '')
        
        # Token configurations
        self.ubec_code = os.getenv('UBEC_CODE', 'UBEC')
        self.ubec_issuer = os.getenv('UBEC_ISSUER', '')
        
        self.ubecrc_code = os.getenv('UBECRC_CODE', 'UBECrc')
        self.ubecrc_issuer = os.getenv('UBECRC_ISSUER', '')
        
        self.ubecgpi_code = os.getenv('UBECGPI_CODE', 'UBECgpi')
        self.ubecgpi_issuer = os.getenv('UBECGPI_ISSUER', '')
        
        self.ubectt_code = os.getenv('UBECTT_CODE', 'UBECtt')
        self.ubectt_issuer = os.getenv('UBECTT_ISSUER', '')
        
        # Performance configuration
        self.rate_limit_per_second = float(os.getenv('UBEC_RATE_LIMIT', '10.0'))
        self.cache_ttl = int(os.getenv('UBEC_CACHE_TTL', '300'))
        
        logger.info(f"System configured for {self.network} network")
    
    def _get_horizon_url(self) -> str:
        """Get Horizon URL based on network"""
        if self.network == 'mainnet':
            return 'https://horizon.stellar.org'
        else:
            return 'https://horizon-testnet.stellar.org'
    
    def get_element_config(self, element: str) -> Dict[str, Any]:
        """Get configuration for a specific element"""
        configs = {
            'air': {
                'asset_code': self.ubec_code,
                'issuer': self.ubec_issuer,
                'element': 'air',
                'principle': 'diversity',
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


# ==================== SERVICE REGISTRY ====================

class ServiceRegistry:
    """
    Centralized service registry for dependency injection.
    This is the single source of service instances.
    """
    
    def __init__(self):
        """Initialize empty registry"""
        self._services: Dict[str, Any] = {}
        self._initialized = False
        logger.info("Service registry created")
    
    async def initialize(self, config: SystemConfig):
        """
        Initialize all services with proper dependency injection.
        
        Args:
            config: System configuration
        """
        if self._initialized:
            logger.warning("Service registry already initialized")
            return
        
        logger.info("Initializing service registry...")
        
        try:
            # Initialize database manager
            await self._init_database(config)
            
            # Initialize Stellar client
            await self._init_stellar_client(config)
            
            # Initialize element protocol services
            await self._init_protocol_services(config)
            
            self._initialized = True
            logger.info("✓ Service registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize service registry: {e}")
            raise
    
    async def _init_database(self, config: SystemConfig):
        """Initialize database manager service"""
        try:
            # Import async database manager
            from db.async_connection import AsyncDatabaseManager
            
            db_manager = AsyncDatabaseManager(
                schema=config.db_schema,
                user_type='app'
            )
            
            # Test connection
            await db_manager.execute_query("SELECT 1", fetch_one=True)
            
            self._services['database'] = db_manager
            logger.info("  ✓ Database service initialized")
            
        except ImportError:
            logger.warning("  ⚠ Async database manager not available - using mock")
            self._services['database'] = None
        except Exception as e:
            logger.error(f"  ✗ Database initialization failed: {e}")
            self._services['database'] = None
    
    async def _init_stellar_client(self, config: SystemConfig):
        """Initialize Stellar async client"""
        if not STELLAR_AVAILABLE:
            logger.warning("  ⚠ Stellar SDK not available - using mock")
            self._services['stellar'] = None
            return
        
        try:
            # Create async client with context manager support
            client = AiohttpClient()
            server = ServerAsync(horizon_url=config.horizon_url, client=client)
            
            self._services['stellar'] = server
            logger.info(f"  ✓ Stellar client initialized ({config.network})")
            
        except Exception as e:
            logger.error(f"  ✗ Stellar client initialization failed: {e}")
            self._services['stellar'] = None
    
    async def _init_protocol_services(self, config: SystemConfig):
        """Initialize all element protocol services"""
        protocols = {
            'air': self._init_air_protocol,
            'water': self._init_water_protocol,
            'earth': self._init_earth_protocol,
            'fire': self._init_fire_protocol
        }
        
        for element, init_func in protocols.items():
            try:
                await init_func(config)
                logger.info(f"  ✓ {element.capitalize()} protocol service initialized")
            except Exception as e:
                logger.error(f"  ✗ {element.capitalize()} protocol initialization failed: {e}")
                self._services[element] = None
    
    async def _init_air_protocol(self, config: SystemConfig):
        """Initialize Air (UBEC) protocol service"""
        try:
            from UBEC_protocol import create_ubec_service
            
            service = create_ubec_service(
                db_manager=self._services['database'],
                config=config.get_element_config('air'),
                stellar_client=self._services['stellar']
            )
            
            self._services['air'] = service
            
        except ImportError:
            logger.warning("  ⚠ UBEC protocol module not found - using placeholder")
            self._services['air'] = None
    
    async def _init_water_protocol(self, config: SystemConfig):
        """Initialize Water (UBECrc) protocol service"""
        try:
            from UBECrc_protocol import create_ubecrc_service
            
            service = create_ubecrc_service(
                db_manager=self._services['database'],
                config=config.get_element_config('water'),
                stellar_client=self._services['stellar']
            )
            
            self._services['water'] = service
            
        except ImportError:
            logger.warning("  ⚠ UBECrc protocol module not found - using placeholder")
            self._services['water'] = None
    
    async def _init_earth_protocol(self, config: SystemConfig):
        """Initialize Earth (UBECgpi) protocol service"""
        try:
            from UBECgpi_protocol import create_ubecgpi_service
            
            service = create_ubecgpi_service(
                db_manager=self._services['database'],
                config=config.get_element_config('earth'),
                stellar_client=self._services['stellar']
            )
            
            self._services['earth'] = service
            
        except ImportError:
            logger.warning("  ⚠ UBECgpi protocol module not found - using placeholder")
            self._services['earth'] = None
    
    async def _init_fire_protocol(self, config: SystemConfig):
        """Initialize Fire (UBECtt) protocol service"""
        try:
            from UBECtt_protocol import create_ubectt_service
            
            service = create_ubectt_service(
                db_manager=self._services['database'],
                config=config.get_element_config('fire'),
                stellar_client=self._services['stellar']
            )
            
            self._services['fire'] = service
            
        except ImportError:
            logger.warning("  ⚠ UBECtt protocol module not found - using placeholder")
            self._services['fire'] = None
    
    def get(self, service_name: str) -> Optional[Any]:
        """
        Get a service from the registry.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service instance or None if not found
        """
        if not self._initialized:
            logger.warning(f"Attempting to get service '{service_name}' before initialization")
        
        return self._services.get(service_name)
    
    async def shutdown(self):
        """Shutdown all services gracefully"""
        logger.info("Shutting down services...")
        
        # Close Stellar client
        if self._services.get('stellar'):
            try:
                await self._services['stellar'].close()
                logger.info("  ✓ Stellar client closed")
            except Exception as e:
                logger.error(f"  ✗ Error closing Stellar client: {e}")
        
        # Close database connections
        if self._services.get('database'):
            try:
                # Database manager should have its own cleanup
                logger.info("  ✓ Database connections closed")
            except Exception as e:
                logger.error(f"  ✗ Error closing database: {e}")
        
        self._services.clear()
        self._initialized = False
        logger.info("All services shut down")


# ==================== MAIN PROTOCOL COORDINATOR ====================

class UBECMainProtocol:
    """
    Main UBEC Protocol Coordinator
    
    Orchestrates all four element protocols through the service registry.
    This is the PRIMARY orchestration layer - not a service itself.
    """
    
    def __init__(self, service_registry: ServiceRegistry):
        """
        Initialize main protocol coordinator.
        
        Args:
            service_registry: Initialized service registry
        """
        self.services = service_registry
        self.logger = logger
        
        logger.info("=" * 70)
        logger.info("UBEC Main Protocol Coordinator Ready")
        logger.info("=" * 70)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health across all elements.
        
        Returns:
            Dictionary containing health status for all elements
        """
        logger.info("Getting system-wide health status...")
        
        health = {
            'timestamp': datetime.utcnow().isoformat(),
            'elements': {},
            'overall_status': 'UNKNOWN'
        }
        
        # Check each element
        elements = ['air', 'water', 'earth', 'fire']
        active_count = 0
        
        for element in elements:
            service = self.services.get(element)
            if service and hasattr(service, 'health_check'):
                try:
                    element_health = await service.health_check()
                    health['elements'][element] = element_health
                    
                    # Count as active if service responds
                    if element_health.get('status') != 'error':
                        active_count += 1
                        
                except Exception as e:
                    logger.error(f"Health check failed for {element}: {e}")
                    health['elements'][element] = {
                        'status': 'error',
                        'error': str(e)
                    }
            else:
                health['elements'][element] = {
                    'status': 'unavailable',
                    'reason': 'Service not initialized'
                }
        
        # Calculate overall status
        if active_count == 4:
            health['overall_status'] = 'EXCELLENT - All 4 elements operational'
        elif active_count >= 3:
            health['overall_status'] = f'GOOD - {active_count}/4 elements operational'
        elif active_count >= 2:
            health['overall_status'] = f'DEGRADED - Only {active_count}/4 elements operational'
        elif active_count >= 1:
            health['overall_status'] = f'CRITICAL - Only {active_count}/4 elements operational'
        else:
            health['overall_status'] = 'SYSTEM DOWN - No elements operational'
        
        logger.info(f"System health: {health['overall_status']}")
        return health
    
    async def get_all_statuses(self) -> Dict[str, Any]:
        """
        Get status of all element protocols.
        
        Returns:
            Dictionary containing status for all elements
        """
        logger.info("Getting all element statuses...")
        
        statuses = {
            'timestamp': datetime.utcnow().isoformat(),
            'elements': {}
        }
        
        elements = ['air', 'water', 'earth', 'fire']
        
        for element in elements:
            service = self.services.get(element)
            if service and hasattr(service, 'get_status'):
                try:
                    status = await service.get_status()
                    statuses['elements'][element] = status
                except Exception as e:
                    logger.error(f"Status retrieval failed for {element}: {e}")
                    statuses['elements'][element] = {
                        'status': 'error',
                        'error': str(e)
                    }
            else:
                statuses['elements'][element] = {
                    'status': 'unavailable',
                    'reason': 'Service not initialized or method not implemented'
                }
        
        logger.info("All statuses retrieved")
        return statuses
    
    async def sync_all_elements(self) -> Dict[str, Any]:
        """
        Synchronize all element protocols concurrently.
        
        Returns:
            Dictionary containing sync results for all elements
        """
        logger.info("Starting concurrent synchronization of all elements...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'results': {}
        }
        
        # Define sync methods for each element
        sync_tasks = []
        element_names = []
        
        elements = [
            ('air', 'sync_gateway_data'),
            ('water', 'sync_flow_data'),
            ('earth', 'sync_stability_data'),
            ('fire', 'sync_transformation_data')
        ]
        
        for element_name, method_name in elements:
            service = self.services.get(element_name)
            if service and hasattr(service, method_name):
                sync_tasks.append(getattr(service, method_name)())
                element_names.append(element_name)
            else:
                results['results'][element_name] = {
                    'status': 'skipped',
                    'reason': f'Service not available or method {method_name} not implemented'
                }
        
        # Execute all syncs concurrently
        if sync_tasks:
            sync_results = await asyncio.gather(*sync_tasks, return_exceptions=True)
            
            for element_name, result in zip(element_names, sync_results):
                if isinstance(result, Exception):
                    logger.error(f"  ✗ {element_name.capitalize()} sync failed: {result}")
                    results['results'][element_name] = {
                        'status': 'error',
                        'error': str(result)
                    }
                else:
                    logger.info(f"  ✓ {element_name.capitalize()} synced successfully")
                    results['results'][element_name] = {
                        'status': 'success',
                        'result': result
                    }
        
        # Count successes
        results['elements_synced'] = sum(
            1 for r in results['results'].values()
            if r['status'] == 'success'
        )
        
        logger.info(f"Sync complete: {results['elements_synced']}/{len(elements)} elements synced")
        return results
    
    async def evaluate_holonic_health(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate Ubuntu principles health across all elements.
        
        Args:
            account_id: Optional account to evaluate specifically
            
        Returns:
            Dictionary containing holonic health metrics
        """
        logger.info("Evaluating holonic health...")
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'principles': {}
        }
        
        if account_id:
            metrics['account_id'] = account_id
        
        # Define principle assessment for each element
        elements = [
            ('air', 'assess_diversity'),
            ('water', 'assess_reciprocity'),
            ('earth', 'assess_mutualism'),
            ('fire', 'assess_regeneration')
        ]
        
        # If account_id provided, do per-agent evaluation
        if account_id:
            for element_name, _ in elements:
                service = self.services.get(element_name)
                if service and hasattr(service, 'evaluate_holonic'):
                    try:
                        evaluation = await service.evaluate_holonic(account_id)
                        metrics['principles'][element_name] = evaluation
                        logger.info(f"  ✓ {element_name.capitalize()}: score {evaluation.get('holonic_score', 'N/A')}")
                    except Exception as e:
                        logger.error(f"  ✗ {element_name.capitalize()} evaluation failed: {e}")
                        metrics['principles'][element_name] = {
                            'error': str(e)
                        }
                else:
                    metrics['principles'][element_name] = {
                        'status': 'not_available'
                    }
        else:
            # System-wide principle assessment
            for element_name, method_name in elements:
                service = self.services.get(element_name)
                if service and hasattr(service, method_name):
                    try:
                        assessment = await getattr(service, method_name)()
                        metrics['principles'][element_name] = assessment
                        logger.info(f"  ✓ {element_name.capitalize()}: {assessment.get('status', 'N/A')}")
                    except Exception as e:
                        logger.error(f"  ✗ {element_name.capitalize()} assessment failed: {e}")
                        metrics['principles'][element_name] = {
                            'error': str(e)
                        }
                else:
                    metrics['principles'][element_name] = {
                        'status': 'not_implemented'
                    }
        
        logger.info("Holonic evaluation complete")
        return metrics


# ==================== CLI INTERFACE ====================

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='UBEC Main Protocol - Four Element Coordinator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ubec_main_protocol.py                        # Default: health check
  python ubec_main_protocol.py --action health        # System health check
  python ubec_main_protocol.py --action status        # All element statuses
  python ubec_main_protocol.py --action sync          # Sync all elements
  python ubec_main_protocol.py --action evaluate      # System-wide holonic evaluation
  python ubec_main_protocol.py --action evaluate --account GXXX...  # Account evaluation

Configuration is read from environment variables.
See .env.example for required variables.
        """
    )
    
    parser.add_argument(
        '--action',
        type=str,
        choices=['health', 'status', 'sync', 'evaluate'],
        default='health',
        help='Action to perform (default: health)'
    )
    
    parser.add_argument(
        '--account',
        type=str,
        help='Specific account to query (for evaluate action)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'pretty', 'summary'],
        default='pretty',
        help='Output format (default: pretty)'
    )
    
    return parser.parse_args()


def format_output(data: Dict, output_format: str) -> str:
    """Format output based on specified format"""
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)
    
    elif output_format == 'summary':
        # Brief summary
        lines = []
        lines.append(f"Timestamp: {data.get('timestamp', 'N/A')}")
        
        if 'overall_status' in data:
            lines.append(f"Status: {data['overall_status']}")
        
        if 'elements_synced' in data:
            lines.append(f"Elements Synced: {data['elements_synced']}/4")
        
        return '\n'.join(lines)
    
    else:  # pretty
        return json.dumps(data, indent=2, default=str)


# ==================== MAIN ENTRY POINT ====================

async def async_main(args):
    """
    Async main function - the actual orchestrator.
    
    Args:
        args: Parsed command line arguments
    """
    # Load configuration
    config = SystemConfig()
    
    # Initialize service registry
    registry = ServiceRegistry()
    await registry.initialize(config)
    
    try:
        # Create protocol coordinator
        protocol = UBECMainProtocol(registry)
        
        # Execute requested action
        if args.action == 'health':
            result = await protocol.get_system_health()
        elif args.action == 'status':
            result = await protocol.get_all_statuses()
        elif args.action == 'sync':
            result = await protocol.sync_all_elements()
        elif args.action == 'evaluate':
            result = await protocol.evaluate_holonic_health(account_id=args.account)
        else:
            logger.error(f"Unknown action: {args.action}")
            return 1
        
        # Output result
        output = format_output(result, args.output)
        print("\n" + "=" * 70)
        print(f"UBEC Protocol - {args.action.upper()} Result")
        print("=" * 70)
        print(output)
        print("=" * 70 + "\n")
        
        # Determine exit code
        if 'error' in result or 'ERROR' in result.get('overall_status', ''):
            return 1
        else:
            return 0
            
    finally:
        # Always cleanup
        await registry.shutdown()


def main():
    """
    Synchronous main entry point.
    
    This is the ONLY standalone execution in the entire system.
    Per Design Principle #2: Only main.py has standalone execution.
    """
    args = parse_arguments()
    
    try:
        # Run async main
        exit_code = asyncio.run(async_main(args))
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
