-- ============================================================================
-- UBEC Database Migration: Add Missing Stellar Operation Types to transaction_type
-- ============================================================================
-- 
-- Migration: expand_transaction_type_enum_v1
-- Date: 2025-11-19
-- Author: UBEC Protocol Development Team
-- 
-- Purpose:
--   Expand the ubec_main.transaction_type enum to include ALL Stellar Protocol 20
--   operation types (27 total).
--   
--   CORRECTION: The enum is called "transaction_type" in "ubec_main" schema,
--   not "operation_type" in "ubec_main" schema.
--
-- Usage:
--   psql -h localhost -U ubec_admin -d ubec -f expand_transaction_type_enum.sql
--
-- ============================================================================

\echo '============================================================================'
\echo 'UBEC Database Migration: Expand transaction_type Enum'
\echo '============================================================================'
\echo ''
\echo 'Current transaction_type enum values:'
\echo ''

SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = 'ubec_main.transaction_type'::regtype 
ORDER BY enumsortorder;

\echo ''
\echo '============================================================================'
\echo 'Adding missing operation types...'
\echo '============================================================================'
\echo ''

-- ============================================================================
-- Add Missing Operation Types (Alphabetically Ordered)
-- ============================================================================
-- NOTE: PostgreSQL requires each ALTER TYPE ADD VALUE to run separately

-- BEGIN_SPONSORING_FUTURE_RESERVES (Protocol 14)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'begin_sponsoring_future_reserves';
    RAISE NOTICE '✓ Added: begin_sponsoring_future_reserves';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: begin_sponsoring_future_reserves (already exists)';
END $$;

-- CLAIM_CLAIMABLE_BALANCE (Protocol 14)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'claim_claimable_balance';
    RAISE NOTICE '✓ Added: claim_claimable_balance';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: claim_claimable_balance (already exists)';
END $$;

-- CLAWBACK (Protocol 17)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'clawback';
    RAISE NOTICE '✓ Added: clawback';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: clawback (already exists)';
END $$;

-- CLAWBACK_CLAIMABLE_BALANCE (Protocol 17)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'clawback_claimable_balance';
    RAISE NOTICE '✓ Added: clawback_claimable_balance';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: clawback_claimable_balance (already exists)';
END $$;

-- CREATE_CLAIMABLE_BALANCE (Protocol 14)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'create_claimable_balance';
    RAISE NOTICE '✓ Added: create_claimable_balance';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: create_claimable_balance (already exists)';
END $$;

-- END_SPONSORING_FUTURE_RESERVES (Protocol 14)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'end_sponsoring_future_reserves';
    RAISE NOTICE '✓ Added: end_sponsoring_future_reserves';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: end_sponsoring_future_reserves (already exists)';
END $$;

-- EXTEND_FOOTPRINT_TTL (Protocol 20 - Soroban)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'extend_footprint_ttl';
    RAISE NOTICE '✓ Added: extend_footprint_ttl';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: extend_footprint_ttl (already exists)';
END $$;

-- INFLATION (Deprecated but may exist in historical data)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'inflation';
    RAISE NOTICE '✓ Added: inflation';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: inflation (already exists)';
END $$;

-- INVOKE_HOST_FUNCTION (Protocol 20 - Soroban)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'invoke_host_function';
    RAISE NOTICE '✓ Added: invoke_host_function';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: invoke_host_function (already exists)';
END $$;

-- LIQUIDITY_POOL_DEPOSIT (Protocol 18)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'liquidity_pool_deposit';
    RAISE NOTICE '✓ Added: liquidity_pool_deposit';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: liquidity_pool_deposit (already exists)';
END $$;

-- LIQUIDITY_POOL_WITHDRAW (Protocol 18)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'liquidity_pool_withdraw';
    RAISE NOTICE '✓ Added: liquidity_pool_withdraw';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: liquidity_pool_withdraw (already exists)';
END $$;

-- RESTORE_FOOTPRINT (Protocol 20 - Soroban)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'restore_footprint';
    RAISE NOTICE '✓ Added: restore_footprint';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: restore_footprint (already exists)';
END $$;

-- REVOKE_SPONSORSHIP (Protocol 15)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'revoke_sponsorship';
    RAISE NOTICE '✓ Added: revoke_sponsorship';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: revoke_sponsorship (already exists)';
END $$;

-- SET_TRUST_LINE_FLAGS (Protocol 17)
DO $$ 
BEGIN
    ALTER TYPE ubec_main.transaction_type ADD VALUE IF NOT EXISTS 'set_trust_line_flags';
    RAISE NOTICE '✓ Added: set_trust_line_flags';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '- Skipped: set_trust_line_flags (already exists)';
END $$;

-- ============================================================================
-- Verify Migration
-- ============================================================================

\echo ''
\echo '============================================================================'
\echo 'Updated transaction_type enum values:'
\echo '============================================================================'
\echo ''

SELECT 
    enumlabel as operation_type,
    enumsortorder as sort_order
FROM pg_enum 
WHERE enumtypid = 'ubec_main.transaction_type'::regtype 
ORDER BY enumsortorder;

-- ============================================================================
-- Summary Report
-- ============================================================================

DO $$ 
DECLARE
    enum_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO enum_count
    FROM pg_enum 
    WHERE enumtypid = 'ubec_main.transaction_type'::regtype;
    
    RAISE NOTICE '';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Migration Complete: Expand transaction_type Enum';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Schema: ubec_main';
    RAISE NOTICE 'Enum Type: transaction_type';
    RAISE NOTICE 'Total operation types: %', enum_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Expected: 27 operation types for complete Stellar Protocol 20 support';
    RAISE NOTICE '';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. Deploy updated ubec_data_synchronizer.py (v5.2.8)';
    RAISE NOTICE '  2. Restart UBEC services: systemctl restart ubec-protocol';
    RAISE NOTICE '  3. Run synchronization: python main.py sync --sync-type all';
    RAISE NOTICE '  4. Monitor logs for new operation types being captured';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- Attribution
-- ============================================================================
-- 
-- This project uses the services of Claude and Anthropic PBC to inform our
-- decisions and recommendations. This project was made possible with the
-- assistance of Claude and Anthropic PBC.
-- 
-- ============================================================================
