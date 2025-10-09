# Database Schema Documentation: ubec_holon_etf

Generated on: 2025-10-08T07:37:07.469036

## Table of Contents

1. [Overview](#overview)
2. [Tables](#tables)
   - [asset_metrics](#asset-metrics)
   - [asset_metrics_history](#asset-metrics-history)
   - [assets](#assets)
   - [etf_config](#etf-config)
   - [holons](#holons)
   - [issuer_trust](#issuer-trust)
   - [liquidity_metrics](#liquidity-metrics)
   - [monitoring_alerts](#monitoring-alerts)
   - [monitoring_metrics](#monitoring-metrics)
   - [monitoring_process_runs](#monitoring-process-runs)
   - [portfolio_holdings](#portfolio-holdings)
   - [portfolio_snapshots](#portfolio-snapshots)
   - [rc_distributions](#rc-distributions)
   - [remaining_count](#remaining-count)
   - [unified_reciprocity_events](#unified-reciprocity-events)
3. [Relationships](#relationships)
4. [Indexes](#indexes)
5. [Triggers](#triggers)
6. [Functions](#functions)
7. [Summary Statistics](#summary-statistics)

## Overview

This documentation provides a complete picture of the `ubec_holon_etf` database schema. It serves as the single source of truth for understanding the data structure, relationships, and business logic implemented in the database.

- **Database Size**: 74 MB
- **PostgreSQL Version**: PostgreSQL 15.13 (Debian 15.13-0+deb12u1) on x86_64-pc-linux-gnu
- **Total Tables**: 15
- **Total Relationships**: 10

## Tables

### asset_metrics

Real-time metrics and Graham valuation data for assets including liquidity scores

**Statistics**: 0 rows, 104 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('asset_metrics_id_seq'::regclass) | - |
| asset_id | integer | Yes | - | - |
| price | numeric(20,10) | No | - | - |
| market_cap | numeric(20,2) | Yes | - | - |
| supply | numeric(20,2) | Yes | - | - |
| daily_volume | numeric(20,2) | Yes | - | - |
| volume_7d | numeric(20,2) | Yes | - | - |
| change_24h | numeric(10,4) | Yes | - | - |
| epts | numeric(20,10) | Yes | - | - |
| growth_rate | numeric(10,4) | Yes | - | - |
| nvt_ratio | numeric(10,2) | Yes | - | - |
| estimated_yield | numeric(10,4) | Yes | - | - |
| yield_stability | numeric(5,4) | Yes | - | - |
| graham_value | numeric(20,10) | Yes | - | - |
| rgv | numeric(10,4) | Yes | - | - |
| adjusted_rgv | numeric(10,4) | Yes | - | - |
| active_accounts | integer | Yes | 0 | - |
| transaction_count_30d | integer | Yes | 0 | - |
| nvt_score | numeric(10,4) | Yes | - | - |
| bid_ask_spread | numeric(10,6) | Yes | 0.0 | Bid-ask spread as a percentage (0-100) |
| meaningful_volume_24h | numeric(20,8) | Yes | 0 | Trading volume from validated meaningful trades only (excludes wash trades, dust trades, etc.) |
| trade_validity_ratio | numeric(5,4) | Yes | 0 | Ratio of meaningful trades to total trades (0-1, where 1 = all trades are meaningful) |
| meaningful_trade_count | integer | Yes | 0 | Number of trades that passed validation checks |
| liquidity_score | numeric(10,4) | Yes | 0 | Composite liquidity score (0-100) based on volume, spread, depth, and trade quality |
| orderbook_quality | numeric(5,4) | Yes | 0 | Quality score of order book data (0-1) based on depth and spread |
| trade_quality_score | numeric(5,4) | Yes | - | Composite score of trade quality based on validity, volume, and spread |
| data_source | varchar(50) | Yes | 'stellar_expert'::character varying | - |
| exchange_id | varchar(100) | Yes | - | - |
| data_sources | jsonb | Yes | '{}'::jsonb | - |
| data_quality_score | numeric(3,2) | Yes | 0.5 | - |
| last_source_update | timestamp without time zone | Yes | CURRENT_TIMESTAMP | - |
| data_conflicts | jsonb | Yes | '[]'::jsonb | - |
| orderbook_depth | numeric(20,7) | Yes | 0 | - |
| last_trade_time | timestamp without time zone | Yes | - | - |
| spread_quality | numeric(3,2) | Yes | 0.5 | - |
| price_confidence | numeric(3,2) | Yes | 0.5 | - |
| volatility_7d | numeric(10,6) | Yes | 0 | - |
| trades_24h | integer | Yes | 0 | - |
| payments_24h | integer | Yes | 0 | - |
| trustlines | integer | Yes | 0 | - |
| payments_count | integer | Yes | 0 | - |
| trades_count | integer | Yes | 0 | - |
| rating | jsonb | Yes | '{}'::jsonb | - |
| data_timestamp | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |
| created_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **asset_metrics_asset_id_fkey** (FOREIGN KEY): FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
- **asset_metrics_liquidity_score_check** (CHECK): CHECK (((liquidity_score >= (0)::numeric) AND (liquidity_score <= (100)::numeric)))
- **asset_metrics_orderbook_quality_check** (CHECK): CHECK (((orderbook_quality >= (0)::numeric) AND (orderbook_quality <= (1)::numeric)))
- **asset_metrics_pkey** (PRIMARY KEY): PRIMARY KEY (id)
- **asset_metrics_price_check** (CHECK): CHECK ((price >= (0)::numeric))
- **asset_metrics_trade_validity_ratio_check** (CHECK): CHECK (((trade_validity_ratio >= (0)::numeric) AND (trade_validity_ratio <= (1)::numeric)))
- **chk_bid_ask_spread_percentage** (CHECK): CHECK (((bid_ask_spread >= (0)::numeric) AND (bid_ask_spread <= (100)::numeric)))
- **unique_asset_metrics** (UNIQUE): UNIQUE (asset_id, data_timestamp)

**Indexes**:

- **asset_metrics_pkey**: id (UNIQUE) (PRIMARY KEY)
- **idx_asset_metrics_bid_ask_spread**: bid_ask_spread
- **idx_asset_metrics_dedup**: asset_id, data_timestamp, liquidity_score
- **idx_asset_metrics_latest**: asset_id, data_timestamp
- **idx_asset_metrics_liquidity_score**: liquidity_score
- **idx_asset_metrics_meaningful_volume**: meaningful_volume_24h
- **idx_asset_metrics_trade_quality**: trade_quality_score
- **idx_asset_metrics_trade_validity**: trade_validity_ratio
- **idx_metrics_asset**: asset_id
- **idx_metrics_rgv**: adjusted_rgv
- **idx_metrics_timestamp**: data_timestamp
- **unique_asset_metrics**: asset_id, data_timestamp (UNIQUE)

**Triggers**:

- **trg_update_trade_quality_score**: BEFORE INSERT (ROW) - Executes EXECUTE FUNCTION update_trade_quality_score()
- **trg_update_trade_quality_score**: BEFORE UPDATE (ROW) - Executes EXECUTE FUNCTION update_trade_quality_score()

---

### asset_metrics_history

**Statistics**: 0 rows, 24 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('asset_metrics_history_id_seq'::regclass) | - |
| asset_id | integer | Yes | - | - |
| metric_date | date | No | - | - |
| price | numeric(20,10) | Yes | - | - |
| market_cap | numeric(20,2) | Yes | - | - |
| supply | numeric(20,2) | Yes | - | - |
| daily_volume | numeric(20,2) | Yes | - | - |
| volume_7d | numeric(20,2) | Yes | - | - |
| change_24h | numeric(10,4) | Yes | - | - |
| epts | numeric(20,10) | Yes | - | - |
| growth_rate | numeric(10,4) | Yes | - | - |
| nvt_ratio | numeric(10,2) | Yes | - | - |
| estimated_yield | numeric(10,4) | Yes | - | - |
| yield_stability | numeric(5,4) | Yes | - | - |
| graham_value | numeric(20,10) | Yes | - | - |
| rgv | numeric(10,4) | Yes | - | - |
| adjusted_rgv | numeric(10,4) | Yes | - | - |
| active_accounts | integer | Yes | - | - |
| transaction_count_30d | integer | Yes | - | - |
| nvt_score | numeric(10,4) | Yes | - | - |
| created_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **asset_metrics_history_asset_id_fkey** (FOREIGN KEY): FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
- **asset_metrics_history_pkey** (PRIMARY KEY): PRIMARY KEY (id)
- **unique_asset_history** (UNIQUE): UNIQUE (asset_id, metric_date)

**Indexes**:

- **asset_metrics_history_pkey**: id (UNIQUE) (PRIMARY KEY)
- **idx_history_asset_date**: asset_id, metric_date
- **unique_asset_history**: asset_id, metric_date (UNIQUE)

---

### assets

Stellar assets eligible for ETF inclusion with Graham valuation metrics and comprehensive ratings

**Statistics**: 1 rows, 160 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('assets_id_seq'::regclass) | - |
| asset_code | varchar(12) | No | - | - |
| issuer | varchar(56) | Yes | - | - |
| asset_id | varchar(100) (generated) | Yes | - | - |
| holon_id | integer | Yes | - | - |
| asset_type | varchar(50) | No | - | - |
| is_native | boolean | Yes | false | - |
| rating_average | numeric(3,1) | Yes | 0.0 | - |
| rating_age | integer | Yes | 0 | - |
| rating_trades | integer | Yes | 0 | - |
| rating_payments | integer | Yes | 0 | - |
| rating_trustlines | integer | Yes | 0 | - |
| rating_volume7d | integer | Yes | 0 | - |
| rating_interop | integer | Yes | 0 | - |
| rating_liquidity | integer | Yes | 0 | - |
| is_strategic | boolean | Yes | false | - |
| strategic_holon | varchar(50) | Yes | - | - |
| trust_level | varchar(20) | Yes | 'low'::character varying | - |
| toml_info | jsonb | Yes | - | - |
| created_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |
| updated_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **assets_asset_id_key** (UNIQUE): UNIQUE (asset_id)
- **assets_holon_id_fkey** (FOREIGN KEY): FOREIGN KEY (holon_id) REFERENCES holons(id)
- **assets_pkey** (PRIMARY KEY): PRIMARY KEY (id)
- **assets_rating_average_check** (CHECK): CHECK (((rating_average >= (0)::numeric) AND (rating_average <= (10)::numeric)))
- **unique_asset_issuer** (UNIQUE): UNIQUE (asset_code, issuer)

**Indexes**:

- **assets_asset_id_key**: asset_id (UNIQUE)
- **assets_pkey**: id (UNIQUE) (PRIMARY KEY)
- **idx_assets_asset_id**: asset_id
- **idx_assets_code**: asset_code
- **idx_assets_holon**: holon_id
- **idx_assets_rating**: rating_average
- **idx_assets_strategic**: is_strategic
- **idx_assets_type**: asset_type
- **unique_asset_issuer**: asset_code, issuer (UNIQUE)

---

### etf_config

Configuration parameters for the ETF system

**Statistics**: 12 rows, 48 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('etf_config_id_seq'::regclass) | - |
| parameter_name | varchar(100) | No | - | - |
| parameter_value | jsonb | No | - | - |
| category | varchar(50) | No | - | - |
| description | text | Yes | - | - |
| created_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |
| updated_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **etf_config_parameter_name_key** (UNIQUE): UNIQUE (parameter_name)
- **etf_config_pkey** (PRIMARY KEY): PRIMARY KEY (id)

**Indexes**:

- **etf_config_parameter_name_key**: parameter_name (UNIQUE)
- **etf_config_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### holons

Semi-autonomous groups for organizing assets by risk and type

**Statistics**: 5 rows, 48 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('holons_id_seq'::regclass) | - |
| holon_name | varchar(100) | No | - | - |
| holon_type | varchar(50) | No | - | - |
| target_weight | numeric(5,4) | No | - | - |
| min_weight | numeric(5,4) | No | - | - |
| max_weight | numeric(5,4) | No | - | - |
| rebalance_threshold | numeric(5,4) | Yes | 0.05 | - |
| description | text | Yes | - | - |
| is_active | boolean | Yes | true | - |
| created_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |
| updated_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **holons_holon_name_key** (UNIQUE): UNIQUE (holon_name)
- **holons_max_weight_check** (CHECK): CHECK (((max_weight >= (0)::numeric) AND (max_weight <= (1)::numeric)))
- **holons_min_weight_check** (CHECK): CHECK (((min_weight >= (0)::numeric) AND (min_weight <= (1)::numeric)))
- **holons_pkey** (PRIMARY KEY): PRIMARY KEY (id)
- **holons_target_weight_check** (CHECK): CHECK (((target_weight >= (0)::numeric) AND (target_weight <= (1)::numeric)))
- **weight_constraints** (CHECK): CHECK (((min_weight <= target_weight) AND (target_weight <= max_weight)))

**Indexes**:

- **holons_holon_name_key**: holon_name (UNIQUE)
- **holons_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### issuer_trust

Trust levels for asset issuers to handle duplicate assets

**Statistics**: 0 rows, 16 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| issuer_id | varchar(56) | No | - | - |
| asset_codes | ARRAY | Yes | - | - |
| trust_level | varchar(20) | Yes | - | - |
| organization_name | varchar(200) | Yes | - | - |
| domain | varchar(200) | Yes | - | - |
| notes | text | Yes | - | - |
| verified_date | timestamp without time zone | Yes | - | - |
| created_at | timestamp without time zone | Yes | CURRENT_TIMESTAMP | - |
| updated_at | timestamp without time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **issuer_trust_pkey** (PRIMARY KEY): PRIMARY KEY (issuer_id)
- **issuer_trust_trust_level_check** (CHECK): CHECK (((trust_level)::text = ANY ((ARRAY['HIGH'::character varying, 'MEDIUM'::character varying, 'LOW'::character varying, 'BLACKLISTED'::character varying])::text[])))

**Indexes**:

- **issuer_trust_pkey**: issuer_id (UNIQUE) (PRIMARY KEY)

**Triggers**:

- **update_issuer_trust_updated_at**: BEFORE UPDATE (ROW) - Executes EXECUTE FUNCTION update_issuer_trust_timestamp()

---

### liquidity_metrics

Enhanced liquidity analysis data for assets

**Statistics**: 0 rows, 32 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('liquidity_metrics_id_seq'::regclass) | - |
| asset_id | integer | Yes | - | - |
| bid_ask_spread | numeric | Yes | - | - |
| depth_2_percent | numeric | Yes | - | - |
| depth_10_percent | numeric | Yes | - | - |
| slippage_1m | numeric | Yes | - | - |
| pool_tvl | numeric | Yes | - | - |
| liquidity_score | numeric | Yes | - | - |
| data_timestamp | timestamp without time zone | Yes | CURRENT_TIMESTAMP | - |
| created_at | timestamp without time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **liquidity_metrics_asset_id_fkey** (FOREIGN KEY): FOREIGN KEY (asset_id) REFERENCES assets(id)
- **liquidity_metrics_pkey** (PRIMARY KEY): PRIMARY KEY (id)

**Indexes**:

- **idx_liquidity_metrics_asset**: asset_id
- **idx_liquidity_metrics_timestamp**: data_timestamp
- **liquidity_metrics_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### monitoring_alerts

Alert log for system monitoring and notifications

**Statistics**: 0 rows, 40 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | No | nextval('monitoring_alerts_id_seq'::regclass) | - |
| timestamp | timestamp with time zone | No | CURRENT_TIMESTAMP | - |
| severity | varchar(20) | No | - | - |
| title | varchar(500) | No | - | - |
| message | text | No | - | - |
| metric_name | varchar(255) | Yes | - | - |
| current_value | numeric | Yes | - | - |
| threshold | numeric | Yes | - | - |
| tags | jsonb | Yes | '{}'::jsonb | - |
| acknowledged | boolean | Yes | false | - |
| acknowledged_by | varchar(100) | Yes | - | - |
| acknowledged_at | timestamp with time zone | Yes | - | - |
| resolution_notes | text | Yes | - | - |
| asset_id | integer | Yes | - | - |
| holon_id | integer | Yes | - | - |

**Constraints**:

- **monitoring_alerts_asset_id_fkey** (FOREIGN KEY): FOREIGN KEY (asset_id) REFERENCES assets(id)
- **monitoring_alerts_holon_id_fkey** (FOREIGN KEY): FOREIGN KEY (holon_id) REFERENCES holons(id)
- **monitoring_alerts_pkey** (PRIMARY KEY): PRIMARY KEY (id)
- **monitoring_alerts_severity_check** (CHECK): CHECK (((severity)::text = ANY ((ARRAY['info'::character varying, 'warning'::character varying, 'error'::character varying, 'critical'::character varying])::text[])))

**Indexes**:

- **idx_alerts_acknowledged**: acknowledged
- **idx_alerts_severity**: severity
- **idx_alerts_timestamp**: timestamp
- **monitoring_alerts_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### monitoring_metrics

Time-series metrics for system monitoring

**Statistics**: 0 rows, 64 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | No | nextval('monitoring_metrics_id_seq'::regclass) | - |
| timestamp | timestamp with time zone | No | CURRENT_TIMESTAMP | - |
| name | varchar(255) | No | - | - |
| value | numeric | No | - | - |
| type | varchar(20) | No | - | - |
| tags | jsonb | Yes | '{}'::jsonb | - |
| metadata | jsonb | Yes | '{}'::jsonb | - |
| asset_id | integer | Yes | - | - |
| holon_id | integer | Yes | - | - |

**Constraints**:

- **monitoring_metrics_asset_id_fkey** (FOREIGN KEY): FOREIGN KEY (asset_id) REFERENCES assets(id)
- **monitoring_metrics_holon_id_fkey** (FOREIGN KEY): FOREIGN KEY (holon_id) REFERENCES holons(id)
- **monitoring_metrics_pkey** (PRIMARY KEY): PRIMARY KEY (id)
- **monitoring_metrics_type_check** (CHECK): CHECK (((type)::text = ANY ((ARRAY['counter'::character varying, 'gauge'::character varying, 'histogram'::character varying, 'summary'::character varying])::text[])))

**Indexes**:

- **idx_monitoring_asset**: asset_id
- **idx_monitoring_holon**: holon_id
- **idx_monitoring_name_timestamp**: name, timestamp
- **idx_monitoring_tags**: tags
- **idx_monitoring_timestamp**: timestamp
- **monitoring_metrics_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### monitoring_process_runs

Tracking of ETF process executions and their results

**Statistics**: 0 rows, 32 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | No | nextval('monitoring_process_runs_id_seq'::regcl... | - |
| run_id | uuid | No | gen_random_uuid() | - |
| process_name | varchar(255) | No | - | - |
| start_time | timestamp with time zone | No | CURRENT_TIMESTAMP | - |
| end_time | timestamp with time zone | Yes | - | - |
| duration_seconds | numeric | Yes | - | - |
| status | varchar(20) | No | 'running'::character varying | - |
| assets_analyzed | integer | Yes | - | - |
| assets_selected | integer | Yes | - | - |
| total_rgv | numeric | Yes | - | - |
| avg_rgv | numeric | Yes | - | - |
| portfolio_id | integer | Yes | - | - |
| error_message | text | Yes | - | - |
| error_details | jsonb | Yes | - | - |
| parameters | jsonb | Yes | '{}'::jsonb | - |
| metrics | jsonb | Yes | '{}'::jsonb | - |

**Constraints**:

- **monitoring_process_runs_pkey** (PRIMARY KEY): PRIMARY KEY (id)
- **process_runs_status_check** (CHECK): CHECK (((status)::text = ANY ((ARRAY['running'::character varying, 'completed'::character varying, 'failed'::character varying, 'cancelled'::character varying])::text[])))

**Indexes**:

- **idx_process_runs_start**: start_time
- **idx_process_runs_status**: status
- **monitoring_process_runs_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### portfolio_holdings

Current ETF portfolio composition and weights

**Statistics**: 0 rows, 32 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('portfolio_holdings_id_seq'::regclass) | - |
| asset_id | integer | Yes | - | - |
| holon_id | integer | Yes | - | - |
| weight | numeric(10,8) | No | - | - |
| holon_weight | numeric(10,8) | Yes | - | - |
| quantity | numeric(20,8) | Yes | - | - |
| value_usd | numeric(20,2) | Yes | - | - |
| last_rebalance | timestamp with time zone | Yes | - | - |
| is_active | boolean | Yes | true | - |
| created_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |
| updated_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **portfolio_holdings_asset_id_fkey** (FOREIGN KEY): FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
- **portfolio_holdings_holon_id_fkey** (FOREIGN KEY): FOREIGN KEY (holon_id) REFERENCES holons(id)
- **portfolio_holdings_pkey** (PRIMARY KEY): PRIMARY KEY (id)
- **portfolio_holdings_weight_check** (CHECK): CHECK (((weight >= (0)::numeric) AND (weight <= (1)::numeric)))

**Indexes**:

- **idx_holdings_active**: is_active
- **idx_holdings_asset**: asset_id
- **idx_holdings_holon**: holon_id
- **portfolio_holdings_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### portfolio_snapshots

Historical snapshots of portfolio state

**Statistics**: 0 rows, 16 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('portfolio_snapshots_id_seq'::regclass) | - |
| snapshot_date | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |
| total_value_usd | numeric(20,2) | Yes | - | - |
| num_assets | integer | Yes | - | - |
| portfolio_metrics | jsonb | Yes | - | - |
| holon_weights | jsonb | Yes | - | - |
| created_at | timestamp with time zone | Yes | CURRENT_TIMESTAMP | - |

**Constraints**:

- **portfolio_snapshots_pkey** (PRIMARY KEY): PRIMARY KEY (id)

**Indexes**:

- **portfolio_snapshots_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### rc_distributions

**Statistics**: 0 rows, 8192 bytes total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('rc_distributions_id_seq'::regclass) | - |
| recipient | varchar(56) | No | - | - |
| amount | numeric(18,7) | No | - | - |
| distribution_type | varchar(50) | Yes | - | - |
| tx_hash | varchar(64) | Yes | - | - |
| status | varchar(20) | Yes | - | - |
| created_at | timestamp without time zone | Yes | now() | - |

**Constraints**:

- **rc_distributions_pkey** (PRIMARY KEY): PRIMARY KEY (id)

**Indexes**:

- **rc_distributions_pkey**: id (UNIQUE) (PRIMARY KEY)

---

### remaining_count

**Statistics**: 1 rows, 8192 bytes total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| count | bigint | Yes | - | - |

---

### unified_reciprocity_events

**Statistics**: 0 rows, 16 kB total size

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | No | nextval('unified_reciprocity_events_id_seq'::re... | - |
| agent_id | varchar(56) | No | - | - |
| action_type | varchar(50) | No | - | - |
| action_data | jsonb | Yes | - | - |
| reciprocity_impact | numeric(10,4) | Yes | - | - |
| created_at | timestamp without time zone | Yes | now() | - |

**Constraints**:

- **unified_reciprocity_events_pkey** (PRIMARY KEY): PRIMARY KEY (id)

**Indexes**:

- **unified_reciprocity_events_pkey**: id (UNIQUE) (PRIMARY KEY)

---

## Relationships

This section documents how tables are connected through foreign key relationships. Understanding these connections is crucial for writing efficient queries and maintaining data integrity.

| From Table | From Column | To Table | To Column | Relationship Type | On Delete |
|------------|-------------|----------|-----------|-------------------|------------|
| asset_metrics | asset_id | assets | id | many-to-one (possible many-to-many via junction) | CASCADE |
| asset_metrics_history | asset_id | assets | id | many-to-one | CASCADE |
| assets | holon_id | holons | id | many-to-one (possible many-to-many via junction) | NO ACTION |
| liquidity_metrics | asset_id | assets | id | many-to-one (possible many-to-many via junction) | NO ACTION |
| monitoring_alerts | asset_id | assets | id | many-to-one (possible many-to-many via junction) | NO ACTION |
| monitoring_alerts | holon_id | holons | id | many-to-one (possible many-to-many via junction) | NO ACTION |
| monitoring_metrics | asset_id | assets | id | many-to-one (possible many-to-many via junction) | NO ACTION |
| monitoring_metrics | holon_id | holons | id | many-to-one (possible many-to-many via junction) | NO ACTION |
| portfolio_holdings | asset_id | assets | id | many-to-one (possible many-to-many via junction) | CASCADE |
| portfolio_holdings | holon_id | holons | id | many-to-one (possible many-to-many via junction) | NO ACTION |

## Summary Statistics

### Schema Overview

- **Total Tables**: 15
- **Total Columns**: 196
- **Total Relationships**: 10
- **Total Indexes**: 52
- **Total Triggers**: 3
- **Total Functions**: 8

### Largest Tables by Row Count

1. **etf_config**: 12 rows
2. **holons**: 5 rows
3. **assets**: 1 rows
4. **remaining_count**: 1 rows
5. **asset_metrics**: 0 rows

### Most Referenced Tables

These tables are referenced by foreign keys from other tables, indicating they are central to the data model:

- **assets**: Referenced by 6 foreign keys
- **holons**: Referenced by 4 foreign keys

### Orphan Tables

These tables have no foreign key relationships. They might be lookup tables, log tables, or candidates for review:

- remaining_count
- portfolio_snapshots
- rc_distributions
- monitoring_process_runs
- unified_reciprocity_events
- etf_config
- issuer_trust
