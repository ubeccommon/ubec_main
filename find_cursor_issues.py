#!/usr/bin/env python3
"""
Find all .cursor() usage in the UBEC codebase

This script will locate any direct cursor access that needs to be fixed.

Usage:
    python find_cursor_issues.py
"""

import os
import re
from pathlib import Path

def find_cursor_usage(root_dir='.'):
    """Find all .cursor() calls in Python files"""
    
    issues = []
    cursor_pattern = re.compile(r'\.cursor\(\)', re.IGNORECASE)
    
    # Directories to search
    search_dirs = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt', 'core', 'config']
    
    print("🔍 Searching for .cursor() usage...\n")
    
    for search_dir in search_dirs:
        dir_path = Path(root_dir) / search_dir
        
        if not dir_path.exists():
            continue
        
        # Walk through all Python files
        for py_file in dir_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Check each line
                for line_num, line in enumerate(lines, 1):
                    if cursor_pattern.search(line):
                        issues.append({
                            'file': str(py_file),
                            'line': line_num,
                            'content': line.strip()
                        })
            except Exception as e:
                print(f"⚠️  Error reading {py_file}: {e}")
    
    return issues

def print_results(issues):
    """Print the results in a readable format"""
    
    if not issues:
        print("✅ No .cursor() usage found! Your code is clean.")
        return
    
    print(f"❌ Found {len(issues)} instance(s) of .cursor() usage:\n")
    print("=" * 80)
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. File: {issue['file']}")
        print(f"   Line {issue['line']}: {issue['content']}")
        print(f"   \n   Fix: Replace with self.db.execute_query(...)")
    
    print("\n" + "=" * 80)
    print(f"\nTotal issues to fix: {len(issues)}")
    print("\nSee FIX_UBECtt_Cursor_Error.md for the correct pattern.")

if __name__ == "__main__":
    print("🔧 UBEC Cursor Usage Diagnostic Tool\n")
    
    # Check if we're in the right directory
    if not (Path('.') / 'main.py').exists():
        print("⚠️  Warning: main.py not found in current directory.")
        print("   Make sure you're in the project root: /path/to/UBEC/projects/UBEC\n")
    
    issues = find_cursor_usage()
    print_results(issues)
    
    if issues:
        print("\n💡 Next steps:")
        print("   1. Open each file listed above")
        print("   2. Replace .cursor() with execute_query() pattern")
        print("   3. Test: python test_database_fix.py")
        print("   4. Run: python main.py sync")
