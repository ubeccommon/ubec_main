-- Check UBECrc Issuer Configuration in Database
-- ================================================
-- Run this to verify what issuer address is stored for UBECrc

SELECT 
    setting_key,
    setting_value,
    LENGTH(setting_value) as length,
    CASE 
        WHEN LENGTH(setting_value) = 56 AND setting_value LIKE 'G%' 
        THEN '✅ VALID FORMAT'
        ELSE '❌ INVALID FORMAT'
    END as validation_status,
    CASE
        WHEN setting_value = 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC'
        THEN '✅ CORRECT ISSUER'
        ELSE '❌ WRONG ISSUER'
    END as correctness_check,
    is_active,
    category,
    updated_at
FROM ubec_main.system_settings
WHERE setting_key IN ('ubecrc_issuer', 'ubec_issuer', 'ubecgpi_issuer', 'ubectt_issuer')
ORDER BY setting_key;

-- Expected Results:
-- ================
-- ubecrc_issuer should be: GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC (56 chars)
-- ubec_issuer should be:   GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN (56 chars)
-- ubecgpi_issuer should be: GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC (56 chars)
-- ubectt_issuer should be:  GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC (56 chars)

-- If any are wrong, use the UPDATE statements below:

-- ==========================================
-- FIX SCRIPTS (only run if needed)
-- ==========================================

-- Fix UBECrc issuer if wrong or missing:
-- UPDATE ubec_main.system_settings 
-- SET setting_value = 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC',
--     updated_at = NOW()
-- WHERE setting_key = 'ubecrc_issuer';

-- Or INSERT if it doesn't exist:
-- INSERT INTO ubec_main.system_settings (setting_key, setting_value, category, is_active)
-- VALUES ('ubecrc_issuer', 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC', 'ASSET_CONFIGURATION', true)
-- ON CONFLICT (setting_key) DO UPDATE 
-- SET setting_value = EXCLUDED.setting_value,
--     updated_at = NOW();
