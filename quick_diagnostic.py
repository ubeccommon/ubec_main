#!/usr/bin/env python3
"""
Quick Diagnostic: Check Service Parameter Types

Run this in your UBEC project directory to quickly identify 
what types are being passed to the distribution service.

Usage:
    python quick_diagnostic.py

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import sys
import re
from pathlib import Path


def find_distribution_service_creation():
    """Find where distribution service is created in main.py"""
    
    main_py = Path('main.py')
    
    if not main_py.exists():
        print("❌ main.py not found in current directory")
        print("   Run this script from your UBEC project root")
        return None
    
    with open(main_py, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find distribution service creation
    creation_patterns = [
        r'create_distribution_service\(',
        r'UBECDistributionService\(',
        r'distribution_service\s*=',
    ]
    
    matches = []
    for i, line in enumerate(lines, start=1):
        for pattern in creation_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                matches.append((i, line.strip()))
    
    return matches, lines


def analyze_service_creation(matches, lines):
    """Analyze how services are being created"""
    
    if not matches:
        print("❌ Could not find distribution service creation in main.py")
        return
    
    print("=" * 80)
    print("DISTRIBUTION SERVICE CREATION ANALYSIS")
    print("=" * 80)
    print()
    
    for line_num, line in matches:
        print(f"Found at line {line_num}:")
        print(f"  {line}")
        print()
        
        # Show context (5 lines before and after)
        start = max(0, line_num - 6)
        end = min(len(lines), line_num + 5)
        
        print("Context:")
        for i in range(start, end):
            marker = ">>> " if i == line_num - 1 else "    "
            print(f"{marker}{i+1:4d}: {lines[i]}")
        print()
    
    print("=" * 80)
    print("WHAT TO CHECK:")
    print("=" * 80)
    print()
    print("Look for these WRONG patterns:")
    print("  ❌ db_manager=config['database']")
    print("  ❌ db_manager=config.get('database')")
    print("  ❌ stellar_client=config['stellar']")
    print("  ❌ stellar_client=stellar_config")
    print()
    print("Should be these CORRECT patterns:")
    print("  ✅ db_manager=db_manager  (where db_manager is AsyncDatabaseManager)")
    print("  ✅ stellar_client=stellar_client  (where stellar_client is ServerAsync)")
    print()


def find_service_initializations():
    """Find where db_manager and stellar_client are initialized"""
    
    main_py = Path('main.py')
    
    with open(main_py, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    print("=" * 80)
    print("SERVICE INITIALIZATION ANALYSIS")
    print("=" * 80)
    print()
    
    # Find database manager initialization
    print("DATABASE MANAGER:")
    print("-" * 80)
    db_patterns = [
        r'AsyncDatabaseManager\(',
        r'DatabaseManager\(',
        r'db_manager\s*=',
    ]
    
    found_db = False
    for i, line in enumerate(lines, start=1):
        for pattern in db_patterns:
            if re.search(pattern, line):
                print(f"Line {i}: {line.strip()}")
                found_db = True
    
    if not found_db:
        print("❌ No database manager initialization found!")
        print("   This is a problem - db_manager needs to be created")
    print()
    
    # Find Stellar client initialization  
    print("STELLAR CLIENT:")
    print("-" * 80)
    stellar_patterns = [
        r'ServerAsync\(',
        r'StellarClient\(',
        r'stellar_client\s*=',
    ]
    
    found_stellar = False
    for i, line in enumerate(lines, start=1):
        for pattern in stellar_patterns:
            if re.search(pattern, line):
                print(f"Line {i}: {line.strip()}")
                found_stellar = True
    
    if not found_stellar:
        print("❌ No Stellar client initialization found!")
        print("   This is likely the problem - stellar_client is probably a dict")
    print()


def check_imports():
    """Check if required imports are present"""
    
    main_py = Path('main.py')
    
    with open(main_py, 'r') as f:
        content = f.read()
    
    print("=" * 80)
    print("IMPORT CHECKS")
    print("=" * 80)
    print()
    
    required_imports = {
        'AsyncDatabaseManager': r'from.*AsyncDatabaseManager',
        'ServerAsync': r'from.*stellar_sdk.*import.*ServerAsync',
    }
    
    for name, pattern in required_imports.items():
        if re.search(pattern, content):
            print(f"✅ {name} is imported")
        else:
            print(f"❌ {name} NOT imported - this is likely a problem!")
    print()


def main():
    """Main diagnostic function"""
    
    print()
    print("🔍 UBEC Distribution Service Diagnostic")
    print("=" * 80)
    print()
    
    # Check imports
    check_imports()
    
    # Find initializations
    find_service_initializations()
    
    # Find service creation
    result = find_distribution_service_creation()
    if result:
        matches, lines = result
        analyze_service_creation(matches, lines)
    
    print()
    print("=" * 80)
    print("RECOMMENDED NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Review the code sections highlighted above")
    print("2. Verify stellar_client is created as ServerAsync instance")
    print("3. Verify db_manager is created as AsyncDatabaseManager instance")
    print("4. Update distribution service creation to pass actual instances")
    print()
    print("For detailed fix instructions, see:")
    print("  - CRITICAL_ADDENDUM.md")
    print("  - FIX_SUMMARY.md")
    print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error running diagnostic: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
