#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.connection import DatabaseManager

db = DatabaseManager(schema='ubec_main')

print("\n⚠️  Clearing ALL data...")
print("Press Ctrl+C to cancel, or Enter to continue...")
input()

print("Clearing balances...")
db.execute_query("TRUNCATE ubec_main.ubec_balances CASCADE")

print("Clearing accounts...")
db.execute_query("TRUNCATE ubec_main.stellar_accounts CASCADE")

print("Clearing operations...")
db.execute_query("TRUNCATE ubec_main.stellar_operations CASCADE")

print("Clearing transactions...")
db.execute_query("TRUNCATE ubec_main.stellar_transactions CASCADE")

print("\n✓ Data cleared!")

# Verify
result = db.execute_query("SELECT COUNT(*) FROM ubec_main.stellar_accounts", fetch_one=True)
print(f"Accounts remaining: {result.get('count', result[0] if result else 0)}")
