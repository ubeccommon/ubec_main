# Health Check Implementation Action Plan

## 🎯 Objective
Fix system health monitoring by adding health_check() methods to 14 services, changing status from "degraded" to "healthy".

**Current State:** 1/15 services healthy  
**Target State:** 15/15 services healthy  
**Time Required:** ~2 hours  
**Complexity:** Low

---

## 📋 Prerequisites

1. **Copy the utility file:**
   ```bash
   # The service_health.py utility has been created at:
   cp /home/claude/core/utils/service_health.py ~/UBEC/projects/UBEC/core/utils/
   ```

2. **Review example:**
   ```bash
   # See complete before/after example at:
   cat /home/claude/examples/health_check_example_config_service.py
   ```

---

## ⚡ Quick Implementation (14 Services)

### Phase 1: Simple Services (20 min)

#### 1. Config Service (5 min)
**File:** `config/ubec_config.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECConfigService class
def health_check(self) -> Dict[str, Any]:
    return ServiceHealthCheck.sync_basic_health_check(
        service_name='config',
        is_initialized=True,
        config_loaded=bool(self._config),
        num_sections=len(self._config)
    )
```

#### 2. Visualizer Service (5 min)
**File:** `services/visualizer/ubec_visualizer_service.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECVisualizerService class
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.basic_health_check(
        service_name='visualizer',
        is_initialized=self._initialized
    )
```

---

### Phase 2: Database Services (40 min)

#### 3. Analytics Service (10 min)
**File:** `services/analytics/ubec_analytics_service.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECAnalyticsService class
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.database_dependent_health(
        service_name='analytics',
        db_manager=self.db,
        is_initialized=self._initialized
    )
```

#### 4. Synchronizer Service (10 min)
**File:** `core/db/ubec_data_synchronizer.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECDataSynchronizer class
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.database_dependent_health(
        service_name='synchronizer',
        db_manager=self.db,
        is_initialized=self._initialized
    )
```

#### 5. Audit Service (10 min)
**File:** `services/audit/ubec_audit_service.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECAuditService class
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.database_dependent_health(
        service_name='audit',
        db_manager=self.db,
        is_initialized=self._initialized,
        last_snapshot=self._last_snapshot_time.isoformat() if self._last_snapshot_time else None
    )
```

#### 6. Distribution Service (10 min)
**File:** `services/distribution/ubec_distribution_service.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECDistributionService class
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.database_dependent_health(
        service_name='distribution',
        db_manager=self.db,
        is_initialized=self._initialized
    )
```

---

### Phase 3: Element Protocol Services (40 min)

#### 7. Air Protocol (UBEC) (10 min)
**File:** `core/protocols/UBEC_protocol.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECProtocolService class
async def health_check(self) -> Dict[str, Any]:
    cache_info = {
        'size': len(self._cache),
        'last_sync': self._last_sync_time.isoformat() if hasattr(self, '_last_sync_time') and self._last_sync_time else None
    }
    
    return await ServiceHealthCheck.api_dependent_health(
        service_name='air_protocol',
        is_initialized=self._initialized,
        rate_limiter=self._rate_limiter,
        cache_info=cache_info,
        asset_code='UBEC',
        element='Air (Gateway)'
    )
```

#### 8. Water Protocol (UBECrc) (10 min)
**File:** `core/protocols/UBECrc_protocol.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECrcProtocolService class
async def health_check(self) -> Dict[str, Any]:
    cache_info = {
        'size': len(self._cache),
        'last_sync': self._last_sync_time.isoformat() if hasattr(self, '_last_sync_time') and self._last_sync_time else None
    }
    
    return await ServiceHealthCheck.api_dependent_health(
        service_name='water_protocol',
        is_initialized=self._initialized,
        rate_limiter=self._rate_limiter,
        cache_info=cache_info,
        asset_code='UBECrc',
        element='Water (Flow)'
    )
```

#### 9. Earth Protocol (UBECgpi) (10 min)
**File:** `core/protocols/UBECgpi_protocol.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECgpiProtocolService class
async def health_check(self) -> Dict[str, Any]:
    cache_info = {
        'size': len(self._cache),
        'last_sync': self._last_sync_time.isoformat() if hasattr(self, '_last_sync_time') and self._last_sync_time else None
    }
    
    return await ServiceHealthCheck.api_dependent_health(
        service_name='earth_protocol',
        is_initialized=self._initialized,
        rate_limiter=self._rate_limiter,
        cache_info=cache_info,
        asset_code='UBECgpi',
        element='Earth (Stability)'
    )
```

#### 10. Fire Protocol (UBECtt) (10 min)
**File:** `core/protocols/UBECtt_protocol.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECttProtocolService class
async def health_check(self) -> Dict[str, Any]:
    cache_info = {
        'size': len(self._cache),
        'last_sync': self._last_sync_time.isoformat() if hasattr(self, '_last_sync_time') and self._last_sync_time else None
    }
    
    return await ServiceHealthCheck.api_dependent_health(
        service_name='fire_protocol',
        is_initialized=self._initialized,
        rate_limiter=self._rate_limiter,
        cache_info=cache_info,
        asset_code='UBECtt',
        element='Fire (Transformation)'
    )
```

---

### Phase 4: Advanced Services (20 min)

#### 11. Stellar Client (5 min)
**File:** `core/stellar/stellar_client.py` (or wherever stellar client is defined)
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to stellar client class
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.api_dependent_health(
        service_name='stellar_client',
        is_initialized=self._initialized if hasattr(self, '_initialized') else True,
        network=getattr(self, 'network', 'unknown')
    )
```

#### 12. OrderBook Service (5 min)
**File:** `services/orderbook/ubec_orderbook_service.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to OrderBookService class
async def health_check(self) -> Dict[str, Any]:
    cache_info = {
        'size': len(getattr(self, '_cache', {})),
        'last_update': getattr(self, '_last_update', None)
    }
    
    return await ServiceHealthCheck.api_dependent_health(
        service_name='orderbook',
        is_initialized=self._initialized,
        cache_info=cache_info,
        has_database=True
    )
```

#### 13. Holonic Evaluator (5 min)
**File:** `core/holonic/ubec_holonic_evaluator.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECHolonicEvaluator class
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.database_dependent_health(
        service_name='holonic_evaluator',
        db_manager=self.db,
        is_initialized=self._initialized,
        holders_loaded=len(getattr(self, 'holders_data', {}))
    )
```

#### 14. Distribution Evaluator (5 min)
**File:** `services/distribution/ubec_distribution_evaluator.py`
```python
# Add import
from core.utils.service_health import ServiceHealthCheck

# Add method to UBECDistributionEvaluator class
async def health_check(self) -> Dict[str, Any]:
    return await ServiceHealthCheck.database_dependent_health(
        service_name='distribution_evaluator',
        db_manager=self.db,
        is_initialized=self._initialized
    )
```

---

## ✅ Testing Each Phase

After implementing each phase, test:

```bash
python main.py --mode health
```

**Expected progression:**
- After Phase 1: 3/15 healthy
- After Phase 2: 7/15 healthy
- After Phase 3: 11/15 healthy
- After Phase 4: 15/15 healthy ✨

---

## 🎉 Success Criteria

```json
{
  "overall_status": "healthy",
  "summary": {
    "total": 15,
    "healthy": 15,
    "unhealthy": 0,
    "unknown": 0
  }
}
```

---

## 🔧 Troubleshooting

### Issue: Import error
```
ModuleNotFoundError: No module named 'core.utils.service_health'
```
**Solution:** Ensure service_health.py is in `core/utils/` directory

### Issue: Service still shows "unknown"
**Possible causes:**
1. Method not named exactly `health_check`
2. Method not accessible (indentation issue)
3. Service class name mismatch

**Solution:** Verify method is at class level, properly indented, and named `health_check`

### Issue: Async/sync mismatch
```
RuntimeWarning: coroutine 'health_check' was never awaited
```
**Solution:** 
- For async services: `async def health_check(...)`
- For sync services (like config): `def health_check(...)`

---

## 📊 Implementation Checklist

- [ ] Phase 1: Simple Services (config, visualizer)
- [ ] Test: 3/15 healthy
- [ ] Phase 2: Database Services (analytics, synchronizer, audit, distribution)
- [ ] Test: 7/15 healthy
- [ ] Phase 3: Element Protocols (air, water, earth, fire)
- [ ] Test: 11/15 healthy
- [ ] Phase 4: Advanced Services (stellar_client, orderbook, holonic_evaluator, distribution_evaluator)
- [ ] Test: 15/15 healthy ✨
- [ ] Final verification: Run full system health check
- [ ] Document any custom metrics added

---

## 📚 Reference Documents

1. **Utility Module:** `/home/claude/core/utils/service_health.py`
2. **Complete Guide:** `/home/claude/docs/HEALTH_CHECK_IMPLEMENTATION_GUIDE.md`
3. **Example:** `/home/claude/examples/health_check_example_config_service.py`

---

## 💡 Key Takeaways

1. **One import per file:**
   ```python
   from core.utils.service_health import ServiceHealthCheck
   ```

2. **One method per service:**
   ```python
   async def health_check(self) -> Dict[str, Any]:
       return await ServiceHealthCheck.xxx_health(...)
   ```

3. **Three patterns:**
   - `basic_health_check` → Simple services
   - `database_dependent_health` → DB services
   - `api_dependent_health` → API services

4. **Test frequently:**
   ```bash
   python main.py --mode health
   ```

---

**Total estimated time:** 2 hours
**Difficulty:** Low
**Impact:** High (Production monitoring ready)

---

*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.*
