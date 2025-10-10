# db/ubec_data_synchronizer.py
"""
UBEC Data Synchronizer - Enhanced Production Version

Synchronizes data between Stellar blockchain and the ubec_main database schema.
Compatible with the four-element protocol architecture.

Key Features:
- Proper operation ordering (accounts before balances)
- Transaction-safe operations
- Comprehensive error handling
- Rate limit management
- Progress tracking
- Idempotent operations

Schema Mapping:
- stellar_accounts: Core account data
- ubec_balances: Token holdings with foreign key to stellar_accounts
- stellar_transactions: Transaction records
- stellar_operations: Operation details
- ubec_sync_status: Synchronization tracking

Four-Element Architecture:
- 🜁 Air (UBEC) - Gateway & Universal Access
- 🜄 Water (UBECrc) - Flow & Exchange  
- 🜃 Earth (UBECgpi) - Stability & Value
- 🜂 Fire (UBECtt) - Transformation & Action

Author: UBEC Protocol Team
Version: 2.1 (Enhanced Error Handling)
Date: 2025-10-09
"""

import os
import sys
import time
import logging
import json
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Optional, Dict, List, Any, Tuple
import requests
from dotenv import load_dotenv

# Make sure we can import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the database connection module
from db.connection import DatabaseManager, get_connection

# Import settings
try:
    from config import settings
except ImportError:
    pass

# Configure precision for decimal calculations
getcontext().prec = 10

logger = logging.getLogger(__name__)


class SyncException(Exception):
    """Custom exception for sync-related errors."""
    pass


class RateLimitException(Exception):
    """Custom exception for rate limit errors."""
    pass


class UBECDataSynchronizer:
    """
    Synchronizes data between Stellar blockchain and ubec_main database.
    
    This class ensures proper operation ordering:
    1. Create account records in stellar_accounts
    2. Create balance records in ubec_balances (requires account to exist)
    3. Store transaction/operation data
    
    All operations are designed to be idempotent and can be safely retried.
    """
    
    # Element mapping
    ELEMENT_MAP = {
        'UBEC': 'air',
        'UBECrc': 'water',
        'UBECgpi': 'earth',
        'UBECtt': 'fire'
    }
    
    # Operation type mapping for Stellar
    OPERATION_TYPE_MAP = {
        'payment': 'payment',
        'exchange_in': 'path_payment_strict_receive',
        'exchange_out': 'path_payment_strict_send',
        'dex_manage_buy_offer': 'manage_buy_offer',
        'dex_manage_sell_offer': 'manage_sell_offer',
        'create_account': 'create_account',
        'change_trust': 'change_trust'
    }
    
    def __init__(self, config_path="../config/settings.py", db_manager=None):
        """
        Initialize the data synchronizer.
        
        Args:
            config_path: Path to settings.py
            db_manager: Optional existing DatabaseManager instance
        """
        self.config_path = config_path
        logger.info(f"Initializing UBEC Data Synchronizer with config: {config_path}")
        
        # Load settings
        self.settings = self._load_settings(config_path)
        
        # Set up database connection
        if db_manager:
            self.db = db_manager
            logger.info("Using provided database manager")
        else:
            try:
                self.db = DatabaseManager(schema=os.getenv('UBEC_DB_SCHEMA', 'ubec_main'))
                logger.info("Created new database manager")
            except Exception as e:
                logger.error(f"Error creating database manager: {e}")
                raise
        
        # Set up Stellar API connection
        self._initialize_stellar_connection()
        
        # Load accounts configuration
        self.accounts = self.settings.ACCOUNTS if hasattr(self.settings, 'ACCOUNTS') else {}

        # Initialize rate limit tracking
        self.rate_limit_remaining = 3000
        self.rate_limit_limit = 3000
        self.rate_limit_reset = 0
        
        # Initialize sync status tracking
        self._initialize_sync_tables()
        
        logger.info("✓ UBEC Data Synchronizer initialized successfully")
    
    def _load_settings(self, config_path: str) -> Any:
        """Load settings from config file."""
        try:
            from config import settings
            logger.info("Successfully imported settings from config package")
            return settings
        except ImportError:
            logger.info(f"Direct import failed, trying to load from {config_path}")
            
            if not os.path.exists(config_path):
                parent_path = os.path.join(os.path.dirname(os.getcwd()), "config/settings.py")
                if os.path.exists(parent_path):
                    config_path = parent_path
                    logger.info(f"Found settings file at: {config_path}")
                else:
                    logger.error(f"Could not find settings file")
                    raise ImportError(f"Settings file not found")
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("settings", config_path)
            settings_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings_module)
            logger.info(f"Successfully loaded settings from {config_path}")
            return settings_module
    
    def _initialize_stellar_connection(self):
        """Initialize connection to Stellar network."""
        try:
            from stellar_sdk import Server, Asset
            
            self.network = self.settings.PUBLIC_NETWORK_PASSPHRASE
            self.server = Server(horizon_url=self.settings.HORIZON_URL)
            self.ubec_code = self.settings.UBEC_CODE
            self.ubec_issuer = self.settings.UBEC_ISSUER
            self.ubec_asset = Asset(self.settings.UBEC_CODE, self.ubec_issuer)
            
            logger.info(f"✓ Connected to Stellar: {self.settings.HORIZON_URL}")
            logger.info(f"  Token: {self.ubec_code}")
            logger.info(f"  Issuer: {self.ubec_issuer}")
            
        except ImportError:
            logger.warning("⚠ Stellar SDK not available - blockchain queries disabled")
            self.server = None
            self.ubec_code = "UBEC"
            self.ubec_issuer = "GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN"
    
    def _initialize_sync_tables(self):
        """Initialize sync tracking tables if they don't exist."""
        try:
            # Create holder_discovery_history table
            discovery_table = """
            CREATE TABLE IF NOT EXISTS ubec_main.holder_discovery_history (
                id SERIAL PRIMARY KEY,
                discovery_date TIMESTAMP NOT NULL DEFAULT NOW(),
                account_id VARCHAR(56) NOT NULL,
                discovery_source VARCHAR(50) NOT NULL,
                source_transaction_id VARCHAR(64),
                initial_balance DECIMAL(18,8) DEFAULT 0,
                is_new BOOLEAN DEFAULT TRUE,
                added_to_tracking BOOLEAN DEFAULT FALSE,
                metadata JSONB
            )
            """
            self.db.execute_query(discovery_table)
            
            # Create api_rate_limits table
            rate_limit_table = """
            CREATE TABLE IF NOT EXISTS ubec_main.api_rate_limits (
                id SERIAL PRIMARY KEY,
                api_name VARCHAR(50) NOT NULL,
                rate_limit_remaining INTEGER,
                rate_limit_limit INTEGER,
                rate_limit_reset INTEGER,
                last_updated TIMESTAMP NOT NULL DEFAULT NOW()
            )
            """
            self.db.execute_query(rate_limit_table)
            
            logger.info("✓ Sync tracking tables initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing sync tables: {e}")
            return False
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    def _update_rate_limits(self, response_headers: Dict[str, str]):
        """
        Update rate limit information from API response headers.
        
        Args:
            response_headers: HTTP response headers from Stellar API
        """
        try:
            if 'X-Ratelimit-Limit' in response_headers:
                self.rate_limit_limit = int(response_headers['X-Ratelimit-Limit'])
            
            if 'X-Ratelimit-Remaining' in response_headers:
                self.rate_limit_remaining = int(response_headers['X-Ratelimit-Remaining'])
            
            if 'X-RateLimit-Reset' in response_headers:
                self.rate_limit_reset = int(response_headers['X-RateLimit-Reset'])
            
            # Log if getting low
            if self.rate_limit_remaining < 100:
                logger.warning(f"⚠ Rate limit low: {self.rate_limit_remaining} remaining")
            else:
                logger.debug(f"Rate limits: {self.rate_limit_remaining}/{self.rate_limit_limit}")
            
            # Store in database (optional - only if you want to track historical data)
            if self.rate_limit_remaining < 50:  # Only log when getting critically low
                try:
                    query = """
                    INSERT INTO ubec_main.api_rate_limits (
                        api_name, rate_limit_remaining, rate_limit_limit, rate_limit_reset
                    ) VALUES ('stellar_horizon', %s, %s, %s)
                    """
                    self.db.execute_query(query, [
                        self.rate_limit_remaining,
                        self.rate_limit_limit,
                        self.rate_limit_reset
                    ])
                except Exception as e:
                    logger.debug(f"Could not log rate limit to DB: {e}")
            
        except Exception as e:
            logger.warning(f"Error updating rate limits: {e}")
    
    def _check_rate_limit(self, buffer: int = 10) -> bool:
        """
        Check if approaching rate limits and wait if necessary.
        
        Args:
            buffer: Number of requests to keep as buffer
            
        Returns:
            bool: True if safe to proceed
        """
        if not hasattr(self, 'rate_limit_remaining'):
            return True
        
        if self.rate_limit_remaining <= buffer:
            now = int(time.time())
            
            if self.rate_limit_reset > now:
                wait_time = self.rate_limit_reset - now + 2
                logger.warning(f"⚠ Rate limit reached. Waiting {wait_time}s until reset")
                time.sleep(wait_time)
                self.rate_limit_remaining = self.rate_limit_limit
                return True
        
        return True
    
    def _handle_rate_limit_error(self, response) -> int:
        """
        Handle rate limit error from Stellar API.
        
        Args:
            response: HTTP response object
            
        Returns:
            int: Seconds to wait before retrying
        """
        try:
            retry_after = 5
            
            if hasattr(response, 'headers'):
                if 'Retry-After' in response.headers:
                    retry_after = int(response.headers['Retry-After'])
                elif 'X-RateLimit-Reset' in response.headers:
                    reset_time = int(response.headers['X-RateLimit-Reset'])
                    current_time = int(time.time())
                    retry_after = max(1, reset_time - current_time)
                
                self._update_rate_limits(response.headers)
            
            logger.warning(f"⚠ Rate limit hit, waiting {retry_after}s")
            return retry_after
            
        except Exception as e:
            logger.error(f"Error handling rate limit: {e}")
            return 30  # Default to 30 seconds
    
    # ========================================================================
    # ACCOUNT MANAGEMENT (stellar_accounts table)
    # ========================================================================
    
    def _validate_account_id(self, account_id: str) -> bool:
        """
        Validate Stellar account ID format.
        
        Args:
            account_id: Stellar account address
            
        Returns:
            bool: True if valid
        """
        if not account_id:
            return False
        
        # Stellar public keys start with G and are 56 characters
        if not account_id.startswith('G') or len(account_id) != 56:
            return False
        
        # Basic character validation (Stellar uses base32)
        import re
        if not re.match(r'^G[A-Z2-7]{55}$', account_id):
            return False
        
        return True
    
    def _save_account(self, account_id: str, element: Optional[str] = None, 
                     token_code: Optional[str] = None, metadata: Optional[Dict] = None) -> Optional[int]:
        """
        Save or update account in stellar_accounts table.
        
        CRITICAL: This must be called BEFORE saving any balances for this account.
        
        Args:
            account_id: Stellar account address (must be valid G-address)
            element: Element type (air, water, earth, fire)
            token_code: Primary token held (UBEC, UBECrc, UBECgpi, UBECtt)
            metadata: Additional metadata dict
            
        Returns:
            int: Account ID from database, or None if failed
        """
        try:
            # Validate account ID
            if not self._validate_account_id(account_id):
                logger.error(f"Invalid account ID format: {account_id}")
                return None
            
            # If element not provided but token_code is, derive element
            if not element and token_code:
                element = self.ELEMENT_MAP.get(token_code, 'air')
            
            # SIMPLIFIED APPROACH: Use basic insert first, then update with full data
            # This avoids complex type casting issues
            
            # Step 1: Ensure basic account record exists
            basic_query = """
            INSERT INTO ubec_main.stellar_accounts 
            (account_id, created_at, last_activity_at)
            VALUES (%s, NOW(), NOW())
            ON CONFLICT (account_id) DO NOTHING
            """
            
            try:
                self.db.execute_query(basic_query, [account_id])
            except Exception as insert_error:
                logger.error(f"✗ Error in basic insert for {account_id[:8]}...: {insert_error}")
                # Continue anyway - might already exist
            
            # Step 2: Update with full data if provided
            if element and token_code:
                update_query = """
                UPDATE ubec_main.stellar_accounts 
                SET primary_element = %s::element_type,
                    last_activity_at = NOW()
                WHERE account_id = %s
                """
                
                try:
                    self.db.execute_query(update_query, [element, account_id])
                except Exception as update_error:
                    logger.error(f"✗ Error updating element for {account_id[:8]}...: {update_error}")
                    # Continue - at least we have the basic record
            
            # Step 3: Verify account exists and get ID
            verify_query = """
            SELECT id FROM ubec_main.stellar_accounts 
            WHERE account_id = %s
            """
            
            result = self.db.execute_query(verify_query, [account_id], fetch_one=True)
            
            if result:
                if isinstance(result, dict) and 'id' in result:
                    account_db_id = result['id']
                    logger.debug(f"✓ Saved/verified account {account_id[:8]}... (id={account_db_id})")
                    return account_db_id
                elif isinstance(result, (list, tuple)) and len(result) > 0:
                    # Some DB drivers return tuples
                    account_db_id = result[0] if isinstance(result[0], int) else result[0]['id']
                    logger.debug(f"✓ Saved/verified account {account_id[:8]}... (id={account_db_id})")
                    return account_db_id
                else:
                    logger.error(f"✗ Unexpected result format: {type(result)} = {result}")
                    return None
            else:
                logger.error(f"✗ Account not found after insert: {account_id[:8]}...")
                return None
            
        except Exception as e:
            logger.error(f"✗ Error saving account {account_id[:8]}...: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _account_exists(self, account_id: str) -> bool:
        """
        Check if account exists in database.
        
        Args:
            account_id: Stellar account address
            
        Returns:
            bool: True if account exists
        """
        try:
            query = "SELECT id FROM ubec_main.stellar_accounts WHERE account_id = %s"
            result = self.db.execute_query(query, [account_id], fetch_one=True)
            return result is not None
        except Exception as e:
            logger.error(f"Error checking account existence: {e}")
            return False
    
    def _ensure_account_exists(self, account_id: str, element: Optional[str] = None, 
                               token_code: Optional[str] = None) -> bool:
        """
        Ensure account exists in database, creating if necessary.
        
        This is a critical safety check that must be called before any balance operations.
        
        Args:
            account_id: Stellar account address
            element: Element type
            token_code: Token code
            
        Returns:
            bool: True if account exists or was created successfully
        """
        try:
            # Check if exists
            if self._account_exists(account_id):
                logger.debug(f"Account {account_id[:8]}... already exists")
                return True
            
            # Create account
            account_id_result = self._save_account(account_id, element, token_code)
            
            if account_id_result:
                logger.debug(f"✓ Created account {account_id[:8]}...")
                return True
            else:
                logger.error(f"✗ Failed to create account {account_id[:8]}...")
                return False
                
        except Exception as e:
            logger.error(f"Error ensuring account exists: {e}")
            return False
    
    # ========================================================================
    # BALANCE MANAGEMENT (ubec_balances table)
    # ========================================================================
    
    def _save_balance(self, account_id: str, token_code: str, element: str, 
                     balance: Decimal, distribution_category: Optional[str] = None) -> bool:
        """
        Save or update balance in ubec_balances table.
        
        PREREQUISITE: Account MUST exist in stellar_accounts table first!
        This method will fail with foreign key violation if account doesn't exist.
        
        Args:
            account_id: Stellar account address
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            element: Element type (air, water, earth, fire)
            balance: Token balance (Decimal for precision)
            distribution_category: Optional category (general_circulation, stewardship, administration)
            
        Returns:
            bool: True if successful
        """
        try:
            # Validate inputs
            if not self._validate_account_id(account_id):
                logger.error(f"Invalid account ID: {account_id}")
                return False
            
            if token_code not in self.ELEMENT_MAP:
                logger.error(f"Invalid token code: {token_code}")
                return False
            
            if balance < 0:
                logger.error(f"Negative balance not allowed: {balance}")
                return False
            
            # CRITICAL SAFETY CHECK
            if not self._account_exists(account_id):
                logger.error(f"✗ Cannot save balance - account {account_id[:8]}... does not exist!")
                logger.error(f"  You must call _ensure_account_exists() first!")
                return False
            
            query = """
            INSERT INTO ubec_main.ubec_balances 
            (account_id, token_code, element, balance, distribution_category, 
             last_modified_at, sync_timestamp)
            VALUES (%s, %s::token_code, %s::element_type, %s, %s::distribution_category, NOW(), NOW())
            ON CONFLICT (account_id, token_code) DO UPDATE 
            SET balance = EXCLUDED.balance,
                last_modified_at = NOW(),
                sync_timestamp = NOW(),
                distribution_category = COALESCE(
                    EXCLUDED.distribution_category, 
                    ubec_balances.distribution_category
                )
            """
            
            self.db.execute_query(query, [
                account_id, 
                token_code, 
                element, 
                str(balance),
                distribution_category
            ])
            
            logger.debug(f"✓ Saved balance: {account_id[:8]}... = {balance} {token_code}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error saving balance for {account_id[:8]}...: {e}")
            
            # Check if it's the foreign key error we're trying to prevent
            if 'foreign key constraint "fk_balance_account"' in str(e):
                logger.error(f"  FOREIGN KEY VIOLATION - Account must be created first!")
                logger.error(f"  Always call _ensure_account_exists() before _save_balance()")
            
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    def _determine_distribution_category(self, balance: Decimal) -> str:
        """
        Determine distribution category based on balance.
        
        This is a placeholder implementation. Adjust based on your tokenomics rules.
        
        Args:
            balance: Token balance
            
        Returns:
            str: Distribution category
        """
        # Default implementation - all go to general_circulation
        # You can add logic here based on:
        # - Balance thresholds
        # - Account type/metadata
        # - Historical behavior
        # - Governance decisions
        
        if balance < 100:
            return 'general_circulation'
        elif balance < 10000:
            return 'general_circulation'
        else:
            # Large holders might need manual classification
            return 'general_circulation'  # Default
    
    # ========================================================================
    # TRANSACTION FETCHING FROM STELLAR
    # ========================================================================
    
    def fetch_account_history(self, account: str, days: int = 30, 
                             max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch transaction history for an account from Stellar blockchain.
        
        Args:
            account: Stellar account address
            days: Number of days of history to fetch
            max_retries: Maximum retry attempts for rate limiting
            
        Returns:
            list: Transaction history
        """
        if not self.server:
            logger.error("✗ Stellar SDK not available")
            return []
        
        logger.info(f"Fetching {days} days of history for {account[:8]}...")
        
        transactions = []
        start_time = datetime.now() - timedelta(days=days)
        cursor = None
        retry_count = 0
        
        try:
            while True:
                try:
                    self._check_rate_limit()
                    
                    # Query operations for the account
                    op_endpoint = self.server.operations().for_account(account).include_failed(False).limit(100)
                    
                    if cursor:
                        op_endpoint = op_endpoint.cursor(cursor)
                    
                    op_response = op_endpoint.call()
                    
                    if hasattr(op_response, 'headers'):
                        self._update_rate_limits(op_response.headers)
                    
                    retry_count = 0  # Reset on successful call
                    
                    if 'records' not in op_response.get('_embedded', {}):
                        break
                    
                    records = op_response['_embedded']['records']
                    if not records:
                        break
                    
                    # Process operations
                    for op in records:
                        try:
                            # Check time bounds
                            if 'created_at' in op:
                                op_time = datetime.strptime(op['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                                if op_time < start_time:
                                    continue
                            
                            op_type = op.get('type', '')
                            
                            # Handle payment operations
                            if op_type == 'payment' and op.get('asset_code') == self.ubec_code:
                                tx_data = {
                                    'id': op['id'],
                                    'hash': op.get('transaction_hash', ''),
                                    'created_at': op.get('created_at', ''),
                                    'source_account': op.get('source_account', ''),
                                    'destination': op.get('to', ''),
                                    'amount': op.get('amount', '0'),
                                    'asset_code': op.get('asset_code', ''),
                                    'operation_type': 'payment'
                                }
                                transactions.append(tx_data)
                            
                            # Handle path payments (exchanges)
                            elif 'path_payment' in op_type:
                                if (op.get('source_asset_code') == self.ubec_code or 
                                    op.get('asset_code') == self.ubec_code):
                                    
                                    operation_type = 'exchange_out' if op.get('source_asset_code') == self.ubec_code else 'exchange_in'
                                    
                                    tx_data = {
                                        'id': op['id'],
                                        'hash': op.get('transaction_hash', ''),
                                        'created_at': op.get('created_at', ''),
                                        'source_account': op.get('source_account', ''),
                                        'destination': op.get('to', ''),
                                        'amount': op.get('amount', '0'),
                                        'asset_code': self.ubec_code,
                                        'operation_type': operation_type,
                                        'exchange_details': {
                                            'source_asset': op.get('source_asset_code', ''),
                                            'source_amount': op.get('source_amount', '0'),
                                            'destination_asset': op.get('asset_code', ''),
                                            'destination_amount': op.get('amount', '0')
                                        }
                                    }
                                    transactions.append(tx_data)
                            
                            # Handle DEX offers
                            elif op_type in ['manage_buy_offer', 'manage_sell_offer']:
                                selling_asset = op.get('selling_asset_code', '')
                                buying_asset = op.get('buying_asset_code', '')
                                
                                if selling_asset == self.ubec_code or buying_asset == self.ubec_code:
                                    tx_data = {
                                        'id': op['id'],
                                        'hash': op.get('transaction_hash', ''),
                                        'created_at': op.get('created_at', ''),
                                        'source_account': op.get('source_account', ''),
                                        'destination': 'market',
                                        'amount': op.get('amount', '0'),
                                        'asset_code': self.ubec_code,
                                        'operation_type': f'dex_{op_type}',
                                        'exchange_details': {
                                            'selling_asset': selling_asset,
                                            'buying_asset': buying_asset,
                                            'price': op.get('price', '0')
                                        }
                                    }
                                    transactions.append(tx_data)
                        
                        except Exception as e:
                            logger.warning(f"Error processing operation: {e}")
                            continue
                    
                    # Check for next page
                    if 'next' not in op_response.get('_links', {}):
                        break
                    
                    next_link = op_response['_links']['next'].get('href', '')
                    if 'cursor=' in next_link:
                        cursor = next_link.split('cursor=')[1].split('&')[0]
                    else:
                        break
                    
                    time.sleep(0.5)  # Small delay between pages
                    
                except Exception as e:
                    # Handle rate limiting
                    if hasattr(e, 'status_code') and e.status_code == 429:
                        retry_count += 1
                        
                        if retry_count > max_retries:
                            logger.error(f"✗ Max retries ({max_retries}) reached for {account[:8]}...")
                            break
                        
                        wait_time = self._handle_rate_limit_error(e.response if hasattr(e, 'response') else None)
                        logger.warning(f"⚠ Rate limit, retry {retry_count}/{max_retries}, waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    
                    logger.error(f"✗ Error fetching history: {e}")
                    if cursor:
                        continue  # Try to continue with next page
                    else:
                        break
        
        except Exception as e:
            logger.error(f"✗ Error fetching operations for {account[:8]}...: {e}")
        
        logger.info(f"✓ Retrieved {len(transactions)} operations for {account[:8]}...")
        return transactions
    
    # ========================================================================
    # TRANSACTION STORAGE (stellar_transactions & stellar_operations)
    # ========================================================================
    
    def _store_transactions(self, account_id: str, transactions: List[Dict[str, Any]]) -> int:
        """
        Store transactions in stellar_transactions and stellar_operations tables.
        
        Args:
            account_id: Account ID
            transactions: List of transaction dicts
            
        Returns:
            int: Number of transactions stored
        """
        if not transactions:
            return 0
        
        count = 0
        
        try:
            # Ensure main account exists first
            if not self._ensure_account_exists(account_id):
                logger.error(f"✗ Cannot store transactions - account {account_id[:8]}... doesn't exist")
                return 0
            
            # CRITICAL FIX: Ensure ALL source accounts exist before storing transactions
            # Extract all unique source accounts from transactions
            source_accounts = set()
            for tx in transactions:
                source_acc = tx.get('source_account')
                if source_acc and self._validate_account_id(source_acc):
                    source_accounts.add(source_acc)
            
            # Ensure all source accounts exist in database
            logger.debug(f"Ensuring {len(source_accounts)} source accounts exist...")
            for source_acc in source_accounts:
                if not self._ensure_account_exists(source_acc):
                    logger.warning(f"⚠ Could not create source account {source_acc[:8]}...")
            
            # Process each transaction
            for tx in transactions:
                try:
                    # Check if operation already exists (idempotent)
                    check_query = "SELECT id FROM ubec_main.stellar_operations WHERE operation_id = %s"
                    existing = self.db.execute_query(check_query, [tx['id']], fetch_one=True)
                    
                    if existing:
                        continue  # Skip existing operations
                    
                    # Determine element and token
                    asset_code = tx.get('asset_code', self.ubec_code)
                    element = self.ELEMENT_MAP.get(asset_code, 'air')
                    
                    # Ensure transaction record exists
                    tx_query = """
                    INSERT INTO ubec_main.stellar_transactions 
                    (transaction_hash, ledger_sequence, primary_element, involves_tokens, 
                     source_account, created_at, successful)
                    VALUES (%s, %s, %s::element_type, %s::token_code[], %s, %s, %s)
                    ON CONFLICT (transaction_hash) DO NOTHING
                    """
                    
                    # For now, use a dummy ledger sequence (would need full tx to get real value)
                    ledger_seq = 0
                    
                    self.db.execute_query(tx_query, [
                        tx['hash'],
                        ledger_seq,
                        element,
                        [asset_code],
                        tx['source_account'],
                        datetime.strptime(tx['created_at'], "%Y-%m-%dT%H:%M:%SZ"),
                        True
                    ])
                    
                    # Insert the operation
                    op_query = """
                    INSERT INTO ubec_main.stellar_operations (
                        operation_id, transaction_hash, operation_element, asset_code,
                        type, source_account, from_account, to_account, amount,
                        asset_issuer, details, created_at
                    ) VALUES (%s, %s, %s::element_type, %s::token_code, %s::transaction_type, 
                              %s, %s, %s, %s, %s, %s::jsonb, %s)
                    """
                    
                    # Prepare operation details
                    details = {}
                    if 'exchange_details' in tx:
                        details['exchange'] = tx['exchange_details']
                    
                    # Map operation type
                    op_type = self.OPERATION_TYPE_MAP.get(tx['operation_type'], 'payment')
                    
                    self.db.execute_query(op_query, [
                        tx['id'],
                        tx['hash'],
                        element,
                        asset_code,
                        op_type,
                        tx['source_account'],
                        tx['source_account'],
                        tx.get('destination'),
                        tx.get('amount'),
                        self.ubec_issuer,
                        json.dumps(details) if details else None,
                        datetime.strptime(tx['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    ])
                    
                    count += 1
                    
                    if count % 10 == 0:
                        logger.info(f"  Stored {count} operations...")
                    
                except Exception as e:
                    logger.error(f"✗ Error storing transaction {tx.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"✓ Stored {count} new operations for {account_id[:8]}...")
            return count
            
        except Exception as e:
            logger.error(f"✗ Error in _store_transactions: {e}")
            return count
    
    # ========================================================================
    # SYNC STATUS TRACKING
    # ========================================================================
    
    def _update_sync_status(self, token_code: str, sync_type: str, status: str, 
                           records_synced: int = 0, error: Optional[str] = None):
        """
        Update sync status in ubec_sync_status table.
        
        Args:
            token_code: Token being synced (UBEC, UBECrc, etc.)
            sync_type: Type of sync (accounts, transactions, balances)
            status: Status (active, error, complete)
            records_synced: Number of records synced
            error: Error message if any
        """
        try:
            element = self.ELEMENT_MAP.get(token_code, 'air')
            
            query = """
            INSERT INTO ubec_main.ubec_sync_status 
            (element, token_code, sync_type, status, last_sync_time, 
             records_synced, errors_encountered, error_log, updated_at)
            VALUES (%s::element_type, %s::token_code, %s, %s, NOW(), 
                    %s, %s, %s::jsonb, NOW())
            ON CONFLICT (element, token_code, sync_type) DO UPDATE
            SET status = EXCLUDED.status,
                last_sync_time = NOW(),
                records_synced = ubec_sync_status.records_synced + EXCLUDED.records_synced,
                errors_encountered = CASE 
                    WHEN EXCLUDED.error_log IS NOT NULL 
                    THEN ubec_sync_status.errors_encountered + 1 
                    ELSE ubec_sync_status.errors_encountered 
                END,
                error_log = EXCLUDED.error_log,
                updated_at = NOW()
            """
            
            error_json = json.dumps({
                'error': error, 
                'timestamp': datetime.now().isoformat()
            }) if error else None
            
            self.db.execute_query(query, [
                element,
                token_code,
                sync_type,
                status,
                records_synced,
                1 if error else 0,
                error_json
            ])
            
        except Exception as e:
            logger.error(f"Error updating sync status: {e}")
    
    # ========================================================================
    # HIGH-LEVEL SYNC OPERATIONS
    # ========================================================================
    
    def sync_account_transactions(self, account_id: str, days_back: int = 30) -> int:
        """
        Fetch and store transaction history for an account.
        
        Args:
            account_id: Stellar account address
            days_back: Number of days to look back
            
        Returns:
            int: Number of new transactions stored
        """
        logger.info(f"Syncing transactions for {account_id[:8]}... ({days_back} days)")
        
        try:
            # Fetch from blockchain
            transactions = self.fetch_account_history(account_id, days_back)
            
            # Store in database
            count = self._store_transactions(account_id, transactions)
            
            logger.info(f"✓ Synced {count} transactions for {account_id[:8]}...")
            return count
            
        except Exception as e:
            logger.error(f"✗ Error syncing account {account_id[:8]}...: {e}")
            return 0
    
    def discover_new_holders(self, days_back: int = 30, batch_size: int = 10, 
                            batch_delay: int = 3) -> int:
        """
        Discover new token holders from recent transactions.
        
        This looks at recent operations to find accounts that received tokens
        but aren't yet in our database.
        
        Args:
            days_back: Days to look back
            batch_size: Accounts per batch
            batch_delay: Delay between batches (seconds)
            
        Returns:
            int: Number of new holders discovered
        """
        try:
            logger.info(f"Discovering new holders from last {days_back} days...")
            
            # Find accounts from recent operations
            query = """
            SELECT DISTINCT to_account as account_id
            FROM ubec_main.stellar_operations 
            WHERE asset_code = %s::token_code
            AND created_at > NOW() - INTERVAL '%s days'
            AND to_account NOT IN (
                SELECT account_id FROM ubec_main.stellar_accounts
            )
            """
            
            results = self.db.execute_query(query, [self.ubec_code, days_back])
            new_accounts = [r['account_id'] for r in results if r['account_id']]
            
            logger.info(f"Found {len(new_accounts)} potential new holders")
            
            if not new_accounts:
                return 0
            
            count = 0
            element = self.ELEMENT_MAP.get(self.ubec_code, 'air')
            
            for i in range(0, len(new_accounts), batch_size):
                batch = new_accounts[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(new_accounts) + batch_size - 1) // batch_size
                
                logger.info(f"Processing batch {batch_num}/{total_batches}...")
                
                for account in batch:
                    if not self._validate_account_id(account):
                        continue
                    
                    try:
                        # STEP 1: Create account record FIRST
                        if not self._ensure_account_exists(account, element, self.ubec_code):
                            logger.error(f"✗ Failed to create account for {account[:8]}..., skipping")
                            continue
                        
                        # STEP 2: Check balance on blockchain if server available
                        if self.server:
                            self._check_rate_limit()
                            
                            stellar_account = self.server.accounts().account_id(account).call()
                            
                            if hasattr(stellar_account, 'headers'):
                                self._update_rate_limits(stellar_account.headers)
                            
                            # Find and save balance
                            for balance_data in stellar_account.get('balances', []):
                                if (balance_data.get('asset_code') == self.ubec_code and
                                    balance_data.get('asset_issuer') == self.ubec_issuer):
                                    
                                    bal_amount = Decimal(balance_data.get('balance', '0'))
                                    
                                    if bal_amount > 0:
                                        # STEP 3: Now safe to save balance
                                        success = self._save_balance(
                                            account,
                                            self.ubec_code,
                                            element,
                                            bal_amount
                                        )
                                        
                                        if success:
                                            count += 1
                                            logger.debug(f"✓ New holder: {account[:8]}... = {bal_amount}")
                                        
                                        time.sleep(0.2)  # Small delay
                                    
                                    break
                        
                    except Exception as e:
                        if hasattr(e, 'status_code') and e.status_code == 429:
                            wait_time = self._handle_rate_limit_error(
                                e.response if hasattr(e, 'response') else None
                            )
                            time.sleep(wait_time)
                            continue
                        else:
                            logger.warning(f"Error processing account {account[:8]}...: {e}")
                
                # Delay between batches
                if i + batch_size < len(new_accounts):
                    logger.info(f"Waiting {batch_delay}s before next batch...")
                    time.sleep(batch_delay)
            
            logger.info(f"✓ Discovered {count} new holders")
            return count
            
        except Exception as e:
            logger.error(f"✗ Error discovering new holders: {e}")
            return 0
    
    def find_all_holders_from_network(self, batch_size: int = 25, max_accounts: int = 200, 
                                      batch_delay: int = 10) -> int:
        """
        Find all token holders directly from Stellar network.
        
        This is the primary method for discovering UBEC holders.
        It ensures proper ordering: accounts are created before balances.
        
        Args:
            batch_size: Accounts per batch
            max_accounts: Maximum accounts to process
            batch_delay: Delay between batches (seconds)
            
        Returns:
            int: Number of holders found and synced
        """
        logger.info(f"Finding all {self.ubec_code} holders from Stellar network")
        logger.info(f"  Batch size: {batch_size}, Max accounts: {max_accounts}")
        
        if not self.server:
            logger.error("✗ Stellar SDK not available")
            return 0
        
        count = 0
        cursor = None
        batch_count = 0
        element = self.ELEMENT_MAP.get(self.ubec_code, 'air')
        
        try:
            while count < max_accounts:
                try:
                    self._check_rate_limit()
                    
                    # Query Stellar for accounts with trustlines to this asset
                    endpoint = self.server.accounts().for_asset(self.ubec_asset).limit(batch_size)
                    
                    if cursor:
                        endpoint = endpoint.cursor(cursor)
                    
                    response = endpoint.call()
                    
                    if hasattr(response, 'headers'):
                        self._update_rate_limits(response.headers)
                    
                    records = response.get('_embedded', {}).get('records', [])
                    
                    if not records:
                        logger.info("No more accounts with trustlines")
                        break
                    
                    batch_count += 1
                    logger.info(f"Processing batch {batch_count} of {len(records)} accounts...")
                    
                    # Process each account in the batch
                    for account in records:
                        account_id = account.get('id') or account.get('account_id')
                        
                        if not self._validate_account_id(account_id):
                            logger.warning(f"Invalid account ID: {account_id}")
                            continue
                        
                        # Find UBEC balance
                        ubec_balance = Decimal('0')
                        for balance_data in account.get('balances', []):
                            if (balance_data.get('asset_code') == self.ubec_code and
                                balance_data.get('asset_issuer') == self.ubec_issuer):
                                ubec_balance = Decimal(balance_data.get('balance', '0'))
                                break
                        
                        # Only process if they have a non-zero balance
                        if ubec_balance > 0:
                            try:
                                # STEP 1: CRITICAL - Create account record FIRST
                                account_db_id = self._save_account(account_id, element, self.ubec_code)
                                
                                if not account_db_id:
                                    logger.error(f"✗ Failed to create account for {account_id[:8]}..., skipping balance")
                                    continue
                                
                                # STEP 2: Now safe to save balance (account exists)
                                success = self._save_balance(
                                    account_id, 
                                    self.ubec_code, 
                                    element, 
                                    ubec_balance
                                )
                                
                                if success:
                                    count += 1
                                    
                                    if count % 10 == 0:
                                        logger.info(f"  ✓ Synced {count} holders so far...")
                                else:
                                    logger.error(f"✗ Failed to save balance for {account_id[:8]}...")
                                
                            except Exception as e:
                                logger.error(f"✗ Error processing account {account_id[:8]}...: {e}")
                        else:
                            logger.debug(f"Skipping {account_id[:8]}... (zero balance)")
                    
                    # Get next page cursor
                    if 'next' not in response.get('_links', {}):
                        logger.info("No more pages available")
                        break
                    
                    next_link = response['_links']['next'].get('href', '')
                    if 'cursor=' in next_link:
                        cursor = next_link.split('cursor=')[1].split('&')[0]
                    else:
                        break
                    
                    if count >= max_accounts:
                        logger.info(f"Reached max accounts ({max_accounts})")
                        break
                    
                    # Delay between batches
                    logger.info(f"Waiting {batch_delay}s before next batch...")
                    time.sleep(batch_delay)
                    
                except Exception as e:
                    # Handle rate limiting
                    if hasattr(e, 'status_code') and e.status_code == 429:
                        wait_time = self._handle_rate_limit_error(
                            e.response if hasattr(e, 'response') else None
                        )
                        logger.warning(f"⚠ Rate limit hit. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"✗ Error processing batch: {e}")
                        time.sleep(10)  # Wait before retrying
        
        except Exception as e:
            logger.error(f"✗ Error finding holders: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        
        logger.info(f"✓ Found and synced {count} holders from network")
        return count
    
    # ========================================================================
    # PUBLIC API METHODS - Called by Protocol Sync Operations
    # ========================================================================
    
    def sync_account_data(self, asset_code: str = 'UBEC', issuer: Optional[str] = None, 
                         limit: int = 200) -> Dict[str, Any]:
        """
        Synchronize account data from Stellar network.
        
        PUBLIC API - Called by protocol sync operations (e.g., UBEC.sync_gateway_data())
        
        This is the main entry point for syncing accounts. It:
        1. Discovers holders from Stellar network
        2. Finds additional holders from recent transactions
        3. Ensures proper ordering (accounts before balances)
        
        Args:
            asset_code: Asset to sync (UBEC, UBECrc, UBECgpi, UBECtt)
            issuer: Issuer address (optional, uses default if not provided)
            limit: Max accounts to sync
            
        Returns:
            dict: Sync results with counts and status
        """
        logger.info(f"=" * 60)
        logger.info(f"SYNCING ACCOUNT DATA FOR {asset_code}")
        logger.info(f"=" * 60)
        
        try:
            # Save original token code and switch context
            original_code = self.ubec_code
            self.ubec_code = asset_code
            
            if issuer is None:
                issuer = self.ubec_issuer
            
            # Update sync status to 'active'
            self._update_sync_status(asset_code, 'accounts', 'active', 0)
            
            # PHASE 1: Discover holders from network
            logger.info(f"\nPhase 1: Discovering holders from Stellar network...")
            accounts_found = self.find_all_holders_from_network(
                batch_size=25,
                max_accounts=limit,
                batch_delay=10
            )
            
            # PHASE 2: Check recent transactions for new holders
            logger.info(f"\nPhase 2: Discovering holders from recent transactions...")
            additional_found = self.discover_new_holders(
                days_back=30,
                batch_size=10,
                batch_delay=3
            )
            
            total = accounts_found + additional_found
            
            # Update sync status to 'complete'
            self._update_sync_status(asset_code, 'accounts', 'complete', total)
            
            # Restore original token code
            self.ubec_code = original_code
            
            logger.info(f"\n✓ SYNC COMPLETE")
            logger.info(f"  Total synced: {total}")
            logger.info(f"  From network: {accounts_found}")
            logger.info(f"  From transactions: {additional_found}")
            logger.info(f"=" * 60)
            
            return {
                'success': True,
                'synced': total,
                'accounts_synced': total,
                'from_network': accounts_found,
                'from_transactions': additional_found,
                'asset_code': asset_code
            }
            
        except Exception as e:
            logger.error(f"✗ Error syncing accounts for {asset_code}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Update sync status to 'error'
            self._update_sync_status(asset_code, 'accounts', 'error', 0, str(e))
            
            # Restore original token code if needed
            if 'original_code' in locals():
                self.ubec_code = original_code
            
            return {
                'success': False,
                'synced': 0,
                'error': str(e)
            }
    
    def sync_transaction_data(self, asset_code: str = 'UBEC', issuer: Optional[str] = None, 
                             days_back: int = 7) -> Dict[str, Any]:
        """
        Synchronize transaction data from Stellar network.
        
        PUBLIC API - Called by protocol sync operations.
        
        Args:
            asset_code: Asset to sync
            issuer: Issuer address (optional)
            days_back: Days of history to fetch
            
        Returns:
            dict: Sync results
        """
        logger.info(f"=" * 60)
        logger.info(f"SYNCING TRANSACTIONS FOR {asset_code} ({days_back} days)")
        logger.info(f"=" * 60)
        
        try:
            # Save and switch context
            original_code = self.ubec_code
            self.ubec_code = asset_code
            
            if issuer is None:
                issuer = self.ubec_issuer
            
            # Update sync status
            self._update_sync_status(asset_code, 'transactions', 'active', 0)
            
            # Get known holders
            query = """
            SELECT DISTINCT account_id 
            FROM ubec_main.ubec_balances 
            WHERE token_code = %s::token_code
            LIMIT 50
            """
            
            holders = self.db.execute_query(query, [asset_code])
            
            if not holders:
                logger.warning(f"No holders found for {asset_code}. Run account sync first.")
                return {
                    'success': False,
                    'synced': 0,
                    'message': 'No holders found. Run account sync first.'
                }
            
            logger.info(f"Syncing transactions for {len(holders)} holders...")
            
            accounts_synced = 0
            total_txs = 0
            
            for i, holder in enumerate(holders):
                account_id = holder.get('account_id')
                if not account_id:
                    continue
                
                try:
                    logger.info(f"  [{i+1}/{len(holders)}] Syncing {account_id[:8]}...")
                    txs = self.sync_account_transactions(account_id, days_back)
                    
                    if txs > 0:
                        accounts_synced += 1
                        total_txs += txs
                        
                except Exception as e:
                    logger.error(f"✗ Error syncing txs for {account_id[:8]}...: {e}")
            
            # Update sync status
            self._update_sync_status(asset_code, 'transactions', 'complete', accounts_synced)
            
            # Restore context
            self.ubec_code = original_code
            
            logger.info(f"\n✓ SYNC COMPLETE")
            logger.info(f"  Accounts processed: {accounts_synced}")
            logger.info(f"  Total transactions: {total_txs}")
            logger.info(f"=" * 60)
            
            return {
                'success': True,
                'synced': accounts_synced,
                'transactions_synced': total_txs,
                'asset_code': asset_code,
                'days_back': days_back
            }
            
        except Exception as e:
            logger.error(f"✗ Error syncing transactions for {asset_code}: {e}")
            self._update_sync_status(asset_code, 'transactions', 'error', 0, str(e))
            
            if 'original_code' in locals():
                self.ubec_code = original_code
            
            return {
                'success': False,
                'synced': 0,
                'error': str(e)
            }
    
    def sync_balance_data(self, asset_code: str = 'UBEC', issuer: Optional[str] = None) -> Dict[str, Any]:
        """
        Synchronize balance data from Stellar network.
        
        PUBLIC API - Called by protocol sync operations.
        
        This refreshes balances for known accounts.
        
        Args:
            asset_code: Asset to sync
            issuer: Issuer address (optional)
            
        Returns:
            dict: Sync results
        """
        logger.info(f"=" * 60)
        logger.info(f"SYNCING BALANCES FOR {asset_code}")
        logger.info(f"=" * 60)
        
        try:
            # Save and switch context
            original_code = self.ubec_code
            self.ubec_code = asset_code
            
            if issuer is None:
                issuer = self.ubec_issuer
            
            # Update sync status
            self._update_sync_status(asset_code, 'balances', 'active', 0)
            
            # Get known accounts
            query = "SELECT account_id FROM ubec_main.stellar_accounts LIMIT 50"
            accounts = self.db.execute_query(query)
            
            if not accounts:
                logger.warning(f"No accounts found for {asset_code}. Running discovery first...")
                discovery = self.sync_account_data(asset_code, issuer, 100)
                accounts = self.db.execute_query(query)
            
            if not accounts:
                logger.error("Still no accounts found after discovery")
                return {
                    'success': False,
                    'synced': 0,
                    'message': 'No accounts found'
                }
            
            logger.info(f"Refreshing balances for {len(accounts)} accounts...")
            
            balances_updated = 0
            element = self.ELEMENT_MAP.get(asset_code, 'air')
            
            for i, account in enumerate(accounts[:50]):  # Limit to 50 for safety
                account_id = account.get('account_id')
                if not self._validate_account_id(account_id):
                    continue
                
                try:
                    logger.info(f"  [{i+1}/{min(len(accounts), 50)}] Checking {account_id[:8]}...")
                    
                    self._check_rate_limit()
                    
                    if self.server:
                        stellar_account = self.server.accounts().account_id(account_id).call()
                        
                        if hasattr(stellar_account, 'headers'):
                            self._update_rate_limits(stellar_account.headers)
                        
                        # Find balance for this asset
                        for balance_data in stellar_account.get('balances', []):
                            if (balance_data.get('asset_code') == asset_code and
                                balance_data.get('asset_issuer') == issuer):
                                
                                bal_amount = Decimal(balance_data.get('balance', '0'))
                                
                                # Account already exists (we got it from stellar_accounts table)
                                # So we can safely save the balance
                                success = self._save_balance(account_id, asset_code, element, bal_amount)
                                
                                if success:
                                    balances_updated += 1
                                    logger.debug(f"✓ Updated: {bal_amount} {asset_code}")
                                
                                break
                        
                        # Small delay every 5 accounts
                        if (i + 1) % 5 == 0:
                            time.sleep(0.5)
                
                except Exception as e:
                    logger.warning(f"✗ Error updating balance for {account_id[:8]}...: {e}")
            
            # Update sync status
            self._update_sync_status(asset_code, 'balances', 'complete', balances_updated)
            
            # Restore context
            self.ubec_code = original_code
            
            logger.info(f"\n✓ SYNC COMPLETE")
            logger.info(f"  Balances updated: {balances_updated}")
            logger.info(f"  Total accounts: {len(accounts)}")
            logger.info(f"=" * 60)
            
            return {
                'success': True,
                'synced': balances_updated,
                'balances_synced': balances_updated,
                'asset_code': asset_code,
                'total_accounts': len(accounts)
            }
            
        except Exception as e:
            logger.error(f"✗ Error syncing balances for {asset_code}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            self._update_sync_status(asset_code, 'balances', 'error', 0, str(e))
            
            if 'original_code' in locals():
                self.ubec_code = original_code
            
            return {
                'success': False,
                'synced': 0,
                'error': str(e)
            }


# ============================================================================
# MAIN - For testing
# ============================================================================

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 70)
    print("TESTING UBEC DATA SYNCHRONIZER (Enhanced Version)")
    print("=" * 70)
    
    try:
        sync = UBECDataSynchronizer()
        
        print("\n1. Testing account sync...")
        result = sync.sync_account_data(asset_code='UBEC', limit=50)
        print(f"   Result: {result}")
        
        print("\n2. Testing balance sync...")
        result = sync.sync_balance_data(asset_code='UBEC')
        print(f"   Result: {result}")
        
        print("\n3. Testing transaction sync...")
        result = sync.sync_transaction_data(asset_code='UBEC', days_back=7)
        print(f"   Result: {result}")
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS COMPLETED!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
