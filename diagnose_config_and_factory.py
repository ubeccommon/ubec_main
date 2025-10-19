#!/usr/bin/env python3
"""
Config Service & Water Protocol Factory Diagnostics
====================================================

This script tests what the config service returns for UBECrc issuer
and simulates the exact factory call from main.py.

Run this to diagnose why water protocol shows "unknown" values.

Usage:
    python diagnose_config_and_factory.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.service_registry import registry


async def test_config_service():
    """Test what the config service returns."""
    
    print("="*70)
    print("CONFIG SERVICE & WATER FACTORY DIAGNOSTICS")
    print("="*70)
    print()
    
    try:
        # Initialize the service registry (this loads everything)
        print("Step 1: Initializing service registry...")
        await registry.initialize_all()
        print("✅ Registry initialized")
        print()
        
        # Get the config service
        print("Step 2: Getting config service...")
        config = await registry.get('config')
        print("✅ Config service retrieved")
        print()
        
        # Check what config returns for each issuer
        print("Step 3: Checking issuer values from config service...")
        print("-" * 70)
        
        issuers = {
            'UBEC (Air)': 'UBEC_ISSUER',
            'UBECrc (Water)': 'UBECRC_ISSUER',
            'UBECgpi (Earth)': 'UBECGPI_ISSUER',
            'UBECtt (Fire)': 'UBECTT_ISSUER'
        }
        
        for name, attr in issuers.items():
            try:
                value = getattr(config, attr)
                length = len(value) if value else 0
                
                if not value:
                    status = "❌ EMPTY/NONE"
                elif length != 56:
                    status = f"❌ INVALID LENGTH ({length})"
                elif not value.startswith('G'):
                    status = "❌ DOESN'T START WITH G"
                else:
                    status = "✅ VALID"
                
                print(f"{name:20} {attr:20}")
                print(f"  Value: {value if value else '(empty)'}")
                print(f"  Status: {status}")
                print()
                
            except AttributeError as e:
                print(f"{name:20} {attr:20}")
                print(f"  ❌ ERROR: Attribute not found - {e}")
                print()
        
        print("-" * 70)
        print()
        
        # Check database directly
        print("Step 4: Checking database system_settings directly...")
        print("-" * 70)
        
        db = await registry.get('database')
        
        query = """
            SELECT setting_key, setting_value, LENGTH(setting_value) as len, is_active
            FROM ubec_main.system_settings
            WHERE setting_key LIKE '%_issuer'
            ORDER BY setting_key
        """
        
        results = await db.fetch_all(query)
        
        if results:
            for row in results:
                key = row['setting_key']
                value = row['setting_value']
                length = row['len']
                active = row['is_active']
                
                status = "✅" if length == 56 and value.startswith('G') and active else "❌"
                active_str = "✅ active" if active else "❌ inactive"
                
                print(f"{status} {key}")
                print(f"   Value: {value}")
                print(f"   Length: {length} chars")
                print(f"   Active: {active_str}")
                print()
        else:
            print("❌ NO ISSUER SETTINGS FOUND IN DATABASE!")
            print()
        
        print("-" * 70)
        print()
        
        # Simulate the exact factory call from main.py
        print("Step 5: Simulating water protocol factory call...")
        print("-" * 70)
        
        try:
            from core.protocols.UBECrc_protocol import create_ubecrc_service
            
            db = await registry.get('database')
            config = await registry.get('config')
            stellar = await registry.get('stellar_client')
            
            # This is the EXACT config dict that main.py creates
            protocol_config = {
                'asset_code': 'UBECrc',
                'issuer': config.UBECRC_ISSUER  # This is what main.py does!
            }
            
            print(f"Protocol config created:")
            print(f"  asset_code: {protocol_config['asset_code']}")
            print(f"  issuer: {protocol_config['issuer']}")
            print(f"  issuer length: {len(protocol_config['issuer']) if protocol_config['issuer'] else 0}")
            print()
            
            if not protocol_config['issuer']:
                print("❌ PROBLEM FOUND!")
                print("   config.UBECRC_ISSUER is returning empty string!")
                print("   This is why water protocol shows 'unknown' values")
                print()
                print("   FIX: Add ubecrc_issuer to database:")
                print("   INSERT INTO ubec_main.system_settings (setting_key, setting_value, category, is_active)")
                print("   VALUES ('ubecrc_issuer', 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC', 'ASSET_CONFIGURATION', true);")
                print()
                return
            
            # Try to create the service
            print("Creating service instance...")
            service = await create_ubecrc_service(db, protocol_config, stellar)
            print("✅ Service created successfully")
            print()
            
            # Check if initialize() will be called
            print("Checking if service has initialize() method...")
            if hasattr(service, 'initialize'):
                print("✅ Service has initialize() method")
                print()
                
                # Try to initialize
                print("Calling initialize()...")
                await service.initialize()
                print("✅ Service initialized successfully")
                print()
                
                # Check final state
                print("Final service state:")
                print(f"  _initialized: {service._initialized}")
                print(f"  asset_code: {service.asset_code}")
                print(f"  issuer: {service.issuer}")
                print(f"  element: {service.element}")
                print(f"  ubuntu_principle: {service.ubuntu_principle}")
                print(f"  symbol: {service.symbol}")
                print()
                
                if service._initialized:
                    print("✅ SUCCESS! Water protocol would work in main.py")
                else:
                    print("❌ FAILURE! Something went wrong during initialization")
            else:
                print("❌ Service missing initialize() method!")
                
        except Exception as e:
            print(f"❌ ERROR creating/initializing service: {e}")
            print(f"   Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
        
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await registry.shutdown()
    
    print()
    print("="*70)
    print("DIAGNOSTICS COMPLETE")
    print("="*70)


if __name__ == '__main__':
    asyncio.run(test_config_service())
