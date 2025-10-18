#!/usr/bin/env python3
"""
Fix Status Mode Display Issues
===============================
Fixes the database pool_size and protocol element_type attributes.

Usage: python fix_status_display.py
"""

import sys
from pathlib import Path


def fix_status_function():
    """Fix the run_status() function to use correct attribute names."""
    
    print("=" * 70)
    print("Fixing Status Mode Display Issues")
    print("=" * 70)
    print()
    
    main_path = Path('main.py')
    if not main_path.exists():
        print("❌ main.py not found")
        return 1
    
    # Read file
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Backup
    backup_path = Path('main.py.status_display_backup')
    print(f"Creating backup: {backup_path}")
    with open(backup_path, 'w') as f:
        f.write(content)
    print("✓ Backup created")
    print()
    
    changes_made = []
    
    # Fix 1: Database pool attributes
    # Old: db.pool_min_size and db.pool_max_size
    # New: db.min_pool_size and db.max_pool_size
    if 'db.pool_min_size' in content:
        print("Fixing database pool attributes...")
        content = content.replace('db.pool_min_size', 'db.min_pool_size')
        content = content.replace('db.pool_max_size', 'db.max_pool_size')
        changes_made.append("Database pool attributes")
        print("✓ Fixed pool_min_size → min_pool_size")
        print("✓ Fixed pool_max_size → max_pool_size")
    
    # Fix 2: Add search_path property access
    # The database manager stores schema but not as search_path attribute
    if "db.search_path if hasattr(db, 'search_path')" in content:
        print()
        print("Fixing database schema access...")
        content = content.replace(
            "db.search_path if hasattr(db, 'search_path') else 'unknown'",
            "db.schema if hasattr(db, 'schema') else 'unknown'"
        )
        changes_made.append("Database schema access")
        print("✓ Fixed search_path → schema")
    
    # Fix 3: Protocol element_type
    # Protocols don't have element_type, they have descriptive names
    # But we can map them from asset_code
    if "getattr(proto, 'element_type', 'unknown')" in content:
        print()
        print("Fixing protocol element type...")
        
        # Replace the element_type line
        old_element_line = "                        'element': getattr(proto, 'element_type', 'unknown'),"
        new_element_lines = """                        'element': {
                            'air': 'Air (Gateway & Universal Access)',
                            'water': 'Water (Flow & Reciprocity)',
                            'earth': 'Earth (Stability & Mutualism)',
                            'fire': 'Fire (Transformation & Catalytic Change)'
                        }.get(proto_name, 'Unknown'),"""
        
        content = content.replace(old_element_line, new_element_lines)
        changes_made.append("Protocol element descriptions")
        print("✓ Fixed element_type mapping")
    
    # Write fixed file
    if changes_made:
        print()
        print("Writing updated main.py...")
        with open(main_path, 'w') as f:
            f.write(content)
        print("✓ File written")
        print()
        
        # Verify syntax
        print("Verifying syntax...")
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'py_compile', 'main.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Syntax valid")
            print()
            print("=" * 70)
            print("SUCCESS!")
            print("=" * 70)
            print()
            print("Changes made:")
            for change in changes_made:
                print(f"  ✓ {change}")
            print()
            print("Test it:")
            print("  python main.py --mode status")
            print()
            print("Expected improvements:")
            print("  • database.connected should now be True")
            print("  • database.pool_size should show '2-10'")
            print("  • database.schemas should show actual schema name")
            print("  • protocols should show proper element names")
            return 0
        else:
            print("❌ Syntax error:")
            print(result.stderr)
            print()
            print("Restoring backup...")
            subprocess.run(['cp', str(backup_path), 'main.py'])
            return 1
    else:
        print("ℹ No changes needed - attributes already correct")
        return 0


if __name__ == '__main__':
    sys.exit(fix_status_function())
