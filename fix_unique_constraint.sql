-- ============================================================================
-- Fix: Add unique constraint to holonic_metrics table
-- ============================================================================
-- Version: 5.2.1-hotfix
-- Date: October 15, 2025
-- Purpose: Add unique constraint required for upsert functionality
-- ============================================================================

-- Check existing constraints first
SELECT 
    tc.constraint_name, 
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.table_schema = 'ubec_main'
AND tc.table_name = 'holonic_metrics'
ORDER BY tc.constraint_type, kcu.ordinal_position;

-- Add unique constraint on (account_id, evaluation_date)
-- This allows one evaluation per account per timestamp
ALTER TABLE ubec_main.holonic_metrics 
    ADD CONSTRAINT uq_holonic_metrics_account_date 
    UNIQUE (account_id, evaluation_date);

-- Verify the constraint was added
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'ubec_main.holonic_metrics'::regclass
AND conname = 'uq_holonic_metrics_account_date';

-- ============================================================================
-- Notes:
-- ============================================================================
-- 1. This constraint ensures one evaluation per account per timestamp
-- 2. If you have duplicate data, clean it first:
--
--    -- Find duplicates
--    SELECT account_id, evaluation_date, COUNT(*)
--    FROM ubec_main.holonic_metrics
--    GROUP BY account_id, evaluation_date
--    HAVING COUNT(*) > 1;
--
--    -- Keep only the most recent (by id or created_at)
--    DELETE FROM ubec_main.holonic_metrics a
--    USING ubec_main.holonic_metrics b
--    WHERE a.id < b.id
--    AND a.account_id = b.account_id
--    AND a.evaluation_date = b.evaluation_date;
--
-- 3. After adding constraint, the upsert will work correctly
-- ============================================================================
