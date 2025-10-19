#!/usr/bin/env python3
"""
Service Registry Inspection
============================

Shows what services are actually registered in your system.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.service_registry import registry


async def inspect_registry():
    print("="*70)
    print("SERVICE REGISTRY INSPECTION")
    print("="*70)
    print()
    
    # Before initialization
    print("BEFORE initialize_all():")
    print("-" * 70)
    print(f"Registered factories: {registry.list_services()}")
    print()
    
    # Initialize
    print("Initializing registry...")
    await registry.initialize_all()
    print()
    
    # After initialization
    print("AFTER initialize_all():")
    print("-" * 70)
    
    services = registry.list_services()
    print(f"Total services: {len(services)}")
    print()
    
    # Check each service
    for name in sorted(services):
        status = registry.get_status(name)
        is_init = registry.is_initialized(name)
        print(f"{'✅' if is_init else '❌'} {name:20} Status: {status.value:15} Initialized: {is_init}")
    
    print()
    print("-" * 70)
    
    # Check specifically for config
    print()
    print("CRITICAL CHECK:")
    if 'config' in services:
        print("✅ 'config' service IS registered")
        try:
            config = await registry.get('config')
            print(f"✅ Successfully retrieved config service: {type(config)}")
        except Exception as e:
            print(f"❌ ERROR getting config: {e}")
    else:
        print("❌ 'config' service NOT registered!")
        print()
        print("This is the problem! Water protocol factory needs config service.")
        print()
        print("Your main.py should have something like:")
        print("  async def create_config(registry: ServiceRegistry):")
        print("      from config.settings import get_system_config")
        print("      db = await registry.get('database')")
        print("      config_service = await get_system_config(db)")
        print("      from config.config import Config")
        print("      return Config(config_service)")
        print()
        print("  registry.register_factory('config', create_config, dependencies=['database'])")
    
    print()
    print("="*70)
    
    await registry.shutdown()


if __name__ == '__main__':
    asyncio.run(inspect_registry())
