#!/usr/bin/env python3
"""
Add Status Mode to main.py
===========================
This script automatically adds the status mode implementation to main.py

Usage:
    python add_status_mode.py
"""

import os
import sys
from pathlib import Path


STATUS_FUNCTION = '''
async def run_status() -> Dict[str, Any]:
    """
    Get comprehensive system status including service states and metrics.
    
    Returns detailed information about:
    - Service initialization states
    - Database connectivity
    - Configuration status
    - Element protocol states
    - Recent operation metrics
    
    This is lighter weight than health check and focuses on current state.
    """
    logger.info("Gathering system status...")
    
    status = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'system': {
            'name': 'UBEC Protocol Suite',
            'version': '7.1.0',
            'python_version': sys.version.split()[0],
            'services_registered': len(registry._services),
        },
        'services': {},
        'database': {},
        'protocols': {},
        'summary': {}
    }
    
    try:
        # Get service registry status
        service_states = {}
        for name in registry._services.keys():
            try:
                service = await registry.get(name)
                service_states[name] = {
                    'registered': True,
                    'initialized': getattr(service, '_initialized', True),
                    'type': type(service).__name__
                }
            except Exception as e:
                service_states[name] = {
                    'registered': True,
                    'initialized': False,
                    'error': str(e)
                }
        
        status['services'] = service_states
        
        # Database status
        try:
            db = await registry.get('database')
            if db:
                # Test connection
                test_query = "SELECT 1 as test"
                result = await db.fetch_one(test_query, ())
                status['database'] = {
                    'connected': result is not None,
                    'pool_size': f"{db.pool_min_size}-{db.pool_max_size}",
                    'schemas': db.search_path if hasattr(db, 'search_path') else 'unknown'
                }
        except Exception as e:
            status['database'] = {
                'connected': False,
                'error': str(e)
            }
        
        # Protocol status (element protocols)
        protocol_names = ['air', 'water', 'earth', 'fire']
        for proto_name in protocol_names:
            try:
                proto = await registry.get(proto_name)
                if proto:
                    status['protocols'][proto_name] = {
                        'element': getattr(proto, 'element_type', 'unknown'),
                        'asset_code': getattr(proto, 'asset_code', 'unknown'),
                        'initialized': getattr(proto, '_initialized', False),
                        'sync_count': getattr(proto, '_sync_count', 0),
                        'error_count': getattr(proto, '_error_count', 0)
                    }
            except Exception as e:
                status['protocols'][proto_name] = {
                    'available': False,
                    'error': str(e)
                }
        
        # Summary
        total_services = len(service_states)
        initialized_services = sum(1 for s in service_states.values() if s.get('initialized'))
        
        status['summary'] = {
            'total_services': total_services,
            'initialized_services': initialized_services,
            'database_connected': status['database'].get('connected', False),
            'protocols_available': len([p for p in status['protocols'].values() if p.get('initialized')]),
            'status': 'operational' if initialized_services == total_services else 'partial'
        }
        
        logger.info(f"✓ Status gathered: {initialized_services}/{total_services} services initialized")
        
    except Exception as e:
        logger.error(f"Error gathering status: {e}", exc_info=True)
        status['success'] = False
        status['error'] = str(e)
    
    return status

'''


MODE_HANDLER = '''            elif args.mode == 'status':
                result = await run_status()
            
'''


def add_status_mode():
    """Add status mode to main.py"""
    
    print("=" * 70)
    print("Adding Status Mode to main.py")
    print("=" * 70)
    print()
    
    # Find main.py
    main_path = Path('main.py')
    if not main_path.exists():
        print("❌ main.py not found in current directory")
        print("   Make sure you're in ~/UBEC/projects/UBEC")
        return 1
    
    # Backup
    backup_path = Path('main.py.status_backup')
    print(f"Creating backup: {backup_path}")
    with open(main_path, 'r') as f:
        content = f.read()
    with open(backup_path, 'w') as f:
        f.write(content)
    print("✓ Backup created")
    print()
    
    lines = content.split('\n')
    
    # Find insertion points
    function_insert_line = None
    handler_insert_line = None
    
    for i, line in enumerate(lines):
        # Find where to insert the function (after run_health_check)
        if 'async def run_sync(' in line and function_insert_line is None:
            function_insert_line = i
        
        # Find where to insert mode handler (after 'elif args.mode == "sync"')
        if "elif args.mode == 'sync':" in line and handler_insert_line is None:
            # Find the next elif or else
            for j in range(i+1, min(i+20, len(lines))):
                if 'else:' in lines[j] or 'elif' in lines[j]:
                    handler_insert_line = j
                    break
    
    if function_insert_line is None:
        print("❌ Could not find insertion point for function")
        return 1
    
    if handler_insert_line is None:
        print("❌ Could not find insertion point for handler")
        return 1
    
    print(f"Function will be inserted at line {function_insert_line}")
    print(f"Handler will be inserted at line {handler_insert_line}")
    print()
    
    # Insert function
    function_lines = STATUS_FUNCTION.strip().split('\n')
    lines = lines[:function_insert_line] + function_lines + [''] + lines[function_insert_line:]
    
    # Adjust handler line number (it shifted)
    handler_insert_line += len(function_lines) + 1
    
    # Insert handler
    handler_lines = MODE_HANDLER.strip().split('\n')
    lines = lines[:handler_insert_line] + handler_lines + lines[handler_insert_line:]
    
    # Write updated file
    print("Writing updated main.py...")
    new_content = '\n'.join(lines)
    with open(main_path, 'w') as f:
        f.write(new_content)
    
    print("✓ main.py updated")
    print()
    
    # Verify
    print("Verifying changes...")
    with open(main_path, 'r') as f:
        verify_content = f.read()
    
    if 'async def run_status()' in verify_content:
        print("✓ run_status() function added")
    else:
        print("❌ run_status() function not found")
        return 1
    
    if "args.mode == 'status'" in verify_content:
        print("✓ Status mode handler added")
    else:
        print("❌ Status mode handler not found")
        return 1
    
    print()
    print("=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print()
    print("Status mode has been added to main.py")
    print()
    print("Test it:")
    print("  python main.py --mode status")
    print()
    print("If something goes wrong, restore from backup:")
    print("  cp main.py.status_backup main.py")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(add_status_mode())
