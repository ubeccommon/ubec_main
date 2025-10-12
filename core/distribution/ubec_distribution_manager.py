#!/usr/bin/env python3
# core/distribution/ubec_distribution_manager.py
"""
UBEC Distribution Manager

Manages the automatic balancing of UBEC token distribution according to 
the tokenomics defined in the Ubuntu Economic Commons whitepaper.

This module uses PostgreSQL database for data persistence and tracking
while maintaining compatibility with the Stellar blockchain for transactions.

Updated: 2025-10-09
- Fixed check_compliance() to accept asset_code and asset_issuer parameters
- Fixed snapshot_distribution() to accept asset_code and asset_issuer parameters
- Fixed schema references to use environment variables
- Fixed DatabaseManager compatibility
- Added proper error handling
"""

import os
import sys
import time
import logging
import json
from decimal import Decimal, getcontext
from pathlib import Path
from datetime import datetime, timedelta

print("Starting UBEC Distribution Manager...")
print(f"Current working directory: {os.getcwd()}")

# Check for .env file
env_path = Path('.env')
if env_path.exists():
    print(f".env file found at {env_path.absolute()}")
else:
    print(f"ERROR: .env file not found at {env_path.absolute()}")
    print("Please create a .env file with your secret keys")
    sys.exit(1)

# Check for config directory and settings.py
config_path = Path('config/settings.py')
if config_path.exists():
    print(f"settings.py found at {config_path.absolute()}")
else:
    print(f"ERROR: settings.py not found at {config_path.absolute()}")
    sys.exit(1)

# Check for dependencies
try:
    import requests
    from dotenv import load_dotenv
    from stellar_sdk import Server, TransactionBuilder, Network, Keypair, Asset
    from stellar_sdk.exceptions import NotFoundError, BadRequestError
    print("All required packages are installed")
except ImportError as e:
    print(f"ERROR: Missing required package: {e}")
    print("Please install required packages with: pip install stellar-sdk python-dotenv requests")
    sys.exit(1)

# Import the database connection module
try:
    from db.connection import DatabaseManager
    print("Successfully imported database connection module")
except ImportError as e:
    print(f"ERROR: Could not import database connection module: {e}")
    print("Make sure the db module is in the correct location")
    sys.exit(1)

# Import the UBECTokenAudit class
try:
    from core.audit.ubec_token_audit import UBECTokenAudit
    print("Successfully imported UBECTokenAudit module")
except ImportError as e:
    print(f"ERROR: Could not import UBECTokenAudit module: {e}")
    print("Make sure the audit module is in the correct location")
    sys.exit(1)

# Load environment variables
try:
    load_dotenv()
    print("Loaded environment variables from .env file")
    
    # Check if required environment variables exist
    required_env_vars = [
        'GENERAL_SECRET_KEY',
        'ADMIN_SECRET_KEY',
        'STEWARD_MGMT_SECRET_KEY',
        'STEWARD_INFRA_SECRET_KEY',
        'STEWARD_LIQUIDITY_SECRET_KEY'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    else:
        print("All required environment variables are present")
        
except Exception as e:
    print(f"ERROR loading environment variables: {e}")
    sys.exit(1)

# Import settings from config folder
try:
    from config import settings
    print("Successfully imported settings from config folder")
except ImportError as e:
    print(f"ERROR importing settings: {e}")
    print("Make sure you have a config/settings.py file and that config/__init__.py exists")
    sys.exit(1)

# Configure precision for decimal calculations
getcontext().prec = 10

# Set up logging to both file and console
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class UBECDistributionManager:
    """
    Manages the automatic balancing of UBEC token distribution according to 
    the tokenomics defined in the Ubuntu Economic Commons whitepaper.
    
    This version uses the PostgreSQL database for data persistence and
    tracking while maintaining compatibility with the Stellar blockchain for transactions.
    """
    
    def __init__(self, data_source="hybrid"):
        """
        Initialize the distribution manager using database and Stellar.
        
        Args:
            data_source: Source of data - "db" (database only), "stellar" (Stellar API only), 
                         or "hybrid" (try database first, fall back to Stellar)
        """
        logger.info("Initializing UBEC Distribution Manager")
        
        # Set data source preference
        self.data_source = data_source
        logger.info(f"Using {data_source} as data source")
        
        # Get schema from environment
        self.db_schema = os.getenv('UBEC_DB_SCHEMA', 'ubec_main')
        
        # Initialize database connection
        if self.data_source != "stellar":
            try:
                self.db = DatabaseManager(schema=self.db_schema)
                logger.info(f"Successfully connected to database (schema: {self.db_schema})")
            except Exception as e:
                logger.error(f"Error connecting to database: {e}")
                if self.data_source == "db":
                    raise
                else:
                    logger.warning("Falling back to Stellar API only due to database connection error")
                    self.data_source = "stellar"
        
        # Set up Stellar network connection
        self.network = Network.PUBLIC_NETWORK_PASSPHRASE
        self.server = Server(horizon_url=settings.HORIZON_URL)
        self.check_interval = settings.CHECK_INTERVAL
        
        # Set up UBEC asset
        self.ubec_issuer = settings.UBEC_ISSUER
        self.ubec_code = settings.UBEC_CODE
        self.ubec_asset = Asset(settings.UBEC_CODE, self.ubec_issuer)
        
        # Load account information
        self.accounts = settings.ACCOUNTS
        self.target_distribution = settings.TARGET_DISTRIBUTION
        self.rebalance_threshold = settings.REBALANCE_THRESHOLD
        
        # Load secret keys from environment variables
        self.secret_keys = {
            'general': os.getenv('GENERAL_SECRET_KEY'),
            'administration': os.getenv('ADMIN_SECRET_KEY'),
            'stewardship': [
                os.getenv('STEWARD_MGMT_SECRET_KEY'),
                os.getenv('STEWARD_INFRA_SECRET_KEY'),
                os.getenv('STEWARD_LIQUIDITY_SECRET_KEY')
            ]
        }
        
        # Validate that we have all the required secret keys
        self._validate_secret_keys()
        
        # Initialize the UBECTokenAudit module for analysis
        self.auditor = UBECTokenAudit(data_source=data_source)
        
        # Use the auditor to get the total supply
        self.total_supply = Decimal(self.auditor.total_supply)
        logger.info(f"Using total supply of {self.total_supply} UBEC from auditor")
        
        logger.info("UBEC Distribution Manager initialized successfully")
    
    def _validate_secret_keys(self):
        """
        Verify that all required secret keys are available from environment variables.
        """
        missing_keys = []
        
        if not self.secret_keys['general']:
            missing_keys.append('GENERAL_SECRET_KEY')
        
        if not self.secret_keys['administration']:
            missing_keys.append('ADMIN_SECRET_KEY')
        
        for i, key in enumerate(self.secret_keys['stewardship']):
            if not key:
                if i == 0:
                    missing_keys.append('STEWARD_MGMT_SECRET_KEY')
                elif i == 1:
                    missing_keys.append('STEWARD_INFRA_SECRET_KEY')
                elif i == 2:
                    missing_keys.append('STEWARD_LIQUIDITY_SECRET_KEY')
        
        if missing_keys:
            missing_keys_str = ', '.join(missing_keys)
            error_msg = f"Missing required environment variables: {missing_keys_str}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_stewardship_balances(self):
        """
        Get detailed balance information for each stewardship account.
        
        Returns:
            dict: Information about each stewardship account's balance and total
        """
        logger.info("Getting stewardship balances")
        
        balances = []
        total_direct_balance = Decimal('0')
        
        # Try database first if not stellar-only mode
        if self.data_source != "stellar":
            try:
                # Query stewardship account balances from database
                for i, address in enumerate(self.accounts['stewardship']):
                    account_label = ["Management", "Infrastructure", "Liquidity"][i] if i < 3 else f"Account {i}"
                    
                    # Get balance from database
                    query = f"""
                    SELECT balance FROM {self.db_schema}.asset_holders 
                    WHERE account_id = %s AND asset_code = %s AND asset_issuer = %s
                    """
                    result = self.db.execute_query(query, 
                                                 [address, self.ubec_code, self.ubec_issuer])
                    
                    if result and len(result) > 0:
                        balance = Decimal(result[0]['balance'])
                    else:
                        # If not found in database, get from auditor
                        balance = self.auditor.get_account_balance(address)
                    
                    balances.append({
                        'index': i,
                        'address': address,
                        'label': account_label,
                        'balance': balance
                    })
                    total_direct_balance += balance
                    
                # Sort by balance (highest first)
                balances.sort(key=lambda x: x['balance'], reverse=True)
                
                # Log detailed stewardship account information
                for acct in balances:
                    percent = (acct['balance'] / total_direct_balance * 100) if total_direct_balance > 0 else 0
                    logger.info(f"Stewardship {acct['label']} Account ({acct['address']}): {acct['balance']} UBEC ({percent:.2f}%)")
                
                return {
                    'accounts': balances,
                    'total_direct': total_direct_balance
                }
                
            except Exception as e:
                logger.error(f"Database error getting stewardship balances: {e}")
                if self.data_source == "db":
                    raise
                logger.warning("Falling back to auditor for stewardship balances")
        
        # If we couldn't get from database or in stellar-only mode, use the auditor
        try:
            return self.auditor.get_stewardship_balances()
        except Exception as e:
            logger.error(f"Error getting stewardship balances from auditor: {e}")
            
            # Fall back to direct calculation if auditor fails
            for i, address in enumerate(self.accounts['stewardship']):
                account_label = ["Management", "Infrastructure", "Liquidity"][i] if i < 3 else f"Account {i}"
                
                try:
                    # Get balance directly from Stellar
                    account = self.server.accounts().account_id(address).call()
                    
                    balance = Decimal('0')
                    for bal in account['balances']:
                        if (bal.get('asset_type') == 'credit_alphanum4' and 
                            bal.get('asset_code') == self.ubec_code and 
                            bal.get('asset_issuer') == self.ubec_issuer):
                            balance = Decimal(bal['balance'])
                            break
                except Exception as e:
                    logger.error(f"Error getting balance for {address}: {e}")
                    balance = Decimal('0')
                
                balances.append({
                    'index': i,
                    'address': address,
                    'label': account_label,
                    'balance': balance
                })
                total_direct_balance += balance
            
            # Sort by balance (highest first)
            balances.sort(key=lambda x: x['balance'], reverse=True)
            
            return {
                'accounts': balances,
                'total_direct': total_direct_balance
            }
    
    def select_stewardship_account_for_transfer(self, amount, is_source=True):
        """
        Select the best stewardship account to use for a transfer.
        
        Args:
            amount: The amount to transfer
            is_source: True if this account is the source of funds, False if destination
            
        Returns:
            tuple: (account_address, secret_key, available_balance)
        """
        # Get all stewardship account balances
        stewardship_info = self.get_stewardship_balances()
        
        if is_source:
            # When sending funds, find the account with sufficient balance
            for acct in stewardship_info['accounts']:
                if acct['balance'] >= amount:
                    logger.info(f"Selected Stewardship {acct['label']} Account for sending {amount} UBEC")
                    return (
                        acct['address'],
                        self.secret_keys['stewardship'][acct['index']],
                        acct['balance']
                    )
            
            # If no single account has enough, use the one with highest balance
            if stewardship_info['accounts'] and stewardship_info['accounts'][0]['balance'] > 0:
                best_acct = stewardship_info['accounts'][0]
                logger.warning(f"No single stewardship account has sufficient balance. Using {best_acct['label']} Account with {best_acct['balance']} UBEC")
                return (
                    best_acct['address'],
                    self.secret_keys['stewardship'][best_acct['index']],
                    best_acct['balance']
                )
        else:
            # When receiving funds, prefer the Management Account (index 0) if available
            management_acct = next((acct for acct in stewardship_info['accounts'] if acct['index'] == 0), None)
            
            if management_acct:
                logger.info(f"Selected Stewardship Management Account for receiving funds")
                return (
                    management_acct['address'],
                    self.secret_keys['stewardship'][0],
                    management_acct['balance']
                )
        
        # Default to Management Account (index 0)
        logger.info("Defaulting to Stewardship Management Account")
        return (
            self.accounts['stewardship'][0],
            self.secret_keys['stewardship'][0],
            self.auditor.get_account_balance(self.accounts['stewardship'][0])
        )
    
    def check_compliance(self, asset_code=None, asset_issuer=None):
        """
        Check if current distribution meets the target percentages.
        
        Args:
            asset_code: Optional asset code to check (defaults to UBEC)
            asset_issuer: Optional asset issuer (defaults to UBEC issuer)
        
        Returns:
            dict: Compliance status with details
        """
        # Use instance defaults if not provided
        if asset_code is None:
            asset_code = self.ubec_code
        if asset_issuer is None:
            asset_issuer = self.ubec_issuer
            
        try:
            audit_report = self.auditor.perform_audit()
            
            compliance_status = {
                'overall': audit_report.get('tokenomics_compliance', {}).get('overall', False),
                'administration': audit_report.get('tokenomics_compliance', {}).get('administration', False),
                'stewardship': audit_report.get('tokenomics_compliance', {}).get('stewardship', False),
                'details': audit_report.get('tokenomics_compliance', {}),
                'asset_code': asset_code,
                'asset_issuer': asset_issuer
            }
            
            logger.info(f"Compliance check for {asset_code}: Overall={compliance_status['overall']}, "
                       f"Administration={compliance_status['administration']}, "
                       f"Stewardship={compliance_status['stewardship']}")
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            return {
                'overall': False,
                'error': str(e),
                'asset_code': asset_code,
                'asset_issuer': asset_issuer
            }
    
    def snapshot_distribution(self, asset_code=None, asset_issuer=None):
        """
        Create a snapshot of the current distribution in the database.
        
        Args:
            asset_code: Optional asset code to snapshot (defaults to UBEC)
            asset_issuer: Optional asset issuer (defaults to UBEC issuer)
        
        Returns:
            int: ID of the created snapshot, or None if failed
        """
        # Use instance defaults if not provided
        if asset_code is None:
            asset_code = self.ubec_code
        if asset_issuer is None:
            asset_issuer = self.ubec_issuer
            
        if self.data_source == "stellar":
            logger.warning("Database not available for snapshot")
            return None
        
        try:
            # Get current distribution from auditor
            audit_report = self.auditor.perform_audit()
            
            # Extract balances
            general_balance = Decimal(audit_report.get('monitored_supply', {}).get('general', 0))
            admin_balance = Decimal(audit_report.get('monitored_supply', {}).get('administration', 0))
            stewardship_balance = Decimal(audit_report.get('monitored_supply', {}).get('stewardship', 0))
            
            # Check if rebalance is needed
            compliance = self.check_compliance(asset_code, asset_issuer)
            rebalance_needed = not compliance.get('overall', True)
            
            # Record in database using helper function
            query = f"""
            SELECT {self.db_schema}.record_distribution_check(
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            result = self.db.execute_query(
                query,
                [
                    asset_code,
                    asset_issuer,
                    float(general_balance),
                    float(admin_balance),
                    float(stewardship_balance),
                    float(self.total_supply),
                    rebalance_needed,
                    json.dumps(audit_report.get('distribution', {}))
                ]
            )
            
            if result and len(result) > 0:
                snapshot_id = result[0]['record_distribution_check']
                logger.info(f"Created distribution snapshot with ID: {snapshot_id} for {asset_code}")
                return snapshot_id
            else:
                logger.warning(f"Could not create distribution snapshot for {asset_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating distribution snapshot: {e}")
            return None
    
    def is_rebalance_needed(self):
        """
        Check if rebalancing is needed based on current distribution vs target.
        
        Returns:
            tuple: (bool: True if rebalancing needed, dict: current distribution percentages)
        """
        # If database is available, check for pending transfers first
        if self.data_source != "stellar":
            try:
                # Check if there are any pending transfers that should be processed first
                query = f"""
                SELECT COUNT(*) as count FROM {self.db_schema}.transfer_recommendations
                WHERE status = 'pending' AND asset_code = %s AND asset_issuer = %s
                """
                result = self.db.execute_query(query, [self.ubec_code, self.ubec_issuer])
                
                if result and len(result) > 0 and result[0]['count'] > 0:
                    logger.info(f"Found {result[0]['count']} pending transfers in database, rebalance needed")
                    # Get current distribution for reference
                    audit_report = self.auditor.perform_audit()
                    current_distribution = {
                        'general': Decimal(audit_report['distribution']['current']['general']),
                        'administration': Decimal(audit_report['distribution']['current']['administration']),
                        'stewardship': Decimal(audit_report['distribution']['current']['stewardship'])
                    }
                    return True, current_distribution
            except Exception as e:
                logger.error(f"Error checking pending transfers: {e}")
        
        # Use the auditor to perform a complete audit
        audit_report = self.auditor.perform_audit()
        
        # Extract the current distribution from the audit report
        current_distribution = {
            'general': Decimal(audit_report['distribution']['current']['general']),
            'administration': Decimal(audit_report['distribution']['current']['administration']),
            'stewardship': Decimal(audit_report['distribution']['current']['stewardship'])
        }
        
        # Also get the total supply distribution percentages
        supply_distribution = {
            'administration': Decimal(audit_report['distribution']['of_total_supply']['administration']),
            'stewardship': Decimal(audit_report['distribution']['of_total_supply']['stewardship'])
        }
        
        # Log the current distribution
        logger.info(f"Current distribution (of monitored): General={current_distribution['general']:.2%}, "
                   f"Stewardship={current_distribution['stewardship']:.2%}, "
                   f"Administration={current_distribution['administration']:.2%}")
        
        logger.info(f"Current distribution (of total supply): "
                   f"Stewardship={supply_distribution['stewardship']:.2%}, "
                   f"Administration={supply_distribution['administration']:.2%}")
        
        # Check if any category deviates by more than the threshold
        for category in ['administration', 'stewardship']:
            deviation = abs(supply_distribution[category] - Decimal(self.target_distribution[category]))
            if deviation > self.rebalance_threshold:
                logger.info(f"Rebalance needed: {category} deviation is {deviation:.2%}")
                return True, current_distribution
        
        logger.info("No rebalance needed, distribution within thresholds")
        return False, current_distribution
    
    def _update_transfer_status(self, transfer_id, status, message=None):
        """
        Update the status of a transfer recommendation in the database.
        
        Args:
            transfer_id: ID of the transfer recommendation
            status: New status ('completed', 'failed', etc.)
            message: Optional status message
            
        Returns:
            bool: True if successful
        """
        try:
            # Update with status message
            update_query = f"""
            UPDATE {self.db_schema}.transfer_recommendations
            SET status = %s, 
                status_message = %s,
                updated_at = NOW()
            WHERE id = %s
            """
            self.db.execute_query(update_query, [status, message, transfer_id])
            
            return True
        except Exception as e:
            logger.error(f"Error updating transfer status: {e}")
            return False
    
    def perform_rebalance(self):
        """
        Execute transactions to rebalance UBEC token distribution using the 
        recommendations from the audit module.
        """
        logger.info("Starting rebalance operation")
        
        # Look for pending transfers in the database first
        transfers = []
        if self.data_source != "stellar":
            try:
                # Check for pending transfers
                query = f"""
                SELECT id, from_account_type as "from", to_account_type as "to", 
                       amount, priority, created_at
                FROM {self.db_schema}.transfer_recommendations
                WHERE status = 'pending' AND asset_code = %s AND asset_issuer = %s
                ORDER BY priority DESC, created_at ASC
                """
                db_transfers = self.db.execute_query(query, [self.ubec_code, self.ubec_issuer])
                
                if db_transfers:
                    logger.info(f"Found {len(db_transfers)} pending transfers in database")
                    
                    # Process stored transfers
                    for transfer in db_transfers:
                        transfers.append({
                            "id": transfer['id'],
                            "from": transfer['from'],
                            "to": transfer['to'],
                            "amount": transfer['amount'],
                            "source": "database"
                        })
            except Exception as e:
                logger.error(f"Error getting pending transfers from database: {e}")
        
        # If no transfers from database, use the auditor
        if not transfers:
            # Use the auditor to get transfer recommendations
            self.auditor.perform_audit()
            
            # Check if the distribution is already compliant
            if self.auditor.audit_report.get("tokenomics_compliance", {}).get("overall", False):
                logger.info("Token distribution is already compliant, no transfers needed")
                return
            
            # Get transfer recommendations
            self.auditor.add_transfer_recommendations()
            auditor_transfers = self.auditor.audit_report.get("transfer_recommendations", {}).get("transfers", [])
            
            if not auditor_transfers:
                logger.info("No transfers recommended by the auditor")
                return
            
            for transfer in auditor_transfers:
                transfers.append({
                    "from": transfer['from'],
                    "to": transfer['to'],
                    "amount": transfer['amount'],
                    "source": "auditor"
                })
        
        # Log the proposed transfers
        for transfer in transfers:
            logger.info(f"Planning transfer: {transfer['amount']} UBEC from "
                       f"{transfer['from']} to {transfer['to']}")
        
        # Execute the transfers
        for transfer in transfers:
            try:
                from_category = transfer['from']
                to_category = transfer['to']
                amount = Decimal(transfer['amount'])
                
                # Determine the source account based on category
                if from_category == 'general':
                    source_account = self.accounts['general']
                    source_secret = self.secret_keys['general']
                    available_balance = self.auditor.get_account_balance(source_account)
                    source_label = "General Distribution"
                elif from_category == 'administration':
                    source_account = self.accounts['administration']
                    source_secret = self.secret_keys['administration']
                    available_balance = self.auditor.get_account_balance(source_account)
                    source_label = "Administration"
                else:  # stewardship
                    source_account, source_secret, available_balance = self.select_stewardship_account_for_transfer(amount, is_source=True)
                    source_label = f"Stewardship ({source_account})"
                
                # Ensure we have enough balance
                buffer = Decimal('0.1')
                if available_balance < (amount + buffer):
                    logger.warning(f"Insufficient balance in {source_label}. "
                                 f"Needed: {amount}, Available: {available_balance}")
                    
                    if available_balance > buffer:
                        adjusted_amount = available_balance - buffer
                        logger.info(f"Adjusting transfer amount from {amount} to {adjusted_amount}")
                        amount = adjusted_amount
                    else:
                        logger.error(f"Skipping transfer due to insufficient funds")
                        
                        if self.data_source != "stellar" and "id" in transfer and transfer["source"] == "database":
                            self._update_transfer_status(
                                transfer["id"], 
                                'failed', 
                                f"Insufficient funds: {available_balance} available, {amount} needed"
                            )
                        
                        continue
                
                # Validate positive amount
                if amount <= 0:
                    logger.warning(f"Transfer amount {amount} is not positive. Skipping.")
                    
                    if self.data_source != "stellar" and "id" in transfer and transfer["source"] == "database":
                        self._update_transfer_status(
                            transfer["id"], 
                            'failed', 
                            'Transfer amount must be positive'
                        )
                    
                    continue
                
                # Determine destination account
                if to_category == 'general':
                    destination_account = self.accounts['general']
                    destination_label = "General Distribution"
                elif to_category == 'administration':
                    destination_account = self.accounts['administration']
                    destination_label = "Administration"
                else:  # stewardship
                    destination_account, _, _ = self.select_stewardship_account_for_transfer(amount, is_source=False)
                    destination_label = f"Stewardship ({destination_account})"
                
                logger.info(f"Executing transfer: {amount} UBEC from {source_label} to {destination_label}")
                
                # Execute the transfer
                try:
                    tx_hash = self._execute_stellar_transfer(
                        source_account, 
                        source_secret,
                        destination_account, 
                        amount,
                        source_label, 
                        destination_label
                    )
                    
                    # Update transfer status in database
                    if self.data_source != "stellar" and "id" in transfer and transfer["source"] == "database":
                        self._update_transfer_status(
                            transfer["id"],
                            'completed',
                            f"Transaction completed with hash: {tx_hash}"
                        )
                        
                        # Update additional fields
                        try:
                            update_query = f"""
                            UPDATE {self.db_schema}.transfer_recommendations
                            SET transaction_hash = %s,
                                actual_amount = %s,
                                completed_at = NOW()
                            WHERE id = %s
                            """
                            self.db.execute_query(update_query, [tx_hash, str(amount), transfer["id"]])
                        except Exception as e:
                            logger.error(f"Error updating transaction details: {e}")
                
                except Exception as e:
                    logger.error(f"Error executing transfer: {e}")
                    
                    if self.data_source != "stellar" and "id" in transfer and transfer["source"] == "database":
                        self._update_transfer_status(
                            transfer["id"],
                            'failed',
                            str(e)[:255]
                        )
                            
            except Exception as e:
                logger.error(f"Error preparing transfer: {str(e)}")
        
        # After transfers, verify new distribution
        logger.info("Running post-transfer audit to verify new distribution")
        post_audit = self.auditor.perform_audit()
        
        new_distribution = {
            'general': Decimal(post_audit['distribution']['current']['general']),
            'administration': Decimal(post_audit['distribution']['current']['administration']),
            'stewardship': Decimal(post_audit['distribution']['current']['stewardship'])
        }
        
        logger.info(f"Distribution after rebalancing: General={new_distribution['general']:.2%}, "
                   f"Stewardship={new_distribution['stewardship']:.2%}, "
                   f"Administration={new_distribution['administration']:.2%}")
    
    def _execute_stellar_transfer(self, source_account, source_secret, destination_account, amount, source_label, destination_label):
        """
        Execute a transfer on the Stellar blockchain and record it in the database.
        
        Args:
            source_account: Source account address
            source_secret: Secret key for the source account
            destination_account: Destination account address
            amount: Amount to transfer
            source_label: Label for the source account (for logging)
            destination_label: Label for the destination account (for logging)
            
        Returns:
            str: Transaction hash if successful
        """
        source_keypair = Keypair.from_secret(source_secret)
        
        try:
            # Get the source account
            source_account_obj = self.server.load_account(source_keypair.public_key)
            
            # Build the transaction
            transaction = (
                TransactionBuilder(
                    source_account=source_account_obj,
                    network_passphrase=self.network,
                    base_fee=100
                )
                .append_payment_op(
                    destination=destination_account,
                    asset=self.ubec_asset,
                    amount=str(amount)
                )
                .set_timeout(30)
                .build()
            )
            
            # Sign the transaction
            transaction.sign(source_keypair)
            
            # Submit the transaction
            response = self.server.submit_transaction(transaction)
            
            # Record the transfer in the database if available
            if self.data_source != "stellar":
                try:
                    self._record_transfer_in_database(
                        source_account,
                        destination_account,
                        amount,
                        response['hash'],
                        source_label,
                        destination_label
                    )
                except Exception as e:
                    logger.error(f"Error recording transfer in database: {e}")
            
            logger.info(f"Transfer completed: {amount} UBEC from {source_label} "
                       f"to {destination_label}, hash: {response['hash']}")
            
            return response['hash']
            
        except BadRequestError as e:
            error_data = getattr(e, 'extras', {}).get('result_codes', {})
            op_errors = error_data.get('operations', [])
            
            if 'op_underfunded' in op_errors:
                logger.error(f"Underfunded error: {e}")
                
                # Try again with 80% of the amount
                try:
                    reduced_amount = amount * Decimal('0.8')
                    logger.info(f"Retrying with reduced amount: {reduced_amount}")
                    
                    # Reload the account
                    source_account_obj = self.server.load_account(source_keypair.public_key)
                    
                    # Build new transaction with reduced amount
                    transaction = (
                        TransactionBuilder(
                            source_account=source_account_obj,
                            network_passphrase=self.network,
                            base_fee=100
                        )
                        .append_payment_op(
                            destination=destination_account,
                            asset=self.ubec_asset,
                            amount=str(reduced_amount)
                        )
                        .set_timeout(30)
                        .build()
                    )
                    
                    transaction.sign(source_keypair)
                    response = self.server.submit_transaction(transaction)
                    
                    # Record in database
                    if self.data_source != "stellar":
                        try:
                            self._record_transfer_in_database(
                                source_account,
                                destination_account,
                                reduced_amount,
                                response['hash'],
                                source_label,
                                destination_label
                            )
                        except Exception as e:
                            logger.error(f"Error recording reduced transfer: {e}")
                    
                    logger.info(f"Reduced transfer completed: {reduced_amount} UBEC")
                    return response['hash']
                    
                except Exception as retry_e:
                    logger.error(f"Failed on retry: {retry_e}")
                    raise
            else:
                logger.error(f"Transaction failed: {e}")
                raise
        except Exception as e:
            logger.error(f"Error executing transfer: {str(e)}")
            raise
    
    def _record_transfer_in_database(self, source, destination, amount, tx_hash, source_label, destination_label):
        """
        Record the transfer in the database for tracking.
        
        Args:
            source: Source account address
            destination: Destination account address
            amount: Amount transferred
            tx_hash: Transaction hash
            source_label: Label for the source account
            destination_label: Label for the destination account
            
        Returns:
            bool: True if successful
        """
        try:
            # Update asset holder balances
            update_balance_query = f"""
            SELECT {self.db_schema}.update_asset_holder_balance(%s, %s, %s, %s)
            """
            
            # Get current balances and update
            source_balance = self.auditor.get_account_balance(source)
            dest_balance = self.auditor.get_account_balance(destination)
            
            self.db.execute_query(update_balance_query, [source, self.ubec_code, self.ubec_issuer, float(source_balance)])
            self.db.execute_query(update_balance_query, [destination, self.ubec_code, self.ubec_issuer, float(dest_balance)])
            
            logger.info(f"Transfer recorded in database: {tx_hash}")
            
            # Record reciprocity transaction if stewardship involved
            if "Stewardship" in source_label or "Stewardship" in destination_label:
                self._record_reciprocity_transaction(source, destination, amount, tx_hash)
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording transfer in database: {str(e)}")
            return False
    
    def _record_reciprocity_transaction(self, source, destination, amount, tx_hash):
        """
        Record the transfer impact on reciprocity scores.
        
        Args:
            source: Source account address
            destination: Destination account address
            amount: Amount transferred
            tx_hash: Transaction hash
            
        Returns:
            bool: True if successful
        """
        try:
            # Insert into reciprocity_transactions table
            query = f"""
            INSERT INTO {self.db_schema}.reciprocity_transactions 
            (account_id, transaction_type, amount, reason, source, context, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            
            # Record for both source and destination
            # Source (debit)
            self.db.execute_query(
                query,
                [
                    source, 
                    'debit', 
                    float(amount),
                    'UBEC tokenomics rebalance',
                    'distribution_manager',
                    json.dumps({'tx_hash': tx_hash, 'destination': destination})
                ]
            )
            
            # Destination (credit)
            self.db.execute_query(
                query,
                [
                    destination, 
                    'credit', 
                    float(amount),
                    'UBEC tokenomics rebalance',
                    'distribution_manager',
                    json.dumps({'tx_hash': tx_hash, 'source': source})
                ]
            )
            
            logger.info(f"Recorded reciprocity impact for transaction {tx_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording reciprocity impact: {str(e)}")
            return False
    
    def _schedule_next_rebalance(self, interval_seconds=None):
        """
        Schedule the next rebalance check using the database scheduler.
        
        Args:
            interval_seconds: Override the default check interval
        
        Returns:
            bool: True if successful
        """
        if self.data_source == "stellar":
            logger.info("Database not available, skipping schedule recording")
            return False
        
        try:
            interval = interval_seconds if interval_seconds is not None else self.check_interval
            
            # Schedule next check
            next_run = datetime.now() + timedelta(seconds=interval)
            
            # Create parameters JSON
            params = json.dumps({
                "parameters": [
                    self.ubec_code,
                    self.ubec_issuer
                ]
            })
            
            # Add or update the scheduler job
            query = f"""
            INSERT INTO {self.db_schema}.scheduler_jobs (
                job_name, schedule_interval, next_run, job_function, parameters, enabled
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (job_name) DO UPDATE SET
                schedule_interval = EXCLUDED.schedule_interval,
                next_run = EXCLUDED.next_run,
                job_function = EXCLUDED.job_function,
                parameters = EXCLUDED.parameters,
                enabled = EXCLUDED.enabled
            """
            
            self.db.execute_query(
                query,
                [
                    'ubec_distribution_rebalance',
                    f'{interval} seconds',
                    next_run,
                    'SELECT check_distribution_balance($1, $2)',
                    params,
                    True
                ]
            )
            
            logger.info(f"Scheduled next rebalance check for {next_run}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling next rebalance: {str(e)}")
            return False
    
    def run(self):
        """
        Run the distribution manager as a continuous process.
        """
        logger.info("Starting UBEC Distribution Manager on PUBLIC network")
        print("Manager started and running. Check the logs for details.")
        
        try:
            # Get initial audit
            initial_audit = self.auditor.perform_audit()
            logger.info(f"Initial audit completed successfully")
            
            # Create initial snapshot
            self.snapshot_distribution()
            
            # Schedule first check
            if self.data_source != "stellar":
                self._schedule_next_rebalance()
            
            while True:
                try:
                    # Check if rebalance is needed
                    needs_rebalance, _ = self.is_rebalance_needed()
                    
                    # If rebalance is needed, perform it
                    if needs_rebalance:
                        self.perform_rebalance()
                        # Create snapshot after rebalance
                        self.snapshot_distribution()
                    
                    # Schedule next check
                    if self.data_source != "stellar":
                        self._schedule_next_rebalance()
                    
                    # Wait for next check interval
                    logger.info(f"Sleeping for {self.check_interval} seconds")
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {str(e)}")
                    time.sleep(60)
        except KeyboardInterrupt:
            logger.info("UBEC Distribution Manager stopped by user")
            print("Manager stopped by user.")
        except Exception as e:
            logger.critical(f"Critical error in UBEC Distribution Manager: {str(e)}")
            print(f"Critical error: {str(e)}")


# Example usage:
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="UBEC Distribution Manager")
    parser.add_argument("--source", choices=["db", "stellar", "hybrid"], default="hybrid", 
                      help="Data source (database, Stellar API, or hybrid)")
    parser.add_argument("--setup-db", action="store_true",
                      help="Display information about database setup")
    args = parser.parse_args()
    
    try:
        if args.setup_db:
            print("\nTo set up the database tables for Distribution Manager:")
            print("1. Run: sudo -u postgres psql -d ubec -f distribution_manager_tables.sql")
            print("2. This will create all necessary tables and functions")
            print("\nTables created:")
            print("  - transfer_recommendations")
            print("  - distribution_history")
            print("  - asset_holders")
            print("  - asset_holder_analysis")
            print("  - participants")
            print("  - reciprocity_transactions")
            print("  - scheduler_jobs")
            print("  - system_configuration")
            sys.exit(0)
        
        # Create and run the distribution manager
        print("Creating UBEC Distribution Manager...")
        manager = UBECDistributionManager(data_source=args.source)
        print("Running UBEC Distribution Manager...")
        manager.run()
    except KeyboardInterrupt:
        print("Manager stopped by user.")
    except Exception as e:
        print(f"Error starting UBEC Distribution Manager: {str(e)}")
        logger.critical(f"Critical error in UBEC Distribution Manager: {str(e)}")
