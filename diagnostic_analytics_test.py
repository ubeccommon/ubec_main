#!/usr/bin/env python3
"""
Diagnostic script to test analytics service SQL queries.

This script will help identify the exact SQL being generated and 
where the syntax error is occurring.
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone

# Simple test to check SQL string generation
def test_sql_generation():
    """Test SQL query string generation."""
    print("=" * 80)
    print("SQL QUERY GENERATION TEST")
    print("=" * 80)
    
    db_schema = "ubec_main"
    
    # Test 1: Accounts query
    print("\nTest 1: Accounts Query")
    print("-" * 40)
    accounts_query = f"""
        SELECT COUNT(DISTINCT account_id) as total
        FROM {db_schema}.ubec_balances
        WHERE balance > 0
    """
    print("Generated SQL:")
    print(accounts_query)
    print(f"Length: {len(accounts_query)} characters")
    print(f"Contains '<': {'<' in accounts_query}")
    print(f"Contains '>': {'>' in accounts_query}")
    
    # Test 2: Active accounts query
    print("\nTest 2: Active Accounts Query")
    print("-" * 40)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    active_query = f"""
        SELECT COUNT(DISTINCT account_id) as active
        FROM (
            SELECT source_account as account_id
            FROM {db_schema}.stellar_operations
            WHERE created_at >= $1
            AND source_account IS NOT NULL
            UNION
            SELECT from_account as account_id
            FROM {db_schema}.stellar_operations
            WHERE created_at >= $1
            AND from_account IS NOT NULL
            UNION
            SELECT to_account as account_id
            FROM {db_schema}.stellar_operations
            WHERE created_at >= $1
            AND to_account IS NOT NULL
        ) combined
    """
    print("Generated SQL:")
    print(active_query)
    print(f"Length: {len(active_query)} characters")
    print(f"Contains '<': {'<' in active_query}")
    print(f"Contains '>': {'>' in active_query}")
    print(f"Parameter: {thirty_days_ago}")
    
    print("\n" + "=" * 80)
    print("If you see '<' in the accounts_query, that's the problem!")
    print("The query should only contain '>' in 'balance > 0'")
    print("=" * 80)


async def test_with_actual_service():
    """Test with the actual analytics service if available."""
    print("\n" + "=" * 80)
    print("ACTUAL SERVICE TEST")
    print("=" * 80)
    
    try:
        # Try to import the analytics service
        sys.path.insert(0, '/home/triag/UBEC/projects/UBEC')
        from services.analytics.ubec_analytics_service import UBECAnalyticsService
        from core.db.database_manager import AsyncDatabaseManager
        
        print("\n✅ Successfully imported UBECAnalyticsService")
        
        # Create a mock database manager
        class MockDBManager:
            async def fetch_one(self, query, params):
                print("\n" + "=" * 80)
                print("INTERCEPTED SQL QUERY:")
                print("=" * 80)
                print(query)
                print("\nParameters:", params)
                print("=" * 80)
                # Raise an exception to prevent actual execution
                raise Exception("Mock database - query intercepted for inspection")
        
        # Create service instance
        mock_db = MockDBManager()
        analytics = UBECAnalyticsService(mock_db, "ubec_main")
        
        print(f"\n✅ Analytics service created")
        print(f"   - Schema: {analytics.db_schema}")
        print(f"   - Schema type: {type(analytics.db_schema)}")
        print(f"   - Schema repr: {repr(analytics.db_schema)}")
        
        # Try to call get_ecosystem_health (will fail but show us the query)
        print("\n⏳ Attempting to call get_ecosystem_health() to see actual SQL...")
        try:
            await analytics.get_ecosystem_health()
        except Exception as e:
            print(f"\n✅ Expected error (mock database): {e}")
        
    except ImportError as e:
        print(f"\n❌ Could not import service: {e}")
        print("   This test requires access to the UBEC project files")
    except Exception as e:
        print(f"\n⚠️  Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\nUBEC Analytics Service - SQL Diagnostic Test")
    print("=" * 80)
    
    # Test 1: Basic SQL generation
    test_sql_generation()
    
    # Test 2: With actual service (if available)
    try:
        asyncio.run(test_with_actual_service())
    except Exception as e:
        print(f"\n⚠️  Could not run service test: {e}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print("\nIf the SQL looks correct above but still fails in production,")
    print("the issue may be with:")
    print("  1. The actual file deployed is different from what was uploaded")
    print("  2. Python bytecode cache needs to be cleared")
    print("  3. The database connection is altering the query somehow")
    print("=" * 80)
