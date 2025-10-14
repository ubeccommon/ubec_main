#!/usr/bin/env python3
"""
UBEC Token Distribution Diagnostic Tool

This script analyzes where all UBEC tokens are located and identifies
any discrepancies between issued supply and tracked balances.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import asyncio
import asyncpg
from decimal import Decimal
from datetime import datetime
import json

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ubec',
    'user': 'ubec_admin',
    'password': None,  # Will prompt or use .pgpass
}

UBEC_ISSUER = 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN'

# Official accounts
OFFICIAL_ACCOUNTS = {
    'general': 'GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74',
    'administration': 'GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC',
    'stewardship_management': 'GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC',
    'stewardship_infrastructure': 'GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC',
    'stewardship_liquidity': 'GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC',
}

# Target distribution
TARGET_DISTRIBUTION = {
    'general': Decimal('0.65'),
    'administration': Decimal('0.05'),
    'stewardship': Decimal('0.30'),
}

TOTAL_ISSUED = Decimal('191766038.91')


async def analyze_token_distribution():
    """Main analysis function."""
    
    print("=" * 80)
    print("UBEC TOKEN DISTRIBUTION DIAGNOSTIC")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Total Issued Supply: {TOTAL_ISSUED:,.2f} UBEC")
    print()
    
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 1. Get total in database
        print("📊 DATABASE ANALYSIS")
        print("-" * 80)
        
        query = """
            SELECT 
                COUNT(DISTINCT account_id) as total_holders,
                SUM(balance) as total_balance
            FROM ubec_main.ubec_balances
            WHERE token_code = 'UBEC' AND balance > 0
        """
        
        result = await conn.fetchrow(query)
        total_holders = result['total_holders']
        total_tracked = Decimal(str(result['total_balance']))
        
        print(f"Total Holders in DB: {total_holders:,}")
        print(f"Total Balance Tracked: {total_tracked:,.7f} UBEC")
        print(f"Percentage of Supply: {(total_tracked / TOTAL_ISSUED * 100):.2f}%")
        print()
        
        # 2. Official accounts breakdown
        print("🏛️  OFFICIAL ACCOUNTS")
        print("-" * 80)
        
        official_total = Decimal('0')
        for label, account_id in OFFICIAL_ACCOUNTS.items():
            query = """
                SELECT COALESCE(SUM(balance), 0) as balance
                FROM ubec_main.ubec_balances
                WHERE account_id = $1 AND token_code = 'UBEC'
            """
            result = await conn.fetchrow(query, account_id)
            balance = Decimal(str(result['balance']))
            official_total += balance
            
            print(f"{label:30s}: {balance:20,.7f} UBEC")
        
        print(f"{'Total Official':30s}: {official_total:20,.7f} UBEC")
        print()
        
        # 3. Check for liquidity pool balances
        print("💧 LIQUIDITY POOLS")
        print("-" * 80)
        
        query = """
            SELECT 
                id,
                pair,
                balance,
                total_shares,
                reserve_a,
                reserve_b
            FROM ubec_main.liquidity_pools
            WHERE token_code = 'UBEC'
        """
        
        pools = await conn.fetch(query)
        lp_total = Decimal('0')
        
        if pools:
            for pool in pools:
                balance = Decimal(str(pool['balance']))
                lp_total += balance
                print(f"Pool {pool['pair']:20s}: {balance:20,.7f} UBEC")
            print(f"{'Total in LPs':30s}: {lp_total:20,.7f} UBEC")
        else:
            print("No liquidity pools found in database")
        print()
        
        # 4. Top holders analysis
        print("🐋 TOP 20 HOLDERS (Excluding Official Accounts)")
        print("-" * 80)
        
        excluded_accounts = list(OFFICIAL_ACCOUNTS.values())
        
        query = """
            SELECT 
                account_id,
                balance,
                (balance / $1 * 100) as percent_of_supply
            FROM ubec_main.ubec_balances
            WHERE token_code = 'UBEC' 
                AND balance > 0
                AND account_id != ALL($2::varchar[])
            ORDER BY balance DESC
            LIMIT 20
        """
        
        top_holders = await conn.fetch(query, float(TOTAL_ISSUED), excluded_accounts)
        
        public_total = Decimal('0')
        for i, holder in enumerate(top_holders, 1):
            balance = Decimal(str(holder['balance']))
            percent = float(holder['percent_of_supply'])
            public_total += balance
            print(f"{i:2d}. {holder['account_id'][:8]}...{holder['account_id'][-8:]}: "
                  f"{balance:15,.7f} UBEC ({percent:6.3f}%)")
        
        print(f"\nTop 20 Public Holders Total: {public_total:,.7f} UBEC")
        print()
        
        # 5. Distribution by holder size
        print("📈 HOLDER DISTRIBUTION BY SIZE")
        print("-" * 80)
        
        query = """
            SELECT 
                CASE 
                    WHEN balance >= 1000000 THEN 'Whales (≥1M)'
                    WHEN balance >= 100000 THEN 'Large (100K-1M)'
                    WHEN balance >= 10000 THEN 'Medium (10K-100K)'
                    WHEN balance >= 1000 THEN 'Small (1K-10K)'
                    ELSE 'Micro (<1K)'
                END as category,
                COUNT(*) as holder_count,
                SUM(balance) as total_balance,
                SUM(balance) / $1 * 100 as percent_of_supply
            FROM ubec_main.ubec_balances
            WHERE token_code = 'UBEC' AND balance > 0
            GROUP BY category
            ORDER BY MIN(balance) DESC
        """
        
        distribution = await conn.fetch(query, float(TOTAL_ISSUED))
        
        for row in distribution:
            print(f"{row['category']:20s}: {row['holder_count']:6,} holders, "
                  f"{Decimal(str(row['total_balance'])):15,.2f} UBEC "
                  f"({float(row['percent_of_supply']):6.2f}%)")
        print()
        
        # 6. Calculate missing tokens
        print("🔍 MISSING TOKENS ANALYSIS")
        print("-" * 80)
        
        missing = TOTAL_ISSUED - total_tracked
        missing_percent = (missing / TOTAL_ISSUED * 100)
        
        print(f"Total Issued:        {TOTAL_ISSUED:20,.7f} UBEC")
        print(f"Total Tracked in DB: {total_tracked:20,.7f} UBEC")
        print(f"Missing/Untracked:   {missing:20,.7f} UBEC ({missing_percent:.2f}%)")
        print()
        
        if missing > 0:
            print("⚠️  Possible locations of missing tokens:")
            print("   1. Still held by issuer (not yet distributed)")
            print("   2. Accounts not yet synced to database")
            print("   3. Burned/clawed back tokens (removed from circulation)")
            print("   4. Tokens in accounts below sync threshold")
            print()
        
        # 7. Compliance check
        print("✅ TOKENOMICS COMPLIANCE CHECK")
        print("-" * 80)
        
        if total_tracked > 0:
            actual_general = Decimal('0')
            actual_admin = Decimal('0')
            actual_steward = Decimal('0')
            
            # General
            query = """
                SELECT COALESCE(SUM(balance), 0) as balance
                FROM ubec_main.ubec_balances
                WHERE account_id = $1 AND token_code = 'UBEC'
            """
            result = await conn.fetchrow(query, OFFICIAL_ACCOUNTS['general'])
            actual_general = Decimal(str(result['balance']))
            
            # Administration
            result = await conn.fetchrow(query, OFFICIAL_ACCOUNTS['administration'])
            actual_admin = Decimal(str(result['balance']))
            
            # Stewardship (all three accounts)
            for key in ['stewardship_management', 'stewardship_infrastructure', 'stewardship_liquidity']:
                result = await conn.fetchrow(query, OFFICIAL_ACCOUNTS[key])
                actual_steward += Decimal(str(result['balance']))
            
            # Calculate percentages against ISSUED supply (not tracked)
            gen_pct = (actual_general / TOTAL_ISSUED * 100)
            admin_pct = (actual_admin / TOTAL_ISSUED * 100)
            steward_pct = (actual_steward / TOTAL_ISSUED * 100)
            
            target_gen_pct = float(TARGET_DISTRIBUTION['general'] * 100)
            target_admin_pct = float(TARGET_DISTRIBUTION['administration'] * 100)
            target_steward_pct = float(TARGET_DISTRIBUTION['stewardship'] * 100)
            
            print(f"{'Category':20s} {'Target':>12s} {'Actual':>12s} {'Status':>12s}")
            print(f"{'-'*20} {'-'*12} {'-'*12} {'-'*12}")
            
            def check_compliance(actual, target, tolerance=2.0):
                diff = abs(float(actual) - target)
                return "✅ COMPLIANT" if diff <= tolerance else "❌ OUT OF RANGE"
            
            print(f"{'General':20s} {target_gen_pct:11.2f}% {gen_pct:11.2f}% "
                  f"{check_compliance(gen_pct, target_gen_pct):>12s}")
            print(f"{'Administration':20s} {target_admin_pct:11.2f}% {admin_pct:11.2f}% "
                  f"{check_compliance(admin_pct, target_admin_pct):>12s}")
            print(f"{'Stewardship':20s} {target_steward_pct:11.2f}% {steward_pct:11.2f}% "
                  f"{check_compliance(steward_pct, target_steward_pct):>12s}")
        
        print()
        print("=" * 80)
        
        # Export to JSON
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_issued': float(TOTAL_ISSUED),
            'total_tracked': float(total_tracked),
            'missing': float(missing),
            'missing_percent': float(missing_percent),
            'total_holders': total_holders,
            'official_accounts': {k: float(v) for k, v in 
                                 [(label, Decimal(str((await conn.fetchrow(
                                     "SELECT COALESCE(SUM(balance), 0) as balance FROM ubec_main.ubec_balances "
                                     "WHERE account_id = $1 AND token_code = 'UBEC'", 
                                     account_id))['balance']))) 
                                  for label, account_id in OFFICIAL_ACCOUNTS.items()]},
            'top_20_public_total': float(public_total),
        }
        
        with open('/home/claude/ubec_distribution_analysis.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print("\n📄 Full analysis exported to: ubec_distribution_analysis.json")
        
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(analyze_token_distribution())
