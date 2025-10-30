#!/usr/bin/env python3
"""
Automated Import Path Fixer for UBEC Protocol Suite

This script automatically corrects incorrect import paths identified in the 
status log analysis (October 29, 2025).

Issues Fixed:
1. Element token imports: protocols.* → core.protocols.*
2. Synchronizer imports: services.sync.* → core.db.ubec_data_synchronizer

Usage:
    python fix_imports.py [--dry-run] [--verbose]

Options:
    --dry-run    Show what would be changed without modifying files
    --verbose    Show detailed progress information

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.
"""

import os
import re
import sys
from pathlib import Path
from typing import Tuple, List
import argparse
from datetime import datetime

# Import path corrections mapping
CORRECTIONS = {
    # Element token protocols - specific imports first
    r'from protocols\.air\.ubec import': 'from core.protocols.UBEC_protocol import',
    r'from protocols\.water\.ubecrc import': 'from core.protocols.UBECrc_protocol import',
    r'from protocols\.earth\.ubecgpi import': 'from core.protocols.UBECgpi_protocol import',
    r'from protocols\.fire\.ubectt import': 'from core.protocols.UBECtt_protocol import',
    
    # Generic protocol imports (catch-all, should be last in this group)
    r'from protocols\.([a-zA-Z_][a-zA-Z0-9_]*) import': r'from core.protocols.\1 import',
    r'import protocols\.([a-zA-Z_][a-zA-Z0-9_]*)': r'import core.protocols.\1',
    
    # Synchronizer service
    r'from services\.sync\.synchronizer import': 'from core.db.ubec_data_synchronizer import',
    r'from services\.sync import': 'from core.db.ubec_data_synchronizer import',
    r'import services\.sync\.synchronizer': 'import core.db.ubec_data_synchronizer',
    r'import services\.sync': 'import core.db.ubec_data_synchronizer',
}

# Directories to skip during scanning
SKIP_DIRS = {'.git', '__pycache__', 'venv', 'env', '.venv', 'node_modules', '.pytest_cache'}

# File patterns to skip
SKIP_PATTERNS = {'.backup', '.bak', '.old', '.tmp'}


def should_skip_file(filepath: Path) -> bool:
    """Determine if a file should be skipped during processing."""
    # Skip if in excluded directory
    if any(skip_dir in filepath.parts for skip_dir in SKIP_DIRS):
        return True
    
    # Skip if matches excluded pattern
    if any(pattern in filepath.name for pattern in SKIP_PATTERNS):
        return True
    
    return False


def fix_imports_in_file(
    filepath: Path, 
    dry_run: bool = False,
    verbose: bool = False
) -> Tuple[bool, List[str], str]:
    """
    Fix import statements in a single file.
    
    Args:
        filepath: Path to the Python file
        dry_run: If True, don't modify files, just report changes
        verbose: If True, print detailed information
    
    Returns:
        (modified: bool, changes: list[str], error: str)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # Apply each correction pattern
        for pattern, replacement in CORRECTIONS.items():
            matches = list(re.finditer(pattern, content))
            
            for match in matches:
                old_import = match.group(0)
                # Handle replacement patterns with backreferences
                if r'\1' in replacement:
                    new_import = re.sub(pattern, replacement, old_import)
                else:
                    new_import = replacement
                
                changes.append(f"    {old_import} → {new_import}")
                
                if verbose:
                    print(f"  Found: {old_import}")
                    print(f"  Replace with: {new_import}")
            
            content = re.sub(pattern, replacement, content)
        
        # If changes were made and not dry-run, save the file
        if content != original:
            if not dry_run:
                # Create backup with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = filepath.with_suffix(f'{filepath.suffix}.backup.{timestamp}')
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original)
                
                # Write corrected version
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                if verbose:
                    print(f"  ✓ Backup created: {backup_path.name}")
            
            return True, changes, ""
        
        return False, [], ""
    
    except Exception as e:
        error_msg = f"Error processing {filepath}: {e}"
        return False, [], error_msg


def main():
    """Scan project and fix all import paths."""
    parser = argparse.ArgumentParser(
        description='Fix incorrect import paths in UBEC Protocol Suite'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress information'
    )
    parser.add_argument(
        '--path',
        type=Path,
        default=Path.cwd(),
        help='Project root path (default: current directory)'
    )
    
    args = parser.parse_args()
    
    project_root = args.path.resolve()
    
    if not project_root.exists():
        print(f"✗ Error: Path does not exist: {project_root}")
        sys.exit(1)
    
    # Find all Python files
    python_files = [
        f for f in project_root.rglob("*.py")
        if not should_skip_file(f)
    ]
    
    # Print header
    print("=" * 70)
    print("UBEC PROTOCOL SUITE - AUTOMATED IMPORT PATH FIXER")
    print("=" * 70)
    print(f"Project root: {project_root}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
    print(f"Scanning {len(python_files)} Python files...")
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No files will be modified")
    print()
    
    # Process files
    modified_count = 0
    total_changes = 0
    errors = []
    
    for filepath in python_files:
        if args.verbose:
            print(f"Checking: {filepath.relative_to(project_root)}")
        
        modified, changes, error = fix_imports_in_file(
            filepath, 
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        if error:
            errors.append(error)
            print(f"✗ {error}")
            continue
        
        if modified:
            modified_count += 1
            total_changes += len(changes)
            
            status = "Would modify" if args.dry_run else "Modified"
            print(f"{'⚠️ ' if args.dry_run else '✓ '}{status}: {filepath.relative_to(project_root)}")
            
            for change in changes:
                print(change)
            print()
    
    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files scanned: {len(python_files)}")
    print(f"Files {('that would be ' if args.dry_run else '')}modified: {modified_count}")
    print(f"Import statements {('that would be ' if args.dry_run else '')}fixed: {total_changes}")
    print(f"Errors encountered: {len(errors)}")
    print()
    
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  ✗ {error}")
        print()
    
    if modified_count > 0:
        if args.dry_run:
            print("⚠️  This was a DRY RUN - no files were modified")
            print("Run without --dry-run to apply changes")
        else:
            print("✓ Import paths corrected successfully")
            print(f"✓ Backup files created with .backup.TIMESTAMP extension")
            print()
            print("NEXT STEPS:")
            print("1. Review changes in modified files")
            print("2. Run: python main.py status --log-level=DEBUG")
            print("3. Verify all 15 services initialize successfully")
            print("4. If successful, delete backup files:")
            print("   find . -name '*.backup.*' -delete")
    else:
        print("⚠️  No import path issues found")
        print()
        print("Possible reasons:")
        print("1. Import paths are already correct")
        print("2. Files are in different locations than expected")
        print("3. Import statements use different patterns")
        print()
        print("MANUAL INVESTIGATION REQUIRED:")
        print("1. Check actual import statements:")
        print("   grep -rn 'from protocols' .")
        print("   grep -rn 'from services.sync' .")
        print()
        print("2. Verify module structure:")
        print("   ls -R core/protocols/")
        print("   ls -R core/db/")
        print()
        print("3. See UBEC_CRITICAL_FIXES.md for manual fix procedure")
    
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
