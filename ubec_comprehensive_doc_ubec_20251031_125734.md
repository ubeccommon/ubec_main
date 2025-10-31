# UBEC Protocol Suite - Comprehensive Database Documentation

## 🜁 🜄 🜃 🜂 Complete Multi-Schema Analysis

**Database:** `ubec`  
**Host:** `localhost`  
**Generated:** 2025-10-31T12:57:33.708321  
**PostgreSQL Version:** PostgreSQL 15.13 (Debian 15.13-0+deb12u1) on x86_64-pc-linux-gnu  
**Documentation Version:** 4.0 - Multi-Schema  
**Database Size:** 80 MB  

## 📊 Database Overview

**Total Schemas:** 4  
**Total Tables:** 68  
**Total Rows:** 87,567  
**Total Columns:** 849  
**Total Views:** 29  
**Total Functions:** 1133  
**Total Relationships:** 9  
**Total Indexes:** 427  

### Schemas in Database

| Schema | Description | Tables | Rows | Views | Functions |
|--------|-------------|--------|------|-------|------------|
| ubec_main | Main schema for UBEC four-element protoc... | 47 | 79,067 | 20 | 80 |
| phenomenal | Unified phenomenological blockchain mode... | 18 | 0 | 7 | 10 |
| topology | PostGIS Topology schema... | 2 | 0 | 0 | 103 |
| public | standard public schema... | 1 | 8,500 | 2 | 940 |

---

## Schema: `phenomenal`

**Description:** Unified phenomenological blockchain model with quantum gravity: combining philosophy, physics, and Ubuntu principles for the ubec database

### Schema Statistics

- **Tables:** 18
- **Total Rows:** 0
- **Columns:** 256
- **Views:** 7
- **Relationships:** 0
- **Indexes:** 105
- **Triggers:** 0
- **Functions:** 10
- **Custom Types:** 6

### Custom Types

#### existence_mode

**Values:** `ready_to_hand`, `present_at_hand`, `unready_to_hand`, `absent`

#### holonic_category

**Values:** `holon`, `autonomous_unit`, `collective`, `network_node`, `isolate`

#### intentional_relation

**Values:** `trustline`, `payment`, `offer`, `sponsorship`, `authorization`, `claimable`, `liquidity_pool`

#### phenomenal_mode

**Values:** `fully_present`, `retained`, `protended`, `co_present`, `implicitly_meant`

#### temporal_horizon

**Values:** `immediate`, `proximal`, `intermediate`, `distant`, `extended`

#### ubuntu_principle

**Values:** `diversity`, `reciprocity`, `mutualism`, `regeneration`

### Tables

| Table | Rows | Columns | Size |
|-------|------|---------|------|
| accounts | 0 | 19 | 80 kB |
| assets | 0 | 17 | 88 kB |
| geodesics | 0 | 10 | 56 kB |
| gravitational_fields | 0 | 10 | 48 kB |
| gravitational_interactions | 0 | 14 | 64 kB |
| gravitational_mass | 0 | 9 | 64 kB |
| holons | 0 | 19 | 64 kB |
| intentional_relations | 0 | 23 | 88 kB |
| lorentz_violation | 0 | 14 | 48 kB |
| network_embeddings | 0 | 8 | 24 kB |
| protentions | 0 | 14 | 48 kB |
| quantum_entanglement | 0 | 15 | 48 kB |
| quantum_gravity_signatures | 0 | 14 | 56 kB |
| quantum_states | 0 | 17 | 40 kB |
| retentions | 0 | 11 | 48 kB |
| spacetime_curvature | 0 | 11 | 40 kB |
| spatial_positions | 0 | 12 | 48 kB |
| transactions | 0 | 19 | 72 kB |

#### phenomenal.accounts

*Accounts as Dasein: beings situated in the blockchain world with intentional directedness*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('accounts_id_seq'::... | - |
| account_address | varchar(56) | ✗ | - | - |
| dasein_type | varchar(50) | ✗ | 'participant'::character va... | - |
| comportment_pattern | varchar(50) | ✓ | - | - |
| holonic_category | enum | ✗ | 'network_node'::holonic_cat... | - |
| thrown_at | timestamp with time zone | ✗ | - | - |
| facticity | jsonb | ✓ | - | - |
| network_position | enum | ✓ | - | - |
| spatial_context | jsonb | ✓ | - | - |
| primary_intentions | ARRAY | ✓ | - | - |
| intention_strength | jsonb | ✓ | - | - |
| internal_horizon | jsonb | ✗ | '{}'::jsonb | - |
| external_horizon | jsonb | ✗ | '{}'::jsonb | - |
| ubuntu_scores | jsonb | ✓ | - | - |
| retained_states | jsonb | ✓ | - | - |
| present_state | jsonb | ✗ | - | - |
| anticipated_states | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `accounts_account_address_key` (UNIQUE)
- `accounts_pkey` (PRIMARY KEY)

#### phenomenal.assets

*Assets as phenomena: things as they appear in the blockchain, with internal/external horizons*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('assets_id_seq'::re... | - |
| asset_code | varchar(12) | ✗ | - | - |
| issuer_address | varchar(56) | ✗ | - | - |
| phenomenal_mode | enum | ✗ | 'fully_present'::phenomenal... | - |
| existence_mode | enum | ✗ | 'present_at_hand'::existenc... | - |
| ubuntu_principle | enum | ✓ | - | - |
| internal_horizon | jsonb | ✗ | '{}'::jsonb | - |
| external_horizon | jsonb | ✗ | '{}'::jsonb | - |
| genesis_at | timestamp with time zone | ✗ | - | - |
| retained_history | jsonb | ✓ | - | - |
| present_state | jsonb | ✗ | - | - |
| protended_futures | jsonb | ✓ | - | - |
| temporal_horizon | enum | ✗ | 'intermediate'::temporal_ho... | - |
| network_position | enum | ✓ | - | - |
| topology_metadata | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `assets_asset_code_issuer_address_key` (UNIQUE)
- `assets_pkey` (PRIMARY KEY)

#### phenomenal.geodesics

*Shortest paths (geodesics) through the network topology*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('geodesics_id_seq':... | - |
| from_account_id | integer | ✗ | - | - |
| to_account_id | integer | ✗ | - | - |
| path_length | integer | ✗ | - | - |
| path_nodes | ARRAY | ✗ | - | - |
| path_edges | ARRAY | ✗ | - | - |
| path_line | enum | ✓ | - | - |
| weighted_distance | numeric(20,10) | ✓ | - | - |
| computed_at | timestamp with time zone | ✗ | now() | - |
| valid_until | timestamp with time zone | ✓ | - | - |

**Constraints:**
- `geodesics_from_account_id_fkey` (FOREIGN KEY)
- `geodesics_from_account_id_to_account_id_key` (UNIQUE)
- `geodesics_pkey` (PRIMARY KEY)
- `geodesics_to_account_id_fkey` (FOREIGN KEY)

#### phenomenal.gravitational_fields

*Gravitational fields: zones of influence surrounding massive entities*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('gravitational_fiel... | - |
| source_mass_id | bigint | ✗ | - | - |
| field_profile | jsonb | ✗ | - | - |
| influence_radius | numeric(20,10) | ✗ | - | - |
| field_geometry | enum | ✓ | - | - |
| field_type | varchar(50) | ✗ | - | - |
| field_strength | numeric(20,10) | ✗ | - | - |
| is_static | boolean | ✗ | false | - |
| temporal_variation | jsonb | ✓ | - | - |
| calculated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `gravitational_fields_field_strength_check` (CHECK)
- `gravitational_fields_field_type_check` (CHECK)
- `gravitational_fields_influence_radius_check` (CHECK)
- `gravitational_fields_pkey` (PRIMARY KEY)
- `gravitational_fields_source_mass_id_fkey` (FOREIGN KEY)

#### phenomenal.gravitational_interactions

*Pairwise gravitational forces between massive entities in the network*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('gravitational_inte... | - |
| entity1_mass_id | bigint | ✗ | - | - |
| entity2_mass_id | bigint | ✗ | - | - |
| force_magnitude | numeric(20,10) | ✗ | - | - |
| force_direction | numeric(10,6) | ✓ | - | - |
| force_vector | enum | ✓ | - | - |
| separation_distance | numeric(20,10) | ✗ | - | - |
| network_hops | integer | ✓ | - | - |
| potential_energy | numeric(20,10) | ✓ | - | - |
| binding_energy | numeric(20,10) | ✓ | - | - |
| interaction_type | varchar(50) | ✗ | - | - |
| is_significant | boolean | ✗ | true | - |
| interaction_strength_history | jsonb | ✓ | - | - |
| measured_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `gravitational_interactions_check` (CHECK)
- `gravitational_interactions_entity1_mass_id_entity2_mass_id__key` (UNIQUE)
- `gravitational_interactions_entity1_mass_id_fkey` (FOREIGN KEY)
- `gravitational_interactions_entity2_mass_id_fkey` (FOREIGN KEY)
- `gravitational_interactions_force_magnitude_check` (CHECK)
- `gravitational_interactions_interaction_type_check` (CHECK)
- `gravitational_interactions_pkey` (PRIMARY KEY)
- `gravitational_interactions_separation_distance_check` (CHECK)

#### phenomenal.gravitational_mass

*Network gravity: measure of entity importance and influence*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('gravitational_mass... | - |
| entity_type | varchar(50) | ✗ | - | - |
| entity_id | bigint | ✗ | - | - |
| gravitational_mass | numeric(20,10) | ✗ | - | - |
| inertial_mass | numeric(20,10) | ✗ | - | - |
| mass_basis | jsonb | ✗ | - | - |
| calculated_at | timestamp with time zone | ✗ | now() | - |
| valid_until | timestamp with time zone | ✓ | - | - |
| mass_trajectory | jsonb | ✓ | - | - |

**Constraints:**
- `gravitational_mass_entity_type_entity_id_calculated_at_key` (UNIQUE)
- `gravitational_mass_gravitational_mass_check` (CHECK)
- `gravitational_mass_inertial_mass_check` (CHECK)
- `gravitational_mass_pkey` (PRIMARY KEY)

#### phenomenal.holons

*Holarchical structures: entities that are both autonomous wholes and integrated parts*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('phenomenal.holons_... | - |
| holon_name | varchar(255) | ✗ | - | - |
| holon_type | varchar(100) | ✗ | - | - |
| autonomy_score | numeric(5,4) | ✗ | - | - |
| integration_score | numeric(5,4) | ✗ | - | - |
| constituent_accounts | ARRAY | ✓ | - | - |
| constituent_assets | ARRAY | ✓ | - | - |
| constituent_relations | ARRAY | ✓ | - | - |
| parent_holons | ARRAY | ✓ | - | - |
| emergent_properties | jsonb | ✓ | - | - |
| collective_behavior | jsonb | ✓ | - | - |
| spatial_region | enum | ✓ | - | - |
| centroid | enum | ✓ | - | - |
| emerged_at | timestamp with time zone | ✗ | - | - |
| stable_from | timestamp with time zone | ✓ | - | - |
| dissolved_at | timestamp with time zone | ✓ | - | - |
| ubuntu_scores | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `holons_pkey` (PRIMARY KEY)

#### phenomenal.intentional_relations

*Intentional directedness: how accounts are related to assets and each other*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('intentional_relati... | - |
| from_account_id | integer | ✗ | - | - |
| to_account_id | integer | ✓ | - | - |
| asset_id | integer | ✓ | - | - |
| relation_type | enum | ✗ | - | - |
| phenomenal_mode | enum | ✗ | 'fully_present'::phenomenal... | - |
| noema | jsonb | ✗ | - | - |
| noesis | jsonb | ✗ | - | - |
| relation_strength | numeric(10,6) | ✗ | 0.5 | - |
| reciprocity_factor | numeric(10,6) | ✓ | - | - |
| stability_score | numeric(10,6) | ✓ | - | - |
| relation_line | enum | ✓ | - | - |
| geodesic_distance | numeric(20,10) | ✓ | - | - |
| euclidean_distance | numeric(20,10) | ✓ | - | - |
| emerged_at | timestamp with time zone | ✗ | - | - |
| retained_history | jsonb | ✓ | - | - |
| present_manifestation | jsonb | ✗ | - | - |
| protended_evolution | jsonb | ✓ | - | - |
| temporal_horizon | enum | ✗ | 'proximal'::temporal_horizon | - |
| active | boolean | ✗ | true | - |
| last_activity_at | timestamp with time zone | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `intentional_relations_asset_id_fkey` (FOREIGN KEY)
- `intentional_relations_from_account_id_fkey` (FOREIGN KEY)
- `intentional_relations_pkey` (PRIMARY KEY)
- `intentional_relations_to_account_id_fkey` (FOREIGN KEY)
- `valid_relation_structure` (CHECK)

#### phenomenal.lorentz_violation

*Lorentz symmetry violations: preferred directions and broken symmetries*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('lorentz_violation_... | - |
| region_geometry | enum | ✗ | - | - |
| preferred_direction | enum | ✓ | - | - |
| anisotropy_vector | jsonb | ✗ | - | - |
| violation_magnitude | numeric(15,10) | ✗ | - | - |
| violation_type | varchar(100) | ✗ | - | - |
| dispersion_coefficients | jsonb | ✓ | - | - |
| speed_anisotropy | numeric(10,6) | ✓ | - | - |
| arrival_time_differences | jsonb | ✓ | - | - |
| test_statistic | numeric(15,10) | ✓ | - | - |
| significance_level | numeric(10,8) | ✓ | - | - |
| is_statistically_significant | boolean | ✓ | - | - |
| observed_at | timestamp with time zone | ✗ | now() | - |
| observation_count | integer | ✗ | 1 | - |

**Constraints:**
- `lorentz_violation_pkey` (PRIMARY KEY)
- `lorentz_violation_violation_magnitude_check` (CHECK)
- `lorentz_violation_violation_type_check` (CHECK)

#### phenomenal.network_embeddings

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('network_embeddings... | - |
| computed_at | timestamp with time zone | ✗ | now() | - |
| embedding_method | varchar(100) | ✗ | - | - |
| dimensions | integer | ✗ | 2 | - |
| parameters | jsonb | ✗ | - | - |
| quality_metrics | jsonb | ✓ | - | - |
| valid_from | timestamp with time zone | ✗ | - | - |
| valid_until | timestamp with time zone | ✓ | - | - |

**Constraints:**
- `network_embeddings_pkey` (PRIMARY KEY)

#### phenomenal.protentions

*Future states anticipated in present consciousness (Husserlian protention)*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('protentions_id_seq... | - |
| entity_type | varchar(50) | ✗ | - | - |
| entity_id | integer | ✗ | - | - |
| protended_from | timestamp with time zone | ✗ | - | - |
| expected_at | timestamp with time zone | ✗ | - | - |
| temporal_distance | interval | ✗ | - | - |
| protended_content | jsonb | ✗ | - | - |
| expectation_confidence | numeric(5,4) | ✗ | 0.5 | - |
| protention_type | varchar(50) | ✗ | - | - |
| fulfilled | boolean | ✓ | - | - |
| fulfilled_at | timestamp with time zone | ✓ | - | - |
| fulfillment_degree | numeric(5,4) | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `protentions_pkey` (PRIMARY KEY)

#### phenomenal.quantum_entanglement

*Quantum entanglement: non-local correlations between entity states*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('quantum_entangleme... | - |
| entity1_state_id | bigint | ✗ | - | - |
| entity2_state_id | bigint | ✗ | - | - |
| entanglement_entropy | numeric(15,10) | ✗ | - | - |
| correlation_coefficient | numeric(10,8) | ✗ | - | - |
| bell_parameter | numeric(10,6) | ✓ | - | - |
| violates_bell_inequality | boolean | ✓ | - | - |
| joint_state | jsonb | ✗ | - | - |
| is_separable | boolean | ✗ | false | - |
| separability_witness | numeric(10,6) | ✓ | - | - |
| separation_distance | numeric(20,10) | ✓ | - | - |
| instantaneous_correlation | boolean | ✓ | - | - |
| entanglement_created_at | timestamp with time zone | ✗ | now() | - |
| entanglement_broken_at | timestamp with time zone | ✓ | - | - |
| entanglement_lifetime | interval | ✓ | - | - |

**Constraints:**
- `quantum_entanglement_check` (CHECK)
- `quantum_entanglement_correlation_coefficient_check` (CHECK)
- `quantum_entanglement_entanglement_entropy_check` (CHECK)
- `quantum_entanglement_entity1_state_id_entity2_state_id_key` (UNIQUE)
- `quantum_entanglement_entity1_state_id_fkey` (FOREIGN KEY)
- `quantum_entanglement_entity2_state_id_fkey` (FOREIGN KEY)
- `quantum_entanglement_pkey` (PRIMARY KEY)

#### phenomenal.quantum_gravity_signatures

*Observable signatures of quantum gravitational effects*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('quantum_gravity_si... | - |
| signature_type | varchar(100) | ✗ | - | - |
| measured_value | numeric(20,10) | ✗ | - | - |
| theoretical_prediction | numeric(20,10) | ✓ | - | - |
| measurement_error | numeric(20,10) | ✓ | - | - |
| measurement_region | enum | ✓ | - | - |
| energy_scale | numeric(20,10) | ✓ | - | - |
| length_scale | numeric(20,10) | ✓ | - | - |
| confidence_level | numeric(10,8) | ✓ | - | - |
| signal_to_noise | numeric(15,10) | ✓ | - | - |
| signature_details | jsonb | ✗ | - | - |
| related_entities | jsonb | ✓ | - | - |
| observed_at | timestamp with time zone | ✗ | now() | - |
| observation_duration | interval | ✓ | - | - |

**Constraints:**
- `quantum_gravity_signatures_confidence_level_check` (CHECK)
- `quantum_gravity_signatures_energy_scale_check` (CHECK)
- `quantum_gravity_signatures_length_scale_check` (CHECK)
- `quantum_gravity_signatures_pkey` (PRIMARY KEY)

#### phenomenal.quantum_states

*Quantum mechanical states: superposition, discrete energies, and uncertainty*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('quantum_states_id_... | - |
| entity_type | varchar(50) | ✗ | - | - |
| entity_id | bigint | ✗ | - | - |
| state_vector | jsonb | ✗ | - | - |
| energy_level | integer | ✗ | - | - |
| energy_value | numeric(20,10) | ✗ | - | - |
| possible_transitions | jsonb | ✓ | - | - |
| position_uncertainty | numeric(20,10) | ✓ | - | - |
| momentum_uncertainty | numeric(20,10) | ✓ | - | - |
| energy_time_uncertainty | numeric(20,10) | ✓ | - | - |
| last_measured_at | timestamp with time zone | ✓ | - | - |
| measurement_outcome | varchar(100) | ✓ | - | - |
| collapse_probability | numeric(10,8) | ✓ | - | - |
| decoherence_rate | numeric(15,10) | ✓ | - | - |
| environment_coupling | numeric(10,6) | ✓ | - | - |
| state_prepared_at | timestamp with time zone | ✗ | now() | - |
| state_valid_until | timestamp with time zone | ✓ | - | - |

**Constraints:**
- `quantum_states_energy_level_check` (CHECK)
- `quantum_states_momentum_uncertainty_check` (CHECK)
- `quantum_states_pkey` (PRIMARY KEY)
- `quantum_states_position_uncertainty_check` (CHECK)

#### phenomenal.retentions

*Past states retained in present consciousness (Husserlian retention)*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('retentions_id_seq'... | - |
| entity_type | varchar(50) | ✗ | - | - |
| entity_id | integer | ✗ | - | - |
| original_present | timestamp with time zone | ✗ | - | - |
| retained_at | timestamp with time zone | ✗ | - | - |
| temporal_distance | interval | ✗ | - | - |
| retained_content | jsonb | ✗ | - | - |
| retention_clarity | numeric(5,4) | ✗ | 1.0 | - |
| retention_type | varchar(50) | ✗ | - | - |
| transformations | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `retentions_pkey` (PRIMARY KEY)

#### phenomenal.spacetime_curvature

*How massive entities warp the topology of the network*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('spacetime_curvatur... | - |
| source_mass_id | bigint | ✗ | - | - |
| ricci_scalar | numeric(20,10) | ✓ | - | - |
| curvature_tensor | jsonb | ✓ | - | - |
| geodesic_deviations | jsonb | ✓ | - | - |
| curvature_geometry | enum | ✓ | - | - |
| curvature_radius | numeric(20,10) | ✗ | - | - |
| metric_signature | jsonb | ✓ | - | - |
| light_deflection | numeric(10,6) | ✓ | - | - |
| time_dilation_factor | numeric(15,10) | ✓ | - | - |
| calculated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `spacetime_curvature_curvature_radius_check` (CHECK)
- `spacetime_curvature_pkey` (PRIMARY KEY)
- `spacetime_curvature_source_mass_id_fkey` (FOREIGN KEY)

#### phenomenal.spatial_positions

*Spatial positions of entities in network embedding space*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('spatial_positions_... | - |
| embedding_id | integer | ✗ | - | - |
| entity_type | varchar(50) | ✗ | - | - |
| entity_id | integer | ✗ | - | - |
| position | enum | ✗ | - | - |
| coordinates | ARRAY | ✓ | - | - |
| local_density | numeric(20,10) | ✓ | - | - |
| centrality_scores | jsonb | ✓ | - | - |
| cluster_membership | ARRAY | ✓ | - | - |
| immediate_neighbors | ARRAY | ✓ | - | - |
| proximal_region | enum | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `spatial_positions_embedding_id_fkey` (FOREIGN KEY)
- `spatial_positions_pkey` (PRIMARY KEY)

#### phenomenal.transactions

*Transaction events as discrete phenomena in blockchain spacetime*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | ✗ | nextval('transactions_id_se... | - |
| transaction_hash | varchar(64) | ✗ | - | - |
| ledger_sequence | bigint | ✗ | - | - |
| event_type | varchar(50) | ✗ | - | - |
| source_account_id | integer | ✓ | - | - |
| ledger_closed_at | timestamp with time zone | ✗ | - | - |
| temporal_context | jsonb | ✓ | - | - |
| operations | jsonb | ✗ | - | - |
| operations_count | integer | ✗ | - | - |
| effects | jsonb | ✓ | - | - |
| successful | boolean | ✗ | - | - |
| result_code | varchar(100) | ✓ | - | - |
| affected_positions | enum | ✓ | - | - |
| network_impact | jsonb | ✓ | - | - |
| fee_charged | bigint | ✗ | - | - |
| resource_fee | bigint | ✓ | - | - |
| memo_type | varchar(20) | ✓ | - | - |
| memo_value | text | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `transactions_pkey` (PRIMARY KEY)
- `transactions_source_account_id_fkey` (FOREIGN KEY)
- `transactions_transaction_hash_key` (UNIQUE)

### Views

#### active_quantum_entanglements

```sql

```

#### current_network_state

```sql

```

#### curved_spacetime_regions

```sql

```

#### intentional_network

```sql

```

#### lorentz_violation_hotspots

```sql

```

#### network_gravity_map

```sql

```

#### strong_gravitational_interactions

```sql

```

### Functions

#### analyze_ubuntu_balance(p_account_id integer)

- **Returns:** jsonb
- **Language:** plpgsql
- **Description:** Analyze Ubuntu principle balance

#### auto_calculate_gravity()

- **Returns:** trigger
- **Language:** plpgsql

#### calculate_entanglement_entropy(p_state1_id bigint, p_state2_id bigint)

- **Returns:** numeric
- **Language:** plpgsql
- **Description:** Calculate von Neumann entanglement entropy

#### calculate_gravitational_force(p_mass1_id bigint, p_mass2_id bigint)

- **Returns:** numeric
- **Language:** plpgsql
- **Description:** Calculate gravitational force between two entities

#### calculate_gravitational_mass(p_entity_type character varying, p_entity_id bigint)

- **Returns:** numeric
- **Language:** plpgsql
- **Description:** Calculates the gravitational mass of an entity based on its connections and age. Returns a numeric value representing the entity's influence in the network.

#### calculate_spacetime_curvature(p_mass_id bigint)

- **Returns:** numeric
- **Language:** plpgsql
- **Description:** Calculate spacetime curvature (Ricci scalar)

#### compute_phenomenal_prominence(p_entity_type character varying, p_entity_id integer)

- **Returns:** jsonb
- **Language:** plpgsql
- **Description:** Compute centrality measures

#### maintain_retentions_trigger()

- **Returns:** trigger
- **Language:** plpgsql

#### update_spatial_positions_trigger()

- **Returns:** trigger
- **Language:** plpgsql

#### update_updated_at_column()

- **Returns:** trigger
- **Language:** plpgsql

---

## Schema: `public`

**Description:** standard public schema

### Schema Statistics

- **Tables:** 1
- **Total Rows:** 8,500
- **Columns:** 5
- **Views:** 2
- **Relationships:** 0
- **Indexes:** 1
- **Triggers:** 0
- **Functions:** 940
- **Custom Types:** 0

### Tables

| Table | Rows | Columns | Size |
|-------|------|---------|------|
| spatial_ref_sys | 8,500 | 5 | 7144 kB |

#### public.spatial_ref_sys

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| srid | integer | ✗ | - | - |
| auth_name | varchar(256) | ✓ | - | - |
| auth_srid | integer | ✓ | - | - |
| srtext | varchar(2048) | ✓ | - | - |
| proj4text | varchar(2048) | ✓ | - | - |

**Constraints:**
- `spatial_ref_sys_pkey` (PRIMARY KEY)
- `spatial_ref_sys_srid_check` (CHECK)

### Views

#### geography_columns

```sql

```

#### geometry_columns

```sql

```

### Functions

#### _postgis_deprecate(oldname text, newname text, version text)

- **Returns:** void
- **Language:** plpgsql

#### _postgis_index_extent(tbl regclass, col text)

- **Returns:** box2d
- **Language:** c

#### _postgis_join_selectivity(regclass, text, regclass, text, text DEFAULT '2'::text)

- **Returns:** double precision
- **Language:** c

#### _postgis_pgsql_version()

- **Returns:** text
- **Language:** sql

#### _postgis_scripts_pgsql_version()

- **Returns:** text
- **Language:** sql

#### _postgis_selectivity(tbl regclass, att_name text, geom geometry, mode text DEFAULT '2'::text)

- **Returns:** double precision
- **Language:** c

#### _postgis_stats(tbl regclass, att_name text, text DEFAULT '2'::text)

- **Returns:** text
- **Language:** c

#### _st_3ddfullywithin(geom1 geometry, geom2 geometry, double precision)

- **Returns:** boolean
- **Language:** c

#### _st_3ddwithin(geom1 geometry, geom2 geometry, double precision)

- **Returns:** boolean
- **Language:** c

#### _st_3dintersects(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_asgml(integer, geometry, integer, integer, text, text)

- **Returns:** text
- **Language:** c

#### _st_asx3d(integer, geometry, integer, integer, text)

- **Returns:** text
- **Language:** c

#### _st_bestsrid(geography)

- **Returns:** integer
- **Language:** c

#### _st_bestsrid(geography, geography)

- **Returns:** integer
- **Language:** c

#### _st_contains(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_containsproperly(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_coveredby(geog1 geography, geog2 geography)

- **Returns:** boolean
- **Language:** c

#### _st_coveredby(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_covers(geog1 geography, geog2 geography)

- **Returns:** boolean
- **Language:** c

#### _st_covers(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_crosses(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_dfullywithin(geom1 geometry, geom2 geometry, double precision)

- **Returns:** boolean
- **Language:** c

#### _st_distancetree(geography, geography)

- **Returns:** double precision
- **Language:** sql

#### _st_distancetree(geography, geography, double precision, boolean)

- **Returns:** double precision
- **Language:** c

#### _st_distanceuncached(geography, geography, double precision, boolean)

- **Returns:** double precision
- **Language:** c

#### _st_distanceuncached(geography, geography, boolean)

- **Returns:** double precision
- **Language:** sql

#### _st_distanceuncached(geography, geography)

- **Returns:** double precision
- **Language:** sql

#### _st_dwithin(geom1 geometry, geom2 geometry, double precision)

- **Returns:** boolean
- **Language:** c

#### _st_dwithin(geog1 geography, geog2 geography, tolerance double precision, use_spheroid boolean DEFAULT true)

- **Returns:** boolean
- **Language:** c

#### _st_dwithinuncached(geography, geography, double precision, boolean)

- **Returns:** boolean
- **Language:** c

#### _st_dwithinuncached(geography, geography, double precision)

- **Returns:** boolean
- **Language:** sql

#### _st_equals(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_expand(geography, double precision)

- **Returns:** geography
- **Language:** c

#### _st_geomfromgml(text, integer)

- **Returns:** geometry
- **Language:** c

#### _st_intersects(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_linecrossingdirection(line1 geometry, line2 geometry)

- **Returns:** integer
- **Language:** c

#### _st_longestline(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c

#### _st_maxdistance(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c

#### _st_orderingequals(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_overlaps(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_pointoutside(geography)

- **Returns:** geography
- **Language:** c

#### _st_sortablehash(geom geometry)

- **Returns:** bigint
- **Language:** c

#### _st_touches(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### _st_voronoi(g1 geometry, clip geometry DEFAULT NULL::geometry, tolerance double precision DEFAULT 0.0, return_polygons boolean DEFAULT true)

- **Returns:** geometry
- **Language:** c

#### _st_within(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** sql

#### addauth(text)

- **Returns:** boolean
- **Language:** plpgsql
- **Description:** args: auth_token - Adds an authorization token to be used in the current transaction.

#### addgeometrycolumn(catalog_name character varying, schema_name character varying, table_name character varying, column_name character varying, new_srid_in integer, new_type character varying, new_dim integer, use_typmod boolean DEFAULT true)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: catalog_name, schema_name, table_name, column_name, srid, type, dimension, use_typmod=true - Adds a geometry column to an existing table.

#### addgeometrycolumn(schema_name character varying, table_name character varying, column_name character varying, new_srid integer, new_type character varying, new_dim integer, use_typmod boolean DEFAULT true)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: schema_name, table_name, column_name, srid, type, dimension, use_typmod=true - Adds a geometry column to an existing table.

#### addgeometrycolumn(table_name character varying, column_name character varying, new_srid integer, new_type character varying, new_dim integer, use_typmod boolean DEFAULT true)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: table_name, column_name, srid, type, dimension, use_typmod=true - Adds a geometry column to an existing table.

#### box(box3d)

- **Returns:** box
- **Language:** c

#### box(geometry)

- **Returns:** box
- **Language:** c

#### box2d(geometry)

- **Returns:** box2d
- **Language:** c
- **Description:** args: geom - Returns a BOX2D representing the 2D extent of a geometry.

#### box2d(box3d)

- **Returns:** box2d
- **Language:** c

#### box2d_in(cstring)

- **Returns:** box2d
- **Language:** c

#### box2d_out(box2d)

- **Returns:** cstring
- **Language:** c

#### box2df_in(cstring)

- **Returns:** box2df
- **Language:** c

#### box2df_out(box2df)

- **Returns:** cstring
- **Language:** c

#### box3d(geometry)

- **Returns:** box3d
- **Language:** c
- **Description:** args: geom - Returns a BOX3D representing the 3D extent of a geometry.

#### box3d(box2d)

- **Returns:** box3d
- **Language:** c

#### box3d_in(cstring)

- **Returns:** box3d
- **Language:** c

#### box3d_out(box3d)

- **Returns:** cstring
- **Language:** c

#### box3dtobox(box3d)

- **Returns:** box
- **Language:** c

#### bytea(geography)

- **Returns:** bytea
- **Language:** c

#### bytea(geometry)

- **Returns:** bytea
- **Language:** c

#### cash_dist(money, money)

- **Returns:** money
- **Language:** c

#### checkauth(text, text)

- **Returns:** integer
- **Language:** sql
- **Description:** args: a_table_name, a_key_column_name - Creates a trigger on a table to prevent/allow updates and deletes of rows based on authorization token.

#### checkauth(text, text, text)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: a_schema_name, a_table_name, a_key_column_name - Creates a trigger on a table to prevent/allow updates and deletes of rows based on authorization token.

#### checkauthtrigger()

- **Returns:** trigger
- **Language:** c

#### contains_2d(box2df, box2df)

- **Returns:** boolean
- **Language:** c

#### contains_2d(box2df, geometry)

- **Returns:** boolean
- **Language:** c

#### contains_2d(geometry, box2df)

- **Returns:** boolean
- **Language:** sql

#### date_dist(date, date)

- **Returns:** integer
- **Language:** c

#### disablelongtransactions()

- **Returns:** text
- **Language:** plpgsql
- **Description:** Disables long transaction support.

#### dropgeometrycolumn(table_name character varying, column_name character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: table_name, column_name - Removes a geometry column from a spatial table.

#### dropgeometrycolumn(catalog_name character varying, schema_name character varying, table_name character varying, column_name character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: catalog_name, schema_name, table_name, column_name - Removes a geometry column from a spatial table.

#### dropgeometrycolumn(schema_name character varying, table_name character varying, column_name character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: schema_name, table_name, column_name - Removes a geometry column from a spatial table.

#### dropgeometrytable(table_name character varying)

- **Returns:** text
- **Language:** sql
- **Description:** args: table_name - Drops a table and all its references in geometry_columns.

#### dropgeometrytable(schema_name character varying, table_name character varying)

- **Returns:** text
- **Language:** sql
- **Description:** args: schema_name, table_name - Drops a table and all its references in geometry_columns.

#### dropgeometrytable(catalog_name character varying, schema_name character varying, table_name character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: catalog_name, schema_name, table_name - Drops a table and all its references in geometry_columns.

#### enablelongtransactions()

- **Returns:** text
- **Language:** plpgsql
- **Description:** Enables long transaction support.

#### equals(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### find_srid(character varying, character varying, character varying)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: a_schema_name, a_table_name, a_geomfield_name - Returns the SRID defined for a geometry column.

#### float4_dist(real, real)

- **Returns:** real
- **Language:** c

#### float8_dist(double precision, double precision)

- **Returns:** double precision
- **Language:** c

#### gbt_bit_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_bit_consistent(internal, bit, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_bit_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bit_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bit_same(gbtreekey_var, gbtreekey_var, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bit_union(internal, internal)

- **Returns:** gbtreekey_var
- **Language:** c

#### gbt_bool_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_bool_consistent(internal, boolean, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_bool_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_bool_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bool_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bool_same(gbtreekey2, gbtreekey2, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bool_union(internal, internal)

- **Returns:** gbtreekey2
- **Language:** c

#### gbt_bpchar_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_bpchar_consistent(internal, character, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_bytea_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_bytea_consistent(internal, bytea, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_bytea_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bytea_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bytea_same(gbtreekey_var, gbtreekey_var, internal)

- **Returns:** internal
- **Language:** c

#### gbt_bytea_union(internal, internal)

- **Returns:** gbtreekey_var
- **Language:** c

#### gbt_cash_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_cash_consistent(internal, money, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_cash_distance(internal, money, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_cash_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_cash_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_cash_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_cash_same(gbtreekey16, gbtreekey16, internal)

- **Returns:** internal
- **Language:** c

#### gbt_cash_union(internal, internal)

- **Returns:** gbtreekey16
- **Language:** c

#### gbt_date_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_date_consistent(internal, date, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_date_distance(internal, date, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_date_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_date_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_date_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_date_same(gbtreekey8, gbtreekey8, internal)

- **Returns:** internal
- **Language:** c

#### gbt_date_union(internal, internal)

- **Returns:** gbtreekey8
- **Language:** c

#### gbt_decompress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_enum_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_enum_consistent(internal, anyenum, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_enum_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_enum_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_enum_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_enum_same(gbtreekey8, gbtreekey8, internal)

- **Returns:** internal
- **Language:** c

#### gbt_enum_union(internal, internal)

- **Returns:** gbtreekey8
- **Language:** c

#### gbt_float4_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_float4_consistent(internal, real, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_float4_distance(internal, real, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_float4_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_float4_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_float4_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_float4_same(gbtreekey8, gbtreekey8, internal)

- **Returns:** internal
- **Language:** c

#### gbt_float4_union(internal, internal)

- **Returns:** gbtreekey8
- **Language:** c

#### gbt_float8_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_float8_consistent(internal, double precision, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_float8_distance(internal, double precision, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_float8_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_float8_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_float8_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_float8_same(gbtreekey16, gbtreekey16, internal)

- **Returns:** internal
- **Language:** c

#### gbt_float8_union(internal, internal)

- **Returns:** gbtreekey16
- **Language:** c

#### gbt_inet_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_inet_consistent(internal, inet, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_inet_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_inet_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_inet_same(gbtreekey16, gbtreekey16, internal)

- **Returns:** internal
- **Language:** c

#### gbt_inet_union(internal, internal)

- **Returns:** gbtreekey16
- **Language:** c

#### gbt_int2_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_int2_consistent(internal, smallint, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_int2_distance(internal, smallint, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_int2_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_int2_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int2_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int2_same(gbtreekey4, gbtreekey4, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int2_union(internal, internal)

- **Returns:** gbtreekey4
- **Language:** c

#### gbt_int4_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_int4_consistent(internal, integer, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_int4_distance(internal, integer, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_int4_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_int4_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int4_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int4_same(gbtreekey8, gbtreekey8, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int4_union(internal, internal)

- **Returns:** gbtreekey8
- **Language:** c

#### gbt_int8_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_int8_consistent(internal, bigint, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_int8_distance(internal, bigint, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_int8_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_int8_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int8_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int8_same(gbtreekey16, gbtreekey16, internal)

- **Returns:** internal
- **Language:** c

#### gbt_int8_union(internal, internal)

- **Returns:** gbtreekey16
- **Language:** c

#### gbt_intv_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_intv_consistent(internal, interval, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_intv_decompress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_intv_distance(internal, interval, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_intv_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_intv_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_intv_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_intv_same(gbtreekey32, gbtreekey32, internal)

- **Returns:** internal
- **Language:** c

#### gbt_intv_union(internal, internal)

- **Returns:** gbtreekey32
- **Language:** c

#### gbt_macad8_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad8_consistent(internal, macaddr8, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_macad8_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad8_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad8_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad8_same(gbtreekey16, gbtreekey16, internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad8_union(internal, internal)

- **Returns:** gbtreekey16
- **Language:** c

#### gbt_macad_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad_consistent(internal, macaddr, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_macad_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad_same(gbtreekey16, gbtreekey16, internal)

- **Returns:** internal
- **Language:** c

#### gbt_macad_union(internal, internal)

- **Returns:** gbtreekey16
- **Language:** c

#### gbt_numeric_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_numeric_consistent(internal, numeric, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_numeric_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_numeric_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_numeric_same(gbtreekey_var, gbtreekey_var, internal)

- **Returns:** internal
- **Language:** c

#### gbt_numeric_union(internal, internal)

- **Returns:** gbtreekey_var
- **Language:** c

#### gbt_oid_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_oid_consistent(internal, oid, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_oid_distance(internal, oid, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_oid_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_oid_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_oid_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_oid_same(gbtreekey8, gbtreekey8, internal)

- **Returns:** internal
- **Language:** c

#### gbt_oid_union(internal, internal)

- **Returns:** gbtreekey8
- **Language:** c

#### gbt_text_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_text_consistent(internal, text, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_text_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_text_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_text_same(gbtreekey_var, gbtreekey_var, internal)

- **Returns:** internal
- **Language:** c

#### gbt_text_union(internal, internal)

- **Returns:** gbtreekey_var
- **Language:** c

#### gbt_time_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_time_consistent(internal, time without time zone, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_time_distance(internal, time without time zone, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_time_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_time_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_time_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_time_same(gbtreekey16, gbtreekey16, internal)

- **Returns:** internal
- **Language:** c

#### gbt_time_union(internal, internal)

- **Returns:** gbtreekey16
- **Language:** c

#### gbt_timetz_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_timetz_consistent(internal, time with time zone, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_ts_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_ts_consistent(internal, timestamp without time zone, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_ts_distance(internal, timestamp without time zone, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_ts_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_ts_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_ts_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_ts_same(gbtreekey16, gbtreekey16, internal)

- **Returns:** internal
- **Language:** c

#### gbt_ts_union(internal, internal)

- **Returns:** gbtreekey16
- **Language:** c

#### gbt_tstz_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_tstz_consistent(internal, timestamp with time zone, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_tstz_distance(internal, timestamp with time zone, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gbt_uuid_compress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_uuid_consistent(internal, uuid, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gbt_uuid_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbt_uuid_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_uuid_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gbt_uuid_same(gbtreekey32, gbtreekey32, internal)

- **Returns:** internal
- **Language:** c

#### gbt_uuid_union(internal, internal)

- **Returns:** gbtreekey32
- **Language:** c

#### gbt_var_decompress(internal)

- **Returns:** internal
- **Language:** c

#### gbt_var_fetch(internal)

- **Returns:** internal
- **Language:** c

#### gbtreekey16_in(cstring)

- **Returns:** gbtreekey16
- **Language:** c

#### gbtreekey16_out(gbtreekey16)

- **Returns:** cstring
- **Language:** c

#### gbtreekey2_in(cstring)

- **Returns:** gbtreekey2
- **Language:** c

#### gbtreekey2_out(gbtreekey2)

- **Returns:** cstring
- **Language:** c

#### gbtreekey32_in(cstring)

- **Returns:** gbtreekey32
- **Language:** c

#### gbtreekey32_out(gbtreekey32)

- **Returns:** cstring
- **Language:** c

#### gbtreekey4_in(cstring)

- **Returns:** gbtreekey4
- **Language:** c

#### gbtreekey4_out(gbtreekey4)

- **Returns:** cstring
- **Language:** c

#### gbtreekey8_in(cstring)

- **Returns:** gbtreekey8
- **Language:** c

#### gbtreekey8_out(gbtreekey8)

- **Returns:** cstring
- **Language:** c

#### gbtreekey_var_in(cstring)

- **Returns:** gbtreekey_var
- **Language:** c

#### gbtreekey_var_out(gbtreekey_var)

- **Returns:** cstring
- **Language:** c

#### geog_brin_inclusion_add_value(internal, internal, internal, internal)

- **Returns:** boolean
- **Language:** c

#### geography(bytea)

- **Returns:** geography
- **Language:** c

#### geography(geography, integer, boolean)

- **Returns:** geography
- **Language:** c

#### geography(geometry)

- **Returns:** geography
- **Language:** c

#### geography_analyze(internal)

- **Returns:** boolean
- **Language:** c

#### geography_cmp(geography, geography)

- **Returns:** integer
- **Language:** c

#### geography_distance_knn(geography, geography)

- **Returns:** double precision
- **Language:** c

#### geography_eq(geography, geography)

- **Returns:** boolean
- **Language:** c

#### geography_ge(geography, geography)

- **Returns:** boolean
- **Language:** c

#### geography_gist_compress(internal)

- **Returns:** internal
- **Language:** c

#### geography_gist_consistent(internal, geography, integer)

- **Returns:** boolean
- **Language:** c

#### geography_gist_decompress(internal)

- **Returns:** internal
- **Language:** c

#### geography_gist_distance(internal, geography, integer)

- **Returns:** double precision
- **Language:** c

#### geography_gist_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### geography_gist_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### geography_gist_same(box2d, box2d, internal)

- **Returns:** internal
- **Language:** c

#### geography_gist_union(bytea, internal)

- **Returns:** internal
- **Language:** c

#### geography_gt(geography, geography)

- **Returns:** boolean
- **Language:** c

#### geography_in(cstring, oid, integer)

- **Returns:** geography
- **Language:** c

#### geography_le(geography, geography)

- **Returns:** boolean
- **Language:** c

#### geography_lt(geography, geography)

- **Returns:** boolean
- **Language:** c

#### geography_out(geography)

- **Returns:** cstring
- **Language:** c

#### geography_overlaps(geography, geography)

- **Returns:** boolean
- **Language:** c

#### geography_recv(internal, oid, integer)

- **Returns:** geography
- **Language:** c

#### geography_send(geography)

- **Returns:** bytea
- **Language:** c

#### geography_spgist_choose_nd(internal, internal)

- **Returns:** void
- **Language:** c

#### geography_spgist_compress_nd(internal)

- **Returns:** internal
- **Language:** c

#### geography_spgist_config_nd(internal, internal)

- **Returns:** void
- **Language:** c

#### geography_spgist_inner_consistent_nd(internal, internal)

- **Returns:** void
- **Language:** c

#### geography_spgist_leaf_consistent_nd(internal, internal)

- **Returns:** boolean
- **Language:** c

#### geography_spgist_picksplit_nd(internal, internal)

- **Returns:** void
- **Language:** c

#### geography_typmod_in(cstring[])

- **Returns:** integer
- **Language:** c

#### geography_typmod_out(integer)

- **Returns:** cstring
- **Language:** c

#### geom2d_brin_inclusion_add_value(internal, internal, internal, internal)

- **Returns:** boolean
- **Language:** c

#### geom3d_brin_inclusion_add_value(internal, internal, internal, internal)

- **Returns:** boolean
- **Language:** c

#### geom4d_brin_inclusion_add_value(internal, internal, internal, internal)

- **Returns:** boolean
- **Language:** c

#### geometry(polygon)

- **Returns:** geometry
- **Language:** c

#### geometry(box2d)

- **Returns:** geometry
- **Language:** c

#### geometry(box3d)

- **Returns:** geometry
- **Language:** c

#### geometry(text)

- **Returns:** geometry
- **Language:** c

#### geometry(geography)

- **Returns:** geometry
- **Language:** c

#### geometry(bytea)

- **Returns:** geometry
- **Language:** c

#### geometry(path)

- **Returns:** geometry
- **Language:** c

#### geometry(point)

- **Returns:** geometry
- **Language:** c

#### geometry(geometry, integer, boolean)

- **Returns:** geometry
- **Language:** c

#### geometry_above(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_analyze(internal)

- **Returns:** boolean
- **Language:** c

#### geometry_below(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_cmp(geom1 geometry, geom2 geometry)

- **Returns:** integer
- **Language:** c

#### geometry_contained_3d(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_contains(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_contains_3d(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_contains_nd(geometry, geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_distance_box(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c

#### geometry_distance_centroid(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c

#### geometry_distance_centroid_nd(geometry, geometry)

- **Returns:** double precision
- **Language:** c

#### geometry_distance_cpa(geometry, geometry)

- **Returns:** double precision
- **Language:** c

#### geometry_eq(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_ge(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_gist_compress_2d(internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_compress_nd(internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_consistent_2d(internal, geometry, integer)

- **Returns:** boolean
- **Language:** c

#### geometry_gist_consistent_nd(internal, geometry, integer)

- **Returns:** boolean
- **Language:** c

#### geometry_gist_decompress_2d(internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_decompress_nd(internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_distance_2d(internal, geometry, integer)

- **Returns:** double precision
- **Language:** c

#### geometry_gist_distance_nd(internal, geometry, integer)

- **Returns:** double precision
- **Language:** c

#### geometry_gist_penalty_2d(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_penalty_nd(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_picksplit_2d(internal, internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_picksplit_nd(internal, internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_same_2d(geom1 geometry, geom2 geometry, internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_same_nd(geometry, geometry, internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_sortsupport_2d(internal)

- **Returns:** void
- **Language:** c

#### geometry_gist_union_2d(bytea, internal)

- **Returns:** internal
- **Language:** c

#### geometry_gist_union_nd(bytea, internal)

- **Returns:** internal
- **Language:** c

#### geometry_gt(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_hash(geometry)

- **Returns:** integer
- **Language:** c

#### geometry_in(cstring)

- **Returns:** geometry
- **Language:** c

#### geometry_le(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_left(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_lt(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_out(geometry)

- **Returns:** cstring
- **Language:** c

#### geometry_overabove(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_overbelow(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_overlaps(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_overlaps_3d(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_overlaps_nd(geometry, geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_overleft(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_overright(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_recv(internal)

- **Returns:** geometry
- **Language:** c

#### geometry_right(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_same(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_same_3d(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_same_nd(geometry, geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_send(geometry)

- **Returns:** bytea
- **Language:** c

#### geometry_sortsupport(internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_choose_2d(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_choose_3d(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_choose_nd(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_compress_2d(internal)

- **Returns:** internal
- **Language:** c

#### geometry_spgist_compress_3d(internal)

- **Returns:** internal
- **Language:** c

#### geometry_spgist_compress_nd(internal)

- **Returns:** internal
- **Language:** c

#### geometry_spgist_config_2d(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_config_3d(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_config_nd(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_inner_consistent_2d(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_inner_consistent_3d(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_inner_consistent_nd(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_leaf_consistent_2d(internal, internal)

- **Returns:** boolean
- **Language:** c

#### geometry_spgist_leaf_consistent_3d(internal, internal)

- **Returns:** boolean
- **Language:** c

#### geometry_spgist_leaf_consistent_nd(internal, internal)

- **Returns:** boolean
- **Language:** c

#### geometry_spgist_picksplit_2d(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_picksplit_3d(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_spgist_picksplit_nd(internal, internal)

- **Returns:** void
- **Language:** c

#### geometry_typmod_in(cstring[])

- **Returns:** integer
- **Language:** c

#### geometry_typmod_out(integer)

- **Returns:** cstring
- **Language:** c

#### geometry_within(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### geometry_within_nd(geometry, geometry)

- **Returns:** boolean
- **Language:** c

#### geometrytype(geography)

- **Returns:** text
- **Language:** c

#### geometrytype(geometry)

- **Returns:** text
- **Language:** c
- **Description:** args: geomA - Returns the type of a geometry as text.

#### geomfromewkb(bytea)

- **Returns:** geometry
- **Language:** c

#### geomfromewkt(text)

- **Returns:** geometry
- **Language:** c

#### get_proj4_from_srid(integer)

- **Returns:** text
- **Language:** plpgsql

#### gettransactionid()

- **Returns:** xid
- **Language:** c

#### gidx_in(cstring)

- **Returns:** gidx
- **Language:** c

#### gidx_out(gidx)

- **Returns:** cstring
- **Language:** c

#### gin_extract_query_trgm(text, internal, smallint, internal, internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gin_extract_value_trgm(text, internal)

- **Returns:** internal
- **Language:** c

#### gin_trgm_consistent(internal, smallint, text, integer, internal, internal, internal, internal)

- **Returns:** boolean
- **Language:** c

#### gin_trgm_triconsistent(internal, smallint, text, integer, internal, internal, internal)

- **Returns:** "char"
- **Language:** c

#### gserialized_gist_joinsel_2d(internal, oid, internal, smallint)

- **Returns:** double precision
- **Language:** c

#### gserialized_gist_joinsel_nd(internal, oid, internal, smallint)

- **Returns:** double precision
- **Language:** c

#### gserialized_gist_sel_2d(internal, oid, internal, integer)

- **Returns:** double precision
- **Language:** c

#### gserialized_gist_sel_nd(internal, oid, internal, integer)

- **Returns:** double precision
- **Language:** c

#### gtrgm_compress(internal)

- **Returns:** internal
- **Language:** c

#### gtrgm_consistent(internal, text, smallint, oid, internal)

- **Returns:** boolean
- **Language:** c

#### gtrgm_decompress(internal)

- **Returns:** internal
- **Language:** c

#### gtrgm_distance(internal, text, smallint, oid, internal)

- **Returns:** double precision
- **Language:** c

#### gtrgm_in(cstring)

- **Returns:** gtrgm
- **Language:** c

#### gtrgm_options(internal)

- **Returns:** void
- **Language:** c

#### gtrgm_out(gtrgm)

- **Returns:** cstring
- **Language:** c

#### gtrgm_penalty(internal, internal, internal)

- **Returns:** internal
- **Language:** c

#### gtrgm_picksplit(internal, internal)

- **Returns:** internal
- **Language:** c

#### gtrgm_same(gtrgm, gtrgm, internal)

- **Returns:** internal
- **Language:** c

#### gtrgm_union(internal, internal)

- **Returns:** gtrgm
- **Language:** c

#### int2_dist(smallint, smallint)

- **Returns:** smallint
- **Language:** c

#### int4_dist(integer, integer)

- **Returns:** integer
- **Language:** c

#### int8_dist(bigint, bigint)

- **Returns:** bigint
- **Language:** c

#### interval_dist(interval, interval)

- **Returns:** interval
- **Language:** c

#### is_contained_2d(geometry, box2df)

- **Returns:** boolean
- **Language:** sql

#### is_contained_2d(box2df, box2df)

- **Returns:** boolean
- **Language:** c

#### is_contained_2d(box2df, geometry)

- **Returns:** boolean
- **Language:** c

#### json(geometry)

- **Returns:** json
- **Language:** c

#### jsonb(geometry)

- **Returns:** jsonb
- **Language:** c

#### lockrow(text, text, text)

- **Returns:** integer
- **Language:** sql
- **Description:** args: a_table_name, a_row_key, an_auth_token - Sets lock/authorization for a row in a table.

#### lockrow(text, text, text, timestamp without time zone)

- **Returns:** integer
- **Language:** sql
- **Description:** args: a_table_name, a_row_key, an_auth_token, expire_dt - Sets lock/authorization for a row in a table.

#### lockrow(text, text, text, text, timestamp without time zone)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: a_schema_name, a_table_name, a_row_key, an_auth_token, expire_dt - Sets lock/authorization for a row in a table.

#### lockrow(text, text, text, text)

- **Returns:** integer
- **Language:** sql

#### longtransactionsenabled()

- **Returns:** boolean
- **Language:** plpgsql

#### oid_dist(oid, oid)

- **Returns:** oid
- **Language:** c

#### overlaps_2d(geometry, box2df)

- **Returns:** boolean
- **Language:** sql

#### overlaps_2d(box2df, box2df)

- **Returns:** boolean
- **Language:** c

#### overlaps_2d(box2df, geometry)

- **Returns:** boolean
- **Language:** c

#### overlaps_geog(gidx, gidx)

- **Returns:** boolean
- **Language:** c

#### overlaps_geog(geography, gidx)

- **Returns:** boolean
- **Language:** sql

#### overlaps_geog(gidx, geography)

- **Returns:** boolean
- **Language:** c

#### overlaps_nd(geometry, gidx)

- **Returns:** boolean
- **Language:** sql

#### overlaps_nd(gidx, geometry)

- **Returns:** boolean
- **Language:** c

#### overlaps_nd(gidx, gidx)

- **Returns:** boolean
- **Language:** c

#### path(geometry)

- **Returns:** path
- **Language:** c

#### pgis_asflatgeobuf_finalfn(internal)

- **Returns:** bytea
- **Language:** c

#### pgis_asflatgeobuf_transfn(internal, anyelement, boolean)

- **Returns:** internal
- **Language:** c

#### pgis_asflatgeobuf_transfn(internal, anyelement)

- **Returns:** internal
- **Language:** c

#### pgis_asflatgeobuf_transfn(internal, anyelement, boolean, text)

- **Returns:** internal
- **Language:** c

#### pgis_asgeobuf_finalfn(internal)

- **Returns:** bytea
- **Language:** c

#### pgis_asgeobuf_transfn(internal, anyelement, text)

- **Returns:** internal
- **Language:** c

#### pgis_asgeobuf_transfn(internal, anyelement)

- **Returns:** internal
- **Language:** c

#### pgis_asmvt_combinefn(internal, internal)

- **Returns:** internal
- **Language:** c

#### pgis_asmvt_deserialfn(bytea, internal)

- **Returns:** internal
- **Language:** c

#### pgis_asmvt_finalfn(internal)

- **Returns:** bytea
- **Language:** c

#### pgis_asmvt_serialfn(internal)

- **Returns:** bytea
- **Language:** c

#### pgis_asmvt_transfn(internal, anyelement, text)

- **Returns:** internal
- **Language:** c

#### pgis_asmvt_transfn(internal, anyelement)

- **Returns:** internal
- **Language:** c

#### pgis_asmvt_transfn(internal, anyelement, text, integer, text, text)

- **Returns:** internal
- **Language:** c

#### pgis_asmvt_transfn(internal, anyelement, text, integer, text)

- **Returns:** internal
- **Language:** c

#### pgis_asmvt_transfn(internal, anyelement, text, integer)

- **Returns:** internal
- **Language:** c

#### pgis_geometry_accum_transfn(internal, geometry, double precision)

- **Returns:** internal
- **Language:** c

#### pgis_geometry_accum_transfn(internal, geometry)

- **Returns:** internal
- **Language:** c

#### pgis_geometry_accum_transfn(internal, geometry, double precision, integer)

- **Returns:** internal
- **Language:** c

#### pgis_geometry_clusterintersecting_finalfn(internal)

- **Returns:** geometry[]
- **Language:** c

#### pgis_geometry_clusterwithin_finalfn(internal)

- **Returns:** geometry[]
- **Language:** c

#### pgis_geometry_collect_finalfn(internal)

- **Returns:** geometry
- **Language:** c

#### pgis_geometry_makeline_finalfn(internal)

- **Returns:** geometry
- **Language:** c

#### pgis_geometry_polygonize_finalfn(internal)

- **Returns:** geometry
- **Language:** c

#### pgis_geometry_union_parallel_combinefn(internal, internal)

- **Returns:** internal
- **Language:** c

#### pgis_geometry_union_parallel_deserialfn(bytea, internal)

- **Returns:** internal
- **Language:** c

#### pgis_geometry_union_parallel_finalfn(internal)

- **Returns:** geometry
- **Language:** c

#### pgis_geometry_union_parallel_serialfn(internal)

- **Returns:** bytea
- **Language:** c

#### pgis_geometry_union_parallel_transfn(internal, geometry, double precision)

- **Returns:** internal
- **Language:** c

#### pgis_geometry_union_parallel_transfn(internal, geometry)

- **Returns:** internal
- **Language:** c

#### point(geometry)

- **Returns:** point
- **Language:** c

#### polygon(geometry)

- **Returns:** polygon
- **Language:** c

#### populate_geometry_columns(tbl_oid oid, use_typmod boolean DEFAULT true)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: relation_oid, use_typmod=true - Ensures geometry columns are defined with type modifiers or have appropriate spatial constraints.

#### populate_geometry_columns(use_typmod boolean DEFAULT true)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: use_typmod=true - Ensures geometry columns are defined with type modifiers or have appropriate spatial constraints.

#### postgis_addbbox(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA - Add bounding box to the geometry.

#### postgis_cache_bbox()

- **Returns:** trigger
- **Language:** c

#### postgis_constraint_dims(geomschema text, geomtable text, geomcolumn text)

- **Returns:** integer
- **Language:** sql

#### postgis_constraint_srid(geomschema text, geomtable text, geomcolumn text)

- **Returns:** integer
- **Language:** sql

#### postgis_constraint_type(geomschema text, geomtable text, geomcolumn text)

- **Returns:** character varying
- **Language:** sql

#### postgis_dropbbox(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA - Drop the bounding box cache from the geometry.

#### postgis_extensions_upgrade()

- **Returns:** text
- **Language:** plpgsql
- **Description:** Packages and upgrades PostGIS extensions (e.g. postgis_raster,postgis_topology, postgis_sfcgal) to latest available version.

#### postgis_full_version()

- **Returns:** text
- **Language:** plpgsql
- **Description:** Reports full PostGIS version and build configuration infos.

#### postgis_geos_noop(geometry)

- **Returns:** geometry
- **Language:** c

#### postgis_geos_version()

- **Returns:** text
- **Language:** c
- **Description:** Returns the version number of the GEOS library.

#### postgis_getbbox(geometry)

- **Returns:** box2d
- **Language:** c

#### postgis_hasbbox(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: geomA - Returns TRUE if the bbox of this geometry is cached, FALSE otherwise.

#### postgis_index_supportfn(internal)

- **Returns:** internal
- **Language:** c

#### postgis_lib_build_date()

- **Returns:** text
- **Language:** c
- **Description:** Returns build date of the PostGIS library.

#### postgis_lib_revision()

- **Returns:** text
- **Language:** c

#### postgis_lib_version()

- **Returns:** text
- **Language:** c
- **Description:** Returns the version number of the PostGIS library.

#### postgis_libjson_version()

- **Returns:** text
- **Language:** c

#### postgis_liblwgeom_version()

- **Returns:** text
- **Language:** c
- **Description:** Returns the version number of the liblwgeom library. This should match the version of PostGIS.

#### postgis_libprotobuf_version()

- **Returns:** text
- **Language:** c

#### postgis_libxml_version()

- **Returns:** text
- **Language:** c
- **Description:** Returns the version number of the libxml2 library.

#### postgis_noop(geometry)

- **Returns:** geometry
- **Language:** c

#### postgis_proj_version()

- **Returns:** text
- **Language:** c
- **Description:** Returns the version number of the PROJ4 library.

#### postgis_scripts_build_date()

- **Returns:** text
- **Language:** sql
- **Description:** Returns build date of the PostGIS scripts.

#### postgis_scripts_installed()

- **Returns:** text
- **Language:** sql
- **Description:** Returns version of the PostGIS scripts installed in this database.

#### postgis_scripts_released()

- **Returns:** text
- **Language:** c
- **Description:** Returns the version number of the postgis.sql script released with the installed PostGIS lib.

#### postgis_svn_version()

- **Returns:** text
- **Language:** sql

#### postgis_transform_geometry(geom geometry, text, text, integer)

- **Returns:** geometry
- **Language:** c

#### postgis_type_name(geomname character varying, coord_dimension integer, use_new_name boolean DEFAULT true)

- **Returns:** character varying
- **Language:** sql

#### postgis_typmod_dims(integer)

- **Returns:** integer
- **Language:** c

#### postgis_typmod_srid(integer)

- **Returns:** integer
- **Language:** c

#### postgis_typmod_type(integer)

- **Returns:** text
- **Language:** c

#### postgis_version()

- **Returns:** text
- **Language:** c
- **Description:** Returns PostGIS version number and compile-time options.

#### postgis_wagyu_version()

- **Returns:** text
- **Language:** c
- **Description:** Returns the version number of the internal Wagyu library.

#### set_limit(real)

- **Returns:** real
- **Language:** c

#### show_limit()

- **Returns:** real
- **Language:** c

#### show_trgm(text)

- **Returns:** text[]
- **Language:** c

#### similarity(text, text)

- **Returns:** real
- **Language:** c

#### similarity_dist(text, text)

- **Returns:** real
- **Language:** c

#### similarity_op(text, text)

- **Returns:** boolean
- **Language:** c

#### spheroid_in(cstring)

- **Returns:** spheroid
- **Language:** c

#### spheroid_out(spheroid)

- **Returns:** cstring
- **Language:** c

#### st_3dclosestpoint(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2 - Returns the 3D point on g1 that is closest to g2. This is the first point of the 3D shortest line.

#### st_3ddfullywithin(geom1 geometry, geom2 geometry, double precision)

- **Returns:** boolean
- **Language:** c

#### st_3ddistance(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1, g2 - Returns the 3D cartesian minimum distance (based on spatial ref) between two geometries in projected units.

#### st_3ddwithin(geom1 geometry, geom2 geometry, double precision)

- **Returns:** boolean
- **Language:** c

#### st_3dintersects(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_3dlength(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_3dlinestring - Returns the 3D length of a linear geometry.

#### st_3dlineinterpolatepoint(geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: a_linestring, a_fraction - Returns a point interpolated along a 3D line at a fractional location.

#### st_3dlongestline(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2 - Returns the 3D longest line between two geometries

#### st_3dmakebox(geom1 geometry, geom2 geometry)

- **Returns:** box3d
- **Language:** c
- **Description:** args: point3DLowLeftBottom, point3DUpRightTop - Creates a BOX3D defined by two 3D point geometries.

#### st_3dmaxdistance(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1, g2 - Returns the 3D cartesian maximum distance (based on spatial ref) between two geometries in projected units.

#### st_3dperimeter(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geomA - Returns the 3D perimeter of a polygonal geometry.

#### st_3dshortestline(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2 - Returns the 3D shortest line between two geometries

#### st_addmeasure(geometry, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom_mline, measure_start, measure_end - Interpolates measures along a linear geometry.

#### st_addpoint(geom1 geometry, geom2 geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring, point, position = -1 - Add a point to a LineString.

#### st_addpoint(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring, point - Add a point to a LineString.

#### st_affine(geometry, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, a, b, c, d, e, f, g, h, i, xoff, yoff, zoff - Apply a 3D affine transformation to a geometry.

#### st_affine(geometry, double precision, double precision, double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, a, b, d, e, xoff, yoff - Apply a 3D affine transformation to a geometry.

#### st_angle(line1 geometry, line2 geometry)

- **Returns:** double precision
- **Language:** sql
- **Description:** args: line1, line2 - Returns the angle between two vectors defined by 3 or 4 points, or 2 lines.

#### st_angle(pt1 geometry, pt2 geometry, pt3 geometry, pt4 geometry DEFAULT '0101000000000000000000F87F000000000000F87F'::geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: point1, point2, point3, point4 - Returns the angle between two vectors defined by 3 or 4 points, or 2 lines.

#### st_area(geog geography, use_spheroid boolean DEFAULT true)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geog, use_spheroid=true - Returns the area of a polygonal geometry.

#### st_area(text)

- **Returns:** double precision
- **Language:** sql

#### st_area(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1 - Returns the area of a polygonal geometry.

#### st_area2d(geometry)

- **Returns:** double precision
- **Language:** c

#### st_asbinary(geography)

- **Returns:** bytea
- **Language:** c

#### st_asbinary(geometry)

- **Returns:** bytea
- **Language:** c

#### st_asbinary(geometry, text)

- **Returns:** bytea
- **Language:** c

#### st_asbinary(geography, text)

- **Returns:** bytea
- **Language:** c

#### st_asencodedpolyline(geom geometry, nprecision integer DEFAULT 5)

- **Returns:** text
- **Language:** c

#### st_asewkb(geometry)

- **Returns:** bytea
- **Language:** c

#### st_asewkb(geometry, text)

- **Returns:** bytea
- **Language:** c

#### st_asewkt(geography, integer)

- **Returns:** text
- **Language:** c

#### st_asewkt(geography)

- **Returns:** text
- **Language:** c

#### st_asewkt(geometry)

- **Returns:** text
- **Language:** c

#### st_asewkt(geometry, integer)

- **Returns:** text
- **Language:** c

#### st_asewkt(text)

- **Returns:** text
- **Language:** sql

#### st_asgeojson(geog geography, maxdecimaldigits integer DEFAULT 9, options integer DEFAULT 0)

- **Returns:** text
- **Language:** c

#### st_asgeojson(text)

- **Returns:** text
- **Language:** sql

#### st_asgeojson(geom geometry, maxdecimaldigits integer DEFAULT 9, options integer DEFAULT 8)

- **Returns:** text
- **Language:** c

#### st_asgeojson(r record, geom_column text DEFAULT ''::text, maxdecimaldigits integer DEFAULT 9, pretty_bool boolean DEFAULT false)

- **Returns:** text
- **Language:** c

#### st_asgml(geog geography, maxdecimaldigits integer DEFAULT 15, options integer DEFAULT 0, nprefix text DEFAULT 'gml'::text, id text DEFAULT ''::text)

- **Returns:** text
- **Language:** c

#### st_asgml(geom geometry, maxdecimaldigits integer DEFAULT 15, options integer DEFAULT 0)

- **Returns:** text
- **Language:** c

#### st_asgml(version integer, geom geometry, maxdecimaldigits integer DEFAULT 15, options integer DEFAULT 0, nprefix text DEFAULT NULL::text, id text DEFAULT NULL::text)

- **Returns:** text
- **Language:** c

#### st_asgml(text)

- **Returns:** text
- **Language:** sql

#### st_asgml(version integer, geog geography, maxdecimaldigits integer DEFAULT 15, options integer DEFAULT 0, nprefix text DEFAULT 'gml'::text, id text DEFAULT ''::text)

- **Returns:** text
- **Language:** c

#### st_ashexewkb(geometry)

- **Returns:** text
- **Language:** c

#### st_ashexewkb(geometry, text)

- **Returns:** text
- **Language:** c

#### st_askml(geom geometry, maxdecimaldigits integer DEFAULT 15, nprefix text DEFAULT ''::text)

- **Returns:** text
- **Language:** c

#### st_askml(text)

- **Returns:** text
- **Language:** sql

#### st_askml(geog geography, maxdecimaldigits integer DEFAULT 15, nprefix text DEFAULT ''::text)

- **Returns:** text
- **Language:** c

#### st_aslatlontext(geom geometry, tmpl text DEFAULT ''::text)

- **Returns:** text
- **Language:** c

#### st_asmarc21(geom geometry, format text DEFAULT 'hdddmmss'::text)

- **Returns:** text
- **Language:** c

#### st_asmvtgeom(geom geometry, bounds box2d, extent integer DEFAULT 4096, buffer integer DEFAULT 256, clip_geom boolean DEFAULT true)

- **Returns:** geometry
- **Language:** c

#### st_assvg(geom geometry, rel integer DEFAULT 0, maxdecimaldigits integer DEFAULT 15)

- **Returns:** text
- **Language:** c

#### st_assvg(text)

- **Returns:** text
- **Language:** sql

#### st_assvg(geog geography, rel integer DEFAULT 0, maxdecimaldigits integer DEFAULT 15)

- **Returns:** text
- **Language:** c

#### st_astext(geometry)

- **Returns:** text
- **Language:** c

#### st_astext(geometry, integer)

- **Returns:** text
- **Language:** c

#### st_astext(geography)

- **Returns:** text
- **Language:** c

#### st_astext(text)

- **Returns:** text
- **Language:** sql

#### st_astext(geography, integer)

- **Returns:** text
- **Language:** c

#### st_astwkb(geom geometry[], ids bigint[], prec integer DEFAULT NULL::integer, prec_z integer DEFAULT NULL::integer, prec_m integer DEFAULT NULL::integer, with_sizes boolean DEFAULT NULL::boolean, with_boxes boolean DEFAULT NULL::boolean)

- **Returns:** bytea
- **Language:** c

#### st_astwkb(geom geometry, prec integer DEFAULT NULL::integer, prec_z integer DEFAULT NULL::integer, prec_m integer DEFAULT NULL::integer, with_sizes boolean DEFAULT NULL::boolean, with_boxes boolean DEFAULT NULL::boolean)

- **Returns:** bytea
- **Language:** c

#### st_asx3d(geom geometry, maxdecimaldigits integer DEFAULT 15, options integer DEFAULT 0)

- **Returns:** text
- **Language:** sql

#### st_azimuth(geog1 geography, geog2 geography)

- **Returns:** double precision
- **Language:** c
- **Description:** args: origin, target - Returns the north-based azimuth of a line between two points.

#### st_azimuth(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: origin, target - Returns the north-based azimuth of a line between two points.

#### st_bdmpolyfromtext(text, integer)

- **Returns:** geometry
- **Language:** plpgsql

#### st_bdpolyfromtext(text, integer)

- **Returns:** geometry
- **Language:** plpgsql

#### st_boundary(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA - Returns the boundary of a geometry.

#### st_boundingdiagonal(geom geometry, fits boolean DEFAULT false)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, fits=false - Returns the diagonal of a geometrys bounding box.

#### st_box2dfromgeohash(text, integer DEFAULT NULL::integer)

- **Returns:** box2d
- **Language:** c

#### st_buffer(geography, double precision)

- **Returns:** geography
- **Language:** sql

#### st_buffer(geom geometry, radius double precision, quadsegs integer)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: g1, radius_of_buffer, num_seg_quarter_circle - Computes a geometry covering all points within a given distance from a geometry.

#### st_buffer(geom geometry, radius double precision, options text DEFAULT ''::text)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, radius_of_buffer, buffer_style_parameters = ' - Computes a geometry covering all points within a given distance from a geometry.

#### st_buffer(text, double precision, integer)

- **Returns:** geometry
- **Language:** sql

#### st_buffer(geography, double precision, integer)

- **Returns:** geography
- **Language:** sql
- **Description:** args: g1, radius_of_buffer, num_seg_quarter_circle - Computes a geometry covering all points within a given distance from a geometry.

#### st_buffer(geography, double precision, text)

- **Returns:** geography
- **Language:** sql
- **Description:** args: g1, radius_of_buffer, buffer_style_parameters - Computes a geometry covering all points within a given distance from a geometry.

#### st_buffer(text, double precision, text)

- **Returns:** geometry
- **Language:** sql

#### st_buffer(text, double precision)

- **Returns:** geometry
- **Language:** sql

#### st_buildarea(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Creates a polygonal geometry formed by the linework of a geometry.

#### st_centroid(geography, use_spheroid boolean DEFAULT true)

- **Returns:** geography
- **Language:** c
- **Description:** args: g1, use_spheroid=true - Returns the geometric center of a geometry.

#### st_centroid(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1 - Returns the geometric center of a geometry.

#### st_centroid(text)

- **Returns:** geometry
- **Language:** sql

#### st_chaikinsmoothing(geometry, integer DEFAULT 1, boolean DEFAULT false)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, nIterations = 1, preserveEndPoints = false - Returns a smoothed version of a geometry, using the Chaikin algorithm

#### st_cleangeometry(geometry)

- **Returns:** geometry
- **Language:** c

#### st_clipbybox2d(geom geometry, box box2d)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, box - Computes the portion of a geometry falling within a rectangle.

#### st_closestpoint(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom1, geom2 - Returns the 2D point on g1 that is closest to g2. This is the first point of the shortest line from one geometry to the other.

#### st_closestpointofapproach(geometry, geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: track1, track2 - Returns a measure at the closest point of approach of two trajectories.

#### st_clusterintersecting(geometry[])

- **Returns:** geometry[]
- **Language:** c

#### st_clusterwithin(geometry[], double precision)

- **Returns:** geometry[]
- **Language:** c

#### st_collect(geometry[])

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1_array - Creates a GeometryCollection or Multi* geometry from a set of geometries.

#### st_collect(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2 - Creates a GeometryCollection or Multi* geometry from a set of geometries.

#### st_collectionextract(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: collection - Given a geometry collection, returns a multi-geometry containing only elements of a specified type.

#### st_collectionextract(geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: collection, type - Given a geometry collection, returns a multi-geometry containing only elements of a specified type.

#### st_collectionhomogenize(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: collection - Returns the simplest representation of a geometry collection.

#### st_combinebbox(box3d, geometry)

- **Returns:** box3d
- **Language:** c

#### st_combinebbox(box2d, geometry)

- **Returns:** box2d
- **Language:** c

#### st_combinebbox(box3d, box3d)

- **Returns:** box3d
- **Language:** c

#### st_concavehull(param_geom geometry, param_pctconvex double precision, param_allow_holes boolean DEFAULT false)

- **Returns:** geometry
- **Language:** c
- **Description:** args: param_geom, param_pctconvex, param_allow_holes = false - Computes a possibly concave geometry that encloses all input geometry vertices

#### st_contains(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_containsproperly(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_convexhull(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA - Computes the convex hull of a geometry.

#### st_coorddim(geometry geometry)

- **Returns:** smallint
- **Language:** c
- **Description:** args: geomA - Return the coordinate dimension of a geometry.

#### st_coveredby(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_coveredby(text, text)

- **Returns:** boolean
- **Language:** sql

#### st_coveredby(geog1 geography, geog2 geography)

- **Returns:** boolean
- **Language:** c

#### st_covers(geog1 geography, geog2 geography)

- **Returns:** boolean
- **Language:** c

#### st_covers(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_covers(text, text)

- **Returns:** boolean
- **Language:** sql

#### st_cpawithin(geometry, geometry, double precision)

- **Returns:** boolean
- **Language:** c
- **Description:** args: track1, track2, dist - Tests if the closest point of approach of two trajectoriesis within the specified distance.

#### st_crosses(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_curvetoline(geom geometry, tol double precision DEFAULT 32, toltype integer DEFAULT 0, flags integer DEFAULT 0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: curveGeom, tolerance, tolerance_type, flags - Converts a geometry containing curves to a linear geometry.

#### st_delaunaytriangles(g1 geometry, tolerance double precision DEFAULT 0.0, flags integer DEFAULT 0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, tolerance, flags - Returns the Delaunay triangulation of the vertices of a geometry.

#### st_dfullywithin(geom1 geometry, geom2 geometry, double precision)

- **Returns:** boolean
- **Language:** c

#### st_difference(geom1 geometry, geom2 geometry, gridsize double precision DEFAULT '-1.0'::numeric)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, geomB, gridSize = -1 - Computes a geometry representing the part of geometry A that does not intersect geometry B.

#### st_dimension(geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: g - Returns the topological dimension of a geometry.

#### st_disjoint(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_distance(geog1 geography, geog2 geography, use_spheroid boolean DEFAULT true)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geog1, geog2, use_spheroid=true - Returns the distance between two geometry or geography values.

#### st_distance(text, text)

- **Returns:** double precision
- **Language:** sql

#### st_distance(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1, g2 - Returns the distance between two geometry or geography values.

#### st_distancecpa(geometry, geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: track1, track2 - Returns the distance between the closest point of approach of two trajectories.

#### st_distancesphere(geom1 geometry, geom2 geometry, radius double precision)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geomlonlatA, geomlonlatB, radius=6371008 - Returns minimum distance in meters between two lon/lat geometries using a spherical earth model.

#### st_distancesphere(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** sql

#### st_distancespheroid(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c

#### st_distancespheroid(geom1 geometry, geom2 geometry, spheroid)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geomlonlatA, geomlonlatB, measurement_spheroid=WGS84 - Returns the minimum distance between two lon/lat geometries using a spheroidal earth model.

#### st_dump(geometry)

- **Returns:** SETOF geometry_dump
- **Language:** c
- **Description:** args: g1 - Returns a set of geometry_dump rows for the components of a geometry.

#### st_dumppoints(geometry)

- **Returns:** SETOF geometry_dump
- **Language:** c
- **Description:** args: geom - Returns a set of geometry_dump rows for the coordinates in a geometry.

#### st_dumprings(geometry)

- **Returns:** SETOF geometry_dump
- **Language:** c
- **Description:** args: a_polygon - Returns a set of geometry_dump rows for the exterior and interior rings of a Polygon.

#### st_dumpsegments(geometry)

- **Returns:** SETOF geometry_dump
- **Language:** c
- **Description:** args: geom - Returns a set of geometry_dump rows for the segments in a geometry.

#### st_dwithin(geog1 geography, geog2 geography, tolerance double precision, use_spheroid boolean DEFAULT true)

- **Returns:** boolean
- **Language:** c

#### st_dwithin(text, text, double precision)

- **Returns:** boolean
- **Language:** sql

#### st_dwithin(geom1 geometry, geom2 geometry, double precision)

- **Returns:** boolean
- **Language:** c

#### st_endpoint(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g - Returns the last point of a LineString or CircularLineString.

#### st_envelope(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1 - Returns a geometry representing the bounding box of a geometry.

#### st_equals(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_estimatedextent(text, text, text)

- **Returns:** box2d
- **Language:** c
- **Description:** args: schema_name, table_name, geocolumn_name - Returns the estimated extent of a spatial table.

#### st_estimatedextent(text, text, text, boolean)

- **Returns:** box2d
- **Language:** c
- **Description:** args: schema_name, table_name, geocolumn_name, parent_only - Returns the estimated extent of a spatial table.

#### st_estimatedextent(text, text)

- **Returns:** box2d
- **Language:** c
- **Description:** args: table_name, geocolumn_name - Returns the estimated extent of a spatial table.

#### st_expand(geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, units_to_expand - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(geom geometry, dx double precision, dy double precision, dz double precision DEFAULT 0, dm double precision DEFAULT 0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, dx, dy, dz=0, dm=0 - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(box box3d, dx double precision, dy double precision, dz double precision DEFAULT 0)

- **Returns:** box3d
- **Language:** c
- **Description:** args: box, dx, dy, dz=0 - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(box3d, double precision)

- **Returns:** box3d
- **Language:** c
- **Description:** args: box, units_to_expand - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(box box2d, dx double precision, dy double precision)

- **Returns:** box2d
- **Language:** c
- **Description:** args: box, dx, dy - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(box2d, double precision)

- **Returns:** box2d
- **Language:** c
- **Description:** args: box, units_to_expand - Returns a bounding box expanded from another bounding box or a geometry.

#### st_exteriorring(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: a_polygon - Returns a LineString representing the exterior ring of a Polygon.

#### st_filterbym(geometry, double precision, double precision DEFAULT NULL::double precision, boolean DEFAULT false)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, min, max = null, returnM = false - Removes vertices based on their M value

#### st_findextent(text, text, text)

- **Returns:** box2d
- **Language:** plpgsql

#### st_findextent(text, text)

- **Returns:** box2d
- **Language:** plpgsql

#### st_flipcoordinates(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Returns a version of a geometry with X and Y axis flipped.

#### st_force2d(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA - Force the geometries into a "2-dimensional mode".

#### st_force3d(geom geometry, zvalue double precision DEFAULT 0.0)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, Zvalue = 0.0 - Force the geometries into XYZ mode. This is an alias for ST_Force3DZ.

#### st_force3dm(geom geometry, mvalue double precision DEFAULT 0.0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, Mvalue = 0.0 - Force the geometries into XYM mode.

#### st_force3dz(geom geometry, zvalue double precision DEFAULT 0.0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, Zvalue = 0.0 - Force the geometries into XYZ mode.

#### st_force4d(geom geometry, zvalue double precision DEFAULT 0.0, mvalue double precision DEFAULT 0.0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, Zvalue = 0.0, Mvalue = 0.0 - Force the geometries into XYZM mode.

#### st_forcecollection(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA - Convert the geometry into a GEOMETRYCOLLECTION.

#### st_forcecurve(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g - Upcast a geometry into its curved type, if applicable.

#### st_forcepolygonccw(geometry)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geom - Orients all exterior rings counter-clockwise and all interior rings clockwise.

#### st_forcepolygoncw(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Orients all exterior rings clockwise and all interior rings counter-clockwise.

#### st_forcerhr(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g - Force the orientation of the vertices in a polygon to follow the Right-Hand-Rule.

#### st_forcesfs(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA - Force the geometries to use SFS 1.1 geometry types only.

#### st_forcesfs(geometry, version text)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, version - Force the geometries to use SFS 1.1 geometry types only.

#### st_frechetdistance(geom1 geometry, geom2 geometry, double precision DEFAULT '-1'::integer)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1, g2, densifyFrac = -1 - Returns the Fréchet distance between two geometries.

#### st_fromflatgeobuf(anyelement, bytea)

- **Returns:** SETOF anyelement
- **Language:** c

#### st_fromflatgeobuftotable(text, text, bytea)

- **Returns:** void
- **Language:** c

#### st_generatepoints(area geometry, npoints integer, seed integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g, npoints, seed - Generates random points contained in a Polygon or MultiPolygon.

#### st_generatepoints(area geometry, npoints integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g, npoints - Generates random points contained in a Polygon or MultiPolygon.

#### st_geogfromtext(text)

- **Returns:** geography
- **Language:** c

#### st_geogfromwkb(bytea)

- **Returns:** geography
- **Language:** c

#### st_geographyfromtext(text)

- **Returns:** geography
- **Language:** c

#### st_geohash(geog geography, maxchars integer DEFAULT 0)

- **Returns:** text
- **Language:** c

#### st_geohash(geom geometry, maxchars integer DEFAULT 0)

- **Returns:** text
- **Language:** c

#### st_geomcollfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_geomcollfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_geomcollfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_geomcollfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_geometricmedian(g geometry, tolerance double precision DEFAULT NULL::double precision, max_iter integer DEFAULT 10000, fail_if_not_converged boolean DEFAULT false)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, tolerance = NULL, max_iter = 10000, fail_if_not_converged = false - Returns the geometric median of a MultiPoint.

#### st_geometryfromtext(text, integer)

- **Returns:** geometry
- **Language:** c

#### st_geometryfromtext(text)

- **Returns:** geometry
- **Language:** c

#### st_geometryn(geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, n - Return an element of a geometry collection.

#### st_geometrytype(geometry)

- **Returns:** text
- **Language:** c
- **Description:** args: g1 - Returns the SQL-MM type of a geometry as text.

#### st_geomfromewkb(bytea)

- **Returns:** geometry
- **Language:** c

#### st_geomfromewkt(text)

- **Returns:** geometry
- **Language:** c

#### st_geomfromgeohash(text, integer DEFAULT NULL::integer)

- **Returns:** geometry
- **Language:** sql

#### st_geomfromgeojson(json)

- **Returns:** geometry
- **Language:** sql

#### st_geomfromgeojson(text)

- **Returns:** geometry
- **Language:** c

#### st_geomfromgeojson(jsonb)

- **Returns:** geometry
- **Language:** sql

#### st_geomfromgml(text, integer)

- **Returns:** geometry
- **Language:** c

#### st_geomfromgml(text)

- **Returns:** geometry
- **Language:** sql

#### st_geomfromkml(text)

- **Returns:** geometry
- **Language:** c

#### st_geomfrommarc21(marc21xml text)

- **Returns:** geometry
- **Language:** c

#### st_geomfromtext(text, integer)

- **Returns:** geometry
- **Language:** c

#### st_geomfromtext(text)

- **Returns:** geometry
- **Language:** c

#### st_geomfromtwkb(bytea)

- **Returns:** geometry
- **Language:** c

#### st_geomfromwkb(bytea)

- **Returns:** geometry
- **Language:** c

#### st_geomfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_gmltosql(text)

- **Returns:** geometry
- **Language:** sql

#### st_gmltosql(text, integer)

- **Returns:** geometry
- **Language:** c

#### st_hasarc(geometry geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: geomA - Tests if a geometry contains a circular arc

#### st_hausdorffdistance(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1, g2 - Returns the Hausdorff distance between two geometries.

#### st_hausdorffdistance(geom1 geometry, geom2 geometry, double precision)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1, g2, densifyFrac - Returns the Hausdorff distance between two geometries.

#### st_hexagon(size double precision, cell_i integer, cell_j integer, origin geometry DEFAULT '010100000000000000000000000000000000000000'::geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: size, cell_i, cell_j, origin - Returns a single hexagon, using the provided edge size and cell coordinate within the hexagon grid space.

#### st_hexagongrid(size double precision, bounds geometry, OUT geom geometry, OUT i integer, OUT j integer)

- **Returns:** SETOF record
- **Language:** c
- **Description:** args: size, bounds - Returns a set of hexagons and cell indices that completely cover the bounds of the geometry argument.

#### st_interiorringn(geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: a_polygon, n - Returns the Nth interior ring (hole) of a Polygon.

#### st_interpolatepoint(line geometry, point geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: linear_geom_with_measure, point - Returns the interpolated measure of a geometry closest to a point.

#### st_intersection(text, text)

- **Returns:** geometry
- **Language:** sql

#### st_intersection(geom1 geometry, geom2 geometry, gridsize double precision DEFAULT '-1'::integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, geomB, gridSize = -1 - Computes a geometry representing the shared portion of geometries A and B.

#### st_intersection(geography, geography)

- **Returns:** geography
- **Language:** sql
- **Description:** args: geogA, geogB - Computes a geometry representing the shared portion of geometries A and B.

#### st_intersects(text, text)

- **Returns:** boolean
- **Language:** sql

#### st_intersects(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_intersects(geog1 geography, geog2 geography)

- **Returns:** boolean
- **Language:** c

#### st_isclosed(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: g - Tests if a LineStringss start and end points are coincident. For a PolyhedralSurface tests if it is closed (volumetric).

#### st_iscollection(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: g - Tests if a geometry is a geometry collection type.

#### st_isempty(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: geomA - Tests if a geometry is empty.

#### st_ispolygonccw(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: geom - Tests if Polygons have exterior rings oriented counter-clockwise and interior rings oriented clockwise.

#### st_ispolygoncw(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: geom - Tests if Polygons have exterior rings oriented clockwise and interior rings oriented counter-clockwise.

#### st_isring(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: g - Tests if a LineString is closed and simple.

#### st_issimple(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: geomA - Tests if a geometry has no points of self-intersection or self-tangency.

#### st_isvalid(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: g - Tests if a geometry is well-formed in 2D.

#### st_isvalid(geometry, integer)

- **Returns:** boolean
- **Language:** sql
- **Description:** args: g, flags - Tests if a geometry is well-formed in 2D.

#### st_isvaliddetail(geom geometry, flags integer DEFAULT 0)

- **Returns:** valid_detail
- **Language:** c
- **Description:** args: geom, flags - Returns a valid_detail row stating if a geometry is valid or if not a reason and a location.

#### st_isvalidreason(geometry, integer)

- **Returns:** text
- **Language:** sql
- **Description:** args: geomA, flags - Returns text stating if a geometry is valid, or a reason for invalidity.

#### st_isvalidreason(geometry)

- **Returns:** text
- **Language:** c
- **Description:** args: geomA - Returns text stating if a geometry is valid, or a reason for invalidity.

#### st_isvalidtrajectory(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: line - Tests if the geometry is a valid trajectory.

#### st_length(geog geography, use_spheroid boolean DEFAULT true)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geog, use_spheroid=true - Returns the 2D length of a linear geometry.

#### st_length(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_2dlinestring - Returns the 2D length of a linear geometry.

#### st_length(text)

- **Returns:** double precision
- **Language:** sql

#### st_length2d(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_2dlinestring - Returns the 2D length of a linear geometry. Alias for ST_Length

#### st_length2dspheroid(geometry, spheroid)

- **Returns:** double precision
- **Language:** c

#### st_lengthspheroid(geometry, spheroid)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_geometry, a_spheroid - Returns the 2D or 3D length/perimeter of a lon/lat geometry on a spheroid.

#### st_letters(letters text, font json DEFAULT NULL::json)

- **Returns:** geometry
- **Language:** plpgsql
- **Description:** args:  letters,  font - Returns the input letters rendered as geometry with a default start position at the origin and default text height of 100.

#### st_linecrossingdirection(line1 geometry, line2 geometry)

- **Returns:** integer
- **Language:** c

#### st_linefromencodedpolyline(txtin text, nprecision integer DEFAULT 5)

- **Returns:** geometry
- **Language:** c

#### st_linefrommultipoint(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: aMultiPoint - Creates a LineString from a MultiPoint geometry.

#### st_linefromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_linefromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_linefromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_linefromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_lineinterpolatepoint(geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: a_linestring, a_fraction - Returns a point interpolated along a line at a fractional location.

#### st_lineinterpolatepoints(geometry, double precision, repeat boolean DEFAULT true)

- **Returns:** geometry
- **Language:** c
- **Description:** args: a_linestring, a_fraction, repeat - Returns points interpolated along a line at a fractional interval.

#### st_linelocatepoint(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_linestring, a_point - Returns the fractional location of the closest point on a line to a point.

#### st_linemerge(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: amultilinestring - Return the lines formed by sewing together a MultiLineString.

#### st_linemerge(geometry, boolean)

- **Returns:** geometry
- **Language:** c
- **Description:** args: amultilinestring, directed - Return the lines formed by sewing together a MultiLineString.

#### st_linestringfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_linestringfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_linesubstring(geometry, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: a_linestring, startfraction, endfraction - Returns the part of a line between two fractional locations.

#### st_linetocurve(geometry geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomANoncircular - Converts a linear geometry to a curved geometry.

#### st_locatealong(geometry geometry, measure double precision, leftrightoffset double precision DEFAULT 0.0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom_with_measure, measure, offset = 0 - Returns the point(s) on a geometry that match a measure value.

#### st_locatebetween(geometry geometry, frommeasure double precision, tomeasure double precision, leftrightoffset double precision DEFAULT 0.0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, measure_start, measure_end, offset = 0 - Returns the portions of a geometry that match a measure range.

#### st_locatebetweenelevations(geometry geometry, fromelevation double precision, toelevation double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, elevation_start, elevation_end - Returns the portions of a geometry that lie in an elevation (Z) range.

#### st_longestline(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: g1, g2 - Returns the 2D longest line between two geometries.

#### st_m(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_point - Returns the M coordinate of a Point.

#### st_makebox2d(geom1 geometry, geom2 geometry)

- **Returns:** box2d
- **Language:** c
- **Description:** args: pointLowLeft, pointUpRight - Creates a BOX2D defined by two 2D point geometries.

#### st_makeenvelope(double precision, double precision, double precision, double precision, integer DEFAULT 0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: xmin, ymin, xmax, ymax, srid=unknown - Creates a rectangular Polygon from minimum and maximum coordinates.

#### st_makeline(geometry[])

- **Returns:** geometry
- **Language:** c
- **Description:** args: geoms_array - Creates a LineString from Point, MultiPoint, or LineString geometries.

#### st_makeline(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom1, geom2 - Creates a LineString from Point, MultiPoint, or LineString geometries.

#### st_makepoint(double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, z, m - Creates a 2D, 3DZ or 4D Point.

#### st_makepoint(double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y - Creates a 2D, 3DZ or 4D Point.

#### st_makepoint(double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, z - Creates a 2D, 3DZ or 4D Point.

#### st_makepointm(double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, m - Creates a Point from X, Y and M values.

#### st_makepolygon(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring - Creates a Polygon from a shell and optional list of holes.

#### st_makepolygon(geometry, geometry[])

- **Returns:** geometry
- **Language:** c
- **Description:** args: outerlinestring, interiorlinestrings - Creates a Polygon from a shell and optional list of holes.

#### st_makevalid(geom geometry, params text)

- **Returns:** geometry
- **Language:** c
- **Description:** args: input, params - Attempts to make an invalid geometry valid without losing vertices.

#### st_makevalid(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: input - Attempts to make an invalid geometry valid without losing vertices.

#### st_maxdistance(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** sql
- **Description:** args: g1, g2 - Returns the 2D largest distance between two geometries in projected units.

#### st_maximuminscribedcircle(geometry, OUT center geometry, OUT nearest geometry, OUT radius double precision)

- **Returns:** record
- **Language:** c
- **Description:** args: geom - Computes the largest circle contained within a geometry.

#### st_memsize(geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: geomA - Returns the amount of memory space a geometry takes.

#### st_minimumboundingcircle(inputgeom geometry, segs_per_quarter integer DEFAULT 48)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, num_segs_per_qt_circ=48 - Returns the smallest circle polygon that contains a geometry.

#### st_minimumboundingradius(geometry, OUT center geometry, OUT radius double precision)

- **Returns:** record
- **Language:** c
- **Description:** args: geom - Returns the center point and radius of the smallest circle that contains a geometry.

#### st_minimumclearance(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g - Returns the minimum clearance of a geometry, a measure of a geometrys robustness.

#### st_minimumclearanceline(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g - Returns the two-point LineString spanning a geometrys minimum clearance.

#### st_mlinefromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_mlinefromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_mlinefromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_mlinefromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_mpointfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_mpointfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_mpointfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_mpointfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_mpolyfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_mpolyfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_mpolyfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_mpolyfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_multi(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Return the geometry as a MULTI* geometry.

#### st_multilinefromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_multilinestringfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_multilinestringfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_multipointfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_multipointfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_multipointfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_multipolyfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_multipolyfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_multipolygonfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_multipolygonfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_ndims(geometry)

- **Returns:** smallint
- **Language:** c
- **Description:** args: g1 - Returns the coordinate dimension of a geometry.

#### st_node(g geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Nodes a collection of lines.

#### st_normalize(geom geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Return the geometry in its canonical form.

#### st_npoints(geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: g1 - Returns the number of points (vertices) in a geometry.

#### st_nrings(geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: geomA - Returns the number of rings in a polygonal geometry.

#### st_numgeometries(geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: geom - Returns the number of elements in a geometry collection.

#### st_numinteriorring(geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: a_polygon - Returns the number of interior rings (holes) of a Polygon. Aias for ST_NumInteriorRings

#### st_numinteriorrings(geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: a_polygon - Returns the number of interior rings (holes) of a Polygon.

#### st_numpatches(geometry)

- **Returns:** integer
- **Language:** sql
- **Description:** args: g1 - Return the number of faces on a Polyhedral Surface. Will return null for non-polyhedral geometries.

#### st_numpoints(geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: g1 - Returns the number of points in a LineString or CircularString.

#### st_offsetcurve(line geometry, distance double precision, params text DEFAULT ''::text)

- **Returns:** geometry
- **Language:** c
- **Description:** args: line, signed_distance, style_parameters=' - Returns an offset line at a given distance and side from an input line.

#### st_orderingequals(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_orientedenvelope(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Returns a minimum-area rectangle containing a geometry.

#### st_overlaps(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_patchn(geometry, integer)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, n - Returns the Nth geometry (face) of a PolyhedralSurface.

#### st_perimeter(geog geography, use_spheroid boolean DEFAULT true)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geog, use_spheroid=true - Returns the length of the boundary of a polygonal geometry or geography.

#### st_perimeter(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1 - Returns the length of the boundary of a polygonal geometry or geography.

#### st_perimeter2d(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geomA - Returns the 2D perimeter of a polygonal geometry. Alias for ST_Perimeter.

#### st_point(double precision, double precision, srid integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, srid=unknown - Creates a Point with X, Y and SRID values.

#### st_point(double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y - Creates a Point with X, Y and SRID values.

#### st_pointfromgeohash(text, integer DEFAULT NULL::integer)

- **Returns:** geometry
- **Language:** c

#### st_pointfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_pointfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_pointfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_pointfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_pointinsidecircle(geometry, double precision, double precision, double precision)

- **Returns:** boolean
- **Language:** c

#### st_pointm(xcoordinate double precision, ycoordinate double precision, mcoordinate double precision, srid integer DEFAULT 0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, m, srid=unknown - Creates a Point with X, Y, M and SRID values.

#### st_pointn(geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: a_linestring, n - Returns the Nth point in the first LineString or circular LineString in a geometry.

#### st_pointonsurface(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1 - Computes a point guaranteed to lie in a polygon, or on a geometry.

#### st_points(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Returns a MultiPoint containing the coordinates of a geometry.

#### st_pointz(xcoordinate double precision, ycoordinate double precision, zcoordinate double precision, srid integer DEFAULT 0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, z, srid=unknown - Creates a Point with X, Y, Z and SRID values.

#### st_pointzm(xcoordinate double precision, ycoordinate double precision, zcoordinate double precision, mcoordinate double precision, srid integer DEFAULT 0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, z, m, srid=unknown - Creates a Point with X, Y, Z, M and SRID values.

#### st_polyfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_polyfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_polyfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_polyfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_polygon(geometry, integer)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: lineString, srid - Creates a Polygon from a LineString with a specified SRID.

#### st_polygonfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_polygonfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_polygonfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_polygonfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_polygonize(geometry[])

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom_array - Computes a collection of polygons formed from the linework of a set of geometries.

#### st_project(geog geography, distance double precision, azimuth double precision)

- **Returns:** geography
- **Language:** c
- **Description:** args: g1, distance, azimuth - Returns a point projected from a start point by a distance and bearing (azimuth).

#### st_quantizecoordinates(g geometry, prec_x integer, prec_y integer DEFAULT NULL::integer, prec_z integer DEFAULT NULL::integer, prec_m integer DEFAULT NULL::integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g, prec_x, prec_y, prec_z, prec_m - Sets least significant bits of coordinates to zero

#### st_reduceprecision(geom geometry, gridsize double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g, gridsize - Returns a valid geometry with points rounded to a grid tolerance.

#### st_relate(geom1 geometry, geom2 geometry, text)

- **Returns:** boolean
- **Language:** c

#### st_relate(geom1 geometry, geom2 geometry, integer)

- **Returns:** text
- **Language:** c

#### st_relate(geom1 geometry, geom2 geometry)

- **Returns:** text
- **Language:** c

#### st_relatematch(text, text)

- **Returns:** boolean
- **Language:** c

#### st_removepoint(geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring, offset - Remove a point from a linestring.

#### st_removerepeatedpoints(geom geometry, tolerance double precision DEFAULT 0.0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, tolerance - Returns a version of a geometry with duplicate points removed.

#### st_reverse(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1 - Return the geometry with vertex order reversed.

#### st_rotate(geometry, double precision, geometry)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, rotRadians, pointOrigin - Rotates a geometry about an origin point.

#### st_rotate(geometry, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, rotRadians, x0, y0 - Rotates a geometry about an origin point.

#### st_rotate(geometry, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, rotRadians - Rotates a geometry about an origin point.

#### st_rotatex(geometry, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, rotRadians - Rotates a geometry about the X axis.

#### st_rotatey(geometry, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, rotRadians - Rotates a geometry about the Y axis.

#### st_rotatez(geometry, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, rotRadians - Rotates a geometry about the Z axis.

#### st_scale(geometry, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, XFactor, YFactor - Scales a geometry by given factors.

#### st_scale(geometry, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, XFactor, YFactor, ZFactor - Scales a geometry by given factors.

#### st_scale(geometry, geometry, origin geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, factor, origin - Scales a geometry by given factors.

#### st_scale(geometry, geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, factor - Scales a geometry by given factors.

#### st_scroll(geometry, geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring, point - Change start point of a closed LineString.

#### st_segmentize(geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, max_segment_length - Return a modified geometry/geography having no segment longer than the given distance.

#### st_segmentize(geog geography, max_segment_length double precision)

- **Returns:** geography
- **Language:** c
- **Description:** args: geog, max_segment_length - Return a modified geometry/geography having no segment longer than the given distance.

#### st_seteffectivearea(geometry, double precision DEFAULT '-1'::integer, integer DEFAULT 1)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, threshold = 0, set_area = 1 - Sets the effective area for each vertex, using the Visvalingam-Whyatt algorithm.

#### st_setpoint(geometry, integer, geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring, zerobasedposition, point - Replace point of a linestring with a given point.

#### st_setsrid(geom geometry, srid integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, srid - Set the SRID on a geometry.

#### st_setsrid(geog geography, srid integer)

- **Returns:** geography
- **Language:** c

#### st_sharedpaths(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: lineal1, lineal2 - Returns a collection containing paths shared by the two input linestrings/multilinestrings.

#### st_shiftlongitude(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Shifts the longitude coordinates of a geometry between -180..180 and 0..360.

#### st_shortestline(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom1, geom2 - Returns the 2D shortest line between two geometries

#### st_simplify(geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, tolerance - Returns a simplified version of a geometry, using the Douglas-Peucker algorithm.

#### st_simplify(geometry, double precision, boolean)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, tolerance, preserveCollapsed - Returns a simplified version of a geometry, using the Douglas-Peucker algorithm.

#### st_simplifypolygonhull(geom geometry, vertex_fraction double precision, is_outer boolean DEFAULT true)

- **Returns:** geometry
- **Language:** c
- **Description:** args: param_geom, vertex_fraction, is_outer = true - Computes a simplifed topology-preserving outer or inner hull of a polygonal geometry.

#### st_simplifypreservetopology(geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, tolerance - Returns a simplified and valid version of a geometry, using the Douglas-Peucker algorithm.

#### st_simplifyvw(geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, tolerance - Returns a simplified version of a geometry, using the Visvalingam-Whyatt algorithm

#### st_snap(geom1 geometry, geom2 geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: input, reference, tolerance - Snap segments and vertices of input geometry to vertices of a reference geometry.

#### st_snaptogrid(geom1 geometry, geom2 geometry, double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, pointOrigin, sizeX, sizeY, sizeZ, sizeM - Snap all points of the input geometry to a regular grid.

#### st_snaptogrid(geometry, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, sizeX, sizeY - Snap all points of the input geometry to a regular grid.

#### st_snaptogrid(geometry, double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, originX, originY, sizeX, sizeY - Snap all points of the input geometry to a regular grid.

#### st_snaptogrid(geometry, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, size - Snap all points of the input geometry to a regular grid.

#### st_split(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: input, blade - Returns a collection of geometries created by splitting a geometry by another geometry.

#### st_square(size double precision, cell_i integer, cell_j integer, origin geometry DEFAULT '010100000000000000000000000000000000000000'::geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: size, cell_i, cell_j, origin - Returns a single square, using the provided edge size and cell coordinate within the square grid space.

#### st_squaregrid(size double precision, bounds geometry, OUT geom geometry, OUT i integer, OUT j integer)

- **Returns:** SETOF record
- **Language:** c
- **Description:** args: size, bounds - Returns a set of grid squares and cell indices that completely cover the bounds of the geometry argument.

#### st_srid(geog geography)

- **Returns:** integer
- **Language:** c

#### st_srid(geom geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: g1 - Returns the spatial reference identifier for a geometry.

#### st_startpoint(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA - Returns the first point of a LineString.

#### st_subdivide(geom geometry, maxvertices integer DEFAULT 256, gridsize double precision DEFAULT '-1.0'::numeric)

- **Returns:** SETOF geometry
- **Language:** c
- **Description:** args: geom, max_vertices=256, gridSize = -1 - Computes a rectilinear subdivision of a geometry.

#### st_summary(geography)

- **Returns:** text
- **Language:** c
- **Description:** args: g - Returns a text summary of the contents of a geometry.

#### st_summary(geometry)

- **Returns:** text
- **Language:** c
- **Description:** args: g - Returns a text summary of the contents of a geometry.

#### st_swapordinates(geom geometry, ords cstring)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, ords - Returns a version of the given geometry with given ordinate values swapped.

#### st_symdifference(geom1 geometry, geom2 geometry, gridsize double precision DEFAULT '-1.0'::numeric)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, geomB, gridSize = -1 - Computes a geometry representing the portions of geometries A and B that do not intersect.

#### st_symmetricdifference(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** sql

#### st_tileenvelope(zoom integer, x integer, y integer, bounds geometry DEFAULT '0102000020110F00000200000093107C45F81B73C193107C45F81B73C193107C45F81B734193107C45F81B7341'::geometry, margin double precision DEFAULT 0.0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: tileZoom, tileX, tileY, bounds=SRID=3857;LINESTRING(-20037508.342789 -20037508.342789,20037508.342789 20037508.342789), margin=0.0 - Creates a rectangular Polygon in Web Mercator (SRID:3857) using the XYZ tile system.

#### st_touches(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_transform(geom geometry, from_proj text, to_srid integer)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geom, from_proj, to_srid - Return a new geometry with coordinates transformed to a different spatial reference system.

#### st_transform(geom geometry, to_proj text)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geom, to_proj - Return a new geometry with coordinates transformed to a different spatial reference system.

#### st_transform(geom geometry, from_proj text, to_proj text)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geom, from_proj, to_proj - Return a new geometry with coordinates transformed to a different spatial reference system.

#### st_transform(geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, srid - Return a new geometry with coordinates transformed to a different spatial reference system.

#### st_translate(geometry, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: g1, deltax, deltay - Translates a geometry by given offsets.

#### st_translate(geometry, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: g1, deltax, deltay, deltaz - Translates a geometry by given offsets.

#### st_transscale(geometry, double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, deltaX, deltaY, XFactor, YFactor - Translates and scales a geometry by given offsets and factors.

#### st_triangulatepolygon(g1 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom - Computes the constrained Delaunay triangulation of polygons

#### st_unaryunion(geometry, gridsize double precision DEFAULT '-1.0'::numeric)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, gridSize = -1 - Computes the union of the components of a single geometry.

#### st_union(geom1 geometry, geom2 geometry, gridsize double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2, gridSize - Computes a geometry representing the point-set union of the input geometries.

#### st_union(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2 - Computes a geometry representing the point-set union of the input geometries.

#### st_union(geometry[])

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1_array - Computes a geometry representing the point-set union of the input geometries.

#### st_voronoilines(g1 geometry, tolerance double precision DEFAULT 0.0, extend_to geometry DEFAULT NULL::geometry)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: g1, tolerance, extend_to - Returns the boundaries of the Voronoi diagram of the vertices of a geometry.

#### st_voronoipolygons(g1 geometry, tolerance double precision DEFAULT 0.0, extend_to geometry DEFAULT NULL::geometry)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: g1, tolerance, extend_to - Returns the cells of the Voronoi diagram of the vertices of a geometry.

#### st_within(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_wkbtosql(wkb bytea)

- **Returns:** geometry
- **Language:** c

#### st_wkttosql(text)

- **Returns:** geometry
- **Language:** c

#### st_wrapx(geom geometry, wrap double precision, move double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, wrap, move - Wrap a geometry around an X value.

#### st_x(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_point - Returns the X coordinate of a Point.

#### st_xmax(box3d)

- **Returns:** double precision
- **Language:** c
- **Description:** args: aGeomorBox2DorBox3D - Returns the X maxima of a 2D or 3D bounding box or a geometry.

#### st_xmin(box3d)

- **Returns:** double precision
- **Language:** c
- **Description:** args: aGeomorBox2DorBox3D - Returns the X minima of a 2D or 3D bounding box or a geometry.

#### st_y(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_point - Returns the Y coordinate of a Point.

#### st_ymax(box3d)

- **Returns:** double precision
- **Language:** c
- **Description:** args: aGeomorBox2DorBox3D - Returns the Y maxima of a 2D or 3D bounding box or a geometry.

#### st_ymin(box3d)

- **Returns:** double precision
- **Language:** c
- **Description:** args: aGeomorBox2DorBox3D - Returns the Y minima of a 2D or 3D bounding box or a geometry.

#### st_z(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_point - Returns the Z coordinate of a Point.

#### st_zmax(box3d)

- **Returns:** double precision
- **Language:** c
- **Description:** args: aGeomorBox2DorBox3D - Returns the Z maxima of a 2D or 3D bounding box or a geometry.

#### st_zmflag(geometry)

- **Returns:** smallint
- **Language:** c
- **Description:** args: geomA - Returns a code indicating the ZM coordinate dimension of a geometry.

#### st_zmin(box3d)

- **Returns:** double precision
- **Language:** c
- **Description:** args: aGeomorBox2DorBox3D - Returns the Z minima of a 2D or 3D bounding box or a geometry.

#### strict_word_similarity(text, text)

- **Returns:** real
- **Language:** c

#### strict_word_similarity_commutator_op(text, text)

- **Returns:** boolean
- **Language:** c

#### strict_word_similarity_dist_commutator_op(text, text)

- **Returns:** real
- **Language:** c

#### strict_word_similarity_dist_op(text, text)

- **Returns:** real
- **Language:** c

#### strict_word_similarity_op(text, text)

- **Returns:** boolean
- **Language:** c

#### text(geometry)

- **Returns:** text
- **Language:** c

#### time_dist(time without time zone, time without time zone)

- **Returns:** interval
- **Language:** c

#### ts_dist(timestamp without time zone, timestamp without time zone)

- **Returns:** interval
- **Language:** c

#### tstz_dist(timestamp with time zone, timestamp with time zone)

- **Returns:** interval
- **Language:** c

#### unlockrows(text)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: auth_token - Removes all locks held by an authorization token.

#### updategeometrysrid(catalogn_name character varying, schema_name character varying, table_name character varying, column_name character varying, new_srid_in integer)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: catalog_name, schema_name, table_name, column_name, srid - Updates the SRID of all features in a geometry column, and the table metadata.

#### updategeometrysrid(character varying, character varying, character varying, integer)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: schema_name, table_name, column_name, srid - Updates the SRID of all features in a geometry column, and the table metadata.

#### updategeometrysrid(character varying, character varying, integer)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: table_name, column_name, srid - Updates the SRID of all features in a geometry column, and the table metadata.

#### word_similarity(text, text)

- **Returns:** real
- **Language:** c

#### word_similarity_commutator_op(text, text)

- **Returns:** boolean
- **Language:** c

#### word_similarity_dist_commutator_op(text, text)

- **Returns:** real
- **Language:** c

#### word_similarity_dist_op(text, text)

- **Returns:** real
- **Language:** c

#### word_similarity_op(text, text)

- **Returns:** boolean
- **Language:** c

---

## Schema: `topology`

**Description:** PostGIS Topology schema

### Schema Statistics

- **Tables:** 2
- **Total Rows:** 0
- **Columns:** 13
- **Views:** 0
- **Relationships:** 0
- **Indexes:** 4
- **Triggers:** 0
- **Functions:** 103
- **Custom Types:** 0

### Tables

| Table | Rows | Columns | Size |
|-------|------|---------|------|
| layer | 0 | 8 | 24 kB |
| topology | 0 | 5 | 24 kB |

#### topology.layer

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| topology_id | integer | ✗ | - | - |
| layer_id | integer | ✗ | - | - |
| schema_name | character varying | ✗ | - | - |
| table_name | character varying | ✗ | - | - |
| feature_column | character varying | ✗ | - | - |
| feature_type | integer | ✗ | - | - |
| level | integer | ✗ | 0 | - |
| child_id | integer | ✓ | - | - |

**Constraints:**
- `layer_pkey` (PRIMARY KEY)
- `layer_schema_name_table_name_feature_column_key` (UNIQUE)
- `layer_topology_id_fkey` (FOREIGN KEY)

#### topology.topology

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('topology_id_seq'::... | - |
| name | character varying | ✗ | - | - |
| srid | integer | ✗ | - | - |
| precision | double precision | ✗ | - | - |
| hasz | boolean | ✗ | false | - |

**Constraints:**
- `topology_name_key` (UNIQUE)
- `topology_pkey` (PRIMARY KEY)

### Functions

#### _asgmledge(edge_id integer, start_node integer, end_node integer, line geometry, visitedtable regclass, nsprefix_in text, prec integer, options integer, idprefix text, gmlver integer)

- **Returns:** text
- **Language:** plpgsql

#### _asgmlface(toponame text, face_id integer, visitedtable regclass, nsprefix_in text, prec integer, options integer, idprefix text, gmlver integer)

- **Returns:** text
- **Language:** plpgsql

#### _asgmlnode(id integer, point geometry, nsprefix_in text, prec integer, options integer, idprefix text, gmlver integer)

- **Returns:** text
- **Language:** plpgsql

#### _checkedgelinking(curedge_edge_id integer, prevedge_edge_id integer, prevedge_next_left_edge integer, prevedge_next_right_edge integer)

- **Returns:** validatetopology_returntype
- **Language:** plpgsql

#### _st_adjacentedges(atopology character varying, anode integer, anedge integer)

- **Returns:** integer[]
- **Language:** plpgsql

#### _st_mintolerance(ageom geometry)

- **Returns:** double precision
- **Language:** sql

#### _st_mintolerance(atopology character varying, ageom geometry)

- **Returns:** double precision
- **Language:** plpgsql

#### _validatetopologyedgelinking(bbox geometry DEFAULT NULL::geometry)

- **Returns:** SETOF validatetopology_returntype
- **Language:** plpgsql

#### _validatetopologygetfaceshellmaximaledgering(atopology character varying, aface integer)

- **Returns:** geometry
- **Language:** plpgsql

#### _validatetopologygetringedges(starting_edge integer)

- **Returns:** integer[]
- **Language:** plpgsql

#### _validatetopologyrings(bbox geometry DEFAULT NULL::geometry)

- **Returns:** SETOF validatetopology_returntype
- **Language:** plpgsql

#### addedge(atopology character varying, aline geometry)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: toponame, aline - Adds a linestring edge to the edge table and associated start and end points to the point nodes table of the specified topology schema using the specified linestring geometry and returns the edgeid of the new (or existing) edge.

#### addface(atopology character varying, apoly geometry, force_new boolean DEFAULT false)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: toponame, apolygon, force_new=false - Registers a face primitive to a topology and gets its identifier.

#### addnode(atopology character varying, apoint geometry, allowedgesplitting boolean DEFAULT false, setcontainingface boolean DEFAULT false)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: toponame, apoint, allowEdgeSplitting=false, computeContainingFace=false - Adds a point node to the node table in the specified topology schema and returns the nodeid of new node. If point already exists as node, the existing nodeid is returned.

#### addtopogeometrycolumn(character varying, character varying, character varying, character varying, character varying)

- **Returns:** integer
- **Language:** sql
- **Description:** args: topology_name, schema_name, table_name, column_name, feature_type - Adds a topogeometry column to an existing table, registers this new column as a layer in topology.layer and returns the new layer_id.

#### addtopogeometrycolumn(toponame character varying, schema character varying, tbl character varying, col character varying, ltype character varying, child integer)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: topology_name, schema_name, table_name, column_name, feature_type, child_layer - Adds a topogeometry column to an existing table, registers this new column as a layer in topology.layer and returns the new layer_id.

#### addtosearchpath(a_schema_name character varying)

- **Returns:** text
- **Language:** plpgsql

#### asgml(tg topogeometry, nsprefix_in text, precision_in integer, options_in integer, visitedtable regclass, idprefix text, gmlver integer)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: tg, nsprefix_in, precision, options, visitedTable, idprefix, gmlversion - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, nsprefix text, prec integer, options integer, vis regclass)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, nsprefix_in, precision, options, visitedTable - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, visitedtable regclass, nsprefix text)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, visitedTable, nsprefix - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, visitedtable regclass)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, visitedTable - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, nsprefix text)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, nsprefix_in - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, nsprefix text, prec integer, opts integer)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, nsprefix_in, precision, options - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, nsprefix text, prec integer, options integer, visitedtable regclass, idprefix text)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, nsprefix_in, precision, options, visitedTable, idprefix - Returns the GML representation of a topogeometry.

#### astopojson(tg topogeometry, edgemaptable regclass)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: tg, edgeMapTable - Returns the TopoJSON representation of a topogeometry.

#### cleartopogeom(tg topogeometry)

- **Returns:** topogeometry
- **Language:** plpgsql
- **Description:** args: topogeom - Clears the content of a topo geometry.

#### copytopology(atopology character varying, newtopo character varying)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: existing_topology_name, new_name - Makes a copy of a topology structure (nodes, edges, faces, layers and TopoGeometries).

#### createtopogeom(toponame character varying, tg_type integer, layer_id integer)

- **Returns:** topogeometry
- **Language:** sql
- **Description:** args: toponame, tg_type, layer_id - Creates a new topo geometry object from topo element array - tg_type: 1:[multi]point, 2:[multi]line, 3:[multi]poly, 4:collection

#### createtopogeom(toponame character varying, tg_type integer, layer_id integer, tg_objs topoelementarray)

- **Returns:** topogeometry
- **Language:** plpgsql
- **Description:** args: toponame, tg_type, layer_id, tg_objs - Creates a new topo geometry object from topo element array - tg_type: 1:[multi]point, 2:[multi]line, 3:[multi]poly, 4:collection

#### createtopology(atopology character varying, srid integer, prec double precision, hasz boolean)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: topology_schema_name, srid, prec, hasz - Creates a new topology schema and registers this new schema in the topology.topology table.

#### createtopology(toponame character varying, srid integer, prec double precision)

- **Returns:** integer
- **Language:** sql
- **Description:** args: topology_schema_name, srid, prec - Creates a new topology schema and registers this new schema in the topology.topology table.

#### createtopology(character varying, integer)

- **Returns:** integer
- **Language:** sql
- **Description:** args: topology_schema_name, srid - Creates a new topology schema and registers this new schema in the topology.topology table.

#### createtopology(character varying)

- **Returns:** integer
- **Language:** sql
- **Description:** args: topology_schema_name - Creates a new topology schema and registers this new schema in the topology.topology table.

#### droptopogeometrycolumn(schema character varying, tbl character varying, col character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: schema_name, table_name, column_name - Drops the topogeometry column from the table named table_name in schema schema_name and unregisters the columns from topology.layer table.

#### droptopology(atopology character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: topology_schema_name - Use with caution: Drops a topology schema and deletes its reference from topology.topology table and references to tables in that schema from the geometry_columns table.

#### equals(tg1 topogeometry, tg2 topogeometry)

- **Returns:** boolean
- **Language:** plpgsql
- **Description:** args: tg1, tg2 - Returns true if two topogeometries are composed of the same topology primitives.

#### findlayer(topology_id integer, layer_id integer)

- **Returns:** layer
- **Language:** sql
- **Description:** args: topology_id, layer_id - Returns a topology.layer record by different means.

#### findlayer(layer_table regclass, feature_column name)

- **Returns:** layer
- **Language:** sql
- **Description:** args: layer_table, feature_column - Returns a topology.layer record by different means.

#### findlayer(schema_name name, table_name name, feature_column name)

- **Returns:** layer
- **Language:** sql
- **Description:** args: schema_name, table_name, feature_column - Returns a topology.layer record by different means.

#### findlayer(tg topogeometry)

- **Returns:** layer
- **Language:** sql
- **Description:** args: tg - Returns a topology.layer record by different means.

#### findtopology(regclass, name)

- **Returns:** topology
- **Language:** sql
- **Description:** args: layerTable, layerColumn - Returns a topology record by different means.

#### findtopology(topogeometry)

- **Returns:** topology
- **Language:** sql
- **Description:** args: topogeom - Returns a topology record by different means.

#### findtopology(name, name, name)

- **Returns:** topology
- **Language:** sql
- **Description:** args: layerSchema, layerTable, layerColumn - Returns a topology record by different means.

#### findtopology(integer)

- **Returns:** topology
- **Language:** sql
- **Description:** args: id - Returns a topology record by different means.

#### findtopology(text)

- **Returns:** topology
- **Language:** sql
- **Description:** args: topoName - Returns a topology record by different means.

#### geometry(topogeom topogeometry)

- **Returns:** geometry
- **Language:** plpgsql

#### geometrytype(tg topogeometry)

- **Returns:** text
- **Language:** sql

#### getedgebypoint(atopology character varying, apoint geometry, tol1 double precision)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, apoint, tol1 - Finds the edge-id of an edge that intersects a given point.

#### getfacebypoint(atopology character varying, apoint geometry, tol1 double precision)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: atopology, apoint, tol1 - Finds face intersecting a given point.

#### getfacecontainingpoint(atopology text, apoint geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, apoint - Finds the face containing a point.

#### getnodebypoint(atopology character varying, apoint geometry, tol1 double precision)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, apoint, tol1 - Finds the node-id of a node at a point location.

#### getnodeedges(atopology character varying, anode integer)

- **Returns:** SETOF getfaceedges_returntype
- **Language:** plpgsql
- **Description:** args: atopology, anode - Returns an ordered set of edges incident to the given node.

#### getringedges(atopology character varying, anedge integer, maxedges integer DEFAULT NULL::integer)

- **Returns:** SETOF getfaceedges_returntype
- **Language:** c
- **Description:** args: atopology, aring, max_edges=null - Returns the ordered set of signed edge identifiers met by walking on ana given edge side.

#### gettopogeomelementarray(toponame character varying, layer_id integer, tgid integer)

- **Returns:** topoelementarray
- **Language:** plpgsql
- **Description:** args: toponame, layer_id, tg_id - Returns a topoelementarray (an array of topoelements) containing the topological elements and type of the given TopoGeometry (primitive elements).

#### gettopogeomelementarray(tg topogeometry)

- **Returns:** topoelementarray
- **Language:** plpgsql
- **Description:** args: tg - Returns a topoelementarray (an array of topoelements) containing the topological elements and type of the given TopoGeometry (primitive elements).

#### gettopogeomelements(toponame character varying, layerid integer, tgid integer)

- **Returns:** SETOF topoelement
- **Language:** plpgsql
- **Description:** args: toponame, layer_id, tg_id - Returns a set of topoelement objects containing the topological element_id,element_type of the given TopoGeometry (primitive elements).

#### gettopogeomelements(tg topogeometry)

- **Returns:** SETOF topoelement
- **Language:** plpgsql
- **Description:** args: tg - Returns a set of topoelement objects containing the topological element_id,element_type of the given TopoGeometry (primitive elements).

#### gettopologyid(toponame character varying)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: toponame - Returns the SRID of a topology in the topology.topology table given the name of the topology.

#### gettopologyname(topoid integer)

- **Returns:** character varying
- **Language:** plpgsql
- **Description:** args: topology_id - Returns the name of a topology (schema) given the id of the topology.

#### gettopologysrid(toponame character varying)

- **Returns:** integer
- **Language:** sql

#### intersects(tg1 topogeometry, tg2 topogeometry)

- **Returns:** boolean
- **Language:** plpgsql
- **Description:** args: tg1, tg2 - Returns true if any pair of primitives from the two topogeometries intersect.

#### layertrigger()

- **Returns:** trigger
- **Language:** plpgsql

#### polygonize(toponame character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: toponame - Finds and registers all faces defined by topology edges.

#### populate_topology_layer()

- **Returns:** TABLE(schema_name text, table_name text, feature_column text)
- **Language:** sql
- **Description:** Adds missing entries to topology.layer table by reading metadata from topo tables.

#### postgis_topology_scripts_installed()

- **Returns:** text
- **Language:** sql

#### relationtrigger()

- **Returns:** trigger
- **Language:** plpgsql

#### removeunusedprimitives(atopology text, bbox geometry DEFAULT NULL::geometry)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: topology_name, bbox - Removes topology primitives which not needed to define existing TopoGeometry objects.

#### st_addedgemodface(atopology character varying, anode integer, anothernode integer, acurve geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anode, anothernode, acurve - Add a new edge and, if in doing so it splits a face, modify the original face and add a new face.

#### st_addedgenewfaces(atopology character varying, anode integer, anothernode integer, acurve geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anode, anothernode, acurve - Add a new edge and, if in doing so it splits a face, delete the original face and replace it with two new faces.

#### st_addisoedge(atopology character varying, anode integer, anothernode integer, acurve geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anode, anothernode, alinestring - Adds an isolated edge defined by geometry alinestring to a topology connecting two existing isolated nodes anode and anothernode and returns the edge id of the new edge.

#### st_addisonode(atopology character varying, aface integer, apoint geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, aface, apoint - Adds an isolated node to a face in a topology and returns the nodeid of the new node. If face is null, the node is still created.

#### st_changeedgegeom(atopology character varying, anedge integer, acurve geometry)

- **Returns:** text
- **Language:** c
- **Description:** args: atopology, anedge, acurve - Changes the shape of an edge without affecting the topology structure.

#### st_createtopogeo(atopology character varying, acollection geometry)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: atopology, acollection - Adds a collection of geometries to a given empty topology and returns a message detailing success.

#### st_geometrytype(tg topogeometry)

- **Returns:** text
- **Language:** sql

#### st_getfaceedges(toponame character varying, face_id integer)

- **Returns:** SETOF getfaceedges_returntype
- **Language:** c
- **Description:** args: atopology, aface - Returns a set of ordered edges that bound aface.

#### st_getfacegeometry(toponame character varying, aface integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: atopology, aface - Returns the polygon in the given topology with the specified face id.

#### st_inittopogeo(atopology character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: topology_schema_name - Creates a new topology schema and registers this new schema in the topology.topology table and details summary of process.

#### st_modedgeheal(toponame character varying, e1id integer, e2id integer)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anedge, anotheredge - Heals two edges by deleting the node connecting them, modifying the first edgeand deleting the second edge. Returns the id of the deleted node.

#### st_modedgesplit(atopology character varying, anedge integer, apoint geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anedge, apoint - Split an edge by creating a new node along an existing edge, modifying the original edge and adding a new edge.

#### st_moveisonode(atopology character varying, anode integer, apoint geometry)

- **Returns:** text
- **Language:** c
- **Description:** args: atopology, anode, apoint - Moves an isolated node in a topology from one point to another. If new apoint geometry exists as a node an error is thrown. Returns description of move.

#### st_newedgeheal(toponame character varying, e1id integer, e2id integer)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anedge, anotheredge - Heals two edges by deleting the node connecting them, deleting both edges,and replacing them with an edge whose direction is the same as the firstedge provided.

#### st_newedgessplit(atopology character varying, anedge integer, apoint geometry)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anedge, apoint - Split an edge by creating a new node along an existing edge, deleting the original edge and replacing it with two new edges. Returns the id of the new node created that joins the new edges.

#### st_remedgemodface(toponame character varying, e1id integer)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anedge - Removes an edge and, if the removed edge separated two faces,delete one of the them and modify the other to take the space of both.

#### st_remedgenewface(toponame character varying, e1id integer)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, anedge - Removes an edge and, if the removed edge separated two faces,delete the original faces and replace them with a new face.

#### st_remisonode(character varying, integer)

- **Returns:** text
- **Language:** c

#### st_removeisoedge(atopology character varying, anedge integer)

- **Returns:** text
- **Language:** c
- **Description:** args: atopology, anedge - Removes an isolated edge and returns description of action. If the edge is not isolated, then an exception is thrown.

#### st_removeisonode(atopology character varying, anode integer)

- **Returns:** text
- **Language:** c
- **Description:** args: atopology, anode - Removes an isolated node and returns description of action. If the node is not isolated (is start or end of an edge), then an exception is thrown.

#### st_simplify(tg topogeometry, tolerance double precision)

- **Returns:** geometry
- **Language:** plpgsql
- **Description:** args: tg, tolerance - Returns a "simplified" geometry version of the given TopoGeometry using the Douglas-Peucker algorithm.

#### st_srid(tg topogeometry)

- **Returns:** integer
- **Language:** sql
- **Description:** args: tg - Returns the spatial reference identifier for a topogeometry.

#### topoelementarray_append(topoelementarray, topoelement)

- **Returns:** topoelementarray
- **Language:** sql

#### topogeo_addgeometry(atopology character varying, ageom geometry, tolerance double precision DEFAULT 0)

- **Returns:** void
- **Language:** plpgsql

#### topogeo_addlinestring(atopology character varying, aline geometry, tolerance double precision DEFAULT 0)

- **Returns:** SETOF integer
- **Language:** c
- **Description:** args: atopology, aline, tolerance - Adds a linestring to an existing topology using a tolerance and possibly splitting existing edges/faces. Returns edge identifiers.

#### topogeo_addpoint(atopology character varying, apoint geometry, tolerance double precision DEFAULT 0)

- **Returns:** integer
- **Language:** c
- **Description:** args: atopology, apoint, tolerance - Adds a point to an existing topology using a tolerance and possibly splitting an existing edge.

#### topogeo_addpolygon(atopology character varying, apoly geometry, tolerance double precision DEFAULT 0)

- **Returns:** SETOF integer
- **Language:** c
- **Description:** args: atopology, apoly, tolerance - Adds a polygon to an existing topology using a tolerance and possibly splitting existing edges/faces. Returns face identifiers.

#### topogeom_addelement(tg topogeometry, el topoelement)

- **Returns:** topogeometry
- **Language:** plpgsql
- **Description:** args: tg, el - Adds an element to the definition of a TopoGeometry.

#### topogeom_addtopogeom(tgt topogeometry, src topogeometry)

- **Returns:** topogeometry
- **Language:** plpgsql
- **Description:** args: tgt, src - Adds element of a TopoGeometry to the definition of another TopoGeometry.

#### topogeom_remelement(tg topogeometry, el topoelement)

- **Returns:** topogeometry
- **Language:** plpgsql
- **Description:** args: tg, el - Removes an element from the definition of a TopoGeometry.

#### topologysummary(atopology character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: topology_schema_name - Takes a topology name and provides summary totals of types of objects in topology.

#### totopogeom(ageom geometry, atopology character varying, alayer integer, atolerance double precision DEFAULT 0)

- **Returns:** topogeometry
- **Language:** plpgsql
- **Description:** args: geom, toponame, layer_id, tolerance - Converts a simple Geometry into a topo geometry.

#### totopogeom(ageom geometry, tg topogeometry, atolerance double precision DEFAULT 0)

- **Returns:** topogeometry
- **Language:** plpgsql
- **Description:** args: geom, topogeom, tolerance - Converts a simple Geometry into a topo geometry.

#### validatetopology(toponame character varying, bbox geometry DEFAULT NULL::geometry)

- **Returns:** SETOF validatetopology_returntype
- **Language:** plpgsql
- **Description:** args: toponame, bbox - Returns a set of validatetopology_returntype objects detailing issues with topology.

#### validatetopologyrelation(toponame character varying)

- **Returns:** TABLE(error text, layer_id integer, topogeo_id integer, element_id integer)
- **Language:** plpgsql
- **Description:** args: toponame - Returns info about invalid topology relation records

---

## Schema: `ubec_main`

**Description:** Main schema for UBEC four-element protocol

### Schema Statistics

- **Tables:** 47
- **Total Rows:** 79,067
- **Columns:** 575
- **Views:** 20
- **Relationships:** 9
- **Indexes:** 317
- **Triggers:** 23
- **Functions:** 80
- **Custom Types:** 8

### Custom Types

#### distribution_category

**Values:** `general_circulation`, `stewardship`, `administration`

#### element_type

**Values:** `air`, `water`, `earth`, `fire`

#### health_status

**Values:** `excellent`, `good`, `fair`, `poor`, `critical`

#### impact_scale

**Values:** `micro`, `meso`, `macro`, `meta`

#### token_code

**Values:** `UBEC`, `UBECrc`, `UBECgpi`, `UBECtt`

#### transaction_type

**Values:** `payment`, `create_account`, `change_trust`, `manage_offer`, `path_payment`, `account_merge`, `manage_data`, `bump_sequence`, `clawback`, `other`, `manage_buy_offer`, `manage_sell_offer`, `create_passive_sell_offer`

#### transformation_type

**Values:** `individual_growth`, `community_building`, `resource_regeneration`, `knowledge_creation`, `system_evolution`, `cultural_shift`, `economic_transition`, `social_healing`

#### ubuntu_principle

**Values:** `diversity`, `reciprocity`, `mutualism`, `regeneration`, `holism`

### Tables

| Table | Rows | Columns | Size |
|-------|------|---------|------|
| stellar_transactions | 74,495 | 20 | 49 MB |
| stellar_accounts | 1,299 | 17 | 1032 kB |
| holonic_metrics | 1,286 | 16 | 2624 kB |
| account_balances | 651 | 6 | 1584 kB |
| ubec_balances | 651 | 15 | 560 kB |
| stellar_operations | 434 | 20 | 1248 kB |
| system_settings | 73 | 12 | 144 kB |
| asset_holder_analysis | 63 | 19 | 184 kB |
| liquidity_pool_owners | 26 | 13 | 936 kB |
| ubec_distributions | 24 | 14 | 112 kB |
| distribution_state | 12 | 9 | 104 kB |
| orderbook_snapshots | 12 | 13 | 96 kB |
| distribution_history | 10 | 15 | 152 kB |
| liquidity_pools | 10 | 20 | 336 kB |
| system_configuration | 10 | 8 | 96 kB |
| monitored_accounts | 5 | 9 | 80 kB |
| api_rate_limits | 4 | 6 | 56 kB |
| scheduler_jobs | 2 | 10 | 80 kB |
| account_order_positions | 0 | 10 | 56 kB |
| agent_activity_history | 0 | 7 | 56 kB |

#### ubec_main.account_balances

*Tracks token balances for all accounts across all UBEC tokens. Used for stability analysis in Earth element (UBECgpi).*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('account_balances_i... | - |
| account_id | varchar(56) | ✗ | - | Stellar public key (G... format) |
| asset_code | varchar(12) | ✗ | - | Token code: UBEC, UBECrc, UBECgpi, or... |
| balance | numeric(20,7) | ✓ | 0.0 | Current token balance for this account |
| last_updated | timestamp with time zone | ✓ | now() | Timestamp of last balance update |
| created_at | timestamp with time zone | ✓ | now() | - |

**Constraints:**
- `account_balances_balance_check` (CHECK)
- `account_balances_pkey` (PRIMARY KEY)
- `account_balances_unique_account_asset` (UNIQUE)

#### ubec_main.account_order_positions

*Aggregated order positions per account and asset*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('account_order_posi... | - |
| account_id | varchar(56) | ✗ | - | - |
| asset_code | enum | ✗ | - | - |
| total_buy_orders | integer | ✓ | 0 | - |
| total_buy_volume | numeric(20,7) | ✓ | 0 | Sum of all active buy order amounts |
| avg_buy_price | numeric(20,7) | ✓ | - | - |
| total_sell_orders | integer | ✓ | 0 | - |
| total_sell_volume | numeric(20,7) | ✓ | 0 | Sum of all active sell order amounts |
| avg_sell_price | numeric(20,7) | ✓ | - | - |
| last_updated | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `account_order_positions_pkey` (PRIMARY KEY)
- `fk_account` (FOREIGN KEY)
- `unique_account_asset` (UNIQUE)

#### ubec_main.agent_activity_history

*Tracks activity history for agents*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('agent_activity_his... | - |
| agent_id | integer | ✗ | - | - |
| activity_type | varchar(100) | ✗ | - | - |
| score_impact | numeric(10,4) | ✓ | 0 | - |
| timestamp | bigint | ✗ | - | - |
| details | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `activity_history_timestamp_check` (CHECK)
- `agent_activity_history_agent_id_fkey` (FOREIGN KEY)
- `agent_activity_history_pkey` (PRIMARY KEY)

#### ubec_main.agent_benefit_history

*Tracks benefit history for agents*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('agent_benefit_hist... | - |
| agent_id | integer | ✗ | - | - |
| benefit_type | varchar(100) | ✗ | - | - |
| amount | numeric(20,7) | ✓ | 0 | - |
| timestamp | bigint | ✗ | - | - |
| details | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `agent_benefit_history_agent_id_fkey` (FOREIGN KEY)
- `agent_benefit_history_pkey` (PRIMARY KEY)
- `benefit_history_timestamp_check` (CHECK)

#### ubec_main.agent_contribution_history

*Tracks contribution history for agents*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('agent_contribution... | - |
| agent_id | integer | ✗ | - | - |
| contribution_type | varchar(100) | ✗ | - | - |
| amount | numeric(20,7) | ✓ | 0 | - |
| timestamp | bigint | ✗ | - | - |
| details | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `agent_contribution_history_agent_id_fkey` (FOREIGN KEY)
- `agent_contribution_history_pkey` (PRIMARY KEY)
- `contribution_history_timestamp_check` (CHECK)

#### ubec_main.agent_holon_memberships

*Tracks agent memberships in holons*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('agent_holon_member... | - |
| agent_id | integer | ✗ | - | - |
| holon_id | integer | ✗ | - | - |
| role_in_holon | varchar(100) | ✓ | - | - |
| contribution_score | numeric(10,4) | ✓ | 0 | - |
| status | varchar(50) | ✗ | 'active'::character varying | - |
| joined_at | timestamp with time zone | ✗ | now() | - |
| left_at | timestamp with time zone | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `agent_holon_memberships_agent_id_fkey` (FOREIGN KEY)
- `agent_holon_memberships_holon_id_fkey` (FOREIGN KEY)
- `agent_holon_memberships_pkey` (PRIMARY KEY)
- `agent_holon_unique` (UNIQUE)
- `valid_membership_status` (CHECK)

#### ubec_main.agents

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('agents_id_seq'::re... | - |
| agent_id | varchar(56) | ✗ | - | - |
| participant_id | integer | ✓ | - | - |
| reputation_score | numeric(10,4) | ✓ | 0 | - |
| reciprocity_score | numeric(10,4) | ✓ | 0 | - |
| loyalty_tier | varchar(20) | ✓ | 'none'::character varying | - |
| last_activity_at | timestamp without time zone | ✓ | - | - |
| created_at | timestamp without time zone | ✗ | now() | - |
| updated_at | timestamp without time zone | ✗ | now() | - |
| status | varchar(20) | ✓ | 'active'::character varying | - |
| metrics | jsonb | ✓ | - | - |

**Constraints:**
- `agents_agent_id_key` (UNIQUE)
- `agents_pkey` (PRIMARY KEY)

#### ubec_main.api_rate_limits

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('api_rate_limits_id... | - |
| api_name | varchar(50) | ✗ | - | - |
| rate_limit_remaining | integer | ✓ | - | - |
| rate_limit_limit | integer | ✓ | - | - |
| rate_limit_reset | integer | ✓ | - | - |
| last_updated | timestamp without time zone | ✗ | now() | - |

**Constraints:**
- `api_rate_limits_pkey` (PRIMARY KEY)
- `unique_api_name` (UNIQUE)

#### ubec_main.asset_holder_analysis

*Periodic analysis of token holder distribution and supply metrics*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('asset_holder_analy... | - |
| analysis_date | timestamp without time zone | ✗ | now() | - |
| asset_code | varchar(12) | ✗ | - | - |
| asset_issuer | varchar(56) | ✗ | - | - |
| total_supply | numeric(18,8) | ✗ | - | - |
| total_holders | integer | ✗ | - | - |
| general_circulation | numeric(18,8) | ✓ | - | - |
| stewardship_held | numeric(18,8) | ✓ | - | - |
| administration_held | numeric(18,8) | ✓ | - | - |
| general_pct | numeric(5,4) | ✓ | - | - |
| stewardship_pct | numeric(5,4) | ✓ | - | - |
| administration_pct | numeric(5,4) | ✓ | - | - |
| is_compliant | boolean | ✓ | - | - |
| details | jsonb | ✓ | - | - |
| active_holders | integer | ✗ | 0 | - |
| new_holders_last_30_days | integer | ✓ | 0 | - |
| whale_concentration_percent | numeric(10,4) | ✓ | - | - |
| gini_coefficient | numeric(10,8) | ✓ | - | - |
| distribution_metrics | jsonb | ✓ | - | - |

**Constraints:**
- `asset_holder_analysis_pkey` (PRIMARY KEY)
- `chk_holders_positive` (CHECK)
- `chk_supply_positive` (CHECK)

#### ubec_main.asset_holders

*Current token balances for all accounts*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('asset_holders_id_s... | - |
| account_id | varchar(56) | ✗ | - | - |
| asset_code | varchar(12) | ✗ | - | - |
| asset_issuer | varchar(56) | ✗ | - | - |
| balance | numeric(18,8) | ✗ | 0 | - |
| last_updated | timestamp without time zone | ✗ | now() | - |
| classification | varchar(20) | ✓ | - | - |

**Constraints:**
- `asset_holders_pkey` (PRIMARY KEY)
- `chk_balance_non_negative` (CHECK)
- `unique_holder_asset` (UNIQUE)

#### ubec_main.constraint_violations

*Logs constraint violations for debugging and data quality monitoring*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('constraint_violati... | - |
| table_name | varchar(100) | ✗ | - | - |
| constraint_name | varchar(100) | ✗ | - | - |
| violation_data | jsonb | ✓ | - | - |
| error_message | text | ✓ | - | - |
| occurred_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |

**Constraints:**
- `constraint_violations_pkey` (PRIMARY KEY)

#### ubec_main.distribution_history

*Historical record of distribution checks and rebalancing actions*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('distribution_histo... | - |
| check_date | timestamp without time zone | ✗ | now() | - |
| asset_code | varchar(12) | ✗ | - | - |
| asset_issuer | varchar(56) | ✗ | - | - |
| general_balance | numeric(18,8) | ✗ | - | - |
| admin_balance | numeric(18,8) | ✗ | - | - |
| stewardship_balance | numeric(18,8) | ✗ | - | - |
| total_supply | numeric(18,8) | ✓ | - | - |
| rebalance_needed | boolean | ✗ | - | - |
| transfers_initiated | integer | ✓ | 0 | - |
| total_transfer_amount | numeric(18,8) | ✓ | 0 | - |
| details | jsonb | ✓ | - | - |
| general_percentage | numeric(10,4) | ✓ | - | - |
| admin_percentage | numeric(10,4) | ✓ | - | - |
| stewardship_percentage | numeric(10,4) | ✓ | - | - |

**Constraints:**
- `chk_balances_positive` (CHECK)
- `distribution_history_pkey` (PRIMARY KEY)

#### ubec_main.distribution_state

*Distribution state tracking for Earth element (UBECgpi). Monitors tokenomics compliance (75/20/5).*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('distribution_state... | - |
| asset_code | varchar(12) | ✗ | - | Token code being tracked |
| category | varchar(50) | ✗ | - | Distribution category: general_circul... |
| current_amount | numeric(20,7) | ✓ | 0.0 | - |
| target_amount | numeric(20,7) | ✓ | 0.0 | - |
| target_percentage | numeric(5,2) | ✗ | - | Target percentage for this category (... |
| actual_percentage | numeric(5,2) | ✓ | 0.0 | Current actual percentage |
| is_compliant | boolean | ✓ | true | Whether current distribution is withi... |
| last_updated | timestamp with time zone | ✓ | now() | - |

**Constraints:**
- `distribution_state_amounts_check` (CHECK)
- `distribution_state_percentages_check` (CHECK)
- `distribution_state_pkey` (PRIMARY KEY)
- `distribution_state_unique_asset_category` (UNIQUE)

#### ubec_main.distribution_transfers

*Records all distribution rebalancing transactions executed on Stellar blockchain*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('distribution_trans... | Unique identifier for each transfer r... |
| tx_hash | text | ✗ | - | Stellar transaction hash (unique iden... |
| from_account | text | ✗ | - | Source account public key (G...) |
| to_account | text | ✗ | - | Destination account public key (G...) |
| amount | numeric(20,7) | ✗ | - | Amount transferred (in token units, u... |
| asset_code | text | ✗ | - | Asset code (e.g., UBEC, UBECrc, etc.) |
| asset_issuer | text | ✗ | - | Asset issuer public key |
| ledger | integer | ✓ | - | Stellar ledger number where transacti... |
| memo | text | ✓ | - | Transaction memo text (max 28 charact... |
| network | text | ✗ | - | Network where transaction occurred (T... |
| executed_at | timestamp without time zone | ✗ | now() | Timestamp when transaction was execut... |
| created_at | timestamp without time zone | ✗ | now() | Timestamp when record was created in ... |
| updated_at | timestamp without time zone | ✗ | now() | Timestamp when record was last updated |
| notes | text | ✓ | - | Optional notes or metadata about the ... |
| recorded_by | text | ✓ | 'distribution_service'::text | System or service that recorded this ... |

**Constraints:**
- `distribution_transfers_network_check` (CHECK)
- `distribution_transfers_pkey` (PRIMARY KEY)
- `distribution_transfers_tx_hash_key` (UNIQUE)
- `positive_amount` (CHECK)
- `valid_network` (CHECK)

#### ubec_main.flow_transactions

*Flow transactions tracking for Water element (UBECrc). Records all token flows.*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| transaction_id | varchar(64) | ✗ | - | Stellar transaction hash |
| asset_code | varchar(12) | ✗ | - | Token code involved in the transaction |
| from_account | varchar(56) | ✗ | - | Sending Stellar account |
| to_account | varchar(56) | ✗ | - | Receiving Stellar account |
| amount | numeric(20,7) | ✗ | - | Amount transferred |
| created_at | timestamp with time zone | ✓ | now() | - |
| memo | text | ✓ | - | - |

**Constraints:**
- `flow_transactions_amount_check` (CHECK)
- `flow_transactions_pkey` (PRIMARY KEY)

#### ubec_main.gateway_accounts

*Gateway accounts tracking for Air element (UBEC). Tracks account balances and trustline status.*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| account_id | varchar(56) | ✗ | - | Stellar public key (G... format) |
| asset_code | varchar(12) | ✗ | - | Token code: UBEC, UBECrc, UBECgpi, or... |
| balance | numeric(20,7) | ✓ | 0.0 | Current token balance for this account |
| trustline_established | boolean | ✓ | false | Whether the account has established a... |
| created_at | timestamp with time zone | ✓ | now() | - |
| last_activity | timestamp with time zone | ✓ | now() | - |
| transaction_count | integer | ✓ | 0 | - |

**Constraints:**
- `gateway_accounts_balance_check` (CHECK)
- `gateway_accounts_pkey` (PRIMARY KEY)
- `gateway_accounts_tx_count_check` (CHECK)

#### ubec_main.holder_discovery_history

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('holder_discovery_h... | - |
| discovery_date | timestamp without time zone | ✗ | now() | - |
| account_id | varchar(56) | ✗ | - | - |
| discovery_source | varchar(50) | ✗ | - | - |
| source_transaction_id | varchar(64) | ✓ | - | - |
| initial_balance | numeric(18,8) | ✓ | 0 | - |
| is_new | boolean | ✓ | true | - |
| added_to_tracking | boolean | ✓ | false | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `holder_discovery_history_pkey` (PRIMARY KEY)

#### ubec_main.holonic_metrics

*Stores holonic evaluation metrics for UBEC token holders*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('holonic_metrics_id... | - |
| evaluation_date | timestamp with time zone | ✗ | now() | Date and time when the evaluation was... |
| autonomy_integration_score | numeric(5,4) | ✗ | 0 | Score for balance of autonomy and int... |
| multi_scale_score | numeric(5,4) | ✗ | 0 | Score for multi-scale participation (... |
| regenerative_impact_score | numeric(5,4) | ✗ | 0 | Score for regenerative impact (0-1) |
| network_contribution_score | numeric(5,4) | ✗ | 0 | Score for network contribution (0-1) |
| ubuntu_alignment_score | numeric(5,4) | ✗ | 0 | Score for Ubuntu philosophy alignment... |
| composite_score | numeric(5,4) | ✗ | 0 | Overall holonic score (0-1) |
| holonic_category | varchar(50) | ✗ | 'Observer'::character varying | Category: Observer, Participant, Cont... |
| raw_metrics | jsonb | ✓ | - | JSON object containing detailed metri... |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |
| evaluation_date_date | date | ✗ | - | - |
| account_id | varchar(56) | ✗ | - | - |
| confidence | numeric(10,6) | ✓ | 0.8 | - |
| calculation_mode | text | ✓ | 'transaction_based'::text | - |

**Constraints:**
- `holonic_metrics_pkey` (PRIMARY KEY)
- `uq_holonic_metrics_account_date` (UNIQUE)
- `valid_autonomy_score` (CHECK)
- `valid_composite_score` (CHECK)
- `valid_holonic_category` (CHECK)
- `valid_multi_scale_score` (CHECK)
- `valid_network_score` (CHECK)
- `valid_regenerative_score` (CHECK)
- `valid_ubuntu_score` (CHECK)

#### ubec_main.holons

*Stores information about holons (groups/communities)*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('holons_id_seq'::re... | - |
| holon_id | varchar(100) | ✗ | - | - |
| holon_name | varchar(255) | ✗ | - | - |
| holon_type | varchar(100) | ✗ | - | - |
| description | text | ✓ | - | - |
| parent_holon_id | integer | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `holons_holon_id_key` (UNIQUE)
- `holons_parent_holon_id_fkey` (FOREIGN KEY)
- `holons_pkey` (PRIMARY KEY)

#### ubec_main.liquidity_pool_owners

*Air element: Account ownership positions in liquidity pools. Tracks shares, percentages, and calculated UBEC balances for distribution compliance.*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('liquidity_pool_own... | - |
| account_id | varchar(56) | ✗ | - | - |
| liquidity_pool_id | varchar(64) | ✗ | - | - |
| shares | numeric(20,7) | ✗ | 0 | Number of pool shares owned (like LP ... |
| ownership_percentage | numeric(10,6) | ✗ | 0 | Percentage of total pool owned (0-100) |
| ubec_balance | numeric(20,7) | ✗ | 0 | Calculated UBEC balance from this LP ... |
| element | enum | ✓ | 'air'::element_type | Element classification (always air fo... |
| token_code | enum | ✓ | - | Which UBEC token this position repres... |
| metadata | jsonb | ✓ | - | - |
| last_modified_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| sync_timestamp | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| created_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| sync_status | varchar(20) | ✓ | 'synced'::character varying | - |

**Constraints:**
- `fk_lp_owner_account` (FOREIGN KEY)
- `fk_lp_owner_pool` (FOREIGN KEY)
- `liquidity_pool_owners_pkey` (PRIMARY KEY)
- `unique_account_pool` (UNIQUE)
- `valid_percentage` (CHECK)
- `valid_shares` (CHECK)
- `valid_ubec_balance` (CHECK)

#### ubec_main.liquidity_pools

*Stellar liquidity pools containing UBEC tokens*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | varchar(64) | ✗ | - | Stellar liquidity pool ID (64-byte he... |
| asset_a_code | varchar(12) | ✗ | - | - |
| asset_a_issuer | varchar(56) | ✓ | - | - |
| asset_b_code | varchar(12) | ✗ | - | - |
| asset_b_issuer | varchar(56) | ✓ | - | - |
| pair | varchar(50) | ✗ | - | Human-readable pair name (e.g., UBEC/... |
| primary_element | enum | ✓ | 'air'::element_type | Element classification (always air fo... |
| token_code | enum | ✓ | - | Which UBEC token is in this pool (UBE... |
| reserve_a | numeric(20,7) | ✗ | 0 | - |
| reserve_b | numeric(20,7) | ✗ | 0 | - |
| total_shares | numeric(20,7) | ✗ | 0 | Total pool shares issued (like LP tok... |
| balance | numeric(20,7) | ✗ | 0 | Total UBEC tokens in this pool |
| ubec_asset_position | char(1) | ✓ | - | Whether UBEC is asset_a or asset_b in... |
| fee_bp | integer | ✓ | 30 | - |
| trustline_count | integer | ✓ | 0 | - |
| metadata | jsonb | ✓ | - | - |
| last_modified_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| sync_timestamp | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| created_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| sync_status | varchar(20) | ✓ | 'synced'::character varying | - |

**Constraints:**
- `liquidity_pools_pkey` (PRIMARY KEY)
- `liquidity_pools_ubec_asset_position_check` (CHECK)
- `valid_balance` (CHECK)
- `valid_fee` (CHECK)
- `valid_reserves` (CHECK)
- `valid_shares` (CHECK)
- `valid_trustlines` (CHECK)

#### ubec_main.monitored_accounts

*Tracks special accounts (administration, stewardship, general) for tokenomics compliance monitoring. Used by analytics service to calculate locked supply and liquidity ratios.*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| account_id | varchar(56) | ✗ | - | Stellar public key (G... format) |
| account_type | varchar(20) | ✗ | - | Account classification for tokenomics... |
| account_name | varchar(100) | ✓ | - | - |
| description | text | ✓ | - | - |
| monitored_since | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| is_active | boolean | ✓ | true | - |
| metadata | jsonb | ✓ | '{}'::jsonb | - |
| created_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |

**Constraints:**
- `monitored_accounts_account_type_check` (CHECK)
- `monitored_accounts_pkey` (PRIMARY KEY)
- `valid_account_id` (CHECK)
- `valid_account_name` (CHECK)

#### ubec_main.mutualism_relationships

*Tracks mutualistic relationships between accounts in the Earth element (UBECgpi). Represents the Ubuntu principle of mutualism.*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('mutualism_relation... | - |
| asset_code | varchar(12) | ✗ | - | Token code for the relationship (prim... |
| account_a | varchar(56) | ✗ | - | First account in the relationship (St... |
| account_b | varchar(56) | ✗ | - | Second account in the relationship (S... |
| interaction_count | integer | ✓ | 0 | Number of mutual interactions between... |
| mutual_benefit_score | numeric(5,4) | ✓ | 0.0 | Score representing mutual benefit (0-... |
| relationship_strength | numeric(5,4) | ✓ | 0.0 | Overall strength of the relationship ... |
| last_interaction | timestamp with time zone | ✓ | now() | Timestamp of most recent interaction |
| first_interaction | timestamp with time zone | ✓ | now() | - |
| created_at | timestamp with time zone | ✓ | now() | - |
| updated_at | timestamp with time zone | ✓ | now() | - |

**Constraints:**
- `mutualism_relationships_interaction_count_check` (CHECK)
- `mutualism_relationships_mutual_benefit_check` (CHECK)
- `mutualism_relationships_pkey` (PRIMARY KEY)
- `mutualism_relationships_strength_check` (CHECK)
- `mutualism_relationships_unique_pair` (UNIQUE)

#### ubec_main.orderbook_analytics

*Pre-computed order book analytics and market metrics*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('orderbook_analytic... | - |
| asset_code | enum | ✗ | - | - |
| analysis_time | timestamp with time zone | ✗ | now() | - |
| total_liquidity | numeric(20,7) | ✓ | - | - |
| buy_pressure | numeric(10,4) | ✓ | - | Buy pressure score 0-100 (higher = mo... |
| sell_pressure | numeric(10,4) | ✓ | - | Sell pressure score 0-100 (higher = m... |
| market_depth_score | numeric(10,4) | ✓ | - | Overall market depth quality 0-100 |
| price_stability_score | numeric(10,4) | ✓ | - | - |
| top_10_buyers_volume | numeric(20,7) | ✓ | - | - |
| top_10_sellers_volume | numeric(20,7) | ✓ | - | - |
| unique_buyers | integer | ✓ | - | - |
| unique_sellers | integer | ✓ | - | - |
| metrics | jsonb | ✓ | - | Extended metrics in JSON format for f... |

**Constraints:**
- `orderbook_analytics_pkey` (PRIMARY KEY)
- `unique_analysis` (UNIQUE)

#### ubec_main.orderbook_snapshots

*Historical order book snapshots for market analysis*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('orderbook_snapshot... | - |
| asset_code | enum | ✗ | - | - |
| counter_asset | varchar(12) | ✗ | - | - |
| snapshot_time | timestamp with time zone | ✗ | now() | - |
| best_bid | numeric(20,7) | ✓ | - | - |
| best_ask | numeric(20,7) | ✓ | - | - |
| spread_bps | integer | ✓ | - | Bid-ask spread in basis points (1 bps... |
| bid_depth_total | numeric(20,7) | ✓ | - | - |
| ask_depth_total | numeric(20,7) | ✓ | - | - |
| bid_levels | integer | ✓ | - | - |
| ask_levels | integer | ✓ | - | - |
| raw_data | jsonb | ✓ | - | JSON snapshot of top 10 bid/ask levels |
| created_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `orderbook_snapshots_pkey` (PRIMARY KEY)
- `unique_snapshot` (UNIQUE)

#### ubec_main.participants

*Categorization of accounts (general, administration, stewardship)*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('participants_id_se... | - |
| account_id | varchar(56) | ✗ | - | - |
| account_type | varchar(50) | ✗ | - | - |
| account_label | varchar(100) | ✓ | - | - |
| is_active | boolean | ✓ | true | - |
| created_at | timestamp without time zone | ✗ | now() | - |
| updated_at | timestamp without time zone | ✗ | now() | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `chk_account_type` (CHECK)
- `participants_account_id_key` (UNIQUE)
- `participants_pkey` (PRIMARY KEY)

#### ubec_main.reciprocity_transactions

*Transactions affecting reciprocity scores*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('reciprocity_transa... | - |
| account_id | varchar(56) | ✗ | - | - |
| transaction_type | varchar(20) | ✗ | - | - |
| amount | numeric(18,8) | ✗ | - | - |
| reason | text | ✓ | - | - |
| source | varchar(50) | ✓ | - | - |
| context | jsonb | ✓ | - | - |
| created_at | timestamp without time zone | ✗ | now() | - |

**Constraints:**
- `chk_reciprocity_tx_type` (CHECK)
- `reciprocity_transactions_pkey` (PRIMARY KEY)

#### ubec_main.regenerative_projects

*Stores information about regenerative projects linked to agents*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('regenerative_proje... | - |
| agent_id | integer | ✗ | - | - |
| project_name | varchar(255) | ✗ | - | - |
| description | text | ✓ | - | - |
| project_type | varchar(100) | ✗ | - | - |
| verification_status | varchar(50) | ✓ | 'unverified'::character var... | - |
| verification_date | timestamp with time zone | ✓ | - | - |
| impact_metrics | jsonb | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |

**Constraints:**
- `regenerative_projects_agent_id_fkey` (FOREIGN KEY)
- `regenerative_projects_pkey` (PRIMARY KEY)
- `valid_verification_status` (CHECK)

#### ubec_main.scheduler_jobs

*Scheduled jobs for automated distribution management*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('scheduler_jobs_id_... | - |
| job_name | varchar(100) | ✗ | - | - |
| schedule_interval | varchar(50) | ✗ | - | - |
| next_run | timestamp without time zone | ✗ | - | - |
| last_run | timestamp without time zone | ✓ | - | - |
| job_function | text | ✗ | - | - |
| parameters | jsonb | ✓ | - | - |
| enabled | boolean | ✓ | true | - |
| created_at | timestamp without time zone | ✗ | now() | - |
| updated_at | timestamp without time zone | ✗ | now() | - |

**Constraints:**
- `chk_next_run_valid` (CHECK)
- `scheduler_jobs_job_name_key` (UNIQUE)
- `scheduler_jobs_pkey` (PRIMARY KEY)

#### ubec_main.stellar_accounts

*Stellar blockchain accounts with element tracking*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('stellar_accounts_i... | - |
| account_id | varchar(56) | ✗ | - | - |
| primary_element | enum | ✓ | - | - |
| token_holdings | ARRAY | ✓ | - | - |
| sequence | bigint | ✓ | - | - |
| subentry_count | integer | ✓ | 0 | - |
| inflation_destination | varchar(56) | ✓ | - | - |
| home_domain | varchar(255) | ✓ | - | - |
| thresholds | jsonb | ✓ | - | - |
| flags | jsonb | ✓ | - | - |
| signers | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✓ | - | - |
| last_modified_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| last_activity_at | timestamp with time zone | ✓ | - | - |
| sync_status | varchar(20) | ✓ | 'pending'::character varying | - |
| sync_cursor | varchar(100) | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `stellar_accounts_account_id_key` (UNIQUE)
- `stellar_accounts_pkey` (PRIMARY KEY)
- `valid_account_id` (CHECK)

#### ubec_main.stellar_effects

*Stellar blockchain effects with element context*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('stellar_effects_id... | - |
| effect_id | varchar(100) | ✗ | - | - |
| operation_id | varchar(100) | ✗ | - | - |
| effect_element | enum | ✓ | - | - |
| type | varchar(50) | ✗ | - | - |
| account | varchar(56) | ✓ | - | - |
| amount | numeric(20,7) | ✓ | - | - |
| asset_type | varchar(20) | ✓ | - | - |
| asset_code | enum | ✓ | - | - |
| asset_issuer | varchar(56) | ✓ | - | - |
| details | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | - | - |

**Constraints:**
- `fk_operation_id` (FOREIGN KEY)
- `stellar_effects_effect_id_key` (UNIQUE)
- `stellar_effects_pkey` (PRIMARY KEY)

#### ubec_main.stellar_offers

*Individual offers/orders on Stellar DEX for UBEC tokens*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('stellar_offers_id_... | - |
| offer_id | bigint | ✗ | - | - |
| seller_account | varchar(56) | ✗ | - | - |
| selling_asset | enum | ✓ | - | - |
| buying_asset | varchar(12) | ✗ | - | - |
| amount | numeric(20,7) | ✗ | - | - |
| price | numeric(20,7) | ✗ | - | - |
| price_r_n | integer | ✓ | - | Price as ratio numerator (for exact p... |
| price_r_d | integer | ✓ | - | Price as ratio denominator (for exact... |
| side | varchar(4) | ✗ | - | Whether this is a buy or sell order f... |
| is_passive | boolean | ✓ | false | Passive orders do not take offers of ... |
| last_modified_ledger | bigint | ✓ | - | - |
| last_modified_time | timestamp with time zone | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |
| status | varchar(20) | ✓ | 'active'::character varying | - |

**Constraints:**
- `fk_seller` (FOREIGN KEY)
- `stellar_offers_offer_id_key` (UNIQUE)
- `stellar_offers_pkey` (PRIMARY KEY)
- `stellar_offers_side_check` (CHECK)
- `stellar_offers_status_check` (CHECK)

#### ubec_main.stellar_operations

*Stellar blockchain operations with element and asset tracking*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('stellar_operations... | - |
| operation_id | varchar(100) | ✗ | - | - |
| transaction_hash | varchar(64) | ✗ | - | - |
| operation_element | enum | ✓ | - | - |
| asset_code | enum | ✓ | - | - |
| type | enum | ✗ | - | - |
| type_i | integer | ✓ | - | - |
| source_account | varchar(56) | ✓ | - | - |
| amount | numeric(20,7) | ✓ | - | - |
| asset_type | varchar(20) | ✓ | - | - |
| asset_issuer | varchar(56) | ✓ | - | - |
| from_account | varchar(56) | ✓ | - | - |
| to_account | varchar(56) | ✓ | - | - |
| details | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | - | - |
| metadata | jsonb | ✓ | - | - |
| exchange_source_asset | varchar(12) | ✓ | - | - |
| exchange_source_amount | numeric(18,8) | ✓ | - | - |
| exchange_dest_asset | varchar(12) | ✓ | - | - |
| exchange_dest_amount | numeric(18,8) | ✓ | - | - |

**Constraints:**
- `fk_transaction_hash` (FOREIGN KEY)
- `stellar_operations_operation_id_key` (UNIQUE)
- `stellar_operations_pkey` (PRIMARY KEY)

#### ubec_main.stellar_transactions

*Stellar blockchain transactions with element context*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('stellar_transactio... | - |
| transaction_hash | varchar(64) | ✗ | - | - |
| ledger_sequence | bigint | ✗ | - | - |
| primary_element | enum | ✓ | - | - |
| involves_tokens | ARRAY | ✓ | - | - |
| source_account | varchar(56) | ✗ | - | - |
| source_account_sequence | bigint | ✓ | - | - |
| fee_charged | bigint | ✓ | - | - |
| max_fee | bigint | ✓ | - | - |
| operation_count | integer | ✓ | - | - |
| time_bounds | jsonb | ✓ | - | - |
| memo_type | varchar(20) | ✓ | - | - |
| memo | varchar(255) | ✓ | - | - |
| successful | boolean | ✓ | true | - |
| result_code | text | ✓ | - | - |
| result_xdr | text | ✓ | - | - |
| created_at | timestamp with time zone | ✗ | - | - |
| ledger_close_time | timestamp with time zone | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |
| ledger | bigint | ✓ | - | Ledger sequence number where this tra... |

**Constraints:**
- `fk_source_account` (FOREIGN KEY)
- `stellar_transactions_pkey` (PRIMARY KEY)
- `stellar_transactions_transaction_hash_key` (UNIQUE)

#### ubec_main.sync_jobs

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('sync_jobs_id_seq':... | - |
| job_type | varchar(50) | ✗ | - | - |
| schedule_interval | interval | ✗ | - | - |
| last_run | timestamp without time zone | ✓ | - | - |
| next_run | timestamp without time zone | ✗ | - | - |
| enabled | boolean | ✓ | true | - |
| parameters | jsonb | ✓ | - | - |
| last_status | varchar(20) | ✓ | - | - |
| error_message | text | ✓ | - | - |
| created_at | timestamp without time zone | ✗ | now() | - |
| updated_at | timestamp without time zone | ✗ | now() | - |

**Constraints:**
- `sync_jobs_pkey` (PRIMARY KEY)

#### ubec_main.sync_status

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| account_id | varchar(56) | ✗ | - | - |
| last_sync | timestamp without time zone | ✗ | now() | - |
| last_block_height | bigint | ✓ | - | - |
| last_ledger_sequence | bigint | ✓ | - | - |
| last_transaction_id | varchar(64) | ✓ | - | - |
| sync_count | integer | ✓ | 0 | - |
| status | varchar(20) | ✓ | 'active'::character varying | - |
| error_count | integer | ✓ | 0 | - |
| last_error | text | ✓ | - | - |
| last_error_at | timestamp without time zone | ✓ | - | - |

**Constraints:**
- `sync_status_pkey` (PRIMARY KEY)

#### ubec_main.system_configuration

*System-wide configuration parameters*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('system_configurati... | - |
| parameter_name | varchar(100) | ✗ | - | - |
| parameter_value | text | ✗ | - | - |
| parameter_type | varchar(20) | ✓ | 'string'::character varying | - |
| description | text | ✓ | - | - |
| is_sensitive | boolean | ✓ | false | - |
| created_at | timestamp without time zone | ✗ | now() | - |
| updated_at | timestamp without time zone | ✗ | now() | - |

**Constraints:**
- `chk_parameter_type` (CHECK)
- `system_configuration_parameter_name_key` (UNIQUE)
- `system_configuration_pkey` (PRIMARY KEY)

#### ubec_main.system_settings

*System configuration settings - single source of truth for all system parameters*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| setting_id | integer | ✗ | nextval('system_settings_se... | - |
| setting_key | varchar(100) | ✗ | - | Unique setting identifier |
| setting_value | text | ✗ | - | Setting value (stored as text, conver... |
| setting_type | varchar(20) | ✓ | 'string'::character varying | Data type of the setting (string, int... |
| description | text | ✓ | - | - |
| category | varchar(50) | ✓ | 'general'::character varying | Setting category for organization |
| is_active | boolean | ✓ | true | Whether the setting is active |
| is_encrypted | boolean | ✓ | false | Whether the setting value is encrypted |
| created_at | timestamp without time zone | ✓ | now() | - |
| updated_at | timestamp without time zone | ✓ | now() | - |
| created_by | varchar(100) | ✓ | - | - |
| updated_by | varchar(100) | ✓ | - | - |

**Constraints:**
- `system_settings_pkey` (PRIMARY KEY)
- `system_settings_setting_key_key` (UNIQUE)
- `system_settings_setting_type_check` (CHECK)

#### ubec_main.transfer_recommendations

*Recommended token transfers for distribution rebalancing*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('transfer_recommend... | - |
| recommendation_date | timestamp without time zone | ✗ | now() | - |
| asset_code | varchar(12) | ✗ | - | - |
| asset_issuer | varchar(56) | ✗ | - | - |
| from_account_type | varchar(50) | ✗ | - | - |
| to_account_type | varchar(50) | ✗ | - | - |
| amount | numeric(18,8) | ✗ | - | - |
| status | varchar(20) | ✗ | 'pending'::character varying | - |
| status_message | text | ✓ | - | - |
| transaction_hash | varchar(64) | ✓ | - | - |
| actual_amount | numeric(18,8) | ✓ | - | - |
| priority | integer | ✓ | 5 | - |
| created_at | timestamp without time zone | ✗ | now() | - |
| updated_at | timestamp without time zone | ✗ | now() | - |
| completed_at | timestamp without time zone | ✓ | - | - |

**Constraints:**
- `chk_transfer_amount_positive` (CHECK)
- `chk_transfer_status` (CHECK)
- `transfer_recommendations_pkey` (PRIMARY KEY)

#### ubec_main.transformation_phases

*Tracks transformation phases and their momentum in the Ubuntu Economic Commons (Fire Element - UBECtt)*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('transformation_pha... | - |
| phase_id | varchar(255) | ✗ | - | Unique identifier for the transformat... |
| name | varchar(255) | ✗ | - | Name of the transformation phase |
| description | text | ✗ | - | Detailed description of the phase |
| start_date | timestamp with time zone | ✗ | - | When the transformation phase began |
| end_date | timestamp with time zone | ✓ | - | When the transformation phase ended (... |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |
| target_outcomes | ARRAY | ✓ | '{}'::text[] | Array of target outcomes for this phase |
| key_indicators | jsonb | ✓ | '{}'::jsonb | Key performance indicators tracked du... |
| participating_agents | ARRAY | ✓ | '{}'::text[] | Array of Stellar account IDs particip... |
| actions_completed | integer | ✓ | 0 | Number of transformative actions comp... |
| total_ubectt_distributed | numeric(20,7) | ✓ | 0.0 | Total UBECtt tokens distributed durin... |
| phase_momentum | numeric(5,4) | ✓ | 0.0 | Rate of transformation in this phase ... |
| is_active | boolean | ✓ | true | Whether this phase is currently active |
| completion_percentage | numeric(5,2) | ✓ | 0.0 | Percentage of phase completion (0 - 100) |
| metadata | jsonb | ✓ | '{}'::jsonb | Additional metadata in JSON format |

**Constraints:**
- `transformation_phases_actions_completed_check` (CHECK)
- `transformation_phases_completion_percentage_check` (CHECK)
- `transformation_phases_phase_id_key` (UNIQUE)
- `transformation_phases_phase_momentum_check` (CHECK)
- `transformation_phases_pkey` (PRIMARY KEY)
- `transformation_phases_total_ubectt_distributed_check` (CHECK)

#### ubec_main.transformative_actions

*Records transformative actions and contributions in the Ubuntu Economic Commons (Fire Element - UBECtt)*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('transformative_act... | - |
| action_id | varchar(255) | ✗ | - | Unique identifier for the transformat... |
| agent_id | varchar(56) | ✗ | - | Stellar account ID of the agent perfo... |
| action_type | enum | ✗ | - | Type of transformative action performed |
| description | text | ✗ | - | Detailed description of the transform... |
| impact_scale | enum | ✗ | - | Scale of impact (micro, meso, macro, ... |
| timestamp | timestamp with time zone | ✗ | now() | - |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |
| direct_beneficiaries | integer | ✓ | 0 | Number of people directly affected by... |
| indirect_reach | integer | ✓ | 0 | Estimated ripple effect reach |
| regeneration_score | numeric(5,4) | ✓ | 0.0 | Regeneration depth score (0.0 - 1.0) |
| catalytic_multiplier | numeric(5,4) | ✓ | 1.0 | How much this action amplifies other ... |
| verified | boolean | ✓ | false | Whether the action has been verified ... |
| verifier_ids | ARRAY | ✓ | '{}'::text[] | Array of Stellar account IDs who veri... |
| evidence_urls | ARRAY | ✓ | '{}'::text[] | URLs to evidence supporting this action |
| verification_count | integer (gen) | ✓ | - | - |
| ubectt_awarded | numeric(20,7) | ✓ | 0.0 | Amount of UBECtt tokens awarded for t... |
| distribution_tx_hash | varchar(64) | ✓ | - | Stellar transaction hash of the token... |
| reward_calculated_at | timestamp with time zone | ✓ | - | - |
| reward_distributed_at | timestamp with time zone | ✓ | - | - |
| tags | ARRAY | ✓ | '{}'::text[] | Tags for categorization and search |
| related_actions | ARRAY | ✓ | '{}'::text[] | IDs of related transformative actions |
| metadata | jsonb | ✓ | '{}'::jsonb | Additional metadata in JSON format |

**Constraints:**
- `fk_transformative_agent` (FOREIGN KEY)
- `transformative_actions_action_id_key` (UNIQUE)
- `transformative_actions_catalytic_multiplier_check` (CHECK)
- `transformative_actions_direct_beneficiaries_check` (CHECK)
- `transformative_actions_indirect_reach_check` (CHECK)
- `transformative_actions_pkey` (PRIMARY KEY)
- `transformative_actions_regeneration_score_check` (CHECK)
- `transformative_actions_ubectt_awarded_check` (CHECK)

#### ubec_main.ubec_audit_log

*Audit trail for Fire element transformation validation*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_audit_log_id_... | - |
| element | enum | ✓ | - | - |
| token_code | enum | ✓ | - | - |
| entity_type | varchar(50) | ✗ | - | - |
| entity_id | varchar(100) | ✗ | - | - |
| audit_type | varchar(50) | ✗ | - | - |
| status | varchar(20) | ✗ | - | - |
| is_valid | boolean | ✓ | true | - |
| is_anomaly | boolean | ✓ | false | - |
| anomaly_type | varchar(50) | ✓ | - | - |
| severity | varchar(20) | ✓ | - | - |
| audit_details | jsonb | ✓ | - | - |
| validation_rules | jsonb | ✓ | - | - |
| violations | jsonb | ✓ | - | - |
| audited_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| auditor | varchar(100) | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `ubec_audit_log_pkey` (PRIMARY KEY)

#### ubec_main.ubec_balances

*Token balances for all four elements with distribution tracking*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_balances_id_s... | - |
| account_id | varchar(56) | ✗ | - | - |
| token_code | enum | ✗ | - | - |
| element | enum | ✗ | - | - |
| balance | numeric(20,7) | ✗ | 0 | - |
| buying_liabilities | numeric(20,7) | ✓ | 0 | - |
| selling_liabilities | numeric(20,7) | ✓ | 0 | - |
| limit_amount | numeric(20,7) | ✓ | - | - |
| is_authorized | boolean | ✓ | false | - |
| is_authorized_to_maintain_liabilities | boolean | ✓ | false | - |
| is_clawback_enabled | boolean | ✓ | false | - |
| distribution_category | enum | ✓ | - | - |
| last_modified_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| sync_timestamp | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `fk_balance_account` (FOREIGN KEY)
- `positive_balance` (CHECK)
- `ubec_balances_pkey` (PRIMARY KEY)
- `unique_account_token` (UNIQUE)

#### ubec_main.ubec_distributions

*Distribution tracking for tokenomics compliance (75/20/5)*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_distributions... | - |
| token_code | enum | ✗ | - | - |
| element | enum | ✗ | - | - |
| category | enum | ✗ | - | - |
| target_percentage | numeric(5,2) | ✗ | - | - |
| current_percentage | numeric(5,2) | ✗ | - | - |
| current_amount | numeric(20,7) | ✗ | - | - |
| total_supply | numeric(20,7) | ✗ | - | - |
| is_compliant | boolean | ✓ | true | - |
| deviation | numeric(5,2) | ✓ | 0 | - |
| snapshot_time | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| last_rebalance | timestamp with time zone | ✓ | - | - |
| next_check | timestamp with time zone | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `ubec_distributions_pkey` (PRIMARY KEY)
- `valid_current_pct` (CHECK)
- `valid_percentages` (CHECK)

#### ubec_main.ubec_holonic_metrics

*Ubuntu principle metrics for holonic health assessment*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_holonic_metri... | - |
| account_id | varchar(56) | ✓ | - | - |
| element | enum | ✓ | - | - |
| principle | enum | ✗ | - | - |
| score | numeric(5,4) | ✗ | - | - |
| raw_value | numeric(20,7) | ✓ | - | - |
| normalized_value | numeric(5,4) | ✓ | - | - |
| health_status | enum | ✓ | - | - |
| assessment_details | jsonb | ✓ | - | - |
| calculation_method | varchar(100) | ✓ | - | - |
| data_points | integer | ✓ | - | - |
| confidence_level | numeric(5,4) | ✓ | - | - |
| calculated_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| valid_until | timestamp with time zone | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `fk_holonic_account` (FOREIGN KEY)
- `ubec_holonic_metrics_pkey` (PRIMARY KEY)
- `valid_normalized` (CHECK)
- `valid_score` (CHECK)

#### ubec_main.ubec_reports

*Generated reports for analysis and compliance*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_reports_id_se... | - |
| element | enum | ✓ | - | - |
| token_code | enum | ✓ | - | - |
| report_type | varchar(50) | ✗ | - | - |
| title | varchar(255) | ✗ | - | - |
| summary | text | ✓ | - | - |
| content | jsonb | ✗ | - | - |
| generated_by | varchar(100) | ✓ | - | - |
| report_period_start | timestamp with time zone | ✓ | - | - |
| report_period_end | timestamp with time zone | ✓ | - | - |
| status | varchar(20) | ✓ | 'draft'::character varying | - |
| generated_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| published_at | timestamp with time zone | ✓ | - | - |
| file_path | varchar(500) | ✓ | - | - |
| file_format | varchar(20) | ✓ | - | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `ubec_reports_pkey` (PRIMARY KEY)

#### ubec_main.ubec_sync_status

*Synchronization status tracking for all elements*

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_sync_status_i... | - |
| element | enum | ✓ | - | - |
| token_code | enum | ✓ | - | - |
| sync_type | varchar(50) | ✗ | - | - |
| status | varchar(20) | ✗ | - | - |
| cursor | varchar(100) | ✓ | - | - |
| last_sync_time | timestamp with time zone | ✓ | - | - |
| next_sync_time | timestamp with time zone | ✓ | - | - |
| records_synced | integer | ✓ | 0 | - |
| errors_encountered | integer | ✓ | 0 | - |
| duration_ms | integer | ✓ | - | - |
| sync_details | jsonb | ✓ | - | - |
| error_log | jsonb | ✓ | - | - |
| created_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP | - |
| metadata | jsonb | ✓ | - | - |

**Constraints:**
- `ubec_sync_status_pkey` (PRIMARY KEY)
- `unique_sync_context` (UNIQUE)

### Views

#### active_verified_actions

```sql

```

#### agent_transformation_profile

```sql

```

#### fire_element_metrics

```sql

```

#### stellar_operations_with_destination

```sql

```

#### transaction_operations

```sql

```

#### transformation_phase_summary

```sql

```

#### ubec_operations

```sql

```

#### v_account_lp_positions

```sql

```

#### v_complete_account_balances

```sql

```

#### v_distribution_with_lp

```sql

```

#### v_lp_totals_by_token

```sql

```

#### v_market_imbalance

```sql

```

#### v_orderbook_depth

```sql

```

#### v_top_traders

```sql

```

#### view_air_gateway

```sql

```

#### view_earth_stability

```sql

```

#### view_fire_transformation

```sql

```

#### view_system_holonic_health

```sql

```

#### view_user_permissions

```sql

```

#### view_water_flow

```sql

```

### Functions

#### armor(bytea)

- **Returns:** text
- **Language:** c

#### armor(bytea, text[], text[])

- **Returns:** text
- **Language:** c

#### calculate_phase_momentum(p_phase_id character varying)

- **Returns:** numeric
- **Language:** plpgsql
- **Description:** Calculates the transformation momentum for a phase based on recent actions

#### calculate_transformation_score(p_impact_scale impact_scale, p_regeneration_score numeric, p_catalytic_multiplier numeric, p_verified boolean)

- **Returns:** numeric
- **Language:** plpgsql
- **Description:** Calculates the transformation score for a transformative action based on multiple factors

#### check_distribution_compliance(p_token_code token_code, p_tolerance numeric DEFAULT 5.0)

- **Returns:** boolean
- **Language:** plpgsql
- **Description:** Checks if token distribution is within compliance tolerance

#### check_orderbook_table_sizes()

- **Returns:** TABLE(table_name text, row_count bigint, total_size text, table_size text, indexes_size text)
- **Language:** plpgsql
- **Description:** Check size and row counts of order book tables

#### crypt(text, text)

- **Returns:** text
- **Language:** c

#### dearmor(text)

- **Returns:** bytea
- **Language:** c

#### decrypt(bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### decrypt_iv(bytea, bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### digest(bytea, text)

- **Returns:** bytea
- **Language:** c

#### digest(text, text)

- **Returns:** bytea
- **Language:** c

#### encrypt(bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### encrypt_iv(bytea, bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### ensure_stellar_account_exists(p_account_id character varying)

- **Returns:** boolean
- **Language:** plpgsql

#### evaluation_date_immutable(timestamp with time zone)

- **Returns:** date
- **Language:** sql

#### extract_date_immutable(ts timestamp with time zone)

- **Returns:** date
- **Language:** plpgsql
- **Description:** Immutable function to extract date from timestamp for use in indexes

#### gen_random_bytes(integer)

- **Returns:** bytea
- **Language:** c

#### gen_random_uuid()

- **Returns:** uuid
- **Language:** c

#### gen_salt(text)

- **Returns:** text
- **Language:** c

#### gen_salt(text, integer)

- **Returns:** text
- **Language:** c

#### get_distribution_percentages(p_asset_code character varying, p_asset_issuer character varying)

- **Returns:** TABLE(general_pct numeric, admin_pct numeric, stewardship_pct numeric, total_supply numeric, is_compliant boolean)
- **Language:** plpgsql
- **Description:** Calculate current distribution percentages and compliance

#### get_element_for_principle(principle ubuntu_principle)

- **Returns:** element_type
- **Language:** plpgsql
- **Description:** Maps Ubuntu principle to corresponding element type

#### get_element_for_token(token token_code)

- **Returns:** element_type
- **Language:** plpgsql
- **Description:** Maps token code to corresponding element type

#### get_latest_holonic_score(p_element element_type, p_principle ubuntu_principle)

- **Returns:** numeric
- **Language:** plpgsql
- **Description:** Gets latest average holonic score for element/principle

#### get_setting(p_key character varying)

- **Returns:** text
- **Language:** plpgsql

#### get_settings_by_category(p_category character varying)

- **Returns:** TABLE(setting_key character varying, setting_value text, setting_type character varying, description text)
- **Language:** plpgsql

#### hmac(text, text, text)

- **Returns:** bytea
- **Language:** c

#### hmac(bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### insert_account_if_not_exists(p_account_id character varying, p_primary_element element_type DEFAULT NULL::element_type, p_token_holdings token_code[] DEFAULT NULL::token_code[])

- **Returns:** integer
- **Language:** plpgsql
- **Description:** Safely inserts a Stellar account only if it does not already exist

#### pgp_armor_headers(text, OUT key text, OUT value text)

- **Returns:** SETOF record
- **Language:** c

#### pgp_key_id(bytea)

- **Returns:** text
- **Language:** c

#### pgp_pub_decrypt(bytea, bytea, text)

- **Returns:** text
- **Language:** c

#### pgp_pub_decrypt(bytea, bytea, text, text)

- **Returns:** text
- **Language:** c

#### pgp_pub_decrypt(bytea, bytea)

- **Returns:** text
- **Language:** c

#### pgp_pub_decrypt_bytea(bytea, bytea)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_decrypt_bytea(bytea, bytea, text, text)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_decrypt_bytea(bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_encrypt(text, bytea)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_encrypt(text, bytea, text)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_encrypt_bytea(bytea, bytea)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_encrypt_bytea(bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### pgp_sym_decrypt(bytea, text, text)

- **Returns:** text
- **Language:** c

#### pgp_sym_decrypt(bytea, text)

- **Returns:** text
- **Language:** c

#### pgp_sym_decrypt_bytea(bytea, text)

- **Returns:** bytea
- **Language:** c

#### pgp_sym_decrypt_bytea(bytea, text, text)

- **Returns:** bytea
- **Language:** c

#### pgp_sym_encrypt(text, text)

- **Returns:** bytea
- **Language:** c

#### pgp_sym_encrypt(text, text, text)

- **Returns:** bytea
- **Language:** c

#### pgp_sym_encrypt_bytea(bytea, text, text)

- **Returns:** bytea
- **Language:** c

#### pgp_sym_encrypt_bytea(bytea, text)

- **Returns:** bytea
- **Language:** c

#### record_distribution_check(p_asset_code character varying, p_asset_issuer character varying, p_general_balance numeric, p_admin_balance numeric, p_stewardship_balance numeric, p_total_supply numeric, p_rebalance_needed boolean, p_details jsonb)

- **Returns:** integer
- **Language:** plpgsql

#### refresh_orderbook_summary()

- **Returns:** void
- **Language:** plpgsql
- **Description:** Refresh orderbook summary materialized view

#### refresh_orderbook_summary_now()

- **Returns:** text
- **Language:** plpgsql
- **Description:** Manually refresh orderbook summary with error handling

#### set_evaluation_date_date()

- **Returns:** trigger
- **Language:** plpgsql

#### set_setting(p_key character varying, p_value text, p_updated_by character varying DEFAULT NULL::character varying)

- **Returns:** boolean
- **Language:** plpgsql

#### sync_lp_pool_metadata()

- **Returns:** trigger
- **Language:** plpgsql
- **Description:** Automatically sets token_code and element for liquidity pools on insert/update

#### update_account_position()

- **Returns:** trigger
- **Language:** plpgsql
- **Description:** Trigger function to update account positions on offer changes

#### update_asset_holder_balance(p_account_id character varying, p_asset_code character varying, p_asset_issuer character varying, p_balance numeric)

- **Returns:** void
- **Language:** plpgsql
- **Description:** Update or insert asset holder balance

#### update_distribution_transfers_updated_at()

- **Returns:** trigger
- **Language:** plpgsql

#### update_holonic_metrics_timestamp()

- **Returns:** trigger
- **Language:** plpgsql

#### update_lp_ownership_percentages()

- **Returns:** trigger
- **Language:** plpgsql
- **Description:** Recalculates ownership percentages and balances when pool data changes

#### update_modified_timestamp()

- **Returns:** trigger
- **Language:** plpgsql

#### update_monitored_accounts_timestamp()

- **Returns:** trigger
- **Language:** plpgsql

#### update_system_settings_timestamp()

- **Returns:** trigger
- **Language:** plpgsql

#### update_timestamp()

- **Returns:** trigger
- **Language:** plpgsql

#### update_transformation_phases_timestamp()

- **Returns:** trigger
- **Language:** plpgsql

#### update_transformative_actions_timestamp()

- **Returns:** trigger
- **Language:** plpgsql

#### update_updated_at_column()

- **Returns:** trigger
- **Language:** plpgsql

#### update_updated_timestamp()

- **Returns:** trigger
- **Language:** plpgsql

#### uuid_generate_v1()

- **Returns:** uuid
- **Language:** c

#### uuid_generate_v1mc()

- **Returns:** uuid
- **Language:** c

#### uuid_generate_v3(namespace uuid, name text)

- **Returns:** uuid
- **Language:** c

#### uuid_generate_v4()

- **Returns:** uuid
- **Language:** c

#### uuid_generate_v5(namespace uuid, name text)

- **Returns:** uuid
- **Language:** c

#### uuid_nil()

- **Returns:** uuid
- **Language:** c

#### uuid_ns_dns()

- **Returns:** uuid
- **Language:** c

#### uuid_ns_oid()

- **Returns:** uuid
- **Language:** c

#### uuid_ns_url()

- **Returns:** uuid
- **Language:** c

#### uuid_ns_x500()

- **Returns:** uuid
- **Language:** c

#### verify_user_setup()

- **Returns:** TABLE(role_name text, can_login boolean, is_superuser boolean, connection_limit integer, table_privileges text)
- **Language:** plpgsql

---

