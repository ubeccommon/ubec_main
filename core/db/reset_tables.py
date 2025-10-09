#!/usr/bin/env python3
# db/reset_tables.py

from connection import DatabaseManager

def reset_ubec_tables():
    """Reset UBEC database tables for fresh synchronization."""
    print("Connecting to database...")
    db = DatabaseManager(schema=os.getenv('UBEC_DB_SCHEMA', 'ubec_main'))
    
    print("Clearing transaction data...")
    db.execute_query("TRUNCATE TABLE ubec_main.transaction_operations CASCADE")
    db.execute_query("TRUNCATE TABLE ubec_main.sync_status CASCADE")
    db.execute_query("TRUNCATE TABLE ubec_main.holder_discovery_history CASCADE")
    db.execute_query("TRUNCATE TABLE ubec_main.holonic_metrics CASCADE")
    
    clear_holders = input("Also clear asset holders? (y/n): ").lower().startswith('y')
    if clear_holders:
        print("Clearing asset holders...")
        db.execute_query("TRUNCATE TABLE ubec_main.asset_holders CASCADE")
    
    print("Reset complete!")

if __name__ == "__main__":
    reset_ubec_tables()
