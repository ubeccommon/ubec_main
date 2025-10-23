-- Fix UBECtt Issuer Address
-- ===========================
--
-- Problem: Current address in database is rejected by Stellar SDK
-- Current:  GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC (INVALID)
-- Correct:  GB2WZ6JA3RFVNSGK2XZMHPQSFDFG5KXZSRDRJNHNM7YVDPFSFMJFHVKZ (from docs)
--
-- This address is from your deployment documentation:
-- "UBECtt (Fire) Token Successfully Deployed"
-- Issuer Account: GB2WZ6JA3RFVNSGK2XZMHPQSFDFG5KXZSRDRJNHNM7YVDPFSFMJFHVKZ

-- Step 1: Check current value
SELECT 
    setting_key, 
    setting_value as current_issuer,
    LENGTH(setting_value) as address_length
FROM system_settings
WHERE setting_key = 'ubectt_issuer';

-- Step 2: Update to correct issuer from documentation
UPDATE system_settings 
SET 
    setting_value = 'GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC',
    updated_at = NOW()
WHERE setting_key = 'ubectt_issuer';

-- Step 3: Verify update
SELECT 
    setting_key, 
    setting_value as new_issuer,
    LENGTH(setting_value) as address_length,
    is_active,
    updated_at
FROM system_settings
WHERE setting_key = 'ubectt_issuer';

-- Step 4: Check if we need to update any existing balances
-- (Only needed if the wrong issuer was somehow used to sync data)
SELECT COUNT(*) as ubectt_records
FROM ubec_balances
WHERE token_code = 'UBECtt';

-- If the above shows records, you may want to clear them and re-sync
-- OPTIONAL: Clear existing UBECtt balances to re-sync with correct issuer
-- DELETE FROM ubec_balances WHERE token_code = 'UBECtt';

-- Done! Now re-run sync:
-- python main.py --mode sync --sync-type all
