#!/usr/bin/env python3
"""
Add Complete Status Mode
=========================
Adds BOTH the function AND the handler.

Usage: python add_complete_status_mode.py
"""

import sys
from pathlib import Path

# The complete function to add
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


def add_complete_status_mode():
    """Add both function and handler."""
    
    print("=" * 70)
    print("Adding Complete Status Mode")
    print("=" * 70)
    print()
    
    main_path = Path('main.py')
    if not main_path.exists():
        print("❌ main.py not found")
        return 1
    
    # Backup
    backup_path = Path('main.py.complete_backup')
    print(f"Creating backup: {backup_path}")
    with open(main_path, 'r') as f:
        content = f.read()
    with open(backup_path, 'w') as f:
        f.write(content)
    print("✓ Backup created")
    print()
    
    lines = content.split('\n')
    
    # Check if function already exists
    has_function = any('async def run_status()' in line for line in lines)
    
    if has_function:
        print("✓ Function already exists")
    else:
        print("Adding run_status() function...")
        
        # Find where to add function (before run_sync)
        func_insert = None
        for i, line in enumerate(lines):
            if 'async def run_sync(' in line:
                func_insert = i
                break
        
        if func_insert is None:
            print("❌ Could not find insertion point for function")
            return 1
        
        # Insert function
        func_lines = STATUS_FUNCTION.strip().split('\n')
        lines = lines[:func_insert] + func_lines + [''] + lines[func_insert:]
        print(f"✓ Function added before line {func_insert + 1}")
    
    # Now add/fix handler
    print()
    print("Adding/fixing status mode handler...")
    
    # Find sync mode handler
    sync_line = None
    for i, line in enumerate(lines):
        if "elif args.mode == 'sync':" in line:
            sync_line = i
            break
    
    if sync_line is None:
        print("❌ Could not find sync mode handler")
        return 1
    
    print(f"Found sync mode at line {sync_line + 1}")
    
    # Get indentation
    indent = len(lines[sync_line]) - len(lines[sync_line].lstrip())
    indent_str = ' ' * indent
    
    # Find insertion point (after the result = await run_sync line)
    insert_line = sync_line + 1
    while insert_line < len(lines) and 'await run_sync' not in lines[insert_line]:
        insert_line += 1
    insert_line += 1
    
    # Skip empty lines
    while insert_line < len(lines) and lines[insert_line].strip() == '':
        insert_line += 1
    
    # Remove existing status handler if present
    for i in range(max(0, insert_line - 3), min(len(lines), insert_line + 10)):
        if "args.mode == 'status'" in lines[i]:
            print(f"Removing old status handler at line {i + 1}")
            lines.pop(i)
            if i < len(lines) and 'run_status()' in lines[i]:
                lines.pop(i)
            break
    
    # Add new handler
    new_handler = [
        f"{indent_str}elif args.mode == 'status':",
        f"{indent_str}    result = await run_status()",
        ""
    ]
    
    for i, line in enumerate(new_handler):
        lines.insert(insert_line + i, line)
    
    print(f"✓ Handler added at line {insert_line + 1}")
    print()
    
    # Write file
    print("Writing main.py...")
    new_content = '\n'.join(lines)
    with open(main_path, 'w') as f:
        f.write(new_content)
    print("✓ File written")
    print()
    
    # Verify
    print("Verifying...")
    import subprocess
    
    # Check syntax
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'main.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Syntax error:")
        print(result.stderr)
        print()
        print("Restoring backup...")
        subprocess.run(['cp', str(backup_path), 'main.py'])
        return 1
    
    print("✓ Syntax valid")
    
    # Check function exists
    if 'async def run_status()' in new_content:
        print("✓ Function present")
    else:
        print("❌ Function missing")
        return 1
    
    # Check handler exists
    if "args.mode == 'status'" in new_content:
        print("✓ Handler present")
    else:
        print("❌ Handler missing")
        return 1
    
    print()
    print("=" * 70)
    print("SUCCESS! Status mode is now complete!")
    print("=" * 70)
    print()
    print("Test it:")
    print("  python main.py --mode status")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(add_complete_status_mode())
