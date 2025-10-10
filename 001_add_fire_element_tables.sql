-- ============================================================================
-- UBEC Protocol Suite - Fire Element (UBECtt) Tables Migration
-- ============================================================================
-- 
-- Migration: 001_add_fire_element_tables.sql
-- Date: 2025-10-10
-- Element: 🜂 Fire (UBECtt) - Transformation & Regeneration
-- Ubuntu Principle: REGENERATION
-- 
-- This migration adds the core tables for the Fire element protocol:
-- 1. transformative_actions - Records transformative actions and contributions
-- 2. transformation_phases - Tracks transformation phases and momentum
--
-- This project uses the services of Claude and Anthropic PBC to inform our 
-- decisions and recommendations. This project was made possible with the 
-- assistance of Claude and Anthropic PBC.
-- ============================================================================

-- Set search path
SET search_path TO ubec_main, public;

-- ============================================================================
-- ENUM TYPES FOR FIRE ELEMENT
-- ============================================================================

-- Transformation action types
CREATE TYPE transformation_type AS ENUM (
    'individual_growth',        -- Personal development & learning
    'community_building',       -- Creating connections & networks
    'resource_regeneration',    -- Ecological restoration
    'knowledge_creation',       -- Innovation & education
    'system_evolution',         -- Infrastructure improvements
    'cultural_shift',           -- Mindset & paradigm changes
    'economic_transition',      -- New economic models
    'social_healing'            -- Conflict resolution & reconciliation
);

COMMENT ON TYPE transformation_type IS 
'Types of transformative actions in the Ubuntu Economic Commons';

-- Impact scale levels
CREATE TYPE impact_scale AS ENUM (
    'micro',    -- Individual level (1-10 people)
    'meso',     -- Community level (10-100 people)
    'macro',    -- Regional level (100-1000 people)
    'meta'      -- System level (1000+ people)
);

COMMENT ON TYPE impact_scale IS 
'Scale of impact for transformative actions from individual to system-wide';

-- ============================================================================
-- TABLE: transformative_actions
-- ============================================================================

CREATE TABLE IF NOT EXISTS transformative_actions (
    -- Primary identification
    id                      SERIAL PRIMARY KEY,
    action_id               VARCHAR(255) UNIQUE NOT NULL,
    agent_id                VARCHAR(56) NOT NULL,
    
    -- Action classification
    action_type             transformation_type NOT NULL,
    description             TEXT NOT NULL,
    impact_scale            impact_scale NOT NULL,
    
    -- Temporal tracking
    timestamp               TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Impact metrics
    direct_beneficiaries    INTEGER DEFAULT 0 CHECK (direct_beneficiaries >= 0),
    indirect_reach          INTEGER DEFAULT 0 CHECK (indirect_reach >= 0),
    regeneration_score      NUMERIC(5,4) DEFAULT 0.0 CHECK (regeneration_score >= 0 AND regeneration_score <= 1),
    catalytic_multiplier    NUMERIC(5,4) DEFAULT 1.0 CHECK (catalytic_multiplier >= 1 AND catalytic_multiplier <= 10),
    
    -- Verification & validation
    verified                BOOLEAN DEFAULT FALSE,
    verifier_ids            TEXT[] DEFAULT '{}',
    evidence_urls           TEXT[] DEFAULT '{}',
    verification_count      INTEGER GENERATED ALWAYS AS (array_length(verifier_ids, 1)) STORED,
    
    -- Token economics
    ubectt_awarded          NUMERIC(20,7) DEFAULT 0.0 CHECK (ubectt_awarded >= 0),
    distribution_tx_hash    VARCHAR(64),
    reward_calculated_at    TIMESTAMP WITH TIME ZONE,
    reward_distributed_at   TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    tags                    TEXT[] DEFAULT '{}',
    related_actions         TEXT[] DEFAULT '{}',
    metadata                JSONB DEFAULT '{}',
    
    -- Foreign key to stellar_accounts
    CONSTRAINT fk_transformative_agent 
        FOREIGN KEY (agent_id) 
        REFERENCES stellar_accounts(account_id)
        ON DELETE CASCADE
);

-- Table comment
COMMENT ON TABLE transformative_actions IS 
'Records transformative actions and contributions in the Ubuntu Economic Commons (Fire Element - UBECtt)';

-- Column comments
COMMENT ON COLUMN transformative_actions.action_id IS 'Unique identifier for the transformative action';
COMMENT ON COLUMN transformative_actions.agent_id IS 'Stellar account ID of the agent performing the action';
COMMENT ON COLUMN transformative_actions.action_type IS 'Type of transformative action performed';
COMMENT ON COLUMN transformative_actions.description IS 'Detailed description of the transformative action';
COMMENT ON COLUMN transformative_actions.impact_scale IS 'Scale of impact (micro, meso, macro, meta)';
COMMENT ON COLUMN transformative_actions.direct_beneficiaries IS 'Number of people directly affected by this action';
COMMENT ON COLUMN transformative_actions.indirect_reach IS 'Estimated ripple effect reach';
COMMENT ON COLUMN transformative_actions.regeneration_score IS 'Regeneration depth score (0.0 - 1.0)';
COMMENT ON COLUMN transformative_actions.catalytic_multiplier IS 'How much this action amplifies other actions (1.0 - 10.0)';
COMMENT ON COLUMN transformative_actions.verified IS 'Whether the action has been verified by the community';
COMMENT ON COLUMN transformative_actions.verifier_ids IS 'Array of Stellar account IDs who verified this action';
COMMENT ON COLUMN transformative_actions.evidence_urls IS 'URLs to evidence supporting this action';
COMMENT ON COLUMN transformative_actions.ubectt_awarded IS 'Amount of UBECtt tokens awarded for this action';
COMMENT ON COLUMN transformative_actions.distribution_tx_hash IS 'Stellar transaction hash of the token distribution';
COMMENT ON COLUMN transformative_actions.tags IS 'Tags for categorization and search';
COMMENT ON COLUMN transformative_actions.related_actions IS 'IDs of related transformative actions';
COMMENT ON COLUMN transformative_actions.metadata IS 'Additional metadata in JSON format';

-- ============================================================================
-- INDEXES: transformative_actions
-- ============================================================================

CREATE INDEX idx_transformative_actions_agent 
    ON transformative_actions(agent_id);

CREATE INDEX idx_transformative_actions_type 
    ON transformative_actions(action_type);

CREATE INDEX idx_transformative_actions_scale 
    ON transformative_actions(impact_scale);

CREATE INDEX idx_transformative_actions_timestamp 
    ON transformative_actions(timestamp DESC);

CREATE INDEX idx_transformative_actions_verified 
    ON transformative_actions(verified) 
    WHERE verified = TRUE;

CREATE INDEX idx_transformative_actions_awarded 
    ON transformative_actions(ubectt_awarded DESC) 
    WHERE ubectt_awarded > 0;

CREATE INDEX idx_transformative_actions_regen 
    ON transformative_actions(regeneration_score DESC);

CREATE INDEX idx_transformative_actions_catalytic 
    ON transformative_actions(catalytic_multiplier DESC);

CREATE INDEX idx_transformative_actions_tags 
    ON transformative_actions USING gin(tags);

CREATE INDEX idx_transformative_actions_metadata 
    ON transformative_actions USING gin(metadata);

-- Composite indexes for common queries
CREATE INDEX idx_transformative_actions_agent_time 
    ON transformative_actions(agent_id, timestamp DESC);

CREATE INDEX idx_transformative_actions_type_verified 
    ON transformative_actions(action_type, verified);

-- ============================================================================
-- TABLE: transformation_phases
-- ============================================================================

CREATE TABLE IF NOT EXISTS transformation_phases (
    -- Primary identification
    id                          SERIAL PRIMARY KEY,
    phase_id                    VARCHAR(255) UNIQUE NOT NULL,
    name                        VARCHAR(255) NOT NULL,
    description                 TEXT NOT NULL,
    
    -- Temporal tracking
    start_date                  TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date                    TIMESTAMP WITH TIME ZONE,
    created_at                  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Phase characteristics
    target_outcomes             TEXT[] DEFAULT '{}',
    key_indicators              JSONB DEFAULT '{}',
    participating_agents        TEXT[] DEFAULT '{}',
    
    -- Progress tracking
    actions_completed           INTEGER DEFAULT 0 CHECK (actions_completed >= 0),
    total_ubectt_distributed    NUMERIC(20,7) DEFAULT 0.0 CHECK (total_ubectt_distributed >= 0),
    phase_momentum              NUMERIC(5,4) DEFAULT 0.0 CHECK (phase_momentum >= 0 AND phase_momentum <= 1),
    
    -- Status
    is_active                   BOOLEAN DEFAULT TRUE,
    completion_percentage       NUMERIC(5,2) DEFAULT 0.0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    
    -- Metadata
    metadata                    JSONB DEFAULT '{}'
);

-- Table comment
COMMENT ON TABLE transformation_phases IS 
'Tracks transformation phases and their momentum in the Ubuntu Economic Commons (Fire Element - UBECtt)';

-- Column comments
COMMENT ON COLUMN transformation_phases.phase_id IS 'Unique identifier for the transformation phase';
COMMENT ON COLUMN transformation_phases.name IS 'Name of the transformation phase';
COMMENT ON COLUMN transformation_phases.description IS 'Detailed description of the phase';
COMMENT ON COLUMN transformation_phases.start_date IS 'When the transformation phase began';
COMMENT ON COLUMN transformation_phases.end_date IS 'When the transformation phase ended (NULL if ongoing)';
COMMENT ON COLUMN transformation_phases.target_outcomes IS 'Array of target outcomes for this phase';
COMMENT ON COLUMN transformation_phases.key_indicators IS 'Key performance indicators tracked during this phase';
COMMENT ON COLUMN transformation_phases.participating_agents IS 'Array of Stellar account IDs participating in this phase';
COMMENT ON COLUMN transformation_phases.actions_completed IS 'Number of transformative actions completed in this phase';
COMMENT ON COLUMN transformation_phases.total_ubectt_distributed IS 'Total UBECtt tokens distributed during this phase';
COMMENT ON COLUMN transformation_phases.phase_momentum IS 'Rate of transformation in this phase (0.0 - 1.0)';
COMMENT ON COLUMN transformation_phases.is_active IS 'Whether this phase is currently active';
COMMENT ON COLUMN transformation_phases.completion_percentage IS 'Percentage of phase completion (0 - 100)';
COMMENT ON COLUMN transformation_phases.metadata IS 'Additional metadata in JSON format';

-- ============================================================================
-- INDEXES: transformation_phases
-- ============================================================================

CREATE INDEX idx_transformation_phases_active 
    ON transformation_phases(is_active) 
    WHERE is_active = TRUE;

CREATE INDEX idx_transformation_phases_start 
    ON transformation_phases(start_date DESC);

CREATE INDEX idx_transformation_phases_end 
    ON transformation_phases(end_date DESC);

CREATE INDEX idx_transformation_phases_completion 
    ON transformation_phases(completion_percentage DESC);

CREATE INDEX idx_transformation_phases_momentum 
    ON transformation_phases(phase_momentum DESC);

CREATE INDEX idx_transformation_phases_agents 
    ON transformation_phases USING gin(participating_agents);

CREATE INDEX idx_transformation_phases_metadata 
    ON transformation_phases USING gin(metadata);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_transformative_actions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_transformative_actions_timestamp
    BEFORE UPDATE ON transformative_actions
    FOR EACH ROW
    EXECUTE FUNCTION update_transformative_actions_timestamp();

-- Function to update transformation_phases timestamp
CREATE OR REPLACE FUNCTION update_transformation_phases_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_transformation_phases_timestamp
    BEFORE UPDATE ON transformation_phases
    FOR EACH ROW
    EXECUTE FUNCTION update_transformation_phases_timestamp();

-- ============================================================================
-- VIEWS FOR FIRE ELEMENT ANALYTICS
-- ============================================================================

-- View: Active verified transformative actions
CREATE OR REPLACE VIEW active_verified_actions AS
SELECT 
    a.action_id,
    a.agent_id,
    a.action_type,
    a.description,
    a.impact_scale,
    a.timestamp,
    a.direct_beneficiaries,
    a.indirect_reach,
    a.regeneration_score,
    a.catalytic_multiplier,
    a.verification_count,
    a.ubectt_awarded,
    s.home_domain as agent_domain,
    s.primary_element as agent_element
FROM transformative_actions a
LEFT JOIN stellar_accounts s ON a.agent_id = s.account_id
WHERE a.verified = TRUE
ORDER BY a.timestamp DESC;

COMMENT ON VIEW active_verified_actions IS 
'View of all verified transformative actions with agent information';

-- View: Transformation phase summary
CREATE OR REPLACE VIEW transformation_phase_summary AS
SELECT 
    p.phase_id,
    p.name,
    p.start_date,
    p.end_date,
    p.is_active,
    p.completion_percentage,
    p.phase_momentum,
    p.actions_completed,
    p.total_ubectt_distributed,
    array_length(p.participating_agents, 1) as participant_count,
    CASE 
        WHEN p.end_date IS NULL THEN EXTRACT(DAY FROM NOW() - p.start_date)
        ELSE EXTRACT(DAY FROM p.end_date - p.start_date)
    END as duration_days
FROM transformation_phases p
ORDER BY p.start_date DESC;

COMMENT ON VIEW transformation_phase_summary IS 
'Summary view of transformation phases with calculated metrics';

-- View: Agent transformation profile
CREATE OR REPLACE VIEW agent_transformation_profile AS
SELECT 
    a.agent_id,
    COUNT(*) as total_actions,
    COUNT(*) FILTER (WHERE a.verified = TRUE) as verified_actions,
    SUM(a.ubectt_awarded) as total_ubectt_earned,
    AVG(a.regeneration_score) as avg_regeneration_score,
    AVG(a.catalytic_multiplier) as avg_catalytic_multiplier,
    SUM(a.direct_beneficiaries) as total_direct_impact,
    SUM(a.indirect_reach) as total_indirect_impact,
    MIN(a.timestamp) as first_action_date,
    MAX(a.timestamp) as latest_action_date,
    COUNT(DISTINCT a.action_type) as action_type_diversity,
    array_agg(DISTINCT a.action_type) as action_types_performed
FROM transformative_actions a
GROUP BY a.agent_id
ORDER BY total_ubectt_earned DESC;

COMMENT ON VIEW agent_transformation_profile IS 
'Profile of each agent showing their transformation activity and impact';

-- View: Fire element metrics summary
CREATE OR REPLACE VIEW fire_element_metrics AS
SELECT 
    COUNT(DISTINCT a.agent_id) as total_transformative_agents,
    COUNT(*) as total_actions,
    COUNT(*) FILTER (WHERE a.verified = TRUE) as verified_actions,
    SUM(a.ubectt_awarded) as total_ubectt_distributed,
    AVG(a.regeneration_score) as avg_regeneration_score,
    AVG(a.catalytic_multiplier) as avg_catalytic_multiplier,
    SUM(a.direct_beneficiaries) as total_direct_beneficiaries,
    SUM(a.indirect_reach) as total_indirect_reach,
    COUNT(DISTINCT p.phase_id) as total_phases,
    COUNT(DISTINCT p.phase_id) FILTER (WHERE p.is_active = TRUE) as active_phases,
    AVG(p.phase_momentum) FILTER (WHERE p.is_active = TRUE) as avg_phase_momentum
FROM transformative_actions a
CROSS JOIN transformation_phases p;

COMMENT ON VIEW fire_element_metrics IS 
'System-wide metrics for the Fire element (UBECtt) protocol';

-- ============================================================================
-- FUNCTIONS FOR FIRE ELEMENT CALCULATIONS
-- ============================================================================

-- Function to calculate transformation score for an action
CREATE OR REPLACE FUNCTION calculate_transformation_score(
    p_impact_scale impact_scale,
    p_regeneration_score NUMERIC,
    p_catalytic_multiplier NUMERIC,
    p_verified BOOLEAN
) RETURNS NUMERIC AS $$
DECLARE
    v_base_score NUMERIC;
    v_catalytic_factor NUMERIC;
    v_verification_bonus NUMERIC;
    v_composite_score NUMERIC;
BEGIN
    -- Base score from impact scale
    v_base_score := CASE p_impact_scale
        WHEN 'micro' THEN 0.25
        WHEN 'meso' THEN 0.50
        WHEN 'macro' THEN 0.75
        WHEN 'meta' THEN 1.00
        ELSE 0.25
    END;
    
    -- Catalytic factor (capped at 2.0)
    v_catalytic_factor := LEAST(p_catalytic_multiplier, 2.0) / 2.0;
    
    -- Verification bonus
    v_verification_bonus := CASE WHEN p_verified THEN 0.2 ELSE 0.0 END;
    
    -- Calculate composite score
    v_composite_score := 
        (v_base_score * 0.4) +
        (p_regeneration_score * 0.3) +
        (v_catalytic_factor * 0.2) +
        (v_verification_bonus * 0.1);
    
    -- Normalize to 0.0 - 1.0 range
    RETURN LEAST(GREATEST(v_composite_score, 0.0), 1.0);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_transformation_score IS 
'Calculates the transformation score for a transformative action based on multiple factors';

-- Function to calculate phase momentum
CREATE OR REPLACE FUNCTION calculate_phase_momentum(
    p_phase_id VARCHAR
) RETURNS NUMERIC AS $$
DECLARE
    v_avg_score NUMERIC;
    v_action_frequency NUMERIC;
    v_frequency_factor NUMERIC;
    v_momentum NUMERIC;
    v_action_count INTEGER;
    v_days_elapsed INTEGER;
BEGIN
    -- Get actions in this phase
    SELECT 
        AVG(calculate_transformation_score(
            a.impact_scale,
            a.regeneration_score,
            a.catalytic_multiplier,
            a.verified
        )),
        COUNT(*),
        EXTRACT(DAY FROM NOW() - p.start_date)
    INTO v_avg_score, v_action_count, v_days_elapsed
    FROM transformation_phases p
    LEFT JOIN transformative_actions a ON 
        a.agent_id = ANY(p.participating_agents) AND
        a.timestamp >= p.start_date AND
        (p.end_date IS NULL OR a.timestamp <= p.end_date)
    WHERE p.phase_id = p_phase_id
    GROUP BY p.start_date;
    
    -- Return 0 if no actions
    IF v_action_count = 0 OR v_avg_score IS NULL THEN
        RETURN 0.0;
    END IF;
    
    -- Calculate action frequency
    v_action_frequency := v_action_count::NUMERIC / GREATEST(v_days_elapsed, 1);
    v_frequency_factor := LEAST(v_action_frequency / 10.0, 1.0);
    
    -- Calculate momentum
    v_momentum := (v_avg_score * 0.7) + (v_frequency_factor * 0.3);
    
    RETURN LEAST(v_momentum, 1.0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_phase_momentum IS 
'Calculates the transformation momentum for a phase based on recent actions';

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Uncomment to insert sample data for testing
/*
INSERT INTO transformative_actions (
    action_id,
    agent_id,
    action_type,
    description,
    impact_scale,
    direct_beneficiaries,
    indirect_reach,
    regeneration_score,
    catalytic_multiplier,
    verified,
    verifier_ids,
    tags
) VALUES (
    'test_action_001',
    'GEXAMPLE1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890',
    'knowledge_creation',
    'Test transformative action for knowledge sharing',
    'meso',
    25,
    100,
    0.75,
    1.5,
    true,
    ARRAY['GVERIFIER1234567890ABC', 'GVERIFIER2345678901BCD'],
    ARRAY['education', 'community', 'test']
);

INSERT INTO transformation_phases (
    phase_id,
    name,
    description,
    start_date,
    target_outcomes,
    participating_agents,
    is_active
) VALUES (
    'test_phase_001',
    'Test Community Learning Initiative',
    'Test transformation phase for community education',
    NOW() - INTERVAL '30 days',
    ARRAY['10 learning circles', '50 participants trained'],
    ARRAY['GEXAMPLE1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'],
    true
);
*/

-- ============================================================================
-- GRANTS (Adjust based on your role structure)
-- ============================================================================

-- Grant permissions to application role (adjust role name as needed)
GRANT SELECT, INSERT, UPDATE, DELETE ON transformative_actions TO ubec_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON transformation_phases TO ubec_app;
GRANT SELECT ON active_verified_actions TO ubec_app;
GRANT SELECT ON transformation_phase_summary TO ubec_app;
GRANT SELECT ON agent_transformation_profile TO ubec_app;
GRANT SELECT ON fire_element_metrics TO ubec_app;
GRANT EXECUTE ON FUNCTION calculate_transformation_score TO ubec_app;
GRANT EXECUTE ON FUNCTION calculate_phase_momentum TO ubec_app;

-- Grant read-only to reporting role (adjust role name as needed)
GRANT SELECT ON transformative_actions TO ubec_readonly;
GRANT SELECT ON transformation_phases TO ubec_readonly;
GRANT SELECT ON active_verified_actions TO ubec_readonly;
GRANT SELECT ON transformation_phase_summary TO ubec_readonly;
GRANT SELECT ON agent_transformation_profile TO ubec_readonly;
GRANT SELECT ON fire_element_metrics TO ubec_readonly;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify table creation
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'ubec_main' 
    AND tablename IN ('transformative_actions', 'transformation_phases');

-- Verify indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'ubec_main' 
    AND tablename IN ('transformative_actions', 'transformation_phases')
ORDER BY tablename, indexname;

-- Verify views
SELECT 
    schemaname,
    viewname,
    viewowner
FROM pg_views 
WHERE schemaname = 'ubec_main' 
    AND viewname LIKE '%transformation%';

-- Verify functions
SELECT 
    n.nspname as schema,
    p.proname as function_name,
    pg_get_function_result(p.oid) as return_type
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'ubec_main' 
    AND p.proname LIKE '%transformation%';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

SELECT 'Fire Element (UBECtt) tables migration completed successfully!' AS status;
