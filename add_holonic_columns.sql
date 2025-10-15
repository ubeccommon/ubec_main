-- ============================================================================
-- Migration: Add optional columns to holonic_metrics table
-- ============================================================================
-- Version: 5.2.1
-- Date: October 15, 2025
-- Purpose: Add confidence and calculation_mode columns to support enhanced
--          holonic evaluation features while maintaining backward compatibility
-- ============================================================================

-- Add confidence column (stores evaluation confidence score 0-1)
ALTER TABLE ubec_main.holonic_metrics 
    ADD COLUMN IF NOT EXISTS confidence NUMERIC(10,6) DEFAULT 0.8;

-- Add calculation_mode column (stores 'transaction_based' or 'balance_based')
ALTER TABLE ubec_main.holonic_metrics 
    ADD COLUMN IF NOT EXISTS calculation_mode TEXT DEFAULT 'transaction_based';

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_holonic_metrics_confidence 
    ON ubec_main.holonic_metrics(confidence);

CREATE INDEX IF NOT EXISTS idx_holonic_metrics_calculation_mode 
    ON ubec_main.holonic_metrics(calculation_mode);

-- Update any existing NULL values (shouldn't be any, but just in case)
UPDATE ubec_main.holonic_metrics 
SET confidence = 0.8 
WHERE confidence IS NULL;

UPDATE ubec_main.holonic_metrics 
SET calculation_mode = 'transaction_based' 
WHERE calculation_mode IS NULL;

-- Verify the changes
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'ubec_main'
AND table_name = 'holonic_metrics'
AND column_name IN ('confidence', 'calculation_mode')
ORDER BY column_name;

-- ============================================================================
-- Notes:
-- ============================================================================
-- 1. These columns are OPTIONAL - the evaluator gracefully handles their absence
-- 2. Adding these columns enables:
--    - Enhanced evaluation transparency (confidence scoring)
--    - Calculation mode tracking (transaction vs balance-based)
-- 3. If you don't add these columns, the evaluator will:
--    - Use default confidence of 0.8
--    - Use default calculation_mode of 'transaction_based'
--    - Log warnings on initialization
-- ============================================================================
