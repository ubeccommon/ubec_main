-- ============================================================================
-- UBEC Database Schema - Emergency Fixes
-- ============================================================================
-- Date: October 9, 2025
-- Purpose: Fix critical schema issues preventing sync operations
-- Run this IMMEDIATELY to resolve blocking errors
-- ============================================================================

-- Connect to database first:
-- psql -U your_user -d ubec

\echo '========================================================================'
\echo 'UBEC Database Emergency Fixes'
\echo 'Starting repairs...'
\echo '========================================================================'

-- ============================================================================
-- FIX #1: Add Missing Unique Constraint for Holonic Metrics
-- ============================================================================
-- Error: constraint "idx_holonic_metrics_unique_agent_date" does not exist
-- Impact: Cannot store holonic evaluation results

\echo ''
\echo 'Fix #1: Adding unique constraint to holonic_metrics...'

-- Drop if exists (in case of partial creation)
DROP INDEX IF EXISTS ubec_main.idx_holonic_metrics_unique_agent_date;

-- Create the unique constraint
CREATE UNIQUE INDEX idx_holonic_metrics_unique_agent_date 
ON ubec_main.holonic_metrics (agent_id, DATE(evaluation_date));

\echo '✓ Unique constraint added'

-- Verify
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'ubec_main' 
        AND indexname = 'idx_holonic_metrics_unique_agent_date'
    ) THEN
        RAISE NOTICE '✓ Constraint verified: idx_holonic_metrics_unique_agent_date exists';
    ELSE
        RAISE EXCEPTION '✗ Constraint creation failed!';
    END IF;
END $$;

-- ============================================================================
-- FIX #2: Create transaction_operations Table/View
-- ============================================================================
-- Error: relation "ubec_main.transaction_operations" does not exist
-- Impact: Holonic evaluator cannot fetch transaction history

\echo ''
\echo 'Fix #2: Creating transaction_operations compatibility layer...'

-- Option A: Create as VIEW (recommended - no data duplication)
DROP VIEW IF EXISTS ubec_main.transaction_operations CASCADE;

CREATE VIEW ubec_main.transaction_operations AS
SELECT 
    o.transaction_hash as transaction_id,
    o.type::text as operation_type,
    o.source_account,
    COALESCE(o.from_account, o.source_account) as sender_account,
    COALESCE(o.to_account, o.source_account) as receiver_account,
    o.amount,
    o.asset_code::text as asset_code,
    o.asset_issuer,
    o.created_at,
    o.details as metadata
FROM ubec_main.stellar_operations o
WHERE o.type IN ('payment', 'create_account', 'path_payment');

\echo '✓ transaction_operations view created'

-- Grant permissions
GRANT SELECT ON ubec_main.transaction_operations TO PUBLIC;

-- Verify
DO $$
DECLARE
    row_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO row_count FROM ubec_main.transaction_operations;
    RAISE NOTICE '✓ View verified: transaction_operations has % rows', row_count;
END $$;

-- ============================================================================
-- FIX #3: Ensure Required Indexes Exist
-- ============================================================================

\echo ''
\echo 'Fix #3: Verifying required indexes...'

-- Index for account lookups
CREATE INDEX IF NOT EXISTS idx_stellar_ops_source 
ON ubec_main.stellar_operations(source_account);

CREATE INDEX IF NOT EXISTS idx_stellar_ops_from 
ON ubec_main.stellar_operations(from_account) 
WHERE from_account IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_stellar_ops_to 
ON ubec_main.stellar_operations(to_account) 
WHERE to_account IS NOT NULL;

-- Index for date range queries
CREATE INDEX IF NOT EXISTS idx_stellar_ops_created 
ON ubec_main.stellar_operations(created_at DESC);

-- Index for asset filtering
CREATE INDEX IF NOT EXISTS idx_stellar_ops_asset 
ON ubec_main.stellar_operations(asset_code) 
WHERE asset_code IS NOT NULL;

\echo '✓ All required indexes verified'

-- ============================================================================
-- FIX #4: Add Helper Function for Transaction Queries
-- ============================================================================

\echo ''
\echo 'Fix #4: Creating helper functions...'

-- Function to get transactions for an account
CREATE OR REPLACE FUNCTION ubec_main.get_account_transactions(
    p_account_id VARCHAR(56),
    p_days_back INTEGER DEFAULT 30,
    p_asset_code VARCHAR(12) DEFAULT NULL
)
RETURNS TABLE (
    transaction_id VARCHAR(64),
    operation_type TEXT,
    counterparty VARCHAR(56),
    amount NUMERIC(20,7),
    asset_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        to.transaction_id,
        to.operation_type,
        CASE 
            WHEN to.sender_account = p_account_id THEN to.receiver_account
            ELSE to.sender_account
        END as counterparty,
        to.amount,
        to.asset_code,
        to.created_at
    FROM ubec_main.transaction_operations to
    WHERE (to.sender_account = p_account_id OR to.receiver_account = p_account_id)
        AND to.created_at >= NOW() - (p_days_back || ' days')::INTERVAL
        AND (p_asset_code IS NULL OR to.asset_code = p_asset_code)
    ORDER BY to.created_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;

\echo '✓ Helper function created: get_account_transactions()'

-- ============================================================================
-- FIX #5: Verify Core Tables Exist
-- ============================================================================

\echo ''
\echo 'Fix #5: Verifying core tables...'

DO $$
DECLARE
    tables_to_check TEXT[] := ARRAY[
        'stellar_accounts',
        'stellar_transactions', 
        'stellar_operations',
        'stellar_effects',
        'ubec_balances',
        'ubec_distributions',
        'ubec_holonic_metrics',
        'ubec_sync_status',
        'ubec_audit_log'
    ];
    table_name TEXT;
    table_exists BOOLEAN;
BEGIN
    FOREACH table_name IN ARRAY tables_to_check
    LOOP
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'ubec_main' 
            AND table_name = table_name
        ) INTO table_exists;
        
        IF table_exists THEN
            RAISE NOTICE '✓ Table exists: %', table_name;
        ELSE
            RAISE WARNING '✗ Missing table: %', table_name;
        END IF;
    END LOOP;
END $$;

-- ============================================================================
-- FIX #6: Update Sync Status Table
-- ============================================================================

\echo ''
\echo 'Fix #6: Initializing sync status...'

-- Insert default sync status records if they don't exist
INSERT INTO ubec_main.ubec_sync_status (element, token_code, sync_type, status)
VALUES 
    ('air', 'UBEC', 'accounts', 'pending'),
    ('air', 'UBEC', 'transactions', 'pending'),
    ('air', 'UBEC', 'balances', 'pending'),
    ('water', 'UBECrc', 'accounts', 'pending'),
    ('water', 'UBECrc', 'transactions', 'pending'),
    ('water', 'UBECrc', 'balances', 'pending'),
    ('earth', 'UBECgpi', 'accounts', 'pending'),
    ('earth', 'UBECgpi', 'transactions', 'pending'),
    ('earth', 'UBECgpi', 'balances', 'pending'),
    ('fire', 'UBECtt', 'accounts', 'pending'),
    ('fire', 'UBECtt', 'transactions', 'pending'),
    ('fire', 'UBECtt', 'balances', 'pending')
ON CONFLICT ON CONSTRAINT unique_sync_context DO NOTHING;

\echo '✓ Sync status initialized'

-- ============================================================================
-- VERIFICATION & SUMMARY
-- ============================================================================

\echo ''
\echo '========================================================================'
\echo 'VERIFICATION SUMMARY'
\echo '========================================================================'

-- Check constraint
\echo ''
\echo 'Constraint Check:'
SELECT 
    indexname,
    tablename,
    CASE WHEN indexdef LIKE '%UNIQUE%' THEN '✓ UNIQUE' ELSE '  Regular' END as type
FROM pg_indexes 
WHERE schemaname = 'ubec_main' 
    AND indexname = 'idx_holonic_metrics_unique_agent_date';

-- Check view
\echo ''
\echo 'View Check:'
SELECT 
    table_name,
    CASE 
        WHEN table_type = 'VIEW' THEN '✓ EXISTS' 
        ELSE '  Other' 
    END as status
FROM information_schema.tables 
WHERE table_schema = 'ubec_main' 
    AND table_name = 'transaction_operations';

-- Check row counts
\echo ''
\echo 'Current Data Counts:'
SELECT 
    'stellar_accounts' as table_name,
    COUNT(*) as row_count
FROM ubec_main.stellar_accounts
UNION ALL
SELECT 
    'stellar_operations',
    COUNT(*)
FROM ubec_main.stellar_operations
UNION ALL
SELECT 
    'ubec_balances',
    COUNT(*)
FROM ubec_main.ubec_balances
UNION ALL
SELECT 
    'holonic_metrics',
    COUNT(*)
FROM ubec_main.holonic_metrics
ORDER BY table_name;

-- Check sync status
\echo ''
\echo 'Sync Status:'
SELECT 
    element,
    token_code,
    sync_type,
    status,
    last_sync_time
FROM ubec_main.ubec_sync_status
ORDER BY element, token_code, sync_type;

\echo ''
\echo '========================================================================'
\echo 'FIXES COMPLETE!'
\echo '========================================================================'
\echo ''
\echo 'Next Steps:'
\echo '1. Run sync: python ubec_main_protocol.py --action sync'
\echo '2. Check for errors in output'
\echo '3. Verify data populated: SELECT COUNT(*) FROM ubec_main.stellar_accounts;'
\echo ''
\echo 'If sync still returns 0 accounts, you need to implement the sync logic.'
\echo 'See: UBEC_Sync_Implementation_Guide.md'
\echo '========================================================================'
