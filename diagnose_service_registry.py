#!/usr/bin/env python3
"""
Diagnostic script to check service registry state
Run this to see what's being returned by registry.get('distribution')
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.service_registry import ServiceRegistry
from main import register_core_services

async def diagnose():
    print("=" * 70)
    print("SERVICE REGISTRY DIAGNOSTIC")
    print("=" * 70)
    
    # Register services
    registry = register_core_services()
    
    print("\n1. Checking registered services...")
    services = registry.list_services()
    print(f"   Total registered: {len(services)}")
    print(f"   Distribution registered: {'distribution' in services}")
    
    print("\n2. Checking service initialization status...")
    is_init = registry.is_initialized('distribution')
    print(f"   Distribution initialized: {is_init}")
    
    print("\n3. Attempting to get distribution service...")
    try:
        async with registry:
            distribution = await registry.get('distribution')
            print(f"   Type: {type(distribution)}")
            print(f"   Is callable: {callable(distribution)}")
            print(f"   Has check_compliance: {hasattr(distribution, 'check_compliance')}")
            
            if hasattr(distribution, '__class__'):
                print(f"   Class name: {distribution.__class__.__name__}")
            
            if hasattr(distribution, '__dict__'):
                print(f"   Attributes: {list(distribution.__dict__.keys())[:10]}")
            
            # Try to call check_compliance
            if hasattr(distribution, 'check_compliance'):
                print("\n4. Testing check_compliance method...")
                result = await distribution.check_compliance()
                print(f"   Success! Got result keys: {list(result.keys())}")
            else:
                print("\n4. ERROR: check_compliance method not found")
                print(f"   This object appears to be: {distribution}")
                
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(diagnose())
