-- ============================================================================
-- UBEC v17.0.0 - Database Pool Configuration Setup
-- ============================================================================
-- This script adds connection pool configuration to the system_settings table,
-- implementing Principles #4 (Single Source of Truth) and #8 (No Duplicate Config)
--
-- Run this before deploying main.py v17.0.0
-- ============================================================================

-- Add pool configuration settings
INSERT INTO system_settings (setting_key, setting_value, category, is_active, description)
VALUES 
    ('db_pool_min', '5', 'database', TRUE, 'Minimum database connection pool size'),
    ('db_pool_max', '20', 'database', TRUE, 'Maximum database connection pool size')
ON CONFLICT (setting_key) DO UPDATE
    SET setting_value = EXCLUDED.setting_value,
        is_active = TRUE,
        description = EXCLUDED.description;

-- Verify settings were added
SELECT 
    setting_key,
    setting_value,
    category,
    is_active,
    description
FROM system_settings
WHERE setting_key IN ('db_pool_min', 'db_pool_max')
ORDER BY setting_key;

-- ============================================================================
-- Expected Output:
-- ============================================================================
--  setting_key  | setting_value | category  | is_active |              description              
-- --------------+---------------+-----------+-----------+---------------------------------------
--  db_pool_max  | 20            | database  | t         | Maximum database connection pool size
--  db_pool_min  | 5             | database  | t         | Minimum database connection pool size
-- ============================================================================

-- ============================================================================
-- OPTIONAL: Adjust pool size for your environment
-- ============================================================================

-- For development/testing (small load):
-- UPDATE system_settings SET setting_value = '2' WHERE setting_key = 'db_pool_min';
-- UPDATE system_settings SET setting_value = '10' WHERE setting_key = 'db_pool_max';

-- For production (medium load) - DEFAULT:
-- UPDATE system_settings SET setting_value = '5' WHERE setting_key = 'db_pool_min';
-- UPDATE system_settings SET setting_value = '20' WHERE setting_key = 'db_pool_max';

-- For high-traffic production (large load):
-- UPDATE system_settings SET setting_value = '10' WHERE setting_key = 'db_pool_min';
-- UPDATE system_settings SET setting_value = '40' WHERE setting_key = 'db_pool_max';

-- For enterprise clusters (very large load):
-- UPDATE system_settings SET setting_value = '20' WHERE setting_key = 'db_pool_min';
-- UPDATE system_settings SET setting_value = '100' WHERE setting_key = 'db_pool_max';

-- ============================================================================
-- RECOMMENDED POOL SIZES
-- ============================================================================
-- Formula: max_pool = (concurrent_services * 1.5) + buffer
--
-- Concurrent Services: 15 (UBEC default)
-- Recommended: 5-20 (current default)
-- Adjust based on your deployment:
--   - More services = larger pool
--   - More traffic = larger pool
--   - Limited RAM = smaller pool
-- ============================================================================

-- ============================================================================
-- TROUBLESHOOTING
-- ============================================================================

-- Check if settings exist:
-- SELECT * FROM system_settings WHERE setting_key LIKE 'db_pool%';

-- Enable if disabled:
-- UPDATE system_settings SET is_active = TRUE WHERE setting_key LIKE 'db_pool%';

-- Reset to defaults:
-- UPDATE system_settings SET setting_value = '5' WHERE setting_key = 'db_pool_min';
-- UPDATE system_settings SET setting_value = '20' WHERE setting_key = 'db_pool_max';

-- Monitor pool usage (run during operation):
-- SELECT 
--     count(*) as total_connections,
--     count(*) FILTER (WHERE state = 'active') as active,
--     count(*) FILTER (WHERE state = 'idle') as idle
-- FROM pg_stat_activity
-- WHERE datname = 'ubec';
