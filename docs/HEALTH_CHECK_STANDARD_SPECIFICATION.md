# 📋 Technical Specification: Element Protocol Health Check Standard

## Document Information

**Title:** UBEC Element Protocol Health Check Implementation Standard  
**Version:** 1.0  
**Date:** October 19, 2025  
**Status:** Approved  
**Applies To:** All element protocols (Air, Water, Earth, Fire, and future protocols)

---

## 1. Overview

This document defines the **mandatory standard** for implementing health check methods in all UBEC element protocols. This standard ensures consistency, maintainability, and comprehensive monitoring across the entire UBEC ecosystem.

---

## 2. Objectives

1. **Consistency:** All protocols use identical health check patterns
2. **DRY Compliance:** No duplicate element metadata (Principle #8)
3. **Comprehensive Monitoring:** Complete visibility into protocol health
4. **Error Tracking:** Full error forensics and debugging capability
5. **Trust Verification:** Asset issuer visibility in all health checks
6. **Method Singularity:** Shared ServiceHealthCheck utility (Principle #12)

---

## 3. Mandatory Requirements

### 3.1 Method Signature

```python
async def health_check(self) -> Dict[str, Any]:
    """
    Comprehensive health check using standardized ServiceHealthCheck utility.
    
    This method implements Principle #12 (Method Singularity) by delegating
    to the shared ServiceHealthCheck utility instead of implementing custom
    health check logic.
    
    Returns:
        Health status dictionary with standardized format
    """
```

### 3.2 Implementation Pattern

**MANDATORY:** All protocols MUST use this exact pattern:

```python
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.element_protocol_health(
        # === REQUIRED PARAMETERS ===
        element_name=self.element,                      # ✅ Instance variable (NOT hardcoded)
        token_code=self.asset_code,                     # ✅ Asset code
        db_manager=self.db_manager,                     # ✅ Database manager
        
        # === RECOMMENDED PARAMETERS ===
        is_initialized=self._initialized,               # Initialization status
        last_sync=self._last_sync_time,                 # Last sync timestamp
        cached_accounts=len(self._account_cache),       # Cache size
        
        # === ELEMENT METADATA ===
        ubuntu_principle=self.ubuntu_principle,         # ✅ Instance variable (NOT hardcoded)
        element_description=self.element_description,   # ✅ Instance variable (NOT hardcoded)
        symbol=self.symbol,                             # ✅ Instance variable (NOT hardcoded)
        
        # === ISSUER VERIFICATION ===
        issuer=self.issuer[:12] + '...' if len(self.issuer) > 12 else self.issuer,  # ✅ Truncated issuer
        
        # === OPERATION STATISTICS ===
        sync_count=self._sync_count,                    # Sync operation counter
        query_count=self._query_count,                  # Query counter
        error_count=self._error_count,                  # Error counter
        
        # === ERROR TRACKING ===
        last_error=self._last_error,                    # ✅ Last error message
        last_error_time=self._last_error_time.isoformat() if self._last_error_time else None  # ✅ Error timestamp
    )
```

---

## 4. Parameter Specifications

### 4.1 Required Parameters

| Parameter | Type | Source | Purpose |
|-----------|------|--------|---------|
| `element_name` | `str` | `self.element` | Element identifier |
| `token_code` | `str` | `self.asset_code` | Asset/token code |
| `db_manager` | `AsyncDatabaseManager` | `self.db_manager` | Database instance |

**CRITICAL:** These parameters are REQUIRED. Health check will fail without them.

---

### 4.2 Recommended Parameters

| Parameter | Type | Source | Purpose |
|-----------|------|--------|---------|
| `is_initialized` | `bool` | `self._initialized` | Service initialization status |
| `last_sync` | `datetime` | `self._last_sync_time` | Last synchronization timestamp |
| `cached_accounts` | `int` | `len(self._account_cache)` | Number of cached accounts |

**Recommendation:** ALWAYS include these for comprehensive monitoring.

---

### 4.3 Element Metadata Parameters

| Parameter | Type | Source | Purpose |
|-----------|------|--------|---------|
| `ubuntu_principle` | `str` | `self.ubuntu_principle` | Associated Ubuntu principle |
| `element_description` | `str` | `self.element_description` | Element description |
| `symbol` | `str` | `self.symbol` | Alchemical symbol |

**CRITICAL:** MUST use instance variables (self.*), NOT hardcoded strings.  
**Rationale:** DRY principle compliance (Principle #8)

---

### 4.4 Issuer Verification

| Parameter | Type | Source | Purpose |
|-----------|------|--------|---------|
| `issuer` | `str` | `self.issuer[:12] + '...'` | Truncated issuer address |

**Format:** First 12 characters + '...' for display  
**Purpose:** Asset verification and trust establishment

---

### 4.5 Operation Statistics

| Parameter | Type | Source | Purpose |
|-----------|------|--------|---------|
| `sync_count` | `int` | `self._sync_count` | Number of sync operations |
| `query_count` | `int` | `self._query_count` | Number of queries performed |
| `error_count` | `int` | `self._error_count` | Number of errors encountered |

**Purpose:** Operational monitoring and performance tracking

---

### 4.6 Error Tracking

| Parameter | Type | Source | Purpose |
|-----------|------|--------|---------|
| `last_error` | `str \| None` | `self._last_error` | Last error message |
| `last_error_time` | `str \| None` | `self._last_error_time.isoformat()` | Last error timestamp (ISO) |

**Format:** ISO 8601 timestamp string  
**Purpose:** Error forensics and debugging

---

## 5. Instance Variable Requirements

### 5.1 Mandatory Instance Variables

All protocols MUST define these in `__init__`:

```python
def __init__(self, db_manager, config, stellar_client=None, **kwargs):
    # Element metadata (REQUIRED)
    self.element = '<element_name>'              # e.g., 'water', 'air', 'earth', 'fire'
    self.ubuntu_principle = '<principle>'        # e.g., 'reciprocity', 'diversity', etc.
    self.element_description = '<description>'   # Brief element description
    self.symbol = '<symbol>'                     # Alchemical symbol emoji
    
    # Configuration (REQUIRED)
    self.asset_code = config.get('asset_code', '<DEFAULT>')
    self.issuer = config.get('issuer', '')
    self.db_manager = db_manager
    
    # Operation tracking (REQUIRED)
    self._initialized = False
    self._last_sync_time: Optional[datetime] = None
    self._sync_count = 0
    self._query_count = 0
    self._error_count = 0
    self._last_error: Optional[str] = None
    self._last_error_time: Optional[datetime] = None
    
    # Cache (REQUIRED)
    self._account_cache: Dict[str, Any] = {}
```

---

## 6. Return Value Specification

### 6.1 Response Structure

The ServiceHealthCheck utility returns a standardized dictionary:

```python
{
    "status": str,           # 'healthy' | 'degraded' | 'unhealthy' | 'unknown'
    "message": str,          # Human-readable status message
    "timestamp": str,        # ISO 8601 timestamp
    "details": {
        # Core health metrics
        "initialized": bool,
        "has_db": bool,
        "db_connection": bool,
        "db_response_time_ms": float,
        
        # Element metadata
        "element": str,
        "ubuntu_principle": str,
        "symbol": str,
        "element_description": str,
        
        # Issuer verification
        "issuer": str,
        
        # Operation statistics
        "sync_count": int,
        "query_count": int,
        "error_count": int,
        
        # Error tracking
        "last_error": str | None,
        "last_error_time": str | None,
        
        # Cache information
        "cached_accounts": int,
        "last_sync": str | None,
        
        # Additional protocol-specific metrics
        # (passed via **kwargs)
    }
}
```

---

## 7. Anti-Patterns (Prohibited)

### 7.1 ❌ Hardcoded Strings

**PROHIBITED:**
```python
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.element_protocol_health(
        element_name="Water",              # ❌ WRONG
        ubuntu_principle="Reciprocity",    # ❌ WRONG
        element_symbol="🜄",               # ❌ WRONG
        # ...
    )
```

**CORRECT:**
```python
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.element_protocol_health(
        element_name=self.element,         # ✅ CORRECT
        ubuntu_principle=self.ubuntu_principle,  # ✅ CORRECT
        symbol=self.symbol,                # ✅ CORRECT
        # ...
    )
```

**Rationale:** Violates DRY principle (Principle #8). Element metadata should be defined once in `__init__`.

---

### 7.2 ❌ Missing Required Parameters

**PROHIBITED:**
```python
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.element_protocol_health(
        element_name=self.element,
        token_code=self.asset_code
        # ❌ MISSING: db_manager (REQUIRED!)
    )
```

**CORRECT:**
```python
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.element_protocol_health(
        element_name=self.element,
        token_code=self.asset_code,
        db_manager=self.db_manager,  # ✅ REQUIRED
        # ...
    )
```

**Rationale:** Database health checks impossible without db_manager parameter.

---

### 7.3 ❌ Incomplete Error Tracking

**PROHIBITED:**
```python
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.element_protocol_health(
        # ... other parameters ...
        error_count=self._error_count
        # ❌ MISSING: last_error, last_error_time
    )
```

**CORRECT:**
```python
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.element_protocol_health(
        # ... other parameters ...
        error_count=self._error_count,
        last_error=self._last_error,  # ✅ Added
        last_error_time=self._last_error_time.isoformat() if self._last_error_time else None  # ✅ Added
    )
```

**Rationale:** Complete error tracking enables forensics and debugging.

---

## 8. Implementation Checklist

Use this checklist when implementing or reviewing health checks:

### Element Protocol Health Check Compliance

- [ ] Uses `ServiceHealthCheck.element_protocol_health()` utility
- [ ] Includes all 3 REQUIRED parameters (element_name, token_code, db_manager)
- [ ] Uses instance variables for element metadata (NO hardcoded strings)
- [ ] Includes initialization status (`is_initialized`)
- [ ] Includes last sync time (`last_sync`)
- [ ] Includes cached accounts count (`cached_accounts`)
- [ ] Includes Ubuntu principle (`ubuntu_principle`) from instance variable
- [ ] Includes element description (`element_description`) from instance variable
- [ ] Includes symbol (`symbol`) from instance variable
- [ ] Includes truncated issuer (`issuer`)
- [ ] Includes operation statistics (`sync_count`, `query_count`, `error_count`)
- [ ] Includes error tracking (`last_error`, `last_error_time`)
- [ ] Method is async (`async def health_check`)
- [ ] Returns `Dict[str, Any]`
- [ ] Has comprehensive docstring
- [ ] Version number updated
- [ ] Changelog updated

---

## 9. Testing Requirements

### 9.1 Unit Tests

All protocols MUST have unit tests verifying:

```python
async def test_health_check_uses_instance_variables():
    """Verify health check uses instance variables, not hardcoded strings."""
    service = await create_protocol_service(...)
    health = await service.health_check()
    
    # Verify element metadata comes from instance variables
    assert health['details']['element'] == service.element
    assert health['details']['ubuntu_principle'] == service.ubuntu_principle
    assert health['details']['symbol'] == service.symbol

async def test_health_check_includes_error_tracking():
    """Verify health check includes error tracking fields."""
    service = await create_protocol_service(...)
    health = await service.health_check()
    
    # Verify error tracking fields present
    assert 'last_error' in health['details']
    assert 'last_error_time' in health['details']

async def test_health_check_includes_issuer():
    """Verify health check includes issuer information."""
    service = await create_protocol_service(...)
    health = await service.health_check()
    
    # Verify issuer field present
    assert 'issuer' in health['details']
    assert health['details']['issuer'] is not None
```

---

## 10. Design Principles Compliance

This standard enforces compliance with:

| Principle | How Standard Enforces It |
|-----------|--------------------------|
| **#7: Per-Asset Monitoring** | Comprehensive health metrics for each protocol |
| **#8: No Duplicate Config** | Instance variables (no hardcoded strings) |
| **#10: Separation of Concerns** | Health logic in ServiceHealthCheck utility |
| **#11: Documentation** | Mandatory docstrings and comments |
| **#12: Method Singularity** | Single shared ServiceHealthCheck utility |

---

## 11. Reference Implementation

**Air Protocol (UBEC)** serves as the reference implementation:
- File: `core/protocols/UBEC_protocol.py`
- Method: `async def health_check()`
- Status: Approved reference standard

All new protocols should use Air protocol's health check as a template.

---

## 12. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-19 | Initial standard established |

---

## 13. Enforcement

This standard is **MANDATORY** for:
- All existing element protocols (Air, Water, Earth, Fire)
- All future element protocols
- All protocol updates and enhancements

**Review Process:**
1. All protocol pull requests MUST pass compliance checklist
2. Code reviews MUST verify adherence to this standard
3. CI/CD pipeline SHOULD include automated compliance checks

---

## 14. Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

**Document Status:** Approved ✅  
**Effective Date:** October 19, 2025  
**Next Review:** January 19, 2026
