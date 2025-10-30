#!/usr/bin/env python3
"""
UBEC Protocol - Health Check System Fix Script

This script fixes the critical bug in main.py where health checks are not
actually running due to incorrect method name.

Bug: main.py checks for 'get_health()' but services implement 'health_check()'
Fix: Update main.py to use correct method name

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

def create_backup(file_path):
    """Create timestamped backup of file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    with open(file_path, 'r') as source:
        with open(backup_path, 'w') as dest:
            dest.write(source.read())
    
    print(f"✓ Backup created: {backup_path}")
    return backup_path

def fix_health_check_method_names(file_path):
    """Fix health check method names in main.py."""
    
    print("\nAnalyzing main.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Fix 1: hasattr check
    if "hasattr(service, 'get_health')" in content:
        content = content.replace(
            "hasattr(service, 'get_health')",
            "hasattr(service, 'health_check')"
        )
        changes_made.append("✓ Fixed: hasattr check now uses 'health_check'")
    
    # Fix 2: method call
    if "await service.get_health()" in content:
        content = content.replace(
            "await service.get_health()",
            "await service.health_check()"
        )
        changes_made.append("✓ Fixed: Method call now uses 'health_check()'")
    
    # Fix 3: health status check
    pattern1 = r"health\.get\('healthy',\s*False\)"
    pattern2 = r"health\.get\(['\"]healthy['\"]\s*,\s*False\)"
    
    if re.search(pattern1, content) or re.search(pattern2, content):
        content = re.sub(pattern1, "health.get('status') == 'healthy'", content)
        content = re.sub(pattern2, "health.get('status') == 'healthy'", content)
        changes_made.append("✓ Fixed: Health status check now uses 'status' key")
    
    # Fix 4: Fallback response structure
    fallback_old = """'healthy': True,
                'message': 'Health check not implemented'"""
    
    fallback_new = """'status': 'unknown',
                'message': 'Health check not implemented',
                'timestamp': datetime.now().isoformat(),
                'details': {}"""
    
    if fallback_old in content:
        content = content.replace(fallback_old, fallback_new)
        changes_made.append("✓ Fixed: Fallback response structure matches ServiceHealthCheck")
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("\nChanges Applied:")
        for change in changes_made:
            print(f"  {change}")
        
        return len(changes_made)
    else:
        print("\n⚠ No changes needed - file may already be fixed")
        return 0

def verify_fix(file_path):
    """Verify the fixes were applied correctly."""
    
    print("\nVerifying fixes...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: No get_health references
    if "get_health" not in content or "health_check" in content:
        checks.append("✓ Method name corrected")
    else:
        checks.append("✗ Still contains 'get_health' references")
    
    # Check 2: Uses status key
    if "health.get('status')" in content:
        checks.append("✓ Health status check uses 'status' key")
    else:
        checks.append("✗ Health status check needs update")
    
    # Check 3: Fallback structure updated
    if "'status': 'unknown'" in content:
        checks.append("✓ Fallback response structure updated")
    else:
        checks.append("⚠ Fallback response may need update")
    
    print("\nVerification Results:")
    for check in checks:
        print(f"  {check}")
    
    all_passed = all(check.startswith("✓") for check in checks)
    return all_passed

def main():
    """Main execution function."""
    
    print("=" * 70)
    print("UBEC Protocol - Health Check System Fix")
    print("=" * 70)
    print()
    
    # Check if main.py exists
    main_py = Path("main.py")
    if not main_py.exists():
        print("✗ Error: main.py not found in current directory")
        print("  Please run this script from the UBEC protocol root directory")
        return 1
    
    # Create backup
    try:
        backup_path = create_backup("main.py")
    except Exception as e:
        print(f"✗ Error creating backup: {e}")
        return 1
    
    # Apply fixes
    try:
        changes = fix_health_check_method_names("main.py")
        
        if changes == 0:
            print("\nNo changes applied - file may already be fixed")
        else:
            print(f"\n✓ Successfully applied {changes} fix(es)")
    except Exception as e:
        print(f"\n✗ Error applying fixes: {e}")
        print(f"  Restoring from backup: {backup_path}")
        
        with open(backup_path, 'r') as backup:
            with open("main.py", 'w') as main:
                main.write(backup.read())
        
        return 1
    
    # Verify fixes
    try:
        if verify_fix("main.py"):
            print("\n✓ All verification checks passed")
        else:
            print("\n⚠ Some verification checks failed - review output above")
    except Exception as e:
        print(f"\n⚠ Error during verification: {e}")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Review the changes made (backup saved)")
    print("2. Test the fix:")
    print("   python main.py --mode health")
    print()
    print("3. Verify output shows detailed health info, not:")
    print('   "Health check not implemented"')
    print()
    print("4. If issues occur, restore from backup:")
    print(f"   cp {backup_path} main.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
