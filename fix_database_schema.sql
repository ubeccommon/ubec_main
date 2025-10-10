-- ============================================================================
-- UBEC Database Schema Fix
-- Addresses column naming mismatch in stellar_operations table
-- ============================================================================
-- 
-- Issue: Code references 'destination_account' column which doesn't exist
-- Solution: Create a view for backward compatibility
--
-- This project uses the services of Claude and Anthropic PBC to inform
-- our decisions and recommendations.
--
-- Date: October 10, 2025
-- ============================================================================

BEGIN;

-- ============================================================================
-- SECTION 1: Create Backward Compatibility View
-- ============================================================================

-- Drop view if it already exists
DROP VIEW IF EXISTS ubec_main.transaction_operations CASCADE;

-- Create view that provides the expected column names
-- Maps new schema (to_account, from_account) to old schema (destination_account)
CREATE VIEW ubec_main.transaction_operations AS
SELECT 
    so.operation_id,
    so.id as transaction_id,
    so.type as operation_type,
    so.type_i,
    so.amount,
    so.created_at,
    so.transaction_hash,
    
    -- Map source accounts (prefer from_account, fallback to source_account)
    COALESCE(so.from_account, so.source_account) as source_account,
    
    -- Map destination account (to_account is the correct column)
    so.to_account as destination_account,
    
    -- Asset information
    so.asset_code,
    so.asset_type,
    so.asset_issuer,
    
    -- Element tracking
    so.operation_element as element,
    
    -- Additional fields
    so.details,
    so.metadata
FROM ubec_main.stellar_operations so;

COMMENT ON VIEW ubec_main.transaction_operations IS 
'Backward compatibility view for legacy code that expects transaction_operations table. Maps to_account to destination_account.';

-- ============================================================================
-- SECTION 2: Create Helper View for UBEC Operations
-- ============================================================================

-- Drop view if it already exists
DROP VIEW IF EXISTS ubec_main.ubec_operations CASCADE;

-- Create view that filters for UBEC token operations only
CREATE VIEW ubec_main.ubec_operations AS
SELECT 
    so.operation_id,
    so.transaction_hash,
    so.type as operation_type,
    so.amount,
    so.created_at,
    COALESCE(so.from_account, so.source_account) as source_account,
    so.to_account as destination_account,
    so.asset_code,
    so.asset_issuer,
    so.operation_element as element,
    
    -- Determine operation direction
    CASE 
        WHEN so.to_account IS NOT NULL THEN 'CREDIT'
        WHEN so.from_account IS NOT NULL THEN 'DEBIT'
        ELSE 'OTHER'
    END as operation_direction,
    
    so.details,
    so.metadata
FROM ubec_main.stellar_operations so
WHERE so.asset_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
ORDER BY so.created_at DESC;

COMMENT ON VIEW ubec_main.ubec_operations IS 
'Filtered view showing only UBEC protocol token operations with simplified column names.';

-- ============================================================================
-- SECTION 3: Create Index to Optimize Common Queries
-- ============================================================================

-- These indexes may already exist, but we'll create them if not
CREATE INDEX IF NOT EXISTS idx_stellar_ops_to_asset 
ON ubec_main.stellar_operations(to_account, asset_code) 
WHERE to_account IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_stellar_ops_from_asset 
ON ubec_main.stellar_operations(from_account, asset_code) 
WHERE from_account IS NOT NULL;

-- Combined index for common WHERE clauses
CREATE INDEX IF NOT EXISTS idx_stellar_ops_accounts_asset 
ON ubec_main.stellar_operations(from_account, to_account, asset_code, created_at DESC);

-- ============================================================================
-- SECTION 4: Grant Permissions
-- ============================================================================

-- Grant SELECT on new views to application users
GRANT SELECT ON ubec_main.transaction_operations TO ubec_app;
GRANT SELECT ON ubec_main.transaction_operations TO ubec_readonly;
GRANT SELECT ON ubec_main.transaction_operations TO ubec_sync;

GRANT SELECT ON ubec_main.ubec_operations TO ubec_app;
GRANT SELECT ON ubec_main.ubec_operations TO ubec_readonly;
GRANT SELECT ON ubec_main.ubec_operations TO ubec_sync;

-- ============================================================================
-- SECTION 5: Validation Queries
-- ============================================================================

-- Test the new views
DO $$
DECLARE
    view_count INTEGER;
    op_count INTEGER;
    ubec_count INTEGER;
BEGIN
    -- Check if views exist
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views
    WHERE table_schema = 'ubec_main'
    AND table_name IN ('transaction_operations', 'ubec_operations');
    
    IF view_count = 2 THEN
        RAISE NOTICE '✅ Both views created successfully';
    ELSE
        RAISE WARNING '⚠️  Expected 2 views, found %', view_count;
    END IF;
    
    -- Check if we can query the views
    EXECUTE 'SELECT COUNT(*) FROM ubec_main.transaction_operations' INTO op_count;
    EXECUTE 'SELECT COUNT(*) FROM ubec_main.ubec_operations' INTO ubec_count;
    
    RAISE NOTICE 'Transaction Operations View: % records', op_count;
    RAISE NOTICE 'UBEC Operations View: % records', ubec_count;
    
    IF op_count > 0 THEN
        RAISE NOTICE '✅ transaction_operations view is queryable';
    ELSE
        RAISE NOTICE '⚠️  transaction_operations view is empty (may need sync)';
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- SECTION 6: Quick Test Queries
-- ============================================================================

-- Show sample of data from new views
SELECT 
    '=== Sample from transaction_operations view ===' as info;

SELECT 
    operation_id,
    operation_type,
    source_account,
    destination_account,
    amount,
    asset_code
FROM ubec_main.transaction_operations
LIMIT 5;

SELECT 
    '=== Sample from ubec_operations view ===' as info;

SELECT 
    operation_id,
    operation_type,
    operation_direction,
    source_account,
    destination_account,
    amount,
    asset_code,
    element
FROM ubec_main.ubec_operations
LIMIT 5;

-- Show column mapping
SELECT 
    '=== Column Mapping Verification ===' as info;

SELECT 
    'stellar_operations' as table_name,
    'to_account' as actual_column,
    'destination_account' as view_column,
    'Maps to_account for backward compatibility' as note
UNION ALL
SELECT 
    'stellar_operations',
    'from_account',
    'source_account',
    'Prefers from_account over source_account';

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
