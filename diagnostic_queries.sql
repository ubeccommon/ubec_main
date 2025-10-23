-- UBEC Token Holder Diagnostic Queries
-- ======================================
-- Run these queries in psql to diagnose why tokens show 0 holders

-- 1. Check issuer configuration in database
-- -----------------------------------------
SELECT 
    setting_key, 
    setting_value as issuer_address,
    is_active,
    updated_at
FROM system_settings
WHERE setting_key LIKE '%issuer%'
ORDER BY setting_key;

-- Expected result: Should show issuer(s) for tokens
-- If you see only 'ubec_issuer', that's the problem!


-- 2. Count holders by token in database
-- --------------------------------------
SELECT 
    token_code,
    COUNT(*) as holder_count,
    SUM(balance) as total_supply,
    MIN(balance) as min_balance,
    MAX(balance) as max_balance
FROM ubec_balances
WHERE balance > 0
GROUP BY token_code
ORDER BY token_code;

-- Expected result: Should show holders for all tokens that are distributed


-- 3. Check if token-specific issuer settings exist
-- -----------------------------------------------
SELECT 
    setting_key,
    setting_value,
    CASE 
        WHEN setting_key = 'ubec_issuer' THEN 'UBEC (Air)'
        WHEN setting_key = 'ubecrc_issuer' THEN 'UBECrc (Water)'
        WHEN setting_key = 'ubecgpi_issuer' THEN 'UBECgpi (Earth)'
        WHEN setting_key = 'ubectt_issuer' THEN 'UBECtt (Fire)'
        ELSE 'Unknown'
    END as token_name
FROM system_settings
WHERE setting_key IN ('ubec_issuer', 'ubecrc_issuer', 'ubecgpi_issuer', 'ubectt_issuer')
    AND is_active = TRUE;

-- If this returns only 1 row, that's the problem!


-- 4. Sample data from ubec_balances
-- ----------------------------------
SELECT 
    token_code,
    element,
    account_id,
    balance,
    last_modified_at
FROM ubec_balances
WHERE balance > 0
ORDER BY token_code, balance DESC
LIMIT 20;


-- 5. Check if tokens exist but with different issuers
-- --------------------------------------------------
-- This query helps identify if there are multiple issuers in use
SELECT DISTINCT
    token_code,
    COUNT(DISTINCT account_id) as unique_holders
FROM ubec_balances
GROUP BY token_code
ORDER BY token_code;


-- ============================================
-- DIAGNOSTIC ANALYSIS
-- ============================================

-- If you see:
-- ✓ UBEC: 641 holders  → Using correct issuer
-- ✗ UBECrc: 0 holders   → Either not distributed OR wrong issuer
-- ✗ UBECgpi: 0 holders  → Either not distributed OR wrong issuer  
-- ✗ UBECtt: 0 holders   → Either not distributed OR wrong issuer

-- MOST LIKELY CAUSE:
-- -----------------
-- Your project uses DIFFERENT issuers for each token (per env.example),
-- but the synchronizer is only looking up ONE issuer ('ubec_issuer')
-- and using it for all four tokens.

-- SOLUTION OPTIONS:
-- ----------------
-- Option 1: Add all issuer settings to database
INSERT INTO system_settings (setting_key, setting_value, setting_type, is_active, category)
VALUES 
    ('ubec_issuer', 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN', 'string', true, 'stellar'),
    ('ubecrc_issuer', 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC', 'string', true, 'stellar'),
    ('ubecgpi_issuer', 'GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC', 'string', true, 'stellar'),
    ('ubectt_issuer', 'GB2WZ6JA3RFVNSGK2XZMHPQSFDFG5KXZSRDRJNHNM7YVDPFSFMJFHVKZ', 'string', true, 'stellar')
ON CONFLICT (setting_key) DO UPDATE SET 
    setting_value = EXCLUDED.setting_value,
    is_active = EXCLUDED.is_active;

-- Option 2: Use same issuer for all tokens (if they're actually issued by same account)
-- Just verify which issuer address is correct and update system_settings


-- ============================================
-- VERIFICATION QUERIES (after fix)
-- ============================================

-- Run sync again, then check:
SELECT 
    token_code,
    COUNT(*) as holders,
    SUM(balance) as total_supply
FROM ubec_balances
WHERE balance > 0
GROUP BY token_code
ORDER BY token_code;

-- Should now show holders for all distributed tokens
