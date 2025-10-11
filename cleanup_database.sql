-- ============================================================================
-- UBEC Protocol - Database Cleanup Script
-- ============================================================================
-- Clears all test/historical data while preserving table structures
-- and essential configuration data.
--
-- This script will:
--   ✓ Clear all account data
--   ✓ Clear all transaction history
--   ✓ Clear all balance records
--   ✓ Clear all relationship data
--   ✓ Reset distribution states to defaults
--   ✓ Preserve table structures
--   ✓ Preserve indexes and constraints
--
-- SAFE TO RUN: This only removes data, not structures
--
-- Attribution:
--   This project uses the services of Claude and Anthropic PBC to inform our
--   decisions and recommendations. This project was made possible with the
--   assistance of Claude and Anthropic PBC.
--
-- Version: 1.0.0
-- Date: October 11, 2025
-- ============================================================================

-- Set schema
SET search_path TO ubec_main;

-- Start transaction (can be rolled back if needed)
BEGIN;

-- ============================================================================
-- DISPLAY CURRENT DATA COUNTS (Before Cleanup)
-- ============================================================================

\echo '========================================================================'
\echo 'CURRENT DATA COUNTS (Before Cleanup)'
\echo '========================================================================'

SELECT 
    'gateway_accounts' as table_name,
    COUNT(*) as row_count
FROM gateway_accounts
UNION ALL
SELECT 
    'flow_transactions' as table_name,
    COUNT(*) as row_count
FROM flow_transactions
UNION ALL
SELECT 
    'account_balances' as table_name,
    COUNT(*) as row_count
FROM account_balances
UNION ALL
SELECT 
    'mutualism_relationships' as table_name,
    COUNT(*) as row_count
FROM mutualism_relationships
UNION ALL
SELECT 
    'distribution_state' as table_name,
    COUNT(*) as row_count
FROM distribution_state
UNION ALL
SELECT 
    'stellar_accounts' as table_name,
    COUNT(*) as row_count
FROM stellar_accounts
UNION ALL
SELECT 
    'stellar_transactions' as table_name,
    COUNT(*) as row_count
FROM stellar_transactions
UNION ALL
SELECT 
    'stellar_operations' as table_name,
    COUNT(*) as row_count
FROM stellar_operations
UNION ALL
SELECT 
    'stellar_effects' as table_name,
    COUNT(*) as row_count
FROM stellar_effects
UNION ALL
SELECT 
    'ubec_balances' as table_name,
    COUNT(*) as row_count
FROM ubec_balances
ORDER BY table_name;

\echo ''
\echo '========================================================================'
\echo 'CLEARING DATA...'
\echo '========================================================================'
\echo ''

-- ============================================================================
-- CLEAR PROTOCOL-SPECIFIC TABLES (Our New Tables)
-- ============================================================================

\echo 'Clearing protocol-specific tables...'

-- Air Element (UBEC)
TRUNCATE TABLE gateway_accounts CASCADE;
\echo '  ✓ gateway_accounts cleared'

-- Water Element (UBECrc)
TRUNCATE TABLE flow_transactions CASCADE;
\echo '  ✓ flow_transactions cleared'

-- Earth Element (UBECgpi)
TRUNCATE TABLE account_balances CASCADE;
\echo '  ✓ account_balances cleared'

TRUNCATE TABLE mutualism_relationships CASCADE;
\echo '  ✓ mutualism_relationships cleared'

-- Note: We'll reset distribution_state rather than truncate
DELETE FROM distribution_state;
\echo '  ✓ distribution_state cleared'

-- Re-insert default distribution state records
INSERT INTO distribution_state (asset_code, category, target_percentage, target_amount, current_amount, actual_percentage) VALUES
    ('UBEC', 'general_circulation', 75.00, 0.0, 0.0, 0.0),
    ('UBEC', 'stewardship', 20.00, 0.0, 0.0, 0.0),
    ('UBEC', 'administration', 5.00, 0.0, 0.0, 0.0),
    ('UBECrc', 'general_circulation', 75.00, 0.0, 0.0, 0.0),
    ('UBECrc', 'stewardship', 20.00, 0.0, 0.0, 0.0),
    ('UBECrc', 'administration', 5.00, 0.0, 0.0, 0.0),
    ('UBECgpi', 'general_circulation', 75.00, 0.0, 0.0, 0.0),
    ('UBECgpi', 'stewardship', 20.00, 0.0, 0.0, 0.0),
    ('UBECgpi', 'administration', 5.00, 0.0, 0.0, 0.0),
    ('UBECtt', 'general_circulation', 75.00, 0.0, 0.0, 0.0),
    ('UBECtt', 'stewardship', 20.00, 0.0, 0.0, 0.0),
    ('UBECtt', 'administration', 5.00, 0.0, 0.0, 0.0);
\echo '  ✓ distribution_state reset to defaults'

\echo ''

-- ============================================================================
-- CLEAR CORE STELLAR TABLES (If they exist)
-- ============================================================================

\echo 'Clearing core Stellar data tables...'

-- Clear in order to respect foreign key constraints
-- Effects depend on operations
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ubec_main' AND table_name = 'stellar_effects') THEN
        TRUNCATE TABLE stellar_effects CASCADE;
        RAISE NOTICE '  ✓ stellar_effects cleared';
    END IF;
END $$;

-- Operations depend on transactions
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ubec_main' AND table_name = 'stellar_operations') THEN
        TRUNCATE TABLE stellar_operations CASCADE;
        RAISE NOTICE '  ✓ stellar_operations cleared';
    END IF;
END $$;

-- Transactions reference accounts
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ubec_main' AND table_name = 'stellar_transactions') THEN
        TRUNCATE TABLE stellar_transactions CASCADE;
        RAISE NOTICE '  ✓ stellar_transactions cleared';
    END IF;
END $$;

-- Clear balances before accounts
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ubec_main' AND table_name = 'ubec_balances') THEN
        TRUNCATE TABLE ubec_balances CASCADE;
        RAISE NOTICE '  ✓ ubec_balances cleared';
    END IF;
END $$;

-- Clear accounts last
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ubec_main' AND table_name = 'stellar_accounts') THEN
        TRUNCATE TABLE stellar_accounts CASCADE;
        RAISE NOTICE '  ✓ stellar_accounts cleared';
    END IF;
END $$;

\echo ''

-- ============================================================================
-- CLEAR AUDIT AND SYNC STATUS TABLES (If they exist)
-- ============================================================================

\echo 'Clearing audit and sync status tables...'

DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ubec_main' AND table_name = 'ubec_audit_log') THEN
        TRUNCATE TABLE ubec_audit_log CASCADE;
        RAISE NOTICE '  ✓ ubec_audit_log cleared';
    END IF;
END $$;

DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ubec_main' AND table_name = 'ubec_sync_status') THEN
        TRUNCATE TABLE ubec_sync_status CASCADE;
        RAISE NOTICE '  ✓ ubec_sync_status cleared';
    END IF;
END $$;

DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ubec_main' AND table_name = 'distribution_history') THEN
        TRUNCATE TABLE distribution_history CASCADE;
        RAISE NOTICE '  ✓ distribution_history cleared';
    END IF;
END $$;

\echo ''

-- ============================================================================
-- RESET SEQUENCES (If any)
-- ============================================================================

\echo 'Resetting sequences...'

-- Reset serial sequences for tables that use them
DO $$ 
BEGIN
    -- Reset distribution_state sequence
    IF EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'ubec_main' AND sequencename = 'distribution_state_id_seq') THEN
        ALTER SEQUENCE distribution_state_id_seq RESTART WITH 1;
        RAISE NOTICE '  ✓ distribution_state_id_seq reset';
    END IF;
    
    -- Reset account_balances sequence
    IF EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'ubec_main' AND sequencename = 'account_balances_id_seq') THEN
        ALTER SEQUENCE account_balances_id_seq RESTART WITH 1;
        RAISE NOTICE '  ✓ account_balances_id_seq reset';
    END IF;
    
    -- Reset mutualism_relationships sequence
    IF EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'ubec_main' AND sequencename = 'mutualism_relationships_id_seq') THEN
        ALTER SEQUENCE mutualism_relationships_id_seq RESTART WITH 1;
        RAISE NOTICE '  ✓ mutualism_relationships_id_seq reset';
    END IF;
END $$;

\echo ''

-- ============================================================================
-- VERIFY CLEANUP
-- ============================================================================

\echo '========================================================================'
\echo 'VERIFICATION: Data Counts After Cleanup'
\echo '========================================================================'

SELECT 
    'gateway_accounts' as table_name,
    COUNT(*) as row_count
FROM gateway_accounts
UNION ALL
SELECT 
    'flow_transactions' as table_name,
    COUNT(*) as row_count
FROM flow_transactions
UNION ALL
SELECT 
    'account_balances' as table_name,
    COUNT(*) as row_count
FROM account_balances
UNION ALL
SELECT 
    'mutualism_relationships' as table_name,
    COUNT(*) as row_count
FROM mutualism_relationships
UNION ALL
SELECT 
    'distribution_state' as table_name,
    COUNT(*) as row_count
FROM distribution_state
UNION ALL
SELECT 
    'stellar_accounts' as table_name,
    COUNT(*) as row_count
FROM stellar_accounts
UNION ALL
SELECT 
    'stellar_transactions' as table_name,
    COUNT(*) as row_count
FROM stellar_transactions
UNION ALL
SELECT 
    'stellar_operations' as table_name,
    COUNT(*) as row_count
FROM stellar_operations
ORDER BY table_name;

\echo ''
\echo '========================================================================'
\echo 'EXPECTED RESULTS:'
\echo '  - Most tables should show 0 rows'
\echo '  - distribution_state should show 12 rows (3 per token)'
\echo '========================================================================'
\echo ''

-- Commit the transaction
COMMIT;

\echo '========================================================================'
\echo '✓ DATABASE CLEANUP COMPLETE'
\echo '========================================================================'
\echo ''
\echo 'Your database is now clean and ready for fresh data!'
\echo ''
\echo 'Next steps:'
\echo '  1. Run: python load_data.py --mode quick'
\echo '  2. Verify: python ubec_main_protocol.py --action sync'
\echo ''
\echo '========================================================================'

-- Verify table structures are intact
\echo 'Verifying table structures...'
\echo ''

SELECT 
    schemaname,
    tablename,
    CASE 
        WHEN tablename IN ('gateway_accounts', 'flow_transactions', 'distribution_state', 
                           'mutualism_relationships', 'account_balances')
        THEN '✓ Protocol table'
        ELSE '  Core table'
    END as status
FROM pg_tables 
WHERE schemaname = 'ubec_main'
    AND tablename IN (
        'gateway_accounts',
        'flow_transactions', 
        'distribution_state',
        'mutualism_relationships',
        'account_balances',
        'stellar_accounts',
        'stellar_transactions',
        'stellar_operations',
        'ubec_balances'
    )
ORDER BY tablename;

\echo ''
\echo '========================================================================'
\echo 'All table structures preserved ✓'
\echo 'Database is ready for fresh data load!'
\echo '========================================================================'
