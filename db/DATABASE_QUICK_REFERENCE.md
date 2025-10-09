# UBEC Database Schema - Quick Reference Guide

**Database:** `ubec`  
**Schema:** `ubec_main`  
**Version:** 1.0  
**Date:** October 8, 2025

---

## Installation

### Method 1: Direct Installation
```bash
# Create database and run schema
psql -U postgres -f ubec_database_schema.sql
```

### Method 2: Step by Step
```bash
# Connect to PostgreSQL
psql -U postgres

# Run the script
\i ubec_database_schema.sql

# Verify installation
\c ubec
\dt ubec_main.*
```

### Verify Installation
```sql
-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'ubec_main'
ORDER BY table_name;

-- Check views
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'ubec_main'
ORDER BY table_name;

-- Check functions
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'ubec_main'
ORDER BY routine_name;
```

---

## Database Structure

### Core Tables (11 tables)

#### Blockchain Data Tables
1. **stellar_accounts** - Stellar account information with element tracking
2. **stellar_transactions** - Transaction history across all tokens
3. **stellar_operations** - Individual operations with element context
4. **stellar_effects** - Blockchain state changes

#### UBEC-Specific Tables
5. **ubec_balances** - Token balances for all four elements
6. **ubec_distributions** - Distribution tracking (75/20/5 rule)
7. **ubec_holonic_metrics** - Ubuntu principles assessment
8. **ubec_audit_log** - Audit trail for validation
9. **ubec_sync_status** - Synchronization state tracking
10. **ubec_reports** - Generated reports and analysis
11. **Element-specific metadata tables**

---

## Custom Types

### element_type
```sql
CREATE TYPE element_type AS ENUM ('air', 'water', 'earth', 'fire');
```
Maps to:
- `air` = UBEC (Gateway)
- `water` = UBECrc (Flow)
- `earth` = UBECgpi (Stability)
- `fire` = UBECtt (Transformation)

### token_code
```sql
CREATE TYPE token_code AS ENUM ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt');
```

### ubuntu_principle
```sql
CREATE TYPE ubuntu_principle AS ENUM ('diversity', 'reciprocity', 'mutualism', 'regeneration', 'holism');
```

### distribution_category
```sql
CREATE TYPE distribution_category AS ENUM ('general_circulation', 'stewardship', 'administration');
```

---

## Element-Specific Views

### 1. Air Element (Gateway)
```sql
SELECT * FROM ubec_main.view_air_gateway;
```
**Columns:**
- account_id
- gateway_created
- last_activity_at
- ubec_balance
- distribution_category
- diversity_score
- transaction_count
- last_transaction

**Use case:** Monitor gateway access points and diversity

### 2. Water Element (Flow)
```sql
SELECT * FROM ubec_main.view_water_flow;
```
**Columns:**
- transaction_hash
- source_account
- created_at
- operation_count
- total_flow_amount
- reciprocity_score
- successful

**Use case:** Track liquidity and exchange patterns

### 3. Earth Element (Stability)
```sql
SELECT * FROM ubec_main.view_earth_stability;
```
**Columns:**
- token_code
- distribution_category
- target_percentage
- current_percentage
- current_amount
- is_compliant
- deviation
- mutualism_score

**Use case:** Monitor distribution compliance and stability

### 4. Fire Element (Transformation)
```sql
SELECT * FROM ubec_main.view_fire_transformation;
```
**Columns:**
- operation_id
- transaction_hash
- operation_type
- source_account
- amount
- validation_status
- is_anomaly
- regeneration_score

**Use case:** Track transformative actions and audits

### 5. System Holonic Health
```sql
SELECT * FROM ubec_main.view_system_holonic_health;
```
**Columns:**
- element
- principle
- avg_score
- min_score
- max_score
- sample_count
- most_common_status

**Use case:** Overall system health assessment

---

## Utility Functions

### 1. Map Token to Element
```sql
SELECT ubec_main.get_element_for_token('UBEC'::token_code);
-- Returns: 'air'

SELECT ubec_main.get_element_for_token('UBECrc'::token_code);
-- Returns: 'water'
```

### 2. Map Principle to Element
```sql
SELECT ubec_main.get_element_for_principle('diversity'::ubuntu_principle);
-- Returns: 'air'

SELECT ubec_main.get_element_for_principle('reciprocity'::ubuntu_principle);
-- Returns: 'water'
```

### 3. Check Distribution Compliance
```sql
SELECT ubec_main.check_distribution_compliance('UBECgpi'::token_code, 5.0);
-- Returns: true/false
-- Second parameter is tolerance percentage (default 5%)
```

### 4. Get Latest Holonic Score
```sql
SELECT ubec_main.get_latest_holonic_score('air'::element_type, 'diversity'::ubuntu_principle);
-- Returns: decimal score (0-1)
```

---

## Common Queries

### Get All Active Accounts for an Element
```sql
SELECT account_id, balance, distribution_category
FROM ubec_main.ubec_balances
WHERE token_code = 'UBEC' 
  AND balance > 0
ORDER BY balance DESC;
```

### Get Recent Transactions for a Token
```sql
SELECT 
    st.transaction_hash,
    st.source_account,
    st.created_at,
    st.operation_count
FROM ubec_main.stellar_transactions st
WHERE 'UBECrc' = ANY(st.involves_tokens)
  AND st.created_at > NOW() - INTERVAL '24 hours'
ORDER BY st.created_at DESC;
```

### Check Distribution Status for All Tokens
```sql
SELECT 
    token_code,
    category,
    target_percentage,
    current_percentage,
    deviation,
    is_compliant
FROM ubec_main.ubec_distributions
WHERE snapshot_time = (
    SELECT MAX(snapshot_time) 
    FROM ubec_main.ubec_distributions
)
ORDER BY token_code, category;
```

### Get Holonic Health Summary
```sql
SELECT 
    element,
    principle,
    AVG(score) as avg_score,
    COUNT(*) as measurements
FROM ubec_main.ubec_holonic_metrics
WHERE calculated_at > NOW() - INTERVAL '7 days'
GROUP BY element, principle
ORDER BY element, principle;
```

### Find Anomalies in Audit Log
```sql
SELECT 
    element,
    entity_type,
    entity_id,
    anomaly_type,
    severity,
    audited_at
FROM ubec_main.ubec_audit_log
WHERE is_anomaly = true
  AND audited_at > NOW() - INTERVAL '24 hours'
ORDER BY severity DESC, audited_at DESC;
```

### Get Sync Status for All Elements
```sql
SELECT 
    element,
    token_code,
    sync_type,
    status,
    last_sync_time,
    records_synced
FROM ubec_main.ubec_sync_status
ORDER BY element, token_code, sync_type;
```

---

## Insert Examples

### Add a New Account
```sql
INSERT INTO ubec_main.stellar_accounts (
    account_id,
    primary_element,
    token_holdings,
    created_at
) VALUES (
    'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'air',
    ARRAY['UBEC']::token_code[],
    NOW()
);
```

### Record a Balance
```sql
INSERT INTO ubec_main.ubec_balances (
    account_id,
    token_code,
    element,
    balance,
    distribution_category
) VALUES (
    'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'UBEC',
    'air',
    1000.00,
    'general_circulation'
);
```

### Log a Holonic Metric
```sql
INSERT INTO ubec_main.ubec_holonic_metrics (
    account_id,
    element,
    principle,
    score,
    health_status
) VALUES (
    'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'air',
    'diversity',
    0.85,
    'excellent'
);
```

### Create an Audit Entry
```sql
INSERT INTO ubec_main.ubec_audit_log (
    element,
    token_code,
    entity_type,
    entity_id,
    audit_type,
    status,
    is_valid
) VALUES (
    'fire',
    'UBECtt',
    'operation',
    'some-operation-id',
    'transformation_validation',
    'complete',
    true
);
```

---

## Update Examples

### Update Account Activity
```sql
UPDATE ubec_main.stellar_accounts
SET last_activity_at = NOW()
WHERE account_id = 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX';
```

### Update Balance
```sql
UPDATE ubec_main.ubec_balances
SET balance = balance + 100.00
WHERE account_id = 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
  AND token_code = 'UBEC';
```

### Update Distribution Status
```sql
UPDATE ubec_main.ubec_distributions
SET 
    current_percentage = 76.5,
    current_amount = 16065000.00,
    deviation = 1.5,
    is_compliant = true,
    snapshot_time = NOW()
WHERE token_code = 'UBECgpi' 
  AND category = 'general_circulation';
```

### Update Sync Status
```sql
UPDATE ubec_main.ubec_sync_status
SET 
    status = 'complete',
    last_sync_time = NOW(),
    records_synced = records_synced + 150
WHERE element = 'air' 
  AND token_code = 'UBEC' 
  AND sync_type = 'transactions';
```

---

## Maintenance Queries

### Check Table Sizes
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'ubec_main'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Vacuum and Analyze
```sql
VACUUM ANALYZE ubec_main.stellar_accounts;
VACUUM ANALYZE ubec_main.stellar_transactions;
VACUUM ANALYZE ubec_main.ubec_balances;
```

### Check Index Usage
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'ubec_main'
ORDER BY idx_scan DESC;
```

### Find Unused Indexes
```sql
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE schemaname = 'ubec_main'
  AND idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey';
```

---

## Backup and Restore

### Backup Database
```bash
# Full database backup
pg_dump -U postgres -d ubec -F c -f ubec_backup_$(date +%Y%m%d).dump

# Schema only
pg_dump -U postgres -d ubec -s -F p -f ubec_schema_$(date +%Y%m%d).sql

# Data only
pg_dump -U postgres -d ubec -a -F p -f ubec_data_$(date +%Y%m%d).sql
```

### Restore Database
```bash
# Restore from custom format
pg_restore -U postgres -d ubec -c ubec_backup_20251008.dump

# Restore from SQL file
psql -U postgres -d ubec -f ubec_backup_20251008.sql
```

---

## Performance Tips

### Add Additional Indexes (if needed)
```sql
-- For specific query patterns
CREATE INDEX idx_custom_balance_lookup 
ON ubec_main.ubec_balances(token_code, balance) 
WHERE balance > 0;

CREATE INDEX idx_custom_recent_transactions 
ON ubec_main.stellar_transactions(created_at DESC) 
WHERE successful = true;
```

### Partitioning Large Tables (for future scaling)
```sql
-- Example: Partition transactions by date
CREATE TABLE ubec_main.stellar_transactions_2025_10 
PARTITION OF ubec_main.stellar_transactions
FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

---

## Security Best Practices

### Create Read-Only User
```sql
CREATE USER ubec_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE ubec TO ubec_readonly;
GRANT USAGE ON SCHEMA ubec_main TO ubec_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA ubec_main TO ubec_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA ubec_main TO ubec_readonly;
```

### Create Application User
```sql
CREATE USER ubec_app WITH PASSWORD 'secure_app_password';
GRANT CONNECT ON DATABASE ubec TO ubec_app;
GRANT USAGE ON SCHEMA ubec_main TO ubec_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA ubec_main TO ubec_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA ubec_main TO ubec_app;
```

### Enable Row-Level Security (if needed)
```sql
ALTER TABLE ubec_main.ubec_balances ENABLE ROW LEVEL SECURITY;

CREATE POLICY balance_view_policy ON ubec_main.ubec_balances
FOR SELECT
TO ubec_readonly
USING (true);
```

---

## Troubleshooting

### Check Connection
```sql
SELECT current_database(), current_schema(), current_user;
```

### Check Schema Exists
```sql
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name = 'ubec_main';
```

### Check Table Row Counts
```sql
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'ubec_main'
ORDER BY n_live_tup DESC;
```

### Check for Locks
```sql
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'ubec'
  AND state != 'idle';
```

### Kill Long-Running Query
```sql
-- Find the query
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE datname = 'ubec' AND state = 'active'
ORDER BY duration DESC;

-- Terminate it (use with caution!)
SELECT pg_terminate_backend(pid);
```

---

## Integration with Python

### Connection Example
```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="ubec",
    user="ubec_app",
    password="secure_app_password"
)

# Set schema
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("SET search_path TO ubec_main, public")

# Query example
cur.execute("""
    SELECT * FROM view_air_gateway 
    WHERE ubec_balance > 0 
    LIMIT 10
""")
results = cur.fetchall()

# Close
cur.close()
conn.close()
```

### Using SQLAlchemy
```python
from sqlalchemy import create_engine, MetaData

# Create engine
engine = create_engine('postgresql://ubec_app:secure_app_password@localhost/ubec')

# Set schema
metadata = MetaData(schema='ubec_main')
metadata.reflect(bind=engine)

# Access tables
accounts_table = metadata.tables['ubec_main.stellar_accounts']
balances_table = metadata.tables['ubec_main.ubec_balances']
```

---

## Next Steps

1. **Configure Issuer Addresses**: Update your application configuration with actual Stellar issuer addresses
2. **Run Synchronizer**: Start the data synchronization process to populate blockchain data
3. **Monitor Performance**: Watch query performance and add indexes as needed
4. **Set Up Backups**: Schedule regular database backups
5. **Review Security**: Adjust permissions based on your security requirements

---

## Support

For questions or issues:
1. Check the main evaluation document: `COMPREHENSIVE_MODULE_EVALUATION.md`
2. Review integration guide: `INTEGRATION_GUIDE_Practical_Code_Examples.md`
3. Follow action plan: `ACTION_PLAN_Next_Steps.md`

---

**Database Status:** ✅ Ready for use

**Version:** 1.0

**Last Updated:** October 8, 2025
