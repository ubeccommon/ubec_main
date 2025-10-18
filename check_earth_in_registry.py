#!/usr/bin/env python3
"""
Earth Protocol Registry Diagnostic
==================================
Uses the actual service registry to diagnose Earth initialization.

Usage: python check_earth_in_registry.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def check_earth_protocol():
    """Check Earth protocol using the actual registry."""
    
    print("=" * 70)
    print("EARTH PROTOCOL REGISTRY DIAGNOSTIC")
    print("=" * 70)
    print()
    
    try:
        # Import registry
        from core.service_registry import registry
        
        # Initialize core services (just database and config)
        print("1. Initializing core services (database, config)...")
        
        # Initialize database
        db = await registry.get('database')
        print(f"   ✓ Database initialized")
        
        # Initialize config
        config = await registry.get('config')
        print(f"   ✓ Config initialized")
        print()
        
        # Check config for Earth
        print("2. Checking Earth (UBECgpi) configuration...")
        if hasattr(config, 'UBECGPI_CODE'):
            print(f"   ✓ UBECGPI_CODE: {config.UBECGPI_CODE}")
        else:
            print(f"   ❌ UBECGPI_CODE not found")
        
        if hasattr(config, 'UBECGPI_ISSUER'):
            print(f"   ✓ UBECGPI_ISSUER: {config.UBECGPI_ISSUER[:10]}...")
        else:
            print(f"   ❌ UBECGPI_ISSUER not found")
        print()
        
        # Try to get Earth service
        print("3. Attempting to get Earth service from registry...")
        try:
            earth = await registry.get('earth')
            print(f"   ✓ Earth service retrieved")
            print(f"   ✓ Type: {type(earth).__name__}")
            print(f"   ✓ Initialized: {getattr(earth, '_initialized', 'unknown')}")
            print()
            
            # Try health check
            print("4. Running Earth protocol health check...")
            health = await earth.health_check()
            print(f"   Status: {health.get('status')}")
            print(f"   Message: {health.get('message', 'No message')}")
            
            if health.get('details'):
                details = health['details']
                print(f"   Database connected: {details.get('database_connected')}")
                print(f"   Stellar connected: {details.get('stellar_connected')}")
                print(f"   Config valid: {details.get('config_valid')}")
                
                # Check for issues
                if health.get('issues'):
                    print()
                    print("   Issues found:")
                    for issue in health['issues']:
                        print(f"     - {issue}")
            
        except Exception as e:
            print(f"   ❌ Failed to get Earth service: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Try to get more details
            import traceback
            print("\n   Full traceback:")
            traceback.print_exc()
        
        print()
        print("=" * 70)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(check_earth_protocol()))
