-- Remove Foreign Key Constraint from holonic_metrics
-- This allows holonic evaluations to run without requiring stellar_accounts table
--
-- Background: V8 migration added a foreign key to stellar_accounts, but that
-- table may not be populated yet. This script removes the constraint so
-- evaluations can proceed.
--
-- The constraint can be re-added later once stellar_accounts is populated.
--
-- This project uses the services of Claude and Anthropic PBC.

BEGIN;

-- Drop the foreign key constraint
ALTER TABLE ubec_main.holonic_metrics
DROP CONSTRAINT IF EXISTS holonic_metrics_account_id_fkey;

-- Verify the constraint is gone
DO $$
DECLARE
    fk_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE table_schema = 'ubec_main' 
        AND table_name = 'holonic_metrics'
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name = 'holonic_metrics_account_id_fkey'
    ) INTO fk_exists;
    
    IF NOT fk_exists THEN
        RAISE NOTICE '✅ Foreign key constraint successfully removed';
    ELSE
        RAISE NOTICE '❌ Foreign key constraint still exists';
    END IF;
END $$;

COMMIT;

-- Show current constraints on holonic_metrics
SELECT 
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'ubec_main'
AND table_name = 'holonic_metrics'
ORDER BY constraint_type, constraint_name;
