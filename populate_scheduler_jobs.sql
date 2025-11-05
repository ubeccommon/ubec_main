-- ============================================================================
-- UBEC Protocol Scheduler Jobs - Default Configuration (FIXED v1.1)
-- ============================================================================
--
-- FIXES in v1.1:
-- 1. Changed TRUNCATE to DELETE (permission issue)
-- 2. Fixed next_run to use future timestamps (constraint validation)
-- 3. Fixed schedule_interval to use integer seconds only (type error)
--
-- Populates the scheduler_jobs table with default periodic tasks for
-- automated protocol operation.
--
-- Design Principle #4: Single Source of Truth - All job configuration
--                      stored in database, no code duplication.
--
-- Attribution: This project uses the services of Claude and Anthropic PBC to 
-- inform our decisions and recommendations. This project was made possible 
-- with the assistance of Claude and Anthropic PBC.
--
-- Author: UBEC Protocol Development Team
-- Version: 1.1.0 (FIXED)
-- Updated: 2025-11-05
-- ============================================================================

-- Clear existing jobs (use DELETE instead of TRUNCATE for permission compatibility)
DELETE FROM ubec_main.scheduler_jobs;

-- Reset sequence (optional, may require elevated permissions)
-- If this fails, it's not critical - just means IDs continue from current value
-- ALTER SEQUENCE ubec_main.scheduler_jobs_id_seq RESTART WITH 1;

-- ============================================================================
-- Job 1: Blockchain Synchronization
-- ============================================================================
-- Frequency: Every 5 minutes (300 seconds)
-- Purpose: Keep blockchain data current
-- Service: sync (UBECDataSynchronizer)
-- Method: sync_incremental()

INSERT INTO ubec_main.scheduler_jobs (
    job_name,
    schedule_interval,
    next_run,
    job_function,
    parameters,
    enabled
) VALUES (
    'blockchain_sync',
    '300',  -- 5 minutes in seconds
    NOW() + INTERVAL '1 minute',  -- Start in 1 minute
    'sync.sync_incremental',
    '{"sync_type": "all", "max_accounts": null}'::jsonb,
    true
);

-- ============================================================================
-- Job 2: Analytics Update
-- ============================================================================
-- Frequency: Every 15 minutes (900 seconds)
-- Purpose: Refresh token and network metrics
-- Service: analytics (UBECAnalyticsService)
-- Method: update_analytics()

INSERT INTO ubec_main.scheduler_jobs (
    job_name,
    schedule_interval,
    next_run,
    job_function,
    parameters,
    enabled
) VALUES (
    'analytics_update',
    '900',  -- 15 minutes in seconds
    NOW() + INTERVAL '2 minutes',  -- Stagger start
    'analytics.update_analytics',
    '{}'::jsonb,
    true
);

-- ============================================================================
-- Job 3: Holonic Evaluation
-- ============================================================================
-- Frequency: Every 30 minutes (1800 seconds)
-- Purpose: Assess Ubuntu principles compliance
-- Service: holonic (UBECHolonicEvaluator)
-- Method: evaluate_all_accounts()

INSERT INTO ubec_main.scheduler_jobs (
    job_name,
    schedule_interval,
    next_run,
    job_function,
    parameters,
    enabled
) VALUES (
    'holonic_evaluation',
    '1800',  -- 30 minutes in seconds
    NOW() + INTERVAL '5 minutes',  -- Stagger start
    'holonic.evaluate_all_accounts',
    '{"force_refresh": false}'::jsonb,
    true
);

-- ============================================================================
-- Job 4: Protocol Health Check
-- ============================================================================
-- Frequency: Every 10 minutes (600 seconds)
-- Purpose: Monitor protocol service health and update cache
-- Service: air_protocol, water_protocol, earth_protocol, fire_protocol
-- Method: refresh_cache()

INSERT INTO ubec_main.scheduler_jobs (
    job_name,
    schedule_interval,
    next_run,
    job_function,
    parameters,
    enabled
) VALUES (
    'protocol_health_check',
    '600',  -- 10 minutes in seconds
    NOW() + INTERVAL '3 minutes',  -- Stagger start
    'air_protocol.refresh_cache',
    '{}'::jsonb,
    true
);

-- ============================================================================
-- Job 5: HTML Report Generation
-- ============================================================================
-- Frequency: Every 6 hours (21600 seconds)
-- Purpose: Create visual dashboards and reports
-- Service: visualizer (UBECHolonicVisualizer)
-- Method: generate_html_report()

INSERT INTO ubec_main.scheduler_jobs (
    job_name,
    schedule_interval,
    next_run,
    job_function,
    parameters,
    enabled
) VALUES (
    'report_generation',
    '21600',  -- 6 hours in seconds
    NOW() + INTERVAL '10 minutes',  -- Stagger start
    'visualizer.generate_html_report',
    '{"output_dir": "./reports", "include_advanced": true}'::jsonb,
    true
);

-- ============================================================================
-- Job 6: Database Maintenance
-- ============================================================================
-- Frequency: Daily (86400 seconds = 24 hours)
-- Purpose: Archive old data, vacuum tables, update statistics
-- Service: database (UBECDatabaseManager)
-- Method: maintenance()

INSERT INTO ubec_main.scheduler_jobs (
    job_name,
    schedule_interval,
    next_run,
    job_function,
    parameters,
    enabled
) VALUES (
    'database_maintenance',
    '86400',  -- 24 hours in seconds
    -- Schedule for tomorrow at 2 AM
    (DATE_TRUNC('day', NOW() + INTERVAL '1 day') + INTERVAL '2 hours'),
    'database.maintenance',
    '{"vacuum": true, "analyze": true, "archive_days": 90}'::jsonb,
    true
);

-- ============================================================================
-- Job 7: Bioregion Analysis
-- ============================================================================
-- Frequency: Every hour (3600 seconds)
-- Purpose: Update bioregion emergence and tracking
-- Service: bioregion_manager (UBECBioregionManager)
-- Method: update_bioregions()

INSERT INTO ubec_main.scheduler_jobs (
    job_name,
    schedule_interval,
    next_run,
    job_function,
    parameters,
    enabled
) VALUES (
    'bioregion_analysis',
    '3600',  -- 1 hour in seconds
    NOW() + INTERVAL '15 minutes',  -- Stagger start
    'bioregion_manager.update_bioregions',
    '{}'::jsonb,
    true
);

-- ============================================================================
-- Verify Installation
-- ============================================================================

\echo ''
\echo '═══════════════════════════════════════════════════════════════════════'
\echo 'UBEC Scheduler Jobs - Installation Summary'
\echo '═══════════════════════════════════════════════════════════════════════'
\echo ''

SELECT 
    job_name,
    schedule_interval || 's' as interval,
    TO_CHAR(next_run, 'YYYY-MM-DD HH24:MI:SS') as next_run,
    enabled,
    job_function
FROM ubec_main.scheduler_jobs
ORDER BY CAST(schedule_interval AS INTEGER);

\echo ''
\echo '═══════════════════════════════════════════════════════════════════════'
\echo 'Installation Complete'
\echo '═══════════════════════════════════════════════════════════════════════'
\echo ''
\echo 'Next steps:'
\echo '  1. Integrate scheduler service into main.py'
\echo '  2. Run: python main.py serve'
\echo '  3. Monitor: tail -f logs/application.log | grep Scheduler'
\echo ''
\echo 'To modify jobs:'
\echo '  - Enable/disable: UPDATE ubec_main.scheduler_jobs SET enabled = false WHERE job_name = ''...'';'
\echo '  - Change interval: UPDATE ubec_main.scheduler_jobs SET schedule_interval = ''600'' WHERE job_name = ''...'';'
\echo '  - View status: SELECT * FROM ubec_main.scheduler_jobs;'
\echo ''

-- ============================================================================
-- Expected Output
-- ============================================================================
/*
═══════════════════════════════════════════════════════════════════════
UBEC Scheduler Jobs - Installation Summary
═══════════════════════════════════════════════════════════════════════

      job_name         | interval |      next_run       | enabled |       job_function        
-----------------------+----------+---------------------+---------+---------------------------
 blockchain_sync       | 300s     | 2025-11-05 05:01:00 | t       | sync.sync_incremental
 protocol_health_check | 600s     | 2025-11-05 05:03:00 | t       | air_protocol.refresh_cache
 analytics_update      | 900s     | 2025-11-05 05:02:00 | t       | analytics.update_analytics
 holonic_evaluation    | 1800s    | 2025-11-05 05:05:00 | t       | holonic.evaluate_all_accounts
 bioregion_analysis    | 3600s    | 2025-11-05 05:15:00 | t       | bioregion_manager.update_bioregions
 report_generation     | 21600s   | 2025-11-05 05:10:00 | t       | visualizer.generate_html_report
 database_maintenance  | 86400s   | 2025-11-06 02:00:00 | t       | database.maintenance

═══════════════════════════════════════════════════════════════════════
Installation Complete
═══════════════════════════════════════════════════════════════════════
*/

-- ============================================================================
-- Troubleshooting Notes
-- ============================================================================
--
-- If you see permission errors:
--   - Use ubec_admin user instead: psql -U ubec_admin -d ubec -f this_file.sql
--   - Or grant permissions: GRANT ALL ON ubec_main.scheduler_jobs TO ubec_app;
--
-- If next_run constraint fails:
--   - Check constraint: SELECT * FROM information_schema.check_constraints 
--                       WHERE table_name = 'scheduler_jobs';
--   - Ensure next_run is in the future (we use NOW() + INTERVAL)
--
-- If schedule_interval type error:
--   - Must be plain integer (seconds), not INTERVAL syntax
--   - Use '300' not '5 minutes'
--
-- ============================================================================
