#!/usr/bin/env python3
"""
UBEC Database Validation Script
Checks schema integrity, data consistency, and identifies issues

This project uses the services of Claude and Anthropic PBC to inform
our decisions and recommendations.
"""

import sys
import os
from datetime import datetime

# Add project root to path (adjust as needed)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from db.connection import DatabaseManager
except ImportError:
    print("Error: Could not import DatabaseManager")
    print("Please run this script from the project root directory")
    sys.exit(1)


class UBECDatabaseValidator:
    """Validates UBEC database schema and data integrity"""
    
    def __init__(self, schema='ubec_main'):
        self.schema = schema
        self.db = DatabaseManager(schema=schema)
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def log_issue(self, message):
        """Log a critical issue"""
        self.issues.append(f"❌ {message}")
        print(f"❌ ISSUE: {message}")
    
    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(f"⚠️  {message}")
        print(f"⚠️  WARNING: {message}")
    
    def log_success(self, message):
        """Log a success"""
        self.successes.append(f"✅ {message}")
        print(f"✅ {message}")
    
    def check_table_exists(self, table_name):
        """Check if a table exists"""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = %s
            AND table_name = %s
        );
        """
        result = self.db.execute_query(query, [self.schema, table_name], fetch_one=True)
        return result and result.get('exists', False)
    
    def check_column_exists(self, table_name, column_name):
        """Check if a column exists in a table"""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = %s
            AND table_name = %s
            AND column_name = %s
        );
        """
        result = self.db.execute_query(query, [self.schema, table_name, column_name], fetch_one=True)
        return result and result.get('exists', False)
    
    def get_table_row_count(self, table_name):
        """Get row count for a table"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.schema}.{table_name}"
            result = self.db.execute_query(query, fetch_one=True)
            return result['count'] if result else 0
        except Exception as e:
            self.log_issue(f"Could not count rows in {table_name}: {e}")
            return None
    
    def validate_core_tables(self):
        """Validate that core tables exist"""
        print("\n" + "="*60)
        print("VALIDATING CORE TABLES")
        print("="*60)
        
        required_tables = [
            'stellar_accounts',
            'stellar_transactions', 
            'stellar_operations',
            'stellar_effects',
            'ubec_balances',
            'ubec_distributions',
            'ubec_holonic_metrics',
            'ubec_sync_status',
            'ubec_audit_log',
            'ubec_reports'
        ]
        
        for table in required_tables:
            if self.check_table_exists(table):
                row_count = self.get_table_row_count(table)
                if row_count is not None:
                    self.log_success(f"Table {table} exists ({row_count} rows)")
            else:
                self.log_issue(f"Required table {table} does not exist")
    
    def validate_stellar_operations_schema(self):
        """Validate stellar_operations table schema"""
        print("\n" + "="*60)
        print("VALIDATING STELLAR_OPERATIONS SCHEMA")
        print("="*60)
        
        if not self.check_table_exists('stellar_operations'):
            self.log_issue("stellar_operations table does not exist")
            return
        
        required_columns = {
            'operation_id': 'Primary key column',
            'transaction_hash': 'Foreign key to transactions',
            'type': 'Operation type',
            'source_account': 'Operation source',
            'from_account': 'Transfer from account',
            'to_account': 'Transfer to account',
            'amount': 'Transaction amount',
            'asset_code': 'Asset code (UBEC, UBECrc, etc)',
            'asset_issuer': 'Asset issuer public key',
            'created_at': 'Timestamp'
        }
        
        for column, description in required_columns.items():
            if self.check_column_exists('stellar_operations', column):
                self.log_success(f"Column stellar_operations.{column} exists ({description})")
            else:
                self.log_issue(f"Column stellar_operations.{column} missing ({description})")
        
        # Check for columns that should NOT exist
        deprecated_columns = ['destination_account']
        for column in deprecated_columns:
            if self.check_column_exists('stellar_operations', column):
                self.log_warning(f"Deprecated column stellar_operations.{column} still exists")
    
    def validate_transaction_operations_view(self):
        """Check if backward compatibility view exists"""
        print("\n" + "="*60)
        print("CHECKING BACKWARD COMPATIBILITY")
        print("="*60)
        
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.views 
            WHERE table_schema = %s
            AND table_name = 'transaction_operations'
        );
        """
        result = self.db.execute_query(query, [self.schema], fetch_one=True)
        
        if result and result.get('exists', False):
            self.log_success("Backward compatibility view 'transaction_operations' exists")
        else:
            self.log_warning("View 'transaction_operations' does not exist (may cause legacy code issues)")
    
    def validate_data_consistency(self):
        """Validate data consistency across tables"""
        print("\n" + "="*60)
        print("VALIDATING DATA CONSISTENCY")
        print("="*60)
        
        # Check transactions vs operations
        query = """
        SELECT 
            COUNT(DISTINCT t.transaction_hash) as tx_count,
            COUNT(DISTINCT o.transaction_hash) as tx_with_ops,
            COUNT(o.id) as total_ops
        FROM {schema}.stellar_transactions t
        LEFT JOIN {schema}.stellar_operations o ON t.transaction_hash = o.transaction_hash
        """.format(schema=self.schema)
        
        try:
            result = self.db.execute_query(query, fetch_one=True)
            if result:
                tx_count = result['tx_count']
                tx_with_ops = result['tx_with_ops']
                total_ops = result['total_ops']
                
                print(f"\nTransaction-Operation Relationship:")
                print(f"  Total transactions: {tx_count}")
                print(f"  Transactions with operations: {tx_with_ops}")
                print(f"  Total operations: {total_ops}")
                
                if tx_count > 0:
                    ops_per_tx = total_ops / tx_count
                    print(f"  Average operations per transaction: {ops_per_tx:.2f}")
                    
                    if tx_with_ops < tx_count:
                        missing = tx_count - tx_with_ops
                        pct = (missing / tx_count) * 100
                        self.log_warning(f"{missing} transactions ({pct:.1f}%) have no operations")
                    else:
                        self.log_success("All transactions have associated operations")
                        
                    if total_ops < 10:
                        self.log_warning(f"Very few operations in database ({total_ops}). May need to run sync.")
                else:
                    self.log_warning("No transactions in database")
        except Exception as e:
            self.log_issue(f"Could not validate transaction-operation consistency: {e}")
        
        # Check accounts vs balances
        query = """
        SELECT 
            COUNT(DISTINCT sa.account_id) as account_count,
            COUNT(DISTINCT ub.account_id) as accounts_with_balance,
            COUNT(ub.id) as total_balances
        FROM {schema}.stellar_accounts sa
        LEFT JOIN {schema}.ubec_balances ub ON sa.account_id = ub.account_id
        """.format(schema=self.schema)
        
        try:
            result = self.db.execute_query(query, fetch_one=True)
            if result:
                account_count = result['account_count']
                accounts_with_balance = result['accounts_with_balance']
                total_balances = result['total_balances']
                
                print(f"\nAccount-Balance Relationship:")
                print(f"  Total accounts: {account_count}")
                print(f"  Accounts with balances: {accounts_with_balance}")
                print(f"  Total balance records: {total_balances}")
                
                if account_count > 0:
                    if accounts_with_balance < account_count:
                        missing = account_count - accounts_with_balance
                        pct = (missing / account_count) * 100
                        self.log_warning(f"{missing} accounts ({pct:.1f}%) have no balance records")
                    else:
                        self.log_success("All accounts have balance records")
        except Exception as e:
            self.log_issue(f"Could not validate account-balance consistency: {e}")
    
    def validate_ubec_asset_data(self):
        """Validate UBEC-specific asset data"""
        print("\n" + "="*60)
        print("VALIDATING UBEC ASSET DATA")
        print("="*60)
        
        # Check for UBEC operations
        query = """
        SELECT 
            asset_code,
            COUNT(*) as operation_count,
            SUM(amount) as total_amount
        FROM {schema}.stellar_operations
        WHERE asset_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
        GROUP BY asset_code
        """.format(schema=self.schema)
        
        try:
            results = self.db.execute_query(query, fetch_all=True)
            if results:
                print("\nUBEC Token Operations:")
                for row in results:
                    asset = row['asset_code']
                    count = row['operation_count']
                    total = float(row['total_amount']) if row['total_amount'] else 0
                    print(f"  {asset}: {count} operations, {total:,.2f} total")
                    self.log_success(f"Found {count} {asset} operations")
            else:
                self.log_warning("No UBEC token operations found in database")
        except Exception as e:
            self.log_issue(f"Could not validate UBEC asset data: {e}")
    
    def generate_report(self):
        """Generate final validation report"""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Critical Issues: {len(self.issues)}")
        
        if self.issues:
            print("\n" + "="*60)
            print("CRITICAL ISSUES THAT NEED FIXING:")
            print("="*60)
            for issue in self.issues:
                print(issue)
        
        if self.warnings:
            print("\n" + "="*60)
            print("WARNINGS TO REVIEW:")
            print("="*60)
            for warning in self.warnings:
                print(warning)
        
        # Overall status
        print("\n" + "="*60)
        if self.issues:
            print("OVERALL STATUS: ❌ CRITICAL ISSUES DETECTED")
            print("="*60)
            print("Action required: Fix critical issues before running evaluations")
            return False
        elif self.warnings:
            print("OVERALL STATUS: ⚠️  WARNINGS PRESENT")
            print("="*60)
            print("System may work but optimizations recommended")
            return True
        else:
            print("OVERALL STATUS: ✅ ALL VALIDATIONS PASSED")
            print("="*60)
            return True


def main():
    """Run validation"""
    print("="*60)
    print("UBEC DATABASE VALIDATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    try:
        validator = UBECDatabaseValidator()
        
        # Run all validations
        validator.validate_core_tables()
        validator.validate_stellar_operations_schema()
        validator.validate_transaction_operations_view()
        validator.validate_data_consistency()
        validator.validate_ubec_asset_data()
        
        # Generate report
        success = validator.generate_report()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
