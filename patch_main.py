#!/usr/bin/env python3
"""
Automatic Patcher for main.py shutdown_services Function

This script will:
1. Backup your current main.py
2. Replace the shutdown_services function with the fixed version
3. Preserve all other code

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path


FIXED_SHUTDOWN_FUNCTION = '''async def shutdown_services(services: Dict[str, Any]):
    """
    Gracefully shutdown all services.
    
    Fixed to properly close synchronizer's server AND session.
    """
    logger.info("Shutting down services...")
    
    # Close protocol services first (they may depend on stellar/database)
    protocol_services = ['air', 'water', 'earth', 'fire']
    for protocol_name in protocol_services:
        if services.get(protocol_name):
            try:
                protocol = services[protocol_name]
                if hasattr(protocol, 'close'):
                    await protocol.close()
                    logger.info(f"✓ {protocol_name.capitalize()} protocol closed")
            except Exception as e:
                logger.error(f"Error closing {protocol_name} protocol: {e}")
    
    # Close synchronizer COMPLETELY (not just session!)
    # The synchronizer has BOTH:
    #   - self.session (aiohttp.ClientSession)
    #   - self.server (ServerAsync with its own aiohttp client)
    # We MUST call close() to close both
    if services.get('synchronizer'):
        try:
            sync = services['synchronizer']
            if hasattr(sync, 'close'):
                # This closes BOTH session and server
                await sync.close()
                logger.info("✓ Synchronizer closed (server + session)")
            elif hasattr(sync, 'session') and sync.session and not sync.session.closed:
                # Fallback if close() method doesn't exist (shouldn't happen)
                await sync.session.close()
                logger.warning("⚠️ Synchronizer session closed (server may still be open!)")
        except Exception as e:
            logger.error(f"Error closing synchronizer: {e}")
    
    # Close shared Stellar client (used by protocols)
    if services.get('stellar'):
        try:
            await services['stellar'].close()
            logger.info("✓ Stellar client closed")
        except Exception as e:
            logger.error(f"Error closing Stellar client: {e}")
    
    # Close database connection last (other services may need it)
    if services.get('database'):
        try:
            await services['database'].close()
            logger.info("✓ Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    logger.info("✓ All services shut down")'''


def find_main_py():
    """Find main.py in common locations"""
    possible_paths = [
        'main.py',
        './main.py',
        '../main.py',
        '~/UBEC/projects/UBEC/main.py',
    ]
    
    for path in possible_paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            return expanded
    
    return None


def backup_file(filepath):
    """Create a backup of the file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    
    return backup_path


def patch_main_py(filepath):
    """Patch the main.py file with the fixed shutdown function"""
    
    # Read current content
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the shutdown_services function using regex
    # Match from "async def shutdown_services" to the next function or EOF
    pattern = r'async def shutdown_services\(services: Dict\[str, Any\]\):.*?(?=\n\nasync def |\n\ndef |\n\n# =|$)'
    
    # Check if function exists
    if not re.search(pattern, content, re.DOTALL):
        print("❌ Could not find shutdown_services function in main.py")
        print("   The function signature might be different than expected.")
        return False
    
    # Replace the function
    new_content = re.sub(pattern, FIXED_SHUTDOWN_FUNCTION, content, flags=re.DOTALL)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True


def main():
    print("=" * 70)
    print("UBEC main.py Patcher - Fix aiohttp Session Leak")
    print("=" * 70)
    print()
    
    # Find main.py
    print("🔍 Searching for main.py...")
    main_py_path = find_main_py()
    
    if not main_py_path:
        print("❌ Could not find main.py")
        print("   Please run this script from your UBEC project directory,")
        print("   or specify the path as an argument:")
        print(f"   python {sys.argv[0]} /path/to/main.py")
        return 1
    
    # Allow path as argument
    if len(sys.argv) > 1:
        main_py_path = sys.argv[1]
        if not os.path.exists(main_py_path):
            print(f"❌ File not found: {main_py_path}")
            return 1
    
    print(f"✓ Found: {main_py_path}")
    print()
    
    # Confirm with user
    response = input("Do you want to patch this file? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Patch cancelled.")
        return 0
    
    print()
    print("📦 Creating backup...")
    backup_path = backup_file(main_py_path)
    print(f"✓ Backup created: {backup_path}")
    print()
    
    print("🔧 Applying patch...")
    success = patch_main_py(main_py_path)
    
    if success:
        print("✓ Patch applied successfully!")
        print()
        print("=" * 70)
        print("Next Steps:")
        print("=" * 70)
        print("1. Test the fix:")
        print("   python main.py --mode health")
        print()
        print("2. Look for clean shutdown (no asyncio errors)")
        print()
        print("3. If something goes wrong, restore from backup:")
        print(f"   cp {backup_path} {main_py_path}")
        print("=" * 70)
        return 0
    else:
        print("❌ Patch failed!")
        print()
        print("You can manually apply the fix by:")
        print("1. Opening main.py")
        print("2. Finding the shutdown_services function")
        print("3. Replacing it with the version in fixed_shutdown_services.py")
        return 1


if __name__ == '__main__':
    sys.exit(main())
