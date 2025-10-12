#!/usr/bin/env python3
"""
UBEC Analytics Service - Usage Examples

Demonstrates how to use the analytics service to gain insights
into the UBEC ecosystem.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import asyncio
import json
import os
from decimal import Decimal
from datetime import datetime

# Import services
from core.db.database_manager import AsyncDatabaseManager
from services.analytics.ubec_analytics_service import (
    UBECAnalyticsService,
    TokenCode,
    AnalyticsException
)


async def example_basic_usage():
    """Example 1: Basic usage - get token distribution"""
    print("=" * 70)
    print("Example 1: Basic Token Distribution Analysis")
    print("=" * 70)
    
    # Initialize database
    db = AsyncDatabaseManager({
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'ubec_main'),
        'user': os.getenv('DB_USER', 'ubec_user'),
        'password': os.getenv('DB_PASSWORD', 'your_password'),
        'port': int(os.getenv('DB_PORT', 5432))
    })
    await db.initialize()
    
    # Initialize analytics service
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Get distribution for UBEC token
    distribution = await analytics.get_token_distribution('UBEC')
    
    print(f"\nToken: {distribution.token_code} ({distribution.element})")
    print(f"Total Holders: {distribution.total_holders:,}")
    print(f"Total Supply: {distribution.total_supply:,.2f}")
    print(f"Average Balance: {distribution.average_balance:,.2f}")
    print(f"Median Balance: {distribution.median_balance:,.2f}")
    print(f"Largest Holder: {distribution.max_balance:,.2f}")
    print(f"\nConcentration Metrics:")
    print(f"  Top 10 holders control: {distribution.top_10_concentration:.2f}%")
    print(f"  Top 100 holders control: {distribution.top_100_concentration:.2f}%")
    if distribution.gini_coefficient:
        print(f"  Gini coefficient: {distribution.gini_coefficient:.4f}")
        print(f"    (0 = perfect equality, 1 = perfect inequality)")
    
    # Cleanup
    await analytics.close()
    await db.close()
    
    print("\n✓ Example 1 complete\n")


async def example_holder_analysis():
    """Example 2: Analyze holder concentration"""
    print("=" * 70)
    print("Example 2: Holder Concentration Analysis")
    print("=" * 70)
    
    # Initialize
    db = AsyncDatabaseManager({
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'ubec_main'),
        'user': os.getenv('DB_USER', 'ubec_user'),
        'password': os.getenv('DB_PASSWORD', 'your_password'),
        'port': int(os.getenv('DB_PORT', 5432))
    })
    await db.initialize()
    
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Analyze holder concentration with custom thresholds
    analysis = await analytics.analyze_holder_concentration(
        token_code='UBEC',
        whale_threshold=Decimal('50000'),  # 50k+ = whale
        mid_tier_threshold=Decimal('5000')  # 5k+ = mid-tier
    )
    
    print(f"\nToken: {analysis.token_code}")
    print(f"Total Holders: {analysis.total_holders:,}\n")
    
    print(f"🐋 Whales (≥50,000 UBEC):")
    print(f"  Count: {analysis.whale_count}")
    print(f"  Holdings: {analysis.whale_holdings:,.2f} UBEC")
    print(f"  Percentage: {analysis.whale_percentage:.2f}% of total supply")
    
    print(f"\n📊 Mid-Tier (≥5,000 UBEC):")
    print(f"  Count: {analysis.mid_tier_count}")
    print(f"  Holdings: {analysis.mid_tier_holdings:,.2f} UBEC")
    
    print(f"\n🐠 Small Holders (<5,000 UBEC):")
    print(f"  Count: {analysis.small_holder_count}")
    print(f"  Holdings: {analysis.small_holder_holdings:,.2f} UBEC")
    
    # Cleanup
    await analytics.close()
    await db.close()
    
    print("\n✓ Example 2 complete\n")


async def example_identify_whales():
    """Example 3: Identify top whale accounts"""
    print("=" * 70)
    print("Example 3: Identify Top Whales")
    print("=" * 70)
    
    # Initialize
    db = AsyncDatabaseManager({
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'ubec_main'),
        'user': os.getenv('DB_USER', 'ubec_user'),
        'password': os.getenv('DB_PASSWORD', 'your_password'),
        'port': int(os.getenv('DB_PORT', 5432))
    })
    await db.initialize()
    
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Find top 10 whales
    whales = await analytics.identify_whales(
        token_code='UBEC',
        threshold=Decimal('10000'),
        limit=10
    )
    
    print(f"\nTop 10 UBEC Whales (≥10,000 UBEC):\n")
    print(f"{'Rank':<6} {'Account ID':<58} {'Balance':>15}")
    print("-" * 80)
    
    for i, whale in enumerate(whales, 1):
        account_short = f"{whale['account_id'][:8]}...{whale['account_id'][-8:]}"
        print(f"{i:<6} {account_short:<58} {whale['balance']:>15,.2f}")
    
    # Cleanup
    await analytics.close()
    await db.close()
    
    print("\n✓ Example 3 complete\n")


async def example_ecosystem_health():
    """Example 4: Check ecosystem health"""
    print("=" * 70)
    print("Example 4: Ecosystem Health Check")
    print("=" * 70)
    
    # Initialize
    db = AsyncDatabaseManager({
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'ubec_main'),
        'user': os.getenv('DB_USER', 'ubec_user'),
        'password': os.getenv('DB_PASSWORD', 'your_password'),
        'port': int(os.getenv('DB_PORT', 5432))
    })
    await db.initialize()
    
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Get ecosystem health
    health = await analytics.get_ecosystem_health()
    
    print(f"\nEcosystem Health Report")
    print(f"Generated: {health.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"📊 Overall Metrics:")
    print(f"  Total Holders: {health.total_holders:,}")
    print(f"  Total Accounts: {health.total_accounts:,}")
    print(f"  Total Transactions: {health.total_transactions:,}")
    print(f"  Total Supply (All Tokens): {health.total_supply_all_tokens:,.2f}")
    
    print(f"\n🔥 Activity Metrics:")
    print(f"  Active in last 24h: {health.active_accounts_24h:,}")
    print(f"  Active in last 7d: {health.active_accounts_7d:,}")
    print(f"  Active in last 30d: {health.active_accounts_30d:,}")
    
    print(f"\n⚖️ Element Balance Score: {health.element_balance_score:.2f}/100")
    if health.element_balance_score >= 75:
        print("  Status: EXCELLENT - Elements are well balanced")
    elif health.element_balance_score >= 50:
        print("  Status: GOOD - Elements are fairly balanced")
    elif health.element_balance_score >= 25:
        print("  Status: FAIR - Some imbalance exists")
    else:
        print("  Status: POOR - Significant imbalance")
    
    # Cleanup
    await analytics.close()
    await db.close()
    
    print("\n✓ Example 4 complete\n")


async def example_compare_all_tokens():
    """Example 5: Compare all 4 tokens"""
    print("=" * 70)
    print("Example 5: Compare All UBEC Tokens")
    print("=" * 70)
    
    # Initialize
    db = AsyncDatabaseManager({
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'ubec_main'),
        'user': os.getenv('DB_USER', 'ubec_user'),
        'password': os.getenv('DB_PASSWORD', 'your_password'),
        'port': int(os.getenv('DB_PORT', 5432))
    })
    await db.initialize()
    
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Compare all tokens
    comparison = await analytics.compare_tokens()
    
    print(f"\nToken Comparison (as of {comparison['timestamp']})\n")
    
    print(f"{'Token':<10} {'Element':<8} {'Holders':>10} {'Supply':>15} {'Avg Balance':>15}")
    print("-" * 70)
    
    for token_code in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
        token_data = comparison['tokens'][token_code]
        print(
            f"{token_code:<10} "
            f"{token_data['element']:<8} "
            f"{token_data['total_holders']:>10,} "
            f"{token_data['total_supply']:>15,.2f} "
            f"{token_data['average_balance']:>15,.2f}"
        )
    
    print("\n📊 Rankings:")
    print(f"\nBy Holders:")
    for rank, item in enumerate(comparison['rankings']['by_holders'], 1):
        print(f"  {rank}. {item['token']}: {item['holders']:,} holders")
    
    print(f"\nBy Supply:")
    for rank, item in enumerate(comparison['rankings']['by_supply'], 1):
        print(f"  {rank}. {item['token']}: {item['supply']:,.2f} tokens")
    
    print(f"\nBy Concentration (Top 10):")
    for rank, item in enumerate(comparison['rankings']['by_concentration'], 1):
        print(f"  {rank}. {item['token']}: {item['concentration']:.2f}%")
    
    print(f"\n🌍 Ecosystem Totals:")
    print(f"  Unique Accounts: {comparison['totals']['unique_accounts']:,}")
    print(f"  Total Supply (All Tokens): {comparison['totals']['total_supply']:,.2f}")
    
    # Cleanup
    await analytics.close()
    await db.close()
    
    print("\n✓ Example 5 complete\n")


async def example_export_analytics():
    """Example 6: Export comprehensive analytics"""
    print("=" * 70)
    print("Example 6: Export Comprehensive Analytics")
    print("=" * 70)
    
    # Initialize
    db = AsyncDatabaseManager({
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'ubec_main'),
        'user': os.getenv('DB_USER', 'ubec_user'),
        'password': os.getenv('DB_PASSWORD', 'your_password'),
        'port': int(os.getenv('DB_PORT', 5432))
    })
    await db.initialize()
    
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Export full analytics summary
    print("\nGenerating comprehensive analytics report...")
    summary = await analytics.export_analytics_summary()
    
    # Save to file
    filename = f"ubec_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"✓ Analytics exported to: {filename}")
    
    # Display summary
    print(f"\nReport Contents:")
    print(f"  • Ecosystem Health Metrics")
    print(f"  • Distribution for {len(summary['token_distributions'])} tokens")
    print(f"  • Holder Concentration Analysis")
    print(f"  • Liquidity Metrics")
    print(f"  • Token Comparison")
    
    # Cleanup
    await analytics.close()
    await db.close()
    
    print("\n✓ Example 6 complete\n")


async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("UBEC ANALYTICS SERVICE - USAGE EXAMPLES")
    print("=" * 70 + "\n")
    
    try:
        # Run examples
        await example_basic_usage()
        await example_holder_analysis()
        await example_identify_whales()
        await example_ecosystem_health()
        await example_compare_all_tokens()
        await example_export_analytics()
        
        print("=" * 70)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
    except AnalyticsException as e:
        print(f"\n❌ Analytics Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        raise


if __name__ == '__main__':
    # Run examples
    asyncio.run(main())
