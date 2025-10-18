#!/usr/bin/env python3
# diagnostic_health_check.py
"""
Quick Diagnostic Script for UBEC Health Check Issues
====================================================
Run this to identify exactly what's wrong with your health checks.

Usage:
    python diagnostic_health_check.py

This will:
1. Check for the problematic service_dependent_health reference
2. Verify health_check methods exist in all services
3. Test imports
4. Suggest specific fixes
"""

import os
import sys
import re
from pathlib import Path


def find_project_root():
    """Find the UBEC project root directory."""
    current = Path.cwd()
    
    # Look for key files that indicate project root
    markers = ['main.py', 'core', 'config', 'services']
    
    for _ in range(5):  # Check up to 5 levels up
        if all((current / marker).exists() for marker in markers):
            return current
        current = current.parent
    
    return Path.cwd()


def search_for_bad_reference(root_dir):
    """Search for references to the non-existent service_dependent_health method."""
    print("=" * 70)
    print("DIAGNOSTIC 1: Searching for service_dependent_health references")
    print("=" * 70)
    
    bad_refs = []
    pattern = re.compile(r'service_dependent_health')
    
    for py_file in root_dir.rglob('*.py'):
        # Skip __pycache__
        if '__pycache__' in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if pattern.search(content):
                    # Find line numbers
                    lines = content.split('\n')
                    line_nums = [i+1 for i, line in enumerate(lines) if 'service_dependent_health' in line]
                    bad_refs.append((py_file, line_nums))
        except Exception as e:
            print(f"⚠ Warning: Could not read {py_file}: {e}")
    
    if bad_refs:
        print("\n❌ FOUND PROBLEM REFERENCES:")
        for file_path, line_nums in bad_refs:
            rel_path = file_path.relative_to(root_dir)
            print(f"\n  File: {rel_path}")
            print(f"  Lines: {', '.join(map(str, line_nums))}")
            print(f"  Action: Remove or replace these references")
    else:
        print("\n✅ No references to service_dependent_health found")
        print("   (This is good! The method doesn't exist anyway)")
    
    return len(bad_refs)


def check_health_check_methods(root_dir):
    """Check which services have health_check methods."""
    print("\n" + "=" * 70)
    print("DIAGNOSTIC 2: Checking for health_check methods in services")
    print("=" * 70)
    
    # Known service files that should have health_check methods
    service_files = [
        'core/evaluation/distribution_evaluator.py',
        'services/audit/ubec_audit_service.py',
        'services/distribution/distribution_service.py',
        'services/analytics/ubec_analytics_service.py',
        'core/protocols/UBEC_protocol.py',
        'core/protocols/UBECrc_protocol.py',
        'core/protocols/UBECgpi_protocol.py',
        'core/protocols/UBECtt_protocol.py',
        'core/db/ubec_data_synchronizer.py',
        'core/holonic/ubec_holonic_evaluator.py',
        'services/orderbook/ubec_orderbook_service.py',
        'config/config.py',
        'core/holonic/ubec_holonic_visualizer.py',
    ]
    
    results = []
    pattern = re.compile(r'(async\s+)?def\s+health_check\s*\(')
    
    for service_file in service_files:
        full_path = root_dir / service_file
        
        if not full_path.exists():
            results.append((service_file, 'FILE_NOT_FOUND', None))
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = pattern.search(content)
                
                if match:
                    # Find line number
                    lines = content[:match.start()].split('\n')
                    line_num = len(lines)
                    is_async = 'async' in match.group(1) if match.group(1) else False
                    results.append((service_file, 'HAS_METHOD', {'line': line_num, 'async': is_async}))
                else:
                    results.append((service_file, 'MISSING_METHOD', None))
        except Exception as e:
            results.append((service_file, 'READ_ERROR', str(e)))
    
    # Print results
    has_method = [r for r in results if r[1] == 'HAS_METHOD']
    missing_method = [r for r in results if r[1] == 'MISSING_METHOD']
    errors = [r for r in results if r[1] not in ['HAS_METHOD', 'MISSING_METHOD', 'FILE_NOT_FOUND']]
    not_found = [r for r in results if r[1] == 'FILE_NOT_FOUND']
    
    print(f"\n✅ Services with health_check method: {len(has_method)}/{len(service_files)}")
    for file, status, info in has_method:
        async_marker = "(async)" if info and info.get('async') else "(sync)"
        print(f"   ✓ {file} {async_marker}")
    
    if missing_method:
        print(f"\n❌ Services missing health_check method: {len(missing_method)}")
        for file, status, _ in missing_method:
            print(f"   ✗ {file}")
            print(f"      Action: Add health_check() method to this service")
    
    if not_found:
        print(f"\n⚠ Files not found: {len(not_found)}")
        for file, status, _ in not_found:
            print(f"   ? {file}")
            print(f"      Action: Verify file path or service may be deprecated")
    
    if errors:
        print(f"\n⚠ Errors reading files: {len(errors)}")
        for file, status, error in errors:
            print(f"   ! {file}: {error}")
    
    return len(missing_method), len(not_found)


def check_servicehealth_utility(root_dir):
    """Check if ServiceHealthCheck utility exists and is correct."""
    print("\n" + "=" * 70)
    print("DIAGNOSTIC 3: Checking ServiceHealthCheck utility")
    print("=" * 70)
    
    utility_path = root_dir / 'core' / 'utils' / 'service_health.py'
    
    if not utility_path.exists():
        print(f"\n❌ ServiceHealthCheck utility not found at:")
        print(f"   {utility_path}")
        print(f"\n   Action: Create this file with the standard health check methods")
        return False
    
    print(f"\n✅ ServiceHealthCheck utility exists")
    
    # Check for expected methods
    expected_methods = [
        'basic_health_check',
        'database_dependent_health',
        'api_dependent_health',
    ]
    
    try:
        with open(utility_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_methods = []
        missing_methods = []
        
        for method in expected_methods:
            pattern = re.compile(rf'def\s+{method}\s*\(')
            if pattern.search(content):
                found_methods.append(method)
            else:
                missing_methods.append(method)
        
        print(f"\n   Methods found: {len(found_methods)}/{len(expected_methods)}")
        for method in found_methods:
            print(f"      ✓ {method}()")
        
        if missing_methods:
            print(f"\n   ❌ Methods missing:")
            for method in missing_methods:
                print(f"      ✗ {method}()")
            return False
        
        # Check that service_dependent_health is NOT there
        if re.search(r'def\s+service_dependent_health\s*\(', content):
            print("\n   ⚠ WARNING: service_dependent_health() method found")
            print("      This method should NOT exist - it's not part of the standard API")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error reading utility file: {e}")
        return False


def check_distribution_evaluator_specifically(root_dir):
    """Special check for the distribution_evaluator since it's showing an error."""
    print("\n" + "=" * 70)
    print("DIAGNOSTIC 4: Special check for distribution_evaluator")
    print("=" * 70)
    
    eval_path = root_dir / 'core' / 'evaluation' / 'distribution_evaluator.py'
    
    if not eval_path.exists():
        print(f"\n❌ distribution_evaluator.py not found at:")
        print(f"   {eval_path}")
        return False
    
    print(f"\n✅ distribution_evaluator.py exists")
    
    try:
        with open(eval_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for health_check method
        if re.search(r'(async\s+)?def\s+health_check\s*\(', content):
            print("   ✓ Has health_check() method")
            
            # Check if it uses ServiceHealthCheck utility
            if 'ServiceHealthCheck' in content:
                print("   ⚠ Uses ServiceHealthCheck utility")
                if 'service_dependent_health' in content:
                    print("   ❌ PROBLEM: Calls service_dependent_health() which doesn't exist!")
                    print("      Action: Remove this call and use built-in health check")
                else:
                    print("   ✓ Does not call service_dependent_health()")
            else:
                print("   ✓ Has custom health_check implementation (doesn't use utility)")
        else:
            print("   ❌ Missing health_check() method")
            print("      Action: Add health_check() method")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error reading distribution_evaluator.py: {e}")
        return False


def provide_recommendations(issues_found):
    """Provide specific recommendations based on issues found."""
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    if not any(issues_found.values()):
        print("\n🎉 No issues found! Your health check system looks good.")
        print("\nIf you're still seeing errors:")
        print("  1. Clear Python cache: find . -type d -name __pycache__ -exec rm -r {} +")
        print("  2. Restart any running services")
        print("  3. Run: python main.py --mode health")
        return
    
    print("\n🔧 Actions needed:")
    
    if issues_found.get('bad_references'):
        print("\n1. Remove references to service_dependent_health()")
        print("   This method doesn't exist and should not be called")
    
    if issues_found.get('missing_methods'):
        print("\n2. Add health_check() methods to services")
        print("   See HEALTH_CHECK_FIXES.md for examples")
    
    if issues_found.get('missing_utility'):
        print("\n3. Create or fix ServiceHealthCheck utility")
        print("   File: core/utils/service_health.py")
    
    if issues_found.get('evaluator_issue'):
        print("\n4. Fix distribution_evaluator specifically")
        print("   This service is causing the current error")
    
    print("\n📚 Resources:")
    print("   - docs/ACTION_PLAN_HEALTH_CHECKS.md")
    print("   - HEALTH_CHECK_FIXES.md (just created)")
    print("   - core/utils/service_health.py")


def main():
    """Run all diagnostics."""
    print("\n" + "=" * 70)
    print("UBEC HEALTH CHECK DIAGNOSTIC")
    print("=" * 70)
    print()
    
    root_dir = find_project_root()
    print(f"Project root: {root_dir}\n")
    
    issues_found = {}
    
    # Run diagnostics
    issues_found['bad_references'] = search_for_bad_reference(root_dir) > 0
    
    missing, not_found = check_health_check_methods(root_dir)
    issues_found['missing_methods'] = missing > 0
    
    issues_found['missing_utility'] = not check_servicehealth_utility(root_dir)
    
    issues_found['evaluator_issue'] = not check_distribution_evaluator_specifically(root_dir)
    
    # Provide recommendations
    provide_recommendations(issues_found)
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    print()
    
    # Exit code
    if any(issues_found.values()):
        print("Status: ⚠ Issues found (see recommendations above)")
        return 1
    else:
        print("Status: ✅ All checks passed")
        return 0


if __name__ == '__main__':
    sys.exit(main())
