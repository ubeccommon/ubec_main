-- ============================================================================
-- PHENOMENOLOGICAL STELLAR BLOCKCHAIN DATA MODEL
-- ============================================================================
-- 
-- This schema models Stellar blockchain assets using phenomenological
-- principles that emphasize contextual and relational ontology.
--
-- Design Philosophy:
-- 1. INTENTIONALITY: Every entity is defined by its directedness toward others
-- 2. HORIZONS: Internal (intrinsic properties) + External (contextual relations)
-- 3. TEMPORALITY: Retention (history), Present (now), Protention (anticipated)
-- 4. SPATIALITY: Network topology as geometric relationships
-- 5. COMPORTMENT: Embodied patterns of engagement and use
--
-- Attribution:
--   This project uses the services of Claude and Anthropic PBC to inform our
--   decisions and recommendations. This project was made possible with the
--   assistance of Claude and Anthropic PBC.
--
-- Version: 1.0.0
-- Date: October 12, 2025
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search

-- Create schema
CREATE SCHEMA IF NOT EXISTS phenomenal CASCADE;

SET search_path TO phenomenal, public;

-- ============================================================================
-- PART 1: CUSTOM TYPES
-- ============================================================================

-- Phenomenological modes of givenness
CREATE TYPE phenomenal_mode AS ENUM (
    'fully_present',        -- Directly experienced in primal impression
    'retained',             -- Given through retention (past)
    'protended',           -- Anticipated through protention (future)
    'co_present',          -- Given in external horizon
    'implicitly_meant'     -- Referred to but not given
);

-- Asset existence modes (following Heidegger's ontological difference)
CREATE TYPE existence_mode AS ENUM (
    'ready_to_hand',       -- Practical, engaged use (Zuhandenheit)
    'present_at_hand',     -- Theoretical, observed (Vorhandenheit)
    'unready_to_hand',     -- Broken, problematic, noticed
    'absent'               -- Referenced but not available
);

-- Relationship intentionality types
CREATE TYPE intentional_relation AS ENUM (
    'trustline',           -- Directedness as trust
    'payment',             -- Directedness as transfer
    'offer',               -- Directedness as exchange
    'sponsorship',         -- Directedness as support
    'authorization',       -- Directedness as permission
    'claimable',          -- Directedness as potential
    'liquidity_pool'      -- Directedness as shared resource
);

-- Ubuntu principle mapping (from UBEC project)
CREATE TYPE ubuntu_principle AS ENUM (
    'diversity',           -- Air: Universal access and variety
    'reciprocity',         -- Water: Flow and exchange
    'mutualism',           -- Earth: Stability through relationship
    'regeneration'         -- Fire: Transformation and renewal
);

-- Holonic categories (nested wholes)
CREATE TYPE holonic_category AS ENUM (
    'holon',              -- Both whole and part
    'autonomous_unit',    -- Acts independently
    'collective',         -- Emergent whole from parts
    'network_node',       -- Defined by connections
    'isolate'            -- Minimal connections
);

-- Temporal horizons
CREATE TYPE temporal_horizon AS ENUM (
    'immediate',          -- Within seconds
    'proximal',           -- Within hours
    'intermediate',       -- Within days
    'distant',            -- Within weeks
    'extended'            -- Beyond weeks
);

-- ============================================================================
-- PART 2: CORE PHENOMENOLOGICAL ENTITIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Assets as Phenomena (Things as they appear)
-- ----------------------------------------------------------------------------
CREATE TABLE assets (
    -- Identity
    id SERIAL PRIMARY KEY,
    asset_code VARCHAR(12) NOT NULL,
    issuer_address VARCHAR(56) NOT NULL,
    
    -- Phenomenological properties
    phenomenal_mode phenomenal_mode NOT NULL DEFAULT 'fully_present',
    existence_mode existence_mode NOT NULL DEFAULT 'present_at_hand',
    ubuntu_principle ubuntu_principle,
    
    -- Internal Horizon (intrinsic properties as given)
    internal_horizon JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "supply": {"total": float, "circulating": float},
    --   "properties": {"flags": [], "metadata": {}},
    --   "essence": {"immutable_attributes": {}}
    -- }
    
    -- External Horizon (contextual embeddedness)
    external_horizon JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "network_context": {"stellar_network": "mainnet|testnet"},
    --   "market_context": {"price_references": []},
    --   "social_context": {"community_size": int}
    -- }
    
    -- Temporal Consciousness
    genesis_at TIMESTAMP WITH TIME ZONE NOT NULL,
    retained_history JSONB,  -- Past states (retention)
    present_state JSONB NOT NULL,
    protended_futures JSONB,  -- Anticipated states (protention)
    temporal_horizon temporal_horizon NOT NULL DEFAULT 'intermediate',
    
    -- Spatial embedding (network position)
    network_position GEOMETRY(POINT, 4326),  -- Derived from graph embedding
    topology_metadata JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(asset_code, issuer_address)
);

CREATE INDEX idx_assets_phenomenal ON assets(phenomenal_mode, existence_mode);
CREATE INDEX idx_assets_ubuntu ON assets(ubuntu_principle);
CREATE INDEX idx_assets_temporal ON assets(genesis_at, temporal_horizon);
CREATE INDEX idx_assets_spatial ON assets USING GIST(network_position);
CREATE INDEX idx_assets_internal_horizon ON assets USING GIN(internal_horizon);
CREATE INDEX idx_assets_external_horizon ON assets USING GIN(external_horizon);

COMMENT ON TABLE assets IS 'Assets as phenomena: things as they appear in the blockchain, with internal/external horizons';
COMMENT ON COLUMN assets.phenomenal_mode IS 'How the asset is given to consciousness/observers';
COMMENT ON COLUMN assets.existence_mode IS 'Heidegger: how the asset manifests in practical vs theoretical engagement';
COMMENT ON COLUMN assets.internal_horizon IS 'Intrinsic properties and essence of the asset itself';
COMMENT ON COLUMN assets.external_horizon IS 'Contextual embedding and co-present background';

-- ----------------------------------------------------------------------------
-- Accounts as Dasein (Being-there, situated consciousness)
-- ----------------------------------------------------------------------------
CREATE TABLE accounts (
    -- Identity
    id SERIAL PRIMARY KEY,
    account_address VARCHAR(56) NOT NULL UNIQUE,
    
    -- Phenomenological being
    dasein_type VARCHAR(50) NOT NULL DEFAULT 'participant',  -- being-in-the-world type
    comportment_pattern VARCHAR(50),  -- How they engage (trader, holder, issuer, etc)
    holonic_category holonic_category NOT NULL DEFAULT 'network_node',
    
    -- Temporal thrownness (Geworfenheit - being thrown into situation)
    thrown_at TIMESTAMP WITH TIME ZONE NOT NULL,  -- Account creation
    facticity JSONB,  -- Given circumstances and constraints
    
    -- Spatial situation
    network_position GEOMETRY(POINT, 4326),
    spatial_context JSONB,
    
    -- Intentional directedness (what this account is "toward")
    primary_intentions intentional_relation[],
    intention_strength JSONB,  -- How strongly directed toward different relations
    
    -- Horizons of experience
    internal_horizon JSONB NOT NULL DEFAULT '{}'::jsonb,
    external_horizon JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Ubuntu assessment
    ubuntu_scores JSONB,  -- Scores on each principle
    
    -- Temporal
    retained_states JSONB,  -- Historical snapshots
    present_state JSONB NOT NULL,
    anticipated_states JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_accounts_comportment ON accounts(comportment_pattern);
CREATE INDEX idx_accounts_holonic ON accounts(holonic_category);
CREATE INDEX idx_accounts_spatial ON accounts USING GIST(network_position);
CREATE INDEX idx_accounts_intentions ON accounts USING GIN(primary_intentions);
CREATE INDEX idx_accounts_internal ON accounts USING GIN(internal_horizon);

COMMENT ON TABLE accounts IS 'Accounts as Dasein: beings situated in the blockchain world with intentional directedness';
COMMENT ON COLUMN accounts.dasein_type IS 'Type of being-in-the-world (issuer, trader, holder, etc)';
COMMENT ON COLUMN accounts.comportment_pattern IS 'Practical engagement pattern (Heideggerian comportment)';
COMMENT ON COLUMN accounts.facticity IS 'Given circumstances: limitations, initial conditions, constraints';

-- ----------------------------------------------------------------------------
-- Intentional Relations (Directedness between entities)
-- ----------------------------------------------------------------------------
CREATE TABLE intentional_relations (
    -- Identity
    id BIGSERIAL PRIMARY KEY,
    
    -- Intentional structure (subject directed toward object)
    from_account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    to_account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    
    -- Type of intentionality
    relation_type intentional_relation NOT NULL,
    
    -- Phenomenal givenness
    phenomenal_mode phenomenal_mode NOT NULL DEFAULT 'fully_present',
    
    -- Intentional content (noema - what is meant)
    noema JSONB NOT NULL,  -- The object as intended
    -- Structure: {
    --   "intended_object": {},
    --   "mode_of_presentation": "",
    --   "meaning": {}
    -- }
    
    -- Intentional act (noesis - how it is intended)
    noesis JSONB NOT NULL,  -- The intending act
    -- Structure: {
    --   "act_type": "trustline|payment|offer",
    --   "act_quality": "belief|desire|perception",
    --   "fulfillment_status": "empty|partially_fulfilled|fulfilled"
    -- }
    
    -- Strength and characteristics
    relation_strength DECIMAL(10, 6) NOT NULL DEFAULT 0.5,
    reciprocity_factor DECIMAL(10, 6),  -- Mutuality measure
    stability_score DECIMAL(10, 6),
    
    -- Spatial representation (geometric relation)
    relation_line GEOMETRY(LINESTRING, 4326),
    geodesic_distance DECIMAL(20, 10),  -- Network distance
    euclidean_distance DECIMAL(20, 10),  -- Embedding space distance
    
    -- Temporal dimension
    emerged_at TIMESTAMP WITH TIME ZONE NOT NULL,
    retained_history JSONB,
    present_manifestation JSONB NOT NULL,
    protended_evolution JSONB,
    temporal_horizon temporal_horizon NOT NULL DEFAULT 'proximal',
    
    -- Active/dormant
    active BOOLEAN NOT NULL DEFAULT TRUE,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_relation_structure CHECK (
        (to_account_id IS NOT NULL AND asset_id IS NULL) OR
        (to_account_id IS NULL AND asset_id IS NOT NULL) OR
        (to_account_id IS NOT NULL AND asset_id IS NOT NULL)
    )
);

CREATE INDEX idx_relations_from ON intentional_relations(from_account_id, relation_type);
CREATE INDEX idx_relations_to ON intentional_relations(to_account_id, relation_type);
CREATE INDEX idx_relations_asset ON intentional_relations(asset_id, relation_type);
CREATE INDEX idx_relations_type ON intentional_relations(relation_type, active);
CREATE INDEX idx_relations_temporal ON intentional_relations(emerged_at, temporal_horizon);
CREATE INDEX idx_relations_spatial ON intentional_relations USING GIST(relation_line);
CREATE INDEX idx_relations_noema ON intentional_relations USING GIN(noema);
CREATE INDEX idx_relations_strength ON intentional_relations(relation_strength) WHERE active = TRUE;

COMMENT ON TABLE intentional_relations IS 'Intentional directedness: how accounts are related to assets and each other';
COMMENT ON COLUMN intentional_relations.noema IS 'The intentional object: what is meant or directed toward';
COMMENT ON COLUMN intentional_relations.noesis IS 'The intentional act: the manner of meaning or directing';
COMMENT ON COLUMN intentional_relations.relation_line IS 'Geometric representation of relationship in network space';

-- ============================================================================
-- PART 3: TEMPORAL PHENOMENOLOGY
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Retentions (Past as retained in present consciousness)
-- ----------------------------------------------------------------------------
CREATE TABLE retentions (
    id BIGSERIAL PRIMARY KEY,
    
    -- What is retained
    entity_type VARCHAR(50) NOT NULL,  -- 'asset', 'account', 'relation'
    entity_id INTEGER NOT NULL,
    
    -- Temporal structure
    original_present TIMESTAMP WITH TIME ZONE NOT NULL,  -- When it was present
    retained_at TIMESTAMP WITH TIME ZONE NOT NULL,        -- Current moment retaining it
    temporal_distance INTERVAL NOT NULL,                  -- How far back
    
    -- Content retained (may fade or transform)
    retained_content JSONB NOT NULL,
    retention_clarity DECIMAL(5, 4) NOT NULL DEFAULT 1.0,  -- How clearly retained (0-1)
    retention_type VARCHAR(50) NOT NULL,  -- 'primary', 'secondary', 'tertiary'
    
    -- Modifications through retention
    transformations JSONB,  -- How memory has changed
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_retentions_entity ON retentions(entity_type, entity_id);
CREATE INDEX idx_retentions_temporal ON retentions(original_present, retained_at);
CREATE INDEX idx_retentions_distance ON retentions(temporal_distance);
CREATE INDEX idx_retentions_clarity ON retentions(retention_clarity) WHERE retention_clarity > 0.5;

COMMENT ON TABLE retentions IS 'Past states retained in present consciousness (Husserlian retention)';
COMMENT ON COLUMN retentions.retention_clarity IS 'Fidelity of retained memory (0=forgotten, 1=clear)';

-- ----------------------------------------------------------------------------
-- Protentions (Future as anticipated in present consciousness)
-- ----------------------------------------------------------------------------
CREATE TABLE protentions (
    id BIGSERIAL PRIMARY KEY,
    
    -- What is anticipated
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    
    -- Temporal structure
    protended_from TIMESTAMP WITH TIME ZONE NOT NULL,     -- Present moment anticipating
    expected_at TIMESTAMP WITH TIME ZONE NOT NULL,        -- When expected to manifest
    temporal_distance INTERVAL NOT NULL,
    
    -- Anticipated content
    protended_content JSONB NOT NULL,
    expectation_confidence DECIMAL(5, 4) NOT NULL DEFAULT 0.5,  -- How certain (0-1)
    protention_type VARCHAR(50) NOT NULL,  -- 'immediate', 'near', 'distant'
    
    -- Fulfillment tracking
    fulfilled BOOLEAN,
    fulfilled_at TIMESTAMP WITH TIME ZONE,
    fulfillment_degree DECIMAL(5, 4),  -- How closely reality matched expectation
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_protentions_entity ON protentions(entity_type, entity_id);
CREATE INDEX idx_protentions_temporal ON protentions(protended_from, expected_at);
CREATE INDEX idx_protentions_confidence ON protentions(expectation_confidence);
CREATE INDEX idx_protentions_fulfilled ON protentions(fulfilled, fulfillment_degree);

COMMENT ON TABLE protentions IS 'Future states anticipated in present consciousness (Husserlian protention)';
COMMENT ON COLUMN protentions.fulfillment_degree IS 'How well the anticipation matched reality (0-1)';

-- ============================================================================
-- PART 4: SPATIAL PHENOMENOLOGY (Network Topology)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Network Embeddings (Geometric representation of blockchain topology)
-- ----------------------------------------------------------------------------
CREATE TABLE network_embeddings (
    id BIGSERIAL PRIMARY KEY,
    
    -- When this embedding was computed
    computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    embedding_method VARCHAR(100) NOT NULL,  -- 'node2vec', 'graph_sage', 'spectral', etc
    
    -- Dimensionality
    dimensions INTEGER NOT NULL DEFAULT 2,
    
    -- Metadata about the embedding
    parameters JSONB NOT NULL,
    quality_metrics JSONB,  -- Stress, distortion, etc.
    
    -- Validity period
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_embeddings_temporal ON network_embeddings(valid_from, valid_until);

-- ----------------------------------------------------------------------------
-- Spatial Positions (Account/Asset positions in embedding space)
-- ----------------------------------------------------------------------------
CREATE TABLE spatial_positions (
    id BIGSERIAL PRIMARY KEY,
    
    embedding_id INTEGER NOT NULL REFERENCES network_embeddings(id) ON DELETE CASCADE,
    
    -- What is positioned
    entity_type VARCHAR(50) NOT NULL,  -- 'account' or 'asset'
    entity_id INTEGER NOT NULL,
    
    -- Position in embedding space
    position GEOMETRY(POINT, 4326) NOT NULL,
    coordinates DECIMAL(20, 10)[],  -- For higher dimensions
    
    -- Spatial context
    local_density DECIMAL(20, 10),
    centrality_scores JSONB,  -- Various centrality measures
    cluster_membership INTEGER[],
    
    -- Neighborhoods (spatial horizons)
    immediate_neighbors INTEGER[],
    proximal_region GEOMETRY(POLYGON, 4326),
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_spatial_positions_entity ON spatial_positions(entity_type, entity_id);
CREATE INDEX idx_spatial_positions_embedding ON spatial_positions(embedding_id);
CREATE INDEX idx_spatial_positions_geom ON spatial_positions USING GIST(position);
CREATE INDEX idx_spatial_positions_region ON spatial_positions USING GIST(proximal_region);

COMMENT ON TABLE spatial_positions IS 'Spatial positions of entities in network embedding space';
COMMENT ON COLUMN spatial_positions.proximal_region IS 'Spatial horizon: nearby region in network space';

-- ----------------------------------------------------------------------------
-- Geodesics (Shortest paths through network)
-- ----------------------------------------------------------------------------
CREATE TABLE geodesics (
    id BIGSERIAL PRIMARY KEY,
    
    from_account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    to_account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    
    -- Path structure
    path_length INTEGER NOT NULL,
    path_nodes INTEGER[] NOT NULL,
    path_edges BIGINT[] NOT NULL,  -- intentional_relations IDs
    
    -- Geometry
    path_line GEOMETRY(LINESTRING, 4326),
    
    -- Weights and costs
    weighted_distance DECIMAL(20, 10),
    
    -- When computed
    computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(from_account_id, to_account_id)
);

CREATE INDEX idx_geodesics_from ON geodesics(from_account_id);
CREATE INDEX idx_geodesics_to ON geodesics(to_account_id);
CREATE INDEX idx_geodesics_length ON geodesics(path_length);
CREATE INDEX idx_geodesics_geom ON geodesics USING GIST(path_line);

COMMENT ON TABLE geodesics IS 'Shortest paths (geodesics) through the network topology';

-- ============================================================================
-- PART 5: TRANSACTION EVENTS (Atomic Phenomena)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Transactions (Discrete events in blockchain spacetime)
-- ----------------------------------------------------------------------------
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    
    -- Stellar identity
    transaction_hash VARCHAR(64) NOT NULL UNIQUE,
    ledger_sequence BIGINT NOT NULL,
    
    -- Phenomenological event structure
    event_type VARCHAR(50) NOT NULL,
    source_account_id INTEGER REFERENCES accounts(id),
    
    -- Temporal structure
    ledger_closed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    temporal_context JSONB,  -- Where in the "stream" of transactions
    
    -- Intentional content
    operations JSONB NOT NULL,  -- Array of operations
    operations_count INTEGER NOT NULL,
    
    -- Effects (what changed)
    effects JSONB,
    
    -- Success/failure
    successful BOOLEAN NOT NULL,
    result_code VARCHAR(100),
    
    -- Spatial context (where in network)
    affected_positions GEOMETRY(MULTIPOINT, 4326),
    network_impact JSONB,
    
    -- Fee and resources
    fee_charged BIGINT NOT NULL,
    resource_fee BIGINT,
    
    -- Memos (additional meaning)
    memo_type VARCHAR(20),
    memo_value TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_hash ON transactions(transaction_hash);
CREATE INDEX idx_transactions_ledger ON transactions(ledger_sequence, ledger_closed_at);
CREATE INDEX idx_transactions_source ON transactions(source_account_id);
CREATE INDEX idx_transactions_temporal ON transactions(ledger_closed_at);
CREATE INDEX idx_transactions_type ON transactions(event_type, successful);
CREATE INDEX idx_transactions_spatial ON transactions USING GIST(affected_positions);

COMMENT ON TABLE transactions IS 'Transaction events as discrete phenomena in blockchain spacetime';

-- ============================================================================
-- PART 6: HOLONIC STRUCTURE (Nested Wholes)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Holons (Entities that are simultaneously wholes and parts)
-- ----------------------------------------------------------------------------
CREATE TABLE holons (
    id BIGSERIAL PRIMARY KEY,
    
    -- What is this holon
    holon_name VARCHAR(255) NOT NULL,
    holon_type VARCHAR(100) NOT NULL,  -- 'account_cluster', 'asset_ecosystem', etc
    
    -- Holonic properties
    autonomy_score DECIMAL(5, 4) NOT NULL,  -- How independent (0-1)
    integration_score DECIMAL(5, 4) NOT NULL,  -- How integrated with larger whole (0-1)
    
    -- Parts (what constitutes this holon)
    constituent_accounts INTEGER[],
    constituent_assets INTEGER[],
    constituent_relations BIGINT[],
    
    -- Wholes (what holons this is part of)
    parent_holons INTEGER[],
    
    -- Emergent properties
    emergent_properties JSONB,
    collective_behavior JSONB,
    
    -- Spatial extent
    spatial_region GEOMETRY(POLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    
    -- Temporal
    emerged_at TIMESTAMP WITH TIME ZONE NOT NULL,
    stable_from TIMESTAMP WITH TIME ZONE,
    dissolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Ubuntu metrics
    ubuntu_scores JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_holons_type ON holons(holon_type);
CREATE INDEX idx_holons_autonomy ON holons(autonomy_score);
CREATE INDEX idx_holons_integration ON holons(integration_score);
CREATE INDEX idx_holons_spatial ON holons USING GIST(spatial_region);
CREATE INDEX idx_holons_centroid ON holons USING GIST(centroid);
CREATE INDEX idx_holons_temporal ON holons(emerged_at, dissolved_at);

COMMENT ON TABLE holons IS 'Holarchical structures: entities that are both autonomous wholes and integrated parts';
COMMENT ON COLUMN holons.autonomy_score IS 'Degree of self-sufficiency and independent agency';
COMMENT ON COLUMN holons.integration_score IS 'Degree of integration into larger wholes';

-- ============================================================================
-- PART 7: ANALYTICAL VIEWS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- View: Current Network State (Present phenomenal field)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW current_network_state AS
SELECT 
    a.id AS asset_id,
    a.asset_code,
    a.issuer_address,
    a.phenomenal_mode,
    a.existence_mode,
    a.ubuntu_principle,
    a.network_position,
    COUNT(DISTINCT ir.from_account_id) AS holder_count,
    SUM(CASE WHEN ir.active THEN 1 ELSE 0 END) AS active_relations,
    AVG(ir.relation_strength) AS avg_relation_strength,
    ST_Distance(
        a.network_position::geography,
        (SELECT ST_Centroid(ST_Collect(network_position)) FROM accounts)::geography
    ) AS distance_from_network_center
FROM assets a
LEFT JOIN intentional_relations ir ON a.id = ir.asset_id
GROUP BY a.id, a.asset_code, a.issuer_address, a.phenomenal_mode, 
         a.existence_mode, a.ubuntu_principle, a.network_position;

COMMENT ON VIEW current_network_state IS 'Present state of assets in their phenomenal field';

-- ----------------------------------------------------------------------------
-- View: Intentional Network (Graph of directedness)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW intentional_network AS
SELECT 
    ir.id AS relation_id,
    ir.relation_type,
    ir.from_account_id,
    ir.to_account_id,
    ir.asset_id,
    ir.relation_strength,
    ir.reciprocity_factor,
    a_from.account_address AS from_address,
    a_to.account_address AS to_address,
    ast.asset_code,
    ir.relation_line,
    ST_Length(ir.relation_line::geography) AS geographic_distance,
    ir.temporal_horizon
FROM intentional_relations ir
LEFT JOIN accounts a_from ON ir.from_account_id = a_from.id
LEFT JOIN accounts a_to ON ir.to_account_id = a_to.id
LEFT JOIN assets ast ON ir.asset_id = ast.id
WHERE ir.active = TRUE;

COMMENT ON VIEW intentional_network IS 'Current network of intentional relations (directedness)';

-- ----------------------------------------------------------------------------
-- View: Temporal Consciousness Stream
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW temporal_consciousness AS
SELECT 
    'retention' AS temporal_mode,
    entity_type,
    entity_id,
    original_present AS temporal_reference,
    retained_at AS consciousness_now,
    retention_clarity AS phenomenal_clarity,
    retained_content AS content
FROM retentions
WHERE retention_clarity > 0.3

UNION ALL

SELECT 
    'protention' AS temporal_mode,
    entity_type,
    entity_id,
    expected_at AS temporal_reference,
    protended_from AS consciousness_now,
    expectation_confidence AS phenomenal_clarity,
    protended_content AS content
FROM protentions
WHERE fulfilled IS NULL OR fulfilled = FALSE

ORDER BY consciousness_now DESC, temporal_mode;

COMMENT ON VIEW temporal_consciousness IS 'Stream of temporal consciousness (retentions and protentions)';

-- ============================================================================
-- PART 8: ANALYTICAL FUNCTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Function: Compute Network Centrality (Phenomenal Prominence)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION compute_phenomenal_prominence(
    p_entity_type VARCHAR,
    p_entity_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_degree_centrality DECIMAL(10, 6);
    v_betweenness DECIMAL(10, 6);
    v_closeness DECIMAL(10, 6);
    v_eigenvector DECIMAL(10, 6);
    v_result JSONB;
BEGIN
    -- Degree centrality: how many direct connections
    SELECT COUNT(DISTINCT CASE WHEN from_account_id = p_entity_id THEN to_account_id
                               WHEN to_account_id = p_entity_id THEN from_account_id END)::DECIMAL
           / (SELECT COUNT(*) FROM accounts)
    INTO v_degree_centrality
    FROM intentional_relations
    WHERE (from_account_id = p_entity_id OR to_account_id = p_entity_id)
      AND active = TRUE;
    
    -- Betweenness centrality: how often entity is on shortest paths
    -- (Simplified calculation)
    SELECT COUNT(*)::DECIMAL / (SELECT COUNT(*) FROM geodesics)
    INTO v_betweenness
    FROM geodesics
    WHERE p_entity_id = ANY(path_nodes);
    
    -- Closeness centrality: average distance to all others
    -- (Inverse of average geodesic distance)
    SELECT 1.0 / NULLIF(AVG(path_length), 0)
    INTO v_closeness
    FROM geodesics
    WHERE from_account_id = p_entity_id OR to_account_id = p_entity_id;
    
    -- Construct result
    v_result := jsonb_build_object(
        'degree_centrality', COALESCE(v_degree_centrality, 0),
        'betweenness_centrality', COALESCE(v_betweenness, 0),
        'closeness_centrality', COALESCE(v_closeness, 0),
        'computed_at', NOW()
    );
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION compute_phenomenal_prominence IS 'Compute centrality measures (phenomenal prominence in network)';

-- ----------------------------------------------------------------------------
-- Function: Compute Spatial Proximity (Phenomenal Nearness)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION compute_spatial_proximity(
    p_entity1_type VARCHAR,
    p_entity1_id INTEGER,
    p_entity2_type VARCHAR,
    p_entity2_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_pos1 GEOMETRY;
    v_pos2 GEOMETRY;
    v_distance DECIMAL(20, 10);
    v_result JSONB;
BEGIN
    -- Get positions
    SELECT position INTO v_pos1
    FROM spatial_positions
    WHERE entity_type = p_entity1_type AND entity_id = p_entity1_id
    ORDER BY created_at DESC LIMIT 1;
    
    SELECT position INTO v_pos2
    FROM spatial_positions
    WHERE entity_type = p_entity2_type AND entity_id = p_entity2_id
    ORDER BY created_at DESC LIMIT 1;
    
    -- Compute distance
    IF v_pos1 IS NOT NULL AND v_pos2 IS NOT NULL THEN
        v_distance := ST_Distance(v_pos1::geography, v_pos2::geography);
    ELSE
        v_distance := NULL;
    END IF;
    
    v_result := jsonb_build_object(
        'euclidean_distance', v_distance,
        'in_proximity', CASE WHEN v_distance < 1000 THEN TRUE ELSE FALSE END,
        'computed_at', NOW()
    );
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION compute_spatial_proximity IS 'Compute spatial proximity between entities in network space';

-- ----------------------------------------------------------------------------
-- Function: Analyze Ubuntu Principle Balance
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION analyze_ubuntu_balance(
    p_account_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_diversity_score DECIMAL(5, 4);
    v_reciprocity_score DECIMAL(5, 4);
    v_mutualism_score DECIMAL(5, 4);
    v_regeneration_score DECIMAL(5, 4);
    v_result JSONB;
BEGIN
    -- Diversity: variety of asset types held
    SELECT (COUNT(DISTINCT asset_id)::DECIMAL / 10.0)
    INTO v_diversity_score
    FROM intentional_relations
    WHERE from_account_id = p_account_id
      AND relation_type IN ('trustline', 'payment')
      AND active = TRUE;
    
    -- Reciprocity: balance of incoming/outgoing flows
    SELECT 1.0 - ABS(
        (SELECT COUNT(*) FROM intentional_relations WHERE from_account_id = p_account_id)::DECIMAL -
        (SELECT COUNT(*) FROM intentional_relations WHERE to_account_id = p_account_id)::DECIMAL
    ) / NULLIF(
        (SELECT COUNT(*) FROM intentional_relations WHERE from_account_id = p_account_id OR to_account_id = p_account_id),
        0
    )
    INTO v_reciprocity_score;
    
    -- Mutualism: strength of mutual relationships
    SELECT AVG(reciprocity_factor)
    INTO v_mutualism_score
    FROM intentional_relations
    WHERE (from_account_id = p_account_id OR to_account_id = p_account_id)
      AND reciprocity_factor IS NOT NULL
      AND active = TRUE;
    
    -- Regeneration: growth over time
    WITH temporal_growth AS (
        SELECT 
            COUNT(*) AS recent_count
        FROM intentional_relations
        WHERE from_account_id = p_account_id
          AND emerged_at > NOW() - INTERVAL '30 days'
    )
    SELECT (recent_count::DECIMAL / 100.0)
    INTO v_regeneration_score
    FROM temporal_growth;
    
    v_result := jsonb_build_object(
        'diversity', LEAST(COALESCE(v_diversity_score, 0), 1.0),
        'reciprocity', COALESCE(v_reciprocity_score, 0.5),
        'mutualism', COALESCE(v_mutualism_score, 0.5),
        'regeneration', LEAST(COALESCE(v_regeneration_score, 0), 1.0),
        'composite', (
            COALESCE(v_diversity_score, 0) * 0.25 +
            COALESCE(v_reciprocity_score, 0.5) * 0.25 +
            COALESCE(v_mutualism_score, 0.5) * 0.25 +
            LEAST(COALESCE(v_regeneration_score, 0), 1.0) * 0.25
        ),
        'analyzed_at', NOW()
    );
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION analyze_ubuntu_balance IS 'Analyze Ubuntu principle balance for an account';

-- ============================================================================
-- PART 9: TRIGGERS FOR MAINTAINING CONSISTENCY
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Trigger: Update spatial positions when embeddings change
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_spatial_positions_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Update account spatial position
    IF NEW.entity_type = 'account' THEN
        UPDATE accounts
        SET network_position = NEW.position,
            updated_at = NOW()
        WHERE id = NEW.entity_id;
    END IF;
    
    -- Update asset spatial position
    IF NEW.entity_type = 'asset' THEN
        UPDATE assets
        SET network_position = NEW.position,
            updated_at = NOW()
        WHERE id = NEW.entity_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_spatial_positions
    AFTER INSERT OR UPDATE ON spatial_positions
    FOR EACH ROW
    EXECUTE FUNCTION update_spatial_positions_trigger();

-- ----------------------------------------------------------------------------
-- Trigger: Maintain temporal consciousness (retentions)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION maintain_retentions_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- When an asset or account is updated, create retention of old state
    INSERT INTO retentions (
        entity_type,
        entity_id,
        original_present,
        retained_at,
        temporal_distance,
        retained_content,
        retention_clarity,
        retention_type
    ) VALUES (
        TG_TABLE_NAME,
        OLD.id,
        OLD.updated_at,
        NOW(),
        NOW() - OLD.updated_at,
        row_to_json(OLD)::jsonb,
        1.0,  -- Initially fully clear
        'primary'
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_maintain_asset_retentions
    AFTER UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION maintain_retentions_trigger();

CREATE TRIGGER trg_maintain_account_retentions
    AFTER UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION maintain_retentions_trigger();

-- ----------------------------------------------------------------------------
-- Trigger: Update updated_at timestamps
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_relations_updated_at
    BEFORE UPDATE ON intentional_relations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PART 10: SAMPLE DATA AND USAGE EXAMPLES
-- ============================================================================

-- Create sample asset (UBEC - Air)
INSERT INTO assets (
    asset_code,
    issuer_address,
    ubuntu_principle,
    phenomenal_mode,
    existence_mode,
    genesis_at,
    internal_horizon,
    external_horizon,
    present_state,
    network_position
) VALUES (
    'UBEC',
    'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'diversity',
    'fully_present',
    'ready_to_hand',
    NOW() - INTERVAL '1 year',
    '{"supply": {"total": 1000000, "circulating": 750000}, "properties": {"divisible": true}}'::jsonb,
    '{"network_context": {"stellar_network": "mainnet"}, "market_context": {}}'::jsonb,
    '{"active_holders": 1200, "daily_volume": 50000}'::jsonb,
    ST_SetSRID(ST_MakePoint(0, 0), 4326)
);

-- ============================================================================
-- GRANTS (Adjust as needed for your deployment)
-- ============================================================================

-- Grant usage on schema
-- GRANT USAGE ON SCHEMA phenomenal TO your_application_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA phenomenal TO your_application_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA phenomenal TO your_application_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA phenomenal TO your_application_user;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

COMMENT ON SCHEMA phenomenal IS 'Phenomenologically-informed blockchain data model integrating philosophy, physics, and Ubuntu principles';
