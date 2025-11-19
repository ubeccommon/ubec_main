# UBEC Protocol Suite - Comprehensive Database Documentation

*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.*

**Generated:** 2025-11-19T12:03:03.443084

**Database:** ubec

**PostgreSQL Version:** PostgreSQL 15.13 (Debian 15.13-0+deb12u1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14+deb12u1) 12.2.0, 64-bit

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Extensions](#extensions)
3. [Security](#security)
   - [Database Users](#database-users)
   - [Database Roles](#database-roles)
4. [Schemas](#schemas)
   - [phenomenal](#phenomenal)
   - [public](#public)
   - [topology](#topology)
   - [ubec_main](#ubec-main)

---

## Database Overview

### Summary Statistics

- **Total Schemas:** 4
- **Total Tables:** 80
- **Total Views:** 35
- **Total Functions:** 1142
- **Total Rows:** 155,571
- **Total Columns:** 1,003
- **Total Foreign Keys:** 31

### Schema Summary

| Schema | Tables | Views | Functions | Rows | Size |
|--------|--------|-------|-----------|------|------|
| phenomenal | 28 | 13 | 19 | 1,297 | 742 MB |
| public | 1 | 2 | 940 | 8,500 | 7144 kB |
| topology | 2 | 0 | 103 | 0 | 48 kB |
| ubec_main | 49 | 20 | 80 | 145,774 | 105 MB |

---

## Extensions

| Extension | Version | Schema | Description |
|-----------|---------|--------|-------------|
| btree_gist | 1.7 | public | support for indexing common datatypes in GiST |
| pg_trgm | 1.6 | public | text similarity measurement and index searching based on trigrams |
| pgcrypto | 1.3 | ubec_main | cryptographic functions |
| plpgsql | 1.0 | pg_catalog | PL/pgSQL procedural language |
| postgis | 3.3.2 | public | PostGIS geometry and geography spatial types and functions |
| postgis_topology | 3.3.2 | topology | PostGIS topology spatial types and functions |
| uuid-ossp | 1.1 | ubec_main | generate universally unique identifiers (UUIDs) |

---

## Security

### Database Users

#### dump_ubec

- **User ID:** 22624702
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No

#### ms_read

- **User ID:** 37491082
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No

#### postgres

- **User ID:** 10
- **Superuser:** Yes
- **Can Create DB:** Yes
- **Can Replicate:** Yes
- **Bypass RLS:** Yes

#### recipro

- **User ID:** 20586767
- **Superuser:** No
- **Can Create DB:** Yes
- **Can Replicate:** No
- **Bypass RLS:** No

#### stellar

- **User ID:** 16389
- **Superuser:** No
- **Can Create DB:** Yes
- **Can Replicate:** No
- **Bypass RLS:** No

#### ubec_admin

- **User ID:** 37483315
- **Superuser:** Yes
- **Can Create DB:** Yes
- **Can Replicate:** Yes
- **Bypass RLS:** No

#### ubec_app

- **User ID:** 37483316
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No

#### ubec_map

- **User ID:** 37499650
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No

#### ubec_readonly

- **User ID:** 37483317
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No

#### ubec_sync

- **User ID:** 37483318
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No

#### ubecgpi_app

- **User ID:** 30297735
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No

#### ubecgpi_readonly

- **User ID:** 30297736
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No

### Database Roles

#### dump_ubec

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### etf_manager

- **Can Login:** No
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### ms_read

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### postgres

- **Can Login:** Yes
- **Superuser:** Yes
- **Inherit Privileges:** Yes
- **Can Create Role:** Yes
- **Can Create DB:** Yes

#### recipro

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** Yes

#### reward_admin

- **Can Login:** No
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### reward_data_writer

- **Can Login:** No
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### reward_read_only

- **Can Login:** No
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### stellar

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** Yes

#### ubec_admin

- **Can Login:** Yes
- **Superuser:** Yes
- **Inherit Privileges:** Yes
- **Can Create Role:** Yes
- **Can Create DB:** Yes

#### ubec_app

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### ubec_map

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### ubec_readonly

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### ubec_sync

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### ubecgpi_app

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

#### ubecgpi_readonly

- **Can Login:** Yes
- **Superuser:** No
- **Inherit Privileges:** Yes
- **Can Create Role:** No
- **Can Create DB:** No

---

## Schemas

## phenomenal

*Phenomenological Quantum Gravity Schema - Advanced analytics and network topology*

**Tables:** 28 | **Views:** 13 | **Functions:** 19 | **Total Rows:** 1,297 | **Size:** 742 MB

### Schema Permissions

- **ubec_app:** USAGE

### Sequences

#### Ecoregions2017_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ecoregions_2017.id

#### Ecoregions2017_id_seq1

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** Ecoregions2017.id

#### accounts_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** accounts.id

#### assets_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** assets.id

#### bioregion_boundaries_gid_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** bioregion_boundaries.gid

#### feow_hydrosheds_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** feow_hydrosheds.id

#### geoBoundariesCGAZ_ADM0_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** geoBoundariesCGAZ_ADM0.id

#### geoBoundariesCGAZ_ADM1_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** geoBoundariesCGAZ_ADM1.id

#### geoBoundariesCGAZ_ADM2_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** geoBoundariesCGAZ_ADM2.id

#### geodesics_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** geodesics.id

#### gravitational_fields_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** gravitational_fields.id

#### gravitational_interactions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** gravitational_interactions.id

#### gravitational_mass_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** gravitational_mass.id

#### holons_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** holons.id

#### intentional_relations_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** intentional_relations.id

#### lorentz_violation_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** lorentz_violation.id

#### network_embeddings_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** network_embeddings.id

#### points_of_interest_gid_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** points_of_interest.gid

#### protentions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** protentions.id

#### quantum_entanglement_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** quantum_entanglement.id

#### quantum_gravity_signatures_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** quantum_gravity_signatures.id

#### quantum_states_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** quantum_states.id

#### retentions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** retentions.id

#### spacetime_curvature_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** spacetime_curvature.id

#### spatial_positions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** spatial_positions.id

#### transactions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 9223372036854775807
- **Cache:** 1
- **Owned By:** transactions.id

#### ubec_bioregions_gid_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ubec_bioregions.gid

#### ubec_poi_gid_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ubec_poi.gid

### Tables

#### Ecoregions2017

**Rows:** N/A | **Size:** 16 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('"Ecoregions2017_id_seq1"'::regclass) |
| geom | USER-DEFINED | ✓ |  |

**Primary Key:**
- Ecoregions2017_pkey1: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### accounts

*Accounts as Dasein: beings situated in the blockchain world with intentional directedness*

**Rows:** 0 | **Size:** 80 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('accounts_id_seq'::regclass) |
| account_address | character varying(56) | ✗ |  |
| dasein_type | character varying(50) | ✗ | 'participant'::character varying |
| comportment_pattern | character varying(50) | ✓ |  |
| holonic_category | USER-DEFINED | ✗ | 'network_node'::holonic_category |
| thrown_at | timestamp with time zone | ✗ |  |
| facticity | jsonb | ✓ |  |
| network_position | USER-DEFINED | ✓ |  |
| spatial_context | jsonb | ✓ |  |
| primary_intentions | ARRAY | ✓ |  |
| intention_strength | jsonb | ✓ |  |
| internal_horizon | jsonb | ✗ | '{}'::jsonb |
| external_horizon | jsonb | ✗ | '{}'::jsonb |
| ubuntu_scores | jsonb | ✓ |  |
| retained_states | jsonb | ✓ |  |
| present_state | jsonb | ✗ |  |
| anticipated_states | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- accounts_pkey: (id)

**Unique Constraints:**
- accounts_account_address_key: (account_address)

**Indexes:**
- UNIQUE BTREE: (account_address) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (comportment_pattern) - 8192 bytes
- BTREE: (holonic_category) - 8192 bytes
- GIN: (primary_intentions) - 16 kB
- GIN: (internal_horizon) - 16 kB
- GIST: (network_position) - 8192 bytes

**Triggers:**
- **trg_account_gravity:** AFTER INSERT OR UPDATE ROW
  - Calls: auto_calculate_gravity
- **trg_accounts_updated_at:** BEFORE UPDATE ROW
  - Calls: update_updated_at_column
- **trg_maintain_account_retentions:** AFTER UPDATE ROW
  - Calls: maintain_retentions_trigger

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### assets

*Assets as phenomena: things as they appear in the blockchain, with internal/external horizons*

**Rows:** 0 | **Size:** 88 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('assets_id_seq'::regclass) |
| asset_code | character varying(12) | ✗ |  |
| issuer_address | character varying(56) | ✗ |  |
| phenomenal_mode | USER-DEFINED | ✗ | 'fully_present'::phenomenal_mode |
| existence_mode | USER-DEFINED | ✗ | 'present_at_hand'::existence_mode |
| ubuntu_principle | USER-DEFINED | ✓ |  |
| internal_horizon | jsonb | ✗ | '{}'::jsonb |
| external_horizon | jsonb | ✗ | '{}'::jsonb |
| genesis_at | timestamp with time zone | ✗ |  |
| retained_history | jsonb | ✓ |  |
| present_state | jsonb | ✗ |  |
| protended_futures | jsonb | ✓ |  |
| temporal_horizon | USER-DEFINED | ✗ | 'intermediate'::temporal_horizon |
| network_position | USER-DEFINED | ✓ |  |
| topology_metadata | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- assets_pkey: (id)

**Unique Constraints:**
- assets_asset_code_issuer_address_key: (asset_code, issuer_address)

**Indexes:**
- UNIQUE BTREE: (asset_code, issuer_address) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- GIN: (external_horizon) - 16 kB
- GIN: (internal_horizon) - 16 kB
- BTREE: (phenomenal_mode, existence_mode) - 8192 bytes
- GIST: (network_position) - 8192 bytes
- BTREE: (genesis_at, temporal_horizon) - 8192 bytes
- BTREE: (ubuntu_principle) - 8192 bytes

**Triggers:**
- **trg_asset_gravity:** AFTER INSERT OR UPDATE ROW
  - Calls: auto_calculate_gravity
- **trg_assets_updated_at:** BEFORE UPDATE ROW
  - Calls: update_updated_at_column
- **trg_maintain_asset_retentions:** AFTER UPDATE ROW
  - Calls: maintain_retentions_trigger

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### bioregion_boundaries

*UBEC Protocol bioregion boundaries with ecological and community metadata. Part of PHENOMENAL analytics schema. Used by Mapbender Digitizer.*

**Rows:** 1 | **Size:** 160 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| gid *(Unique identifier (auto-generated))* | integer(32) | ✗ | nextval('bioregion_boundaries_gid_seq'::regclass) |
| bioregion_name | character varying(255) | ✗ |  |
| bioregion_code | character varying(50) | ✓ |  |
| status *(Workflow status: proposed → under_review → approved → active)* | character varying(50) | ✓ | 'proposed'::character varying |
| geom *(Polygon geometry in WGS84 (SRID 4326))* | USER-DEFINED | ✗ |  |
| area_sqkm *(Area in square kilometers (auto-calculated on insert/update))* | numeric(12,2) | ✓ |  |
| centroid_lat | numeric(10,6) | ✓ |  |
| centroid_lon | numeric(10,6) | ✓ |  |
| primary_watershed *(Primary watershed/river basin defining the bioregion)* | character varying(255) | ✓ |  |
| ecoregion_level2 | character varying(255) | ✓ |  |
| ecoregion_level3 | character varying(255) | ✓ |  |
| elevation_range | character varying(100) | ✓ |  |
| climate_zone | character varying(100) | ✓ |  |
| dominant_ecosystems | text | ✓ |  |
| boundary_description | text | ✓ |  |
| boundary_rationale | text | ✓ |  |
| north_boundary | character varying(255) | ✓ |  |
| east_boundary | character varying(255) | ✓ |  |
| south_boundary | character varying(255) | ✓ |  |
| west_boundary | character varying(255) | ✓ |  |
| key_natural_features | text | ✓ |  |
| population_estimate | integer(32) | ✓ |  |
| major_communities | text | ✓ |  |
| indigenous_territories | character varying(255) | ✓ |  |
| economic_focus | text | ✓ |  |
| submitted_by | character varying(255) | ✓ |  |
| contact_email | character varying(255) | ✓ |  |
| organization | character varying(255) | ✓ |  |
| submission_date | timestamp without time zone | ✓ | now() |
| approved_date | timestamp without time zone | ✓ |  |
| approved_by | character varying(255) | ✓ |  |
| last_modified | timestamp without time zone | ✓ | now() |
| modified_by | character varying(255) | ✓ |  |
| attachment_path | character varying(500) | ✓ |  |
| map_image_path | character varying(500) | ✓ |  |
| notes | text | ✓ |  |
| tags | character varying(255) | ✓ |  |
| internal_notes | text | ✓ |  |
| ubec_allocation *(Air token (UBEC) allocation for this bioregion)* | numeric(18,7) | ✓ |  |
| water_allocation *(Water token (UBECrc) allocation)* | numeric(18,7) | ✓ |  |
| earth_allocation *(Earth token (UBECgpi) allocation)* | numeric(18,7) | ✓ |  |
| fire_allocation *(Fire token (UBECtt) allocation)* | numeric(18,7) | ✓ |  |

**Primary Key:**
- bioregion_boundaries_pkey: (gid)

**Unique Constraints:**
- bioregion_boundaries_bioregion_code_key: (bioregion_code)

**Check Constraints:**
- positive_area: CHECK (((area_sqkm IS NULL) OR (area_sqkm > (0)::numeric)))
- positive_population: CHECK (((population_estimate IS NULL) OR (population_estimate > 0)))
- valid_email: CHECK (((contact_email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'::text))
- valid_status: CHECK (((status)::text = ANY ((ARRAY['proposed'::character varying, 'under_review'::character varying, 'approved'::character varying, 'active'::character varying, 'inactive'::character varying, 'archived'::character varying])::text[])))

**Indexes:**
- UNIQUE BTREE: (bioregion_code) - 16 kB
- PRIMARY UNIQUE BTREE: (gid) - 16 kB
- BTREE: (bioregion_code) - 16 kB
- GIST: (geom) - 8192 bytes
- BTREE: (bioregion_name) - 16 kB
- GIN: () - 24 kB
- BTREE: (status) - 16 kB
- BTREE: (submission_date) - 16 kB
- BTREE: (primary_watershed) - 16 kB

**Triggers:**
- **update_bioregion_geometry_trigger:** BEFORE INSERT OR UPDATE ROW
  - Calls: update_bioregion_geometry
- **validate_bioregion_geometry_trigger:** BEFORE INSERT OR UPDATE ROW
  - Calls: validate_bioregion_geometry

**Permissions:**
- **ubec_app:** SELECT

---

#### ecoregions_2017

**Rows:** 847 | **Size:** 206 MB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('"Ecoregions2017_id_seq"'::regclass) |
| geom | USER-DEFINED | ✓ |  |
| objectid | numeric | ✓ |  |
| eco_name | character varying(150) | ✓ |  |
| biome_num | numeric | ✓ |  |
| biome_name | character varying(254) | ✓ |  |
| realm | character varying(254) | ✓ |  |
| eco_biome_ | character varying(254) | ✓ |  |
| nnh | bigint(64) | ✓ |  |
| eco_id | bigint(64) | ✓ |  |
| shape_leng | numeric | ✓ |  |
| shape_area | numeric | ✓ |  |
| nnh_name | character varying(64) | ✓ |  |
| color | character varying(7) | ✓ |  |
| color_bio | character varying(7) | ✓ |  |
| color_nnh | character varying(7) | ✓ |  |
| license | character varying(64) | ✓ |  |

**Primary Key:**
- Ecoregions2017_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 40 kB
- GIST: (geom) - 40 kB
- GIST: (geom) - 40 kB

**Permissions:**
- **ms_read:** SELECT
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### feow_hydrosheds

**Rows:** 449 | **Size:** 20 MB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('feow_hydrosheds_id_seq'::regclass) |
| geom | USER-DEFINED | ✓ |  |
| feow_id | bigint(64) | ✓ |  |
| area_skm | double precision(53) | ✓ |  |

**Primary Key:**
- feow_hydrosheds_pkey: (id)

**Indexes:**
- GIST: (geom) - 24 kB
- PRIMARY UNIQUE BTREE: (id) - 32 kB
- GIST: (geom) - 24 kB

**Permissions:**
- **ms_read:** SELECT
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### geoBoundariesCGAZ_ADM0

**Rows:** N/A | **Size:** 154 MB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('"geoBoundariesCGAZ_ADM0_id_seq"'::regclass) |
| geom | USER-DEFINED | ✓ |  |
| shapegroup | character varying(80) | ✓ |  |
| shapetype | character varying(80) | ✓ |  |
| shapename | character varying(80) | ✓ |  |

**Primary Key:**
- geoBoundariesCGAZ_ADM0_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 16 kB
- GIST: (geom) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### geoBoundariesCGAZ_ADM1

**Rows:** N/A | **Size:** 141 MB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('"geoBoundariesCGAZ_ADM1_id_seq"'::regclass) |
| geom | USER-DEFINED | ✓ |  |
| shapename | character varying(80) | ✓ |  |
| shapeid | character varying(80) | ✓ |  |
| shapegroup | character varying(80) | ✓ |  |
| shapetype | character varying(80) | ✓ |  |

**Primary Key:**
- geoBoundariesCGAZ_ADM1_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 88 kB
- GIST: (geom) - 144 kB

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### geoBoundariesCGAZ_ADM2

**Rows:** N/A | **Size:** 219 MB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('"geoBoundariesCGAZ_ADM2_id_seq"'::regclass) |
| geom | USER-DEFINED | ✓ |  |
| shapename | character varying(80) | ✓ |  |
| shapeid | character varying(80) | ✓ |  |
| shapegroup | character varying(80) | ✓ |  |
| shapetype | character varying(80) | ✓ |  |

**Primary Key:**
- geoBoundariesCGAZ_ADM2_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 1096 kB
- GIST: (geom) - 1992 kB

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### geodesics

*Shortest paths (geodesics) through the network topology*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('geodesics_id_seq'::regclass) |
| from_account_id | integer(32) | ✗ |  |
| to_account_id | integer(32) | ✗ |  |
| path_length | integer(32) | ✗ |  |
| path_nodes | ARRAY | ✗ |  |
| path_edges | ARRAY | ✗ |  |
| path_line | USER-DEFINED | ✓ |  |
| weighted_distance | numeric(20,10) | ✓ |  |
| computed_at | timestamp with time zone | ✗ | now() |
| valid_until | timestamp with time zone | ✓ |  |

**Primary Key:**
- geodesics_pkey: (id)

**Foreign Keys:**
- geodesics_from_account_id_fkey: (from_account_id) → phenomenal.accounts(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE
- geodesics_to_account_id_fkey: (to_account_id) → phenomenal.accounts(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- geodesics_from_account_id_to_account_id_key: (from_account_id, to_account_id)

**Indexes:**
- UNIQUE BTREE: (from_account_id, to_account_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (from_account_id) - 8192 bytes
- GIST: (path_line) - 8192 bytes
- BTREE: (path_length) - 8192 bytes
- BTREE: (to_account_id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### gravitational_fields

*Gravitational fields: zones of influence surrounding massive entities*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('gravitational_fields_id_seq'::regclass) |
| source_mass_id | bigint(64) | ✗ |  |
| field_profile | jsonb | ✗ |  |
| influence_radius | numeric(20,10) | ✗ |  |
| field_geometry | USER-DEFINED | ✓ |  |
| field_type | character varying(50) | ✗ |  |
| field_strength | numeric(20,10) | ✗ |  |
| is_static | boolean | ✗ | false |
| temporal_variation | jsonb | ✓ |  |
| calculated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- gravitational_fields_pkey: (id)

**Foreign Keys:**
- gravitational_fields_source_mass_id_fkey: (source_mass_id) → phenomenal.gravitational_mass(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Check Constraints:**
- gravitational_fields_field_strength_check: CHECK ((field_strength >= (0)::numeric))
- gravitational_fields_field_type_check: CHECK (((field_type)::text = ANY ((ARRAY['attractive'::character varying, 'repulsive'::character varying, 'neutral'::character varying, 'mixed'::character varying])::text[])))
- gravitational_fields_influence_radius_check: CHECK ((influence_radius >= (0)::numeric))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (source_mass_id) - 8192 bytes
- GIST: (field_geometry) - 8192 bytes
- BTREE: (field_strength) - 8192 bytes
- BTREE: (field_type) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### gravitational_interactions

*Pairwise gravitational forces between massive entities in the network*

**Rows:** 0 | **Size:** 64 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('gravitational_interactions_id_seq'::regclass) |
| entity1_mass_id | bigint(64) | ✗ |  |
| entity2_mass_id | bigint(64) | ✗ |  |
| force_magnitude | numeric(20,10) | ✗ |  |
| force_direction | numeric(10,6) | ✓ |  |
| force_vector | USER-DEFINED | ✓ |  |
| separation_distance | numeric(20,10) | ✗ |  |
| network_hops | integer(32) | ✓ |  |
| potential_energy | numeric(20,10) | ✓ |  |
| binding_energy | numeric(20,10) | ✓ |  |
| interaction_type | character varying(50) | ✗ |  |
| is_significant | boolean | ✗ | true |
| interaction_strength_history | jsonb | ✓ |  |
| measured_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- gravitational_interactions_pkey: (id)

**Foreign Keys:**
- gravitational_interactions_entity1_mass_id_fkey: (entity1_mass_id) → phenomenal.gravitational_mass(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE
- gravitational_interactions_entity2_mass_id_fkey: (entity2_mass_id) → phenomenal.gravitational_mass(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- gravitational_interactions_entity1_mass_id_entity2_mass_id__key: (entity1_mass_id, entity2_mass_id, measured_at)

**Check Constraints:**
- gravitational_interactions_check: CHECK ((entity1_mass_id <> entity2_mass_id))
- gravitational_interactions_force_magnitude_check: CHECK ((force_magnitude >= (0)::numeric))
- gravitational_interactions_interaction_type_check: CHECK (((interaction_type)::text = ANY ((ARRAY['attraction'::character varying, 'repulsion'::character varying, 'equilibrium'::character varying])::text[])))
- gravitational_interactions_separation_distance_check: CHECK ((separation_distance >= (0)::numeric))

**Indexes:**
- UNIQUE BTREE: (entity1_mass_id, entity2_mass_id, measured_at) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (entity1_mass_id, entity2_mass_id) - 8192 bytes
- BTREE: (force_magnitude) - 8192 bytes
- BTREE: (is_significant) - 8192 bytes
- GIST: (force_vector) - 8192 bytes
- BTREE: (interaction_type) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### gravitational_mass

*Network gravity: measure of entity importance and influence*

**Rows:** 0 | **Size:** 64 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('gravitational_mass_id_seq'::regclass) |
| entity_type | character varying(50) | ✗ |  |
| entity_id | bigint(64) | ✗ |  |
| gravitational_mass | numeric(20,10) | ✗ |  |
| inertial_mass | numeric(20,10) | ✗ |  |
| mass_basis | jsonb | ✗ |  |
| calculated_at | timestamp with time zone | ✗ | now() |
| valid_until | timestamp with time zone | ✓ |  |
| mass_trajectory | jsonb | ✓ |  |

**Primary Key:**
- gravitational_mass_pkey: (id)

**Unique Constraints:**
- gravitational_mass_entity_type_entity_id_calculated_at_key: (entity_type, entity_id, calculated_at)

**Check Constraints:**
- gravitational_mass_gravitational_mass_check: CHECK ((gravitational_mass >= (0)::numeric))
- gravitational_mass_inertial_mass_check: CHECK ((inertial_mass >= (0)::numeric))

**Indexes:**
- UNIQUE BTREE: (entity_type, entity_id, calculated_at) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- GIN: (mass_basis) - 16 kB
- BTREE: (entity_type, entity_id) - 8192 bytes
- BTREE: (calculated_at, valid_until) - 8192 bytes
- BTREE: (gravitational_mass) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### holons

*Holarchical structures: entities that are both autonomous wholes and integrated parts*

**Rows:** 0 | **Size:** 64 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('phenomenal.holons_id_seq'::regclass) |
| holon_name | character varying(255) | ✗ |  |
| holon_type | character varying(100) | ✗ |  |
| autonomy_score | numeric(5,4) | ✗ |  |
| integration_score | numeric(5,4) | ✗ |  |
| constituent_accounts | ARRAY | ✓ |  |
| constituent_assets | ARRAY | ✓ |  |
| constituent_relations | ARRAY | ✓ |  |
| parent_holons | ARRAY | ✓ |  |
| emergent_properties | jsonb | ✓ |  |
| collective_behavior | jsonb | ✓ |  |
| spatial_region | USER-DEFINED | ✓ |  |
| centroid | USER-DEFINED | ✓ |  |
| emerged_at | timestamp with time zone | ✗ |  |
| stable_from | timestamp with time zone | ✓ |  |
| dissolved_at | timestamp with time zone | ✓ |  |
| ubuntu_scores | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- holons_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (autonomy_score) - 8192 bytes
- GIST: (centroid) - 8192 bytes
- BTREE: (integration_score) - 8192 bytes
- GIST: (spatial_region) - 8192 bytes
- BTREE: (emerged_at, dissolved_at) - 8192 bytes
- BTREE: (holon_type) - 8192 bytes

**Triggers:**
- **trg_holon_gravity:** AFTER INSERT OR UPDATE ROW
  - Calls: auto_calculate_gravity

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### intentional_relations

*Intentional directedness: how accounts are related to assets and each other*

**Rows:** 0 | **Size:** 88 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('intentional_relations_id_seq'::regclass) |
| from_account_id | integer(32) | ✗ |  |
| to_account_id | integer(32) | ✓ |  |
| asset_id | integer(32) | ✓ |  |
| relation_type | USER-DEFINED | ✗ |  |
| phenomenal_mode | USER-DEFINED | ✗ | 'fully_present'::phenomenal_mode |
| noema | jsonb | ✗ |  |
| noesis | jsonb | ✗ |  |
| relation_strength | numeric(10,6) | ✗ | 0.5 |
| reciprocity_factor | numeric(10,6) | ✓ |  |
| stability_score | numeric(10,6) | ✓ |  |
| relation_line | USER-DEFINED | ✓ |  |
| geodesic_distance | numeric(20,10) | ✓ |  |
| euclidean_distance | numeric(20,10) | ✓ |  |
| emerged_at | timestamp with time zone | ✗ |  |
| retained_history | jsonb | ✓ |  |
| present_manifestation | jsonb | ✗ |  |
| protended_evolution | jsonb | ✓ |  |
| temporal_horizon | USER-DEFINED | ✗ | 'proximal'::temporal_horizon |
| active | boolean | ✗ | true |
| last_activity_at | timestamp with time zone | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- intentional_relations_pkey: (id)

**Foreign Keys:**
- intentional_relations_asset_id_fkey: (asset_id) → phenomenal.assets(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE
- intentional_relations_from_account_id_fkey: (from_account_id) → phenomenal.accounts(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE
- intentional_relations_to_account_id_fkey: (to_account_id) → phenomenal.accounts(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Check Constraints:**
- valid_relation_structure: CHECK ((((to_account_id IS NOT NULL) AND (asset_id IS NULL)) OR ((to_account_id IS NULL) AND (asset_id IS NOT NULL)) OR ((to_account_id IS NOT NULL) AND (asset_id IS NOT NULL))))

**Indexes:**
- BTREE: (asset_id, relation_type) - 8192 bytes
- BTREE: (from_account_id, relation_type) - 8192 bytes
- GIN: (noema) - 16 kB
- GIST: (relation_line) - 8192 bytes
- BTREE: (relation_strength) - 8192 bytes
- BTREE: (emerged_at, temporal_horizon) - 8192 bytes
- BTREE: (to_account_id, relation_type) - 8192 bytes
- BTREE: (relation_type, active) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Triggers:**
- **trg_relations_updated_at:** BEFORE UPDATE ROW
  - Calls: update_updated_at_column

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### lorentz_violation

*Lorentz symmetry violations: preferred directions and broken symmetries*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('lorentz_violation_id_seq'::regclass) |
| region_geometry | USER-DEFINED | ✗ |  |
| preferred_direction | USER-DEFINED | ✓ |  |
| anisotropy_vector | jsonb | ✗ |  |
| violation_magnitude | numeric(15,10) | ✗ |  |
| violation_type | character varying(100) | ✗ |  |
| dispersion_coefficients | jsonb | ✓ |  |
| speed_anisotropy | numeric(10,6) | ✓ |  |
| arrival_time_differences | jsonb | ✓ |  |
| test_statistic | numeric(15,10) | ✓ |  |
| significance_level | numeric(10,8) | ✓ |  |
| is_statistically_significant | boolean | ✓ |  |
| observed_at | timestamp with time zone | ✗ | now() |
| observation_count | integer(32) | ✗ | 1 |

**Primary Key:**
- lorentz_violation_pkey: (id)

**Check Constraints:**
- lorentz_violation_violation_magnitude_check: CHECK ((violation_magnitude >= (0)::numeric))
- lorentz_violation_violation_type_check: CHECK (((violation_type)::text = ANY ((ARRAY['rotation'::character varying, 'boost'::character varying, 'cpt'::character varying, 'space_isotropy'::character varying, 'time_reversal'::character varying, 'parity'::character varying])::text[])))

**Indexes:**
- BTREE: (violation_magnitude) - 8192 bytes
- BTREE: (is_statistically_significant) - 8192 bytes
- GIST: (region_geometry) - 8192 bytes
- BTREE: (violation_type) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### network_embeddings

**Rows:** 0 | **Size:** 24 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('network_embeddings_id_seq'::regclass) |
| computed_at | timestamp with time zone | ✗ | now() |
| embedding_method | character varying(100) | ✗ |  |
| dimensions | integer(32) | ✗ | 2 |
| parameters | jsonb | ✗ |  |
| quality_metrics | jsonb | ✓ |  |
| valid_from | timestamp with time zone | ✗ |  |
| valid_until | timestamp with time zone | ✓ |  |

**Primary Key:**
- network_embeddings_pkey: (id)

**Indexes:**
- BTREE: (valid_from, valid_until) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### points_of_interest

*Points of Interest for UBEC Protocol - farms, community centers, landmarks, resources, etc. Supports text, images, and rich metadata.*

**Rows:** 0 | **Size:** 104 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| gid *(Unique identifier (auto-generated))* | integer(32) | ✗ | nextval('points_of_interest_gid_seq'::regclass) |
| poi_name | character varying(255) | ✗ |  |
| poi_code | character varying(50) | ✓ |  |
| poi_type *(Type: farm, community_center, resource, landmark, meeting_place, etc.)* | character varying(100) | ✗ |  |
| status | character varying(50) | ✓ | 'active'::character varying |
| geom *(Point geometry in WGS84 (SRID 4326))* | USER-DEFINED | ✗ |  |
| latitude | numeric(10,6) | ✓ |  |
| longitude | numeric(10,6) | ✓ |  |
| elevation_m | numeric(8,2) | ✓ |  |
| bioregion_gid *(References bioregion_boundaries.gid if POI is within a bioregion)* | integer(32) | ✓ |  |
| bioregion_name | character varying(255) | ✓ |  |
| address | text | ✓ |  |
| locality | character varying(255) | ✓ |  |
| region | character varying(255) | ✓ |  |
| country | character varying(100) | ✓ |  |
| short_description | text | ✓ |  |
| full_description | text | ✓ |  |
| keywords | character varying(500) | ✓ |  |
| primary_image_path *(Image path relative to Mapbender uploads directory. Recommended structure: /uploads/poi/{gid}/primary.jpg)* | character varying(500) | ✓ |  |
| image_gallery_paths *(JSON array of paths. Example: ["/uploads/poi/123/gallery1.jpg", "/uploads/poi/123/gallery2.jpg"])* | text | ✓ |  |
| video_url | character varying(500) | ✓ |  |
| audio_url | character varying(500) | ✓ |  |
| document_path | character varying(500) | ✓ |  |
| contact_person | character varying(255) | ✓ |  |
| contact_email | character varying(255) | ✓ |  |
| contact_phone | character varying(50) | ✓ |  |
| website_url | character varying(500) | ✓ |  |
| operating_hours | text | ✓ |  |
| seasonal_availability | character varying(100) | ✓ |  |
| accessibility_info | text | ✓ |  |
| primary_category | character varying(100) | ✓ |  |
| secondary_categories | character varying(255) | ✓ |  |
| tags | character varying(500) | ✓ |  |
| ubec_account_id | character varying(100) | ✓ |  |
| affiliated_organization | character varying(255) | ✓ |  |
| role_type *(UBEC role type if applicable)* | character varying(50) | ✓ |  |
| submitted_by | character varying(255) | ✓ |  |
| submission_date | timestamp without time zone | ✓ | now() |
| verified_date | timestamp without time zone | ✓ |  |
| verified_by | character varying(255) | ✓ |  |
| last_modified | timestamp without time zone | ✓ | now() |
| modified_by | character varying(255) | ✓ |  |
| visibility *(public: everyone, bioregion: bioregion members only, private: owner only)* | character varying(50) | ✓ | 'public'::character varying |
| featured | boolean | ✓ | false |
| notes | text | ✓ |  |
| internal_notes | text | ✓ |  |

**Primary Key:**
- points_of_interest_pkey: (gid)

**Unique Constraints:**
- points_of_interest_poi_code_key: (poi_code)

**Check Constraints:**
- points_of_interest_role_type_check: CHECK (((role_type)::text = ANY ((ARRAY['farmer'::character varying, 'community'::character varying, 'activator'::character varying, 'living_lab'::character varying, 'other'::character varying, NULL::character varying])::text[])))
- points_of_interest_visibility_check: CHECK (((visibility)::text = ANY ((ARRAY['public'::character varying, 'bioregion'::character varying, 'private'::character varying])::text[])))
- valid_elevation: CHECK (((elevation_m IS NULL) OR ((elevation_m >= ('-500'::integer)::numeric) AND (elevation_m <= (9000)::numeric))))
- valid_email: CHECK (((contact_email IS NULL) OR ((contact_email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'::text)))
- valid_status: CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'pending'::character varying, 'archived'::character varying])::text[])))

**Indexes:**
- BTREE: (bioregion_gid) - 8192 bytes
- BTREE: (primary_category) - 8192 bytes
- BTREE: (featured) - 8192 bytes
- GIST: (geom) - 8192 bytes
- BTREE: (poi_name) - 8192 bytes
- GIN: () - 16 kB
- BTREE: (status) - 8192 bytes
- BTREE: (poi_type) - 8192 bytes
- BTREE: (visibility) - 8192 bytes
- PRIMARY UNIQUE BTREE: (gid) - 8192 bytes
- UNIQUE BTREE: (poi_code) - 8192 bytes

**Triggers:**
- **assign_poi_bioregion_trigger:** BEFORE INSERT OR UPDATE ROW
  - Calls: assign_poi_bioregion
- **update_poi_coordinates_trigger:** BEFORE INSERT OR UPDATE ROW
  - Calls: update_poi_coordinates

**Permissions:**
- **ubec_app:** SELECT

---

#### protentions

*Future states anticipated in present consciousness (Husserlian protention)*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('protentions_id_seq'::regclass) |
| entity_type | character varying(50) | ✗ |  |
| entity_id | integer(32) | ✗ |  |
| protended_from | timestamp with time zone | ✗ |  |
| expected_at | timestamp with time zone | ✗ |  |
| temporal_distance | interval | ✗ |  |
| protended_content | jsonb | ✗ |  |
| expectation_confidence | numeric(5,4) | ✗ | 0.5 |
| protention_type | character varying(50) | ✗ |  |
| fulfilled | boolean | ✓ |  |
| fulfilled_at | timestamp with time zone | ✓ |  |
| fulfillment_degree | numeric(5,4) | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- protentions_pkey: (id)

**Indexes:**
- BTREE: (expectation_confidence) - 8192 bytes
- BTREE: (entity_type, entity_id) - 8192 bytes
- BTREE: (fulfilled, fulfillment_degree) - 8192 bytes
- BTREE: (protended_from, expected_at) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### quantum_entanglement

*Quantum entanglement: non-local correlations between entity states*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('quantum_entanglement_id_seq'::regclass) |
| entity1_state_id | bigint(64) | ✗ |  |
| entity2_state_id | bigint(64) | ✗ |  |
| entanglement_entropy | numeric(15,10) | ✗ |  |
| correlation_coefficient | numeric(10,8) | ✗ |  |
| bell_parameter | numeric(10,6) | ✓ |  |
| violates_bell_inequality | boolean | ✓ |  |
| joint_state | jsonb | ✗ |  |
| is_separable | boolean | ✗ | false |
| separability_witness | numeric(10,6) | ✓ |  |
| separation_distance | numeric(20,10) | ✓ |  |
| instantaneous_correlation | boolean | ✓ |  |
| entanglement_created_at | timestamp with time zone | ✗ | now() |
| entanglement_broken_at | timestamp with time zone | ✓ |  |
| entanglement_lifetime | interval | ✓ |  |

**Primary Key:**
- quantum_entanglement_pkey: (id)

**Foreign Keys:**
- quantum_entanglement_entity1_state_id_fkey: (entity1_state_id) → phenomenal.quantum_states(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE
- quantum_entanglement_entity2_state_id_fkey: (entity2_state_id) → phenomenal.quantum_states(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- quantum_entanglement_entity1_state_id_entity2_state_id_key: (entity1_state_id, entity2_state_id)

**Check Constraints:**
- quantum_entanglement_check: CHECK ((entity1_state_id <> entity2_state_id))
- quantum_entanglement_correlation_coefficient_check: CHECK (((correlation_coefficient >= ('-1'::integer)::numeric) AND (correlation_coefficient <= (1)::numeric)))
- quantum_entanglement_entanglement_entropy_check: CHECK ((entanglement_entropy >= (0)::numeric))

**Indexes:**
- BTREE: (entanglement_broken_at) - 8192 bytes
- BTREE: (entity1_state_id, entity2_state_id) - 8192 bytes
- BTREE: (entanglement_entropy) - 8192 bytes
- UNIQUE BTREE: (entity1_state_id, entity2_state_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### quantum_gravity_signatures

*Observable signatures of quantum gravitational effects*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('quantum_gravity_signatures_id_seq'::regclass) |
| signature_type | character varying(100) | ✗ |  |
| measured_value | numeric(20,10) | ✗ |  |
| theoretical_prediction | numeric(20,10) | ✓ |  |
| measurement_error | numeric(20,10) | ✓ |  |
| measurement_region | USER-DEFINED | ✓ |  |
| energy_scale | numeric(20,10) | ✓ |  |
| length_scale | numeric(20,10) | ✓ |  |
| confidence_level | numeric(10,8) | ✓ |  |
| signal_to_noise | numeric(15,10) | ✓ |  |
| signature_details | jsonb | ✗ |  |
| related_entities | jsonb | ✓ |  |
| observed_at | timestamp with time zone | ✗ | now() |
| observation_duration | interval | ✓ |  |

**Primary Key:**
- quantum_gravity_signatures_pkey: (id)

**Check Constraints:**
- quantum_gravity_signatures_confidence_level_check: CHECK (((confidence_level >= (0)::numeric) AND (confidence_level <= (1)::numeric)))
- quantum_gravity_signatures_energy_scale_check: CHECK ((energy_scale > (0)::numeric))
- quantum_gravity_signatures_length_scale_check: CHECK ((length_scale > (0)::numeric))

**Indexes:**
- BTREE: (confidence_level) - 8192 bytes
- GIN: (signature_details) - 16 kB
- GIST: (measurement_region) - 8192 bytes
- BTREE: (signature_type) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### quantum_states

*Quantum mechanical states: superposition, discrete energies, and uncertainty*

**Rows:** 0 | **Size:** 40 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('quantum_states_id_seq'::regclass) |
| entity_type | character varying(50) | ✗ |  |
| entity_id | bigint(64) | ✗ |  |
| state_vector | jsonb | ✗ |  |
| energy_level | integer(32) | ✗ |  |
| energy_value | numeric(20,10) | ✗ |  |
| possible_transitions | jsonb | ✓ |  |
| position_uncertainty | numeric(20,10) | ✓ |  |
| momentum_uncertainty | numeric(20,10) | ✓ |  |
| energy_time_uncertainty | numeric(20,10) | ✓ |  |
| last_measured_at | timestamp with time zone | ✓ |  |
| measurement_outcome | character varying(100) | ✓ |  |
| collapse_probability | numeric(10,8) | ✓ |  |
| decoherence_rate | numeric(15,10) | ✓ |  |
| environment_coupling | numeric(10,6) | ✓ |  |
| state_prepared_at | timestamp with time zone | ✗ | now() |
| state_valid_until | timestamp with time zone | ✓ |  |

**Primary Key:**
- quantum_states_pkey: (id)

**Check Constraints:**
- quantum_states_energy_level_check: CHECK ((energy_level >= 0))
- quantum_states_momentum_uncertainty_check: CHECK ((momentum_uncertainty >= (0)::numeric))
- quantum_states_position_uncertainty_check: CHECK ((position_uncertainty >= (0)::numeric))

**Indexes:**
- BTREE: () - 8192 bytes
- BTREE: (energy_level, energy_value) - 8192 bytes
- BTREE: (entity_type, entity_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### retentions

*Past states retained in present consciousness (Husserlian retention)*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('retentions_id_seq'::regclass) |
| entity_type | character varying(50) | ✗ |  |
| entity_id | integer(32) | ✗ |  |
| original_present | timestamp with time zone | ✗ |  |
| retained_at | timestamp with time zone | ✗ |  |
| temporal_distance | interval | ✗ |  |
| retained_content | jsonb | ✗ |  |
| retention_clarity | numeric(5,4) | ✗ | 1.0 |
| retention_type | character varying(50) | ✗ |  |
| transformations | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- retentions_pkey: (id)

**Indexes:**
- BTREE: (retention_clarity) - 8192 bytes
- BTREE: (temporal_distance) - 8192 bytes
- BTREE: (entity_type, entity_id) - 8192 bytes
- BTREE: (original_present, retained_at) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### spacetime_curvature

*How massive entities warp the topology of the network*

**Rows:** 0 | **Size:** 40 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('spacetime_curvature_id_seq'::regclass) |
| source_mass_id | bigint(64) | ✗ |  |
| ricci_scalar | numeric(20,10) | ✓ |  |
| curvature_tensor | jsonb | ✓ |  |
| geodesic_deviations | jsonb | ✓ |  |
| curvature_geometry | USER-DEFINED | ✓ |  |
| curvature_radius | numeric(20,10) | ✗ |  |
| metric_signature | jsonb | ✓ |  |
| light_deflection | numeric(10,6) | ✓ |  |
| time_dilation_factor | numeric(15,10) | ✓ |  |
| calculated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- spacetime_curvature_pkey: (id)

**Foreign Keys:**
- spacetime_curvature_source_mass_id_fkey: (source_mass_id) → phenomenal.gravitational_mass(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Check Constraints:**
- spacetime_curvature_curvature_radius_check: CHECK ((curvature_radius >= (0)::numeric))

**Indexes:**
- BTREE: (ricci_scalar) - 8192 bytes
- BTREE: (source_mass_id) - 8192 bytes
- GIST: (curvature_geometry) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### spatial_positions

*Spatial positions of entities in network embedding space*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('spatial_positions_id_seq'::regclass) |
| embedding_id | integer(32) | ✗ |  |
| entity_type | character varying(50) | ✗ |  |
| entity_id | integer(32) | ✗ |  |
| position | USER-DEFINED | ✗ |  |
| coordinates | ARRAY | ✓ |  |
| local_density | numeric(20,10) | ✓ |  |
| centrality_scores | jsonb | ✓ |  |
| cluster_membership | ARRAY | ✓ |  |
| immediate_neighbors | ARRAY | ✓ |  |
| proximal_region | USER-DEFINED | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- spatial_positions_pkey: (id)

**Foreign Keys:**
- spatial_positions_embedding_id_fkey: (embedding_id) → phenomenal.network_embeddings(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Indexes:**
- BTREE: (embedding_id) - 8192 bytes
- BTREE: (entity_type, entity_id) - 8192 bytes
- GIST: (position) - 8192 bytes
- GIST: (proximal_region) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Triggers:**
- **trg_update_spatial_positions:** AFTER INSERT OR UPDATE ROW
  - Calls: update_spatial_positions_trigger

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### transactions

*Transaction events as discrete phenomena in blockchain spacetime*

**Rows:** 0 | **Size:** 72 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | bigint(64) | ✗ | nextval('transactions_id_seq'::regclass) |
| transaction_hash | character varying(64) | ✗ |  |
| ledger_sequence | bigint(64) | ✗ |  |
| event_type | character varying(50) | ✗ |  |
| source_account_id | integer(32) | ✓ |  |
| ledger_closed_at | timestamp with time zone | ✗ |  |
| temporal_context | jsonb | ✓ |  |
| operations | jsonb | ✗ |  |
| operations_count | integer(32) | ✗ |  |
| effects | jsonb | ✓ |  |
| successful | boolean | ✗ |  |
| result_code | character varying(100) | ✓ |  |
| affected_positions | USER-DEFINED | ✓ |  |
| network_impact | jsonb | ✓ |  |
| fee_charged | bigint(64) | ✗ |  |
| resource_fee | bigint(64) | ✓ |  |
| memo_type | character varying(20) | ✓ |  |
| memo_value | text | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- transactions_pkey: (id)

**Foreign Keys:**
- transactions_source_account_id_fkey: (source_account_id) → phenomenal.accounts(id)
  - ON UPDATE: NO ACTION, ON DELETE: NO ACTION

**Unique Constraints:**
- transactions_transaction_hash_key: (transaction_hash)

**Indexes:**
- BTREE: (transaction_hash) - 8192 bytes
- BTREE: (ledger_sequence, ledger_closed_at) - 8192 bytes
- BTREE: (source_account_id) - 8192 bytes
- GIST: (affected_positions) - 8192 bytes
- BTREE: (ledger_closed_at) - 8192 bytes
- BTREE: (event_type, successful) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- UNIQUE BTREE: (transaction_hash) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### ubec_bioregions

**Rows:** 0 | **Size:** 24 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| gid | integer(32) | ✗ | nextval('ubec_bioregions_gid_seq'::regclass) |
| name | text | ✓ |  |
| geom | USER-DEFINED | ✗ |  |

**Primary Key:**
- ubec_bioregions_pkey: (gid)

**Indexes:**
- GIST: (geom) - 8192 bytes
- PRIMARY UNIQUE BTREE: (gid) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### ubec_poi

**Rows:** 0 | **Size:** 24 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| gid | integer(32) | ✗ | nextval('ubec_poi_gid_seq'::regclass) |
| name | text | ✓ |  |
| category | text | ✓ |  |
| notes | text | ✓ |  |
| public | boolean | ✓ | true |
| modification_date | timestamp without time zone | ✓ | now() |
| geom | USER-DEFINED | ✗ |  |

**Primary Key:**
- ubec_poi_pkey: (gid)

**Indexes:**
- GIST: (geom) - 8192 bytes
- PRIMARY UNIQUE BTREE: (gid) - 8192 bytes

**Triggers:**
- **ubec_poi_set_modified:** BEFORE UPDATE ROW
  - Calls: set_modified

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

### Views

#### active_pois

```sql

```

#### active_quantum_entanglements

```sql

```

#### approved_bioregions

```sql

```

#### bioregion_stats

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

#### poi_stats

```sql

```

#### pois_by_type

```sql

```

#### recent_submissions

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

#### assign_poi_bioregion()

- **Returns:** trigger
- **Language:** plpgsql
- **Description:** Automatically assigns POI to bioregion if point falls within bioregion boundaries

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

#### check_bioregion_overlap(p_geom geometry, p_gid integer DEFAULT NULL::integer)

- **Returns:** TABLE(overlapping_gid integer, overlapping_name character varying, overlap_area_sqkm numeric, overlap_percent numeric)
- **Language:** plpgsql
- **Description:** Check for overlapping approved bioregions for conflict detection

#### compute_phenomenal_prominence(p_entity_type character varying, p_entity_id integer)

- **Returns:** jsonb
- **Language:** plpgsql
- **Description:** Compute centrality measures

#### find_bioregion_by_point(p_lat numeric, p_lon numeric)

- **Returns:** TABLE(bioregion_gid integer, bioregion_name character varying, bioregion_status character varying, distance_km numeric)
- **Language:** plpgsql
- **Description:** Find nearest bioregions to a given latitude/longitude point

#### find_nearby_pois(p_lat numeric, p_lon numeric, p_radius_km numeric DEFAULT 10)

- **Returns:** TABLE(poi_gid integer, poi_name character varying, poi_type character varying, distance_km numeric, bioregion_name character varying)
- **Language:** plpgsql
- **Description:** Find POIs within specified radius (km) of a lat/lon point

#### get_bioregion_pois(p_bioregion_gid integer)

- **Returns:** TABLE(poi_gid integer, poi_name character varying, poi_type character varying, primary_category character varying)
- **Language:** plpgsql
- **Description:** Get all active POIs within a specific bioregion

#### maintain_retentions_trigger()

- **Returns:** trigger
- **Language:** plpgsql

#### set_modified()

- **Returns:** trigger
- **Language:** plpgsql

#### update_bioregion_geometry()

- **Returns:** trigger
- **Language:** plpgsql
- **Description:** Automatically calculates area and centroid when bioregion geometry is inserted or updated

#### update_poi_coordinates()

- **Returns:** trigger
- **Language:** plpgsql
- **Description:** Automatically extracts latitude and longitude from point geometry

#### update_spatial_positions_trigger()

- **Returns:** trigger
- **Language:** plpgsql

#### update_updated_at_column()

- **Returns:** trigger
- **Language:** plpgsql

#### validate_bioregion_geometry()

- **Returns:** trigger
- **Language:** plpgsql

---

## public

*PostgreSQL default schema - PostGIS extensions and shared utilities*

**Tables:** 1 | **Views:** 2 | **Functions:** 940 | **Total Rows:** 8,500 | **Size:** 7144 kB

### Tables

#### spatial_ref_sys

**Rows:** 8,500 | **Size:** 7144 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| srid | integer(32) | ✗ |  |
| auth_name | character varying(256) | ✓ |  |
| auth_srid | integer(32) | ✓ |  |
| srtext | character varying(2048) | ✓ |  |
| proj4text | character varying(2048) | ✓ |  |

**Primary Key:**
- spatial_ref_sys_pkey: (srid)

**Check Constraints:**
- spatial_ref_sys_srid_check: CHECK (((srid > 0) AND (srid <= 998999)))

**Indexes:**
- PRIMARY UNIQUE BTREE: (srid) - 208 kB

**Permissions:**
- **PUBLIC:** SELECT
- **ubec_app:** SELECT

---

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

#### _st_distanceuncached(geography, geography)

- **Returns:** double precision
- **Language:** sql

#### _st_distanceuncached(geography, geography, double precision, boolean)

- **Returns:** double precision
- **Language:** c

#### _st_distanceuncached(geography, geography, boolean)

- **Returns:** double precision
- **Language:** sql

#### _st_dwithin(geog1 geography, geog2 geography, tolerance double precision, use_spheroid boolean DEFAULT true)

- **Returns:** boolean
- **Language:** c

#### _st_dwithin(geom1 geometry, geom2 geometry, double precision)

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

#### addgeometrycolumn(table_name character varying, column_name character varying, new_srid integer, new_type character varying, new_dim integer, use_typmod boolean DEFAULT true)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: table_name, column_name, srid, type, dimension, use_typmod=true - Adds a geometry column to an existing table.

#### addgeometrycolumn(schema_name character varying, table_name character varying, column_name character varying, new_srid integer, new_type character varying, new_dim integer, use_typmod boolean DEFAULT true)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: schema_name, table_name, column_name, srid, type, dimension, use_typmod=true - Adds a geometry column to an existing table.

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

#### box3d(box2d)

- **Returns:** box3d
- **Language:** c

#### box3d(geometry)

- **Returns:** box3d
- **Language:** c
- **Description:** args: geom - Returns a BOX3D representing the 3D extent of a geometry.

#### box3d_in(cstring)

- **Returns:** box3d
- **Language:** c

#### box3d_out(box3d)

- **Returns:** cstring
- **Language:** c

#### box3dtobox(box3d)

- **Returns:** box
- **Language:** c

#### bytea(geometry)

- **Returns:** bytea
- **Language:** c

#### bytea(geography)

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

#### contains_2d(geometry, box2df)

- **Returns:** boolean
- **Language:** sql

#### contains_2d(box2df, geometry)

- **Returns:** boolean
- **Language:** c

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

#### dropgeometrytable(catalog_name character varying, schema_name character varying, table_name character varying)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: catalog_name, schema_name, table_name - Drops a table and all its references in geometry_columns.

#### dropgeometrytable(schema_name character varying, table_name character varying)

- **Returns:** text
- **Language:** sql
- **Description:** args: schema_name, table_name - Drops a table and all its references in geometry_columns.

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

#### geography(geometry)

- **Returns:** geography
- **Language:** c

#### geography(bytea)

- **Returns:** geography
- **Language:** c

#### geography(geography, integer, boolean)

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

#### geometry(text)

- **Returns:** geometry
- **Language:** c

#### geometry(path)

- **Returns:** geometry
- **Language:** c

#### geometry(geometry, integer, boolean)

- **Returns:** geometry
- **Language:** c

#### geometry(box2d)

- **Returns:** geometry
- **Language:** c

#### geometry(bytea)

- **Returns:** geometry
- **Language:** c

#### geometry(geography)

- **Returns:** geometry
- **Language:** c

#### geometry(point)

- **Returns:** geometry
- **Language:** c

#### geometry(polygon)

- **Returns:** geometry
- **Language:** c

#### geometry(box3d)

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

#### geometrytype(geometry)

- **Returns:** text
- **Language:** c
- **Description:** args: geomA - Returns the type of a geometry as text.

#### geometrytype(geography)

- **Returns:** text
- **Language:** c

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

#### is_contained_2d(box2df, geometry)

- **Returns:** boolean
- **Language:** c

#### is_contained_2d(box2df, box2df)

- **Returns:** boolean
- **Language:** c

#### json(geometry)

- **Returns:** json
- **Language:** c

#### jsonb(geometry)

- **Returns:** jsonb
- **Language:** c

#### lockrow(text, text, text, timestamp without time zone)

- **Returns:** integer
- **Language:** sql
- **Description:** args: a_table_name, a_row_key, an_auth_token, expire_dt - Sets lock/authorization for a row in a table.

#### lockrow(text, text, text, text)

- **Returns:** integer
- **Language:** sql

#### lockrow(text, text, text, text, timestamp without time zone)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: a_schema_name, a_table_name, a_row_key, an_auth_token, expire_dt - Sets lock/authorization for a row in a table.

#### lockrow(text, text, text)

- **Returns:** integer
- **Language:** sql
- **Description:** args: a_table_name, a_row_key, an_auth_token - Sets lock/authorization for a row in a table.

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

#### overlaps_geog(geography, gidx)

- **Returns:** boolean
- **Language:** sql

#### overlaps_geog(gidx, geography)

- **Returns:** boolean
- **Language:** c

#### overlaps_geog(gidx, gidx)

- **Returns:** boolean
- **Language:** c

#### overlaps_nd(gidx, gidx)

- **Returns:** boolean
- **Language:** c

#### overlaps_nd(gidx, geometry)

- **Returns:** boolean
- **Language:** c

#### overlaps_nd(geometry, gidx)

- **Returns:** boolean
- **Language:** sql

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

#### pgis_asgeobuf_transfn(internal, anyelement)

- **Returns:** internal
- **Language:** c

#### pgis_asgeobuf_transfn(internal, anyelement, text)

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

#### pgis_asmvt_transfn(internal, anyelement, text, integer)

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

#### pgis_asmvt_transfn(internal, anyelement, text)

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

#### pgis_geometry_union_parallel_transfn(internal, geometry)

- **Returns:** internal
- **Language:** c

#### pgis_geometry_union_parallel_transfn(internal, geometry, double precision)

- **Returns:** internal
- **Language:** c

#### point(geometry)

- **Returns:** point
- **Language:** c

#### polygon(geometry)

- **Returns:** polygon
- **Language:** c

#### populate_geometry_columns(use_typmod boolean DEFAULT true)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: use_typmod=true - Ensures geometry columns are defined with type modifiers or have appropriate spatial constraints.

#### populate_geometry_columns(tbl_oid oid, use_typmod boolean DEFAULT true)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: relation_oid, use_typmod=true - Ensures geometry columns are defined with type modifiers or have appropriate spatial constraints.

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

#### st_addpoint(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring, point - Add a point to a LineString.

#### st_addpoint(geom1 geometry, geom2 geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring, point, position = -1 - Add a point to a LineString.

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

#### st_area(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1 - Returns the area of a polygonal geometry.

#### st_area(text)

- **Returns:** double precision
- **Language:** sql

#### st_area(geog geography, use_spheroid boolean DEFAULT true)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geog, use_spheroid=true - Returns the area of a polygonal geometry.

#### st_area2d(geometry)

- **Returns:** double precision
- **Language:** c

#### st_asbinary(geography)

- **Returns:** bytea
- **Language:** c

#### st_asbinary(geometry)

- **Returns:** bytea
- **Language:** c

#### st_asbinary(geography, text)

- **Returns:** bytea
- **Language:** c

#### st_asbinary(geometry, text)

- **Returns:** bytea
- **Language:** c

#### st_asencodedpolyline(geom geometry, nprecision integer DEFAULT 5)

- **Returns:** text
- **Language:** c

#### st_asewkb(geometry, text)

- **Returns:** bytea
- **Language:** c

#### st_asewkb(geometry)

- **Returns:** bytea
- **Language:** c

#### st_asewkt(text)

- **Returns:** text
- **Language:** sql

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

#### st_asgeojson(geom geometry, maxdecimaldigits integer DEFAULT 9, options integer DEFAULT 8)

- **Returns:** text
- **Language:** c

#### st_asgeojson(r record, geom_column text DEFAULT ''::text, maxdecimaldigits integer DEFAULT 9, pretty_bool boolean DEFAULT false)

- **Returns:** text
- **Language:** c

#### st_asgeojson(geog geography, maxdecimaldigits integer DEFAULT 9, options integer DEFAULT 0)

- **Returns:** text
- **Language:** c

#### st_asgeojson(text)

- **Returns:** text
- **Language:** sql

#### st_asgml(version integer, geog geography, maxdecimaldigits integer DEFAULT 15, options integer DEFAULT 0, nprefix text DEFAULT 'gml'::text, id text DEFAULT ''::text)

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

#### st_asgml(geog geography, maxdecimaldigits integer DEFAULT 15, options integer DEFAULT 0, nprefix text DEFAULT 'gml'::text, id text DEFAULT ''::text)

- **Returns:** text
- **Language:** c

#### st_ashexewkb(geometry, text)

- **Returns:** text
- **Language:** c

#### st_ashexewkb(geometry)

- **Returns:** text
- **Language:** c

#### st_askml(text)

- **Returns:** text
- **Language:** sql

#### st_askml(geog geography, maxdecimaldigits integer DEFAULT 15, nprefix text DEFAULT ''::text)

- **Returns:** text
- **Language:** c

#### st_askml(geom geometry, maxdecimaldigits integer DEFAULT 15, nprefix text DEFAULT ''::text)

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

#### st_astext(geography, integer)

- **Returns:** text
- **Language:** c

#### st_astext(text)

- **Returns:** text
- **Language:** sql

#### st_astext(geometry, integer)

- **Returns:** text
- **Language:** c

#### st_astext(geography)

- **Returns:** text
- **Language:** c

#### st_astwkb(geom geometry, prec integer DEFAULT NULL::integer, prec_z integer DEFAULT NULL::integer, prec_m integer DEFAULT NULL::integer, with_sizes boolean DEFAULT NULL::boolean, with_boxes boolean DEFAULT NULL::boolean)

- **Returns:** bytea
- **Language:** c

#### st_astwkb(geom geometry[], ids bigint[], prec integer DEFAULT NULL::integer, prec_z integer DEFAULT NULL::integer, prec_m integer DEFAULT NULL::integer, with_sizes boolean DEFAULT NULL::boolean, with_boxes boolean DEFAULT NULL::boolean)

- **Returns:** bytea
- **Language:** c

#### st_asx3d(geom geometry, maxdecimaldigits integer DEFAULT 15, options integer DEFAULT 0)

- **Returns:** text
- **Language:** sql

#### st_azimuth(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: origin, target - Returns the north-based azimuth of a line between two points.

#### st_azimuth(geog1 geography, geog2 geography)

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

#### st_buffer(geography, double precision, text)

- **Returns:** geography
- **Language:** sql
- **Description:** args: g1, radius_of_buffer, buffer_style_parameters - Computes a geometry covering all points within a given distance from a geometry.

#### st_buffer(text, double precision, integer)

- **Returns:** geometry
- **Language:** sql

#### st_buffer(geography, double precision, integer)

- **Returns:** geography
- **Language:** sql
- **Description:** args: g1, radius_of_buffer, num_seg_quarter_circle - Computes a geometry covering all points within a given distance from a geometry.

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

#### st_centroid(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1 - Returns the geometric center of a geometry.

#### st_centroid(text)

- **Returns:** geometry
- **Language:** sql

#### st_centroid(geography, use_spheroid boolean DEFAULT true)

- **Returns:** geography
- **Language:** c
- **Description:** args: g1, use_spheroid=true - Returns the geometric center of a geometry.

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

#### st_collect(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2 - Creates a GeometryCollection or Multi* geometry from a set of geometries.

#### st_collect(geometry[])

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1_array - Creates a GeometryCollection or Multi* geometry from a set of geometries.

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

#### st_combinebbox(box2d, geometry)

- **Returns:** box2d
- **Language:** c

#### st_combinebbox(box3d, box3d)

- **Returns:** box3d
- **Language:** c

#### st_combinebbox(box3d, geometry)

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

#### st_coveredby(text, text)

- **Returns:** boolean
- **Language:** sql

#### st_coveredby(geog1 geography, geog2 geography)

- **Returns:** boolean
- **Language:** c

#### st_coveredby(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

#### st_covers(geog1 geography, geog2 geography)

- **Returns:** boolean
- **Language:** c

#### st_covers(text, text)

- **Returns:** boolean
- **Language:** sql

#### st_covers(geom1 geometry, geom2 geometry)

- **Returns:** boolean
- **Language:** c

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

#### st_distance(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: g1, g2 - Returns the distance between two geometry or geography values.

#### st_distance(geog1 geography, geog2 geography, use_spheroid boolean DEFAULT true)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geog1, geog2, use_spheroid=true - Returns the distance between two geometry or geography values.

#### st_distance(text, text)

- **Returns:** double precision
- **Language:** sql

#### st_distancecpa(geometry, geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: track1, track2 - Returns the distance between the closest point of approach of two trajectories.

#### st_distancesphere(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** sql

#### st_distancesphere(geom1 geometry, geom2 geometry, radius double precision)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geomlonlatA, geomlonlatB, radius=6371008 - Returns minimum distance in meters between two lon/lat geometries using a spherical earth model.

#### st_distancespheroid(geom1 geometry, geom2 geometry, spheroid)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geomlonlatA, geomlonlatB, measurement_spheroid=WGS84 - Returns the minimum distance between two lon/lat geometries using a spheroidal earth model.

#### st_distancespheroid(geom1 geometry, geom2 geometry)

- **Returns:** double precision
- **Language:** c

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

#### st_dwithin(text, text, double precision)

- **Returns:** boolean
- **Language:** sql

#### st_dwithin(geog1 geography, geog2 geography, tolerance double precision, use_spheroid boolean DEFAULT true)

- **Returns:** boolean
- **Language:** c

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

#### st_estimatedextent(text, text, text, boolean)

- **Returns:** box2d
- **Language:** c
- **Description:** args: schema_name, table_name, geocolumn_name, parent_only - Returns the estimated extent of a spatial table.

#### st_estimatedextent(text, text, text)

- **Returns:** box2d
- **Language:** c
- **Description:** args: schema_name, table_name, geocolumn_name - Returns the estimated extent of a spatial table.

#### st_estimatedextent(text, text)

- **Returns:** box2d
- **Language:** c
- **Description:** args: table_name, geocolumn_name - Returns the estimated extent of a spatial table.

#### st_expand(geometry, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, units_to_expand - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(box box2d, dx double precision, dy double precision)

- **Returns:** box2d
- **Language:** c
- **Description:** args: box, dx, dy - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(box box3d, dx double precision, dy double precision, dz double precision DEFAULT 0)

- **Returns:** box3d
- **Language:** c
- **Description:** args: box, dx, dy, dz=0 - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(box3d, double precision)

- **Returns:** box3d
- **Language:** c
- **Description:** args: box, units_to_expand - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(box2d, double precision)

- **Returns:** box2d
- **Language:** c
- **Description:** args: box, units_to_expand - Returns a bounding box expanded from another bounding box or a geometry.

#### st_expand(geom geometry, dx double precision, dy double precision, dz double precision DEFAULT 0, dm double precision DEFAULT 0)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, dx, dy, dz=0, dm=0 - Returns a bounding box expanded from another bounding box or a geometry.

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

#### st_geomfromgeojson(jsonb)

- **Returns:** geometry
- **Language:** sql

#### st_geomfromgeojson(text)

- **Returns:** geometry
- **Language:** c

#### st_geomfromgml(text)

- **Returns:** geometry
- **Language:** sql

#### st_geomfromgml(text, integer)

- **Returns:** geometry
- **Language:** c

#### st_geomfromkml(text)

- **Returns:** geometry
- **Language:** c

#### st_geomfrommarc21(marc21xml text)

- **Returns:** geometry
- **Language:** c

#### st_geomfromtext(text)

- **Returns:** geometry
- **Language:** c

#### st_geomfromtext(text, integer)

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

#### st_intersection(geom1 geometry, geom2 geometry, gridsize double precision DEFAULT '-1'::integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, geomB, gridSize = -1 - Computes a geometry representing the shared portion of geometries A and B.

#### st_intersection(text, text)

- **Returns:** geometry
- **Language:** sql

#### st_intersection(geography, geography)

- **Returns:** geography
- **Language:** sql
- **Description:** args: geogA, geogB - Computes a geometry representing the shared portion of geometries A and B.

#### st_intersects(text, text)

- **Returns:** boolean
- **Language:** sql

#### st_intersects(geog1 geography, geog2 geography)

- **Returns:** boolean
- **Language:** c

#### st_intersects(geom1 geometry, geom2 geometry)

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

#### st_isvalid(geometry, integer)

- **Returns:** boolean
- **Language:** sql
- **Description:** args: g, flags - Tests if a geometry is well-formed in 2D.

#### st_isvalid(geometry)

- **Returns:** boolean
- **Language:** c
- **Description:** args: g - Tests if a geometry is well-formed in 2D.

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

#### st_length(geometry)

- **Returns:** double precision
- **Language:** c
- **Description:** args: a_2dlinestring - Returns the 2D length of a linear geometry.

#### st_length(geog geography, use_spheroid boolean DEFAULT true)

- **Returns:** double precision
- **Language:** c
- **Description:** args: geog, use_spheroid=true - Returns the 2D length of a linear geometry.

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

#### st_makepoint(double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, z - Creates a 2D, 3DZ or 4D Point.

#### st_makepoint(double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, z, m - Creates a 2D, 3DZ or 4D Point.

#### st_makepoint(double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y - Creates a 2D, 3DZ or 4D Point.

#### st_makepointm(double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, m - Creates a Point from X, Y and M values.

#### st_makepolygon(geometry, geometry[])

- **Returns:** geometry
- **Language:** c
- **Description:** args: outerlinestring, interiorlinestrings - Creates a Polygon from a shell and optional list of holes.

#### st_makepolygon(geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: linestring - Creates a Polygon from a shell and optional list of holes.

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

#### st_mlinefromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_mlinefromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_mlinefromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_mlinefromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_mpointfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_mpointfromtext(text, integer)

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

#### st_multipointfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_multipointfromwkb(bytea)

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

#### st_point(double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y - Creates a Point with X, Y and SRID values.

#### st_point(double precision, double precision, srid integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: x, y, srid=unknown - Creates a Point with X, Y and SRID values.

#### st_pointfromgeohash(text, integer DEFAULT NULL::integer)

- **Returns:** geometry
- **Language:** c

#### st_pointfromtext(text, integer)

- **Returns:** geometry
- **Language:** sql

#### st_pointfromtext(text)

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

#### st_polyfromwkb(bytea)

- **Returns:** geometry
- **Language:** sql

#### st_polyfromwkb(bytea, integer)

- **Returns:** geometry
- **Language:** sql

#### st_polygon(geometry, integer)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: lineString, srid - Creates a Polygon from a LineString with a specified SRID.

#### st_polygonfromtext(text)

- **Returns:** geometry
- **Language:** sql

#### st_polygonfromtext(text, integer)

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

#### st_relate(geom1 geometry, geom2 geometry)

- **Returns:** text
- **Language:** c

#### st_relate(geom1 geometry, geom2 geometry, text)

- **Returns:** boolean
- **Language:** c

#### st_relate(geom1 geometry, geom2 geometry, integer)

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

#### st_rotate(geometry, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, rotRadians - Rotates a geometry about an origin point.

#### st_rotate(geometry, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, rotRadians, x0, y0 - Rotates a geometry about an origin point.

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

#### st_scale(geometry, geometry, origin geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, factor, origin - Scales a geometry by given factors.

#### st_scale(geometry, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, XFactor, YFactor, ZFactor - Scales a geometry by given factors.

#### st_scale(geometry, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, XFactor, YFactor - Scales a geometry by given factors.

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

#### st_setsrid(geog geography, srid integer)

- **Returns:** geography
- **Language:** c

#### st_setsrid(geom geometry, srid integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geom, srid - Set the SRID on a geometry.

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

#### st_snaptogrid(geometry, double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, originX, originY, sizeX, sizeY - Snap all points of the input geometry to a regular grid.

#### st_snaptogrid(geometry, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, size - Snap all points of the input geometry to a regular grid.

#### st_snaptogrid(geometry, double precision, double precision)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geomA, sizeX, sizeY - Snap all points of the input geometry to a regular grid.

#### st_snaptogrid(geom1 geometry, geom2 geometry, double precision, double precision, double precision, double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: geomA, pointOrigin, sizeX, sizeY, sizeZ, sizeM - Snap all points of the input geometry to a regular grid.

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

#### st_summary(geometry)

- **Returns:** text
- **Language:** c
- **Description:** args: g - Returns a text summary of the contents of a geometry.

#### st_summary(geography)

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

#### st_transform(geom geometry, to_proj text)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geom, to_proj - Return a new geometry with coordinates transformed to a different spatial reference system.

#### st_transform(geometry, integer)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, srid - Return a new geometry with coordinates transformed to a different spatial reference system.

#### st_transform(geom geometry, from_proj text, to_proj text)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geom, from_proj, to_proj - Return a new geometry with coordinates transformed to a different spatial reference system.

#### st_transform(geom geometry, from_proj text, to_srid integer)

- **Returns:** geometry
- **Language:** sql
- **Description:** args: geom, from_proj, to_srid - Return a new geometry with coordinates transformed to a different spatial reference system.

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

#### st_union(geom1 geometry, geom2 geometry)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2 - Computes a geometry representing the point-set union of the input geometries.

#### st_union(geom1 geometry, geom2 geometry, gridsize double precision)

- **Returns:** geometry
- **Language:** c
- **Description:** args: g1, g2, gridSize - Computes a geometry representing the point-set union of the input geometries.

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

#### updategeometrysrid(character varying, character varying, integer)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: table_name, column_name, srid - Updates the SRID of all features in a geometry column, and the table metadata.

#### updategeometrysrid(catalogn_name character varying, schema_name character varying, table_name character varying, column_name character varying, new_srid_in integer)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: catalog_name, schema_name, table_name, column_name, srid - Updates the SRID of all features in a geometry column, and the table metadata.

#### updategeometrysrid(character varying, character varying, character varying, integer)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: schema_name, table_name, column_name, srid - Updates the SRID of all features in a geometry column, and the table metadata.

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

## topology

*PostGIS Topology Schema - Spatial network topology and geometric relationships*

**Tables:** 2 | **Views:** 0 | **Functions:** 103 | **Total Rows:** 0 | **Size:** 48 kB

### Sequences

#### topology_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** topology.id

### Tables

#### layer

**Rows:** 0 | **Size:** 24 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| topology_id | integer(32) | ✗ |  |
| layer_id | integer(32) | ✗ |  |
| schema_name | character varying | ✗ |  |
| table_name | character varying | ✗ |  |
| feature_column | character varying | ✗ |  |
| feature_type | integer(32) | ✗ |  |
| level | integer(32) | ✗ | 0 |
| child_id | integer(32) | ✓ |  |

**Primary Key:**
- layer_pkey: (topology_id, layer_id)

**Foreign Keys:**
- layer_topology_id_fkey: (topology_id) → topology.topology(id)
  - ON UPDATE: NO ACTION, ON DELETE: NO ACTION

**Unique Constraints:**
- layer_schema_name_table_name_feature_column_key: (schema_name, table_name, feature_column)

**Indexes:**
- PRIMARY UNIQUE BTREE: (topology_id, layer_id) - 8192 bytes
- UNIQUE BTREE: (schema_name, table_name, feature_column) - 8192 bytes

**Triggers:**
- **layer_integrity_checks:** BEFORE DELETE OR UPDATE ROW
  - Calls: layertrigger

**Permissions:**
- **PUBLIC:** SELECT
- **ubec_app:** SELECT

---

#### topology

**Rows:** 0 | **Size:** 24 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('topology_id_seq'::regclass) |
| name | character varying | ✗ |  |
| srid | integer(32) | ✗ |  |
| precision | double precision(53) | ✗ |  |
| hasz | boolean | ✗ | false |

**Primary Key:**
- topology_pkey: (id)

**Unique Constraints:**
- topology_name_key: (name)

**Indexes:**
- UNIQUE BTREE: (name) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **PUBLIC:** SELECT
- **ubec_app:** SELECT

---

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

#### addtopogeometrycolumn(toponame character varying, schema character varying, tbl character varying, col character varying, ltype character varying, child integer)

- **Returns:** integer
- **Language:** plpgsql
- **Description:** args: topology_name, schema_name, table_name, column_name, feature_type, child_layer - Adds a topogeometry column to an existing table, registers this new column as a layer in topology.layer and returns the new layer_id.

#### addtopogeometrycolumn(character varying, character varying, character varying, character varying, character varying)

- **Returns:** integer
- **Language:** sql
- **Description:** args: topology_name, schema_name, table_name, column_name, feature_type - Adds a topogeometry column to an existing table, registers this new column as a layer in topology.layer and returns the new layer_id.

#### addtosearchpath(a_schema_name character varying)

- **Returns:** text
- **Language:** plpgsql

#### asgml(tg topogeometry, nsprefix text)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, nsprefix_in - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, nsprefix text, prec integer, options integer, visitedtable regclass, idprefix text)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, nsprefix_in, precision, options, visitedTable, idprefix - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, nsprefix_in text, precision_in integer, options_in integer, visitedtable regclass, idprefix text, gmlver integer)

- **Returns:** text
- **Language:** plpgsql
- **Description:** args: tg, nsprefix_in, precision, options, visitedTable, idprefix, gmlversion - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, visitedtable regclass, nsprefix text)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, visitedTable, nsprefix - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, visitedtable regclass)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, visitedTable - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, nsprefix text, prec integer, options integer, vis regclass)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, nsprefix_in, precision, options, visitedTable - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg - Returns the GML representation of a topogeometry.

#### asgml(tg topogeometry, nsprefix text, prec integer, opts integer)

- **Returns:** text
- **Language:** sql
- **Description:** args: tg, nsprefix_in, precision, options - Returns the GML representation of a topogeometry.

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

#### findlayer(layer_table regclass, feature_column name)

- **Returns:** layer
- **Language:** sql
- **Description:** args: layer_table, feature_column - Returns a topology.layer record by different means.

#### findlayer(tg topogeometry)

- **Returns:** layer
- **Language:** sql
- **Description:** args: tg - Returns a topology.layer record by different means.

#### findlayer(schema_name name, table_name name, feature_column name)

- **Returns:** layer
- **Language:** sql
- **Description:** args: schema_name, table_name, feature_column - Returns a topology.layer record by different means.

#### findlayer(topology_id integer, layer_id integer)

- **Returns:** layer
- **Language:** sql
- **Description:** args: topology_id, layer_id - Returns a topology.layer record by different means.

#### findtopology(integer)

- **Returns:** topology
- **Language:** sql
- **Description:** args: id - Returns a topology record by different means.

#### findtopology(topogeometry)

- **Returns:** topology
- **Language:** sql
- **Description:** args: topogeom - Returns a topology record by different means.

#### findtopology(regclass, name)

- **Returns:** topology
- **Language:** sql
- **Description:** args: layerTable, layerColumn - Returns a topology record by different means.

#### findtopology(name, name, name)

- **Returns:** topology
- **Language:** sql
- **Description:** args: layerSchema, layerTable, layerColumn - Returns a topology record by different means.

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

#### gettopogeomelements(tg topogeometry)

- **Returns:** SETOF topoelement
- **Language:** plpgsql
- **Description:** args: tg - Returns a set of topoelement objects containing the topological element_id,element_type of the given TopoGeometry (primitive elements).

#### gettopogeomelements(toponame character varying, layerid integer, tgid integer)

- **Returns:** SETOF topoelement
- **Language:** plpgsql
- **Description:** args: toponame, layer_id, tg_id - Returns a set of topoelement objects containing the topological element_id,element_type of the given TopoGeometry (primitive elements).

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

## ubec_main

*Four-Element Protocol - Primary operational schema for UBEC token management*

**Tables:** 49 | **Views:** 20 | **Functions:** 80 | **Total Rows:** 145,774 | **Size:** 105 MB

### Schema Permissions

- **recipro:** USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE
- **reward_admin:** USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE
- **reward_data_writer:** USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE
- **ubec_admin:** USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE
- **ubec_app:** USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE
- **ubec_sync:** USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE, USAGE

### Sequences

#### account_balances_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** account_balances.id

#### account_order_positions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** account_order_positions.id

#### agent_activity_history_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** agent_activity_history.id

#### agent_benefit_history_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** agent_benefit_history.id

#### agent_contribution_history_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** agent_contribution_history.id

#### agent_holon_memberships_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** agent_holon_memberships.id

#### agents_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** agents.id

#### api_rate_limits_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** api_rate_limits.id

#### asset_holder_analysis_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** asset_holder_analysis.id

#### asset_holders_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** asset_holders.id

#### bioregion_analysis_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** bioregion_analysis.id

#### constraint_violations_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** constraint_violations.id

#### distribution_history_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** distribution_history.id

#### distribution_state_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** distribution_state.id

#### distribution_transfers_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** distribution_transfers.id

#### holder_discovery_history_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** holder_discovery_history.id

#### holonic_metrics_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** holonic_metrics.id

#### holons_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** holons.id

#### liquidity_pool_owners_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** liquidity_pool_owners.id

#### mutualism_relationships_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** mutualism_relationships.id

#### orderbook_analytics_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** orderbook_analytics.id

#### orderbook_snapshots_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** orderbook_snapshots.id

#### participants_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** participants.id

#### reciprocity_transactions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** reciprocity_transactions.id

#### regenerative_projects_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** regenerative_projects.id

#### scheduler_jobs_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** scheduler_jobs.id

#### schema_migrations_migration_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** schema_migrations.migration_id

#### stellar_accounts_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** stellar_accounts.id

#### stellar_effects_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** stellar_effects.id

#### stellar_offers_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** stellar_offers.id

#### stellar_operations_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** stellar_operations.id

#### stellar_transactions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** stellar_transactions.id

#### sync_jobs_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** sync_jobs.id

#### system_configuration_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** system_configuration.id

#### system_settings_setting_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** system_settings.setting_id

#### transfer_recommendations_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** transfer_recommendations.id

#### transformation_phases_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** transformation_phases.id

#### transformative_actions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** transformative_actions.id

#### ubec_audit_log_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ubec_audit_log.id

#### ubec_balances_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ubec_balances.id

#### ubec_distributions_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ubec_distributions.id

#### ubec_holonic_metrics_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ubec_holonic_metrics.id

#### ubec_reports_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ubec_reports.id

#### ubec_sync_status_id_seq

- **Start:** 1
- **Increment:** 1
- **Min:** 1, **Max:** 2147483647
- **Cache:** 1
- **Owned By:** ubec_sync_status.id

### Tables

#### account_balances

*Tracks token balances for all accounts across all UBEC tokens. Used for stability analysis in Earth element (UBECgpi).*

**Rows:** 651 | **Size:** 1584 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('account_balances_id_seq'::regclass) |
| account_id *(Stellar public key (G... format))* | character varying(56) | ✗ |  |
| asset_code *(Token code: UBEC, UBECrc, UBECgpi, or UBECtt)* | character varying(12) | ✗ |  |
| balance *(Current token balance for this account)* | numeric(20,7) | ✓ | 0.0 |
| last_updated *(Timestamp of last balance update)* | timestamp with time zone | ✓ | now() |
| created_at | timestamp with time zone | ✓ | now() |

**Primary Key:**
- account_balances_pkey: (id)

**Unique Constraints:**
- account_balances_unique_account_asset: (account_id, asset_code)

**Check Constraints:**
- account_balances_balance_check: CHECK ((balance >= (0)::numeric))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 40 kB
- UNIQUE BTREE: (account_id, asset_code) - 160 kB
- BTREE: (account_id) - 160 kB
- BTREE: (asset_code, balance) - 296 kB
- BTREE: (asset_code) - 16 kB
- BTREE: (asset_code, last_updated) - 40 kB
- BTREE: (balance) - 264 kB
- BTREE: (last_updated) - 280 kB

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### account_order_positions

*Aggregated order positions per account and asset*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('account_order_positions_id_seq'::regclass) |
| account_id | character varying(56) | ✗ |  |
| asset_code | USER-DEFINED | ✗ |  |
| total_buy_orders | integer(32) | ✓ | 0 |
| total_buy_volume *(Sum of all active buy order amounts)* | numeric(20,7) | ✓ | 0 |
| avg_buy_price | numeric(20,7) | ✓ |  |
| total_sell_orders | integer(32) | ✓ | 0 |
| total_sell_volume *(Sum of all active sell order amounts)* | numeric(20,7) | ✓ | 0 |
| avg_sell_price | numeric(20,7) | ✓ |  |
| last_updated | timestamp with time zone | ✗ | now() |

**Primary Key:**
- account_order_positions_pkey: (id)

**Foreign Keys:**
- fk_account: (account_id) → ubec_main.stellar_accounts(account_id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- unique_account_asset: (account_id, asset_code)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (account_id) - 8192 bytes
- BTREE: (asset_code) - 8192 bytes
- BTREE: (asset_code, total_buy_volume) - 8192 bytes
- BTREE: (asset_code, total_sell_volume) - 8192 bytes
- BTREE: (last_updated) - 8192 bytes
- UNIQUE BTREE: (account_id, asset_code) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### agent_activity_history

*Tracks activity history for agents*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('agent_activity_history_id_seq'::regclass) |
| agent_id | integer(32) | ✗ |  |
| activity_type | character varying(100) | ✗ |  |
| score_impact | numeric(10,4) | ✓ | 0 |
| timestamp | bigint(64) | ✗ |  |
| details | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- agent_activity_history_pkey: (id)

**Foreign Keys:**
- agent_activity_history_agent_id_fkey: (agent_id) → ubec_main.agents(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Check Constraints:**
- activity_history_timestamp_check: CHECK (("timestamp" > 0))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (timestamp) - 8192 bytes
- BTREE: (activity_type) - 8192 bytes
- BTREE: (timestamp) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### agent_benefit_history

*Tracks benefit history for agents*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('agent_benefit_history_id_seq'::regclass) |
| agent_id | integer(32) | ✗ |  |
| benefit_type | character varying(100) | ✗ |  |
| amount | numeric(20,7) | ✓ | 0 |
| timestamp | bigint(64) | ✗ |  |
| details | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- agent_benefit_history_pkey: (id)

**Foreign Keys:**
- agent_benefit_history_agent_id_fkey: (agent_id) → ubec_main.agents(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Check Constraints:**
- benefit_history_timestamp_check: CHECK (("timestamp" > 0))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (timestamp) - 8192 bytes
- BTREE: (benefit_type) - 8192 bytes
- BTREE: (timestamp) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### agent_contribution_history

*Tracks contribution history for agents*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('agent_contribution_history_id_seq'::regclass) |
| agent_id | integer(32) | ✗ |  |
| contribution_type | character varying(100) | ✗ |  |
| amount | numeric(20,7) | ✓ | 0 |
| timestamp | bigint(64) | ✗ |  |
| details | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- agent_contribution_history_pkey: (id)

**Foreign Keys:**
- agent_contribution_history_agent_id_fkey: (agent_id) → ubec_main.agents(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Check Constraints:**
- contribution_history_timestamp_check: CHECK (("timestamp" > 0))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (timestamp) - 8192 bytes
- BTREE: (contribution_type) - 8192 bytes
- BTREE: (timestamp) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### agent_holon_memberships

*Tracks agent memberships in holons*

**Rows:** 0 | **Size:** 72 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('agent_holon_memberships_id_seq'::regclass) |
| agent_id | integer(32) | ✗ |  |
| holon_id | integer(32) | ✗ |  |
| role_in_holon | character varying(100) | ✓ |  |
| contribution_score | numeric(10,4) | ✓ | 0 |
| status | character varying(50) | ✗ | 'active'::character varying |
| joined_at | timestamp with time zone | ✗ | now() |
| left_at | timestamp with time zone | ✓ |  |
| metadata | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- agent_holon_memberships_pkey: (id)

**Foreign Keys:**
- agent_holon_memberships_agent_id_fkey: (agent_id) → ubec_main.agents(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE
- agent_holon_memberships_holon_id_fkey: (holon_id) → ubec_main.holons(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- agent_holon_unique: (agent_id, holon_id)

**Check Constraints:**
- valid_membership_status: CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'suspended'::character varying])::text[])))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- UNIQUE BTREE: (agent_id, holon_id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (holon_id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (holon_id) - 8192 bytes
- BTREE: (status) - 8192 bytes
- BTREE: (status) - 8192 bytes

**Triggers:**
- **update_agent_holon_memberships_updated_at:** BEFORE UPDATE ROW
  - Calls: update_updated_at_column

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### agents

**Rows:** 0 | **Size:** 40 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('agents_id_seq'::regclass) |
| agent_id | character varying(56) | ✗ |  |
| participant_id | integer(32) | ✓ |  |
| reputation_score | numeric(10,4) | ✓ | 0 |
| reciprocity_score | numeric(10,4) | ✓ | 0 |
| loyalty_tier | character varying(20) | ✓ | 'none'::character varying |
| last_activity_at | timestamp without time zone | ✓ |  |
| created_at | timestamp without time zone | ✗ | now() |
| updated_at | timestamp without time zone | ✗ | now() |
| status | character varying(20) | ✓ | 'active'::character varying |
| metrics | jsonb | ✓ |  |

**Primary Key:**
- agents_pkey: (id)

**Unique Constraints:**
- agents_agent_id_key: (agent_id)

**Indexes:**
- UNIQUE BTREE: (agent_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (agent_id) - 8192 bytes
- BTREE: (status) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### api_rate_limits

**Rows:** 4 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('api_rate_limits_id_seq'::regclass) |
| api_name | character varying(50) | ✗ |  |
| rate_limit_remaining | integer(32) | ✓ |  |
| rate_limit_limit | integer(32) | ✓ |  |
| rate_limit_reset | integer(32) | ✓ |  |
| last_updated | timestamp without time zone | ✗ | now() |

**Primary Key:**
- api_rate_limits_pkey: (id)

**Unique Constraints:**
- unique_api_name: (api_name)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 16 kB
- BTREE: (api_name) - 16 kB
- UNIQUE BTREE: (api_name) - 16 kB

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### asset_holder_analysis

*Periodic analysis of token holder distribution and supply metrics*

**Rows:** 63 | **Size:** 184 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('asset_holder_analysis_id_seq'::regclass) |
| analysis_date | timestamp without time zone | ✗ | now() |
| asset_code | character varying(12) | ✗ |  |
| asset_issuer | character varying(56) | ✗ |  |
| total_supply | numeric(18,8) | ✗ |  |
| total_holders | integer(32) | ✗ |  |
| general_circulation | numeric(18,8) | ✓ |  |
| stewardship_held | numeric(18,8) | ✓ |  |
| administration_held | numeric(18,8) | ✓ |  |
| general_pct | numeric(5,4) | ✓ |  |
| stewardship_pct | numeric(5,4) | ✓ |  |
| administration_pct | numeric(5,4) | ✓ |  |
| is_compliant | boolean | ✓ |  |
| details | jsonb | ✓ |  |
| active_holders | integer(32) | ✗ | 0 |
| new_holders_last_30_days | integer(32) | ✓ | 0 |
| whale_concentration_percent | numeric(10,4) | ✓ |  |
| gini_coefficient | numeric(10,8) | ✓ |  |
| distribution_metrics | jsonb | ✓ |  |

**Primary Key:**
- asset_holder_analysis_pkey: (id)

**Check Constraints:**
- chk_holders_positive: CHECK ((total_holders >= 0))
- chk_supply_positive: CHECK ((total_supply > (0)::numeric))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 16 kB
- BTREE: (asset_code, asset_issuer) - 16 kB
- BTREE: (is_compliant) - 16 kB
- BTREE: (analysis_date) - 16 kB
- BTREE: (asset_code, asset_issuer) - 16 kB
- BTREE: (analysis_date) - 16 kB

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### asset_holders

*Current token balances for all accounts*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('asset_holders_id_seq'::regclass) |
| account_id | character varying(56) | ✗ |  |
| asset_code | character varying(12) | ✗ |  |
| asset_issuer | character varying(56) | ✗ |  |
| balance | numeric(18,8) | ✗ | 0 |
| last_updated | timestamp without time zone | ✗ | now() |
| classification | character varying(20) | ✓ |  |

**Primary Key:**
- asset_holders_pkey: (id)

**Unique Constraints:**
- unique_holder_asset: (account_id, asset_code, asset_issuer)

**Check Constraints:**
- chk_balance_non_negative: CHECK ((balance >= (0)::numeric))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (account_id) - 8192 bytes
- BTREE: (asset_code, asset_issuer) - 8192 bytes
- BTREE: (balance) - 8192 bytes
- UNIQUE BTREE: (account_id, asset_code, asset_issuer) - 8192 bytes
- BTREE: (last_updated) - 8192 bytes
- UNIQUE BTREE: (account_id, asset_code, asset_issuer) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### bioregion_analysis

**Rows:** 9,013 | **Size:** 3048 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('bioregion_analysis_id_seq'::regclass) |
| account_id | character varying(56) | ✗ |  |
| community_id | integer(32) | ✗ |  |
| analysis_date | timestamp with time zone | ✓ | now() |
| source_type | character varying(20) | ✓ |  |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- bioregion_analysis_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 216 kB

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### constraint_violations

*Logs constraint violations for debugging and data quality monitoring*

**Rows:** 0 | **Size:** 32 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('constraint_violations_id_seq'::regclass) |
| table_name | character varying(100) | ✗ |  |
| constraint_name | character varying(100) | ✗ |  |
| violation_data | jsonb | ✓ |  |
| error_message | text | ✓ |  |
| occurred_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |

**Primary Key:**
- constraint_violations_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (table_name) - 8192 bytes
- BTREE: (occurred_at) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### distribution_history

*Historical record of distribution checks and rebalancing actions*

**Rows:** 10 | **Size:** 152 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('distribution_history_id_seq'::regclass) |
| check_date | timestamp without time zone | ✗ | now() |
| asset_code | character varying(12) | ✗ |  |
| asset_issuer | character varying(56) | ✗ |  |
| general_balance | numeric(18,8) | ✗ |  |
| admin_balance | numeric(18,8) | ✗ |  |
| stewardship_balance | numeric(18,8) | ✗ |  |
| total_supply | numeric(18,8) | ✓ |  |
| rebalance_needed | boolean | ✗ |  |
| transfers_initiated | integer(32) | ✓ | 0 |
| total_transfer_amount | numeric(18,8) | ✓ | 0 |
| details | jsonb | ✓ |  |
| general_percentage | numeric(10,4) | ✓ |  |
| admin_percentage | numeric(10,4) | ✓ |  |
| stewardship_percentage | numeric(10,4) | ✓ |  |

**Primary Key:**
- distribution_history_pkey: (id)

**Check Constraints:**
- chk_balances_positive: CHECK (((general_balance >= (0)::numeric) AND (admin_balance >= (0)::numeric) AND (stewardship_balance >= (0)::numeric)))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 16 kB
- BTREE: (asset_code, asset_issuer) - 16 kB
- BTREE: (check_date) - 16 kB
- GIN: (details) - 24 kB
- BTREE: (rebalance_needed) - 16 kB
- BTREE: (asset_code, asset_issuer) - 16 kB
- BTREE: (check_date) - 16 kB
- BTREE: (rebalance_needed) - 16 kB

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### distribution_state

*Distribution state tracking for Earth element (UBECgpi). Monitors tokenomics compliance (75/20/5).*

**Rows:** 12 | **Size:** 104 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('distribution_state_id_seq'::regclass) |
| asset_code *(Token code being tracked)* | character varying(12) | ✗ |  |
| category *(Distribution category: general_circulation, stewardship, or administration)* | character varying(50) | ✗ |  |
| current_amount | numeric(20,7) | ✓ | 0.0 |
| target_amount | numeric(20,7) | ✓ | 0.0 |
| target_percentage *(Target percentage for this category (75%, 20%, or 5%))* | numeric(5,2) | ✗ |  |
| actual_percentage *(Current actual percentage)* | numeric(5,2) | ✓ | 0.0 |
| is_compliant *(Whether current distribution is within compliance thresholds)* | boolean | ✓ | true |
| last_updated | timestamp with time zone | ✓ | now() |

**Primary Key:**
- distribution_state_pkey: (id)

**Unique Constraints:**
- distribution_state_unique_asset_category: (asset_code, category)

**Check Constraints:**
- distribution_state_amounts_check: CHECK (((current_amount >= (0)::numeric) AND (target_amount >= (0)::numeric)))
- distribution_state_percentages_check: CHECK (((target_percentage >= (0)::numeric) AND (target_percentage <= (100)::numeric)))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 16 kB
- UNIQUE BTREE: (asset_code, category) - 16 kB
- BTREE: (asset_code) - 16 kB
- BTREE: (category) - 16 kB
- BTREE: (is_compliant) - 16 kB
- BTREE: (last_updated) - 16 kB

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### distribution_transfers

*Records all distribution rebalancing transactions executed on Stellar blockchain*

**Rows:** 0 | **Size:** 80 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id *(Unique identifier for each transfer record)* | integer(32) | ✗ | nextval('distribution_transfers_id_seq'::regclass) |
| tx_hash *(Stellar transaction hash (unique identifier on blockchain))* | text | ✗ |  |
| from_account *(Source account public key (G...))* | text | ✗ |  |
| to_account *(Destination account public key (G...))* | text | ✗ |  |
| amount *(Amount transferred (in token units, up to 7 decimal places))* | numeric(20,7) | ✗ |  |
| asset_code *(Asset code (e.g., UBEC, UBECrc, etc.))* | text | ✗ |  |
| asset_issuer *(Asset issuer public key)* | text | ✗ |  |
| ledger *(Stellar ledger number where transaction was recorded)* | integer(32) | ✓ |  |
| memo *(Transaction memo text (max 28 characters))* | text | ✓ |  |
| network *(Network where transaction occurred (TESTNET or MAINNET))* | text | ✗ |  |
| executed_at *(Timestamp when transaction was executed on blockchain)* | timestamp without time zone | ✗ | now() |
| created_at *(Timestamp when record was created in database)* | timestamp without time zone | ✗ | now() |
| updated_at *(Timestamp when record was last updated)* | timestamp without time zone | ✗ | now() |
| notes *(Optional notes or metadata about the transfer)* | text | ✓ |  |
| recorded_by *(System or service that recorded this transfer)* | text | ✓ | 'distribution_service'::text |

**Primary Key:**
- distribution_transfers_pkey: (id)

**Unique Constraints:**
- distribution_transfers_tx_hash_key: (tx_hash)

**Check Constraints:**
- distribution_transfers_network_check: CHECK ((network = ANY (ARRAY['TESTNET'::text, 'MAINNET'::text])))
- positive_amount: CHECK ((amount > (0)::numeric))
- valid_network: CHECK ((network = ANY (ARRAY['TESTNET'::text, 'MAINNET'::text])))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- UNIQUE BTREE: (tx_hash) - 8192 bytes
- BTREE: (asset_code, asset_issuer) - 8192 bytes
- BTREE: (asset_code, executed_at) - 8192 bytes
- BTREE: (executed_at) - 8192 bytes
- BTREE: (from_account) - 8192 bytes
- BTREE: (network) - 8192 bytes
- BTREE: (to_account) - 8192 bytes
- BTREE: (tx_hash) - 8192 bytes

**Triggers:**
- **trigger_distribution_transfers_updated_at:** BEFORE UPDATE ROW
  - Calls: update_distribution_transfers_updated_at

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### flow_transactions

*Flow transactions tracking for Water element (UBECrc). Records all token flows.*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| transaction_id *(Stellar transaction hash)* | character varying(64) | ✗ |  |
| asset_code *(Token code involved in the transaction)* | character varying(12) | ✗ |  |
| from_account *(Sending Stellar account)* | character varying(56) | ✗ |  |
| to_account *(Receiving Stellar account)* | character varying(56) | ✗ |  |
| amount *(Amount transferred)* | numeric(20,7) | ✗ |  |
| created_at | timestamp with time zone | ✓ | now() |
| memo | text | ✓ |  |

**Primary Key:**
- flow_transactions_pkey: (transaction_id)

**Check Constraints:**
- flow_transactions_amount_check: CHECK ((amount > (0)::numeric))

**Indexes:**
- PRIMARY UNIQUE BTREE: (transaction_id) - 8192 bytes
- BTREE: (asset_code) - 8192 bytes
- BTREE: (asset_code, created_at) - 8192 bytes
- BTREE: (created_at) - 8192 bytes
- BTREE: (from_account) - 8192 bytes
- BTREE: (to_account) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### gateway_accounts

*Gateway accounts tracking for Air element (UBEC). Tracks account balances and trustline status.*

**Rows:** 0 | **Size:** 32 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| account_id *(Stellar public key (G... format))* | character varying(56) | ✗ |  |
| asset_code *(Token code: UBEC, UBECrc, UBECgpi, or UBECtt)* | character varying(12) | ✗ |  |
| balance *(Current token balance for this account)* | numeric(20,7) | ✓ | 0.0 |
| trustline_established *(Whether the account has established a trustline for this asset)* | boolean | ✓ | false |
| created_at | timestamp with time zone | ✓ | now() |
| last_activity | timestamp with time zone | ✓ | now() |
| transaction_count | integer(32) | ✓ | 0 |

**Primary Key:**
- gateway_accounts_pkey: (account_id)

**Check Constraints:**
- gateway_accounts_balance_check: CHECK ((balance >= (0)::numeric))
- gateway_accounts_tx_count_check: CHECK ((transaction_count >= 0))

**Indexes:**
- PRIMARY UNIQUE BTREE: (account_id) - 8192 bytes
- BTREE: (asset_code) - 8192 bytes
- BTREE: (last_activity) - 8192 bytes
- BTREE: (trustline_established) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### holder_discovery_history

**Rows:** 0 | **Size:** 16 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('holder_discovery_history_id_seq'::regclass) |
| discovery_date | timestamp without time zone | ✗ | now() |
| account_id | character varying(56) | ✗ |  |
| discovery_source | character varying(50) | ✗ |  |
| source_transaction_id | character varying(64) | ✓ |  |
| initial_balance | numeric(18,8) | ✓ | 0 |
| is_new | boolean | ✓ | true |
| added_to_tracking | boolean | ✓ | false |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- holder_discovery_history_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### holonic_metrics

*Stores holonic evaluation metrics for UBEC token holders*

**Rows:** 2,283 | **Size:** 3720 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('holonic_metrics_id_seq'::regclass) |
| evaluation_date *(Date and time when the evaluation was performed)* | timestamp with time zone | ✗ | now() |
| autonomy_integration_score *(Score for balance of autonomy and integration (0-1))* | numeric(5,4) | ✗ | 0 |
| multi_scale_score *(Score for multi-scale participation (0-1))* | numeric(5,4) | ✗ | 0 |
| regenerative_impact_score *(Score for regenerative impact (0-1))* | numeric(5,4) | ✗ | 0 |
| network_contribution_score *(Score for network contribution (0-1))* | numeric(5,4) | ✗ | 0 |
| ubuntu_alignment_score *(Score for Ubuntu philosophy alignment (0-1))* | numeric(5,4) | ✗ | 0 |
| composite_score *(Overall holonic score (0-1))* | numeric(5,4) | ✗ | 0 |
| holonic_category *(Category: Observer, Participant, Contributor, Integrator, or Exemplar)* | character varying(50) | ✗ | 'Observer'::character varying |
| raw_metrics *(JSON object containing detailed metrics for each dimension)* | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |
| evaluation_date_date | date | ✗ |  |
| account_id | character varying(56) | ✗ |  |
| confidence | numeric(10,6) | ✓ | 0.8 |
| calculation_mode | text | ✓ | 'transaction_based'::text |

**Primary Key:**
- holonic_metrics_pkey: (id)

**Unique Constraints:**
- uq_holonic_metrics_account_date: (account_id, evaluation_date)

**Check Constraints:**
- valid_autonomy_score: CHECK (((autonomy_integration_score >= (0)::numeric) AND (autonomy_integration_score <= (1)::numeric)))
- valid_composite_score: CHECK (((composite_score >= (0)::numeric) AND (composite_score <= (1)::numeric)))
- valid_holonic_category: CHECK (((holonic_category)::text = ANY ((ARRAY['Observer'::character varying, 'Participant'::character varying, 'Contributor'::character varying, 'Integrator'::character varying, 'Exemplar'::character varying])::text[])))
- valid_multi_scale_score: CHECK (((multi_scale_score >= (0)::numeric) AND (multi_scale_score <= (1)::numeric)))
- valid_network_score: CHECK (((network_contribution_score >= (0)::numeric) AND (network_contribution_score <= (1)::numeric)))
- valid_regenerative_score: CHECK (((regenerative_impact_score >= (0)::numeric) AND (regenerative_impact_score <= (1)::numeric)))
- valid_ubuntu_score: CHECK (((ubuntu_alignment_score >= (0)::numeric) AND (ubuntu_alignment_score <= (1)::numeric)))

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 152 kB
- UNIQUE BTREE: (account_id) - 280 kB
- BTREE: (account_id) - 144 kB
- BTREE: (calculation_mode) - 56 kB
- BTREE: (holonic_category) - 72 kB
- BTREE: (composite_score) - 168 kB
- BTREE: (confidence) - 136 kB
- BTREE: (evaluation_date) - 208 kB
- UNIQUE BTREE: (evaluation_date, account_id) - 376 kB

**Triggers:**
- **trg_set_evaluation_date_date:** BEFORE INSERT OR UPDATE ROW
  - Calls: set_evaluation_date_date
- **update_holonic_metrics_updated_at:** BEFORE UPDATE ROW
  - Calls: update_updated_at_column

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### holons

*Stores information about holons (groups/communities)*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('holons_id_seq'::regclass) |
| holon_id | character varying(100) | ✗ |  |
| holon_name | character varying(255) | ✗ |  |
| holon_type | character varying(100) | ✗ |  |
| description | text | ✓ |  |
| parent_holon_id | integer(32) | ✓ |  |
| metadata | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- holons_pkey: (id)

**Foreign Keys:**
- holons_parent_holon_id_fkey: (parent_holon_id) → ubec_main.holons(id)
  - ON UPDATE: NO ACTION, ON DELETE: SET NULL

**Unique Constraints:**
- holons_holon_id_key: (holon_id)

**Indexes:**
- UNIQUE BTREE: (holon_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- BTREE: (holon_id) - 8192 bytes
- BTREE: (holon_type) - 8192 bytes
- BTREE: (parent_holon_id) - 8192 bytes

**Triggers:**
- **update_holons_updated_at:** BEFORE UPDATE ROW
  - Calls: update_updated_at_column

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### liquidity_pool_owners

*Air element: Account ownership positions in liquidity pools. Tracks shares, percentages, and calculated UBEC balances for distribution compliance.*

**Rows:** 26 | **Size:** 936 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('liquidity_pool_owners_id_seq'::regclass) |
| account_id | character varying(56) | ✗ |  |
| liquidity_pool_id | character varying(64) | ✗ |  |
| shares *(Number of pool shares owned (like LP tokens))* | numeric(20,7) | ✗ | 0 |
| ownership_percentage *(Percentage of total pool owned (0-100))* | numeric(10,6) | ✗ | 0 |
| ubec_balance *(Calculated UBEC balance from this LP position)* | numeric(20,7) | ✗ | 0 |
| element *(Element classification (always air for gateway/access))* | USER-DEFINED | ✓ | 'air'::element_type |
| token_code *(Which UBEC token this position represents)* | USER-DEFINED | ✓ |  |
| metadata | jsonb | ✓ |  |
| last_modified_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| sync_timestamp | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| created_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| sync_status | character varying(20) | ✓ | 'synced'::character varying |

**Primary Key:**
- liquidity_pool_owners_pkey: (id)

**Foreign Keys:**
- fk_lp_owner_account: (account_id) → ubec_main.stellar_accounts(account_id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE
- fk_lp_owner_pool: (liquidity_pool_id) → ubec_main.liquidity_pools(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- unique_account_pool: (account_id, liquidity_pool_id)

**Check Constraints:**
- valid_percentage: CHECK (((ownership_percentage >= (0)::numeric) AND (ownership_percentage <= (100)::numeric)))
- valid_shares: CHECK ((shares >= (0)::numeric))
- valid_ubec_balance: CHECK ((ubec_balance >= (0)::numeric))

**Indexes:**
- BTREE: (account_id) - 16 kB
- BTREE: (account_id, ubec_balance) - 240 kB
- BTREE: (account_id, token_code) - 16 kB
- BTREE: (ubec_balance) - 88 kB
- BTREE: (element) - 16 kB
- BTREE: (last_modified_at) - 128 kB
- BTREE: (liquidity_pool_id) - 16 kB
- BTREE: (sync_status) - 32 kB
- BTREE: (sync_timestamp) - 128 kB
- BTREE: (token_code) - 16 kB
- PRIMARY UNIQUE BTREE: (id) - 16 kB
- UNIQUE BTREE: (account_id, liquidity_pool_id) - 16 kB

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### liquidity_pools

*Stellar liquidity pools containing UBEC tokens*

**Rows:** 10 | **Size:** 336 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id *(Stellar liquidity pool ID (64-byte hex string))* | character varying(64) | ✗ |  |
| asset_a_code | character varying(12) | ✗ |  |
| asset_a_issuer | character varying(56) | ✓ |  |
| asset_b_code | character varying(12) | ✗ |  |
| asset_b_issuer | character varying(56) | ✓ |  |
| pair *(Human-readable pair name (e.g., UBEC/XLM))* | character varying(50) | ✗ |  |
| primary_element *(Element classification (always air for gateway/access))* | USER-DEFINED | ✓ | 'air'::element_type |
| token_code *(Which UBEC token is in this pool (UBEC, UBECrc, UBECgpi, or UBECtt))* | USER-DEFINED | ✓ |  |
| reserve_a | numeric(20,7) | ✗ | 0 |
| reserve_b | numeric(20,7) | ✗ | 0 |
| total_shares *(Total pool shares issued (like LP tokens))* | numeric(20,7) | ✗ | 0 |
| balance *(Total UBEC tokens in this pool)* | numeric(20,7) | ✗ | 0 |
| ubec_asset_position *(Whether UBEC is asset_a or asset_b in the pool)* | character(1) | ✓ |  |
| fee_bp | integer(32) | ✓ | 30 |
| trustline_count | integer(32) | ✓ | 0 |
| metadata | jsonb | ✓ |  |
| last_modified_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| sync_timestamp | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| created_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| sync_status | character varying(20) | ✓ | 'synced'::character varying |

**Primary Key:**
- liquidity_pools_pkey: (id)

**Check Constraints:**
- liquidity_pools_ubec_asset_position_check: CHECK ((ubec_asset_position = ANY (ARRAY['a'::bpchar, 'b'::bpchar])))
- valid_balance: CHECK ((balance >= (0)::numeric))
- valid_fee: CHECK (((fee_bp >= 0) AND (fee_bp <= 10000)))
- valid_reserves: CHECK (((reserve_a >= (0)::numeric) AND (reserve_b >= (0)::numeric)))
- valid_shares: CHECK ((total_shares >= (0)::numeric))
- valid_trustlines: CHECK ((trustline_count >= 0))

**Indexes:**
- BTREE: (asset_a_code, asset_a_issuer) - 16 kB
- BTREE: (asset_b_code, asset_b_issuer) - 16 kB
- BTREE: (balance) - 40 kB
- BTREE: (primary_element) - 16 kB
- BTREE: (last_modified_at) - 40 kB
- BTREE: (pair) - 16 kB
- BTREE: (sync_status) - 16 kB
- BTREE: (sync_timestamp) - 40 kB
- BTREE: (token_code) - 16 kB
- PRIMARY UNIQUE BTREE: (id) - 16 kB

**Triggers:**
- **trg_sync_lp_pool_metadata:** BEFORE INSERT OR UPDATE ROW
  - Calls: sync_lp_pool_metadata
- **trg_update_lp_ownership:** AFTER UPDATE ROW
  - Calls: update_lp_ownership_percentages

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### monitored_accounts

*Tracks special accounts (administration, stewardship, general) for tokenomics compliance monitoring. Used by analytics service to calculate locked supply and liquidity ratios.*

**Rows:** 5 | **Size:** 80 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| account_id *(Stellar public key (G... format))* | character varying(56) | ✗ |  |
| account_type *(Account classification for tokenomics: general (65% target), administration (5% target), stewardship (30% target))* | character varying(20) | ✗ |  |
| account_name | character varying(100) | ✓ |  |
| description | text | ✓ |  |
| monitored_since | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| is_active | boolean | ✓ | true |
| metadata | jsonb | ✓ | '{}'::jsonb |
| created_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| updated_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |

**Primary Key:**
- monitored_accounts_pkey: (account_id)

**Check Constraints:**
- monitored_accounts_account_type_check: CHECK (((account_type)::text = ANY ((ARRAY['general'::character varying, 'administration'::character varying, 'stewardship'::character varying])::text[])))
- valid_account_id: CHECK (((account_id)::text ~ '^G[A-Z0-9]{55}$'::text))
- valid_account_name: CHECK (((account_name IS NULL) OR (length((account_name)::text) > 0)))

**Indexes:**
- BTREE: (is_active) - 16 kB
- BTREE: (account_id, account_type) - 16 kB
- BTREE: (account_type) - 16 kB
- PRIMARY UNIQUE BTREE: (account_id) - 16 kB

**Triggers:**
- **trg_monitored_accounts_updated_at:** BEFORE UPDATE ROW
  - Calls: update_monitored_accounts_timestamp

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### mutualism_relationships

*Tracks mutualistic relationships between accounts in the Earth element (UBECgpi). Represents the Ubuntu principle of mutualism.*

**Rows:** 0 | **Size:** 64 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('mutualism_relationships_id_seq'::regclass) |
| asset_code *(Token code for the relationship (primarily UBECgpi))* | character varying(12) | ✗ |  |
| account_a *(First account in the relationship (Stellar public key))* | character varying(56) | ✗ |  |
| account_b *(Second account in the relationship (Stellar public key))* | character varying(56) | ✗ |  |
| interaction_count *(Number of mutual interactions between accounts)* | integer(32) | ✓ | 0 |
| mutual_benefit_score *(Score representing mutual benefit (0-1, where 1 is maximum mutual benefit))* | numeric(5,4) | ✓ | 0.0 |
| relationship_strength *(Overall strength of the relationship (0-1, composite of interactions and benefits))* | numeric(5,4) | ✓ | 0.0 |
| last_interaction *(Timestamp of most recent interaction)* | timestamp with time zone | ✓ | now() |
| first_interaction | timestamp with time zone | ✓ | now() |
| created_at | timestamp with time zone | ✓ | now() |
| updated_at | timestamp with time zone | ✓ | now() |

**Primary Key:**
- mutualism_relationships_pkey: (id)

**Unique Constraints:**
- mutualism_relationships_unique_pair: (asset_code, account_a, account_b)

**Check Constraints:**
- mutualism_relationships_interaction_count_check: CHECK ((interaction_count >= 0))
- mutualism_relationships_mutual_benefit_check: CHECK (((mutual_benefit_score >= (0)::numeric) AND (mutual_benefit_score <= (1)::numeric)))
- mutualism_relationships_strength_check: CHECK (((relationship_strength >= (0)::numeric) AND (relationship_strength <= (1)::numeric)))

**Indexes:**
- BTREE: (account_a) - 8192 bytes
- BTREE: (account_b) - 8192 bytes
- BTREE: (asset_code) - 8192 bytes
- BTREE: (asset_code, relationship_strength) - 8192 bytes
- BTREE: (last_interaction) - 8192 bytes
- BTREE: (relationship_strength) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- UNIQUE BTREE: (asset_code, account_a, account_b) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### orderbook_analytics

*Pre-computed order book analytics and market metrics*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('orderbook_analytics_id_seq'::regclass) |
| asset_code | USER-DEFINED | ✗ |  |
| analysis_time | timestamp with time zone | ✗ | now() |
| total_liquidity | numeric(20,7) | ✓ |  |
| buy_pressure *(Buy pressure score 0-100 (higher = more buying))* | numeric(10,4) | ✓ |  |
| sell_pressure *(Sell pressure score 0-100 (higher = more selling))* | numeric(10,4) | ✓ |  |
| market_depth_score *(Overall market depth quality 0-100)* | numeric(10,4) | ✓ |  |
| price_stability_score | numeric(10,4) | ✓ |  |
| top_10_buyers_volume | numeric(20,7) | ✓ |  |
| top_10_sellers_volume | numeric(20,7) | ✓ |  |
| unique_buyers | integer(32) | ✓ |  |
| unique_sellers | integer(32) | ✓ |  |
| metrics *(Extended metrics in JSON format for flexibility)* | jsonb | ✓ |  |

**Primary Key:**
- orderbook_analytics_pkey: (id)

**Unique Constraints:**
- unique_analysis: (asset_code, analysis_time)

**Indexes:**
- BTREE: (asset_code) - 8192 bytes
- BTREE: (asset_code, analysis_time) - 8192 bytes
- BTREE: (analysis_time) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- UNIQUE BTREE: (asset_code, analysis_time) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### orderbook_snapshots

*Historical order book snapshots for market analysis*

**Rows:** 12 | **Size:** 96 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('orderbook_snapshots_id_seq'::regclass) |
| asset_code | USER-DEFINED | ✗ |  |
| counter_asset | character varying(12) | ✗ |  |
| snapshot_time | timestamp with time zone | ✗ | now() |
| best_bid | numeric(20,7) | ✓ |  |
| best_ask | numeric(20,7) | ✓ |  |
| spread_bps *(Bid-ask spread in basis points (1 bps = 0.01%))* | integer(32) | ✓ |  |
| bid_depth_total | numeric(20,7) | ✓ |  |
| ask_depth_total | numeric(20,7) | ✓ |  |
| bid_levels | integer(32) | ✓ |  |
| ask_levels | integer(32) | ✓ |  |
| raw_data *(JSON snapshot of top 10 bid/ask levels)* | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- orderbook_snapshots_pkey: (id)

**Unique Constraints:**
- unique_snapshot: (asset_code, counter_asset, snapshot_time)

**Indexes:**
- BTREE: (asset_code, counter_asset) - 16 kB
- BTREE: (asset_code, snapshot_time) - 16 kB
- BTREE: (snapshot_time) - 16 kB
- PRIMARY UNIQUE BTREE: (id) - 16 kB
- UNIQUE BTREE: (asset_code, counter_asset, snapshot_time) - 16 kB

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### participants

*Categorization of accounts (general, administration, stewardship)*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('participants_id_seq'::regclass) |
| account_id | character varying(56) | ✗ |  |
| account_type | character varying(50) | ✗ |  |
| account_label | character varying(100) | ✓ |  |
| is_active | boolean | ✓ | true |
| created_at | timestamp without time zone | ✗ | now() |
| updated_at | timestamp without time zone | ✗ | now() |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- participants_pkey: (id)

**Unique Constraints:**
- participants_account_id_key: (account_id)

**Check Constraints:**
- chk_account_type: CHECK (((account_type)::text = ANY ((ARRAY['general'::character varying, 'administration'::character varying, 'stewardship'::character varying, 'issuer'::character varying, 'other'::character varying])::text[])))

**Indexes:**
- BTREE: (account_id) - 8192 bytes
- BTREE: (account_id) - 8192 bytes
- BTREE: (is_active) - 8192 bytes
- BTREE: (account_type) - 8192 bytes
- UNIQUE BTREE: (account_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Triggers:**
- **trg_participants_updated:** BEFORE UPDATE ROW
  - Calls: update_timestamp

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### reciprocity_transactions

*Transactions affecting reciprocity scores*

**Rows:** 0 | **Size:** 72 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('reciprocity_transactions_id_seq'::regclass) |
| account_id | character varying(56) | ✗ |  |
| transaction_type | character varying(20) | ✗ |  |
| amount | numeric(18,8) | ✗ |  |
| reason | text | ✓ |  |
| source | character varying(50) | ✓ |  |
| context | jsonb | ✓ |  |
| created_at | timestamp without time zone | ✗ | now() |

**Primary Key:**
- reciprocity_transactions_pkey: (id)

**Check Constraints:**
- chk_reciprocity_tx_type: CHECK (((transaction_type)::text = ANY ((ARRAY['credit'::character varying, 'debit'::character varying, 'adjustment'::character varying])::text[])))

**Indexes:**
- BTREE: (account_id) - 8192 bytes
- BTREE: (created_at) - 8192 bytes
- BTREE: (transaction_type) - 8192 bytes
- BTREE: (account_id) - 8192 bytes
- BTREE: (created_at) - 8192 bytes
- BTREE: (source) - 8192 bytes
- BTREE: (transaction_type) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### regenerative_projects

*Stores information about regenerative projects linked to agents*

**Rows:** 0 | **Size:** 48 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('regenerative_projects_id_seq'::regclass) |
| agent_id | integer(32) | ✗ |  |
| project_name | character varying(255) | ✗ |  |
| description | text | ✓ |  |
| project_type | character varying(100) | ✗ |  |
| verification_status | character varying(50) | ✓ | 'unverified'::character varying |
| verification_date | timestamp with time zone | ✓ |  |
| impact_metrics | jsonb | ✓ |  |
| metadata | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |

**Primary Key:**
- regenerative_projects_pkey: (id)

**Foreign Keys:**
- regenerative_projects_agent_id_fkey: (agent_id) → ubec_main.agents(id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Check Constraints:**
- valid_verification_status: CHECK (((verification_status)::text = ANY ((ARRAY['unverified'::character varying, 'pending'::character varying, 'verified'::character varying, 'rejected'::character varying])::text[])))

**Indexes:**
- BTREE: (agent_id) - 8192 bytes
- BTREE: (project_type) - 8192 bytes
- BTREE: (verification_status) - 8192 bytes
- BTREE: (verification_status) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Triggers:**
- **update_regenerative_projects_updated_at:** BEFORE UPDATE ROW
  - Calls: update_updated_at_column

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### scheduler_jobs

*Scheduled jobs for automated distribution management*

**Rows:** 7 | **Size:** 112 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('scheduler_jobs_id_seq'::regclass) |
| job_name | character varying(100) | ✗ |  |
| schedule_interval | character varying(50) | ✗ |  |
| next_run | timestamp without time zone | ✗ |  |
| last_run | timestamp without time zone | ✓ |  |
| job_function | text | ✗ |  |
| parameters | jsonb | ✓ |  |
| enabled | boolean | ✓ | true |
| created_at | timestamp without time zone | ✗ | now() |
| updated_at | timestamp without time zone | ✗ | now() |

**Primary Key:**
- scheduler_jobs_pkey: (id)

**Unique Constraints:**
- scheduler_jobs_job_name_key: (job_name)

**Check Constraints:**
- chk_next_run_valid: CHECK ((next_run > created_at))

**Indexes:**
- BTREE: (enabled) - 16 kB
- BTREE: (next_run) - 16 kB
- UNIQUE BTREE: (job_name) - 16 kB
- PRIMARY UNIQUE BTREE: (id) - 16 kB

**Triggers:**
- **trg_scheduler_jobs_updated:** BEFORE UPDATE ROW
  - Calls: update_timestamp

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### schema_migrations

*Tracks all schema migrations applied to the database. Provides audit trail and version control for database structure changes.*

**Rows:** 2 | **Size:** 80 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| migration_id *(Auto-incrementing primary key)* | integer(32) | ✗ | nextval('schema_migrations_migration_id_seq'::regclass) |
| migration_name *(Unique migration identifier, typically: YYYYMMDD_HHMM_description)* | character varying(255) | ✗ |  |
| applied_at *(Timestamp when migration was executed)* | timestamp without time zone | ✗ | now() |
| applied_by *(Database user who executed the migration)* | character varying(100) | ✗ |  |
| description *(Human-readable description of what the migration does)* | text | ✓ |  |
| checksum *(SHA256 checksum of migration file for integrity verification)* | character varying(64) | ✓ |  |
| execution_time_ms *(How long the migration took to execute (milliseconds))* | integer(32) | ✓ |  |
| status *(Migration status: completed, failed, or rolled_back)* | character varying(20) | ✗ | 'completed'::character varying |
| error_message *(Error details if migration failed)* | text | ✓ |  |
| rollback_script *(SQL script to reverse this migration if needed)* | text | ✓ |  |

**Primary Key:**
- schema_migrations_pkey: (migration_id)

**Unique Constraints:**
- schema_migrations_migration_name_key: (migration_name)

**Check Constraints:**
- chk_migration_status: CHECK (((status)::text = ANY ((ARRAY['completed'::character varying, 'failed'::character varying, 'rolled_back'::character varying])::text[])))

**Indexes:**
- BTREE: (applied_at) - 16 kB
- BTREE: (status) - 16 kB
- UNIQUE BTREE: (migration_name) - 16 kB
- PRIMARY UNIQUE BTREE: (migration_id) - 16 kB

**Permissions:**
- **ubec_app:** DELETE, INSERT, SELECT, UPDATE

---

#### stellar_accounts

*Stellar blockchain accounts with element tracking*

**Rows:** 1,481 | **Size:** 1032 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('stellar_accounts_id_seq'::regclass) |
| account_id | character varying(56) | ✗ |  |
| primary_element | USER-DEFINED | ✓ |  |
| token_holdings | ARRAY | ✓ |  |
| sequence | bigint(64) | ✓ |  |
| subentry_count | integer(32) | ✓ | 0 |
| inflation_destination | character varying(56) | ✓ |  |
| home_domain | character varying(255) | ✓ |  |
| thresholds | jsonb | ✓ |  |
| flags | jsonb | ✓ |  |
| signers | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✓ |  |
| last_modified_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| last_activity_at | timestamp with time zone | ✓ |  |
| sync_status | character varying(20) | ✓ | 'pending'::character varying |
| sync_cursor | character varying(100) | ✓ |  |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- stellar_accounts_pkey: (id)

**Unique Constraints:**
- stellar_accounts_account_id_key: (account_id)

**Check Constraints:**
- valid_account_id: CHECK ((length((account_id)::text) = 56))

**Indexes:**
- BTREE: (account_id) - 216 kB
- BTREE: (last_activity_at) - 40 kB
- BTREE: (created_at) - 40 kB
- BTREE: (primary_element) - 40 kB
- UNIQUE BTREE: (account_id) - 216 kB
- PRIMARY UNIQUE BTREE: (id) - 72 kB

**Triggers:**
- **trg_stellar_accounts_modified:** BEFORE UPDATE ROW
  - Calls: update_modified_timestamp

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** INSERT, SELECT, UPDATE

---

#### stellar_effects

*Stellar blockchain effects with element context*

**Rows:** 0 | **Size:** 80 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('stellar_effects_id_seq'::regclass) |
| effect_id | character varying(100) | ✗ |  |
| operation_id | character varying(100) | ✗ |  |
| effect_element | USER-DEFINED | ✓ |  |
| type | character varying(50) | ✗ |  |
| account | character varying(56) | ✓ |  |
| amount | numeric(20,7) | ✓ |  |
| asset_type | character varying(20) | ✓ |  |
| asset_code | USER-DEFINED | ✓ |  |
| asset_issuer | character varying(56) | ✓ |  |
| details | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ |  |

**Primary Key:**
- stellar_effects_pkey: (id)

**Foreign Keys:**
- fk_operation_id: (operation_id) → ubec_main.stellar_operations(operation_id)
  - ON UPDATE: NO ACTION, ON DELETE: NO ACTION

**Unique Constraints:**
- stellar_effects_effect_id_key: (effect_id)

**Indexes:**
- BTREE: (account) - 8192 bytes
- BTREE: (asset_code) - 8192 bytes
- BTREE: (created_at) - 8192 bytes
- BTREE: (effect_element) - 8192 bytes
- BTREE: (effect_id) - 8192 bytes
- BTREE: (operation_id) - 8192 bytes
- BTREE: (type) - 8192 bytes
- UNIQUE BTREE: (effect_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** INSERT, SELECT, UPDATE

---

#### stellar_offers

*Individual offers/orders on Stellar DEX for UBEC tokens*

**Rows:** 0 | **Size:** 72 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('stellar_offers_id_seq'::regclass) |
| offer_id | bigint(64) | ✗ |  |
| seller_account | character varying(56) | ✗ |  |
| selling_asset | USER-DEFINED | ✓ |  |
| buying_asset | character varying(12) | ✗ |  |
| amount | numeric(20,7) | ✗ |  |
| price | numeric(20,7) | ✗ |  |
| price_r_n *(Price as ratio numerator (for exact precision))* | integer(32) | ✓ |  |
| price_r_d *(Price as ratio denominator (for exact precision))* | integer(32) | ✓ |  |
| side *(Whether this is a buy or sell order for UBEC tokens)* | character varying(4) | ✗ |  |
| is_passive *(Passive orders do not take offers of equal price)* | boolean | ✓ | false |
| last_modified_ledger | bigint(64) | ✓ |  |
| last_modified_time | timestamp with time zone | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |
| status | character varying(20) | ✓ | 'active'::character varying |

**Primary Key:**
- stellar_offers_pkey: (id)

**Foreign Keys:**
- fk_seller: (seller_account) → ubec_main.stellar_accounts(account_id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- stellar_offers_offer_id_key: (offer_id)

**Check Constraints:**
- stellar_offers_side_check: CHECK (((side)::text = ANY ((ARRAY['buy'::character varying, 'sell'::character varying])::text[])))
- stellar_offers_status_check: CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'filled'::character varying, 'cancelled'::character varying])::text[])))

**Indexes:**
- BTREE: (selling_asset, buying_asset) - 8192 bytes
- BTREE: (seller_account) - 8192 bytes
- BTREE: (selling_asset) - 8192 bytes
- BTREE: (side) - 8192 bytes
- BTREE: (status) - 8192 bytes
- BTREE: (selling_asset, status) - 8192 bytes
- BTREE: (last_modified_time) - 8192 bytes
- UNIQUE BTREE: (offer_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Triggers:**
- **trigger_update_position:** AFTER INSERT OR UPDATE ROW
  - Calls: update_account_position

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### stellar_operations

*Stellar blockchain operations with element and asset tracking*

**Rows:** 30,889 | **Size:** 29 MB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('stellar_operations_id_seq'::regclass) |
| operation_id | character varying(100) | ✗ |  |
| transaction_hash | character varying(64) | ✗ |  |
| operation_element | USER-DEFINED | ✓ |  |
| asset_code | USER-DEFINED | ✓ |  |
| type | USER-DEFINED | ✗ |  |
| type_i | integer(32) | ✓ |  |
| source_account | character varying(56) | ✓ |  |
| amount | numeric(20,7) | ✓ |  |
| asset_type | character varying(20) | ✓ |  |
| asset_issuer | character varying(56) | ✓ |  |
| from_account | character varying(56) | ✓ |  |
| to_account | character varying(56) | ✓ |  |
| details | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✗ |  |
| metadata | jsonb | ✓ |  |
| exchange_source_asset | character varying(12) | ✓ |  |
| exchange_source_amount | numeric(18,8) | ✓ |  |
| exchange_dest_asset | character varying(12) | ✓ |  |
| exchange_dest_amount | numeric(18,8) | ✓ |  |

**Primary Key:**
- stellar_operations_pkey: (id)

**Foreign Keys:**
- fk_transaction_hash: (transaction_hash) → ubec_main.stellar_transactions(transaction_hash)
  - ON UPDATE: NO ACTION, ON DELETE: NO ACTION

**Unique Constraints:**
- stellar_operations_operation_id_key: (operation_id)

**Indexes:**
- BTREE: (asset_code) - 240 kB
- BTREE: (created_at) - 936 kB
- BTREE: (operation_element) - 240 kB
- BTREE: (from_account) - 368 kB
- BTREE: (operation_id) - 1672 kB
- BTREE: (to_account) - 448 kB
- BTREE: (transaction_hash) - 3320 kB
- BTREE: (type) - 248 kB
- BTREE: (asset_code, from_account, to_account, created_at) - 7112 kB
- BTREE: (asset_code) - 16 kB
- BTREE: (created_at) - 864 kB
- BTREE: (from_account) - 288 kB
- BTREE: (asset_code, from_account) - 288 kB
- BTREE: (source_account) - 360 kB
- BTREE: (to_account) - 376 kB
- BTREE: (asset_code, to_account) - 384 kB
- UNIQUE BTREE: (operation_id) - 1640 kB
- PRIMARY UNIQUE BTREE: (id) - 736 kB

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** INSERT, SELECT, UPDATE

---

#### stellar_transactions

*Stellar blockchain transactions with element context*

**Rows:** 98,549 | **Size:** 60 MB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('stellar_transactions_id_seq'::regclass) |
| transaction_hash | character varying(64) | ✗ |  |
| ledger_sequence | bigint(64) | ✗ |  |
| primary_element | USER-DEFINED | ✓ |  |
| involves_tokens | ARRAY | ✓ |  |
| source_account | character varying(56) | ✗ |  |
| source_account_sequence | bigint(64) | ✓ |  |
| fee_charged | bigint(64) | ✓ |  |
| max_fee | bigint(64) | ✓ |  |
| operation_count | integer(32) | ✓ |  |
| time_bounds | jsonb | ✓ |  |
| memo_type | character varying(20) | ✓ |  |
| memo | character varying(255) | ✓ |  |
| successful | boolean | ✓ | true |
| result_code | text | ✓ |  |
| result_xdr | text | ✓ |  |
| created_at | timestamp with time zone | ✗ |  |
| ledger_close_time | timestamp with time zone | ✓ |  |
| metadata | jsonb | ✓ |  |
| ledger *(Ledger sequence number where this transaction was included)* | bigint(64) | ✓ |  |

**Primary Key:**
- stellar_transactions_pkey: (id)

**Foreign Keys:**
- fk_source_account: (source_account) → ubec_main.stellar_accounts(account_id)
  - ON UPDATE: NO ACTION, ON DELETE: NO ACTION

**Unique Constraints:**
- stellar_transactions_transaction_hash_key: (transaction_hash)

**Indexes:**
- BTREE: (created_at) - 2880 kB
- BTREE: (primary_element) - 1088 kB
- BTREE: (transaction_hash) - 12 MB
- BTREE: (ledger_sequence) - 1112 kB
- BTREE: (source_account) - 1256 kB
- GIN: (involves_tokens) - 480 kB
- PRIMARY UNIQUE BTREE: (id) - 2408 kB
- UNIQUE BTREE: (transaction_hash) - 12 MB

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** INSERT, SELECT, UPDATE

---

#### sync_jobs

**Rows:** 0 | **Size:** 16 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('sync_jobs_id_seq'::regclass) |
| job_type | character varying(50) | ✗ |  |
| schedule_interval | interval | ✗ |  |
| last_run | timestamp without time zone | ✓ |  |
| next_run | timestamp without time zone | ✗ |  |
| enabled | boolean | ✓ | true |
| parameters | jsonb | ✓ |  |
| last_status | character varying(20) | ✓ |  |
| error_message | text | ✓ |  |
| created_at | timestamp without time zone | ✗ | now() |
| updated_at | timestamp without time zone | ✗ | now() |

**Primary Key:**
- sync_jobs_pkey: (id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### sync_status

**Rows:** 0 | **Size:** 16 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| account_id | character varying(56) | ✗ |  |
| last_sync | timestamp without time zone | ✗ | now() |
| last_block_height | bigint(64) | ✓ |  |
| last_ledger_sequence | bigint(64) | ✓ |  |
| last_transaction_id | character varying(64) | ✓ |  |
| sync_count | integer(32) | ✓ | 0 |
| status | character varying(20) | ✓ | 'active'::character varying |
| error_count | integer(32) | ✓ | 0 |
| last_error | text | ✓ |  |
| last_error_at | timestamp without time zone | ✓ |  |

**Primary Key:**
- sync_status_pkey: (account_id)

**Indexes:**
- PRIMARY UNIQUE BTREE: (account_id) - 8192 bytes

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)

---

#### system_configuration

*System-wide configuration parameters*

**Rows:** 10 | **Size:** 96 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('system_configuration_id_seq'::regclass) |
| parameter_name | character varying(100) | ✗ |  |
| parameter_value | text | ✗ |  |
| parameter_type | character varying(20) | ✓ | 'string'::character varying |
| description | text | ✓ |  |
| is_sensitive | boolean | ✓ | false |
| created_at | timestamp without time zone | ✗ | now() |
| updated_at | timestamp without time zone | ✗ | now() |

**Primary Key:**
- system_configuration_pkey: (id)

**Unique Constraints:**
- system_configuration_parameter_name_key: (parameter_name)

**Check Constraints:**
- chk_parameter_type: CHECK (((parameter_type)::text = ANY ((ARRAY['string'::character varying, 'number'::character varying, 'boolean'::character varying, 'json'::character varying, 'address'::character varying])::text[])))

**Indexes:**
- BTREE: (parameter_name) - 16 kB
- BTREE: (parameter_type) - 16 kB
- BTREE: (parameter_name) - 16 kB
- UNIQUE BTREE: (parameter_name) - 16 kB
- PRIMARY UNIQUE BTREE: (id) - 16 kB

**Triggers:**
- **trg_system_config_updated:** BEFORE UPDATE ROW
  - Calls: update_timestamp

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### system_settings

*System configuration settings - single source of truth for all system parameters*

**Rows:** 73 | **Size:** 144 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| setting_id | integer(32) | ✗ | nextval('system_settings_setting_id_seq'::regclass) |
| setting_key *(Unique setting identifier)* | character varying(100) | ✗ |  |
| setting_value *(Setting value (stored as text, converted based on setting_type))* | text | ✗ |  |
| setting_type *(Data type of the setting (string, integer, float, boolean, json))* | character varying(20) | ✓ | 'string'::character varying |
| description | text | ✓ |  |
| category *(Setting category for organization)* | character varying(50) | ✓ | 'general'::character varying |
| is_active *(Whether the setting is active)* | boolean | ✓ | true |
| is_encrypted *(Whether the setting value is encrypted)* | boolean | ✓ | false |
| created_at | timestamp without time zone | ✓ | now() |
| updated_at | timestamp without time zone | ✓ | now() |
| created_by | character varying(100) | ✓ |  |
| updated_by | character varying(100) | ✓ |  |

**Primary Key:**
- system_settings_pkey: (setting_id)

**Unique Constraints:**
- system_settings_setting_key_key: (setting_key)

**Check Constraints:**
- system_settings_setting_type_check: CHECK (((setting_type)::text = ANY ((ARRAY['string'::character varying, 'integer'::character varying, 'float'::character varying, 'boolean'::character varying, 'json'::character varying])::text[])))

**Indexes:**
- BTREE: (category) - 16 kB
- BTREE: (setting_key) - 16 kB
- BTREE: (setting_key, is_active) - 16 kB
- BTREE: (setting_key) - 16 kB
- PRIMARY UNIQUE BTREE: (setting_id) - 16 kB
- UNIQUE BTREE: (setting_key) - 16 kB

**Triggers:**
- **trg_update_system_settings_timestamp:** BEFORE UPDATE ROW
  - Calls: update_system_settings_timestamp

**Permissions:**
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** SELECT

---

#### transfer_recommendations

*Recommended token transfers for distribution rebalancing*

**Rows:** 0 | **Size:** 80 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('transfer_recommendations_id_seq'::regclass) |
| recommendation_date | timestamp without time zone | ✗ | now() |
| asset_code | character varying(12) | ✗ |  |
| asset_issuer | character varying(56) | ✗ |  |
| from_account_type | character varying(50) | ✗ |  |
| to_account_type | character varying(50) | ✗ |  |
| amount | numeric(18,8) | ✗ |  |
| status | character varying(20) | ✗ | 'pending'::character varying |
| status_message | text | ✓ |  |
| transaction_hash | character varying(64) | ✓ |  |
| actual_amount | numeric(18,8) | ✓ |  |
| priority | integer(32) | ✓ | 5 |
| created_at | timestamp without time zone | ✗ | now() |
| updated_at | timestamp without time zone | ✗ | now() |
| completed_at | timestamp without time zone | ✓ |  |

**Primary Key:**
- transfer_recommendations_pkey: (id)

**Check Constraints:**
- chk_transfer_amount_positive: CHECK ((amount > (0)::numeric))
- chk_transfer_status: CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying, 'cancelled'::character varying])::text[])))

**Indexes:**
- BTREE: (asset_code, asset_issuer) - 8192 bytes
- BTREE: (recommendation_date) - 8192 bytes
- BTREE: (priority) - 8192 bytes
- BTREE: (status) - 8192 bytes
- BTREE: (asset_code, asset_issuer) - 8192 bytes
- BTREE: (created_at) - 8192 bytes
- BTREE: (recommendation_date) - 8192 bytes
- BTREE: (status) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Triggers:**
- **trg_transfer_rec_updated:** BEFORE UPDATE ROW
  - Calls: update_timestamp

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### transformation_phases

*Tracks transformation phases and their momentum in the Ubuntu Economic Commons (Fire Element - UBECtt)*

**Rows:** 0 | **Size:** 96 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('transformation_phases_id_seq'::regclass) |
| phase_id *(Unique identifier for the transformation phase)* | character varying(255) | ✗ |  |
| name *(Name of the transformation phase)* | character varying(255) | ✗ |  |
| description *(Detailed description of the phase)* | text | ✗ |  |
| start_date *(When the transformation phase began)* | timestamp with time zone | ✗ |  |
| end_date *(When the transformation phase ended (NULL if ongoing))* | timestamp with time zone | ✓ |  |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |
| target_outcomes *(Array of target outcomes for this phase)* | ARRAY | ✓ | '{}'::text[] |
| key_indicators *(Key performance indicators tracked during this phase)* | jsonb | ✓ | '{}'::jsonb |
| participating_agents *(Array of Stellar account IDs participating in this phase)* | ARRAY | ✓ | '{}'::text[] |
| actions_completed *(Number of transformative actions completed in this phase)* | integer(32) | ✓ | 0 |
| total_ubectt_distributed *(Total UBECtt tokens distributed during this phase)* | numeric(20,7) | ✓ | 0.0 |
| phase_momentum *(Rate of transformation in this phase (0.0 - 1.0))* | numeric(5,4) | ✓ | 0.0 |
| is_active *(Whether this phase is currently active)* | boolean | ✓ | true |
| completion_percentage *(Percentage of phase completion (0 - 100))* | numeric(5,2) | ✓ | 0.0 |
| metadata *(Additional metadata in JSON format)* | jsonb | ✓ | '{}'::jsonb |

**Primary Key:**
- transformation_phases_pkey: (id)

**Unique Constraints:**
- transformation_phases_phase_id_key: (phase_id)

**Check Constraints:**
- transformation_phases_actions_completed_check: CHECK ((actions_completed >= 0))
- transformation_phases_completion_percentage_check: CHECK (((completion_percentage >= (0)::numeric) AND (completion_percentage <= (100)::numeric)))
- transformation_phases_phase_momentum_check: CHECK (((phase_momentum >= (0)::numeric) AND (phase_momentum <= (1)::numeric)))
- transformation_phases_total_ubectt_distributed_check: CHECK ((total_ubectt_distributed >= (0)::numeric))

**Indexes:**
- BTREE: (is_active) - 8192 bytes
- GIN: (participating_agents) - 16 kB
- BTREE: (completion_percentage) - 8192 bytes
- BTREE: (end_date) - 8192 bytes
- GIN: (metadata) - 16 kB
- BTREE: (phase_momentum) - 8192 bytes
- BTREE: (start_date) - 8192 bytes
- UNIQUE BTREE: (phase_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Triggers:**
- **trigger_update_transformation_phases_timestamp:** BEFORE UPDATE ROW
  - Calls: update_transformation_phases_timestamp

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### transformative_actions

*Records transformative actions and contributions in the Ubuntu Economic Commons (Fire Element - UBECtt)*

**Rows:** 0 | **Size:** 136 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('transformative_actions_id_seq'::regclass) |
| action_id *(Unique identifier for the transformative action)* | character varying(255) | ✗ |  |
| agent_id *(Stellar account ID of the agent performing the action)* | character varying(56) | ✗ |  |
| action_type *(Type of transformative action performed)* | USER-DEFINED | ✗ |  |
| description *(Detailed description of the transformative action)* | text | ✗ |  |
| impact_scale *(Scale of impact (micro, meso, macro, meta))* | USER-DEFINED | ✗ |  |
| timestamp | timestamp with time zone | ✗ | now() |
| created_at | timestamp with time zone | ✗ | now() |
| updated_at | timestamp with time zone | ✗ | now() |
| direct_beneficiaries *(Number of people directly affected by this action)* | integer(32) | ✓ | 0 |
| indirect_reach *(Estimated ripple effect reach)* | integer(32) | ✓ | 0 |
| regeneration_score *(Regeneration depth score (0.0 - 1.0))* | numeric(5,4) | ✓ | 0.0 |
| catalytic_multiplier *(How much this action amplifies other actions (1.0 - 10.0))* | numeric(5,4) | ✓ | 1.0 |
| verified *(Whether the action has been verified by the community)* | boolean | ✓ | false |
| verifier_ids *(Array of Stellar account IDs who verified this action)* | ARRAY | ✓ | '{}'::text[] |
| evidence_urls *(URLs to evidence supporting this action)* | ARRAY | ✓ | '{}'::text[] |
| verification_count | integer(32) | ✓ |  |
| ubectt_awarded *(Amount of UBECtt tokens awarded for this action)* | numeric(20,7) | ✓ | 0.0 |
| distribution_tx_hash *(Stellar transaction hash of the token distribution)* | character varying(64) | ✓ |  |
| reward_calculated_at | timestamp with time zone | ✓ |  |
| reward_distributed_at | timestamp with time zone | ✓ |  |
| tags *(Tags for categorization and search)* | ARRAY | ✓ | '{}'::text[] |
| related_actions *(IDs of related transformative actions)* | ARRAY | ✓ | '{}'::text[] |
| metadata *(Additional metadata in JSON format)* | jsonb | ✓ | '{}'::jsonb |

**Primary Key:**
- transformative_actions_pkey: (id)

**Foreign Keys:**
- fk_transformative_agent: (agent_id) → ubec_main.stellar_accounts(account_id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- transformative_actions_action_id_key: (action_id)

**Check Constraints:**
- transformative_actions_catalytic_multiplier_check: CHECK (((catalytic_multiplier >= (1)::numeric) AND (catalytic_multiplier <= (10)::numeric)))
- transformative_actions_direct_beneficiaries_check: CHECK ((direct_beneficiaries >= 0))
- transformative_actions_indirect_reach_check: CHECK ((indirect_reach >= 0))
- transformative_actions_regeneration_score_check: CHECK (((regeneration_score >= (0)::numeric) AND (regeneration_score <= (1)::numeric)))
- transformative_actions_ubectt_awarded_check: CHECK ((ubectt_awarded >= (0)::numeric))

**Indexes:**
- BTREE: (agent_id) - 8192 bytes
- BTREE: (agent_id, timestamp) - 8192 bytes
- BTREE: (ubectt_awarded) - 8192 bytes
- BTREE: (catalytic_multiplier) - 8192 bytes
- GIN: (metadata) - 16 kB
- BTREE: (regeneration_score) - 8192 bytes
- BTREE: (impact_scale) - 8192 bytes
- GIN: (tags) - 16 kB
- BTREE: (timestamp) - 8192 bytes
- BTREE: (action_type) - 8192 bytes
- BTREE: (action_type, verified) - 8192 bytes
- BTREE: (verified) - 8192 bytes
- UNIQUE BTREE: (action_id) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Triggers:**
- **trigger_update_transformative_actions_timestamp:** BEFORE UPDATE ROW
  - Calls: update_transformative_actions_timestamp

**Permissions:**
- **ubec_app:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE

---

#### ubec_audit_log

*Audit trail for Fire element transformation validation*

**Rows:** 0 | **Size:** 72 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('ubec_audit_log_id_seq'::regclass) |
| element | USER-DEFINED | ✓ |  |
| token_code | USER-DEFINED | ✓ |  |
| entity_type | character varying(50) | ✗ |  |
| entity_id | character varying(100) | ✗ |  |
| audit_type | character varying(50) | ✗ |  |
| status | character varying(20) | ✗ |  |
| is_valid | boolean | ✓ | true |
| is_anomaly | boolean | ✓ | false |
| anomaly_type | character varying(50) | ✓ |  |
| severity | character varying(20) | ✓ |  |
| audit_details | jsonb | ✓ |  |
| validation_rules | jsonb | ✓ |  |
| violations | jsonb | ✓ |  |
| audited_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| auditor | character varying(100) | ✓ |  |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- ubec_audit_log_pkey: (id)

**Indexes:**
- BTREE: (is_anomaly) - 8192 bytes
- BTREE: (element) - 8192 bytes
- BTREE: (entity_type, entity_id) - 8192 bytes
- BTREE: (status) - 8192 bytes
- BTREE: (audited_at) - 8192 bytes
- BTREE: (token_code) - 8192 bytes
- BTREE: (audit_type) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** SELECT

---

#### ubec_balances

*Token balances for all four elements with distribution tracking*

**Rows:** 654 | **Size:** 560 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('ubec_balances_id_seq'::regclass) |
| account_id | character varying(56) | ✗ |  |
| token_code | USER-DEFINED | ✗ |  |
| element | USER-DEFINED | ✗ |  |
| balance | numeric(20,7) | ✗ | 0 |
| buying_liabilities | numeric(20,7) | ✓ | 0 |
| selling_liabilities | numeric(20,7) | ✓ | 0 |
| limit_amount | numeric(20,7) | ✓ |  |
| is_authorized | boolean | ✓ | false |
| is_authorized_to_maintain_liabilities | boolean | ✓ | false |
| is_clawback_enabled | boolean | ✓ | false |
| distribution_category | USER-DEFINED | ✓ |  |
| last_modified_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| sync_timestamp | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- ubec_balances_pkey: (id)

**Foreign Keys:**
- fk_balance_account: (account_id) → ubec_main.stellar_accounts(account_id)
  - ON UPDATE: NO ACTION, ON DELETE: CASCADE

**Unique Constraints:**
- unique_account_token: (account_id, token_code)

**Check Constraints:**
- positive_balance: CHECK ((balance >= (0)::numeric))

**Indexes:**
- BTREE: (account_id) - 72 kB
- BTREE: (balance) - 72 kB
- BTREE: (distribution_category) - 16 kB
- BTREE: (element) - 16 kB
- BTREE: (last_modified_at) - 80 kB
- BTREE: (token_code) - 16 kB
- PRIMARY UNIQUE BTREE: (id) - 40 kB
- UNIQUE BTREE: (account_id, token_code) - 72 kB

**Triggers:**
- **trg_ubec_balances_modified:** BEFORE UPDATE ROW
  - Calls: update_modified_timestamp

**Row Level Security:** Enabled

- **Policy:** admin_all_policy
  - **Command:** *
  - **Roles:** {, u, b, e, c, _, a, d, m, i, n, }
  - **USING:** `true`
  - **CHECK:** `true`
- **Policy:** app_all_policy
  - **Command:** *
  - **Roles:** {, u, b, e, c, _, a, p, p, }
  - **USING:** `true`
  - **CHECK:** `true`
- **Policy:** readonly_select_policy
  - **Command:** r
  - **Roles:** {, u, b, e, c, _, r, e, a, d, o, n, l, y, }
  - **USING:** `true`
- **Policy:** sync_all_policy
  - **Command:** *
  - **Roles:** {, u, b, e, c, _, s, y, n, c, }
  - **USING:** `true`
  - **CHECK:** `true`

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** INSERT, SELECT, UPDATE

---

#### ubec_distributions

*Distribution tracking for tokenomics compliance (75/20/5)*

**Rows:** 24 | **Size:** 112 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('ubec_distributions_id_seq'::regclass) |
| token_code | USER-DEFINED | ✗ |  |
| element | USER-DEFINED | ✗ |  |
| category | USER-DEFINED | ✗ |  |
| target_percentage | numeric(5,2) | ✗ |  |
| current_percentage | numeric(5,2) | ✗ |  |
| current_amount | numeric(20,7) | ✗ |  |
| total_supply | numeric(20,7) | ✗ |  |
| is_compliant | boolean | ✓ | true |
| deviation | numeric(5,2) | ✓ | 0 |
| snapshot_time | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| last_rebalance | timestamp with time zone | ✓ |  |
| next_check | timestamp with time zone | ✓ |  |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- ubec_distributions_pkey: (id)

**Check Constraints:**
- valid_current_pct: CHECK (((current_percentage >= (0)::numeric) AND (current_percentage <= (100)::numeric)))
- valid_percentages: CHECK (((target_percentage >= (0)::numeric) AND (target_percentage <= (100)::numeric)))

**Indexes:**
- BTREE: (category) - 16 kB
- BTREE: (is_compliant) - 16 kB
- BTREE: (element) - 16 kB
- BTREE: (snapshot_time) - 16 kB
- BTREE: (token_code) - 16 kB
- PRIMARY UNIQUE BTREE: (id) - 16 kB

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** INSERT, SELECT, UPDATE

---

#### ubec_holonic_metrics

*Ubuntu principle metrics for holonic health assessment*

**Rows:** 1,996 | **Size:** 2224 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('ubec_holonic_metrics_id_seq'::regclass) |
| account_id | character varying(56) | ✓ |  |
| element | USER-DEFINED | ✓ |  |
| principle | USER-DEFINED | ✗ |  |
| score | numeric(5,4) | ✗ |  |
| raw_value | numeric(20,7) | ✓ |  |
| normalized_value | numeric(5,4) | ✓ |  |
| health_status | USER-DEFINED | ✓ |  |
| assessment_details | jsonb | ✓ |  |
| calculation_method | character varying(100) | ✓ |  |
| data_points | integer(32) | ✓ |  |
| confidence_level | numeric(5,4) | ✓ |  |
| calculated_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| valid_until | timestamp with time zone | ✓ |  |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- ubec_holonic_metrics_pkey: (id)

**Foreign Keys:**
- fk_holonic_account: (account_id) → ubec_main.stellar_accounts(account_id)
  - ON UPDATE: NO ACTION, ON DELETE: NO ACTION

**Check Constraints:**
- valid_normalized: CHECK (((normalized_value IS NULL) OR ((normalized_value >= (0)::numeric) AND (normalized_value <= (1)::numeric))))
- valid_score: CHECK (((score >= (0)::numeric) AND (score <= (1)::numeric)))

**Indexes:**
- BTREE: (account_id) - 88 kB
- BTREE: (calculated_at) - 160 kB
- BTREE: (element) - 48 kB
- BTREE: (health_status) - 72 kB
- BTREE: (principle) - 48 kB
- BTREE: (score) - 192 kB
- PRIMARY UNIQUE BTREE: (id) - 160 kB

**Row Level Security:** Enabled

- **Policy:** admin_all_policy_metrics
  - **Command:** *
  - **Roles:** {, u, b, e, c, _, a, d, m, i, n, }
  - **USING:** `true`
  - **CHECK:** `true`
- **Policy:** app_all_policy_metrics
  - **Command:** *
  - **Roles:** {, u, b, e, c, _, a, p, p, }
  - **USING:** `true`
  - **CHECK:** `true`
- **Policy:** readonly_select_policy_metrics
  - **Command:** r
  - **Roles:** {, u, b, e, c, _, r, e, a, d, o, n, l, y, }
  - **USING:** `true`
- **Policy:** sync_all_policy_metrics
  - **Command:** r
  - **Roles:** {, u, b, e, c, _, s, y, n, c, }
  - **USING:** `true`

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** SELECT

---

#### ubec_reports

*Generated reports for analysis and compliance*

**Rows:** 0 | **Size:** 56 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('ubec_reports_id_seq'::regclass) |
| element | USER-DEFINED | ✓ |  |
| token_code | USER-DEFINED | ✓ |  |
| report_type | character varying(50) | ✗ |  |
| title | character varying(255) | ✗ |  |
| summary | text | ✓ |  |
| content | jsonb | ✗ |  |
| generated_by | character varying(100) | ✓ |  |
| report_period_start | timestamp with time zone | ✓ |  |
| report_period_end | timestamp with time zone | ✓ |  |
| status | character varying(20) | ✓ | 'draft'::character varying |
| generated_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| published_at | timestamp with time zone | ✓ |  |
| file_path | character varying(500) | ✓ |  |
| file_format | character varying(20) | ✓ |  |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- ubec_reports_pkey: (id)

**Indexes:**
- BTREE: (element) - 8192 bytes
- BTREE: (generated_at) - 8192 bytes
- BTREE: (status) - 8192 bytes
- BTREE: (token_code) - 8192 bytes
- BTREE: (report_type) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** SELECT

---

#### ubec_sync_status

*Synchronization status tracking for all elements*

**Rows:** 0 | **Size:** 64 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer(32) | ✗ | nextval('ubec_sync_status_id_seq'::regclass) |
| element | USER-DEFINED | ✓ |  |
| token_code | USER-DEFINED | ✓ |  |
| sync_type | character varying(50) | ✗ |  |
| status | character varying(20) | ✗ |  |
| cursor | character varying(100) | ✓ |  |
| last_sync_time | timestamp with time zone | ✓ |  |
| next_sync_time | timestamp with time zone | ✓ |  |
| records_synced | integer(32) | ✓ | 0 |
| errors_encountered | integer(32) | ✓ | 0 |
| duration_ms | integer(32) | ✓ |  |
| sync_details | jsonb | ✓ |  |
| error_log | jsonb | ✓ |  |
| created_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| updated_at | timestamp with time zone | ✓ | CURRENT_TIMESTAMP |
| metadata | jsonb | ✓ |  |

**Primary Key:**
- ubec_sync_status_pkey: (id)

**Unique Constraints:**
- unique_sync_context: (element, token_code, sync_type)

**Indexes:**
- BTREE: (element) - 8192 bytes
- BTREE: (status) - 8192 bytes
- BTREE: (token_code) - 8192 bytes
- BTREE: (sync_type) - 8192 bytes
- BTREE: (updated_at) - 8192 bytes
- PRIMARY UNIQUE BTREE: (id) - 8192 bytes
- UNIQUE BTREE: (element, token_code, sync_type) - 8192 bytes

**Triggers:**
- **trg_ubec_sync_updated:** BEFORE UPDATE ROW
  - Calls: update_updated_timestamp

**Permissions:**
- **PUBLIC:** SELECT
- **recipro:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_admin:** DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
- **reward_data_writer:** INSERT, SELECT, UPDATE
- **reward_read_only:** SELECT
- **ubec_admin:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_app:** DELETE (GRANT), INSERT (GRANT), REFERENCES (GRANT), SELECT (GRANT), TRIGGER (GRANT), TRUNCATE (GRANT), UPDATE (GRANT)
- **ubec_readonly:** SELECT
- **ubec_sync:** INSERT, SELECT, UPDATE

---

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

#### gen_salt(text, integer)

- **Returns:** text
- **Language:** c

#### gen_salt(text)

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

#### pgp_pub_decrypt(bytea, bytea)

- **Returns:** text
- **Language:** c

#### pgp_pub_decrypt(bytea, bytea, text)

- **Returns:** text
- **Language:** c

#### pgp_pub_decrypt(bytea, bytea, text, text)

- **Returns:** text
- **Language:** c

#### pgp_pub_decrypt_bytea(bytea, bytea, text, text)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_decrypt_bytea(bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_decrypt_bytea(bytea, bytea)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_encrypt(text, bytea, text)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_encrypt(text, bytea)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_encrypt_bytea(bytea, bytea, text)

- **Returns:** bytea
- **Language:** c

#### pgp_pub_encrypt_bytea(bytea, bytea)

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

#### pgp_sym_encrypt_bytea(bytea, text)

- **Returns:** bytea
- **Language:** c

#### pgp_sym_encrypt_bytea(bytea, text, text)

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

