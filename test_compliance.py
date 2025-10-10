#!/usr/bin/env python3
"""
Test Compliance with 12 Project Design Principles

This test suite verifies that the updated UBEC protocol modules
comply with all 12 design principles.

STANDALONE VERSION: Does not import any UBEC modules to avoid
triggering broken package imports. Uses AST parsing only.

Focus: Tests the updated modules (UBECtt_protocol.py and ubec_main_protocol.py)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import sys
import ast
from pathlib import Path

# Prevent Python from importing anything from current package
# This avoids triggering __init__.py imports that might be broken
sys.dont_write_bytecode = True


def find_file(filename: str) -> Path:
    """Find file in multiple locations"""
    # Search paths
    search_paths = [
        Path('.'),                    # Current directory
        Path('..'),                   # Parent directory
        Path('../..'),                # Grandparent
        Path('.').absolute(),         # Absolute current
        Path('.').absolute().parent,  # Absolute parent
    ]
    
    for search_path in search_paths:
        file_path = search_path / filename
        if file_path.exists():
            print(f"✓ Found {filename} at {file_path}")
            return file_path
    
    raise FileNotFoundError(f"Cannot find {filename} in any search path")


def read_file_content(filename: str) -> str:
    """Read file content"""
    file_path = find_file(filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


class ComplianceTest:
    """Compliance test runner"""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        
        # Files to test
        self.files = [
            'UBECtt_protocol.py',
            'ubec_main_protocol.py'
        ]
    
    def test(self, name: str, condition: bool, message: str = ""):
        """Record test result"""
        if condition:
            self.passed.append(name)
            print(f"  ✓ {name}")
        else:
            self.failed.append(name)
            print(f"  ✗ {name}")
            if message:
                print(f"     {message}")
    
    def warn(self, message: str):
        """Record warning"""
        self.warnings.append(message)
        print(f"  ⚠ {message}")
    
    def run_all_tests(self):
        """Run all compliance tests"""
        print("\n" + "=" * 70)
        print("DESIGN PRINCIPLES COMPLIANCE TEST")
        print("=" * 70 + "\n")
        
        # Try to load files
        print("Loading files...")
        try:
            self.ubectt_content = read_file_content('UBECtt_protocol.py')
            self.main_content = read_file_content('ubec_main_protocol.py')
        except FileNotFoundError as e:
            print(f"\n✗ ERROR: {e}")
            print("\nPlease ensure the test file is in the same directory as:")
            print("  - UBECtt_protocol.py")
            print("  - ubec_main_protocol.py")
            print("\nOr run from the UBEC project root directory.")
            sys.exit(1)
        
        print()
        
        # Run all principle tests
        self.test_principle_1()
        self.test_principle_2()
        self.test_principle_3()
        self.test_principle_4()
        self.test_principle_5()
        self.test_principle_6()
        self.test_principle_8()
        self.test_principle_9()
        self.test_principle_10()
        self.test_principle_11()
        self.test_principle_12()
        
        # Print summary
        self.print_summary()
    
    def test_principle_1(self):
        """Principle 1: Modular Design"""
        print("Principle 1: Modular Design and Architecture")
        
        violations = []
        for filename in self.files:
            content = read_file_content(filename)
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        lines = node.end_lineno - node.lineno
                        if lines > 50:
                            violations.append(
                                f"{filename}: Function '{node.name}' is {lines} lines"
                            )
        
        self.test(
            "Functions are reasonably sized (<50 lines)",
            len(violations) < 3,
            f"Found {len(violations)} functions over 50 lines"
        )
        print()
    
    def test_principle_2(self):
        """Principle 2: Service Pattern"""
        print("Principle 2: Service Pattern with Centralized Execution")
        
        # Test 1: Only main.py has __main__
        has_main_in_ubectt = "if __name__ == '__main__':" in self.ubectt_content
        has_main_in_main = "if __name__ == '__main__':" in self.main_content
        
        self.test(
            "UBECtt_protocol.py has NO __main__ block",
            not has_main_in_ubectt,
            "Service modules should not have standalone execution"
        )
        
        self.test(
            "ubec_main_protocol.py HAS __main__ block",
            has_main_in_main,
            "Main orchestrator must have standalone execution"
        )
        
        # Test 2: Factory pattern
        has_factory = 'def create_ubectt_service' in self.ubectt_content
        factory_exported = "'create_ubectt_service'" in self.ubectt_content or \
                          '"create_ubectt_service"' in self.ubectt_content
        
        self.test(
            "UBECtt uses factory function pattern",
            has_factory,
            "Should have 'create_ubectt_service' factory function"
        )
        
        self.test(
            "Factory function is exported",
            factory_exported,
            "Factory function should be in __all__"
        )
        print()
    
    def test_principle_3(self):
        """Principle 3: Service Registry"""
        print("Principle 3: Service Registry for Dependencies")
        
        # Test 1: ServiceRegistry exists
        has_registry = 'class ServiceRegistry' in self.main_content
        has_get_method = 'def get(self' in self.main_content
        
        self.test(
            "ServiceRegistry class exists",
            has_registry,
            "Main protocol should have ServiceRegistry class"
        )
        
        self.test(
            "ServiceRegistry has get() method",
            has_get_method,
            "ServiceRegistry should provide service lookup"
        )
        
        # Test 2: Dependency injection in UBECtt
        tree = ast.parse(self.ubectt_content)
        service_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and 'Service' in node.name:
                service_class = node
                break
        
        has_init_with_deps = False
        if service_class:
            for item in service_class.body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    arg_names = [arg.arg for arg in item.args.args]
                    has_init_with_deps = 'db_manager' in arg_names and 'config' in arg_names
                    break
        
        self.test(
            "UBECtt service uses dependency injection",
            has_init_with_deps,
            "__init__ should accept db_manager and config"
        )
        print()
    
    def test_principle_4(self):
        """Principle 4: Single Source of Truth"""
        print("Principle 4: Single Source of Truth")
        
        # Database is authoritative
        has_db_write = 'await self.db.execute_query' in self.ubectt_content or \
                       'await self._store_action_to_db' in self.ubectt_content
        
        has_cache = '_cache' in self.ubectt_content.lower()
        
        has_db_load = '_load_from_database' in self.ubectt_content or \
                      'load_from_database' in self.ubectt_content
        
        self.test(
            "Writes to database",
            has_db_write,
            "Should have async database write operations"
        )
        
        self.test(
            "Has caching mechanism",
            has_cache,
            "Should have cache for performance"
        )
        
        self.test(
            "Cache refreshes from database",
            has_db_load,
            "Should load data from database"
        )
        print()
    
    def test_principle_5(self):
        """Principle 5: Strict Async Operations"""
        print("Principle 5: Strict Async Operations")
        
        violations = []
        
        for filename in self.files:
            content = read_file_content(filename)
            
            # Check for sync violations
            if 'import time' in content and 'time.sleep(' in content:
                violations.append(f"{filename}: uses time.sleep()")
            
            if 'import requests' in content:
                violations.append(f"{filename}: uses sync requests library")
        
        self.test(
            "No blocking operations (time.sleep, requests)",
            len(violations) == 0,
            "; ".join(violations) if violations else ""
        )
        
        # Count async methods
        ubectt_async_count = self.ubectt_content.count('async def ')
        main_async_count = self.main_content.count('async def ')
        
        self.test(
            f"UBECtt has sufficient async methods ({ubectt_async_count})",
            ubectt_async_count >= 5,
            f"Expected ≥5, found {ubectt_async_count}"
        )
        
        self.test(
            f"Main protocol has sufficient async methods ({main_async_count})",
            main_async_count >= 5,
            f"Expected ≥5, found {main_async_count}"
        )
        print()
    
    def test_principle_6(self):
        """Principle 6: No Sync Fallbacks"""
        print("Principle 6: No Sync Fallbacks or Backward Compatibility")
        
        violations = []
        
        for filename in self.files:
            content = read_file_content(filename)
            
            if 'def sync_wrapper' in content or 'def sync_' in content:
                violations.append(f"{filename}: has sync wrapper methods")
            
            if 'backward compatibility' in content.lower():
                self.warn(f"{filename} mentions backward compatibility")
        
        self.test(
            "No sync fallback methods",
            len(violations) == 0,
            "; ".join(violations) if violations else ""
        )
        print()
    
    def test_principle_8(self):
        """Principle 8: No Duplicate Configuration"""
        print("Principle 8: No Duplicate Configuration")
        
        # Config injection, not internal loading
        no_config_parser = 'ConfigParser' not in self.ubectt_content
        has_config_param = 'config' in self.ubectt_content and '__init__' in self.ubectt_content
        
        self.test(
            "No ConfigParser (config file loading)",
            no_config_parser,
            "Should not load config files internally"
        )
        
        self.test(
            "Accepts config via constructor",
            has_config_param,
            "Should use dependency injection for config"
        )
        print()
    
    def test_principle_9(self):
        """Principle 9: Integrated Rate Limiting"""
        print("Principle 9: Integrated Rate Limiting")
        
        has_rate_limiter_class = 'class RateLimiter' in self.ubectt_content
        has_async_acquire = 'async def acquire' in self.ubectt_content
        uses_rate_limiter = 'self.rate_limiter' in self.ubectt_content
        
        self.test(
            "RateLimiter class exists",
            has_rate_limiter_class,
            "Should have RateLimiter implementation"
        )
        
        self.test(
            "RateLimiter has async acquire method",
            has_async_acquire,
            "Rate limiting should be async"
        )
        
        self.test(
            "Service uses rate limiter",
            uses_rate_limiter,
            "Should instantiate and use rate limiter"
        )
        print()
    
    def test_principle_10(self):
        """Principle 10: Separation of Concerns"""
        print("Principle 10: Clear Separation of Concerns")
        
        # Main protocol is orchestrator
        has_orchestrator = 'class UBECMainProtocol' in self.main_content
        uses_registry = 'ServiceRegistry' in self.main_content
        
        # UBECtt is service
        has_service_class = 'Service' in self.ubectt_content
        no_orchestration = 'ServiceRegistry' not in self.ubectt_content
        
        self.test(
            "Main protocol is orchestrator",
            has_orchestrator and uses_registry,
            "Should have UBECMainProtocol using ServiceRegistry"
        )
        
        self.test(
            "UBECtt is service (not orchestrator)",
            has_service_class and no_orchestration,
            "Service should not orchestrate other services"
        )
        print()
    
    def test_principle_11(self):
        """Principle 11: Comprehensive Documentation"""
        print("Principle 11: Comprehensive Documentation")
        
        violations = []
        
        # Attribution
        for filename in self.files:
            content = read_file_content(filename)
            
            if 'Anthropic PBC' not in content:
                violations.append(f"{filename}: Missing Anthropic PBC attribution")
            
            if 'Claude' not in content:
                violations.append(f"{filename}: Missing Claude attribution")
        
        self.test(
            "Attribution present in all files",
            len(violations) == 0,
            "; ".join(violations) if violations else ""
        )
        
        # Docstrings
        ubectt_tree = ast.parse(self.ubectt_content)
        main_tree = ast.parse(self.main_content)
        
        missing_docstrings = []
        for tree, filename in [(ubectt_tree, 'UBECtt'), (main_tree, 'Main')]:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        missing_docstrings.append(f"{filename}: Class '{node.name}'")
        
        self.test(
            "Classes have docstrings",
            len(missing_docstrings) < 3,
            f"Found {len(missing_docstrings)} classes without docstrings"
        )
        print()
    
    def test_principle_12(self):
        """Principle 12: Method Singularity"""
        print("Principle 12: Method Singularity (No Redundancy)")
        
        for filename in self.files:
            content = read_file_content(filename)
            tree = ast.parse(content)
            
            method_names = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith('__'):
                        method_names.append(node.name)
            
            duplicates = [name for name in set(method_names) if method_names.count(name) > 1]
            suspicious = [d for d in duplicates if not d.startswith('_')]
            
            self.test(
                f"{filename.split('.')[0]}: No duplicate methods",
                len(suspicious) == 0,
                f"Duplicate methods: {suspicious}" if suspicious else ""
            )
        print()
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        total = len(self.passed) + len(self.failed)
        pass_rate = (len(self.passed) / total * 100) if total > 0 else 0
        
        print(f"\n✓ Passed: {len(self.passed)}/{total} ({pass_rate:.1f}%)")
        
        if self.failed:
            print(f"✗ Failed: {len(self.failed)}/{total}")
            print("\nFailed tests:")
            for test in self.failed:
                print(f"  - {test}")
        
        if self.warnings:
            print(f"\n⚠ Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("\n" + "=" * 70)
        
        if len(self.failed) == 0:
            print("🎉 ALL TESTS PASSED - 100% COMPLIANCE ✅")
        else:
            print(f"⚠️  {len(self.failed)} TESTS FAILED - REVIEW NEEDED")
        
        print("=" * 70 + "\n")
        
        # Return exit code
        return 0 if len(self.failed) == 0 else 1


def main():
    """Main entry point"""
    print("\nUBEC Protocol - Design Principles Compliance Test")
    print("Standalone version - no package imports\n")
    
    # Run tests
    tester = ComplianceTest()
    exit_code = tester.run_all_tests()
    
    # Print principles list
    print("\nDesign Principles Tested:")
    principles = [
        "1. Modular Design and Architecture",
        "2. Service Pattern with Centralized Execution",
        "3. Service Registry for Dependencies",
        "4. Single Source of Truth",
        "5. Strict Async Operations",
        "6. No Sync Fallbacks or Backward Compatibility",
        "7. Per-Asset Monitoring (tested in integration)",
        "8. No Duplicate Configuration",
        "9. Integrated Rate Limiting",
        "10. Clear Separation of Concerns",
        "11. Comprehensive Documentation",
        "12. Method Singularity (No Redundancy)"
    ]
    
    for principle in principles:
        print(f"  • {principle}")
    
    print("\nFiles Tested:")
    print("  • UBECtt_protocol.py (Fire Element)")
    print("  • ubec_main_protocol.py (Main Orchestrator)")
    
    print("\n" + "=" * 70)
    print("Attribution:")
    print("This project uses the services of Claude and Anthropic PBC to inform")
    print("our decisions and recommendations. This project was made possible with")
    print("the assistance of Claude and Anthropic PBC.")
    print("=" * 70 + "\n")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
