# Test Compliance Guide

## Overview

The `test_compliance.py` file provides comprehensive automated testing for all 12 design principles. This guide explains how to use it effectively.

---

## What's Tested

### ✅ All 12 Design Principles

1. **Modular Design** - Checks function sizes and class boundaries
2. **Service Pattern** - Verifies only main.py has standalone execution
3. **Service Registry** - Confirms ServiceRegistry exists and works
4. **Single Source of Truth** - Validates database-first approach
5. **Strict Async** - Ensures all I/O is async
6. **No Sync Fallbacks** - Confirms no backward compatibility layers
7. **Per-Asset Monitoring** - (Integration test)
8. **No Duplicate Config** - Verifies config injection
9. **Rate Limiting** - Checks RateLimiter implementation
10. **Separation of Concerns** - Validates layer architecture
11. **Documentation** - Confirms attribution and docstrings
12. **Method Singularity** - Ensures no duplicate methods

### 📁 Files Tested

- `UBECtt_protocol.py` - Fire Element protocol service
- `ubec_main_protocol.py` - Main orchestrator

---

## Setup

### 1. Install Test Dependencies

```bash
pip install pytest pytest-asyncio
```

### 2. Place Test File

The test file can be placed in multiple locations:

**Option A: In project root** (Recommended)
```
UBEC_project/
├── test_compliance.py
├── UBECtt_protocol.py
├── ubec_main_protocol.py
└── ...
```

**Option B: In tests directory**
```
UBEC_project/
├── tests/
│   └── test_compliance.py
├── UBECtt_protocol.py
├── ubec_main_protocol.py
└── ...
```

---

## Running Tests

### Quick Test (All Tests)

```bash
# From project root
python test_compliance.py

# Or using pytest
pytest test_compliance.py -v
```

### Run Specific Test Class

```bash
# Test only design principles
pytest test_compliance.py::TestDesignPrincipleCompliance -v

# Test only async functionality
pytest test_compliance.py::TestAsyncFunctionality -v

# Generate compliance report
pytest test_compliance.py::TestComplianceSummary -v
```

### Run Specific Test

```bash
# Test a specific principle
pytest test_compliance.py::TestDesignPrincipleCompliance::test_principle_5_all_io_async -v

# Test attribution
pytest test_compliance.py::TestDesignPrincipleCompliance::test_principle_11_attribution -v
```

---

## Understanding Output

### ✅ Successful Test Output

```
tests/test_compliance.py::TestDesignPrincipleCompliance::test_principle_2_only_main_has_execution PASSED
tests/test_compliance.py::TestDesignPrincipleCompliance::test_principle_5_all_io_async PASSED
...
=============== 20 passed in 0.52s ===============
```

### ❌ Failed Test Output

```
FAILED tests/test_compliance.py::TestDesignPrincipleCompliance::test_principle_5_all_io_async
AssertionError: Async operation violations:
UBECtt_protocol.py: uses time.sleep() - should use asyncio.sleep()
```

This tells you:
- Which principle failed
- Which file has the violation
- What needs to be fixed

---

## Common Test Scenarios

### 1. Files Not Found

**Error:**
```
FileNotFoundError: Cannot find UBECtt_protocol.py
```

**Solution:**
- Ensure test file is in correct location
- Or run from directory containing the protocol files
- Or update `UPDATED_FILES` list in test to match your structure

### 2. Import Errors

**Error:**
```
ImportError: cannot import name 'GlobalConfig'
```

**Solution:**
- The test file is designed to NOT import from config
- If you see this, you're likely running the old test file
- Use the updated test_compliance.py from this package

### 3. Async Tests Skip

**Warning:**
```
SKIPPED [1] test_compliance.py: Async functionality test skipped
```

**Note:**
- This is normal if modules can't be imported
- Tests still validate code structure via AST parsing
- Functional tests would require full environment setup

---

## Test Categories

### 1. Structure Tests (Always Run)

These use AST parsing and don't require imports:
- ✅ Modular design
- ✅ Service pattern
- ✅ Method singularity
- ✅ Documentation
- ✅ Attribution

**Advantage:** Fast, no dependencies needed

### 2. Pattern Tests (Run if files found)

These check for specific code patterns:
- ✅ Async/await usage
- ✅ Rate limiting implementation
- ✅ Dependency injection
- ✅ Configuration management

**Advantage:** Validates implementation details

### 3. Functional Tests (Require full setup)

These actually run the code:
- ✅ Async operations work
- ✅ Concurrent execution
- ✅ Service registry

**Requirement:** Full environment with database, etc.

---

## Customization

### Test Your Own Files

Edit the `UPDATED_FILES` list:

```python
class TestDesignPrincipleCompliance:
    UPDATED_FILES = [
        'UBECtt_protocol.py',
        'ubec_main_protocol.py',
        'UBEC_protocol.py',  # Add your files here
        'UBECrc_protocol.py',
    ]
```

### Add Custom Tests

```python
def test_my_custom_principle(self):
    """
    Test a custom requirement
    """
    content = self.read_file_content('my_module.py')
    
    # Your test logic here
    assert 'expected_pattern' in content, \
        "Should have expected pattern"
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Compliance Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        pip install pytest pytest-asyncio
    
    - name: Run compliance tests
      run: |
        pytest test_compliance.py -v --tb=short
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python test_compliance.py
if [ $? -ne 0 ]; then
    echo "Compliance tests failed. Commit aborted."
    exit 1
fi
```

---

## Troubleshooting

### Test Failures

**1. "Uses time.sleep()"**
- Replace `time.sleep()` with `await asyncio.sleep()`

**2. "Uses sync requests"**
- Replace `requests` with `aiohttp`

**3. "Function too long"**
- Break down functions into smaller helper methods

**4. "Missing docstring"**
- Add docstrings to all public classes and methods

**5. "Missing attribution"**
- Add Claude/Anthropic attribution to file header

### Performance Issues

If tests are slow:

```bash
# Run only fast structure tests
pytest test_compliance.py::TestDesignPrincipleCompliance -v --ignore-glob="*async*"

# Skip functional tests
pytest test_compliance.py -v -k "not test_async"
```

---

## Test Coverage Report

### Generate HTML Report

```bash
pip install pytest-cov
pytest test_compliance.py --cov=. --cov-report=html
open htmlcov/index.html
```

### Generate Terminal Report

```bash
pytest test_compliance.py -v --tb=short --color=yes
```

---

## Best Practices

### 1. Run Tests Frequently

```bash
# During development
pytest test_compliance.py -v

# Before committing
pytest test_compliance.py

# Before pushing
pytest test_compliance.py -v --tb=short
```

### 2. Fix Issues Immediately

Don't accumulate violations. Fix them as they appear:

1. Run test
2. See failure
3. Fix code
4. Verify fix
5. Commit

### 3. Use Tests as Documentation

The tests document the design principles:

```python
# Read test to understand requirement
def test_principle_5_all_io_async(self):
    """All I/O methods use async/await"""
    # Implementation shows exactly what's required
```

### 4. Add Tests for New Modules

When creating new protocol modules:

1. Add to `UPDATED_FILES` list
2. Run tests
3. Fix violations
4. Commit with passing tests

---

## Expected Output

### All Tests Passing

```
============================================ test session starts =============================================
platform linux -- Python 3.11.2, pytest-8.4.2, pluggy-1.6.0
collected 20 items

test_compliance.py::TestDesignPrincipleCompliance::test_principle_1_modular_boundaries PASSED        [  5%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_2_only_main_has_execution PASSED   [ 10%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_2_service_factory_pattern PASSED   [ 15%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_3_service_registry_exists PASSED   [ 20%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_3_dependency_injection PASSED      [ 25%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_4_database_authoritative PASSED    [ 30%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_5_all_io_async PASSED             [ 35%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_5_async_method_count PASSED       [ 40%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_6_no_backward_compatibility PASSED [ 45%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_8_config_injection PASSED         [ 50%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_9_rate_limiter_exists PASSED      [ 55%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_10_layer_separation PASSED        [ 60%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_11_attribution PASSED             [ 65%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_11_docstrings PASSED              [ 70%]
test_compliance.py::TestDesignPrincipleCompliance::test_principle_12_no_duplicate_methods PASSED    [ 75%]
test_compliance.py::TestAsyncFunctionality::test_async_operations_work PASSED                       [ 80%]
test_compliance.py::TestAsyncFunctionality::test_concurrent_operations PASSED                       [ 85%]
test_compliance.py::TestComplianceSummary::test_generate_compliance_report PASSED                   [ 90%]

======================================================================
DESIGN PRINCIPLES COMPLIANCE REPORT
======================================================================

Principles Tested:
  ✓ 1. Modular Design and Architecture
  ✓ 2. Service Pattern with Centralized Execution
  ✓ 3. Service Registry for Dependencies
  ✓ 4. Single Source of Truth
  ✓ 5. Strict Async Operations
  ✓ 6. No Sync Fallbacks or Backward Compatibility
  ✓ 7. Per-Asset Monitoring (tested in integration)
  ✓ 8. No Duplicate Configuration
  ✓ 9. Integrated Rate Limiting
  ✓ 10. Clear Separation of Concerns
  ✓ 11. Comprehensive Documentation
  ✓ 12. Method Singularity (No Redundancy)

Files Tested:
  ✓ UBECtt_protocol.py (Fire Element)
  ✓ ubec_main_protocol.py (Main Orchestrator)

======================================================================
All tests passed = 100% Compliance ✅
======================================================================

============================================= 20 passed in 0.84s =============================================
```

---

## Summary

The compliance test suite provides:

✅ **Automated validation** of all 12 design principles  
✅ **Fast feedback** during development  
✅ **Clear error messages** for violations  
✅ **AST-based checking** (no imports required)  
✅ **Functional tests** for async operations  
✅ **Compliance report** generation  

Use it regularly to maintain 100% compliance! 🎯

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

**Last Updated:** October 10, 2025  
**Test Suite Version:** 1.0.0  
**Compatible With:** UBECtt v2.0.0, ubec_main_protocol v2.0.0
