-- ============================================================================
-- UBEC Order Book - Quick Verification Queries
-- ============================================================================
-- Run these to verify everything is working correctly
-- ============================================================================

SET search_path TO ubec_main;

-- Test 1: Refresh the materialized view
SELECT refresh_orderbook_summary_now();

-- Test 2: Check table sizes
SELECT * FROM check_orderbook_table_sizes();

-- Test 3: Verify all tables exist
SELECT 
    'Tables' as category,
    string_agg(tablename, ', ') as items
FROM pg_tables
WHERE schemaname = 'ubec_main'
AND tablename IN ('orderbook_snapshots', 'stellar_offers', 'account_order_positions', 'orderbook_analytics');

-- Test 4: Verify views exist
SELECT 
    'Views' as category,
    string_agg(table_name, ', ') as items
FROM information_schema.views
WHERE table_schema = 'ubec_main'
AND table_name IN ('v_orderbook_depth', 'v_top_traders', 'v_market_imbalance');

-- Test 5: Verify materialized views
SELECT 
    'Materialized Views' as category,
    string_agg(matviewname, ', ') as items
FROM pg_matviews
WHERE schemaname = 'ubec_main'
AND matviewname = 'orderbook_summary';

-- Test 6: Show configuration
SELECT 
    '═══════════════════════════════════════' as title
UNION ALL
SELECT '  Order Book Configuration'
UNION ALL
SELECT '═══════════════════════════════════════'
UNION ALL
SELECT ''
UNION ALL
SELECT parameter_name || ': ' || parameter_value
FROM system_configuration
WHERE parameter_name LIKE 'orderbook_%'
ORDER BY parameter_name;

-- Test 7: Show scheduler jobs
SELECT 
    '═══════════════════════════════════════' as title
UNION ALL
SELECT '  Scheduled Jobs'
UNION ALL
SELECT '═══════════════════════════════════════'
UNION ALL
SELECT ''
UNION ALL
SELECT job_name || ' (every ' || schedule_interval || ')'
FROM scheduler_jobs
WHERE job_name LIKE 'orderbook_%';

-- Test 8: Insert a test snapshot (safe - uses ON CONFLICT)
INSERT INTO orderbook_snapshots (
    asset_code,
    counter_asset,
    snapshot_time,
    best_bid,
    best_ask,
    spread_bps,
    bid_depth_total,
    ask_depth_total,
    bid_levels,
    ask_levels,
    raw_data
) VALUES (
    'UBEC',
    'XLM',
    NOW(),
    0.95,
    1.05,
    1000,
    10000.00,
    9500.00,
    10,
    12,
    '{"bids": [{"price": "0.95", "amount": "1000"}], "asks": [{"price": "1.05", "amount": "950"}]}'::jsonb
)
ON CONFLICT (asset_code, counter_asset, snapshot_time) DO NOTHING;

-- Test 9: Query the test data back
SELECT 
    asset_code,
    counter_asset,
    snapshot_time,
    best_bid,
    best_ask,
    spread_bps,
    bid_depth_total + ask_depth_total as total_liquidity
FROM orderbook_snapshots
WHERE asset_code = 'UBEC'
ORDER BY snapshot_time DESC
LIMIT 1;

-- Test 10: Show index count
SELECT 
    '═══════════════════════════════════════' as title
UNION ALL
SELECT '  Index Summary'
UNION ALL
SELECT '═══════════════════════════════════════'
UNION ALL
SELECT ''
UNION ALL
SELECT tablename || ': ' || COUNT(*)::text || ' indexes'
FROM pg_indexes
WHERE schemaname = 'ubec_main'
AND tablename IN ('orderbook_snapshots', 'stellar_offers', 'account_order_positions', 'orderbook_analytics')
GROUP BY tablename;

-- Final Success Message
SELECT 
    '═══════════════════════════════════════' as message
UNION ALL
SELECT '  ✓ ORDER BOOK SETUP COMPLETE'
UNION ALL
SELECT '═══════════════════════════════════════'
UNION ALL
SELECT ''
UNION ALL
SELECT 'All systems operational!'
UNION ALL
SELECT ''
UNION ALL
SELECT 'Next steps:'
UNION ALL
SELECT '1. Copy ubec_orderbook_service.py to:'
UNION ALL
SELECT '   services/market/ubec_orderbook_service.py'
UNION ALL
SELECT ''
UNION ALL
SELECT '2. Initialize the service in your code'
UNION ALL
SELECT ''
UNION ALL
SELECT '3. Start fetching order book data!'
UNION ALL
SELECT '';
