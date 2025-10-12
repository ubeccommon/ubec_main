-- ============================================================================
-- Fixed calculate_gravitational_mass Function
-- Fixes the aggregation error in the phenomenal schema
-- ============================================================================

-- Drop the existing function if it exists
DROP FUNCTION IF EXISTS phenomenal.calculate_gravitational_mass(VARCHAR, BIGINT);

-- Create the corrected function
CREATE OR REPLACE FUNCTION phenomenal.calculate_gravitational_mass(
    p_entity_type VARCHAR,
    p_entity_id BIGINT
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_connection_count INTEGER;
    v_days_since_creation NUMERIC;
    v_gravitational_mass NUMERIC;
BEGIN
    -- Get the count of unique connections and average days since account creation
    SELECT 
        COUNT(DISTINCT CASE 
            WHEN from_account_id = p_entity_id THEN to_account_id
            WHEN to_account_id = p_entity_id THEN from_account_id
        END) as connection_count,
        MAX(EXTRACT(days FROM (NOW() - a.thrown_at))) as days_since_creation
    INTO v_connection_count, v_days_since_creation
    FROM phenomenal.intentional_relations ir
    CROSS JOIN phenomenal.accounts a
    WHERE (ir.from_account_id = p_entity_id OR ir.to_account_id = p_entity_id)
      AND a.id = p_entity_id
      AND ir.active = TRUE;
    
    -- Handle NULL cases
    v_connection_count := COALESCE(v_connection_count, 0);
    v_days_since_creation := COALESCE(v_days_since_creation, 0);
    
    -- Calculate gravitational mass
    -- Formula: connections * log(1 + days_since_creation)
    -- This gives more weight to older accounts with more connections
    IF v_connection_count > 0 AND v_days_since_creation > 0 THEN
        v_gravitational_mass := v_connection_count * LN(1 + v_days_since_creation);
    ELSE
        v_gravitational_mass := 0;
    END IF;
    
    RETURN v_gravitational_mass;
END;
$$;

-- Add function comment
COMMENT ON FUNCTION phenomenal.calculate_gravitational_mass(VARCHAR, BIGINT) IS 
    'Calculates the gravitational mass of an entity based on its connections and age. '
    'Returns a numeric value representing the entity''s influence in the network.';

-- Test the function
SELECT phenomenal.calculate_gravitational_mass('account', 999999) as test_mass_calculation;
