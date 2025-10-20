# 🚀 UBEC Main.py - Quick Reference Guide

**For Developers Working with the UBEC Protocol System**

---

## 📋 Quick Start

### Running the System
```bash
# Health check (recommended first run)
python main.py --mode health

# System status
python main.py --mode status

# Sync data from blockchain
python main.py --mode sync --sync-type all

# Generate analytics
python main.py --mode analytics --analysis-type summary
```

---

## 🏗️ Adding a New Service

### Step 1: Create Your Service Module
```python
# services/myservice/my_service.py
class MyService:
    def __init__(self, db_manager, config):
        self.db = db_manager
        self.config = config
        self._initialized = False
    
    async def initialize(self):
        """Initialize service resources."""
        # Your initialization code
        self._initialized = True
    
    async def health_check(self):
        """Use ServiceHealthCheck utility."""
        from core.utils.service_health import ServiceHealthCheck
        return await ServiceHealthCheck.database_dependent_health(
            service_name="my_service",
            db_manager=self.db,
            is_initialized=self._initialized
        )
    
    async def close(self):
        """Cleanup resources."""
        self._initialized = False

# Factory function
def create_my_service(db_manager, config):
    """Factory to create service instance."""
    service = MyService(db_manager, config)
    return service  # Return instance for initialization
```

### Step 2: Register in main.py
```python
# In register_core_services() function

async def create_myservice(registry: ServiceRegistry):
    """Create my service."""
    from services.myservice.my_service import create_my_service
    
    db = await registry.get('database')
    config = await registry.get('config')
    
    logger.info("  ├─ MyService: Description here")
    
    service = create_my_service(db_manager=db, config=config)
    
    # Call initialize if service has it
    if hasattr(service, 'initialize'):
        await service.initialize()
    
    return service

registry.register_factory(
    'myservice',
    create_myservice,
    dependencies=['database', 'config'],
    config={'some_param': 'value'}
)
logger.info("✓ Registered: myservice (depends on: database, config)")
```

### Step 3: Add to Required Services
```python
# In validate_service_registration() function
required_services = [
    'database', 'config', 'stellar_client',
    'air', 'water', 'earth', 'fire',
    'synchronizer', 'analytics', 'distribution',
    'distribution_evaluator', 'holonic_evaluator',
    'visualizer', 'audit',
    'myservice'  # Add your service here
]
```

### Step 4: Add Operation Handler (Optional)
```python
async def run_myservice_operation(param1, param2) -> Dict[str, Any]:
    """Run my service operation."""
    logger.info(f"\nRunning my service operation: {param1}, {param2}")
    
    try:
        myservice = await registry.get('myservice')
        result = await myservice.do_something(param1, param2)
        
        logger.info("✓ Operation completed successfully")
        return create_response(True, data=result)
        
    except Exception as e:
        logger.error(f"✗ Operation failed: {e}", exc_info=True)
        return create_response(False, error=str(e))

# Add to main_async() routing
elif args.mode == 'myoperation':
    result = await run_myservice_operation(args.param1, args.param2)
```

---

## 🔧 Common Patterns

### Pattern 1: Service with Async Factory
```python
# In your service module
async def create_my_service(db_manager, config):
    """Async factory function."""
    service = MyService(db_manager, config)
    await service.initialize()
    return service

# In main.py
async def create_myservice(registry: ServiceRegistry):
    from services.myservice import create_my_service
    db = await registry.get('database')
    config = await registry.get('config')
    
    # IMPORTANT: Use await for async factories
    return await create_my_service(db, config)
```

### Pattern 2: Service with Sync Factory + Init
```python
# In your service module
def create_my_service(db_manager, config):
    """Sync factory function."""
    return MyService(db_manager, config)

# In main.py
async def create_myservice(registry: ServiceRegistry):
    from services.myservice import create_my_service
    db = await registry.get('database')
    config = await registry.get('config')
    
    # NO await for sync factories
    service = create_my_service(db, config)
    
    # But DO await initialize if service has it
    await service.initialize()
    
    return service
```

### Pattern 3: Service with No Init Required
```python
# In your service module
def create_my_service(db_manager, config):
    """Factory that returns ready-to-use service."""
    service = MyService(db_manager, config)
    # Service is ready immediately
    return service

# In main.py
async def create_myservice(registry: ServiceRegistry):
    from services.myservice import create_my_service
    db = await registry.get('database')
    config = await registry.get('config')
    
    # Just return the service
    return create_my_service(db, config)
```

---

## 🎯 Decision Tree: Await or Not?

```
┌─────────────────────────────────────┐
│ Is the factory function async def?  │
└─────────────┬───────────────────────┘
              │
              ├─ YES → Use await
              │        service = await create_service(...)
              │
              └─ NO → Don't use await
                       service = create_service(...)
                       
┌─────────────────────────────────────┐
│ Does service have initialize()?     │
└─────────────┬───────────────────────┘
              │
              ├─ YES → Call it with await
              │        await service.initialize()
              │
              └─ NO → Just return service
                      return service
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ WRONG: Awaiting a sync function
```python
# This will FAIL
service = await create_ubecgpi_service(...)  # create_ubecgpi_service is NOT async
```

### ✅ RIGHT: Check if factory is async
```python
# Check the function signature first
def create_ubecgpi_service(...):  # def = sync
    ...

async def create_ubecrc_service(...):  # async def = async
    ...

# Then use appropriately
service = create_ubecgpi_service(...)      # sync - no await
service = await create_ubecrc_service(...) # async - use await
```

### ❌ WRONG: Not calling initialize
```python
# Some services NEED initialize() to be called
service = create_water_service(...)
return service  # WRONG - not initialized!
```

### ✅ RIGHT: Call initialize when needed
```python
service = await create_water_service(...)
await service.initialize()  # Initialize before returning
return service
```

### ❌ WRONG: Forgetting to add to required_services
```python
# Service registered but not validated
registry.register_factory('myservice', create_myservice, ...)
# Missing from required_services list = validation fails
```

### ✅ RIGHT: Add to validation list
```python
required_services = [
    'database', 'config', 'stellar_client',
    ...,
    'myservice'  # Always add new services here
]
```

---

## 🏥 Health Check Implementation

### Using ServiceHealthCheck Utility

```python
from core.utils.service_health import ServiceHealthCheck

class MyService:
    async def health_check(self):
        """Comprehensive health check using utility."""
        
        # For database-dependent services
        return await ServiceHealthCheck.database_dependent_health(
            service_name="my_service",
            db_manager=self.db,
            is_initialized=self._initialized,
            additional_checks=[
                self._check_cache_validity,
                self._check_connection
            ],
            include_stats=True,
            operation_count=self._operation_count,
            error_count=self._error_count,
            last_operation_time=self._last_operation
        )
        
        # For API-dependent services
        return await ServiceHealthCheck.api_dependent_health(
            service_name="my_service",
            is_initialized=self._initialized,
            has_rate_limiter=True,
            rate_limiter=self.rate_limiter,
            has_cache=True,
            cache_info={'size': len(self._cache)},
            additional_context={
                'api_endpoint': self.api_url,
                'last_call': self._last_call_time
            }
        )
```

---

## 🐛 Debugging Tips

### 1. Check Service Initialization Order
```bash
# Services initialize in dependency order
# Look for this in logs:
2025-10-20 03:17:08,614 - core.service_registry - INFO - Initializing 14 services...
2025-10-20 03:17:08,614 - core.service_registry - INFO - Initializing service: database
2025-10-20 03:17:08,702 - core.service_registry - INFO - Initializing service: config
...
```

### 2. Enable Debug Logging
```bash
python main.py --mode health --log-level DEBUG
```

### 3. Check Health Status
```bash
# Get detailed health info
python main.py --mode health | grep -A 10 "service_name"
```

### 4. Verify Dependencies
```python
# In your factory function, add logging
logger.info(f"Dependencies for myservice: {dependencies}")
db = await registry.get('database')
logger.info(f"✓ Database retrieved: {type(db)}")
```

---

## 📊 Performance Guidelines

### Do's ✅
- ✅ Keep factory functions under 30 lines
- ✅ Use async/await for all I/O operations
- ✅ Implement health_check() in all services
- ✅ Use ServiceHealthCheck utility for consistency
- ✅ Add comprehensive logging
- ✅ Handle exceptions gracefully

### Don'ts ❌
- ❌ Don't use blocking I/O operations
- ❌ Don't implement custom health checks (use utility)
- ❌ Don't forget to call initialize() when needed
- ❌ Don't mix async and sync code incorrectly
- ❌ Don't duplicate configuration
- ❌ Don't forget to update required_services list

---

## 📚 Reference

### Key Files
- **main.py**: Entry point and orchestration (THIS FILE)
- **core/service_registry.py**: Service registration and lifecycle
- **core/utils/service_health.py**: Health check utilities
- **config/settings.py**: Configuration service

### Design Principles
1. Modular Design
2. Service Pattern (main.py ONLY execution)
3. Service Registry
4. Single Source of Truth
5. Strict Async
6. No Sync Fallbacks
7. Per-Asset Monitoring
8. No Duplicate Configuration
9. Integrated Rate Limiting
10. Clear Separation of Concerns
11. Comprehensive Documentation
12. Method Singularity

### Current Services (v12.2.2)
1. database - PostgreSQL connection pool
2. config - Database-backed configuration
3. stellar_client - Stellar Horizon API
4. air - UBEC (Gateway & Diversity)
5. water - UBECrc (Flow & Reciprocity)
6. earth - UBECgpi (Stability & Mutualism)
7. fire - UBECtt (Transformation)
8. synchronizer - Blockchain data sync
9. analytics - Token distribution metrics
10. distribution - Balance management
11. distribution_evaluator - Compliance checking
12. holonic_evaluator - Ubuntu principles
13. visualizer - Charts & reports
14. audit - Tokenomics compliance

---

## 🆘 Getting Help

### Check These First
1. Review this guide
2. Check service logs: `python main.py --mode health --log-level DEBUG`
3. Review MAIN_PY_FIX_SUMMARY.md for detailed fix history
4. Check individual service documentation

### Common Error Messages

**"cannot import name 'X' from 'Y'"**
→ Check import statement and factory function name

**"object X can't be used in 'await' expression"**
→ Remove `await` - function is not async

**"coroutine X was never awaited"**
→ Add `await` - function is async

**"Failed to initialize service 'X'"**
→ Check dependencies and initialization order

---

**Last Updated:** October 20, 2025  
**Version:** 12.2.2  
**Maintainer:** UBEC Protocol Team
