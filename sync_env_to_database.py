#!/usr/bin/env python3
"""
UBEC Configuration Sync - Environment to Database
==================================================

Securely synchronizes configuration from .env file to database system_settings table.
This provides a single source of truth while maintaining security best practices.

Features:
    - Reads from .env file securely
    - Maps environment variables to database settings
    - Type-aware (string, decimal, integer, boolean, json)
    - Validates Stellar addresses
    - Sensitive data handling (never logs secrets)
    - Idempotent (safe to run multiple times)
    - Dry-run mode for testing
    - Backup existing settings before update

Design Compliance:
    ✅ Principle 4: Single Source of Truth - Database authoritative
    ✅ Principle 5: Strict Async - All database operations async
    ✅ Principle 8: No Duplicate Configuration - Centralized in database
    ✅ Principle 11: Comprehensive Documentation

Security Features:
    - Never logs secret keys or passwords
    - Validates all inputs before database insertion
    - Uses parameterized queries (SQL injection safe)
    - Supports encryption-at-rest (if database configured)
    - Creates audit trail of changes

Usage:
    # Dry run (shows what would be updated)
    python sync_env_to_database.py --dry-run
    
    # Sync all settings
    python sync_env_to_database.py
    
    # Sync specific category
    python sync_env_to_database.py --category network
    python sync_env_to_database.py --category accounts
    
    # Backup before sync
    python sync_env_to_database.py --backup
    
    # Verbose output
    python sync_env_to_database.py --verbose

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 1.0.0
Date: October 17, 2025
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Core imports
from core.db.database_manager import AsyncDatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION MAPPING
# ============================================================================

class ConfigurationMapping:
    """
    Maps environment variables to database settings with type information.
    
    This is the authoritative mapping between .env and system_settings table.
    """
    
    # Setting categories for organized management
    CATEGORIES = {
        'network': 'Stellar Network Configuration',
        'database': 'Database Connection Settings',
        'tokens': 'Token Issuer Addresses',
        'accounts': 'Distribution Account Addresses',
        'tokenomics': 'Token Distribution Rules',
        'operations': 'Operational Parameters',
        'limits': 'Rate Limits and Thresholds',
    }
    
    # Mapping: (env_var, db_key, type, category, description, sensitive)
    MAPPINGS: List[Tuple[str, str, str, str, str, bool]] = [
        # Network Configuration
        ('UBEC_NETWORK', 'network', 'string', 'network', 
         'Stellar network (testnet/mainnet)', False),
        ('HORIZON_URL', 'horizon_url', 'string', 'network',
         'Stellar Horizon API URL', False),
        
        # Token Issuers
        ('UBEC_ISSUER', 'ubec_issuer', 'string', 'tokens',
         'UBEC (Air) token issuer address', False),
        ('UBECrc_ISSUER', 'ubecrc_issuer', 'string', 'tokens',
         'UBECrc (Water) token issuer address', False),
        ('UBECgpi_ISSUER', 'ubecgpi_issuer', 'string', 'tokens',
         'UBECgpi (Earth) token issuer address', False),
        ('UBECtt_ISSUER', 'ubectt_issuer', 'string', 'tokens',
         'UBECtt (Fire) token issuer address', False),
        
        # Token Codes
        ('UBEC_CODE', 'ubec_code', 'string', 'tokens',
         'UBEC token code', False),
        ('UBECrc_CODE', 'ubecrc_code', 'string', 'tokens',
         'UBECrc token code', False),
        ('UBECgpi_CODE', 'ubecgpi_code', 'string', 'tokens',
         'UBECgpi token code', False),
        ('UBECtt_CODE', 'ubectt_code', 'string', 'tokens',
         'UBECtt token code', False),
        
        # Distribution Accounts (Public Keys Only - NO SECRETS!)
        ('GENERAL_PUBLIC_KEY', 'general_account', 'string', 'accounts',
         'General distribution account address', False),
        ('ADMIN_PUBLIC_KEY', 'administration_account', 'string', 'accounts',
         'Administration account address', False),
        ('STEWARD_MGMT_PUBLIC_KEY', 'stewardship_management_account', 'string', 'accounts',
         'Stewardship management account address', False),
        ('STEWARD_INFRA_PUBLIC_KEY', 'stewardship_infrastructure_account', 'string', 'accounts',
         'Stewardship infrastructure account address', False),
        ('STEWARD_LIQUIDITY_PUBLIC_KEY', 'stewardship_liquidity_account', 'string', 'accounts',
         'Stewardship liquidity account address', False),
        
        # Aggregated accounts (for backward compatibility)
        ('ADMIN_PUBLIC_KEY', 'administration_account', 'string', 'accounts',
         'Administration account (duplicate for compatibility)', False),
        ('STEWARD_MGMT_PUBLIC_KEY', 'stewardship_account', 'string', 'accounts',
         'Primary stewardship account (duplicate for compatibility)', False),
        
        # Tokenomics Parameters
        ('ADMIN_TARGET_PCT', 'administration_target', 'float', 'tokenomics',
         'Administration target percentage (0.05 = 5%)', False),
        ('STEWARD_TARGET_PCT', 'stewardship_target', 'float', 'tokenomics',
         'Stewardship target percentage (0.30 = 30%)', False),
        ('REBALANCE_THRESHOLD', 'rebalance_threshold', 'float', 'tokenomics',
         'Rebalance threshold (0.01 = 1%)', False),
        
        # Operational Limits
        ('UBEC_RATE_LIMIT', 'rate_limit', 'float', 'limits',
         'API calls per second limit', False),
        ('UBEC_CACHE_TTL', 'cache_ttl', 'integer', 'operations',
         'Cache time-to-live in seconds', False),
        ('UBEC_MAX_ACCOUNTS', 'max_accounts', 'integer', 'limits',
         'Maximum accounts to process', False),
        ('UBEC_SYNC_DAYS', 'sync_days', 'integer', 'operations',
         'Days of history to sync', False),
        ('UBEC_MONITOR_INTERVAL', 'monitor_interval', 'integer', 'operations',
         'Monitoring interval in seconds', False),
        ('SYNC_LIMIT', 'sync_limit', 'integer', 'limits',
         'Transaction sync batch size', False),
        ('DISCOVER_LIMIT', 'discover_limit', 'integer', 'limits',
         'Account discovery batch size', False),
    ]
    
    # Default values if not in environment
    DEFAULTS = {
        'network': 'testnet',
        'horizon_url': 'https://horizon-testnet.stellar.org',
        'ubec_code': 'UBEC',
        'ubecrc_code': 'UBECrc',
        'ubecgpi_code': 'UBECgpi',
        'ubectt_code': 'UBECtt',
        'administration_target': '0.05',
        'stewardship_target': '0.30',
        'rebalance_threshold': '0.01',
        'rate_limit': '10.0',
        'cache_ttl': '300',
        'max_accounts': '1000',
        'sync_days': '7',
        'monitor_interval': '300',
        'sync_limit': '200',
        'discover_limit': '100',
    }
    
    @classmethod
    def get_mappings_by_category(cls, category: str) -> List[Tuple]:
        """Get all mappings for a specific category."""
        return [m for m in cls.MAPPINGS if m[3] == category]
    
    @classmethod
    def get_env_value(cls, env_var: str, default: Optional[str] = None) -> Optional[str]:
        """Safely get environment variable value."""
        return os.getenv(env_var, default)
    
    @classmethod
    def is_sensitive(cls, db_key: str) -> bool:
        """Check if a setting contains sensitive data."""
        # Settings containing 'secret', 'password', 'key' are sensitive
        sensitive_keywords = ['secret', 'password', 'private']
        return any(keyword in db_key.lower() for keyword in sensitive_keywords)


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_stellar_address(address: str) -> bool:
    """
    Validate Stellar address format.
    
    Args:
        address: Stellar address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not address:
        return False
    
    # Basic validation
    if not address.startswith('G'):
        return False
    
    if len(address) != 56:
        return False
    
    # Could add base32 validation, checksum validation
    # For now, basic format check is sufficient
    
    return True


def convert_value(value: str, value_type: str) -> Any:
    """
    Convert string value to appropriate type.
    
    Args:
        value: String value from environment
        value_type: Target type (string, float, integer, boolean, json)
        
    Returns:
        Converted value
        
    Raises:
        ValueError: If conversion fails
    """
    if value_type == 'string':
        return str(value)
    
    elif value_type == 'float':
        return str(float(value))
    
    elif value_type == 'integer':
        return str(int(value))
    
    elif value_type == 'boolean':
        return str(value.lower() in ('true', 'yes', '1', 'on'))
    
    elif value_type == 'json':
        # Validate JSON and return as string
        parsed = json.loads(value)
        return json.dumps(parsed)
    
    else:
        raise ValueError(f"Unknown value type: {value_type}")


def redact_sensitive_value(value: str) -> str:
    """
    Redact sensitive values for logging.
    
    Args:
        value: Value to redact
        
    Returns:
        Redacted value (first 8 chars + '...')
    """
    if not value or len(value) <= 8:
        return '***'
    
    return value[:8] + '...'


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

async def backup_current_settings(db: AsyncDatabaseManager) -> Dict[str, Any]:
    """
    Backup current settings before making changes.
    
    Args:
        db: Database manager instance
        
    Returns:
        Dict of current settings
    """
    query = """
        SELECT setting_key, setting_value, setting_type, is_active
        FROM system_settings
        ORDER BY setting_key
    """
    
    rows = await db.fetch_all(query)
    
    backup = {
        'timestamp': datetime.now().isoformat(),
        'settings': {row['setting_key']: dict(row) for row in rows}
    }
    
    return backup


async def save_backup_to_file(backup: Dict[str, Any], filename: str = None):
    """
    Save backup to JSON file.
    
    Args:
        backup: Backup data
        filename: Output filename (optional)
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'config_backup_{timestamp}.json'
    
    # Create backups directory
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    filepath = backup_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(backup, f, indent=2, default=str)
    
    logger.info(f"✓ Backup saved to: {filepath}")
    return filepath


async def upsert_setting(
    db: AsyncDatabaseManager,
    key: str,
    value: str,
    value_type: str,
    description: str = None
) -> bool:
    """
    Insert or update a configuration setting.
    
    Args:
        db: Database manager instance
        key: Setting key
        value: Setting value (as string)
        value_type: Type of value
        description: Optional description
        
    Returns:
        True if successful
    """
    query = """
        INSERT INTO system_settings 
            (setting_key, setting_value, setting_type, description, is_active)
        VALUES ($1, $2, $3, $4, true)
        ON CONFLICT (setting_key) DO UPDATE
        SET 
            setting_value = EXCLUDED.setting_value,
            setting_type = EXCLUDED.setting_type,
            description = COALESCE(EXCLUDED.description, system_settings.description),
            updated_at = CURRENT_TIMESTAMP
        RETURNING setting_key
    """
    
    try:
        result = await db.fetch_one(
            query,
            (key, value, value_type, description)
        )
        return result is not None
    
    except Exception as e:
        logger.error(f"Failed to upsert {key}: {e}")
        return False


async def get_current_value(db: AsyncDatabaseManager, key: str) -> Optional[str]:
    """
    Get current value from database.
    
    Args:
        db: Database manager instance
        key: Setting key
        
    Returns:
        Current value or None
    """
    query = """
        SELECT setting_value
        FROM system_settings
        WHERE setting_key = $1 AND is_active = true
    """
    
    result = await db.fetch_one(query, (key,))
    
    if result:
        return result['setting_value']
    
    return None


# ============================================================================
# SYNC OPERATIONS
# ============================================================================

async def sync_configuration(
    db: AsyncDatabaseManager,
    dry_run: bool = False,
    category: str = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Synchronize configuration from .env to database.
    
    Args:
        db: Database manager instance
        dry_run: If True, only show what would be done
        category: Only sync specific category
        verbose: Show detailed output
        
    Returns:
        Sync results dictionary
    """
    results = {
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'category': category,
        'added': [],
        'updated': [],
        'unchanged': [],
        'skipped': [],
        'errors': []
    }
    
    # Filter mappings by category if specified
    mappings = ConfigurationMapping.MAPPINGS
    if category:
        mappings = ConfigurationMapping.get_mappings_by_category(category)
        if not mappings:
            results['errors'].append(f"Unknown category: {category}")
            return results
    
    logger.info(f"Processing {len(mappings)} configuration mappings...")
    
    for env_var, db_key, value_type, cat, description, sensitive in mappings:
        try:
            # Get value from environment
            env_value = ConfigurationMapping.get_env_value(env_var)
            
            # Use default if not in environment
            if env_value is None:
                if db_key in ConfigurationMapping.DEFAULTS:
                    env_value = ConfigurationMapping.DEFAULTS[db_key]
                else:
                    # Skip if no value and no default
                    results['skipped'].append({
                        'key': db_key,
                        'reason': 'Not set in environment and no default'
                    })
                    if verbose:
                        logger.info(f"⊘ Skipped {db_key} (not set)")
                    continue
            
            # Convert and validate value
            try:
                converted_value = convert_value(env_value, value_type)
            except Exception as e:
                results['errors'].append({
                    'key': db_key,
                    'error': f"Conversion failed: {e}"
                })
                logger.error(f"✗ Failed to convert {db_key}: {e}")
                continue
            
            # Additional validation for Stellar addresses
            # Only validate if it's a string type AND ends with 'issuer' or '_account'
            if value_type == 'string' and (db_key.endswith('_issuer') or db_key.endswith('_account')):
                if not validate_stellar_address(converted_value):
                    results['errors'].append({
                        'key': db_key,
                        'error': 'Invalid Stellar address format'
                    })
                    logger.error(f"✗ Invalid Stellar address for {db_key}")
                    continue
            
            # Get current value from database
            current_value = await get_current_value(db, db_key)
            
            # Determine action
            if current_value is None:
                action = 'add'
            elif current_value == converted_value:
                action = 'unchanged'
            else:
                action = 'update'
            
            # Display value (redact if sensitive)
            display_value = (
                redact_sensitive_value(converted_value)
                if sensitive or ConfigurationMapping.is_sensitive(db_key)
                else converted_value
            )
            
            # Log action
            if action == 'add':
                symbol = '+'
                color = 'green'
                results['added'].append({
                    'key': db_key,
                    'value': display_value,
                    'type': value_type
                })
            elif action == 'update':
                symbol = '↻'
                color = 'yellow'
                results['updated'].append({
                    'key': db_key,
                    'old_value': redact_sensitive_value(current_value) if sensitive else current_value,
                    'new_value': display_value,
                    'type': value_type
                })
            else:  # unchanged
                symbol = '='
                color = 'gray'
                results['unchanged'].append({
                    'key': db_key,
                    'value': display_value,
                    'type': value_type
                })
            
            if verbose or action != 'unchanged':
                logger.info(f"{symbol} {db_key}: {display_value} ({value_type})")
            
            # Perform database operation (unless dry run)
            if not dry_run and action != 'unchanged':
                success = await upsert_setting(
                    db, db_key, converted_value, value_type, description
                )
                
                if not success:
                    results['errors'].append({
                        'key': db_key,
                        'error': 'Database operation failed'
                    })
        
        except Exception as e:
            results['errors'].append({
                'key': db_key,
                'error': str(e)
            })
            logger.error(f"✗ Error processing {db_key}: {e}")
    
    return results


# ============================================================================
# REPORTING
# ============================================================================

def print_summary(results: Dict[str, Any]):
    """Print sync results summary."""
    print("\n" + "="*70)
    print("CONFIGURATION SYNC SUMMARY")
    print("="*70)
    
    if results['dry_run']:
        print("⚠  DRY RUN MODE - No changes were made")
    
    if results['category']:
        print(f"📁 Category: {results['category']}")
    
    print(f"🕐 Timestamp: {results['timestamp']}")
    print()
    
    # Counts
    added_count = len(results['added'])
    updated_count = len(results['updated'])
    unchanged_count = len(results['unchanged'])
    skipped_count = len(results['skipped'])
    error_count = len(results['errors'])
    total_count = added_count + updated_count + unchanged_count + skipped_count
    
    print(f"✓ Total processed: {total_count}")
    print(f"  + Added:         {added_count}")
    print(f"  ↻ Updated:       {updated_count}")
    print(f"  = Unchanged:     {unchanged_count}")
    print(f"  ⊘ Skipped:       {skipped_count}")
    if error_count > 0:
        print(f"  ✗ Errors:        {error_count}")
    
    # Show details
    if results['added']:
        print("\n📝 Added Settings:")
        for item in results['added']:
            print(f"  + {item['key']}: {item['value']} ({item['type']})")
    
    if results['updated']:
        print("\n🔄 Updated Settings:")
        for item in results['updated']:
            print(f"  ↻ {item['key']}: {item['old_value']} → {item['new_value']}")
    
    if results['skipped']:
        print("\n⊘ Skipped Settings:")
        for item in results['skipped']:
            print(f"  ⊘ {item['key']}: {item['reason']}")
    
    if results['errors']:
        print("\n❌ Errors:")
        for item in results['errors']:
            print(f"  ✗ {item['key']}: {item['error']}")
    
    print("="*70 + "\n")


# ============================================================================
# CLI
# ============================================================================

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Sync configuration from .env to database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python sync_env_to_database.py --dry-run
  
  # Sync all settings
  python sync_env_to_database.py
  
  # Sync specific category
  python sync_env_to_database.py --category network
  
  # Backup before sync
  python sync_env_to_database.py --backup
  
  # Verbose output
  python sync_env_to_database.py --verbose
  
Categories:
  network      - Stellar network configuration
  database     - Database connection settings
  tokens       - Token issuer addresses
  accounts     - Distribution account addresses
  tokenomics   - Token distribution rules
  operations   - Operational parameters
  limits       - Rate limits and thresholds
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying database'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        choices=list(ConfigurationMapping.CATEGORIES.keys()),
        help='Only sync specific category'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Backup current settings before sync'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output including unchanged settings'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    
    return parser.parse_args()


# ============================================================================
# MAIN
# ============================================================================

async def main_async(args):
    """Async main function."""
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    logger.info("="*70)
    logger.info("UBEC Configuration Sync - Environment to Database")
    logger.info("="*70)
    
    # Get database configuration from environment
    search_path = os.getenv('DB_SEARCH_PATH')
    if search_path:
        schemas = [s.strip() for s in search_path.split(',')]
        schema = ', '.join(schemas)
    else:
        schema = os.getenv('DB_SCHEMA', 'ubec_main')
    
    # Create database connection
    db = AsyncDatabaseManager(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'ubec'),
        schema=schema,
        user=os.getenv('DB_USER', 'ubec_app'),
        password=os.getenv('DB_PASSWORD', '')
    )
    
    try:
        # Initialize database connection pool
        await db.initialize()
        logger.info("✓ Database connection established")
        
        # Backup if requested
        if args.backup:
            logger.info("Creating backup of current settings...")
            backup = await backup_current_settings(db)
            backup_file = await save_backup_to_file(backup)
            logger.info(f"✓ Backup created: {backup_file}")
        
        # Sync configuration
        logger.info("Starting configuration sync...")
        results = await sync_configuration(
            db,
            dry_run=args.dry_run,
            category=args.category,
            verbose=args.verbose
        )
        
        # Print summary
        print_summary(results)
        
        # Success check
        if results['errors']:
            logger.warning(f"⚠  Completed with {len(results['errors'])} errors")
            return 1
        
        if args.dry_run:
            logger.info("✓ Dry run completed successfully")
        else:
            logger.info("✓ Configuration sync completed successfully")
        
        return 0
    
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        return 1
    
    finally:
        # Close database connection pool
        await db.close()
        logger.info("✓ Database connection closed")


def main():
    """Main entry point."""
    args = parse_arguments()
    
    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 0
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
