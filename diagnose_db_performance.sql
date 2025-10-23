-- Diagnostic queries for UBEC database performance issue
-- Index exists but query slow during initialization

-- 1. Check if index is valid and being used
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'system_settings'
ORDER BY indexname;

-- 2. Check index validity and size
SELECT 
    indexrelid::regclass AS index_name,
    indisvalid AS is_valid,
    indisready AS is_ready,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_index
WHERE indrelid = 'system_settings'::regclass;

-- 3. Check table statistics freshness
SELECT 
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
WHERE tablename = 'system_settings';

-- 4. Analyze the actual query with EXPLAIN
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) 
SELECT setting_key, setting_value, setting_type
FROM system_settings
WHERE is_active = TRUE 
  AND setting_key LIKE 'rate_limit_%'
ORDER BY setting_key;

-- 5. Check for table bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) AS indexes_size,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows
FROM pg_stat_user_tables
WHERE tablename = 'system_settings';

-- 6. Check active connections and pool status
SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle,
    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity
WHERE datname = 'ubec';

-- 7. Check for locks on system_settings table
SELECT 
    locktype,
    relation::regclass,
    mode,
    granted,
    pid,
    query_start,
    state
FROM pg_locks l
LEFT JOIN pg_stat_activity a ON l.pid = a.pid
WHERE relation = 'system_settings'::regclass
   OR relation IS NULL AND locktype = 'relation';

-- 8. Check query planner settings
SHOW shared_buffers;
SHOW effective_cache_size;
SHOW random_page_cost;
SHOW seq_page_cost;
