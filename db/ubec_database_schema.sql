-- ============================================================================
-- UBEC Protocol Database Schema
-- Database: ubec
-- Schema: ubec_main
-- Version: 1.0
-- Date: October 8, 2025
-- 
-- Description:
-- Complete database schema for the UBEC four-element protocol
-- Integrates existing Ubuntu_EcoCoin structure with new element architecture
-- 
-- Elements:
-- 🜁 Air (UBEC)      - Gateway & Universal Access
-- 🜄 Water (UBECrc)  - Flow & Exchange
-- 🜃 Earth (UBECgpi) - Stability & Value
-- 🜂 Fire (UBECtt)   - Transformation & Action
-- ============================================================================

-- ============================================================================
-- DATABASE CREATION
-- ============================================================================

-- Drop database if exists (use with caution in production!)
-- DROP DATABASE IF EXISTS ubec;

-- Create the database
CREATE DATABASE ubec
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE = template0;

COMMENT ON DATABASE ubec IS 'UBEC Protocol - Four Element Token System';

-- Connect to the database
\c ubec;

-- ============================================================================
-- SCHEMA CREATION
-- ============================================================================

-- Create main schema
CREATE SCHEMA IF NOT EXISTS ubec_main;

-- Set search path
SET search_path TO ubec_main, public;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

COMMENT ON SCHEMA ubec_main IS 'Main schema for UBEC four-element protocol';

-- ============================================================================
-- ENUMS AND TYPES
-- ============================================================================

-- Element types
CREATE TYPE ubec_main.element_type AS ENUM (
    'air',      -- UBEC - Gateway
    'water',    -- UBECrc - Flow
    'earth',    -- UBECgpi - Stability
    'fire'      -- UBECtt - Transformation
);

COMMENT ON TYPE ubec_main.element_type IS 'Four element types in UBEC protocol';

-- Token codes
CREATE TYPE ubec_main.token_code AS ENUM (
    'UBEC',     -- Air token
    'UBECrc',   -- Water token
    'UBECgpi',  -- Earth token
    'UBECtt'    -- Fire token
);

COMMENT ON TYPE ubec_main.token_code IS 'Four token codes in UBEC protocol';

-- Ubuntu principles
CREATE TYPE ubec_main.ubuntu_principle AS ENUM (
    'diversity',     -- Air principle
    'reciprocity',   -- Water principle
    'mutualism',     -- Earth principle
    'regeneration',  -- Fire principle
    'holism'         -- System-wide principle
);

COMMENT ON TYPE ubec_main.ubuntu_principle IS 'Five Ubuntu principles';

-- Distribution categories
CREATE TYPE ubec_main.distribution_category AS ENUM (
    'general_circulation',  -- 75%
    'stewardship',          -- 20%
    'administration'        -- 5%
);

COMMENT ON TYPE ubec_main.distribution_category IS 'Token distribution categories (75/20/5)';

-- Transaction types
CREATE TYPE ubec_main.transaction_type AS ENUM (
    'payment',
    'create_account',
    'change_trust',
    'manage_offer',
    'path_payment',
    'account_merge',
    'manage_data',
    'bump_sequence',
    'clawback',
    'other'
);

-- Health status
CREATE TYPE ubec_main.health_status AS ENUM (
    'excellent',
    'good',
    'fair',
    'poor',
    'critical'
);

-- ============================================================================
-- CORE BLOCKCHAIN TABLES
-- ============================================================================

-- Stellar Accounts Table
CREATE TABLE ubec_main.stellar_accounts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(56) NOT NULL UNIQUE,
    
    -- Element tracking
    primary_element element_type,
    token_holdings token_code[],
    
    -- Account data
    sequence BIGINT,
    subentry_count INTEGER DEFAULT 0,
    inflation_destination VARCHAR(56),
    home_domain VARCHAR(255),
    thresholds JSONB,
    flags JSONB,
    signers JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE,
    last_modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    
    -- Tracking
    sync_status VARCHAR(20) DEFAULT 'pending',
    sync_cursor VARCHAR(100),
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT valid_account_id CHECK (LENGTH(account_id) = 56)
);

CREATE INDEX idx_stellar_accounts_account_id ON ubec_main.stellar_accounts(account_id);
CREATE INDEX idx_stellar_accounts_element ON ubec_main.stellar_accounts(primary_element);
CREATE INDEX idx_stellar_accounts_created ON ubec_main.stellar_accounts(created_at);
CREATE INDEX idx_stellar_accounts_activity ON ubec_main.stellar_accounts(last_activity_at);

COMMENT ON TABLE ubec_main.stellar_accounts IS 'Stellar blockchain accounts with element tracking';

-- Stellar Transactions Table
CREATE TABLE ubec_main.stellar_transactions (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(64) NOT NULL UNIQUE,
    ledger_sequence BIGINT NOT NULL,
    
    -- Element context
    primary_element element_type,
    involves_tokens token_code[],
    
    -- Transaction data
    source_account VARCHAR(56) NOT NULL,
    source_account_sequence BIGINT,
    fee_charged BIGINT,
    max_fee BIGINT,
    operation_count INTEGER,
    
    -- Transaction details
    time_bounds JSONB,
    memo_type VARCHAR(20),
    memo VARCHAR(255),
    
    -- Status
    successful BOOLEAN DEFAULT true,
    result_code VARCHAR(50),
    result_xdr TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ledger_close_time TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT fk_source_account FOREIGN KEY (source_account) 
        REFERENCES ubec_main.stellar_accounts(account_id)
);

CREATE INDEX idx_stellar_transactions_hash ON ubec_main.stellar_transactions(transaction_hash);
CREATE INDEX idx_stellar_transactions_ledger ON ubec_main.stellar_transactions(ledger_sequence);
CREATE INDEX idx_stellar_transactions_source ON ubec_main.stellar_transactions(source_account);
CREATE INDEX idx_stellar_transactions_element ON ubec_main.stellar_transactions(primary_element);
CREATE INDEX idx_stellar_transactions_created ON ubec_main.stellar_transactions(created_at);
CREATE INDEX idx_stellar_transactions_tokens ON ubec_main.stellar_transactions USING GIN(involves_tokens);

COMMENT ON TABLE ubec_main.stellar_transactions IS 'Stellar blockchain transactions with element context';

-- Stellar Operations Table
CREATE TABLE ubec_main.stellar_operations (
    id SERIAL PRIMARY KEY,
    operation_id VARCHAR(100) NOT NULL UNIQUE,
    transaction_hash VARCHAR(64) NOT NULL,
    
    -- Element context
    operation_element element_type,
    asset_code token_code,
    
    -- Operation data
    type transaction_type NOT NULL,
    type_i INTEGER,
    source_account VARCHAR(56),
    
    -- Operation-specific data
    amount DECIMAL(20, 7),
    asset_type VARCHAR(20),
    asset_issuer VARCHAR(56),
    from_account VARCHAR(56),
    to_account VARCHAR(56),
    
    -- Additional data
    details JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT fk_transaction_hash FOREIGN KEY (transaction_hash) 
        REFERENCES ubec_main.stellar_transactions(transaction_hash)
);

CREATE INDEX idx_stellar_operations_id ON ubec_main.stellar_operations(operation_id);
CREATE INDEX idx_stellar_operations_tx ON ubec_main.stellar_operations(transaction_hash);
CREATE INDEX idx_stellar_operations_type ON ubec_main.stellar_operations(type);
CREATE INDEX idx_stellar_operations_element ON ubec_main.stellar_operations(operation_element);
CREATE INDEX idx_stellar_operations_asset ON ubec_main.stellar_operations(asset_code);
CREATE INDEX idx_stellar_operations_from ON ubec_main.stellar_operations(from_account);
CREATE INDEX idx_stellar_operations_to ON ubec_main.stellar_operations(to_account);
CREATE INDEX idx_stellar_operations_created ON ubec_main.stellar_operations(created_at);

COMMENT ON TABLE ubec_main.stellar_operations IS 'Stellar blockchain operations with element and asset tracking';

-- Stellar Effects Table
CREATE TABLE ubec_main.stellar_effects (
    id SERIAL PRIMARY KEY,
    effect_id VARCHAR(100) NOT NULL UNIQUE,
    operation_id VARCHAR(100) NOT NULL,
    
    -- Element context
    effect_element element_type,
    
    -- Effect data
    type VARCHAR(50) NOT NULL,
    account VARCHAR(56),
    amount DECIMAL(20, 7),
    asset_type VARCHAR(20),
    asset_code token_code,
    asset_issuer VARCHAR(56),
    
    -- Effect details
    details JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    CONSTRAINT fk_operation_id FOREIGN KEY (operation_id) 
        REFERENCES ubec_main.stellar_operations(operation_id)
);

CREATE INDEX idx_stellar_effects_id ON ubec_main.stellar_effects(effect_id);
CREATE INDEX idx_stellar_effects_operation ON ubec_main.stellar_effects(operation_id);
CREATE INDEX idx_stellar_effects_type ON ubec_main.stellar_effects(type);
CREATE INDEX idx_stellar_effects_account ON ubec_main.stellar_effects(account);
CREATE INDEX idx_stellar_effects_element ON ubec_main.stellar_effects(effect_element);
CREATE INDEX idx_stellar_effects_asset ON ubec_main.stellar_effects(asset_code);
CREATE INDEX idx_stellar_effects_created ON ubec_main.stellar_effects(created_at);

COMMENT ON TABLE ubec_main.stellar_effects IS 'Stellar blockchain effects with element context';

-- ============================================================================
-- UBEC-SPECIFIC TABLES
-- ============================================================================

-- UBEC Balances Table
CREATE TABLE ubec_main.ubec_balances (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(56) NOT NULL,
    
    -- Token and element
    token_code token_code NOT NULL,
    element element_type NOT NULL,
    
    -- Balance data
    balance DECIMAL(20, 7) NOT NULL DEFAULT 0,
    buying_liabilities DECIMAL(20, 7) DEFAULT 0,
    selling_liabilities DECIMAL(20, 7) DEFAULT 0,
    
    -- Trust line data
    limit_amount DECIMAL(20, 7),
    is_authorized BOOLEAN DEFAULT false,
    is_authorized_to_maintain_liabilities BOOLEAN DEFAULT false,
    is_clawback_enabled BOOLEAN DEFAULT false,
    
    -- Distribution category
    distribution_category distribution_category,
    
    -- Timestamps
    last_modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT fk_balance_account FOREIGN KEY (account_id) 
        REFERENCES ubec_main.stellar_accounts(account_id),
    CONSTRAINT unique_account_token UNIQUE (account_id, token_code),
    CONSTRAINT positive_balance CHECK (balance >= 0)
);

CREATE INDEX idx_ubec_balances_account ON ubec_main.ubec_balances(account_id);
CREATE INDEX idx_ubec_balances_token ON ubec_main.ubec_balances(token_code);
CREATE INDEX idx_ubec_balances_element ON ubec_main.ubec_balances(element);
CREATE INDEX idx_ubec_balances_category ON ubec_main.ubec_balances(distribution_category);
CREATE INDEX idx_ubec_balances_balance ON ubec_main.ubec_balances(balance);
CREATE INDEX idx_ubec_balances_modified ON ubec_main.ubec_balances(last_modified_at);

COMMENT ON TABLE ubec_main.ubec_balances IS 'Token balances for all four elements with distribution tracking';

-- UBEC Distributions Table
CREATE TABLE ubec_main.ubec_distributions (
    id SERIAL PRIMARY KEY,
    
    -- Token and element
    token_code token_code NOT NULL,
    element element_type NOT NULL,
    
    -- Distribution data
    category distribution_category NOT NULL,
    target_percentage DECIMAL(5, 2) NOT NULL,
    current_percentage DECIMAL(5, 2) NOT NULL,
    current_amount DECIMAL(20, 7) NOT NULL,
    total_supply DECIMAL(20, 7) NOT NULL,
    
    -- Compliance
    is_compliant BOOLEAN DEFAULT true,
    deviation DECIMAL(5, 2) DEFAULT 0,
    
    -- Timestamps
    snapshot_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_rebalance TIMESTAMP WITH TIME ZONE,
    next_check TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT valid_percentages CHECK (target_percentage >= 0 AND target_percentage <= 100),
    CONSTRAINT valid_current_pct CHECK (current_percentage >= 0 AND current_percentage <= 100)
);

CREATE INDEX idx_ubec_distributions_token ON ubec_main.ubec_distributions(token_code);
CREATE INDEX idx_ubec_distributions_element ON ubec_main.ubec_distributions(element);
CREATE INDEX idx_ubec_distributions_category ON ubec_main.ubec_distributions(category);
CREATE INDEX idx_ubec_distributions_compliance ON ubec_main.ubec_distributions(is_compliant);
CREATE INDEX idx_ubec_distributions_snapshot ON ubec_main.ubec_distributions(snapshot_time);

COMMENT ON TABLE ubec_main.ubec_distributions IS 'Distribution tracking for tokenomics compliance (75/20/5)';

-- UBEC Holonic Metrics Table
CREATE TABLE ubec_main.ubec_holonic_metrics (
    id SERIAL PRIMARY KEY,
    
    -- Scope
    account_id VARCHAR(56),
    element element_type,
    principle ubuntu_principle NOT NULL,
    
    -- Metric data
    score DECIMAL(5, 4) NOT NULL,
    raw_value DECIMAL(20, 7),
    normalized_value DECIMAL(5, 4),
    
    -- Assessment
    health_status health_status,
    assessment_details JSONB,
    
    -- Context
    calculation_method VARCHAR(100),
    data_points INTEGER,
    confidence_level DECIMAL(5, 4),
    
    -- Timestamps
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT fk_holonic_account FOREIGN KEY (account_id) 
        REFERENCES ubec_main.stellar_accounts(account_id),
    CONSTRAINT valid_score CHECK (score >= 0 AND score <= 1),
    CONSTRAINT valid_normalized CHECK (normalized_value IS NULL OR (normalized_value >= 0 AND normalized_value <= 1))
);

CREATE INDEX idx_ubec_holonic_account ON ubec_main.ubec_holonic_metrics(account_id);
CREATE INDEX idx_ubec_holonic_element ON ubec_main.ubec_holonic_metrics(element);
CREATE INDEX idx_ubec_holonic_principle ON ubec_main.ubec_holonic_metrics(principle);
CREATE INDEX idx_ubec_holonic_score ON ubec_main.ubec_holonic_metrics(score);
CREATE INDEX idx_ubec_holonic_health ON ubec_main.ubec_holonic_metrics(health_status);
CREATE INDEX idx_ubec_holonic_calculated ON ubec_main.ubec_holonic_metrics(calculated_at);

COMMENT ON TABLE ubec_main.ubec_holonic_metrics IS 'Ubuntu principle metrics for holonic health assessment';

-- UBEC Audit Log Table
CREATE TABLE ubec_main.ubec_audit_log (
    id SERIAL PRIMARY KEY,
    
    -- Audit context
    element element_type,
    token_code token_code,
    
    -- Audited entity
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    
    -- Audit data
    audit_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    
    -- Findings
    is_valid BOOLEAN DEFAULT true,
    is_anomaly BOOLEAN DEFAULT false,
    anomaly_type VARCHAR(50),
    severity VARCHAR(20),
    
    -- Details
    audit_details JSONB,
    validation_rules JSONB,
    violations JSONB,
    
    -- Timestamps
    audited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    auditor VARCHAR(100),
    
    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_ubec_audit_element ON ubec_main.ubec_audit_log(element);
CREATE INDEX idx_ubec_audit_token ON ubec_main.ubec_audit_log(token_code);
CREATE INDEX idx_ubec_audit_entity ON ubec_main.ubec_audit_log(entity_type, entity_id);
CREATE INDEX idx_ubec_audit_type ON ubec_main.ubec_audit_log(audit_type);
CREATE INDEX idx_ubec_audit_status ON ubec_main.ubec_audit_log(status);
CREATE INDEX idx_ubec_audit_anomaly ON ubec_main.ubec_audit_log(is_anomaly);
CREATE INDEX idx_ubec_audit_time ON ubec_main.ubec_audit_log(audited_at);

COMMENT ON TABLE ubec_main.ubec_audit_log IS 'Audit trail for Fire element transformation validation';

-- UBEC Sync Status Table
CREATE TABLE ubec_main.ubec_sync_status (
    id SERIAL PRIMARY KEY,
    
    -- Sync context
    element element_type,
    token_code token_code,
    sync_type VARCHAR(50) NOT NULL,
    
    -- Sync state
    status VARCHAR(20) NOT NULL,
    cursor VARCHAR(100),
    last_sync_time TIMESTAMP WITH TIME ZONE,
    next_sync_time TIMESTAMP WITH TIME ZONE,
    
    -- Sync statistics
    records_synced INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    duration_ms INTEGER,
    
    -- Details
    sync_details JSONB,
    error_log JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT unique_sync_context UNIQUE (element, token_code, sync_type)
);

CREATE INDEX idx_ubec_sync_element ON ubec_main.ubec_sync_status(element);
CREATE INDEX idx_ubec_sync_token ON ubec_main.ubec_sync_status(token_code);
CREATE INDEX idx_ubec_sync_type ON ubec_main.ubec_sync_status(sync_type);
CREATE INDEX idx_ubec_sync_status ON ubec_main.ubec_sync_status(status);
CREATE INDEX idx_ubec_sync_updated ON ubec_main.ubec_sync_status(updated_at);

COMMENT ON TABLE ubec_main.ubec_sync_status IS 'Synchronization status tracking for all elements';

-- UBEC Reports Table
CREATE TABLE ubec_main.ubec_reports (
    id SERIAL PRIMARY KEY,
    
    -- Report context
    element element_type,
    token_code token_code,
    report_type VARCHAR(50) NOT NULL,
    
    -- Report data
    title VARCHAR(255) NOT NULL,
    summary TEXT,
    content JSONB NOT NULL,
    
    -- Report metadata
    generated_by VARCHAR(100),
    report_period_start TIMESTAMP WITH TIME ZONE,
    report_period_end TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    
    -- Timestamps
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE,
    
    -- Files
    file_path VARCHAR(500),
    file_format VARCHAR(20),
    
    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_ubec_reports_element ON ubec_main.ubec_reports(element);
CREATE INDEX idx_ubec_reports_token ON ubec_main.ubec_reports(token_code);
CREATE INDEX idx_ubec_reports_type ON ubec_main.ubec_reports(report_type);
CREATE INDEX idx_ubec_reports_status ON ubec_main.ubec_reports(status);
CREATE INDEX idx_ubec_reports_generated ON ubec_main.ubec_reports(generated_at);

COMMENT ON TABLE ubec_main.ubec_reports IS 'Generated reports for analysis and compliance';

-- ============================================================================
-- ELEMENT-SPECIFIC VIEWS
-- ============================================================================

-- Air Element View (UBEC - Gateway)
CREATE VIEW ubec_main.view_air_gateway AS
SELECT 
    sa.account_id,
    sa.created_at AS gateway_created,
    sa.last_activity_at,
    ub.balance AS ubec_balance,
    ub.distribution_category,
    hm.score AS diversity_score,
    COUNT(DISTINCT st.transaction_hash) AS transaction_count,
    MAX(st.created_at) AS last_transaction
FROM ubec_main.stellar_accounts sa
LEFT JOIN ubec_main.ubec_balances ub 
    ON sa.account_id = ub.account_id AND ub.token_code = 'UBEC'
LEFT JOIN ubec_main.ubec_holonic_metrics hm 
    ON sa.account_id = hm.account_id 
    AND hm.element = 'air' 
    AND hm.principle = 'diversity'
LEFT JOIN ubec_main.stellar_transactions st 
    ON sa.account_id = st.source_account 
    AND 'UBEC' = ANY(st.involves_tokens)
WHERE sa.primary_element = 'air' OR 'UBEC' = ANY(sa.token_holdings)
GROUP BY sa.account_id, sa.created_at, sa.last_activity_at, 
         ub.balance, ub.distribution_category, hm.score;

COMMENT ON VIEW ubec_main.view_air_gateway IS 'Air element gateway metrics and access points';

-- Water Element View (UBECrc - Flow)
CREATE VIEW ubec_main.view_water_flow AS
SELECT 
    st.transaction_hash,
    st.source_account,
    st.created_at,
    st.ledger_sequence,
    COUNT(so.id) AS operation_count,
    SUM(so.amount) AS total_flow_amount,
    hm.score AS reciprocity_score,
    st.successful
FROM ubec_main.stellar_transactions st
LEFT JOIN ubec_main.stellar_operations so 
    ON st.transaction_hash = so.transaction_hash 
    AND so.asset_code = 'UBECrc'
LEFT JOIN ubec_main.ubec_holonic_metrics hm 
    ON st.source_account = hm.account_id 
    AND hm.element = 'water' 
    AND hm.principle = 'reciprocity'
WHERE st.primary_element = 'water' OR 'UBECrc' = ANY(st.involves_tokens)
GROUP BY st.transaction_hash, st.source_account, st.created_at, 
         st.ledger_sequence, hm.score, st.successful;

COMMENT ON VIEW ubec_main.view_water_flow IS 'Water element flow metrics and exchange patterns';

-- Earth Element View (UBECgpi - Stability)
CREATE VIEW ubec_main.view_earth_stability AS
SELECT 
    ud.token_code,
    ud.category AS distribution_category,
    ud.target_percentage,
    ud.current_percentage,
    ud.current_amount,
    ud.total_supply,
    ud.is_compliant,
    ud.deviation,
    ud.snapshot_time,
    hm.score AS mutualism_score,
    hm.health_status
FROM ubec_main.ubec_distributions ud
LEFT JOIN ubec_main.ubec_holonic_metrics hm 
    ON ud.element = hm.element 
    AND hm.principle = 'mutualism'
WHERE ud.element = 'earth' AND ud.token_code = 'UBECgpi';

COMMENT ON VIEW ubec_main.view_earth_stability IS 'Earth element stability and distribution compliance';

-- Fire Element View (UBECtt - Transformation)
CREATE VIEW ubec_main.view_fire_transformation AS
SELECT 
    so.operation_id,
    so.transaction_hash,
    so.type AS operation_type,
    so.source_account,
    so.created_at,
    so.amount,
    al.is_valid AS validation_status,
    al.is_anomaly,
    al.audit_type,
    hm.score AS regeneration_score
FROM ubec_main.stellar_operations so
LEFT JOIN ubec_main.ubec_audit_log al 
    ON so.operation_id = al.entity_id 
    AND al.entity_type = 'operation'
LEFT JOIN ubec_main.ubec_holonic_metrics hm 
    ON so.source_account = hm.account_id 
    AND hm.element = 'fire' 
    AND hm.principle = 'regeneration'
WHERE so.operation_element = 'fire' OR so.asset_code = 'UBECtt';

COMMENT ON VIEW ubec_main.view_fire_transformation IS 'Fire element transformative actions and audit status';

-- System-Wide Holonic Health View
CREATE VIEW ubec_main.view_system_holonic_health AS
SELECT 
    hm.element,
    hm.principle,
    AVG(hm.score) AS avg_score,
    MIN(hm.score) AS min_score,
    MAX(hm.score) AS max_score,
    COUNT(*) AS sample_count,
    MODE() WITHIN GROUP (ORDER BY hm.health_status) AS most_common_status,
    MAX(hm.calculated_at) AS last_calculation
FROM ubec_main.ubec_holonic_metrics hm
WHERE hm.calculated_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY hm.element, hm.principle
ORDER BY hm.element, hm.principle;

COMMENT ON VIEW ubec_main.view_system_holonic_health IS 'System-wide Ubuntu principle health across all elements';

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update last_modified timestamp
CREATE OR REPLACE FUNCTION ubec_main.update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION ubec_main.update_updated_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for stellar_accounts
CREATE TRIGGER trg_stellar_accounts_modified
    BEFORE UPDATE ON ubec_main.stellar_accounts
    FOR EACH ROW
    EXECUTE FUNCTION ubec_main.update_modified_timestamp();

-- Trigger for ubec_balances
CREATE TRIGGER trg_ubec_balances_modified
    BEFORE UPDATE ON ubec_main.ubec_balances
    FOR EACH ROW
    EXECUTE FUNCTION ubec_main.update_modified_timestamp();

-- Trigger for ubec_sync_status
CREATE TRIGGER trg_ubec_sync_updated
    BEFORE UPDATE ON ubec_main.ubec_sync_status
    FOR EACH ROW
    EXECUTE FUNCTION ubec_main.update_updated_timestamp();

-- Function to map token to element
CREATE OR REPLACE FUNCTION ubec_main.get_element_for_token(token token_code)
RETURNS element_type AS $$
BEGIN
    RETURN CASE token
        WHEN 'UBEC' THEN 'air'::element_type
        WHEN 'UBECrc' THEN 'water'::element_type
        WHEN 'UBECgpi' THEN 'earth'::element_type
        WHEN 'UBECtt' THEN 'fire'::element_type
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION ubec_main.get_element_for_token IS 'Maps token code to corresponding element type';

-- Function to map principle to element
CREATE OR REPLACE FUNCTION ubec_main.get_element_for_principle(principle ubuntu_principle)
RETURNS element_type AS $$
BEGIN
    RETURN CASE principle
        WHEN 'diversity' THEN 'air'::element_type
        WHEN 'reciprocity' THEN 'water'::element_type
        WHEN 'mutualism' THEN 'earth'::element_type
        WHEN 'regeneration' THEN 'fire'::element_type
        WHEN 'holism' THEN NULL  -- System-wide
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION ubec_main.get_element_for_principle IS 'Maps Ubuntu principle to corresponding element type';

-- Function to calculate distribution compliance
CREATE OR REPLACE FUNCTION ubec_main.check_distribution_compliance(
    p_token_code token_code,
    p_tolerance DECIMAL DEFAULT 5.0
)
RETURNS BOOLEAN AS $$
DECLARE
    v_compliant BOOLEAN := true;
    v_deviation DECIMAL;
BEGIN
    -- Check if any category deviates more than tolerance
    SELECT MAX(ABS(deviation)) INTO v_deviation
    FROM ubec_main.ubec_distributions
    WHERE token_code = p_token_code
        AND snapshot_time = (
            SELECT MAX(snapshot_time) 
            FROM ubec_main.ubec_distributions 
            WHERE token_code = p_token_code
        );
    
    IF v_deviation > p_tolerance THEN
        v_compliant := false;
    END IF;
    
    RETURN v_compliant;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ubec_main.check_distribution_compliance IS 'Checks if token distribution is within compliance tolerance';

-- Function to get latest holonic score
CREATE OR REPLACE FUNCTION ubec_main.get_latest_holonic_score(
    p_element element_type,
    p_principle ubuntu_principle
)
RETURNS DECIMAL AS $$
DECLARE
    v_score DECIMAL;
BEGIN
    SELECT AVG(score) INTO v_score
    FROM ubec_main.ubec_holonic_metrics
    WHERE element = p_element
        AND principle = p_principle
        AND calculated_at > CURRENT_TIMESTAMP - INTERVAL '24 hours';
    
    RETURN COALESCE(v_score, 0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ubec_main.get_latest_holonic_score IS 'Gets latest average holonic score for element/principle';

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default distribution targets for all tokens
INSERT INTO ubec_main.ubec_distributions (token_code, element, category, target_percentage, current_percentage, current_amount, total_supply, is_compliant)
VALUES
    -- UBEC (Air)
    ('UBEC', 'air', 'general_circulation', 75.00, 0, 0, 0, true),
    ('UBEC', 'air', 'stewardship', 20.00, 0, 0, 0, true),
    ('UBEC', 'air', 'administration', 5.00, 0, 0, 0, true),
    
    -- UBECrc (Water) - More flow
    ('UBECrc', 'water', 'general_circulation', 70.00, 0, 0, 0, true),
    ('UBECrc', 'water', 'stewardship', 25.00, 0, 0, 0, true),
    ('UBECrc', 'water', 'administration', 5.00, 0, 0, 0, true),
    
    -- UBECgpi (Earth) - More stability
    ('UBECgpi', 'earth', 'general_circulation', 80.00, 0, 0, 0, true),
    ('UBECgpi', 'earth', 'stewardship', 15.00, 0, 0, 0, true),
    ('UBECgpi', 'earth', 'administration', 5.00, 0, 0, 0, true),
    
    -- UBECtt (Fire) - More control
    ('UBECtt', 'fire', 'general_circulation', 65.00, 0, 0, 0, true),
    ('UBECtt', 'fire', 'stewardship', 25.00, 0, 0, 0, true),
    ('UBECtt', 'fire', 'administration', 10.00, 0, 0, 0, true)
ON CONFLICT DO NOTHING;

-- Initialize sync status for all elements
INSERT INTO ubec_main.ubec_sync_status (element, token_code, sync_type, status)
VALUES
    ('air', 'UBEC', 'accounts', 'ready'),
    ('air', 'UBEC', 'transactions', 'ready'),
    ('air', 'UBEC', 'balances', 'ready'),
    
    ('water', 'UBECrc', 'accounts', 'ready'),
    ('water', 'UBECrc', 'transactions', 'ready'),
    ('water', 'UBECrc', 'balances', 'ready'),
    
    ('earth', 'UBECgpi', 'accounts', 'ready'),
    ('earth', 'UBECgpi', 'transactions', 'ready'),
    ('earth', 'UBECgpi', 'balances', 'ready'),
    
    ('fire', 'UBECtt', 'accounts', 'ready'),
    ('fire', 'UBECtt', 'transactions', 'ready'),
    ('fire', 'UBECtt', 'balances', 'ready')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PERMISSIONS (adjust as needed for your environment)
-- ============================================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA ubec_main TO PUBLIC;

-- Grant select on all tables and views
GRANT SELECT ON ALL TABLES IN SCHEMA ubec_main TO PUBLIC;

-- Grant execute on all functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ubec_main TO PUBLIC;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '===========================================================';
    RAISE NOTICE 'UBEC Protocol Database Schema Installation Complete!';
    RAISE NOTICE '===========================================================';
    RAISE NOTICE 'Database: ubec';
    RAISE NOTICE 'Schema: ubec_main';
    RAISE NOTICE '';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - 5 custom types (element_type, token_code, etc.)';
    RAISE NOTICE '  - 11 core tables (accounts, transactions, balances, etc.)';
    RAISE NOTICE '  - 5 element-specific views';
    RAISE NOTICE '  - 6 utility functions';
    RAISE NOTICE '  - 3 triggers';
    RAISE NOTICE '';
    RAISE NOTICE 'Elements configured:';
    RAISE NOTICE '  🜁 Air (UBEC)      - Gateway & Universal Access';
    RAISE NOTICE '  🜄 Water (UBECrc)  - Flow & Exchange';
    RAISE NOTICE '  🜃 Earth (UBECgpi) - Stability & Value';
    RAISE NOTICE '  🜂 Fire (UBECtt)   - Transformation & Action';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Update issuer addresses in your configuration';
    RAISE NOTICE '  2. Run the synchronizer to populate blockchain data';
    RAISE NOTICE '  3. Review and adjust permissions as needed';
    RAISE NOTICE '===========================================================';
END $$;
