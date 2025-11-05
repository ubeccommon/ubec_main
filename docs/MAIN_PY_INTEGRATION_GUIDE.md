# UBEC Scheduler Service - Main.py Integration Guide

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Overview

This guide shows the exact modifications needed to integrate the scheduler service into main.py.

**Files Modified**: `main.py` only  
**New Dependencies**: None (all async with stdlib)  
**Database Changes**: Populate `scheduler_jobs` table

---

## Step 1: Register Scheduler Service

**Location**: In the `register_core_services()` function  
**Add After**: Visualizer service registration  
**Add Before**: Return statement

```python
# ========================================================================
# STEP 1: Add Scheduler Service Factory
# Add this function inside register_core_services(), after visualizer
# ========================================================================

async def create_scheduler_service():
    """
    Create scheduler service for automated task execution.
    
    Principle #2: Service pattern with factory function
    Principle #12: Uses standardized factory function
    """
    from services.scheduler.ubec_scheduler_service import create_scheduler_service
    
    logger.info("  ├─ Scheduler Service: Automated periodic tasks")
    
    # Use the factory function from scheduler service module
    scheduler_service = await create_scheduler_service(registry)
    
    logger.info("✓ Scheduler service created")
    return scheduler_service

# Register in service registry
registry.register_factory(
    'scheduler',
    create_scheduler_service,
    dependencies=[
        'database',
        'config',
        'sync',
        'analytics',
        'holonic',
        'visualizer',
        'bioregion_manager'
    ]
)
```

**Complete Code Block to Insert**:

```python
    # Scheduler service (NEW)
    async def create_scheduler_service():
        from services.scheduler.ubec_scheduler_service import create_scheduler_service
        logger.info("  ├─ Scheduler Service: Automated periodic tasks")
        scheduler = await create_scheduler_service(registry)
        logger.info("✓ Scheduler service created")
        return scheduler
    
    registry.register_factory(
        'scheduler',
        create_scheduler_service,
        dependencies=['database', 'config', 'sync', 'analytics', 'holonic', 'visualizer', 'bioregion_manager']
    )
```

**Insert Location**: Add this right after the API service registration and before the final `logger.info` statements.

---

## Step 2: Modify handle_serve() Function

**Location**: In the `handle_serve()` function  
**Add After**: API service initialization  
**Add Before**: `server.serve()`

```python
# ========================================================================
# STEP 2: Start Scheduler Service in handle_serve()
# Modify the existing handle_serve() function
# ========================================================================

async def handle_serve(registry: ServiceRegistry, host: str = '0.0.0.0', 
                      port: int = 8000, reload: bool = False):
    """
    Start the FastAPI backend server with scheduler.
    
    This exposes REST endpoints for the www server to consume
    AND starts the background scheduler for automated tasks.
    
    Args:
        registry: Service registry
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
    """
    logger.info("=" * 70)
    logger.info(f"STARTING UBEC PROTOCOL SERVER")
    logger.info(f"API: http://{host}:{port}")
    logger.info("=" * 70)
    
    # Get the API service
    api_service = await registry.get('api_service')
    app = api_service.app
    
    # ===== NEW: Start Scheduler Service =====
    try:
        logger.info("\n🔄 Initializing Scheduler Service...")
        scheduler = await registry.get('scheduler')
        await scheduler.start()
        logger.info("✅ Scheduler started - automated tasks active")
    except Exception as e:
        logger.error(f"⚠️  Failed to start scheduler: {e}")
        logger.warning("Server will continue without scheduler")
    # =========================================
    
    logger.info(f"\n✅ API Server ready")
    logger.info(f"📊 Swagger docs: http://{host}:{port}/docs")
    logger.info(f"📖 ReDoc: http://{host}:{port}/redoc")
    logger.info(f"💚 Health: http://{host}:{port}/health")
    logger.info(f"⏰ Scheduler: Active (background tasks running)")
    logger.info("\n👉 Press Ctrl+C to stop")
    logger.info("=" * 70)
    
    # Run the server
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Shutting down...")
        
        # ===== NEW: Stop Scheduler Gracefully =====
        try:
            logger.info("Stopping scheduler...")
            await scheduler.stop()
            logger.info("✅ Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
        # ==========================================
        
        logger.info("✅ Server stopped")
```

---

## Step 3: Add Scheduler Status Command (Optional)

**Location**: Add new command handler in main.py  
**Add After**: `handle_protocol_health()`  
**Add Before**: `handle_serve()`

```python
async def handle_scheduler_status(registry: ServiceRegistry):
    """
    Display scheduler status and job information.
    
    Args:
        registry: Service registry
    """
    logger.info("=" * 70)
    logger.info("SCHEDULER STATUS")
    logger.info("=" * 70)
    
    try:
        scheduler = await registry.get('scheduler')
        health = await scheduler.health_check()
        
        # Overall status
        status_symbol = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌'
        }.get(health['status'], '❓')
        
        logger.info(f"\n{status_symbol} Status: {health['status'].upper()}")
        logger.info(f"Running: {'Yes' if health['running'] else 'No'}")
        
        # Metrics
        metrics = health['metrics']
        logger.info(f"\nMetrics:")
        logger.info(f"  Total Jobs: {metrics['total_jobs']}")
        logger.info(f"  Enabled: {metrics['enabled_jobs']}")
        logger.info(f"  Currently Running: {metrics['running_jobs']}")
        logger.info(f"  Success Rate: {metrics['overall_success_rate']:.1%}")
        
        # Job details
        logger.info(f"\nJobs:")
        for job in health['jobs']:
            job_status = '✅' if job['enabled'] else '❌'
            circuit = job['circuit_state']
            circuit_symbol = {
                'closed': '✅',
                'half_open': '⚠️',
                'open': '❌'
            }.get(circuit, '❓')
            
            logger.info(f"\n  {job_status} {job['name']}")
            logger.info(f"     Next Run: {job['next_run']}")
            logger.info(f"     Success Rate: {job['success_rate']:.1%}")
            logger.info(f"     Avg Duration: {job['avg_duration_ms']:.0f}ms")
            logger.info(f"     Circuit: {circuit_symbol} {circuit}")
            
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
    
    logger.info("\n" + "=" * 70)
```

**Add Command Line Argument**:

```python
# In main() function, add new subparser
subparsers.add_parser('scheduler-status', help='Display scheduler status')

# In command execution section
elif args.command == 'scheduler-status':
    await handle_scheduler_status(registry)
```

---

## Step 4: Update Health Check to Include Scheduler

**Location**: In `handle_health_check()` function  
**Modify**: Add 'scheduler' to service_names list

```python
async def handle_health_check(registry: ServiceRegistry, detailed: bool = False):
    """
    Perform comprehensive health check on all services.
    """
    # ... existing code ...
    
    # Add 'scheduler' to the list
    service_names = [
        'database', 'config', 'stellar',
        'air_protocol', 'water_protocol', 'earth_protocol', 'fire_protocol',
        'sync', 'analytics', 'holonic', 'visualizer', 'bioregion_manager', 
        'api_service', 'scheduler'  # <-- ADD THIS
    ]
    
    # ... rest of function unchanged ...
```

---

## Step 5: Create Scheduler Service Directory

Create the directory structure:

```bash
mkdir -p services/scheduler
touch services/scheduler/__init__.py
```

Copy the scheduler service file:

```bash
cp ubec_scheduler_service.py services/scheduler/
```

---

## Step 6: Populate Database

Run the SQL script to populate scheduler_jobs table:

```bash
psql -U ubec_admin -d ubec -f populate_scheduler_jobs.sql
```

Or programmatically:

```python
# In a migration or setup script
async def setup_scheduler_jobs():
    db = await get_database()
    
    with open('populate_scheduler_jobs.sql', 'r') as f:
        sql = f.read()
    
    async with db.pool.acquire() as conn:
        await conn.execute(sql)
    
    logger.info("✓ Scheduler jobs populated")
```

---

## Complete Modified Sections

### Section A: Service Registration (in register_core_services)

```python
    # ... existing services ...
    
    # Scheduler service (NEW - add this entire block)
    async def create_scheduler_service():
        from services.scheduler.ubec_scheduler_service import create_scheduler_service
        logger.info("  ├─ Scheduler Service: Automated periodic tasks")
        scheduler = await create_scheduler_service(registry)
        logger.info("✓ Scheduler service created")
        return scheduler
    
    registry.register_factory(
        'scheduler',
        create_scheduler_service,
        dependencies=['database', 'config', 'sync', 'analytics', 'holonic', 'visualizer', 'bioregion_manager']
    )
    
    logger.info("=" * 70)
    logger.info(f"✓ Registered {len(registry._factories)} services")
    logger.info("=" * 70)
    
    return registry
```

### Section B: Serve Handler (complete replacement)

```python
async def handle_serve(registry: ServiceRegistry, host: str = '0.0.0.0', 
                      port: int = 8000, reload: bool = False):
    """
    Start the FastAPI backend server with scheduler.
    """
    logger.info("=" * 70)
    logger.info(f"STARTING UBEC PROTOCOL SERVER")
    logger.info(f"API: http://{host}:{port}")
    logger.info("=" * 70)
    
    # Get the API service
    api_service = await registry.get('api_service')
    app = api_service.app
    
    # Start scheduler service (NEW)
    try:
        logger.info("\n🔄 Initializing Scheduler Service...")
        scheduler = await registry.get('scheduler')
        await scheduler.start()
        logger.info("✅ Scheduler started")
    except Exception as e:
        logger.error(f"⚠️  Failed to start scheduler: {e}")
        logger.warning("Server will continue without scheduler")
    
    logger.info(f"\n✅ Server ready")
    logger.info(f"📊 API: http://{host}:{port}/docs")
    logger.info(f"⏰ Scheduler: Active")
    logger.info("\n👉 Press Ctrl+C to stop")
    logger.info("=" * 70)
    
    # Run the server
    config = uvicorn.Config(app, host=host, port=port, reload=reload, log_level="info")
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Shutting down...")
        try:
            logger.info("Stopping scheduler...")
            await scheduler.stop()
            logger.info("✅ Scheduler stopped")
        except:
            pass
        logger.info("✅ Server stopped")
```

---

## Testing the Integration

### 1. Verify Database Schema
```bash
psql -U ubec_admin -d ubec -c "SELECT * FROM ubec_main.scheduler_jobs;"
```

### 2. Test Service Registration
```bash
python main.py health
# Should show scheduler service in list
```

### 3. Start Server with Scheduler
```bash
python main.py serve
```

Expected output:
```
═══════════════════════════════════════════════════════════════════════
STARTING UBEC PROTOCOL SERVER
API: http://0.0.0.0:8000
═══════════════════════════════════════════════════════════════════════

🔄 Initializing Scheduler Service...
✅ Scheduler started - automated tasks active

✅ Server ready
📊 API: http://0.0.0.0:8000/docs
⏰ Scheduler: Active

👉 Press Ctrl+C to stop
═══════════════════════════════════════════════════════════════════════
```

### 4. Monitor Scheduler Activity
Watch the logs for job execution:
```bash
tail -f logs/application.log | grep "Scheduler"
```

Expected log entries:
```
2025-11-05 10:30:00 INFO Scheduler: Executing job: blockchain_sync
2025-11-05 10:30:02 INFO Scheduler: ✓ Job 'blockchain_sync' completed (2100ms)
2025-11-05 10:32:00 INFO Scheduler: Executing job: analytics_update
```

### 5. Check Scheduler Status
```bash
python main.py scheduler-status
```

### 6. Test API Endpoints
```bash
# Health endpoint should include scheduler
curl http://localhost:8000/health | jq .

# Check specific scheduler status
curl http://localhost:8000/api/v1/scheduler/status | jq .
```

---

## Troubleshooting

### Issue: Scheduler Not Starting

**Check**:
1. Database connection: `python main.py health`
2. Jobs loaded: `SELECT COUNT(*) FROM ubec_main.scheduler_jobs;`
3. Dependencies registered: Check main.py service registration

**Fix**:
```bash
# Reinitialize database
psql -U ubec_admin -d ubec -f populate_scheduler_jobs.sql

# Verify
psql -U ubec_admin -d ubec -c "SELECT job_name, enabled FROM ubec_main.scheduler_jobs;"
```

### Issue: Jobs Not Executing

**Check**:
1. Job enabled: `SELECT * FROM ubec_main.scheduler_jobs WHERE enabled = false;`
2. Next run time: `SELECT job_name, next_run FROM ubec_main.scheduler_jobs;`
3. Circuit breaker: Check logs for "Circuit breaker open"

**Fix**:
```sql
-- Enable job
UPDATE ubec_main.scheduler_jobs SET enabled = true WHERE job_name = 'blockchain_sync';

-- Reset next_run
UPDATE ubec_main.scheduler_jobs SET next_run = NOW() WHERE job_name = 'blockchain_sync';
```

### Issue: Service Method Not Found

**Error**: `AttributeError: Service 'sync' has no method 'sync_incremental'`

**Fix**:
1. Check service exists: `await registry.get('sync')`
2. Check method name matches exactly
3. Verify job_function in database matches actual method name

---

## Success Criteria Checklist

- [ ] Scheduler service registered in service registry
- [ ] Scheduler starts with `python main.py serve`
- [ ] Jobs visible in `python main.py scheduler-status`
- [ ] Jobs execute on schedule (check logs)
- [ ] Reports generate automatically
- [ ] Health endpoint shows scheduler status
- [ ] Graceful shutdown with Ctrl+C
- [ ] No errors in logs

---

## Next Steps

1. Monitor first 24 hours of operation
2. Adjust job intervals based on load
3. Add custom jobs as needed
4. Set up alerting for failures
5. Create dashboard for scheduler metrics

---

**Ready to integrate!** 🚀
