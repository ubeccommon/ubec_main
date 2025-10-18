#!/usr/bin/env python3
"""
Earth Protocol Complete Diagnostic
===================================
Replicates main.py's initialization to diagnose Earth protocol.

Usage: python full_earth_diagnostic.py

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def full_diagnostic():
    """Run complete Earth diagnostic with full registry initialization."""
    
    print("=" * 70)
    print("EARTH PROTOCOL COMPLETE DIAGNOSTIC")
    print("=" * 70)
    print()
    
    try:
        # Import what we need
        from core.service_registry import registry
        
        # Step 1: Register and initialize minimal services
        print("Step 1: Registering minimal services...")
        
        # Database - sync factory, no arguments
        def create_database():
            from core.db.database_manager import AsyncDatabaseManager
            db = AsyncDatabaseManager(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '5432')),
                database=os.getenv('DB_NAME', 'ubec'),
                schema='ubec_main, phenomenal, topology, public',
                user=os.getenv('DB_USER', 'ubec_app'),
                password=os.getenv('DB_PASSWORD', '')
            )
            return db
        
        registry.register_factory('database', create_database, dependencies=[])
        print("   ✓ Database registered")
        
        # Config - async factory with registry parameter
        async def create_config(registry):
            from config.settings import get_system_config
            db = await registry.get('database')
            return await get_system_config(db)
        
        registry.register_factory('config', create_config, dependencies=['database'])
        print("   ✓ Config registered")
        
        # Stellar - async factory with registry parameter
        async def create_stellar(registry):
            from stellar_sdk import ServerAsync
            config = await registry.get('config')
            return ServerAsync(horizon_url=config.HORIZON_URL)
        
        registry.register_factory('stellar_client', create_stellar, dependencies=['config'])
        print("   ✓ Stellar client registered")
        print()
        
        # Step 2: Register Earth protocol
        print("Step 2: Registering Earth protocol...")
        
        async def create_earth(registry):
            """Create Earth protocol service"""
            db = await registry.get('database')
            stellar = await registry.get('stellar_client')
            config = await registry.get('config')
            
            # Import the factory
            from core.protocols.UBECgpi_protocol import create_ubecgpi_service
            
            # Create config for Earth
            earth_config = {
                'asset_code': config.UBECGPI_CODE,
                'issuer': config.UBECGPI_ISSUER,
                'element': 'earth',
                'principle': 'mutualism'
            }
            
            logger.info(f"Creating Earth service with config: {earth_config['asset_code']}")
            
            # Create the service
            service = await create_ubecgpi_service(
                db_manager=db,
                config=earth_config,
                stellar_client=stellar
            )
            
            return service
        
        registry.register_factory(
            'earth',
            create_earth,
            dependencies=['database', 'stellar_client', 'config']
        )
        print("   ✓ Earth protocol registered")
        print()
        
        # Step 3: Initialize Earth protocol
        print("Step 3: Initializing Earth protocol...")
        print()
        
        try:
            earth = await registry.get('earth')
            print(f"   ✓ Earth service created")
            print(f"   Type: {type(earth).__name__}")
            print(f"   Asset code: {earth.asset_code}")
            print(f"   Issuer: {earth.issuer[:10]}...")
            
            # Check initialization state
            is_initialized = getattr(earth, '_initialized', False)
            print(f"   Initialized: {is_initialized}")
            
            if not is_initialized:
                print()
                print("   ⚠ Service created but not initialized")
                print("   This is the issue! Service exists but _initialized = False")
                print()
                
                # Check what would initialize it
                if hasattr(earth, 'initialize'):
                    print("   Attempting manual initialization...")
                    try:
                        await earth.initialize()
                        print("   ✓ Manual initialization succeeded")
                        print(f"   Initialized now: {earth._initialized}")
                    except Exception as init_error:
                        print(f"   ❌ Manual initialization failed: {init_error}")
            
            print()
            
            # Step 4: Run health check
            print("Step 4: Running health check...")
            health = await earth.health_check()
            
            print(f"   Status: {health['status']}")
            print(f"   Message: {health.get('message', 'No message')}")
            
            if health.get('details'):
                details = health['details']
                print(f"\n   Details:")
                print(f"     Database connected: {details.get('database_connected', 'unknown')}")
                print(f"     Stellar connected: {details.get('stellar_connected', 'unknown')}")
                print(f"     Config valid: {details.get('config_valid', 'unknown')}")
                print(f"     Initialized: {details.get('initialized', 'unknown')}")
            
            # Check for issues
            issues = []
            if 'issues' in health:
                issues = health['issues']
            elif health['status'] != 'healthy':
                issues = [health.get('message', 'Unknown issue')]
            
            if issues:
                print(f"\n   ⚠ Issues found ({len(issues)}):")
                for i, issue in enumerate(issues, 1):
                    print(f"     {i}. {issue}")
            
        except Exception as e:
            print(f"   ❌ Failed to initialize Earth: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            import traceback
            print("\n   Full traceback:")
            traceback.print_exc()
            
            return 1
        
        print()
        print("=" * 70)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 70)
        print()
        
        if is_initialized and health['status'] == 'healthy':
            print("✅ Earth protocol is working correctly!")
        elif is_initialized:
            print("⚠ Earth protocol initialized but has health issues")
        else:
            print("❌ Earth protocol NOT initializing")
            print()
            print("SOLUTION NEEDED:")
            print("The Earth protocol factory creates the service but")
            print("the service's _initialized flag remains False.")
            print()
            print("This could be because:")
            print("1. UBECgpiProtocolService.__init__ doesn't set _initialized=True")
            print("2. There's no auto-initialization in the factory")
            print("3. The service requires manual initialization")
        
        # Cleanup
        await registry.shutdown()
        
        print()
        print("=" * 70)
        
        return 0 if is_initialized else 1
        
    except Exception as e:
        print(f"\nâŒ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(full_diagnostic()))
