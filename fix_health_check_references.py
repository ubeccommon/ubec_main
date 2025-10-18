#!/usr/bin/env python3
"""
Automatic Fix Script for service_dependent_health References
=============================================================
This script replaces all calls to the non-existent service_dependent_health()
method with the correct database_dependent_health() method.

Run this to automatically fix all the health check issues.

Usage:
    python fix_health_check_references.py
    
This will:
1. Backup affected files (creates .backup files)
2. Replace service_dependent_health with database_dependent_health
3. Report what was changed
4. Allow you to verify changes before committing
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime


def find_project_root():
    """Find the UBEC project root directory."""
    current = Path.cwd()
    
    # Look for key files
    markers = ['main.py', 'core', 'config', 'services']
    
    for _ in range(5):
        if all((current / marker).exists() for marker in markers):
            return current
        current = current.parent
    
    return Path.cwd()


def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = str(file_path) + '.backup'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not backup {file_path}: {e}")
        return False


def fix_file(file_path):
    """Fix service_dependent_health references in a file."""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file needs fixing
        if 'service_dependent_health' not in content:
            return 0, []
        
        # Backup first
        if not backup_file(file_path):
            print(f"❌ Skipping {file_path} - backup failed")
            return 0, []
        
        # Track changes
        changes = []
        original_lines = content.split('\n')
        
        # Replace the method calls
        # Pattern: ServiceHealthCheck.service_dependent_health(...)
        new_content = content
        
        # Pattern 1: Direct method call
        pattern1 = r'ServiceHealthCheck\.service_dependent_health\('
        replacement1 = r'ServiceHealthCheck.database_dependent_health('
        count1 = len(re.findall(pattern1, new_content))
        new_content = re.sub(pattern1, replacement1, new_content)
        
        # Pattern 2: In comments or docs
        pattern2 = r"'service_dependent_health'"
        replacement2 = r"'database_dependent_health'"
        count2 = len(re.findall(pattern2, new_content))
        new_content = re.sub(pattern2, replacement2, new_content)
        
        # Pattern 3: Plain text references
        pattern3 = r'\bservice_dependent_health\b'
        replacement3 = r'database_dependent_health'
        count3 = len(re.findall(pattern3, new_content))
        new_content = re.sub(pattern3, replacement3, new_content)
        
        total_replacements = count1 + count2 + count3
        
        if total_replacements > 0:
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Find changed lines
            new_lines = new_content.split('\n')
            for i, (old, new) in enumerate(zip(original_lines, new_lines)):
                if old != new and 'service_dependent_health' in old.lower():
                    changes.append((i+1, old.strip(), new.strip()))
        
        return total_replacements, changes
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return 0, []


def main():
    """Main fix routine."""
    print("=" * 70)
    print("AUTOMATIC HEALTH CHECK REFERENCE FIXER")
    print("=" * 70)
    print()
    
    root_dir = find_project_root()
    print(f"Project root: {root_dir}")
    print()
    
    # Files that need fixing (from diagnostic)
    files_to_fix = [
        'main.py',
        'core/evaluation/distribution_evaluator.py',
        # Note: Not fixing diagnostic_health_check.py or test files
        # as they are reference files
    ]
    
    print("Files to fix:")
    for f in files_to_fix:
        full_path = root_dir / f
        if full_path.exists():
            print(f"  ✓ {f}")
        else:
            print(f"  ✗ {f} (NOT FOUND)")
    print()
    
    # Ask for confirmation
    response = input("Proceed with automatic fixes? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Aborted by user.")
        return 1
    
    print()
    print("=" * 70)
    print("APPLYING FIXES")
    print("=" * 70)
    print()
    
    total_files_fixed = 0
    total_replacements = 0
    
    for file_name in files_to_fix:
        file_path = root_dir / file_name
        
        if not file_path.exists():
            print(f"⚠ Skipping {file_name} - file not found")
            continue
        
        print(f"Processing: {file_name}")
        replacements, changes = fix_file(file_path)
        
        if replacements > 0:
            total_files_fixed += 1
            total_replacements += replacements
            print(f"  ✅ Fixed {replacements} reference(s)")
            
            if changes:
                print(f"  Changed lines:")
                for line_num, old, new in changes[:3]:  # Show first 3
                    print(f"    Line {line_num}:")
                    print(f"      Old: {old[:70]}")
                    print(f"      New: {new[:70]}")
                if len(changes) > 3:
                    print(f"    ... and {len(changes) - 3} more")
            
            print(f"  💾 Backup saved: {file_name}.backup")
        else:
            print(f"  ℹ No changes needed")
        
        print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Files processed: {len(files_to_fix)}")
    print(f"Files fixed: {total_files_fixed}")
    print(f"Total replacements: {total_replacements}")
    print()
    
    if total_files_fixed > 0:
        print("✅ Fixes applied successfully!")
        print()
        print("Next steps:")
        print("  1. Clear Python cache:")
        print("     find . -name __pycache__ -exec rm -r {} + 2>/dev/null")
        print()
        print("  2. Test the fixes:")
        print("     python main.py --mode health")
        print()
        print("  3. If everything works, remove backups:")
        print("     rm *.backup core/evaluation/*.backup")
        print()
        print("  4. If something breaks, restore from backups:")
        print("     mv main.py.backup main.py")
        print("     mv core/evaluation/distribution_evaluator.py.backup core/evaluation/distribution_evaluator.py")
    else:
        print("ℹ No fixes needed")
    
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
