#!/usr/bin/env python3
"""Test to verify factory signature"""
import sys
import inspect
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path.cwd()))

try:
    from core.protocols.UBECgpi_protocol import create_ubecgpi_service
    
    print("Factory signature test:")
    print(f"  Function: {create_ubecgpi_service.__name__}")
    print(f"  Is coroutine: {inspect.iscoroutinefunction(create_ubecgpi_service)}")
    print(f"  Signature: {inspect.signature(create_ubecgpi_service)}")
    
    if inspect.iscoroutinefunction(create_ubecgpi_service):
        print("\n✓ Factory IS async - use: service = await create_ubecgpi_service(...)")
    else:
        print("\n✓ Factory is sync - use: service = create_ubecgpi_service(...)")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
