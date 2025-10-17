# UBEC Health Check - Quick Reference Card

## 🚀 Three Magic Patterns

### Pattern 1: Basic Service (No Dependencies)
```python
from core.utils.service_health import ServiceHealthCheck

async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.basic_health_check(
        service_name='my_service',
        is_initialized=self._initialized,
        # Add any custom metrics here
        cache_size=len(self._cache)
    )
```

### Pattern 2: Database Service
```python
from core.utils.service_health import ServiceHealthCheck

async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.database_dependent_health(
        service_name='my_service',
        db_manager=self.db,  # or self._db or self.db_manager
        is_initialized=self._initialized
    )
```

### Pattern 3: Element Protocol
```python
from core.utils.service_health import ServiceHealthCheck
from datetime import datetime

async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.element_protocol_health(
        element_name='fire',  # or 'air', 'water', 'earth'
        token_code='UBECtt',  # or 'UBEC', 'UBECrc', 'UBECgpi'
        db_manager=self.db,
        is_initialized=self._initialized,
        last_sync=getattr(self, 'last_sync', None),
        cached_accounts=len(getattr(self, '_cache', {})),
        ubuntu_principle='regeneration'  # or 'diversity', 'reciprocity', 'mutualism'
    )
```

---

## 📋 Implementation Checklist

### Step 1: Deploy Files (5 min)
```bash
cd ~/UBEC/projects/UBEC
cp service_health.py core/utils/service_health.py
cp config.py config/config.py
```

### Step 2: Add Import (1 line per file)
```python
from core.utils.service_health import ServiceHealthCheck
```

### Step 3: Add Method (5-10 lines per service)
```python
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.[TYPE]_health(...)
```

### Step 4: Test
```bash
python main.py --mode health
```

---

## 🎯 Service-by-Service Map

| Service | Pattern | Database Attr | Time |
|---------|---------|---------------|------|
| config | ✅ DONE | N/A | 0 min |
| visualizer | basic | N/A | 5 min |
| analytics | database | self.db | 5 min |
| synchronizer | database | self.db | 5 min |
| audit | database | self.db | 5 min |
| distribution | database | self.db | 5 min |
| air | element | self.db | 10 min |
| water | element | self.db | 10 min |
| earth | element | self.db | 10 min |
| fire | element | self.db | 10 min |
| stellar_client | api | N/A | 10 min |
| orderbook | database | self.db_manager | 10 min |
| holonic_evaluator | database | self.db | 10 min |
| distribution_evaluator | database | self.db | 10 min |

**Total Time:** 2 hours

---

## 🔥 Copy-Paste Templates

### Template A: Basic Service
```python
# Add at top of file
from core.utils.service_health import ServiceHealthCheck
from typing import Dict, Any

# Add to class
async def health_check(self) -> Dict[str, Any]:
    """Health check for [SERVICE_NAME] service."""
    return await ServiceHealthCheck.basic_health_check(
        service_name='[SERVICE_NAME]',
        is_initialized=self._initialized
    )
```

### Template B: Database Service
```python
# Add at top of file
from core.utils.service_health import ServiceHealthCheck
from typing import Dict, Any

# Add to class
async def health_check(self) -> Dict[str, Any]:
    """Health check for [SERVICE_NAME] service."""
    return await ServiceHealthCheck.database_dependent_health(
        service_name='[SERVICE_NAME]',
        db_manager=self.db,
        is_initialized=self._initialized
    )
```

### Template C: Element Protocol
```python
# Add at top of file
from core.utils.service_health import ServiceHealthCheck
from typing import Dict, Any
from datetime import datetime

# Add to class
async def health_check(self) -> Dict[str, Any]:
    """Health check for [ELEMENT] protocol ([TOKEN] - [PRINCIPLE])."""
    return await ServiceHealthCheck.element_protocol_health(
        element_name='[ELEMENT]',
        token_code='[TOKEN]',
        db_manager=self.db,
        is_initialized=self._initialized,
        last_sync=getattr(self, 'last_sync', None),
        cached_accounts=len(getattr(self, '_cache', {})),
        ubuntu_principle='[PRINCIPLE]'
    )
```

Replace:
- `[SERVICE_NAME]` → actual service name
- `[ELEMENT]` → air, water, earth, or fire
- `[TOKEN]` → UBEC, UBECrc, UBECgpi, or UBECtt
- `[PRINCIPLE]` → diversity, reciprocity, mutualism, or regeneration

---

## 🎨 Element Reference

| Element | Token | Principle | Symbol |
|---------|-------|-----------|--------|
| Air | UBEC | diversity | 🜁 |
| Water | UBECrc | reciprocity | 🜄 |
| Earth | UBECgpi | mutualism | 🜃 |
| Fire | UBECtt | regeneration | 🜂 |

---

## ✅ Test Commands

```bash
# Full health check
python main.py --mode health

# Quick test (check if import works)
python3 -c "from core.utils.service_health import ServiceHealthCheck; print('✓')"

# Check specific service class
python3 -c "from services.analytics.ubec_analytics_service import UBECAnalyticsService; print(hasattr(UBECAnalyticsService, 'health_check'))"
```

---

## 🐛 Common Issues

### Issue: "No module named 'core.utils.service_health'"
```bash
# Solution: Check file location
ls -la core/utils/service_health.py
```

### Issue: "Service still shows 'unknown'"
```bash
# Solution: Check method name
python3 -c "from services.X import Y; print(dir(Y))"
# Look for 'health_check' in output
```

### Issue: "AttributeError: 'self' has no attribute 'db'"
```python
# Solution: Find correct attribute name
# Try: self.db, self._db, self.db_manager, self.database
```

---

## 📊 Progress Tracking

### After Each Phase

```bash
python main.py --mode health | grep "services healthy"
```

**Expected progression:**
- Start: `1/15 services healthy`
- Phase 1: `3/15 services healthy`
- Phase 2: `7/15 services healthy`
- Phase 3: `11/15 services healthy`
- Phase 4: `15/15 services healthy` ✨

---

## 🎉 Success Output

```
"overall_status": "healthy",
"summary": {
  "total": 15,
  "healthy": 15,
  "unhealthy": 0,
  "unknown": 0
}
```

---

## 💡 Pro Tips

1. **Work in phases** - Test after every 2-3 services
2. **Copy exactly** - Don't modify the patterns
3. **Check indentation** - Python is strict
4. **Save often** - Ctrl+S after each change
5. **Use git** - Commit after each phase

---

## ⏱️ Time Estimates

- Deploy files: 5 min
- Simple services (2): 20 min
- Database services (4): 40 min
- Element protocols (4): 40 min
- Advanced services (4): 40 min
- **Total: ~2 hours**

---

## 📞 Quick Help

**Stuck?** Check these in order:

1. Is `service_health.py` in `core/utils/`?
2. Did you add the import at the top?
3. Is the method called exactly `health_check`?
4. Is it indented at class level?
5. Is it `async def` (not just `def`)?
6. Does the service have `self._initialized`?

---

**Transform your system from degraded to healthy!** 🚀

**Start now:** Copy Template B, replace `[SERVICE_NAME]`, test!
