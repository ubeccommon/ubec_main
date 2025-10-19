#!/usr/bin/env python3
"""
Water Protocol Initialization Diagnostics
==========================================

This script tests the water protocol initialization to identify the exact failure point.

Run this to diagnose why water protocol shows "initialized": false.

Usage:
    python diagnose_water_protocol.py
    
Attribution:
    This project uses the services of Claude and Anthropic PBC.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.protocols.UBECrc_protocol import create_ubecrc_service, UBECrcProtocolService


async def test_water_protocol():
    """Test water protocol creation and initialization."""
    
    print("="*70)
    print("WATER PROTOCOL INITIALIZATION DIAGNOSTICS")
    print("="*70)
    print()
    
    # Test 1: Check if service class has initialize method
    print("Test 1: Checking if UBECrcProtocolService has initialize() method...")
    if hasattr(UBECrcProtocolService, 'initialize'):
        print("✅ PASS: initialize() method exists")
        print(f"   Method is async: {asyncio.iscoroutinefunction(UBECrcProtocolService.initialize)}")
    else:
        print("❌ FAIL: initialize() method missing!")
        print("   This is the root cause - service registry can't initialize it")
        return
    print()
    
    # Test 2: Check required element metadata properties
    print("Test 2: Checking element metadata properties...")
    required_properties = ['element', 'ubuntu_principle', 'element_description', 'symbol']
    
    # Create mock config for testing with CORRECT UBECrc issuer
    mock_config = {
        'asset_code': 'UBECrc',
        'issuer': 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC',  # Correct 56-char issuer
        'db_schema': 'ubec_main'
    }
    
    print(f"   Creating test instance with config: {mock_config}")
    
    # Create instance without db_manager (will fail, but we can check properties)
    try:
        # Mock database manager
        class MockDB:
            async def execute(self, query):
                return True
        
        service = UBECrcProtocolService(
            db_manager=MockDB(),
            config=mock_config,
            stellar_client=None
        )
        
        print("✅ PASS: Service instance created")
        
        # Check properties
        for prop in required_properties:
            value = getattr(service, prop, "MISSING")
            status = "✅" if value != "MISSING" and value != "unknown" else "❌"
            print(f"   {status} {prop}: {value}")
        
        print()
        print("Test 3: Checking initialization state...")
        print(f"   _initialized (before): {service._initialized}")
        
        if service._initialized:
            print("   ❌ FAIL: _initialized should be False before calling initialize()")
            print("   This was the bug in v3.0.0 - it was set to True in constructor!")
        else:
            print("   ✅ PASS: _initialized is False (correct)")
        
        # Test initialize method
        print()
        print("Test 4: Testing initialize() method...")
        try:
            await service.initialize()
            print(f"   ✅ PASS: initialize() completed successfully")
            print(f"   _initialized (after): {service._initialized}")
            
            if service._initialized:
                print("   ✅ PASS: _initialized is now True")
            else:
                print("   ❌ FAIL: _initialized still False after initialize()")
                
        except Exception as e:
            print(f"   ❌ FAIL: initialize() threw exception: {e}")
            print(f"   Exception type: {type(e).__name__}")
            import traceback
            print("   Traceback:")
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ FAIL: Could not create service instance")
        print(f"   Error: {e}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        print("   Traceback:")
        traceback.print_exc()
    
    print()
    print("="*70)
    print("DIAGNOSTICS COMPLETE")
    print("="*70)
    
    print()
    print("Summary:")
    print("--------")
    print("If all tests passed:")
    print("  → Water protocol v3.1.0 is correctly implemented")
    print("  → Service registry will properly initialize it")
    print("  → Status output will show initialized: true")
    print()
    print("If tests failed:")
    print("  → Check error messages above")
    print("  → Verify you're using the v3.1.0 updated file")
    print("  → Ensure all required properties are set in __init__")
    print()


if __name__ == '__main__':
    asyncio.run(test_water_protocol())
