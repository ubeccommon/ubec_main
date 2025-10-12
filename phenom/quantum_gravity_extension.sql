-- ============================================================================
-- PHENOMENOLOGICAL QUANTUM GRAVITY EXTENSION
-- ============================================================================
-- 
-- This extension adds gravity and quantum gravity concepts to the 
-- phenomenological Stellar blockchain data model.
--
-- Theoretical Foundations:
-- 1. Network Gravity: Entities with "mass" (importance) create attractive/
--    repulsive forces in the network space
-- 2. Spacetime Curvature: Mass warps network topology - influence propagates
--    along geodesics in curved space
-- 3. Quantum Effects: Discreteness, uncertainty, entanglement between entities
-- 4. Phenomenological QG: Observable effects of quantum gravity at network scale
-- 5. Lorentz Violation: Directional preferences, symmetry breaking in network
--
-- Design Principle: "Precision in Implementation"
-- Every component is implementable, testable, and production-ready.
--
-- Attribution:
--   This project uses the services of Claude and Anthropic PBC to inform our
--   decisions and recommendations. This project was made possible with the
--   assistance of Claude and Anthropic PBC.
--
-- Version: 1.0.0
-- Date: October 12, 2025
-- ============================================================================

-- Ensure we're in the phenomenal schema
SET search_path TO phenomenal, public;

-- ============================================================================
-- PART 1: GRAVITATIONAL MASS - THE MEASURE OF IMPORTANCE
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Gravitational Mass: Measure of Network Importance and Influence
-- ----------------------------------------------------------------------------
-- In network gravity, "mass" represents importance, influence, or centrality.
-- High-mass entities attract more connections and have greater impact.
CREATE TABLE IF NOT EXISTS gravitational_mass (
    id BIGSERIAL PRIMARY KEY,
    
    -- What entity has mass
    entity_type VARCHAR(50) NOT NULL,  -- 'account', 'asset', 'holon'
    entity_id BIGINT NOT NULL,
    
    -- Mass components (analogous to physics)
    gravitational_mass DECIMAL(20, 10) NOT NULL, -- Attractive influence on others
    inertial_mass DECIMAL(20, 10) NOT NULL,      -- Resistance to change/stability
    
    -- Mass calculation methodology
    mass_basis JSONB NOT NULL,
    -- Structure: {
    --   "transaction_volume": float,      // Total value transacted
    --   "holder_count": int,              // Number of holders (for assets)
    --   "connection_count": int,          // Number of network connections
    --   "age_days": int,                  // Age/maturity factor
    --   "ubuntu_composite": float,        // Ubuntu principle alignment
    --   "activity_score": float,          // Recent activity level
    --   "trust_score": float              // Network trust/reputation
    -- }
    
    -- Temporal evolution
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    
    -- Mass history trajectory
    mass_trajectory JSONB,
    -- Structure: Array of {timestamp, value} showing mass evolution
    
    -- Constraints
    UNIQUE(entity_type, entity_id, calculated_at),
    CHECK (gravitational_mass >= 0),
    CHECK (inertial_mass >= 0)
);

CREATE INDEX idx_grav_mass_entity ON gravitational_mass(entity_type, entity_id);
CREATE INDEX idx_grav_mass_value ON gravitational_mass(gravitational_mass DESC);
CREATE INDEX idx_grav_mass_temporal ON gravitational_mass(calculated_at, valid_until);
CREATE INDEX idx_grav_mass_basis ON gravitational_mass USING GIN(mass_basis);

COMMENT ON TABLE gravitational_mass IS 
'Network gravity: measure of entity importance and influence';
COMMENT ON COLUMN gravitational_mass.gravitational_mass IS 
'Attractive influence - how strongly this entity pulls others toward it';
COMMENT ON COLUMN gravitational_mass.inertial_mass IS 
'Resistance to change - stability and persistence in the network';
COMMENT ON COLUMN gravitational_mass.mass_basis IS 
'Detailed breakdown of factors contributing to mass calculation';

-- ============================================================================
-- PART 2: GRAVITATIONAL FIELDS - ZONES OF INFLUENCE
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Gravitational Fields: Influence Zones Around Massive Entities
-- ----------------------------------------------------------------------------
-- Each massive entity creates a field that affects nearby entities.
-- Field strength decreases with distance (similar to inverse square law).
CREATE TABLE IF NOT EXISTS gravitational_fields (
    id BIGSERIAL PRIMARY KEY,
    
    -- Source of gravitational field
    source_mass_id BIGINT NOT NULL REFERENCES gravitational_mass(id) ON DELETE CASCADE,
    
    -- Field strength at various distances (measured in network hops or embedding distance)
    field_profile JSONB NOT NULL,
    -- Structure: {
    --   "0-1": float,      // Force at distance 0-1 (immediate neighbors)
    --   "1-2": float,      // Force at distance 1-2 hops
    --   "2-3": float,      // etc.
    --   "3-5": float,
    --   "5-10": float,
    --   "10+": float,
    --   "decay_rate": float  // How quickly field strength decreases
    -- }
    
    -- Spatial representation of field extent
    influence_radius DECIMAL(20, 10) NOT NULL,  -- Maximum effective radius
    field_geometry GEOMETRY(POLYGON, 4326),      -- Spatial extent in network embedding space
    
    -- Field characteristics
    field_type VARCHAR(50) NOT NULL,  -- 'attractive', 'repulsive', 'neutral', 'mixed'
    field_strength DECIMAL(20, 10) NOT NULL,  -- Overall strength at origin
    
    -- Field dynamics
    is_static BOOLEAN NOT NULL DEFAULT FALSE,  -- Does field change over time?
    temporal_variation JSONB,  -- How field varies with time
    
    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CHECK (influence_radius >= 0),
    CHECK (field_strength >= 0),
    CHECK (field_type IN ('attractive', 'repulsive', 'neutral', 'mixed'))
);

CREATE INDEX idx_grav_field_source ON gravitational_fields(source_mass_id);
CREATE INDEX idx_grav_field_spatial ON gravitational_fields USING GIST(field_geometry);
CREATE INDEX idx_grav_field_type ON gravitational_fields(field_type);
CREATE INDEX idx_grav_field_strength ON gravitational_fields(field_strength DESC);

COMMENT ON TABLE gravitational_fields IS 
'Gravitational fields: zones of influence surrounding massive entities';
COMMENT ON COLUMN gravitational_fields.influence_radius IS 
'Maximum distance at which field has measurable effect';

-- ============================================================================
-- PART 3: GRAVITATIONAL INTERACTIONS - FORCES BETWEEN ENTITIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Gravitational Interactions: Pairwise Forces Between Entities
-- ----------------------------------------------------------------------------
-- Captures the gravitational force between any two massive entities.
-- Analogous to F = G*m1*m2/r^2 but adapted for network context.
CREATE TABLE IF NOT EXISTS gravitational_interactions (
    id BIGSERIAL PRIMARY KEY,
    
    -- Interacting entities
    entity1_mass_id BIGINT NOT NULL REFERENCES gravitational_mass(id) ON DELETE CASCADE,
    entity2_mass_id BIGINT NOT NULL REFERENCES gravitational_mass(id) ON DELETE CASCADE,
    
    -- Force characteristics
    force_magnitude DECIMAL(20, 10) NOT NULL,  -- Strength of interaction
    force_direction DECIMAL(10, 6),  -- Direction in degrees (if applicable)
    force_vector GEOMETRY(LINESTRING, 4326),  -- Spatial representation of force
    
    -- Distance metrics
    separation_distance DECIMAL(20, 10) NOT NULL,  -- Distance in network space
    network_hops INTEGER,  -- Topological distance (shortest path length)
    
    -- Energy and potential
    potential_energy DECIMAL(20, 10),  -- Gravitational potential between entities
    binding_energy DECIMAL(20, 10),    -- Energy required to separate entities
    
    -- Interaction type
    interaction_type VARCHAR(50) NOT NULL,  -- 'attraction', 'repulsion', 'equilibrium'
    is_significant BOOLEAN NOT NULL DEFAULT TRUE,  -- Is this force strong enough to matter?
    
    -- Temporal aspects
    interaction_strength_history JSONB,  -- How force has evolved
    measured_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CHECK (entity1_mass_id != entity2_mass_id),  -- Can't interact with self
    CHECK (force_magnitude >= 0),
    CHECK (separation_distance >= 0),
    CHECK (interaction_type IN ('attraction', 'repulsion', 'equilibrium')),
    UNIQUE(entity1_mass_id, entity2_mass_id, measured_at)
);

CREATE INDEX idx_grav_int_entities ON gravitational_interactions(entity1_mass_id, entity2_mass_id);
CREATE INDEX idx_grav_int_magnitude ON gravitational_interactions(force_magnitude DESC);
CREATE INDEX idx_grav_int_type ON gravitational_interactions(interaction_type);
CREATE INDEX idx_grav_int_significant ON gravitational_interactions(is_significant) WHERE is_significant = TRUE;
CREATE INDEX idx_grav_int_spatial ON gravitational_interactions USING GIST(force_vector);

COMMENT ON TABLE gravitational_interactions IS 
'Pairwise gravitational forces between massive entities in the network';
COMMENT ON COLUMN gravitational_interactions.separation_distance IS 
'Distance in network embedding space (continuous)';
COMMENT ON COLUMN gravitational_interactions.network_hops IS 
'Topological distance via shortest path (discrete)';

-- ============================================================================
-- PART 4: SPACETIME CURVATURE - NETWORK TOPOLOGY WARPING
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Spacetime Curvature: How Mass Warps Network Topology
-- ----------------------------------------------------------------------------
-- Massive entities curve the network "spacetime" around them, affecting
-- how connections form and how influence propagates. This is analogous to
-- how mass curves spacetime in general relativity.
CREATE TABLE IF NOT EXISTS spacetime_curvature (
    id BIGSERIAL PRIMARY KEY,
    
    -- Source of curvature
    source_mass_id BIGINT NOT NULL REFERENCES gravitational_mass(id) ON DELETE CASCADE,
    
    -- Curvature metrics
    ricci_scalar DECIMAL(20, 10),  -- Overall curvature at this point
    curvature_tensor JSONB,  -- Detailed curvature information
    -- Structure: {
    --   "temporal": float,  // Curvature in time dimension
    --   "spatial_x": float,  // Curvature in x spatial dimension
    --   "spatial_y": float,  // Curvature in y spatial dimension
    --   "trace": float  // Trace of curvature tensor
    -- }
    
    -- Geodesics: Shortest paths in curved space
    geodesic_deviations JSONB,  -- How paths bend around massive objects
    -- Structure: Array of {from, to, straight_distance, geodesic_distance}
    
    -- Curvature region
    curvature_geometry GEOMETRY(POLYGON, 4326),  -- Spatial extent of significant curvature
    curvature_radius DECIMAL(20, 10) NOT NULL,  -- Radius of curvature effect
    
    -- Metric tensor components
    metric_signature JSONB,  -- Signature of spacetime metric
    -- Structure: {
    --   "g_tt": float,  // Temporal metric component
    --   "g_xx": float,  // Spatial metric components
    --   "g_yy": float,
    --   "g_xy": float  // Off-diagonal (coupling between dimensions)
    -- }
    
    -- Phenomena caused by curvature
    light_deflection DECIMAL(10, 6),  -- How "paths" bend (in degrees)
    time_dilation_factor DECIMAL(15, 10),  -- Time flows differently near massive objects
    
    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CHECK (curvature_radius >= 0)
);

CREATE INDEX idx_spacetime_source ON spacetime_curvature(source_mass_id);
CREATE INDEX idx_spacetime_scalar ON spacetime_curvature(ricci_scalar);
CREATE INDEX idx_spacetime_spatial ON spacetime_curvature USING GIST(curvature_geometry);

COMMENT ON TABLE spacetime_curvature IS 
'How massive entities warp the topology of the network, affecting paths and connections';
COMMENT ON COLUMN spacetime_curvature.ricci_scalar IS 
'Single number summarizing curvature - positive = space curved inward, negative = outward';
COMMENT ON COLUMN spacetime_curvature.geodesic_deviations IS 
'How shortest paths deviate from straight lines due to curvature';

-- ============================================================================
-- PART 5: QUANTUM EFFECTS - DISCRETE, PROBABILISTIC, ENTANGLED
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Quantum States: Superposition and Discrete Energy Levels
-- ----------------------------------------------------------------------------
-- In quantum gravity, entities can exist in superposition of states and
-- have discrete energy levels. This models uncertainty and probabilistic behavior.
CREATE TABLE IF NOT EXISTS quantum_states (
    id BIGSERIAL PRIMARY KEY,
    
    -- What entity has quantum behavior
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT NOT NULL,
    
    -- Quantum state description
    state_vector JSONB NOT NULL,  -- Quantum state in basis representation
    -- Structure: {
    --   "basis_states": [
    --     {"state": "active", "amplitude": complex, "probability": float},
    --     {"state": "dormant", "amplitude": complex, "probability": float},
    --     {"state": "transitional", "amplitude": complex, "probability": float}
    --   ],
    --   "phase": float,  // Global phase
    --   "coherence": float  // Measure of quantum coherence
    -- }
    
    -- Energy levels (discrete)
    energy_level INTEGER NOT NULL,  -- Current energy eigenstate
    energy_value DECIMAL(20, 10) NOT NULL,  -- Energy of this level
    possible_transitions JSONB,  -- Allowed quantum jumps
    -- Structure: Array of {from_level, to_level, transition_probability, energy_diff}
    
    -- Uncertainty relations
    position_uncertainty DECIMAL(20, 10),  -- Uncertainty in position
    momentum_uncertainty DECIMAL(20, 10),  -- Uncertainty in momentum/velocity
    energy_time_uncertainty DECIMAL(20, 10),  -- Energy-time uncertainty product
    
    -- Measurement and collapse
    last_measured_at TIMESTAMP WITH TIME ZONE,
    measurement_outcome VARCHAR(100),  -- Result of last measurement
    collapse_probability DECIMAL(10, 8),  -- Probability of wave function collapse
    
    -- Decoherence
    decoherence_rate DECIMAL(15, 10),  -- How fast quantum effects disappear
    environment_coupling DECIMAL(10, 6),  -- Strength of environmental interaction
    
    -- Metadata
    state_prepared_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    state_valid_until TIMESTAMP WITH TIME ZONE,
    
    CHECK (energy_level >= 0),
    CHECK (position_uncertainty >= 0),
    CHECK (momentum_uncertainty >= 0)
);

CREATE INDEX idx_quantum_entity ON quantum_states(entity_type, entity_id);
CREATE INDEX idx_quantum_energy ON quantum_states(energy_level, energy_value);
CREATE INDEX idx_quantum_coherence ON quantum_states((state_vector->>'coherence'));

COMMENT ON TABLE quantum_states IS 
'Quantum mechanical states: superposition, discrete energies, and uncertainty';
COMMENT ON COLUMN quantum_states.energy_level IS 
'Discrete quantum number - entities can only exist at specific energy levels';
COMMENT ON COLUMN quantum_states.decoherence_rate IS 
'How quickly quantum behavior gives way to classical behavior';

-- ----------------------------------------------------------------------------
-- Quantum Entanglement: Non-Local Correlations Between Entities
-- ----------------------------------------------------------------------------
-- Entangled entities have correlated states even when separated.
-- Measuring one entity instantly affects the state of its entangled partner.
CREATE TABLE IF NOT EXISTS quantum_entanglement (
    id BIGSERIAL PRIMARY KEY,
    
    -- Entangled entities
    entity1_state_id BIGINT NOT NULL REFERENCES quantum_states(id) ON DELETE CASCADE,
    entity2_state_id BIGINT NOT NULL REFERENCES quantum_states(id) ON DELETE CASCADE,
    
    -- Entanglement characteristics
    entanglement_entropy DECIMAL(15, 10) NOT NULL,  -- Measure of entanglement strength
    correlation_coefficient DECIMAL(10, 8) NOT NULL,  -- Statistical correlation
    
    -- Bell inequalities (tests of quantum behavior)
    bell_parameter DECIMAL(10, 6),  -- S parameter in CHSH inequality
    violates_bell_inequality BOOLEAN,  -- True if quantum correlation detected
    
    -- Entangled state description
    joint_state JSONB NOT NULL,  -- Description of the entangled state
    -- Structure: {
    --   "schmidt_decomposition": [
    --     {"coefficient": float, "state_A": string, "state_B": string}
    --   ],
    --   "entanglement_type": string,  // 'maximally_entangled', 'partially_entangled', 'separable'
    --   "purity": float
    -- }
    
    -- Separability
    is_separable BOOLEAN NOT NULL DEFAULT FALSE,  -- Can states be factored?
    separability_witness DECIMAL(10, 6),  -- Test for entanglement
    
    -- Distance and non-locality
    separation_distance DECIMAL(20, 10),  -- Spatial separation
    instantaneous_correlation BOOLEAN,  -- Are correlations non-local?
    
    -- Temporal evolution
    entanglement_created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    entanglement_broken_at TIMESTAMP WITH TIME ZONE,
    entanglement_lifetime INTERVAL,
    
    -- Constraints
    CHECK (entity1_state_id != entity2_state_id),
    CHECK (entanglement_entropy >= 0),
    CHECK (correlation_coefficient BETWEEN -1 AND 1),
    UNIQUE(entity1_state_id, entity2_state_id)
);

CREATE INDEX idx_entangle_entities ON quantum_entanglement(entity1_state_id, entity2_state_id);
CREATE INDEX idx_entangle_strength ON quantum_entanglement(entanglement_entropy DESC);
CREATE INDEX idx_entangle_active ON quantum_entanglement(entanglement_broken_at) 
    WHERE entanglement_broken_at IS NULL;

COMMENT ON TABLE quantum_entanglement IS 
'Quantum entanglement: non-local correlations between entity states';
COMMENT ON COLUMN quantum_entanglement.bell_parameter IS 
'CHSH parameter - value > 2 indicates quantum entanglement';
COMMENT ON COLUMN quantum_entanglement.entanglement_entropy IS 
'Von Neumann entropy - 0 = no entanglement, max = maximally entangled';

-- ============================================================================
-- PART 6: LORENTZ VIOLATION - SYMMETRY BREAKING
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Lorentz Violation: Directional Preferences and Symmetry Breaking
-- ----------------------------------------------------------------------------
-- In phenomenological quantum gravity, Lorentz symmetry (isotropy) may be
-- violated - certain directions are preferred over others.
CREATE TABLE IF NOT EXISTS lorentz_violation (
    id BIGSERIAL PRIMARY KEY,
    
    -- Where violation occurs
    region_geometry GEOMETRY(POLYGON, 4326) NOT NULL,  -- Spatial region
    
    -- Preferred directions
    preferred_direction GEOMETRY(LINESTRING, 4326),  -- Vector indicating preference
    anisotropy_vector JSONB NOT NULL,  -- Components of anisotropy
    -- Structure: {
    --   "temporal": float,  // Preferred time direction
    --   "spatial": {
    --     "x": float,
    --     "y": float,
    --     "magnitude": float,
    --     "azimuth": float  // Direction in degrees
    --   },
    --   "boost_preference": float  // Preferred velocity direction
    -- }
    
    -- Violation parameters
    violation_magnitude DECIMAL(15, 10) NOT NULL,  -- Strength of violation
    violation_type VARCHAR(100) NOT NULL,  -- Type of symmetry broken
    -- Examples: 'rotation', 'boost', 'cpt', 'space_isotropy', 'time_reversal'
    
    -- Modified dispersion relations
    dispersion_coefficients JSONB,  -- How energy-momentum relation changes
    -- Structure: {
    --   "c0": float,  // Speed of "light" (information) at zero momentum
    --   "c1": float,  // First order correction
    --   "c2": float,  // Second order correction
    --   "direction_dependent": boolean
    -- }
    
    -- Observable effects
    speed_anisotropy DECIMAL(10, 6),  -- Variation in propagation speed by direction
    arrival_time_differences JSONB,  -- Signals arrive at different times from different directions
    
    -- Statistical tests
    test_statistic DECIMAL(15, 10),  -- Statistical measure of violation
    significance_level DECIMAL(10, 8),  -- p-value for violation detection
    is_statistically_significant BOOLEAN,
    
    -- Metadata
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    observation_count INTEGER NOT NULL DEFAULT 1,
    
    CHECK (violation_magnitude >= 0),
    CHECK (violation_type IN ('rotation', 'boost', 'cpt', 'space_isotropy', 'time_reversal', 'parity'))
);

CREATE INDEX idx_lorentz_spatial ON lorentz_violation USING GIST(region_geometry);
CREATE INDEX idx_lorentz_magnitude ON lorentz_violation(violation_magnitude DESC);
CREATE INDEX idx_lorentz_type ON lorentz_violation(violation_type);
CREATE INDEX idx_lorentz_significant ON lorentz_violation(is_statistically_significant) 
    WHERE is_statistically_significant = TRUE;

COMMENT ON TABLE lorentz_violation IS 
'Lorentz symmetry violations: preferred directions and broken symmetries in network space';
COMMENT ON COLUMN lorentz_violation.anisotropy_vector IS 
'Direction and magnitude of preferential behavior - network not isotropic';

-- ============================================================================
-- PART 7: PHENOMENOLOGICAL OBSERVABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Quantum Gravity Signatures: Observable Manifestations
-- ----------------------------------------------------------------------------
-- Phenomenological approach: Focus on what we can actually observe and measure.
-- This table captures measurable signatures of quantum gravitational effects.
CREATE TABLE IF NOT EXISTS quantum_gravity_signatures (
    id BIGSERIAL PRIMARY KEY,
    
    -- What signature is observed
    signature_type VARCHAR(100) NOT NULL,
    -- Examples: 'discreteness', 'foam_structure', 'minimum_length', 
    --           'modified_commutator', 'holographic_bound'
    
    -- Observable quantity
    measured_value DECIMAL(20, 10) NOT NULL,
    theoretical_prediction DECIMAL(20, 10),
    measurement_error DECIMAL(20, 10),
    
    -- Context
    measurement_region GEOMETRY(POLYGON, 4326),
    energy_scale DECIMAL(20, 10),  -- Energy at which effect is measured
    length_scale DECIMAL(20, 10),  -- Length scale of observation
    
    -- Statistical confidence
    confidence_level DECIMAL(10, 8),  -- Confidence in measurement (0-1)
    signal_to_noise DECIMAL(15, 10),  -- Quality of signal
    
    -- Description
    signature_details JSONB NOT NULL,
    -- Structure varies by signature_type, but generally includes:
    -- {
    --   "description": string,
    --   "parameters": {...},
    --   "theoretical_framework": string,
    --   "interpretation": string
    -- }
    
    -- Related entities
    related_entities JSONB,  -- Which entities show this signature
    
    -- Temporal aspects
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    observation_duration INTERVAL,
    
    CHECK (energy_scale > 0),
    CHECK (length_scale > 0),
    CHECK (confidence_level BETWEEN 0 AND 1)
);

CREATE INDEX idx_qg_sig_type ON quantum_gravity_signatures(signature_type);
CREATE INDEX idx_qg_sig_confidence ON quantum_gravity_signatures(confidence_level DESC);
CREATE INDEX idx_qg_sig_spatial ON quantum_gravity_signatures USING GIST(measurement_region);
CREATE INDEX idx_qg_sig_details ON quantum_gravity_signatures USING GIN(signature_details);

COMMENT ON TABLE quantum_gravity_signatures IS 
'Observable signatures of quantum gravitational effects in the network';
COMMENT ON COLUMN quantum_gravity_signatures.signature_type IS 
'Type of quantum gravity phenomenon observed';

-- ============================================================================
-- PART 8: FUNCTIONS FOR CALCULATIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Calculate Gravitational Mass
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_gravitational_mass(
    p_entity_type VARCHAR(50),
    p_entity_id BIGINT
) RETURNS DECIMAL(20, 10) AS $$
DECLARE
    v_mass DECIMAL(20, 10);
    v_tx_volume DECIMAL(20, 10);
    v_holder_count INTEGER;
    v_connection_count INTEGER;
    v_age_days INTEGER;
    v_ubuntu_score DECIMAL(10, 6);
    v_activity_score DECIMAL(10, 6);
BEGIN
    -- Calculate mass based on multiple factors
    -- This is a simplified version - actual implementation would be more sophisticated
    
    IF p_entity_type = 'account' THEN
        -- For accounts: transaction volume + connections + age
        SELECT 
            COALESCE(SUM(amount), 0),
            COUNT(DISTINCT target_account_id),
            EXTRACT(days FROM (NOW() - created_at))
        INTO v_tx_volume, v_connection_count, v_age_days
        FROM phenomenal.intentional_relations ir
        JOIN phenomenal.accounts a ON ir.source_account_id = p_entity_id
        WHERE ir.source_account_id = p_entity_id;
        
        -- Simplified mass calculation
        v_mass := (v_tx_volume / 1000000.0) + 
                  (v_connection_count * 10.0) + 
                  (v_age_days / 30.0);
        
    ELSIF p_entity_type = 'asset' THEN
        -- For assets: holder count + total supply + ubuntu alignment
        SELECT 
            COUNT(DISTINCT account_id),
            COALESCE(SUM(balance), 0)
        INTO v_holder_count, v_tx_volume
        FROM phenomenal.intentional_relations
        WHERE target_asset_id = p_entity_id;
        
        -- Get ubuntu score
        SELECT COALESCE(AVG(alignment_score), 0.5)
        INTO v_ubuntu_score
        FROM phenomenal.ubuntu_balances
        WHERE asset_id = p_entity_id;
        
        -- Simplified mass calculation
        v_mass := (v_holder_count * 5.0) + 
                  (v_tx_volume / 1000000.0) + 
                  (v_ubuntu_score * 100.0);
    ELSE
        v_mass := 0.0;
    END IF;
    
    RETURN GREATEST(v_mass, 0.0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_gravitational_mass IS 
'Calculate gravitational mass (importance) for any entity';

-- ----------------------------------------------------------------------------
-- Calculate Gravitational Force Between Two Entities
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_gravitational_force(
    p_mass1_id BIGINT,
    p_mass2_id BIGINT
) RETURNS DECIMAL(20, 10) AS $$
DECLARE
    v_mass1 DECIMAL(20, 10);
    v_mass2 DECIMAL(20, 10);
    v_distance DECIMAL(20, 10);
    v_force DECIMAL(20, 10);
    v_G CONSTANT DECIMAL(20, 10) := 1.0;  -- Gravitational constant (normalized)
BEGIN
    -- Get masses
    SELECT gravitational_mass INTO v_mass1
    FROM phenomenal.gravitational_mass
    WHERE id = p_mass1_id;
    
    SELECT gravitational_mass INTO v_mass2
    FROM phenomenal.gravitational_mass
    WHERE id = p_mass2_id;
    
    -- Calculate distance (this is simplified - actual would use network embedding)
    v_distance := 1.0;  -- Placeholder
    
    -- F = G * m1 * m2 / r^2
    IF v_distance > 0 THEN
        v_force := (v_G * v_mass1 * v_mass2) / (v_distance * v_distance);
    ELSE
        v_force := v_G * v_mass1 * v_mass2;  -- Infinite force at zero distance
    END IF;
    
    RETURN v_force;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_gravitational_force IS 
'Calculate gravitational force between two massive entities using modified inverse square law';

-- ----------------------------------------------------------------------------
-- Calculate Spacetime Curvature
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_spacetime_curvature(
    p_mass_id BIGINT
) RETURNS DECIMAL(20, 10) AS $$
DECLARE
    v_mass DECIMAL(20, 10);
    v_curvature DECIMAL(20, 10);
    v_G CONSTANT DECIMAL(20, 10) := 1.0;
BEGIN
    -- Get mass
    SELECT gravitational_mass INTO v_mass
    FROM phenomenal.gravitational_mass
    WHERE id = p_mass_id;
    
    -- Ricci scalar proportional to mass density
    -- R = -8πG * (ρ - 3p)
    -- Simplified: R ≈ G * M
    v_curvature := v_G * v_mass;
    
    RETURN v_curvature;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_spacetime_curvature IS 
'Calculate spacetime curvature (Ricci scalar) induced by massive entity';

-- ----------------------------------------------------------------------------
-- Calculate Entanglement Entropy
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_entanglement_entropy(
    p_state1_id BIGINT,
    p_state2_id BIGINT
) RETURNS DECIMAL(15, 10) AS $$
DECLARE
    v_entropy DECIMAL(15, 10);
    v_state1 JSONB;
    v_state2 JSONB;
    v_correlation DECIMAL(10, 8);
BEGIN
    -- Get quantum states
    SELECT state_vector INTO v_state1
    FROM phenomenal.quantum_states
    WHERE id = p_state1_id;
    
    SELECT state_vector INTO v_state2
    FROM phenomenal.quantum_states
    WHERE id = p_state2_id;
    
    -- Calculate correlation (simplified)
    v_correlation := 0.5;  -- Placeholder - actual would compute from state vectors
    
    -- Von Neumann entropy: S = -Tr(ρ log ρ)
    -- Simplified approximation
    IF v_correlation > 0 AND v_correlation < 1 THEN
        v_entropy := -v_correlation * log(2, v_correlation) - 
                     (1 - v_correlation) * log(2, 1 - v_correlation);
    ELSE
        v_entropy := 0.0;
    END IF;
    
    RETURN GREATEST(v_entropy, 0.0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_entanglement_entropy IS 
'Calculate von Neumann entanglement entropy between two quantum states';

-- ============================================================================
-- PART 9: VIEWS FOR ANALYSIS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- View: Network Gravity Map
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW network_gravity_map AS
SELECT 
    gm.entity_type,
    gm.entity_id,
    gm.gravitational_mass,
    gm.inertial_mass,
    gf.influence_radius,
    gf.field_strength,
    gf.field_type,
    gf.field_geometry,
    gm.calculated_at
FROM phenomenal.gravitational_mass gm
LEFT JOIN phenomenal.gravitational_fields gf ON gm.id = gf.source_mass_id
WHERE gm.valid_until IS NULL OR gm.valid_until > NOW()
ORDER BY gm.gravitational_mass DESC;

COMMENT ON VIEW network_gravity_map IS 
'Visualization of gravitational mass and fields across the network';

-- ----------------------------------------------------------------------------
-- View: Strong Gravitational Interactions
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW strong_gravitational_interactions AS
SELECT 
    gi.id,
    gm1.entity_type AS entity1_type,
    gm1.entity_id AS entity1_id,
    gm2.entity_type AS entity2_type,
    gm2.entity_id AS entity2_id,
    gi.force_magnitude,
    gi.separation_distance,
    gi.potential_energy,
    gi.interaction_type,
    gi.measured_at
FROM phenomenal.gravitational_interactions gi
JOIN phenomenal.gravitational_mass gm1 ON gi.entity1_mass_id = gm1.id
JOIN phenomenal.gravitational_mass gm2 ON gi.entity2_mass_id = gm2.id
WHERE gi.is_significant = TRUE
  AND gi.force_magnitude > 0.1  -- Threshold for "strong"
ORDER BY gi.force_magnitude DESC;

COMMENT ON VIEW strong_gravitational_interactions IS 
'Network of significant gravitational interactions between entities';

-- ----------------------------------------------------------------------------
-- View: Curved Spacetime Regions
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW curved_spacetime_regions AS
SELECT 
    sc.id,
    gm.entity_type,
    gm.entity_id,
    gm.gravitational_mass,
    sc.ricci_scalar,
    sc.curvature_radius,
    sc.light_deflection,
    sc.time_dilation_factor,
    sc.curvature_geometry,
    sc.calculated_at
FROM phenomenal.spacetime_curvature sc
JOIN phenomenal.gravitational_mass gm ON sc.source_mass_id = gm.id
WHERE ABS(sc.ricci_scalar) > 0.01  -- Significant curvature
ORDER BY ABS(sc.ricci_scalar) DESC;

COMMENT ON VIEW curved_spacetime_regions IS 
'Regions of significant spacetime curvature in the network';

-- ----------------------------------------------------------------------------
-- View: Active Quantum Entanglements
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW active_quantum_entanglements AS
SELECT 
    qe.id,
    qs1.entity_type AS entity1_type,
    qs1.entity_id AS entity1_id,
    qs2.entity_type AS entity2_type,
    qs2.entity_id AS entity2_id,
    qe.entanglement_entropy,
    qe.correlation_coefficient,
    qe.violates_bell_inequality,
    qe.separation_distance,
    qe.entanglement_created_at,
    (NOW() - qe.entanglement_created_at) AS entanglement_age
FROM phenomenal.quantum_entanglement qe
JOIN phenomenal.quantum_states qs1 ON qe.entity1_state_id = qs1.id
JOIN phenomenal.quantum_states qs2 ON qe.entity2_state_id = qs2.id
WHERE qe.entanglement_broken_at IS NULL
ORDER BY qe.entanglement_entropy DESC;

COMMENT ON VIEW active_quantum_entanglements IS 
'Currently active quantum entanglements in the network';

-- ----------------------------------------------------------------------------
-- View: Lorentz Violation Hotspots
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW lorentz_violation_hotspots AS
SELECT 
    lv.id,
    lv.violation_type,
    lv.violation_magnitude,
    lv.speed_anisotropy,
    lv.test_statistic,
    lv.significance_level,
    lv.is_statistically_significant,
    lv.region_geometry,
    lv.observed_at,
    lv.observation_count
FROM phenomenal.lorentz_violation lv
WHERE lv.is_statistically_significant = TRUE
ORDER BY lv.violation_magnitude DESC;

COMMENT ON VIEW lorentz_violation_hotspots IS 
'Regions with statistically significant Lorentz symmetry violations';

-- ============================================================================
-- PART 10: TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Trigger: Auto-calculate gravitational mass when entities change
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION auto_calculate_gravity() RETURNS TRIGGER AS $$
DECLARE
    v_mass DECIMAL(20, 10);
    v_entity_type VARCHAR(50);
BEGIN
    -- Determine entity type from table
    v_entity_type := CASE TG_TABLE_NAME
        WHEN 'accounts' THEN 'account'
        WHEN 'assets' THEN 'asset'
        WHEN 'holons' THEN 'holon'
        ELSE 'unknown'
    END;
    
    -- Calculate mass
    v_mass := calculate_gravitational_mass(v_entity_type, NEW.id);
    
    -- Insert or update gravitational_mass
    INSERT INTO phenomenal.gravitational_mass (
        entity_type,
        entity_id,
        gravitational_mass,
        inertial_mass,
        mass_basis,
        calculated_at
    ) VALUES (
        v_entity_type,
        NEW.id,
        v_mass,
        v_mass * 1.1,  -- Inertial slightly higher than gravitational
        jsonb_build_object(
            'auto_calculated', TRUE,
            'calculation_method', 'trigger'
        ),
        NOW()
    )
    ON CONFLICT (entity_type, entity_id, calculated_at) 
    DO UPDATE SET
        gravitational_mass = v_mass,
        inertial_mass = v_mass * 1.1;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION auto_calculate_gravity IS 
'Automatically calculate gravitational mass when entities are created or updated';

-- Apply trigger to relevant tables (only if they exist)
DO $$
BEGIN
    -- For accounts
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'phenomenal' AND table_name = 'accounts') THEN
        DROP TRIGGER IF EXISTS trg_account_gravity ON phenomenal.accounts;
        CREATE TRIGGER trg_account_gravity
            AFTER INSERT OR UPDATE ON phenomenal.accounts
            FOR EACH ROW
            EXECUTE FUNCTION auto_calculate_gravity();
    END IF;
    
    -- For assets
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'phenomenal' AND table_name = 'assets') THEN
        DROP TRIGGER IF EXISTS trg_asset_gravity ON phenomenal.assets;
        CREATE TRIGGER trg_asset_gravity
            AFTER INSERT OR UPDATE ON phenomenal.assets
            FOR EACH ROW
            EXECUTE FUNCTION auto_calculate_gravity();
    END IF;
END $$;

-- ============================================================================
-- PART 11: MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Materialized View: Gravitational Network (for fast visualization)
-- ----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS gravitational_network AS
SELECT 
    gi.id AS interaction_id,
    gm1.entity_type AS entity1_type,
    gm1.entity_id AS entity1_id,
    gm1.gravitational_mass AS entity1_mass,
    gm2.entity_type AS entity2_type,
    gm2.entity_id AS entity2_id,
    gm2.gravitational_mass AS entity2_mass,
    gi.force_magnitude,
    gi.separation_distance,
    gi.interaction_type,
    ST_AsGeoJSON(gi.force_vector) AS force_vector_geojson,
    gi.measured_at
FROM phenomenal.gravitational_interactions gi
JOIN phenomenal.gravitational_mass gm1 ON gi.entity1_mass_id = gm1.id
JOIN phenomenal.gravitational_mass gm2 ON gi.entity2_mass_id = gm2.id
WHERE gi.is_significant = TRUE
  AND gi.force_magnitude > 0.01;

CREATE INDEX idx_mv_grav_net_force ON gravitational_network(force_magnitude DESC);
CREATE INDEX idx_mv_grav_net_type ON gravitational_network(interaction_type);

COMMENT ON MATERIALIZED VIEW gravitational_network IS 
'Pre-computed gravitational network for fast visualization (refresh periodically)';

-- ============================================================================
-- PART 12: EXAMPLE QUERIES
-- ============================================================================

-- Query 1: Find most massive entities (highest importance)
-- SELECT entity_type, entity_id, gravitational_mass, mass_basis
-- FROM phenomenal.gravitational_mass
-- WHERE valid_until IS NULL OR valid_until > NOW()
-- ORDER BY gravitational_mass DESC
-- LIMIT 10;

-- Query 2: Find entities with strongest gravitational interactions
-- SELECT * FROM phenomenal.strong_gravitational_interactions
-- LIMIT 20;

-- Query 3: Find regions of highest spacetime curvature
-- SELECT * FROM phenomenal.curved_spacetime_regions
-- LIMIT 10;

-- Query 4: Find maximally entangled entity pairs
-- SELECT * FROM phenomenal.active_quantum_entanglements
-- WHERE entanglement_entropy > 0.9  -- Near maximum entanglement
-- ORDER BY entanglement_entropy DESC;

-- Query 5: Detect Lorentz violation hotspots
-- SELECT * FROM phenomenal.lorentz_violation_hotspots
-- WHERE violation_magnitude > 0.1
-- ORDER BY significance_level ASC;  -- Most significant first

-- Query 6: Find entities in superposition
-- SELECT entity_type, entity_id, 
--        state_vector->>'coherence' AS coherence,
--        energy_level
-- FROM phenomenal.quantum_states
-- WHERE (state_vector->>'coherence')::float > 0.7
-- ORDER BY (state_vector->>'coherence')::float DESC;

-- Query 7: Network gravity within a spatial region
-- SELECT * FROM phenomenal.network_gravity_map
-- WHERE ST_Within(
--     field_geometry,
--     ST_MakeEnvelope(-180, -90, 180, 90, 4326)
-- );

-- Query 8: Time evolution of gravitational mass
-- SELECT entity_type, entity_id, calculated_at, gravitational_mass
-- FROM phenomenal.gravitational_mass
-- WHERE entity_type = 'account' AND entity_id = 12345
-- ORDER BY calculated_at;

-- ============================================================================
-- END OF QUANTUM GRAVITY EXTENSION
-- ============================================================================

-- Final setup
COMMENT ON SCHEMA phenomenal IS 
'Phenomenological blockchain model with comprehensive quantum gravity extensions';

-- Grant permissions (adjust as needed)
-- GRANT USAGE ON SCHEMA phenomenal TO your_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA phenomenal TO your_user;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA phenomenal TO your_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA phenomenal TO your_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Quantum Gravity Extension installed successfully!';
    RAISE NOTICE 'New tables: gravitational_mass, gravitational_fields, gravitational_interactions,';
    RAISE NOTICE '            spacetime_curvature, quantum_states, quantum_entanglement,';
    RAISE NOTICE '            lorentz_violation, quantum_gravity_signatures';
    RAISE NOTICE 'New functions: calculate_gravitational_mass, calculate_gravitational_force,';
    RAISE NOTICE '               calculate_spacetime_curvature, calculate_entanglement_entropy';
    RAISE NOTICE 'New views: network_gravity_map, strong_gravitational_interactions,';
    RAISE NOTICE '           curved_spacetime_regions, active_quantum_entanglements,';
    RAISE NOTICE '           lorentz_violation_hotspots';
END $$;
