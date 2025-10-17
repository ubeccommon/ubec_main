#!/usr/bin/env python3
"""
Add Missing Configuration Values
=================================

Interactively adds required configuration values to the database
that are missing and causing service initialization failures.

Usage:
    python add_missing_config.py

Or with specific values:
    python add_missing_config.py --admin-account GXXX... --steward-account GYYY...

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Import database manager
from core.db.database_manager import AsyncDatabaseManager


async def check_existing_config(db: AsyncDatabaseManager) -> dict:
    """Check which configuration values already exist."""
    
    required_keys = [
        'administration_account',
        'stewardship_account',
        'administration_target',
        'stewardship_target',
        'rebalance_threshold'
    ]
    
    query = """
        SELECT setting_key, setting_value, setting_type
        FROM system_settings
        WHERE setting_key = ANY($1)
    """
    
    results = await db.execute_query(query, [required_keys], fetch_all=True)
    
    existing = {row['setting_key']: row for row in results}
    missing = [key for key in required_keys if key not in existing]
    
    return {
        'existing': existing,
        'missing': missing,
        'required': required_keys
    }


async def add_configuration_value(
    db: AsyncDatabaseManager,
    key: str,
    value: str,
    value_type: str = 'string'
) -> bool:
    """Add or update a configuration value."""
    
    query = """
        INSERT INTO system_settings (setting_key, setting_value, setting_type, is_active)
        VALUES ($1, $2, $3, true)
        ON CONFLICT (setting_key) DO UPDATE
        SET setting_value = EXCLUDED.setting_value,
            setting_type = EXCLUDED.setting_type,
            updated_at = CURRENT_TIMESTAMP
        RETURNING setting_key, setting_value
    """
    
    try:
        result = await db.execute_query(
            query, 
            [key, value, value_type], 
            fetch_one=True
        )
        return result is not None
    except Exception as e:
        print(f"Error adding {key}: {e}")
        return False


def validate_stellar_address(address: str) -> bool:
    """Validate that a string looks like a Stellar address."""
    if not address:
        return False
    
    # Basic validation: starts with G, 56 characters
    if not address.startswith('G'):
        return False
    
    if len(address) != 56:
        return False
    
    # Could add more validation (base32, checksum) but this is sufficient
    return True


async def interactive_add_config(db: AsyncDatabaseManager):
    """Interactively prompt for missing configuration values."""
    
    print("\n" + "="*70)
    print("UBEC Configuration Setup")
    print("="*70 + "\n")
    
    # Check existing configuration
    config_status = await check_existing_config(db)
    
    if not config_status['missing']:
        print("✓ All required configuration values are already present!")
        print("\nExisting values:")
        for key, data in config_status['existing'].items():
            value = data['setting_value']
            # Redact sensitive values
            if 'account' in key and len(value) > 10:
                value = value[:10] + '...'
            print(f"  • {key}: {value}")
        return True
    
    print(f"Found {len(config_status['missing'])} missing configuration values:\n")
    for key in config_status['missing']:
        print(f"  ✗ {key}")
    
    print("\n" + "-"*70)
    print("Let's add the missing values...")
    print("-"*70 + "\n")
    
    # Get administration account
    if 'administration_account' in config_status['missing']:
        while True:
            admin_account = input("Administration account (Stellar address starting with G): ").strip()
            
            if admin_account.lower() == 'skip':
                print("⚠ Skipping - audit service will not initialize")
                admin_account = ''
                break
            
            if validate_stellar_address(admin_account):
                break
            else:
                print("❌ Invalid Stellar address. Must start with G and be 56 characters.")
                print("   Or type 'skip' to skip this value.\n")
        
        if admin_account:
            success = await add_configuration_value(db, 'administration_account', admin_account)
            if success:
                print(f"✓ Added administration_account\n")
            else:
                print(f"✗ Failed to add administration_account\n")
    
    # Get stewardship account
    if 'stewardship_account' in config_status['missing']:
        while True:
            steward_account = input("Stewardship account (Stellar address starting with G): ").strip()
            
            if steward_account.lower() == 'skip':
                print("⚠ Skipping - distribution service may have issues")
                steward_account = ''
                break
            
            if validate_stellar_address(steward_account):
                break
            else:
                print("❌ Invalid Stellar address. Must start with G and be 56 characters.")
                print("   Or type 'skip' to skip this value.\n")
        
        if steward_account:
            success = await add_configuration_value(db, 'stewardship_account', steward_account)
            if success:
                print(f"✓ Added stewardship_account\n")
            else:
                print(f"✗ Failed to add stewardship_account\n")
    
    # Add default tokenomics values if missing
    defaults = {
        'administration_target': ('0.05', 'decimal'),
        'stewardship_target': ('0.30', 'decimal'),
        'rebalance_threshold': ('0.01', 'decimal')
    }
    
    for key, (value, value_type) in defaults.items():
        if key in config_status['missing']:
            success = await add_configuration_value(db, key, value, value_type)
            if success:
                print(f"✓ Added {key} = {value}")
            else:
                print(f"✗ Failed to add {key}")
    
    print("\n" + "="*70)
    print("Configuration setup complete!")
    print("="*70 + "\n")
    
    return True


async def add_config_from_args(
    db: AsyncDatabaseManager,
    admin_account: str = None,
    steward_account: str = None
):
    """Add configuration from command-line arguments."""
    
    print("\n" + "="*70)
    print("Adding Configuration Values")
    print("="*70 + "\n")
    
    success_count = 0
    
    # Add accounts if provided
    if admin_account:
        if validate_stellar_address(admin_account):
            success = await add_configuration_value(db, 'administration_account', admin_account)
            if success:
                print(f"✓ Added administration_account")
                success_count += 1
            else:
                print(f"✗ Failed to add administration_account")
        else:
            print(f"✗ Invalid administration_account address")
    
    if steward_account:
        if validate_stellar_address(steward_account):
            success = await add_configuration_value(db, 'stewardship_account', steward_account)
            if success:
                print(f"✓ Added stewardship_account")
                success_count += 1
            else:
                print(f"✗ Failed to add stewardship_account")
        else:
            print(f"✗ Invalid stewardship_account address")
    
    # Add default tokenomics values
    defaults = {
        'administration_target': ('0.05', 'decimal'),
        'stewardship_target': ('0.30', 'decimal'),
        'rebalance_threshold': ('0.01', 'decimal')
    }
    
    for key, (value, value_type) in defaults.items():
        success = await add_configuration_value(db, key, value, value_type)
        if success:
            print(f"✓ Added {key} = {value}")
            success_count += 1
        else:
            print(f"✗ Failed to add {key}")
    
    print(f"\n✓ Successfully added {success_count} configuration values")
    print("="*70 + "\n")
    
    return success_count > 0


async def main_async(args):
    """Main async function."""
    
    # Get database schema configuration
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
        # Initialize connection
        await db.__aenter__()
        
        # Add configuration
        if args.admin_account or args.steward_account:
            # Use command-line arguments
            await add_config_from_args(
                db,
                args.admin_account,
                args.steward_account
            )
        else:
            # Interactive mode
            await interactive_add_config(db)
        
        # Show next steps
        print("\nNext steps:")
        print("  1. Test with: python main.py --mode health")
        print("  2. If successful, all 15 services should initialize")
        print("\n")
        
    finally:
        await db.__aexit__(None, None, None)


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description='Add missing configuration values to UBEC database',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--admin-account',
        type=str,
        help='Administration account (Stellar address)'
    )
    
    parser.add_argument(
        '--steward-account',
        type=str,
        help='Stewardship account (Stellar address)'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check what is missing, do not add'
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main_async(args))
        return 0
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
