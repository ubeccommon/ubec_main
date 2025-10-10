#!/usr/bin/env python3
"""
Verification script for Holonic Metrics Migration V8
Tests that the database schema changes are working correctly
Uses the project's existing database connection infrastructure

This project uses the services of Claude and Anthropic PBC.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connection import DatabaseManager, get_connection

def test_database_migration():
    """Test the holonic_metrics table structure after migration."""
    
    print("=" * 60)
    print("HOLONIC METRICS MIGRATION VERIFICATION")
    print("=" * 60)
    print()
    
    try:
        # Use project's database connection
        db = DatabaseManager(schema='ubec_main')
        
        # Test 1: Check columns
        print("TEST 1: Checking table columns...")
        result = db.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'ubec_main' 
            AND table_name = 'holonic_metrics' 
            AND column_name IN ('account_id', 'agent_id')
            ORDER BY column_name;
        """, fetch_all=True)
        
        if result and len(result) == 1 and result[0]['column_name'] == 'account_id':
            print("✅ PASS: Only account_id column exists")
        else:
            print("❌ FAIL: Expected only account_id column")
            for col in result:
                print(f"   Found: {col['column_name']} ({col['data_type']})")
            return False
        
        # Test 2: Check IMMUTABLE function exists
        print("\nTEST 2: Checking extract_date_immutable function...")
        result = db.execute_query("""
            SELECT routine_name, routine_type 
            FROM information_schema.routines 
            WHERE routine_schema = 'ubec_main' 
            AND routine_name = 'extract_date_immutable';
        """, fetch_one=True)
        
        if result:
            print("✅ PASS: extract_date_immutable function exists")
        else:
            print("❌ FAIL: extract_date_immutable function not found")
            return False
        
        # Test 3: Check unique index exists
        print("\nTEST 3: Checking unique index...")
        result = db.execute_query("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE schemaname = 'ubec_main' 
            AND tablename = 'holonic_metrics'
            AND indexname = 'idx_holonic_metrics_account_date_unique';
        """, fetch_one=True)
        
        if result:
            print("✅ PASS: Unique index idx_holonic_metrics_account_date_unique exists")
            print(f"   Definition: {result['indexdef'][:80]}...")
        else:
            print("❌ FAIL: Unique index not found")
            return False
        
        # Test 4: Check foreign key constraint (may or may not exist)
        print("\nTEST 4: Checking foreign key constraint...")
        result = db.execute_query("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_schema = 'ubec_main' 
            AND table_name = 'holonic_metrics'
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name = 'holonic_metrics_account_id_fkey';
        """, fetch_one=True)
        
        if result:
            print("✅ PASS: Foreign key constraint exists")
            print("   Note: This may need to be removed if stellar_accounts is unpopulated")
        else:
            print("ℹ️  INFO: Foreign key constraint not found (this is OK)")
            print("   This is expected if you ran remove_foreign_key_constraint.sql")
        
        # Test 5: Check extract_date_immutable function works
        print("\nTEST 5: Testing extract_date_immutable function...")
        result = db.execute_query("""
            SELECT ubec_main.extract_date_immutable(NOW()::timestamp with time zone) as result;
        """, fetch_one=True)
        
        if result and result['result']:
            print(f"✅ PASS: Function returns date: {result['result']}")
        else:
            print("❌ FAIL: Function did not return expected result")
            return False
        
        # Test 6: Check if we can query holonic_metrics
        print("\nTEST 6: Testing holonic_metrics table accessibility...")
        result = db.execute_query("""
            SELECT COUNT(*) as record_count 
            FROM ubec_main.holonic_metrics;
        """, fetch_one=True)
        
        if result is not None:
            count = result['record_count']
            print(f"✅ PASS: Table accessible, contains {count} records")
            
            if count > 0:
                # Show sample
                sample = db.execute_query("""
                    SELECT 
                        LEFT(account_id, 15) || '...' as account,
                        composite_score,
                        holonic_category,
                        evaluation_date::date as eval_date
                    FROM ubec_main.holonic_metrics
                    ORDER BY evaluation_date DESC
                    LIMIT 3;
                """, fetch_all=True)
                
                if sample:
                    print("\n   Sample records:")
                    for row in sample:
                        print(f"   - {row['account']}: {row['holonic_category']} "
                              f"(score: {row['composite_score']:.3f}, date: {row['eval_date']})")
        else:
            print("❌ FAIL: Could not query table")
            return False
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Migration Status: SUCCESS")
        print()
        print("Schema Summary:")
        print("- Column: account_id (VARCHAR) ✅")
        print("- Function: extract_date_immutable() ✅")
        print("- Unique Index: account_id + date ✅")
        print("- Table Accessible: YES ✅")
        print()
        print("Next Steps:")
        if count == 0:
            print("1. Run holonic evaluator to populate data")
            print("2. python3 -m core.holonic.ubec_holonic_evaluator")
        else:
            print("1. Verify evaluator updates existing records (no duplicates)")
            print("2. Run: python3 -m core.holonic.ubec_holonic_evaluator")
            print("3. Check record count stays the same")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_migration()
    sys.exit(0 if success else 1)
