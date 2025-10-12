# UBEC Protocol Suite - Database Schema Documentation

## 🜁 🜄 🜃 🜂 Four-Element Protocol

**Schema:** `ubec_main`  
**Database:** `ubec`  
**Generated:** 2025-10-12T01:52:49.645554  
**PostgreSQL Version:** PostgreSQL 15.13 (Debian 15.13-0+deb12u1) on x86_64-pc-linux-gnu  
**Protocol Version:** Four-Element Protocol v1.0  

## The Four Elements

### 🜁 Air - UBEC

- **Ubuntu Principle:** Diversity
- **Role:** Gateway & Universal Access
- **Tables:** `ubec_audit_log`, `ubec_balances`, `ubec_distributions`, `ubec_holonic_metrics`, `ubec_reports`, `ubec_sync_status`

### 🜄 Water - UBECrc

- **Ubuntu Principle:** Reciprocity
- **Role:** Flow & Exchange
- **Tables:** `flow_transactions`

### 🜃 Earth - UBECgpi

- **Ubuntu Principle:** Mutualism
- **Role:** Stability & Value
- **Tables:** `distribution_history`, `distribution_state`

### 🜂 Fire - UBECtt

- **Ubuntu Principle:** Regeneration
- **Role:** Transformation & Action
- **Tables:** `system_settings`, `transformation_phases`

### Core Infrastructure Tables

Shared tables used across all elements:

- `account_balances`
- `holonic_metrics`
- `stellar_accounts`
- `stellar_effects`
- `stellar_operations`
- `stellar_transactions`

## Custom Types

### distribution_category

Token distribution categories: 75% general, 20% stewardship, 5% administration

**Values:** `general_circulation`, `stewardship`, `administration`

### element_type

Four elements: air=UBEC (Gateway), water=UBECrc (Flow), earth=UBECgpi (Stability), fire=UBECtt (Transformation)

**Values:** `air`, `water`, `earth`, `fire`

### health_status

System health indicators

**Values:** `excellent`, `good`, `fair`, `poor`, `critical`

### impact_scale

Custom type

**Values:** `micro`, `meso`, `macro`, `meta`

### token_code

Four UBEC protocol tokens

**Values:** `UBEC`, `UBECrc`, `UBECgpi`, `UBECtt`

### transaction_type

Stellar transaction operation types

**Values:** `payment`, `create_account`, `change_trust`, `manage_offer`, `path_payment`, `account_merge`, `manage_data`, `bump_sequence`, `clawback`, `other`, `manage_buy_offer`, `manage_sell_offer`, `create_passive_sell_offer`

### transformation_type

Custom type

**Values:** `individual_growth`, `community_building`, `resource_regeneration`, `knowledge_creation`, `system_evolution`, `cultural_shift`, `economic_transition`, `social_healing`

### ubuntu_principle

Five Ubuntu principles: diversity, reciprocity, mutualism, regeneration, holism

**Values:** `diversity`, `reciprocity`, `mutualism`, `regeneration`, `holism`

## Database Summary

- **Total Tables:** 40
- **Total Columns:** 474
- **Total Relationships:** 6
- **Total Indexes:** 249
- **Total Views:** 13
- **Total Functions:** 72
- **Total Custom Types:** 8
- **Database Size:** 47 MB

### Tables by Element

- 🜁 **Air:** 6 tables
- 🜄 **Water:** 1 tables
- 🜃 **Earth:** 2 tables
- 🜂 **Fire:** 2 tables
- 📊 **Core:** 6 tables

### Largest Tables

| Table | Rows | Size |
|-------|------|------|
| stellar_transactions | 51,289 | 34 MB |
| stellar_accounts | 1,246 | 592 kB |
| ubec_balances | 651 | 552 kB |
| asset_holder_analysis | 63 | 184 kB |
| system_settings | 37 | 80 kB |
| ubec_distributions | 24 | 112 kB |
| distribution_state | 12 | 104 kB |
| holonic_metrics | 10 | 152 kB |
| system_configuration | 5 | 96 kB |
| account_balances | 0 | 56 kB |

---

## Detailed Table Documentation

### Core Infrastructure Tables

#### account_balances

*Tracks token balances for all accounts across all UBEC tokens. Used for stability analysis in Earth element (UBECgpi).*

**Statistics:** 0 rows | Table: 0 bytes | Indexes: 56 kB | Total: 56 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.account_balances_i... | - |
| account_id | varchar(56) | ✗ | - | Stellar public key (G... format) |
| asset_code | varchar(12) | ✗ | - | Token code: UBEC, UBECrc, UBECgpi, or UBECtt |
| balance | numeric(20,7) | ✓ | 0.0 | Current token balance for this account |
| last_updated | timestamp with time zone | ✓ | now() | Timestamp of last balance update |
| created_at | timestamp with time zone | ✓ | now() | - |

**Constraints:**

- `account_balances_balance_check` (CHECK)
- `account_balances_pkey` (PRIMARY KEY)
- `account_balances_unique_account_asset` (UNIQUE)

**Indexes:**

- `account_balances_pkey` (PRIMARY, UNIQUE)
- `account_balances_unique_account_asset` (UNIQUE)
- `idx_account_balances_account_id`
- `idx_account_balances_asset_balance`
- `idx_account_balances_asset_code`
- `idx_account_balances_balance`
- `idx_account_balances_last_updated`

#### holonic_metrics

*Stores holonic evaluation metrics for UBEC token holders*

**Statistics:** 10 rows | Table: 56 kB | Indexes: 96 kB | Total: 152 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.holonic_metrics_id... | - |
| evaluation_date | timestamp with time zone | ✗ | now() | Date and time when the evaluation was performed |
| autonomy_integration_score | numeric(5,4) | ✗ | 0 | Score for balance of autonomy and integration (... |
| multi_scale_score | numeric(5,4) | ✗ | 0 | Score for multi-scale participation (0-1) |
| regenerative_impact_score | numeric(5,4) | ✗ | 0 | Score for regenerative impact (0-1) |
| network_contribution_score | numeric(5,4) | ✗ | 0 | Score for network contribution (0-1) |
| ubuntu_alignment_score | numeric(5,4) | ✗ | 0 | Score for Ubuntu philosophy alignment (0-1) |
| composite_score | numeric(5,4) | ✗ | 0 | Overall holonic score (0-1) |
| holonic_category | varchar(50) | ✗ | 'Observer'::character varying | Category: Observer, Participant, Contributor, I... |
| raw_metrics | jsonb | ✓ | - | JSON object containing detailed metrics for eac... |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |
| evaluation_date_date | date | ✗ | - | - |
| account_id | varchar(56) | ✗ | - | - |

**Constraints:**

- `holonic_metrics_pkey` (PRIMARY KEY)
- `valid_autonomy_score` (CHECK)
- `valid_composite_score` (CHECK)
- `valid_holonic_category` (CHECK)
- `valid_multi_scale_score` (CHECK)
- `valid_network_score` (CHECK)
- `valid_regenerative_score` (CHECK)
- `valid_ubuntu_score` (CHECK)

**Indexes:**

- `holonic_metrics_pkey` (PRIMARY, UNIQUE)
- `idx_holonic_metrics_account_date_unique` (UNIQUE)
- `idx_holonic_metrics_account_id`
- `idx_holonic_metrics_category`
- `idx_holonic_metrics_composite_score`
- `idx_holonic_metrics_evaluation_date`

#### stellar_accounts

*Stellar blockchain accounts with element tracking*

**Statistics:** 1,246 rows | Table: 208 kB | Indexes: 384 kB | Total: 592 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.stellar_accounts_i... | - |
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

**Indexes:**

- `idx_stellar_accounts_account_id`
- `idx_stellar_accounts_activity`
- `idx_stellar_accounts_created`
- `idx_stellar_accounts_element`
- `stellar_accounts_account_id_key` (UNIQUE)
- `stellar_accounts_pkey` (PRIMARY, UNIQUE)

#### stellar_effects

*Stellar blockchain effects with element context*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 72 kB | Total: 80 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.stellar_effects_id... | - |
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

**Indexes:**

- `idx_stellar_effects_account`
- `idx_stellar_effects_asset`
- `idx_stellar_effects_created`
- `idx_stellar_effects_element`
- `idx_stellar_effects_id`
- `idx_stellar_effects_operation`
- `idx_stellar_effects_type`
- `stellar_effects_effect_id_key` (UNIQUE)
- `stellar_effects_pkey` (PRIMARY, UNIQUE)

#### stellar_operations

*Stellar blockchain operations with element and asset tracking*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 144 kB | Total: 152 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.stellar_operations... | - |
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

**Indexes:**

- `idx_stellar_operations_asset`
- `idx_stellar_operations_created`
- `idx_stellar_operations_element`
- `idx_stellar_operations_from`
- `idx_stellar_operations_id`
- `idx_stellar_operations_to`
- `idx_stellar_operations_tx`
- `idx_stellar_operations_type`
- `idx_stellar_ops_accounts_asset`
- `idx_stellar_ops_asset`
- `idx_stellar_ops_created`
- `idx_stellar_ops_from`
- `idx_stellar_ops_from_asset`
- `idx_stellar_ops_source`
- `idx_stellar_ops_to`
- `idx_stellar_ops_to_asset`
- `stellar_operations_operation_id_key` (UNIQUE)
- `stellar_operations_pkey` (PRIMARY, UNIQUE)

#### stellar_transactions

*Stellar blockchain transactions with element context*

**Statistics:** 51,289 rows | Table: 17 MB | Indexes: 17 MB | Total: 34 MB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.stellar_transactio... | - |
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
| ledger | bigint | ✓ | - | Ledger sequence number where this transaction w... |

**Constraints:**

- `fk_source_account` (FOREIGN KEY)
- `stellar_transactions_pkey` (PRIMARY KEY)
- `stellar_transactions_transaction_hash_key` (UNIQUE)

**Indexes:**

- `idx_stellar_transactions_created`
- `idx_stellar_transactions_element`
- `idx_stellar_transactions_hash`
- `idx_stellar_transactions_ledger`
- `idx_stellar_transactions_source`
- `idx_stellar_transactions_tokens`
- `stellar_transactions_pkey` (PRIMARY, UNIQUE)
- `stellar_transactions_transaction_hash_key` (UNIQUE)

---

### 🜁 Air Element (UBEC)

#### ubec_audit_log

*Audit trail for Fire element transformation validation*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 64 kB | Total: 72 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.ubec_audit_log_id_... | - |
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

**Indexes:**

- `idx_ubec_audit_anomaly`
- `idx_ubec_audit_element`
- `idx_ubec_audit_entity`
- `idx_ubec_audit_status`
- `idx_ubec_audit_time`
- `idx_ubec_audit_token`
- `idx_ubec_audit_type`
- `ubec_audit_log_pkey` (PRIMARY, UNIQUE)

#### ubec_balances

*Token balances for all four elements with distribution tracking*

**Statistics:** 651 rows | Table: 152 kB | Indexes: 400 kB | Total: 552 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.ubec_balances_id_s... | - |
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

**Indexes:**

- `idx_ubec_balances_account`
- `idx_ubec_balances_balance`
- `idx_ubec_balances_category`
- `idx_ubec_balances_element`
- `idx_ubec_balances_modified`
- `idx_ubec_balances_token`
- `ubec_balances_pkey` (PRIMARY, UNIQUE)
- `unique_account_token` (UNIQUE)

#### ubec_distributions

*Distribution tracking for tokenomics compliance (75/20/5)*

**Statistics:** 24 rows | Table: 16 kB | Indexes: 96 kB | Total: 112 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.ubec_distributions... | - |
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

**Indexes:**

- `idx_ubec_distributions_category`
- `idx_ubec_distributions_compliance`
- `idx_ubec_distributions_element`
- `idx_ubec_distributions_snapshot`
- `idx_ubec_distributions_token`
- `ubec_distributions_pkey` (PRIMARY, UNIQUE)

#### ubec_holonic_metrics

*Ubuntu principle metrics for holonic health assessment*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 56 kB | Total: 64 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.ubec_holonic_metri... | - |
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

**Indexes:**

- `idx_ubec_holonic_account`
- `idx_ubec_holonic_calculated`
- `idx_ubec_holonic_element`
- `idx_ubec_holonic_health`
- `idx_ubec_holonic_principle`
- `idx_ubec_holonic_score`
- `ubec_holonic_metrics_pkey` (PRIMARY, UNIQUE)

#### ubec_reports

*Generated reports for analysis and compliance*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 48 kB | Total: 56 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.ubec_reports_id_se... | - |
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

**Indexes:**

- `idx_ubec_reports_element`
- `idx_ubec_reports_generated`
- `idx_ubec_reports_status`
- `idx_ubec_reports_token`
- `idx_ubec_reports_type`
- `ubec_reports_pkey` (PRIMARY, UNIQUE)

#### ubec_sync_status

*Synchronization status tracking for all elements*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 56 kB | Total: 64 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.ubec_sync_status_i... | - |
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

**Indexes:**

- `idx_ubec_sync_element`
- `idx_ubec_sync_status`
- `idx_ubec_sync_token`
- `idx_ubec_sync_type`
- `idx_ubec_sync_updated`
- `ubec_sync_status_pkey` (PRIMARY, UNIQUE)
- `unique_sync_context` (UNIQUE)

---

### 🜄 Water Element (UBECrc)

#### flow_transactions

*Flow transactions tracking for Water element (UBECrc). Records all token flows.*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 48 kB | Total: 56 kB

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

**Indexes:**

- `flow_transactions_pkey` (PRIMARY, UNIQUE)
- `idx_flow_transactions_asset_code`
- `idx_flow_transactions_asset_time`
- `idx_flow_transactions_created_at`
- `idx_flow_transactions_from_account`
- `idx_flow_transactions_to_account`

---

### 🜃 Earth Element (UBECgpi)

#### distribution_history

*Historical record of distribution checks and rebalancing actions*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 72 kB | Total: 80 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.distribution_histo... | - |
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

**Indexes:**

- `distribution_history_pkey` (PRIMARY, UNIQUE)
- `idx_dist_hist_asset`
- `idx_dist_hist_date`
- `idx_dist_hist_details`
- `idx_dist_hist_rebalance`
- `idx_distribution_history_asset`
- `idx_distribution_history_date`
- `idx_distribution_history_rebalance`

#### distribution_state

*Distribution state tracking for Earth element (UBECgpi). Monitors tokenomics compliance (75/20/5).*

**Statistics:** 12 rows | Table: 8192 bytes | Indexes: 96 kB | Total: 104 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.distribution_state... | - |
| asset_code | varchar(12) | ✗ | - | Token code being tracked |
| category | varchar(50) | ✗ | - | Distribution category: general_circulation, ste... |
| current_amount | numeric(20,7) | ✓ | 0.0 | - |
| target_amount | numeric(20,7) | ✓ | 0.0 | - |
| target_percentage | numeric(5,2) | ✗ | - | Target percentage for this category (75%, 20%, ... |
| actual_percentage | numeric(5,2) | ✓ | 0.0 | Current actual percentage |
| is_compliant | boolean | ✓ | true | Whether current distribution is within complian... |
| last_updated | timestamp with time zone | ✓ | now() | - |

**Constraints:**

- `distribution_state_amounts_check` (CHECK)
- `distribution_state_percentages_check` (CHECK)
- `distribution_state_pkey` (PRIMARY KEY)
- `distribution_state_unique_asset_category` (UNIQUE)

**Indexes:**

- `distribution_state_pkey` (PRIMARY, UNIQUE)
- `distribution_state_unique_asset_category` (UNIQUE)
- `idx_distribution_state_asset_code`
- `idx_distribution_state_category`
- `idx_distribution_state_compliance`
- `idx_distribution_state_last_updated`

---

### 🜂 Fire Element (UBECtt)

#### system_settings

*System configuration settings - single source of truth for all system parameters*

**Statistics:** 37 rows | Table: 16 kB | Indexes: 64 kB | Total: 80 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| setting_id | integer | ✗ | nextval('ubec_main.system_settings_se... | - |
| setting_key | varchar(100) | ✗ | - | Unique setting identifier |
| setting_value | text | ✗ | - | Setting value (stored as text, converted based ... |
| setting_type | varchar(20) | ✓ | 'string'::character varying | Data type of the setting (string, integer, floa... |
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

**Indexes:**

- `idx_system_settings_category`
- `idx_system_settings_key`
- `system_settings_pkey` (PRIMARY, UNIQUE)
- `system_settings_setting_key_key` (UNIQUE)

#### transformation_phases

*Tracks transformation phases and their momentum in the Ubuntu Economic Commons (Fire Element - UBECtt)*

**Statistics:** 0 rows | Table: 8192 bytes | Indexes: 88 kB | Total: 96 kB

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | ✗ | nextval('ubec_main.transformation_pha... | - |
| phase_id | varchar(255) | ✗ | - | Unique identifier for the transformation phase |
| name | varchar(255) | ✗ | - | Name of the transformation phase |
| description | text | ✗ | - | Detailed description of the phase |
| start_date | timestamp with time zone | ✗ | - | When the transformation phase began |
| end_date | timestamp with time zone | ✓ | - | When the transformation phase ended (NULL if on... |
| created_at | timestamp with time zone | ✗ | now() | - |
| updated_at | timestamp with time zone | ✗ | now() | - |
| target_outcomes | ARRAY | ✓ | '{}'::text[] | Array of target outcomes for this phase |
| key_indicators | jsonb | ✓ | '{}'::jsonb | Key performance indicators tracked during this ... |
| participating_agents | ARRAY | ✓ | '{}'::text[] | Array of Stellar account IDs participating in t... |
| actions_completed | integer | ✓ | 0 | Number of transformative actions completed in t... |
| total_ubectt_distributed | numeric(20,7) | ✓ | 0.0 | Total UBECtt tokens distributed during this phase |
| phase_momentum | numeric(5,4) | ✓ | 0.0 | Rate of transformation in this phase (0.0 - 1.0) |
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

**Indexes:**

- `idx_transformation_phases_active`
- `idx_transformation_phases_agents`
- `idx_transformation_phases_completion`
- `idx_transformation_phases_end`
- `idx_transformation_phases_metadata`
- `idx_transformation_phases_momentum`
- `idx_transformation_phases_start`
- `transformation_phases_phase_id_key` (UNIQUE)
- `transformation_phases_pkey` (PRIMARY, UNIQUE)

---

## Views

### active_verified_actions

```sql
