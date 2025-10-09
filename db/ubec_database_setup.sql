-- ============================================================================
-- UBEC Protocol Suite - PostgreSQL Database Setup
-- ============================================================================
-- Database: ubec
-- Schema: ubec_main
-- Purpose: Integrated four-element protocol with existing Ubuntu_EcoCoin modules
-- Date: October 8, 2025
-- ============================================================================

-- ============================================================================
-- STEP 1: CREATE DATABASE (Run as superuser)
-- ============================================================================
-- Note: This section should be run separately by a database superuser
-- Connect to postgres database first, then run:

-- DROP DATABASE IF EXISTS ubec;
-- CREATE DATABASE ubec
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'en_US.UTF-8'
--     LC_CTYPE = 'en_US.UTF-8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1;

-- COMMENT ON DATABASE ubec IS 'UBEC Protocol Suite - Four Element Token System';

-- ============================================================================
-- STEP 2: CONNECT TO DATABASE AND CREATE SCHEMA
-- ============================================================================
-- Now connect to the ubec database and run the rest:
-- \c ubec

-- Drop schema if exists (for clean install)
DROP SCHEMA IF EXISTS ubec_main CASCADE;

-- Create main schema
CREATE SCHEMA ubec_main;

COMMENT ON SCHEMA ubec_main IS 'Main schema for UBEC Protocol Suite';

-- Set search path
SET search_path TO ubec_main, public;

-- ============================================================================
-- STEP 3: CREATE EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- STEP 4: CREATE CUSTOM TYPES
-- ============================================================================

-- Element types for the four-element protocol
CREATE TYPE element_type AS ENUM ('air', 'water', 'earth', 'fire');
COMMENT ON TYPE element_type IS 'Four elements: air=UBEC, water=UBECrc, earth=UBECgpi, fire=UBECtt';

-- Token codes
CREATE TYPE token_code AS ENUM ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt');
COMMENT ON TYPE token_code IS 'Four UBEC token types';

-- Distribution categories
CREATE TYPE distribution_category AS ENUM ('general_circulation', 'stewardship', 'administration');
COMMENT ON TYPE distribution_category IS 'Token distribution categories: 75%, 20%, 5%';

-- Ubuntu principles
CREATE TYPE ubuntu_principle AS ENUM ('diversity', 'reciprocity', 'mutualism', 'regeneration', 'holism');
COMMENT ON TYPE ubuntu_principle IS 'Five Ubuntu principles mapped to elements';

-- Transaction types
CREATE TYPE transaction_type AS ENUM (
    'create_account',
    'payment',
    'path_payment_strict_receive',
    'path_payment_strict_send',
    'manage_sell_offer',
    'manage_buy_offer',
    'create_passive_sell_offer',
    'set_options',
    'change_trust',
    'allow_trust',
    'account_merge',
    'inflation',
    'manage_data',
    'bump_sequence',
    'create_claimable_balance',
    'claim_claimable_balance',
    'begin_sponsoring_future_reserves',
    'end_sponsoring_future_reserves',
    'revoke_sponsorship'
);
COMMENT ON TYPE transaction_type IS 'Stellar transaction operation types';

-- Health status
CREATE TYPE health_status AS ENUM ('excellent', 'good', 'fair', 'poor', 'critical');
COMMENT ON TYPE health_status IS 'System health status levels';

-- ============================================================================
-- STEP 5: CORE BLOCKCHAIN TABLES
-- ============================================================================

-- Stellar Accounts Table
CREATE TABLE stellar_accounts (
    id BIGSERIAL PRIMARY KEY,
    account_id VARCHAR(56) NOT NULL UNIQUE,
    token_type token_code,
    element element_type,
    balance NUMERIC(20, 7) DEFAULT 0,
    sequence_number BIGINT,
    num_subentries INTEGER DEFAULT 0,
    num_sponsoring INTEGER DEFAULT 0,
    num_sponsored INTEGER DEFAULT 0,
    flags INTEGER DEFAULT 0,
    home_domain VARCHAR(255),
    inflation_destination VARCHAR(56),
    last_modified_ledger INTEGER,
    last_modified_time TIMESTAMP WITH TIME ZONE,
    thresholds_low INTEGER DEFAULT 0,
    thresholds_med INTEGER DEFAULT 0,
    thresholds_high INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT valid_stellar_address CHECK (account_id ~ '^G[A-Z2-7]{55}$')
);

CREATE INDEX idx_stellar_accounts_account_id ON stellar_accounts(account_id);
CREATE INDEX idx_stellar_accounts_token_type ON stellar_accounts(token_type);
CREATE INDEX idx_stellar_accounts_element ON stellar_accounts(element);
CREATE INDEX idx_stellar_accounts_active ON stellar_accounts(is_active);
CREATE INDEX idx_stellar_accounts_updated ON stellar_accounts(updated_at DESC);

COMMENT ON TABLE stellar_accounts IS 'Stellar blockchain accounts holding UBEC tokens';
COMMENT ON COLUMN stellar_accounts.element IS 'Element association based on primary token held';

-- Stellar Transactions Table
CREATE TABLE stellar_transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_hash VARCHAR(64) NOT NULL UNIQUE,
    ledger_sequence INTEGER NOT NULL,
    token_type token_code,
    element element_type,
    source_account VARCHAR(56) NOT NULL,
    fee_charged BIGINT NOT NULL,
    operation_count INTEGER NOT NULL,
    memo_type VARCHAR(20),
    memo TEXT,
    time_bounds_min BIGINT,
    time_bounds_max BIGINT,
    successful BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    paging_token VARCHAR(50),
    CONSTRAINT valid_tx_hash CHECK (transaction_hash ~ '^[a-f0-9]{64}$')
);

CREATE INDEX idx_stellar_txs_hash ON stellar_transactions(transaction_hash);
CREATE INDEX idx_stellar_txs_ledger ON stellar_transactions(ledger_sequence DESC);
CREATE INDEX idx_stellar_txs_token ON stellar_transactions(token_type);
CREATE INDEX idx_stellar_txs_element ON stellar_transactions(element);
CREATE INDEX idx_stellar_txs_source ON stellar_transactions(source_account);
CREATE INDEX idx_stellar_txs_created ON stellar_transactions(created_at DESC);
CREATE INDEX idx_stellar_txs_successful ON stellar_transactions(successful);

COMMENT ON TABLE stellar_transactions IS 'Stellar blockchain transactions for UBEC tokens';

-- Stellar Operations Table
CREATE TABLE stellar_operations (
    id BIGSERIAL PRIMARY KEY,
    operation_id VARCHAR(50) NOT NULL UNIQUE,
    transaction_id BIGINT NOT NULL REFERENCES stellar_transactions(id) ON DELETE CASCADE,
    token_type token_code,
    element element_type,
    source_account VARCHAR(56),
    type transaction_type NOT NULL,
    type_i INTEGER NOT NULL,
    asset_type VARCHAR(20),
    asset_code VARCHAR(12),
    asset_issuer VARCHAR(56),
    amount NUMERIC(20, 7),
    from_account VARCHAR(56),
    to_account VARCHAR(56),
    starting_balance NUMERIC(20, 7),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_transformative BOOLEAN DEFAULT FALSE,
    CONSTRAINT valid_op_id CHECK (operation_id ~ '^[0-9]+-[0-9]+$')
);

CREATE INDEX idx_stellar_ops_id ON stellar_operations(operation_id);
CREATE INDEX idx_stellar_ops_tx ON stellar_operations(transaction_id);
CREATE INDEX idx_stellar_ops_token ON stellar_operations(token_type);
CREATE INDEX idx_stellar_ops_element ON stellar_operations(element);
CREATE INDEX idx_stellar_ops_type ON stellar_operations(type);
CREATE INDEX idx_stellar_ops_from ON stellar_operations(from_account);
CREATE INDEX idx_stellar_ops_to ON stellar_operations(to_account);
CREATE INDEX idx_stellar_ops_created ON stellar_operations(created_at DESC);
CREATE INDEX idx_stellar_ops_transformative ON stellar_operations(is_transformative);

COMMENT ON TABLE stellar_operations IS 'Individual operations within Stellar transactions';
COMMENT ON COLUMN stellar_operations.is_transformative IS 'Flag for Fire element transformative actions';

-- Stellar Effects Table
CREATE TABLE stellar_effects (
    id BIGSERIAL PRIMARY KEY,
    effect_id VARCHAR(50) NOT NULL UNIQUE,
    operation_id BIGINT NOT NULL REFERENCES stellar_operations(id) ON DELETE CASCADE,
    token_type token_code,
    element element_type,
    account VARCHAR(56),
    type VARCHAR(50) NOT NULL,
    type_i INTEGER NOT NULL,
    amount NUMERIC(20, 7),
    asset_type VARCHAR(20),
    asset_code VARCHAR(12),
    asset_issuer VARCHAR(56),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_stellar_effects_id ON stellar_effects(effect_id);
CREATE INDEX idx_stellar_effects_op ON stellar_effects(operation_id);
CREATE INDEX idx_stellar_effects_token ON stellar_effects(token_type);
CREATE INDEX idx_stellar_effects_element ON stellar_effects(element);
CREATE INDEX idx_stellar_effects_account ON stellar_effects(account);
CREATE INDEX idx_stellar_effects_type ON stellar_effects(type);

COMMENT ON TABLE stellar_effects IS 'Effects resulting from Stellar operations';

-- ============================================================================
-- STEP 6: UBEC-SPECIFIC TABLES
-- ============================================================================

-- UBEC Balances Table (Current Holdings)
CREATE TABLE ubec_balances (
    id BIGSERIAL PRIMARY KEY,
    account_id VARCHAR(56) NOT NULL,
    token_type token_code NOT NULL,
    element element_type NOT NULL,
    balance NUMERIC(20, 7) NOT NULL DEFAULT 0,
    distribution_category distribution_category,
    last_transaction_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(account_id, token_type),
    FOREIGN KEY (account_id) REFERENCES stellar_accounts(account_id) ON DELETE CASCADE,
    CONSTRAINT balance_non_negative CHECK (balance >= 0)
);

CREATE INDEX idx_ubec_balances_account ON ubec_balances(account_id);
CREATE INDEX idx_ubec_balances_token ON ubec_balances(token_type);
CREATE INDEX idx_ubec_balances_element ON ubec_balances(element);
CREATE INDEX idx_ubec_balances_category ON ubec_balances(distribution_category);
CREATE INDEX idx_ubec_balances_updated ON ubec_balances(updated_at DESC);

COMMENT ON TABLE ubec_balances IS 'Current token balances for all UBEC accounts';
COMMENT ON COLUMN ubec_balances.distribution_category IS 'Classification for 75/20/5 distribution rule';

-- UBEC Distribution Tracking Table
CREATE TABLE ubec_distributions (
    id BIGSERIAL PRIMARY KEY,
    token_type token_code NOT NULL,
    element element_type NOT NULL,
    category distribution_category NOT NULL,
    total_amount NUMERIC(20, 7) NOT NULL DEFAULT 0,
    account_count INTEGER NOT NULL DEFAULT 0,
    percentage NUMERIC(5, 2) NOT NULL DEFAULT 0,
    target_percentage NUMERIC(5, 2) NOT NULL,
    deviation NUMERIC(5, 2) NOT NULL DEFAULT 0,
    is_compliant BOOLEAN NOT NULL DEFAULT TRUE,
    snapshot_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(token_type, category, snapshot_date),
    CONSTRAINT percentage_range CHECK (percentage >= 0 AND percentage <= 100),
    CONSTRAINT deviation_range CHECK (deviation >= -100 AND deviation <= 100)
);

CREATE INDEX idx_ubec_dist_token ON ubec_distributions(token_type);
CREATE INDEX idx_ubec_dist_element ON ubec_distributions(element);
CREATE INDEX idx_ubec_dist_category ON ubec_distributions(category);
CREATE INDEX idx_ubec_dist_compliant ON ubec_distributions(is_compliant);
CREATE INDEX idx_ubec_dist_snapshot ON ubec_distributions(snapshot_date DESC);

COMMENT ON TABLE ubec_distributions IS 'Token distribution tracking for compliance monitoring';
COMMENT ON COLUMN ubec_distributions.target_percentage IS 'Target: 75% general, 20% stewardship, 5% admin';

-- UBEC Holonic Metrics Table
CREATE TABLE ubec_holonic_metrics (
    id BIGSERIAL PRIMARY KEY,
    account_id VARCHAR(56),
    token_type token_code,
    element element_type,
    principle ubuntu_principle NOT NULL,
    score NUMERIC(5, 4) NOT NULL,
    confidence NUMERIC(5, 4) DEFAULT 1.0,
    data_points INTEGER DEFAULT 0,
    calculation_method VARCHAR(100),
    metadata JSONB,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (account_id) REFERENCES stellar_accounts(account_id) ON DELETE CASCADE,
    CONSTRAINT score_range CHECK (score >= 0 AND score <= 1),
    CONSTRAINT confidence_range CHECK (confidence >= 0 AND confidence <= 1)
);

CREATE INDEX idx_holonic_account ON ubec_holonic_metrics(account_id);
CREATE INDEX idx_holonic_token ON ubec_holonic_metrics(token_type);
CREATE INDEX idx_holonic_element ON ubec_holonic_metrics(element);
CREATE INDEX idx_holonic_principle ON ubec_holonic_metrics(principle);
CREATE INDEX idx_holonic_score ON ubec_holonic_metrics(score DESC);
CREATE INDEX idx_holonic_calculated ON ubec_holonic_metrics(calculated_at DESC);

COMMENT ON TABLE ubec_holonic_metrics IS 'Ubuntu principles assessment for accounts and network';
COMMENT ON COLUMN ubec_holonic_metrics.principle IS 'diversity=air, reciprocity=water, mutualism=earth, regeneration=fire';

-- Network-wide Holonic Health Table
CREATE TABLE ubec_holonic_health (
    id BIGSERIAL PRIMARY KEY,
    token_type token_code,
    element element_type,
    diversity_score NUMERIC(5, 4) DEFAULT 0,
    reciprocity_score NUMERIC(5, 4) DEFAULT 0,
    mutualism_score NUMERIC(5, 4) DEFAULT 0,
    regeneration_score NUMERIC(5, 4) DEFAULT 0,
    holism_score NUMERIC(5, 4) DEFAULT 0,
    overall_score NUMERIC(5, 4) DEFAULT 0,
    health_status health_status,
    total_accounts INTEGER DEFAULT 0,
    active_accounts INTEGER DEFAULT 0,
    assessment_notes TEXT,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_holonic_health_token ON ubec_holonic_health(token_type);
CREATE INDEX idx_holonic_health_element ON ubec_holonic_health(element);
CREATE INDEX idx_holonic_health_status ON ubec_holonic_health(health_status);
CREATE INDEX idx_holonic_health_calculated ON ubec_holonic_health(calculated_at DESC);

COMMENT ON TABLE ubec_holonic_health IS 'System-wide holonic health snapshots';

-- ============================================================================
-- STEP 7: ELEMENT-SPECIFIC TABLES
-- ============================================================================

-- Air Element (UBEC) - Gateway Metrics
CREATE TABLE air_gateway_metrics (
    id BIGSERIAL PRIMARY KEY,
    account_id VARCHAR(56) NOT NULL,
    first_entry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    entry_method VARCHAR(50),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    access_level VARCHAR(50) DEFAULT 'basic',
    diversity_contribution NUMERIC(5, 4) DEFAULT 0,
    gateway_score NUMERIC(5, 4) DEFAULT 0,
    is_active_gateway BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (account_id) REFERENCES stellar_accounts(account_id) ON DELETE CASCADE
);

CREATE INDEX idx_air_gateway_account ON air_gateway_metrics(account_id);
CREATE INDEX idx_air_gateway_active ON air_gateway_metrics(is_active_gateway);
CREATE INDEX idx_air_gateway_score ON air_gateway_metrics(gateway_score DESC);

COMMENT ON TABLE air_gateway_metrics IS 'Air element: Gateway access and diversity metrics';

-- Water Element (UBECrc) - Flow Metrics
CREATE TABLE water_flow_metrics (
    id BIGSERIAL PRIMARY KEY,
    from_account VARCHAR(56) NOT NULL,
    to_account VARCHAR(56) NOT NULL,
    transaction_count INTEGER DEFAULT 0,
    total_volume NUMERIC(20, 7) DEFAULT 0,
    reciprocity_score NUMERIC(5, 4) DEFAULT 0,
    flow_balance NUMERIC(10, 2) DEFAULT 0,
    last_flow_date TIMESTAMP WITH TIME ZONE,
    is_balanced_flow BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (from_account) REFERENCES stellar_accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (to_account) REFERENCES stellar_accounts(account_id) ON DELETE CASCADE
);

CREATE INDEX idx_water_flow_from ON water_flow_metrics(from_account);
CREATE INDEX idx_water_flow_to ON water_flow_metrics(to_account);
CREATE INDEX idx_water_flow_reciprocity ON water_flow_metrics(reciprocity_score DESC);
CREATE INDEX idx_water_flow_balanced ON water_flow_metrics(is_balanced_flow);

COMMENT ON TABLE water_flow_metrics IS 'Water element: Transaction flow and reciprocity analysis';

-- Earth Element (UBECgpi) - Stability Metrics
CREATE TABLE earth_stability_metrics (
    id BIGSERIAL PRIMARY KEY,
    account_id VARCHAR(56) NOT NULL,
    balance NUMERIC(20, 7) NOT NULL,
    balance_volatility NUMERIC(10, 4) DEFAULT 0,
    holding_duration_days INTEGER DEFAULT 0,
    stability_score NUMERIC(5, 4) DEFAULT 0,
    mutualism_score NUMERIC(5, 4) DEFAULT 0,
    support_network_size INTEGER DEFAULT 0,
    is_stable_holder BOOLEAN DEFAULT TRUE,
    last_major_change TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (account_id) REFERENCES stellar_accounts(account_id) ON DELETE CASCADE
);

CREATE INDEX idx_earth_stability_account ON earth_stability_metrics(account_id);
CREATE INDEX idx_earth_stability_score ON earth_stability_metrics(stability_score DESC);
CREATE INDEX idx_earth_stability_mutualism ON earth_stability_metrics(mutualism_score DESC);
CREATE INDEX idx_earth_stability_stable ON earth_stability_metrics(is_stable_holder);

COMMENT ON TABLE earth_stability_metrics IS 'Earth element: Value stability and mutualism tracking';

-- Fire Element (UBECtt) - Transformation Metrics
CREATE TABLE fire_transformation_metrics (
    id BIGSERIAL PRIMARY KEY,
    account_id VARCHAR(56) NOT NULL,
    operation_id BIGINT NOT NULL,
    transformation_type VARCHAR(50) NOT NULL,
    impact_score NUMERIC(5, 4) DEFAULT 0,
    community_benefit NUMERIC(5, 4) DEFAULT 0,
    regeneration_score NUMERIC(5, 4) DEFAULT 0,
    catalyst_effectiveness NUMERIC(5, 4) DEFAULT 0,
    is_validated BOOLEAN DEFAULT FALSE,
    validation_notes TEXT,
    transformation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (account_id) REFERENCES stellar_accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (operation_id) REFERENCES stellar_operations(id) ON DELETE CASCADE
);

CREATE INDEX idx_fire_transform_account ON fire_transformation_metrics(account_id);
CREATE INDEX idx_fire_transform_operation ON fire_transformation_metrics(operation_id);
CREATE INDEX idx_fire_transform_type ON fire_transformation_metrics(transformation_type);
CREATE INDEX idx_fire_transform_impact ON fire_transformation_metrics(impact_score DESC);
CREATE INDEX idx_fire_transform_validated ON fire_transformation_metrics(is_validated);
CREATE INDEX idx_fire_transform_date ON fire_transformation_metrics(transformation_date DESC);

COMMENT ON TABLE fire_transformation_metrics IS 'Fire element: Transformative actions and regeneration tracking';

-- ============================================================================
-- STEP 8: AUDIT AND MONITORING TABLES
-- ============================================================================

-- UBEC Audit Log
CREATE TABLE ubec_audit_log (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    token_type token_code,
    element element_type,
    account_id VARCHAR(56),
    transaction_hash VARCHAR(64),
    operation_id VARCHAR(50),
    description TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    flagged BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'system'
);

CREATE INDEX idx_audit_event_type ON ubec_audit_log(event_type);
CREATE INDEX idx_audit_token ON ubec_audit_log(token_type);
CREATE INDEX idx_audit_element ON ubec_audit_log(element);
CREATE INDEX idx_audit_account ON ubec_audit_log(account_id);
CREATE INDEX idx_audit_severity ON ubec_audit_log(severity);
CREATE INDEX idx_audit_flagged ON ubec_audit_log(flagged);
CREATE INDEX idx_audit_created ON ubec_audit_log(created_at DESC);

COMMENT ON TABLE ubec_audit_log IS 'Comprehensive audit trail for all UBEC activities';

-- Anomaly Detection Table
CREATE TABLE ubec_anomalies (
    id BIGSERIAL PRIMARY KEY,
    anomaly_type VARCHAR(50) NOT NULL,
    token_type token_code,
    element element_type,
    account_id VARCHAR(56),
    transaction_hash VARCHAR(64),
    severity health_status NOT NULL,
    description TEXT NOT NULL,
    confidence_score NUMERIC(5, 4) DEFAULT 0,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT confidence_valid CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

CREATE INDEX idx_anomalies_type ON ubec_anomalies(anomaly_type);
CREATE INDEX idx_anomalies_token ON ubec_anomalies(token_type);
CREATE INDEX idx_anomalies_element ON ubec_anomalies(element);
CREATE INDEX idx_anomalies_account ON ubec_anomalies(account_id);
CREATE INDEX idx_anomalies_severity ON ubec_anomalies(severity);
CREATE INDEX idx_anomalies_resolved ON ubec_anomalies(is_resolved);
CREATE INDEX idx_anomalies_detected ON ubec_anomalies(detected_at DESC);

COMMENT ON TABLE ubec_anomalies IS 'Detected anomalies and unusual patterns';

-- ============================================================================
-- STEP 9: SYNCHRONIZATION AND STATUS TABLES
-- ============================================================================

-- Sync Status Table
CREATE TABLE ubec_sync_status (
    id BIGSERIAL PRIMARY KEY,
    token_type token_code NOT NULL UNIQUE,
    element element_type NOT NULL,
    last_sync_ledger INTEGER,
    last_sync_time TIMESTAMP WITH TIME ZONE,
    cursor VARCHAR(50),
    sync_status VARCHAR(20) DEFAULT 'idle',
    accounts_synced INTEGER DEFAULT 0,
    transactions_synced INTEGER DEFAULT 0,
    operations_synced INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sync_status_token ON ubec_sync_status(token_type);
CREATE INDEX idx_sync_status_element ON ubec_sync_status(element);
CREATE INDEX idx_sync_status_active ON ubec_sync_status(is_active);

COMMENT ON TABLE ubec_sync_status IS 'Synchronization status for each token type';

-- System Health Table
CREATE TABLE ubec_system_health (
    id BIGSERIAL PRIMARY KEY,
    component VARCHAR(50) NOT NULL,
    token_type token_code,
    element element_type,
    status health_status NOT NULL,
    uptime_seconds BIGINT DEFAULT 0,
    last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    metadata JSONB,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_system_health_component ON ubec_system_health(component);
CREATE INDEX idx_system_health_token ON ubec_system_health(token_type);
CREATE INDEX idx_system_health_element ON ubec_system_health(element);
CREATE INDEX idx_system_health_status ON ubec_system_health(status);
CREATE INDEX idx_system_health_check ON ubec_system_health(last_check DESC);

COMMENT ON TABLE ubec_system_health IS 'Real-time system health monitoring';

-- ============================================================================
-- STEP 10: REPORTING AND ANALYTICS TABLES
-- ============================================================================

-- Reports Table
CREATE TABLE ubec_reports (
    id BIGSERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    token_type token_code,
    element element_type,
    report_title VARCHAR(255) NOT NULL,
    report_data JSONB NOT NULL,
    summary TEXT,
    generated_by VARCHAR(100) DEFAULT 'system',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reports_type ON ubec_reports(report_type);
CREATE INDEX idx_reports_token ON ubec_reports(token_type);
CREATE INDEX idx_reports_element ON ubec_reports(element);
CREATE INDEX idx_reports_public ON ubec_reports(is_public);
CREATE INDEX idx_reports_created ON ubec_reports(created_at DESC);

COMMENT ON TABLE ubec_reports IS 'Generated reports and analytics';

-- Key Performance Indicators
CREATE TABLE ubec_kpis (
    id BIGSERIAL PRIMARY KEY,
    kpi_name VARCHAR(100) NOT NULL,
    token_type token_code,
    element element_type,
    kpi_value NUMERIC(20, 7) NOT NULL,
    target_value NUMERIC(20, 7),
    unit VARCHAR(20),
    trend VARCHAR(20),
    is_healthy BOOLEAN DEFAULT TRUE,
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_kpis_name ON ubec_kpis(kpi_name);
CREATE INDEX idx_kpis_token ON ubec_kpis(token_type);
CREATE INDEX idx_kpis_element ON ubec_kpis(element);
CREATE INDEX idx_kpis_healthy ON ubec_kpis(is_healthy);
CREATE INDEX idx_kpis_calculated ON ubec_kpis(calculated_at DESC);

COMMENT ON TABLE ubec_kpis IS 'Key performance indicators tracking';

-- ============================================================================
-- STEP 11: ELEMENT SUMMARY VIEWS
-- ============================================================================

-- Air (UBEC) - Gateway View
CREATE VIEW air_gateway_summary AS
SELECT 
    'UBEC' AS token,
    'air' AS element,
    COUNT(DISTINCT sa.account_id) AS total_gateways,
    COUNT(DISTINCT CASE WHEN agm.is_active_gateway THEN sa.account_id END) AS active_gateways,
    COUNT(DISTINCT CASE WHEN sa.created_at > NOW() - INTERVAL '24 hours' THEN sa.account_id END) AS new_gateways_24h,
    SUM(ub.balance) AS total_supply,
    AVG(agm.diversity_contribution) AS avg_diversity_score,
    AVG(agm.gateway_score) AS avg_gateway_score
FROM stellar_accounts sa
LEFT JOIN ubec_balances ub ON sa.account_id = ub.account_id AND ub.token_type = 'UBEC'
LEFT JOIN air_gateway_metrics agm ON sa.account_id = agm.account_id
WHERE sa.token_type = 'UBEC' OR ub.token_type = 'UBEC';

COMMENT ON VIEW air_gateway_summary IS 'Air element gateway metrics summary';

-- Water (UBECrc) - Flow View
CREATE VIEW water_flow_summary AS
SELECT 
    'UBECrc' AS token,
    'water' AS element,
    COUNT(DISTINCT st.id) AS transaction_count,
    SUM(so.amount) AS total_flow_volume,
    COUNT(DISTINCT CASE WHEN st.created_at > NOW() - INTERVAL '24 hours' THEN st.id END) AS transactions_24h,
    AVG(wfm.reciprocity_score) AS avg_reciprocity_score,
    COUNT(DISTINCT CASE WHEN wfm.is_balanced_flow THEN wfm.id END)::FLOAT / 
        NULLIF(COUNT(DISTINCT wfm.id), 0) AS balanced_flow_ratio
FROM stellar_transactions st
LEFT JOIN stellar_operations so ON st.id = so.transaction_id
LEFT JOIN water_flow_metrics wfm ON st.source_account = wfm.from_account
WHERE st.token_type = 'UBECrc';

COMMENT ON VIEW water_flow_summary IS 'Water element flow metrics summary';

-- Earth (UBECgpi) - Stability View
CREATE VIEW earth_stability_summary AS
SELECT 
    'UBECgpi' AS token,
    'earth' AS element,
    COUNT(DISTINCT sa.account_id) AS total_holders,
    SUM(ub.balance) AS total_supply,
    AVG(esm.stability_score) AS avg_stability_score,
    AVG(esm.mutualism_score) AS avg_mutualism_score,
    AVG(esm.balance_volatility) AS avg_volatility,
    COUNT(DISTINCT CASE WHEN esm.is_stable_holder THEN sa.account_id END)::FLOAT /
        NULLIF(COUNT(DISTINCT sa.account_id), 0) AS stable_holder_ratio
FROM stellar_accounts sa
LEFT JOIN ubec_balances ub ON sa.account_id = ub.account_id AND ub.token_type = 'UBECgpi'
LEFT JOIN earth_stability_metrics esm ON sa.account_id = esm.account_id
WHERE sa.token_type = 'UBECgpi' OR ub.token_type = 'UBECgpi';

COMMENT ON VIEW earth_stability_summary IS 'Earth element stability metrics summary';

-- Fire (UBECtt) - Transformation View
CREATE VIEW fire_transformation_summary AS
SELECT 
    'UBECtt' AS token,
    'fire' AS element,
    COUNT(DISTINCT ftm.id) AS total_transformations,
    COUNT(DISTINCT CASE WHEN ftm.transformation_date > NOW() - INTERVAL '24 hours' THEN ftm.id END) AS transformations_24h,
    AVG(ftm.impact_score) AS avg_impact_score,
    AVG(ftm.regeneration_score) AS avg_regeneration_score,
    AVG(ftm.catalyst_effectiveness) AS avg_catalyst_effectiveness,
    COUNT(DISTINCT CASE WHEN ftm.is_validated THEN ftm.id END)::FLOAT /
        NULLIF(COUNT(DISTINCT ftm.id), 0) AS validation_rate
FROM fire_transformation_metrics ftm;

COMMENT ON VIEW fire_transformation_summary IS 'Fire element transformation metrics summary';

-- Distribution Compliance View
CREATE VIEW distribution_compliance_summary AS
SELECT 
    token_type,
    element,
    MAX(CASE WHEN category = 'general_circulation' THEN percentage END) AS general_pct,
    MAX(CASE WHEN category = 'stewardship' THEN percentage END) AS stewardship_pct,
    MAX(CASE WHEN category = 'administration' THEN percentage END) AS administration_pct,
    MAX(CASE WHEN category = 'general_circulation' THEN deviation END) AS general_deviation,
    MAX(CASE WHEN category = 'stewardship' THEN deviation END) AS stewardship_deviation,
    MAX(CASE WHEN category = 'administration' THEN deviation END) AS administration_deviation,
    BOOL_AND(is_compliant) AS all_compliant,
    MAX(snapshot_date) AS last_snapshot
FROM ubec_distributions
WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM ubec_distributions ud2 WHERE ud2.token_type = ubec_distributions.token_type)
GROUP BY token_type, element;

COMMENT ON VIEW distribution_compliance_summary IS 'Current distribution compliance status for all tokens';

-- System Health View
CREATE VIEW system_health_summary AS
SELECT 
    component,
    token_type,
    element,
    status,
    last_check,
    error_count,
    warning_count,
    CASE 
        WHEN status = 'excellent' THEN 5
        WHEN status = 'good' THEN 4
        WHEN status = 'fair' THEN 3
        WHEN status = 'poor' THEN 2
        ELSE 1
    END AS status_score
FROM ubec_system_health
WHERE last_check = (
    SELECT MAX(last_check) 
    FROM ubec_system_health ush2 
    WHERE ush2.component = ubec_system_health.component 
    AND ush2.token_type = ubec_system_health.token_type
);

COMMENT ON VIEW system_health_summary IS 'Current system health status across all components';

-- ============================================================================
-- STEP 12: FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function: Update timestamp on row update
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update_updated_at trigger to relevant tables
CREATE TRIGGER update_stellar_accounts_updated_at BEFORE UPDATE ON stellar_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ubec_balances_updated_at BEFORE UPDATE ON ubec_balances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_air_gateway_updated_at BEFORE UPDATE ON air_gateway_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_water_flow_updated_at BEFORE UPDATE ON water_flow_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_earth_stability_updated_at BEFORE UPDATE ON earth_stability_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sync_status_updated_at BEFORE UPDATE ON ubec_sync_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function: Calculate distribution compliance
CREATE OR REPLACE FUNCTION check_distribution_compliance(
    p_token_type token_code
) RETURNS BOOLEAN AS $$
DECLARE
    v_compliant BOOLEAN;
    v_max_deviation NUMERIC;
BEGIN
    SELECT 
        MAX(ABS(deviation)) <= 5.0 -- Allow 5% deviation
    INTO v_max_deviation
    FROM ubec_distributions
    WHERE token_type = p_token_type
    AND snapshot_date = (SELECT MAX(snapshot_date) FROM ubec_distributions WHERE token_type = p_token_type);
    
    RETURN COALESCE(v_max_deviation, FALSE);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_distribution_compliance IS 'Check if token distribution is compliant with rules';

-- Function: Calculate holonic health score
CREATE OR REPLACE FUNCTION calculate_holonic_health_score(
    p_token_type token_code DEFAULT NULL
) RETURNS TABLE (
    token token_code,
    element element_type,
    overall_score NUMERIC,
    status health_status
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        uhm.token_type,
        uhm.element,
        AVG(uhm.score) AS overall_score,
        CASE 
            WHEN AVG(uhm.score) >= 0.8 THEN 'excellent'::health_status
            WHEN AVG(uhm.score) >= 0.6 THEN 'good'::health_status
            WHEN AVG(uhm.score) >= 0.4 THEN 'fair'::health_status
            WHEN AVG(uhm.score) >= 0.2 THEN 'poor'::health_status
            ELSE 'critical'::health_status
        END AS status
    FROM ubec_holonic_metrics uhm
    WHERE (p_token_type IS NULL OR uhm.token_type = p_token_type)
    AND uhm.calculated_at > NOW() - INTERVAL '7 days'
    GROUP BY uhm.token_type, uhm.element;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_holonic_health_score IS 'Calculate overall holonic health for tokens';

-- ============================================================================
-- STEP 13: INITIAL DATA SETUP
-- ============================================================================

-- Initialize sync status for all tokens
INSERT INTO ubec_sync_status (token_type, element, sync_status) VALUES
    ('UBEC', 'air', 'idle'),
    ('UBECrc', 'water', 'idle'),
    ('UBECgpi', 'earth', 'idle'),
    ('UBECtt', 'fire', 'idle');

-- Initialize distribution targets
INSERT INTO ubec_distributions (token_type, element, category, target_percentage, snapshot_date) VALUES
    -- UBEC (Air) - Standard distribution
    ('UBEC', 'air', 'general_circulation', 75.0, NOW()),
    ('UBEC', 'air', 'stewardship', 20.0, NOW()),
    ('UBEC', 'air', 'administration', 5.0, NOW()),
    -- UBECrc (Water) - More flow through stewardship
    ('UBECrc', 'water', 'general_circulation', 70.0, NOW()),
    ('UBECrc', 'water', 'stewardship', 25.0, NOW()),
    ('UBECrc', 'water', 'administration', 5.0, NOW()),
    -- UBECgpi (Earth) - More stable in general
    ('UBECgpi', 'earth', 'general_circulation', 80.0, NOW()),
    ('UBECgpi', 'earth', 'stewardship', 15.0, NOW()),
    ('UBECgpi', 'earth', 'administration', 5.0, NOW()),
    -- UBECtt (Fire) - More administrative control
    ('UBECtt', 'fire', 'general_circulation', 65.0, NOW()),
    ('UBECtt', 'fire', 'stewardship', 25.0, NOW()),
    ('UBECtt', 'fire', 'administration', 10.0, NOW());

-- ============================================================================
-- STEP 14: GRANTS AND PERMISSIONS
-- ============================================================================

-- Create application role (adjust as needed)
-- CREATE ROLE ubec_app WITH LOGIN PASSWORD 'your_secure_password';
-- GRANT USAGE ON SCHEMA ubec_main TO ubec_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ubec_main TO ubec_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ubec_main TO ubec_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ubec_main TO ubec_app;

-- Create read-only role for reporting
-- CREATE ROLE ubec_readonly WITH LOGIN PASSWORD 'your_secure_password';
-- GRANT USAGE ON SCHEMA ubec_main TO ubec_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA ubec_main TO ubec_readonly;

-- ============================================================================
-- STEP 15: COMPLETION AND VERIFICATION
-- ============================================================================

-- Create a verification function
CREATE OR REPLACE FUNCTION verify_database_setup()
RETURNS TABLE (
    check_name TEXT,
    status TEXT,
    details TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'Schema Created'::TEXT,
        CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        'Schema ubec_main exists'::TEXT
    FROM information_schema.schemata 
    WHERE schema_name = 'ubec_main'
    
    UNION ALL
    
    SELECT 
        'Core Tables'::TEXT,
        CASE WHEN COUNT(*) >= 25 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        COUNT(*)::TEXT || ' tables created'::TEXT
    FROM information_schema.tables 
    WHERE table_schema = 'ubec_main' AND table_type = 'BASE TABLE'
    
    UNION ALL
    
    SELECT 
        'Views Created'::TEXT,
        CASE WHEN COUNT(*) >= 5 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        COUNT(*)::TEXT || ' views created'::TEXT
    FROM information_schema.views 
    WHERE table_schema = 'ubec_main'
    
    UNION ALL
    
    SELECT 
        'Custom Types'::TEXT,
        CASE WHEN COUNT(*) >= 6 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        COUNT(*)::TEXT || ' types created'::TEXT
    FROM pg_type 
    WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'ubec_main')
    
    UNION ALL
    
    SELECT 
        'Indexes Created'::TEXT,
        CASE WHEN COUNT(*) >= 50 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        COUNT(*)::TEXT || ' indexes created'::TEXT
    FROM pg_indexes 
    WHERE schemaname = 'ubec_main'
    
    UNION ALL
    
    SELECT 
        'Functions Created'::TEXT,
        CASE WHEN COUNT(*) >= 3 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        COUNT(*)::TEXT || ' functions created'::TEXT
    FROM pg_proc 
    WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'ubec_main');
END;
$$ LANGUAGE plpgsql;

-- Run verification
SELECT * FROM verify_database_setup();

-- Display summary
SELECT 
    'UBEC Database Setup Complete' AS message,
    NOW() AS completed_at,
    current_database() AS database_name,
    current_schema() AS schema_name,
    current_user AS installed_by;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================

/*
USAGE INSTRUCTIONS:

1. CREATE DATABASE (as superuser):
   psql -U postgres -c "CREATE DATABASE ubec;"

2. RUN THIS SCRIPT:
   psql -U postgres -d ubec -f ubec_database_setup.sql

3. VERIFY SETUP:
   psql -U postgres -d ubec -c "SELECT * FROM ubec_main.verify_database_setup();"

4. SET DEFAULT SCHEMA (in your connection):
   SET search_path TO ubec_main, public;

The database is now ready for the UBEC Protocol Suite integration!
*/
