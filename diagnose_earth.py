#!/usr/bin/env python3
"""
Diagnose Earth Protocol Initialization Issue
============================================
Checks why the Earth (UBECgpi) protocol is not initializing.

Usage: python diagnose_earth.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def diagnose_earth():
    """Diagnose Earth protocol initialization."""
    
    print("=" * 70)
    print("EARTH PROTOCOL INITIALIZATION DIAGNOSTIC")
    print("=" * 70)
    print()
    
    issues = []
    
    # Check 1: Module exists
    print("1. Checking if UBECgpi protocol module exists...")
    earth_module_path = project_root / 'core' / 'protocols' / 'UBECgpi_protocol.py'
    if earth_module_path.exists():
        print(f"   ✓ Module found: {earth_module_path}")
    else:
        print(f"   ❌ Module NOT found: {earth_module_path}")
        issues.append("Module file missing")
    print()
    
    # Check 2: Can import module
    print("2. Checking if module can be imported...")
    try:
        from core.protocols import UBECgpi_protocol
        print("   ✓ Module imported successfully")
        
        # Check for factory function
        if hasattr(UBECgpi_protocol, 'create_ubecgpi_service'):
            print("   ✓ Factory function 'create_ubecgpi_service' exists")
        else:
            print("   ❌ Factory function 'create_ubecgpi_service' NOT found")
            issues.append("Factory function missing or misnamed")
            
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        issues.append(f"Import error: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        issues.append(f"Module error: {e}")
    print()
    
    # Check 3: Config values
    print("3. Checking configuration values...")
    try:
        from config.settings import get_system_config
        from core.db.database_manager import AsyncDatabaseManager
        
        # Create temp DB connection
        db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema='ubec_main, phenomenal, topology, public',
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        await db.initialize()
        config = await get_system_config(db)
        
        # Check Earth-specific config
        if hasattr(config, 'UBECGPI_CODE'):
            print(f"   ✓ UBECGPI_CODE: {config.UBECGPI_CODE}")
        else:
            print("   ❌ UBECGPI_CODE not found in config")
            issues.append("UBECGPI_CODE missing")
        
        if hasattr(config, 'UBECGPI_ISSUER'):
            print(f"   ✓ UBECGPI_ISSUER: {config.UBECGPI_ISSUER[:10]}...")
        else:
            print("   ❌ UBECGPI_ISSUER not found in config")
            issues.append("UBECGPI_ISSUER missing")
        
        await db.close()
        
    except Exception as e:
        print(f"   ❌ Config check failed: {e}")
        issues.append(f"Config error: {e}")
    print()
    
    # Check 4: Try to create service directly
    print("4. Attempting direct service creation...")
    try:
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        from core.db.database_manager import AsyncDatabaseManager
        from stellar_sdk import ServerAsync
        from config.settings import get_system_config
        
        # Create dependencies
        db = AsyncDatabaseManager(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'ubec'),
            schema='ubec_main, phenomenal, topology, public',
            user=os.getenv('DB_USER', 'ubec_app'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        await db.initialize()
        config = await get_system_config(db)
        stellar = ServerAsync(horizon_url=config.HORIZON_URL)
        
        # Try to create service
        service_config = {
            'asset_code': config.UBECGPI_CODE,
            'issuer': config.UBECGPI_ISSUER,
            'element': 'earth',
            'principle': 'mutualism'
        }
        
        service = await create_ubecgpi_service(
            db_manager=db,
            config=service_config,
            stellar_client=stellar
        )
        
        print("   ✓ Service created successfully")
        print(f"   ✓ Service type: {type(service).__name__}")
        print(f"   ✓ Service initialized: {getattr(service, '_initialized', False)}")
        
        # Try health check
        health = await service.health_check()
        print(f"   ✓ Health check: {health['status']}")
        
        await stellar.close()
        await db.close()
        
    except Exception as e:
        print(f"   ❌ Service creation failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print("\n   Full traceback:")
        traceback.print_exc()
        issues.append(f"Service creation error: {e}")
    print()
    
    # Summary
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print()
    
    if not issues:
        print("✅ NO ISSUES FOUND")
        print()
        print("Earth protocol should be working. The initialization failure")
        print("might be happening in the service registry or during the")
        print("specific initialization sequence in main.py.")
        print()
        print("Recommendation: Check main.py service registration for 'earth'")
    else:
        print(f"❌ FOUND {len(issues)} ISSUE(S):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print()
        print("These issues must be resolved for Earth protocol to initialize.")
    
    print("=" * 70)


if __name__ == '__main__':
    try:
        asyncio.run(diagnose_earth())
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
