#!/usr/bin/env python3
"""
UBEC Module Structure Diagnostic
=================================
This script checks your actual module structure and identifies import issues.

Usage:
    python diagnose_modules.py
"""

import os
import sys
from pathlib import Path

def check_file(path_str, description):
    """Check if a file exists and is readable."""
    path = Path(path_str)
    if path.exists() and path.is_file():
        size = path.stat().st_size
        print(f"✅ {description}")
        print(f"   Path: {path}")
        print(f"   Size: {size:,} bytes")
        return True
    else:
        print(f"❌ {description}")
        print(f"   Path: {path} (NOT FOUND)")
        return False

def check_directory(path_str, description):
    """Check if a directory exists."""
    path = Path(path_str)
    if path.exists() and path.is_dir():
        files = list(path.glob('*.py'))
        print(f"✅ {description}")
        print(f"   Path: {path}")
        print(f"   Python files: {len(files)}")
        for f in sorted(files):
            print(f"     - {f.name}")
        return True
    else:
        print(f"❌ {description}")
        print(f"   Path: {path} (NOT FOUND)")
        return False

def test_import(import_statement, description):
    """Test if an import statement works."""
    try:
        exec(import_statement)
        print(f"✅ {description}")
        print(f"   Import: {import_statement}")
        return True
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Import: {import_statement}")
        print(f"   Error: {e}")
        return False

def main():
    print("=" * 70)
    print("UBEC Module Structure Diagnostic")
    print("=" * 70)
    print()
    
    # Get project root
    project_root = Path.cwd()
    print(f"Project root: {project_root}")
    print()
    
    # Check main.py
    print("=" * 70)
    print("1. Checking Main Files")
    print("=" * 70)
    check_file("main.py", "main.py (orchestrator)")
    check_file(".env", ".env (configuration)")
    print()
    
    # Check core directory structure
    print("=" * 70)
    print("2. Checking Core Directory Structure")
    print("=" * 70)
    check_directory("core", "core/ directory")
    check_directory("core/db", "core/db/ directory")
    check_directory("core/holonic", "core/holonic/ directory")
    check_directory("core/audit", "core/audit/ directory")
    print()
    
    # Check specific files
    print("=" * 70)
    print("3. Checking Database Modules")
    print("=" * 70)
    check_file("core/db/__init__.py", "core/db/__init__.py")
    check_file("core/db/connection.py", "core/db/connection.py")
    check_file("core/db/UBECDataSynchronizer.py", "core/db/UBECDataSynchronizer.py")
    print()
    
    # Check holonic modules
    print("=" * 70)
    print("4. Checking Holonic Modules")
    print("=" * 70)
    check_directory("core/holonic", "core/holonic/ directory")
    check_file("core/holonic/__init__.py", "core/holonic/__init__.py")
    check_file("core/holonic/UBECHolonicEvaluator.py", "core/holonic/UBECHolonicEvaluator.py")
    print()
    
    # Check alternative locations
    print("=" * 70)
    print("5. Checking Alternative Locations (legacy)")
    print("=" * 70)
    check_directory("db", "db/ directory (legacy)")
    check_directory("holonic", "holonic/ directory (legacy)")
    print()
    
    # Test imports
    print("=" * 70)
    print("6. Testing Imports")
    print("=" * 70)
    
    # Add project root to path
    sys.path.insert(0, str(project_root))
    
    test_import(
        "from core.db.connection import DatabaseConnection",
        "Import DatabaseConnection from core.db"
    )
    
    test_import(
        "from core.db.connection import get_connection",
        "Import get_connection from core.db"
    )
    
    if Path("core/db/UBECDataSynchronizer.py").exists():
        test_import(
            "from core.db.UBECDataSynchronizer import UBECDataSynchronizer",
            "Import UBECDataSynchronizer from core.db"
        )
    
    if Path("core/holonic/UBECHolonicEvaluator.py").exists():
        test_import(
            "from core.holonic.UBECHolonicEvaluator import UBECHolonicEvaluator",
            "Import UBECHolonicEvaluator from core.holonic"
        )
    
    print()
    
    # Search for synchronizer files
    print("=" * 70)
    print("7. Searching for Synchronizer Files")
    print("=" * 70)
    print("Searching for *Synchronizer*.py files...")
    sync_files = list(project_root.rglob("*Synchronizer*.py"))
    if sync_files:
        for f in sync_files:
            rel_path = f.relative_to(project_root)
            print(f"  Found: {rel_path}")
    else:
        print("  No synchronizer files found")
    print()
    
    # Search for evaluator files
    print("=" * 70)
    print("8. Searching for Evaluator Files")
    print("=" * 70)
    print("Searching for *Evaluator*.py files...")
    eval_files = list(project_root.rglob("*Evaluator*.py"))
    if eval_files:
        for f in eval_files:
            rel_path = f.relative_to(project_root)
            print(f"  Found: {rel_path}")
    else:
        print("  No evaluator files found")
    print()
    
    # Check __init__.py files
    print("=" * 70)
    print("9. Checking __init__.py Files (Python Package Structure)")
    print("=" * 70)
    init_files = [
        "core/__init__.py",
        "core/db/__init__.py",
        "core/holonic/__init__.py",
        "core/audit/__init__.py"
    ]
    
    for init_file in init_files:
        path = Path(init_file)
        if path.exists():
            print(f"✅ {init_file} exists")
        else:
            print(f"⚠️  {init_file} missing (will create)")
    print()
    
    # Final recommendations
    print("=" * 70)
    print("10. Recommendations")
    print("=" * 70)
    
    recommendations = []
    
    # Check if core/__init__.py exists
    if not Path("core/__init__.py").exists():
        recommendations.append("Create core/__init__.py")
    
    if not Path("core/db/__init__.py").exists():
        recommendations.append("Create core/db/__init__.py")
    
    if not Path("core/holonic/__init__.py").exists():
        recommendations.append("Create core/holonic/__init__.py")
    
    if not Path("core/db/UBECDataSynchronizer.py").exists():
        recommendations.append("UBECDataSynchronizer.py not in core/db/ - check actual location")
    
    if not Path("core/holonic/UBECHolonicEvaluator.py").exists():
        recommendations.append("UBECHolonicEvaluator.py not in core/holonic/ - check actual location")
    
    if recommendations:
        print("⚠️  Issues found:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print("✅ No issues found - module structure looks good!")
    
    print()
    print("=" * 70)
    print("Diagnostic Complete")
    print("=" * 70)

if __name__ == '__main__':
    main()
