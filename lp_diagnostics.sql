-- ============================================================================
-- Liquidity Pool Synchronization Diagnostics (CORRECTED)
-- Run these queries to verify LP sync is working correctly
-- ============================================================================

-- Connect to database
-- \c ubec

SET search_path TO ubec_main, public;

-- ============================================================================
-- 1. CHECK TABLE STRUCTURE
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'LIQUIDITY POOLS TABLE STRUCTURE'
\echo '===================================================================='

SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'ubec_main' 
    AND table_name = 'liquidity_pools'
ORDER BY ordinal_position;

-- ============================================================================
-- 2. CHECK POOL RECORDS
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'LIQUIDITY POOL RECORDS'
\echo '===================================================================='

SELECT 
    id,
    pair,
    token_code,
    primary_element,
    asset_a_code,
    asset_b_code,
    reserve_a,
    reserve_b,
    balance as ubec_balance,
    ubec_asset_position,
    trustline_count,
    sync_timestamp,
    sync_status
FROM liquidity_pools
ORDER BY balance DESC NULLS LAST, sync_timestamp DESC
LIMIT 20;

-- ============================================================================
-- 3. CHECK POOL OWNERS/PARTICIPANTS
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'LIQUIDITY POOL OWNERS/PARTICIPANTS'
\echo '===================================================================='

SELECT 
    lpo.account_id,
    lpo.liquidity_pool_id,
    lp.pair,
    lpo.shares,
    lpo.ownership_percentage,
    lpo.ubec_balance,
    lpo.token_code,
    lpo.element,
    lpo.sync_timestamp
FROM liquidity_pool_owners lpo
JOIN liquidity_pools lp ON lpo.liquidity_pool_id = lp.id
ORDER BY lpo.ubec_balance DESC
LIMIT 20;

-- ============================================================================
-- 4. SUMMARY STATISTICS
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'SUMMARY STATISTICS'
\echo '===================================================================='

SELECT 
    COUNT(*) as total_pools,
    COUNT(DISTINCT CASE WHEN token_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt') 
                   THEN id END) as ubec_pools,
    SUM(CASE WHEN ubec_asset_position IS NOT NULL THEN balance ELSE 0 END) as total_ubec_in_pools,
    SUM(trustline_count) as total_participants,
    MAX(sync_timestamp) as last_sync_time
FROM liquidity_pools;

-- ============================================================================
-- 5. POOLS BY ASSET
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'POOLS BY UBEC ASSET'
\echo '===================================================================='

SELECT 
    token_code as ubec_asset,
    primary_element,
    COUNT(*) as pool_count,
    SUM(balance) as total_balance,
    SUM(trustline_count) as total_participants
FROM liquidity_pools
WHERE token_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
GROUP BY token_code, primary_element
ORDER BY total_balance DESC NULLS LAST;

-- ============================================================================
-- 6. TOP POOLS BY TVL
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'TOP POOLS BY UBEC TVL'
\echo '===================================================================='

SELECT 
    pair,
    token_code,
    balance as ubec_tvl,
    ubec_asset_position,
    trustline_count as participants,
    ROUND(reserve_a::numeric, 2) as reserve_a,
    ROUND(reserve_b::numeric, 2) as reserve_b,
    fee_bp,
    sync_timestamp,
    sync_status
FROM liquidity_pools
WHERE balance > 0
ORDER BY balance DESC
LIMIT 10;

-- ============================================================================
-- 7. RECENT SYNC ACTIVITY
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'RECENT SYNC ACTIVITY'
\echo '===================================================================='

SELECT 
    pair,
    token_code,
    asset_a_code,
    asset_b_code,
    balance,
    trustline_count,
    sync_timestamp,
    AGE(NOW(), sync_timestamp) as time_since_sync,
    sync_status
FROM liquidity_pools
WHERE sync_timestamp IS NOT NULL
ORDER BY sync_timestamp DESC
LIMIT 10;

-- ============================================================================
-- 8. POOLS WITHOUT UBEC POSITION
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'POOLS WITHOUT UBEC POSITION (POSSIBLE ISSUES)'
\echo '===================================================================='

SELECT 
    id,
    pair,
    token_code,
    asset_a_code,
    asset_a_issuer,
    asset_b_code,
    asset_b_issuer,
    balance,
    ubec_asset_position,
    sync_timestamp,
    sync_status
FROM liquidity_pools
WHERE token_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
  AND ubec_asset_position IS NULL
LIMIT 10;

-- ============================================================================
-- 9. PARTICIPANT DISTRIBUTION BY POOL
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'PARTICIPANT SHARE DISTRIBUTION BY POOL'
\echo '===================================================================='

SELECT 
    lp.pair,
    lp.token_code,
    COUNT(lpo.account_id) as participant_count,
    SUM(lpo.shares) as total_shares_held,
    AVG(lpo.ownership_percentage) as avg_ownership_pct,
    SUM(lpo.ubec_balance) as total_ubec_distributed,
    MAX(lpo.ownership_percentage) as max_ownership_pct,
    MIN(lpo.ownership_percentage) as min_ownership_pct
FROM liquidity_pool_owners lpo
JOIN liquidity_pools lp ON lpo.liquidity_pool_id = lp.id
GROUP BY lp.pair, lp.token_code, lp.id
ORDER BY participant_count DESC
LIMIT 10;

-- ============================================================================
-- 10. TOP LP HOLDERS BY UBEC BALANCE
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'TOP LP HOLDERS BY UBEC BALANCE'
\echo '===================================================================='

SELECT 
    lpo.account_id,
    lpo.token_code,
    COUNT(DISTINCT lpo.liquidity_pool_id) as pools_participating,
    SUM(lpo.ubec_balance) as total_ubec_from_lps,
    SUM(lpo.shares) as total_shares,
    AVG(lpo.ownership_percentage) as avg_ownership_pct,
    MAX(lpo.sync_timestamp) as last_sync
FROM liquidity_pool_owners lpo
GROUP BY lpo.account_id, lpo.token_code
ORDER BY total_ubec_from_lps DESC
LIMIT 20;

-- ============================================================================
-- 11. OWNERSHIP PERCENTAGE DISTRIBUTION
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'OWNERSHIP PERCENTAGE DISTRIBUTION'
\echo '===================================================================='

SELECT 
    CASE 
        WHEN ownership_percentage >= 50 THEN '>= 50%'
        WHEN ownership_percentage >= 25 THEN '25-50%'
        WHEN ownership_percentage >= 10 THEN '10-25%'
        WHEN ownership_percentage >= 5 THEN '5-10%'
        WHEN ownership_percentage >= 1 THEN '1-5%'
        ELSE '< 1%'
    END as ownership_bracket,
    COUNT(*) as position_count,
    SUM(ubec_balance) as total_ubec_in_bracket
FROM liquidity_pool_owners
GROUP BY ownership_bracket
ORDER BY MIN(ownership_percentage) DESC;

-- ============================================================================
-- 12. VERIFICATION CHECKLIST
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'VERIFICATION CHECKLIST'
\echo '===================================================================='

SELECT 
    'Tables Exist' as check_item,
    CASE WHEN COUNT(*) = 2 THEN '✓ PASS' ELSE '✗ FAIL' END as status
FROM information_schema.tables
WHERE table_schema = 'ubec_main' 
    AND table_name IN ('liquidity_pools', 'liquidity_pool_owners')

UNION ALL

SELECT 
    'Pools Synced',
    CASE WHEN COUNT(*) > 0 THEN '✓ PASS (' || COUNT(*) || ' pools)' ELSE '✗ FAIL (0 pools)' END
FROM liquidity_pools

UNION ALL

SELECT 
    'UBEC Pools Exist',
    CASE WHEN COUNT(*) > 0 THEN '✓ PASS (' || COUNT(*) || ' UBEC pools)' ELSE '✗ FAIL (0 UBEC pools)' END
FROM liquidity_pools
WHERE token_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')

UNION ALL

SELECT 
    'Participants Tracked',
    CASE WHEN COUNT(*) > 0 THEN '✓ PASS (' || COUNT(*) || ' participants)' ELSE '✗ FAIL (0 participants)' END
FROM liquidity_pool_owners

UNION ALL

SELECT 
    'Recent Sync (< 1 hour)',
    CASE WHEN MAX(sync_timestamp) > NOW() - INTERVAL '1 hour' 
         THEN '✓ PASS (synced ' || AGE(NOW(), MAX(sync_timestamp)) || ' ago)' 
         WHEN MAX(sync_timestamp) IS NULL THEN '✗ FAIL (never synced)'
         ELSE '⚠ WARNING (last sync: ' || AGE(NOW(), MAX(sync_timestamp)) || ' ago)' 
    END
FROM liquidity_pools

UNION ALL

SELECT
    'Total UBEC in LPs',
    '✓ INFO (' || ROUND(COALESCE(SUM(balance), 0)::numeric, 2) || ' UBEC)'
FROM liquidity_pools
WHERE token_code = 'UBEC'

UNION ALL

SELECT
    'Active Sync Status',
    CASE 
        WHEN COUNT(*) FILTER (WHERE sync_status = 'active') > 0 
        THEN '✓ PASS (' || COUNT(*) FILTER (WHERE sync_status = 'active') || ' active)'
        ELSE '⚠ WARNING (0 active)'
    END
FROM liquidity_pools;

\echo ''
\echo '===================================================================='
\echo 'Diagnostics Complete'
\echo '===================================================================='
\echo ''
\echo 'NEXT STEPS:'
\echo '============'
\echo ''
\echo 'If you see "0 pools" but sync reported finding pools:'
\echo '  1. Check asset matching - compare issuer addresses'
\echo '  2. Verify INSERT permissions for the role'
\echo '  3. Check for database errors in application logs'
\echo ''
\echo 'If pools synced successfully:'
\echo '  ✓ Review TVL calculations'
\echo '  ✓ Verify participant ownership percentages'
\echo '  ✓ Check distribution compliance reports'
\echo ''
