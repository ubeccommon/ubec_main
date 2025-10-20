#!/usr/bin/env python3
"""
Health Check Diagnostic Tool
=============================

This script helps diagnose why services are showing as unhealthy or unknown
by testing each service's health_check() method individually and showing
detailed error information.

Usage:
    python diagnose_health.py

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import asyncio
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import registry
from core.service_registry import registry


async def test_service_health(service_name: str):
    """Test a single service's health check with detailed error reporting."""
    print(f"\n{'='*70}")
    print(f"Testing: {service_name}")
    print(f"{'='*70}")
    
    try:
        # Get the service
        print(f"  → Getting service from registry...")
        service = await registry.get(service_name)
        print(f"  ✓ Service retrieved: {type(service).__name__}")
        
        # Check if service has health_check method
        if not hasattr(service, 'health_check'):
            print(f"  ✗ No health_check() method found")
            print(f"    Service type: {type(service)}")
            print(f"    Available methods: {[m for m in dir(service) if not m.startswith('_')]}")
            return {'status': 'unknown', 'reason': 'no_health_check_method'}
        
        print(f"  ✓ health_check() method exists")
        
        # Call health check
        print(f"  → Calling health_check()...")
        health = await service.health_check()
        print(f"  ✓ health_check() completed")
        print(f"\n  Status: {health.get('status', 'MISSING')}")
        print(f"  Message: {health.get('message', 'MISSING')}")
        
        if 'details' in health:
            print(f"\n  Details:")
            for key, value in health['details'].items():
                if isinstance(value, dict):
                    print(f"    {key}:")
                    for k, v in value.items():
                        print(f"      {k}: {v}")
                else:
                    print(f"    {key}: {value}")
        
        if 'action' in health:
            print(f"\n  Action: {health['action']}")
        
        return health
        
    except Exception as e:
        print(f"  ✗ ERROR: {type(e).__name__}: {str(e)}")
        print(f"\n  Traceback:")
        import traceback
        traceback.print_exc()
        return {
            'status': 'unhealthy',
            'error': str(e),
            'error_type': type(e).__name__
        }


async def diagnose_all():
    """Run diagnostic on all problematic services."""
    print("\n" + "="*70)
    print("UBEC HEALTH CHECK DIAGNOSTIC TOOL")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Services to test
    problematic_services = [
        'distribution',
        'holonic_evaluator',
        'visualizer'
    ]
    
    # Also test a working service for comparison
    working_services = [
        'analytics',
        'synchronizer'
    ]
    
    results = {}
    
    # Test problematic services
    print("\n\n" + "="*70)
    print("TESTING PROBLEMATIC SERVICES")
    print("="*70)
    
    for service_name in problematic_services:
        results[service_name] = await test_service_health(service_name)
    
    # Test working services for comparison
    print("\n\n" + "="*70)
    print("TESTING WORKING SERVICES (for comparison)")
    print("="*70)
    
    for service_name in working_services:
        results[service_name] = await test_service_health(service_name)
    
    # Summary
    print("\n\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    for service_name, health in results.items():
        status = health.get('status', 'UNKNOWN')
        
        if status == 'healthy':
            symbol = "✓"
        elif status in ['needs_sync', 'degraded']:
            symbol = "⚠"
        else:
            symbol = "✗"
        
        print(f"\n{symbol} {service_name}: {status}")
        
        if 'error' in health:
            print(f"  Error: {health['error_type']}: {health['error']}")
        elif 'message' in health:
            print(f"  Message: {health['message']}")
        
        if 'reason' in health:
            print(f"  Reason: {health['reason']}")
    
    # Recommendations
    print("\n\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    for service_name, health in results.items():
        if health.get('status') in ['unhealthy', 'unknown']:
            print(f"\n{service_name}:")
            
            if health.get('reason') == 'no_health_check_method':
                print(f"  → Service needs health_check() method implementation")
                print(f"     Add: async def health_check(self) -> Dict[str, Any]")
            
            elif 'error' in health:
                error = health['error']
                error_type = health.get('error_type', '')
                
                if 'AttributeError' in error_type:
                    print(f"  → Missing attribute or method")
                    print(f"     Check: {error}")
                
                elif 'RuntimeError' in error_type or 'not initialized' in error.lower():
                    print(f"  → Service not properly initialized")
                    print(f"     Check factory function calls initialize()")
                
                elif 'database' in error.lower() or 'connection' in error.lower():
                    print(f"  → Database connectivity issue")
                    print(f"     Check database connection and credentials")
                
                else:
                    print(f"  → Error in health_check() implementation")
                    print(f"     Review the health_check() method code")
                    print(f"     Error details: {error}")


async def main():
    """Main entry point."""
    try:
        # Register services
        print("Registering services...")
        from main import register_core_services
        register_core_services()
        print("✓ Services registered\n")
        
        # Run diagnostics within registry context
        async with registry:
            await diagnose_all()
        
        print("\n" + "="*70)
        print("DIAGNOSTIC COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
