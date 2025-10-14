#!/bin/bash
# UBEC Token Distribution Quick Analysis
# Run this script to get an immediate overview of token distribution

echo "================================================================================"
echo "UBEC TOKEN DISTRIBUTION QUICK ANALYSIS"
echo "================================================================================"
echo ""

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "❌ Error: psql not found. Please install PostgreSQL client tools."
    exit 1
fi

# Run the analysis
sudo -u postgres psql -d ubec << 'EOF'
\echo '📊 TOTAL TRACKED IN DATABASE'
\echo '--------------------------------------------------------------------------------'
SELECT 
    COUNT(DISTINCT account_id) as total_holders,
    SUM(balance)::numeric(20,7) as total_balance,
    (SUM(balance) / 191766038.91 * 100)::numeric(10,2) as percent_of_issued
FROM ubec_main.ubec_balances
WHERE token_code = 'UBEC' AND balance > 0;

\echo ''
\echo '🔍 MISSING TOKENS CALCULATION'
\echo '--------------------------------------------------------------------------------'
SELECT 
    191766038.91::numeric(20,7) as total_issued,
    SUM(balance)::numeric(20,7) as total_tracked,
    (191766038.91 - SUM(balance))::numeric(20,7) as missing,
    ((191766038.91 - SUM(balance)) / 191766038.91 * 100)::numeric(10,2) as missing_percent
FROM ubec_main.ubec_balances
WHERE token_code = 'UBEC' AND balance > 0;

\echo ''
\echo '🏛️  OFFICIAL ACCOUNTS'
\echo '--------------------------------------------------------------------------------'
WITH account_labels AS (
    SELECT 'General' as label, 'GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74' as account_id
    UNION ALL SELECT 'Administration', 'GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC'
    UNION ALL SELECT 'Stewardship-Mgmt', 'GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC'
    UNION ALL SELECT 'Stewardship-Infra', 'GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC'
    UNION ALL SELECT 'Stewardship-Liq', 'GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC'
)
SELECT 
    a.label,
    COALESCE(b.balance, 0)::numeric(20,7) as balance,
    (COALESCE(b.balance, 0) / 191766038.91 * 100)::numeric(10,4) as percent
FROM account_labels a
LEFT JOIN ubec_main.ubec_balances b ON a.account_id = b.account_id AND b.token_code = 'UBEC'
ORDER BY a.label;

\echo ''
\echo '🐋 TOP 10 PUBLIC HOLDERS'
\echo '--------------------------------------------------------------------------------'
WITH official AS (
    SELECT unnest(ARRAY[
        'GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74',
        'GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC',
        'GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC',
        'GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC',
        'GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC'
    ]) as id
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY balance DESC) as rank,
    LEFT(account_id, 8) || '...' || RIGHT(account_id, 8) as account,
    balance::numeric(20,7),
    (balance / 191766038.91 * 100)::numeric(10,4) as percent
FROM ubec_main.ubec_balances
WHERE token_code = 'UBEC' 
    AND balance > 0
    AND account_id NOT IN (SELECT id FROM official)
ORDER BY balance DESC
LIMIT 10;

\echo ''
\echo '================================================================================'
EOF

echo ""
echo "✅ Analysis complete!"
echo ""
echo "Next steps:"
echo "  1. If missing tokens > 20%, run: python main.py --mode sync --sync-type all --asset-code UBEC"
echo "  2. Then re-evaluate: python main.py --mode distribution --action evaluate"
echo ""
