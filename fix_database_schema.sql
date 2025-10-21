-- ============================================================================
-- UBEC Database Critical Fixes
-- ============================================================================
-- Date: October 21, 2025
-- Purpose: Fix critical database schema issues preventing system startup
-- System Version: 16.0.0
-- Database: ubec (PostgreSQL 15.13)
--
-- CRITICAL: These fixes must be applied before system can start
-- ============================================================================

-- Connect to ubec database
\c ubec

-- Set search path to main schema
SET search_path TO ubec_main, public;

-- ============================================================================
-- FIX #1: Add Missing UNIQUE Constraint to api_rate_limits
-- ============================================================================
-- Issue: ON CONFLICT (api_name) fails without unique constraint
-- Impact: Rate limiter service cannot persist metrics on shutdown
-- Severity: CRITICAL
-- ============================================================================

\echo ''
\echo '============================================================================'
\echo 'FIX #1: Adding UNIQUE constraint to api_rate_limits.api_name'
\echo '============================================================================'

-- Check if constraint already exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'unique_api_name'
        AND table_name = 'api_rate_limits'
        AND table_schema = 'ubec_main'
    ) THEN
        -- Add the constraint
        ALTER TABLE ubec_main.api_rate_limits 
        ADD CONSTRAINT unique_api_name UNIQUE (api_name);
        
        RAISE NOTICE '✓ UNIQUE constraint added to api_rate_limits.api_name';
    ELSE
        RAISE NOTICE '✓ UNIQUE constraint already exists on api_rate_limits.api_name';
    END IF;
END $$;

-- Verify constraint exists
SELECT 
    constraint_name,
    constraint_type,
    table_name
FROM information_schema.table_constraints
WHERE table_name = 'api_rate_limits'
AND table_schema = 'ubec_main'
AND constraint_name = 'unique_api_name';

-- ============================================================================
-- FIX #2: Verify Required Configuration Settings Exist
-- ============================================================================
-- Issue: Element services require asset_code and issuer configuration
-- Impact: Air, Water, Earth, Fire services cannot initialize
-- Severity: CRITICAL
-- ============================================================================

\echo ''
\echo '============================================================================'
\echo 'FIX #2: Verifying required token configuration settings'
\echo '============================================================================'

-- Check for all required token settings
SELECT 
    setting_key,
    setting_value,
    is_active,
    CASE 
        WHEN setting_value IS NULL OR setting_value = '' THEN '❌ MISSING'
        WHEN is_active = FALSE THEN '⚠ INACTIVE'
        ELSE '✓ OK'
    END as status
FROM ubec_main.system_settings
WHERE setting_key IN (
    'ubec_code', 'ubec_issuer',
    'ubecrc_code', 'ubecrc_issuer',
    'ubecgpi_code', 'ubecgpi_issuer',
    'ubectt_code', 'ubectt_issuer'
)
ORDER BY setting_key;

-- Count missing settings
DO $$
DECLARE
    missing_count INTEGER;
    required_settings TEXT[] := ARRAY[
        'ubec_code', 'ubec_issuer',
        'ubecrc_code', 'ubecrc_issuer',
        'ubecgpi_code', 'ubecgpi_issuer',
        'ubectt_code', 'ubectt_issuer'
    ];
BEGIN
    SELECT COUNT(*)
    INTO missing_count
    FROM unnest(required_settings) AS setting_key
    WHERE NOT EXISTS (
        SELECT 1
        FROM ubec_main.system_settings
        WHERE system_settings.setting_key = unnest.setting_key
        AND system_settings.is_active = TRUE
        AND system_settings.setting_value IS NOT NULL
        AND system_settings.setting_value != ''
    );
    
    IF missing_count > 0 THEN
        RAISE WARNING '❌ CRITICAL: % required token settings are missing or inactive', missing_count;
        RAISE WARNING 'Run the INSERT statements below to add missing settings';
    ELSE
        RAISE NOTICE '✓ All required token settings present and active';
    END IF;
END $$;

-- ============================================================================
-- OPTIONAL: Insert Missing Token Configuration (if needed)
-- ============================================================================
-- Uncomment and modify these INSERT statements if settings are missing
-- Replace placeholder values with your actual token codes and issuer addresses
-- ============================================================================

-- Example: Add missing UBEC (Air) configuration
/*
INSERT INTO ubec_main.system_settings (
    setting_key, 
    setting_value, 
    setting_type, 
    description, 
    category, 
    is_active
) VALUES 
    ('ubec_code', 'UBEC', 'string', 'UBEC token code (Air element)', 'tokens', TRUE),
    ('ubec_issuer', 'GDPNB7S3WTAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'string', 'UBEC issuer address', 'tokens', TRUE)
ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;
*/

-- Example: Add missing UBECrc (Water) configuration
/*
INSERT INTO ubec_main.system_settings (
    setting_key, 
    setting_value, 
    setting_type, 
    description, 
    category, 
    is_active
) VALUES 
    ('ubecrc_code', 'UBECrc', 'string', 'UBECrc token code (Water element)', 'tokens', TRUE),
    ('ubecrc_issuer', 'GDPNB7S3WTAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'string', 'UBECrc issuer address', 'tokens', TRUE)
ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;
*/

-- Example: Add missing UBECgpi (Earth) configuration
/*
INSERT INTO ubec_main.system_settings (
    setting_key, 
    setting_value, 
    setting_type, 
    description, 
    category, 
    is_active
) VALUES 
    ('ubecgpi_code', 'UBECgpi', 'string', 'UBECgpi token code (Earth element)', 'tokens', TRUE),
    ('ubecgpi_issuer', 'GDPNB7S3WTAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'string', 'UBECgpi issuer address', 'tokens', TRUE)
ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;
*/

-- Example: Add missing UBECtt (Fire) configuration
/*
INSERT INTO ubec_main.system_settings (
    setting_key, 
    setting_value, 
    setting_type, 
    description, 
    category, 
    is_active
) VALUES 
    ('ubectt_code', 'UBECtt', 'string', 'UBECtt token code (Fire element)', 'tokens', TRUE),
    ('ubectt_issuer', 'GDPNB7S3WTAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'string', 'UBECtt issuer address', 'tokens', TRUE)
ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;
*/

-- ============================================================================
-- PERFORMANCE FIX #1: Add Index on system_settings for Faster Lookups
-- ============================================================================
-- Issue: Rate limiter loads settings slowly (1065ms vs 50ms baseline)
-- Impact: 21x slower initialization
-- Severity: HIGH
-- ============================================================================

\echo ''
\echo '============================================================================'
\echo 'PERFORMANCE FIX #1: Adding index on system_settings'
\echo '============================================================================'

-- Create partial index for active settings (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_system_settings_key_active 
ON ubec_main.system_settings(setting_key, is_active) 
WHERE is_active = TRUE;

\echo '✓ Index created: idx_system_settings_key_active'

-- ============================================================================
-- PERFORMANCE FIX #2: Add Index on api_rate_limits for Faster Lookups
-- ============================================================================
-- Issue: Rate limiter loads API limits slowly
-- Impact: Contributes to slow initialization
-- Severity: HIGH
-- ============================================================================

\echo ''
\echo '============================================================================'
\echo 'PERFORMANCE FIX #2: Adding index on api_rate_limits'
\echo '============================================================================'

-- Create index on api_name (also helps enforce UNIQUE constraint)
CREATE INDEX IF NOT EXISTS idx_api_rate_limits_name 
ON ubec_main.api_rate_limits(api_name);

\echo '✓ Index created: idx_api_rate_limits_name'

-- ============================================================================
-- VERIFICATION: Check All Fixes Applied Successfully
-- ============================================================================

\echo ''
\echo '============================================================================'
\echo 'VERIFICATION SUMMARY'
\echo '============================================================================'

-- 1. Verify UNIQUE constraint
\echo ''
\echo '1. UNIQUE Constraint on api_rate_limits:'
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE constraint_name = 'unique_api_name'
            AND table_name = 'api_rate_limits'
            AND table_schema = 'ubec_main'
        ) THEN '✓ CONSTRAINT EXISTS'
        ELSE '❌ CONSTRAINT MISSING'
    END as constraint_status;

-- 2. Verify indices
\echo ''
\echo '2. Performance Indices:'
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'ubec_main'
AND tablename IN ('system_settings', 'api_rate_limits')
ORDER BY tablename, indexname;

-- 3. Verify configuration completeness
\echo ''
\echo '3. Required Token Configuration Settings:'
SELECT 
    COUNT(*) as total_required,
    SUM(CASE WHEN setting_value IS NOT NULL AND setting_value != '' AND is_active THEN 1 ELSE 0 END) as configured,
    SUM(CASE WHEN setting_value IS NULL OR setting_value = '' OR NOT is_active THEN 1 ELSE 0 END) as missing
FROM ubec_main.system_settings
WHERE setting_key IN (
    'ubec_code', 'ubec_issuer',
    'ubecrc_code', 'ubecrc_issuer',
    'ubecgpi_code', 'ubecgpi_issuer',
    'ubectt_code', 'ubectt_issuer'
);

-- 4. Summary
\echo ''
\echo '============================================================================'
\echo 'NEXT STEPS:'
\echo '============================================================================'
\echo '1. If any token settings are missing, uncomment and run the INSERT'
\echo '   statements above with your actual issuer addresses'
\echo '2. Fix main.py element service factories (see DATABASE_REVIEW document)'
\echo '3. Fix synchronizer import path in main.py'
\echo '4. Restart system: python main.py --mode health'
\echo '============================================================================'

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
