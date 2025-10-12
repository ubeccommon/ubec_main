#!/usr/bin/env python3
"""
UBEC Data Synchronizer - Async Production Version

Synchronizes data between Stellar blockchain and the ubec_main database schema.
Compatible with the four-element protocol architecture.

Design Principles Compliance:
- ✅ Modular Design: Self-contained service with defined boundaries
- ✅ Service Pattern: No standalone execution
- ✅ Database as Single Source of Truth: Settings loaded from database
- ✅ Strict Async: All I/O operations use async/await
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ No Duplicate Configuration: Settings stored once in database

Key Features:
- FULLY ASYNC operations (async/await pattern throughout)
- Proper operation ordering (accounts before balances)
- Transaction-safe operations with async context managers
- Comprehensive error handling
- Integrated rate limit management with async waiting
- Progress tracking
- Idempotent operations
- Compatible with asyncpg datetime conversion (handled in database_manager)

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

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 4.6 (Increased default account sync limit from 200 to 5000, added unlimited option)
Date: October 11, 2025
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Optional, Dict, List, Any, Tuple
import aiohttp

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
    Asynchronous data synchronizer between Stellar blockchain and ubec_main database.
    
    This class ensures proper operation ordering:
    1. Create account records in stellar_accounts
    2. Create balance records in ubec_balances (requires account to exist)
    3. Store transaction/operation data
    
    All operations are designed to be idempotent and can be safely retried.
    All I/O operations use async/await patterns for maximum efficiency.
    
    Settings are loaded from database (single source of truth principle).
    
    Note: Datetime conversion is handled automatically by database_manager.py
    This module passes ISO 8601 strings directly - they are converted at the
    database boundary layer for proper asyncpg compatibility.
    """
    
    # Element mapping - ONLY for UBEC family tokens
    ELEMENT_MAP = {
        'UBEC': 'air',
        'UBECrc': 'water',
        'UBECgpi': 'earth',
        'UBECtt': 'fire'
    }
    
    # Valid UBEC token codes (what we store in database)
    VALID_UBEC_TOKENS = {'UBEC', 'UBECrc', 'UBECgpi', 'UBECtt'}
    
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
    
    def __init__(self, db_manager):
        """
        Initialize the async data synchronizer.
        
        Args:
            db_manager: AsyncDatabaseManager instance
        """
        logger.info(f"Initializing UBEC Data Synchronizer (Async) with database manager")
        
        # Store database manager
        self.db = db_manager
        
        # Settings will be loaded from database
        self.settings = {}
        self.accounts = {}
        
        # Network configuration defaults (will be overridden by database settings)
        self.network = None
        self.horizon_url = None
        self.ubec_code = "UBEC"
        self.ubec_issuer = None
        self.ubec_asset = None
        
        # Stellar server (initialized in async context)
        self.server = None
        
        # Initialize rate limit tracking
        self.rate_limit_remaining = 3000
        self.rate_limit_limit = 3000
        self.rate_limit_reset = 0
        
        # Session for async HTTP requests
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("✓ UBEC Data Synchronizer (Async) initialized - settings will load on first use")
    
    async def _load_settings_from_database(self):
        """
        Load settings from database (single source of truth).
        Settings are stored in a configuration table.
        """
        try:
            # Load system settings from database
            query = """
                SELECT setting_key, setting_value, setting_type
                FROM system_settings
                WHERE is_active = TRUE
                ORDER BY setting_key
            """
            
            rows = await self.db.fetch_all(query)
            
            if not rows:
                # Use environment variables as fallback
                logger.warning("No settings found in database, using environment variables")
                self.settings = {
                    'horizon_url': os.getenv('HORIZON_URL', 'https://horizon.stellar.org'),
                    'network_passphrase': os.getenv('NETWORK_PASSPHRASE', 'Public Global Stellar Network ; September 2015'),
                    'ubec_code': os.getenv('UBEC_CODE', 'UBEC'),
                    'ubec_issuer': os.getenv('UBEC_ISSUER', 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN')
                }
            else:
                # Convert database rows to settings dict
                self.settings = {}
                for row in rows:
                    key = row['setting_key']
                    value = row['setting_value']
                    setting_type = row.get('setting_type', 'string')
                    
                    # Convert types
                    if setting_type == 'integer':
                        value = int(value)
                    elif setting_type == 'float':
                        value = float(value)
                    elif setting_type == 'boolean':
                        value = value.lower() in ('true', '1', 'yes')
                    
                    self.settings[key] = value
                
                logger.info(f"✓ Loaded {len(self.settings)} settings from database")
            
            # Extract commonly used settings
            self.horizon_url = self.settings.get('horizon_url', 'https://horizon.stellar.org')
            self.network = self.settings.get('network_passphrase', 'Public Global Stellar Network ; September 2015')
            self.ubec_code = self.settings.get('ubec_code', 'UBEC')
            self.ubec_issuer = self.settings.get('ubec_issuer', 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN')
            
            # Load issuers for all 4 UBEC tokens
            # Priority: 1) Database settings, 2) Environment variables, 3) Default to main issuer
            self.ubecrc_issuer = self.settings.get('ubecrc_issuer') or os.getenv('UBECRC_ISSUER') or self.ubec_issuer
            self.ubecgpi_issuer = self.settings.get('ubecgpi_issuer') or os.getenv('UBECGPI_ISSUER') or self.ubec_issuer
            self.ubectt_issuer = self.settings.get('ubectt_issuer') or os.getenv('UBECTT_ISSUER') or self.ubec_issuer
            
            # Log issuer configuration
            logger.info(f"Token issuer configuration:")
            logger.info(f"  UBEC:    {self.ubec_issuer}")
            logger.info(f"  UBECrc:  {self.ubecrc_issuer}")
            logger.info(f"  UBECgpi: {self.ubecgpi_issuer}")
            logger.info(f"  UBECtt:  {self.ubectt_issuer}")
            
            # Check if all tokens use the same issuer
            unique_issuers = len(set([
                self.ubec_issuer, 
                self.ubecrc_issuer, 
                self.ubecgpi_issuer, 
                self.ubectt_issuer
            ]))
            if unique_issuers == 1:
                logger.info("  All 4 tokens use the SAME issuer")
            else:
                logger.info(f"  Tokens use {unique_issuers} different issuers")
            
        except Exception as e:
            logger.error(f"Error loading settings from database: {e}")
            # Use environment variables as fallback
            self.settings = {
                'horizon_url': os.getenv('HORIZON_URL', 'https://horizon.stellar.org'),
                'network_passphrase': os.getenv('NETWORK_PASSPHRASE', 'Public Global Stellar Network ; September 2015'),
                'ubec_code': os.getenv('UBEC_CODE', 'UBEC'),
                'ubec_issuer': os.getenv('UBEC_ISSUER', 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN')
            }
            
            self.horizon_url = self.settings['horizon_url']
            self.network = self.settings['network_passphrase']
            self.ubec_code = self.settings['ubec_code']
            self.ubec_issuer = self.settings['ubec_issuer']
            
            # Load issuers for other tokens from environment (fallback to main issuer)
            self.ubecrc_issuer = os.getenv('UBECRC_ISSUER', self.ubec_issuer)
            self.ubecgpi_issuer = os.getenv('UBECGPI_ISSUER', self.ubec_issuer)
            self.ubectt_issuer = os.getenv('UBECTT_ISSUER', self.ubec_issuer)
            
            logger.warning("Using environment variables as fallback for settings")
    
    async def _load_accounts_from_database(self):
        """Load tracked accounts from database."""
        try:
            query = """
                SELECT account_id, primary_element, metadata
                FROM stellar_accounts
                ORDER BY account_id
            """
            
            rows = await self.db.fetch_all(query)
            
            self.accounts = {}
            for row in rows:
                account_id = row['account_id']
                self.accounts[account_id] = {
                    'name': account_id,
                    'element': row.get('primary_element', 'unknown'),
                    'metadata': row.get('metadata', {})
                }
            
            logger.info(f"✓ Loaded {len(self.accounts)} accounts from database")
            
        except Exception as e:
            logger.error(f"Error loading accounts from database: {e}")
            self.accounts = {}
    
    async def _initialize_stellar_connection(self):
        """Initialize connection to Stellar network."""
        try:
            from stellar_sdk import ServerAsync, Asset
            
            # Load settings if not already loaded
            if not self.settings:
                await self._load_settings_from_database()
            
            # Create async Stellar server
            self.server = ServerAsync(horizon_url=self.horizon_url)
            self.ubec_asset = Asset(self.ubec_code, self.ubec_issuer)
            
            logger.info(f"✓ Connected to Stellar: {self.horizon_url}")
            logger.info(f"  Token: {self.ubec_code}")
            logger.info(f"  Issuer: {self.ubec_issuer}")
            
        except ImportError:
            logger.warning("⚠ Stellar SDK not available - blockchain queries disabled")
            self.server = None
    
    async def initialize(self):
        """
        Initialize synchronizer - load settings and connect to Stellar.
        Must be called before using the synchronizer.
        """
        logger.info("Initializing UBEC Data Synchronizer...")
        
        # Load settings from database
        await self._load_settings_from_database()
        
        # Load accounts from database
        await self._load_accounts_from_database()
        
        # Initialize Stellar connection
        await self._initialize_stellar_connection()
        
        # Create HTTP session
        self.session = aiohttp.ClientSession()
        
        logger.info("✓ UBEC Data Synchronizer fully initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        if self.server:
            await self.server.close()
    
    async def close(self):
        """Close connections and clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("HTTP session closed")
        
        if self.server:
            await self.server.close()
            logger.info("Stellar connection closed")
    
    def _get_issuer_for_token(self, asset_code: str) -> str:
        """
        Get the correct issuer for a given token code.
        
        Args:
            asset_code: Token code ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
        
        Returns:
            Issuer account ID for the token
        """
        issuer_map = {
            'UBEC': self.ubec_issuer,
            'UBECrc': self.ubecrc_issuer,
            'UBECgpi': self.ubecgpi_issuer,
            'UBECtt': self.ubectt_issuer
        }
        
        issuer = issuer_map.get(asset_code, self.ubec_issuer)
        logger.debug(f"Token {asset_code} -> Issuer {issuer}")
        return issuer
    
    # ========================================================================
    # RATE LIMITING - ASYNC VERSION
    # ========================================================================
    
    def _update_rate_limits(self, response_headers: Dict[str, str]):
        """
        Update rate limit information from API response headers.
        
        Args:
            response_headers: HTTP response headers from Stellar API
        """
        try:
            self.rate_limit_remaining = int(response_headers.get('X-Ratelimit-Remaining', 3000))
            self.rate_limit_limit = int(response_headers.get('X-Ratelimit-Limit', 3000))
            self.rate_limit_reset = int(response_headers.get('X-Ratelimit-Reset', 0))
            
            logger.debug(
                f"Rate limits updated: {self.rate_limit_remaining}/{self.rate_limit_limit} "
                f"(resets at {self.rate_limit_reset})"
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse rate limit headers: {e}")
    
    async def _check_rate_limit(self):
        """
        Check if we're approaching rate limits and wait if necessary.
        Implements async waiting when rate limit is low.
        """
        if self.rate_limit_remaining < 100:
            current_time = int(datetime.now().timestamp())
            
            if self.rate_limit_reset > current_time:
                wait_time = self.rate_limit_reset - current_time + 1
                logger.warning(
                    f"Approaching rate limit ({self.rate_limit_remaining} remaining). "
                    f"Waiting {wait_time} seconds..."
                )
                await asyncio.sleep(wait_time)
            else:
                # Reset has passed, wait a short time for limits to refresh
                logger.warning(
                    f"Rate limit low ({self.rate_limit_remaining}), waiting 5 seconds for refresh..."
                )
                await asyncio.sleep(5)
    
    # ========================================================================
    # ACCOUNT SYNCHRONIZATION
    # ========================================================================
    
    async def sync_account(self, account_id: str) -> bool:
        """
        Synchronize a single account's data from Stellar to database.
        
        Args:
            account_id: Stellar account ID to synchronize
            
        Returns:
            bool: True if sync successful, False otherwise
        """
        try:
            logger.info(f"Syncing account: {account_id}")
            
            # Check rate limits
            await self._check_rate_limit()
            
            # Fetch account data from Stellar
            if not self.server:
                logger.error("Stellar server not initialized")
                return False
            
            account = await self.server.accounts().account_id(account_id).call()
            
            # Update rate limits from response
            if hasattr(account, 'headers'):
                self._update_rate_limits(account.headers)
            
            # Store account in database
            await self._store_account(account)
            
            # Store balances (only UBEC family tokens)
            await self._store_balances(account_id, account.get('balances', []))
            
            logger.info(f"✓ Account synced successfully: {account_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing account {account_id}: {e}")
            return False
    
    async def _store_account(self, account_data: Dict):
        """
        Store or update account in database.
        
        Args:
            account_data: Account data from Stellar API
        """
        try:
            account_id = account_data['id']
            
            query = """
                INSERT INTO stellar_accounts (
                    account_id, sequence, subentry_count, home_domain,
                    last_modified_at, sync_status
                )
                VALUES ($1, $2, $3, $4, NOW(), 'synced')
                ON CONFLICT (account_id) DO UPDATE SET
                    sequence = EXCLUDED.sequence,
                    subentry_count = EXCLUDED.subentry_count,
                    home_domain = EXCLUDED.home_domain,
                    last_modified_at = NOW(),
                    sync_status = 'synced'
            """
            
            params = (
                account_id,
                int(account_data.get('sequence', '0')),
                int(account_data.get('subentry_count', 0)),
                account_data.get('home_domain')
            )
            
            await self.db.execute(query, params)
            logger.debug(f"Account stored: {account_id}")
            
        except Exception as e:
            logger.error(f"Error storing account {account_data.get('id')}: {e}")
            raise
    
    async def _store_balances(self, account_id: str, balances: List[Dict]):
        """
        Store account balances in database - ONLY UBEC family tokens.
        
        This method filters for UBEC, UBECrc, UBECgpi, and UBECtt tokens only.
        XLM and other assets are explicitly excluded to match database constraints.
        
        Args:
            account_id: Stellar account ID
            balances: List of balance records from Stellar API
        """
        try:
            stored_count = 0
            skipped_count = 0
            
            for balance in balances:
                # Determine token info
                if balance['asset_type'] == 'native':
                    token_code = 'XLM'
                else:
                    token_code = balance.get('asset_code', 'UNKNOWN')
                
                # CRITICAL FIX: Only store UBEC family tokens
                # Skip XLM and any other assets
                if token_code not in self.VALID_UBEC_TOKENS:
                    skipped_count += 1
                    logger.debug(f"Skipping non-UBEC token: {token_code} for account {account_id}")
                    continue
                
                # Get element for this UBEC token
                element = self.ELEMENT_MAP.get(token_code, 'air')  # Default to air if not found
                
                # Calculate numeric balance
                balance_amount = Decimal(balance.get('balance', '0'))
                
                # Get authorization flags
                is_authorized = balance.get('is_authorized', False)
                is_auth_maintain = balance.get('is_authorized_to_maintain_liabilities', False)
                is_clawback = balance.get('is_clawback_enabled', False)
                
                query = """
                    INSERT INTO ubec_balances (
                        account_id, token_code, element,
                        balance, limit_amount, 
                        buying_liabilities, selling_liabilities,
                        is_authorized, is_authorized_to_maintain_liabilities, 
                        is_clawback_enabled
                    )
                    VALUES (
                        $1, $2::ubec_main.token_code, $3::ubec_main.element_type,
                        $4, $5,
                        $6, $7,
                        $8, $9, $10
                    )
                    ON CONFLICT (account_id, token_code) DO UPDATE SET
                        balance = EXCLUDED.balance,
                        limit_amount = EXCLUDED.limit_amount,
                        buying_liabilities = EXCLUDED.buying_liabilities,
                        selling_liabilities = EXCLUDED.selling_liabilities,
                        is_authorized = EXCLUDED.is_authorized,
                        is_authorized_to_maintain_liabilities = EXCLUDED.is_authorized_to_maintain_liabilities,
                        is_clawback_enabled = EXCLUDED.is_clawback_enabled,
                        last_modified_at = CURRENT_TIMESTAMP
                """
                
                params = (
                    account_id,
                    token_code,
                    element,
                    balance_amount,
                    Decimal(balance.get('limit', '0')) if 'limit' in balance else None,
                    Decimal(balance.get('buying_liabilities', '0')),
                    Decimal(balance.get('selling_liabilities', '0')),
                    is_authorized,
                    is_auth_maintain,
                    is_clawback
                )
                
                await self.db.execute(query, params)
                stored_count += 1
            
            logger.debug(
                f"Balance storage for {account_id}: "
                f"{stored_count} UBEC tokens stored, {skipped_count} non-UBEC assets skipped"
            )
            
        except Exception as e:
            logger.error(f"Error storing balances for {account_id}: {e}")
            raise

    async def sync_transactions(
        self,
        account_id: str,
        limit: int = 200,
        cursor: Optional[str] = None
    ) -> int:
        """
        Synchronize transactions for an account.
        
        Args:
            account_id: Stellar account ID
            limit: Maximum transactions to fetch
            cursor: Starting cursor for pagination
            
        Returns:
            int: Number of transactions synchronized
        """
        try:
            logger.info(f"Syncing transactions for {account_id} (limit: {limit})")
            
            if not self.server:
                logger.error("Stellar server not initialized")
                return 0
            
            # Check rate limits
            await self._check_rate_limit()
            
            # Build request
            request = self.server.transactions().for_account(account_id).limit(limit)
            
            if cursor:
                request = request.cursor(cursor)
            
            # Fetch transactions
            response = await request.call()
            
            # Update rate limits
            if hasattr(response, 'headers'):
                self._update_rate_limits(response.headers)
            
            # Store transactions
            transactions = response.get('_embedded', {}).get('records', [])
            
            for tx in transactions:
                await self._ensure_account_exists(tx['source_account'])
                await self._store_transaction(tx)
            
            logger.info(f"✓ Synced {len(transactions)} transactions for {account_id}")
            return len(transactions)
            
        except Exception as e:
            logger.error(f"Error syncing transactions for {account_id}: {e}")
            return 0
    
    async def _ensure_account_exists(self, account_id: str):
        """
        Ensure an account record exists in the database before storing related data.
        
        Args:
            account_id: Stellar account ID
        """
        try:
            query = """
                INSERT INTO stellar_accounts (account_id, sync_status)
                VALUES ($1, 'partial')
                ON CONFLICT (account_id) DO NOTHING
            """
            await self.db.execute(query, (account_id,))
            
        except Exception as e:
            logger.error(f"Error ensuring account exists {account_id}: {e}")
            raise
    
    async def _store_transaction(self, tx_data: Dict):
        """
        Store transaction in database.
        
        Args:
            tx_data: Transaction data from Stellar API
            
        Note:
            The created_at field from Stellar is an ISO 8601 string.
            Datetime conversion is handled automatically by database_manager.py
            for proper asyncpg compatibility.
        """
        try:
            query = """
                INSERT INTO stellar_transactions (
                    transaction_hash, ledger_sequence, created_at, source_account,
                    fee_charged, operation_count, memo_type, memo,
                    successful, result_code
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (transaction_hash) DO UPDATE SET
                    successful = EXCLUDED.successful,
                    result_code = EXCLUDED.result_code
            """
            
            # FIXED: Use 'ledger_sequence' instead of 'ledger' to match database schema
            # The created_at is passed as ISO 8601 string - database_manager.py 
            # will automatically convert it to datetime for asyncpg
            params = (
                tx_data['hash'],
                tx_data.get('ledger_sequence', 0),  # FIXED: was 'ledger'
                tx_data.get('created_at'),  # ISO 8601 string - auto-converted by database_manager
                tx_data.get('source_account'),
                int(tx_data.get('fee_charged', 0)),
                tx_data.get('operation_count', 0),
                tx_data.get('memo_type'),
                tx_data.get('memo'),
                tx_data.get('successful', True),
                tx_data.get('result_xdr', '')[:100] if tx_data.get('result_xdr') else None
            )
            
            await self.db.execute(query, params)
            logger.debug(f"Transaction stored: {tx_data['hash']}")
            
        except Exception as e:
            logger.error(f"Error storing transaction {tx_data.get('hash')}: {e}")
            raise
    
    # ========================================================================
    # ACCOUNT DISCOVERY
    # ========================================================================
    
    async def discover_asset_holders(
        self,
        asset_code: str,
        limit: int = 200,
        max_accounts: int = 1000
    ) -> int:
        """
        Discover accounts holding a specific asset from Stellar network.
        
        Args:
            asset_code: Asset code to search for (UBEC, UBECrc, UBECgpi, UBECtt)
            limit: Records per page
            max_accounts: Maximum accounts to discover
            
        Returns:
            int: Number of accounts discovered
        """
        if not self.server:
            logger.error("Stellar server not initialized")
            return 0
        
        logger.info(f"Discovering holders of {asset_code}...")
        
        try:
            discovered = 0
            cursor = None
            
            # Get the CORRECT issuer for this specific token
            asset_issuer = self._get_issuer_for_token(asset_code)
            
            logger.info(f"Using issuer: {asset_issuer} for {asset_code}")
            
            # Import Asset class
            from stellar_sdk import Asset
            
            # Create Asset object with the CORRECT issuer
            asset = Asset(asset_code, asset_issuer)
            
            while discovered < max_accounts:
                # Check rate limits
                await self._check_rate_limit()
                
                # Build request
                request = self.server.accounts().for_asset(asset).limit(limit)
                
                if cursor:
                    request = request.cursor(cursor)
                
                # Fetch accounts
                try:
                    response = await request.call()
                except Exception as e:
                    logger.error(f"Error fetching accounts: {e}")
                    break
                
                # Update rate limits
                if hasattr(response, '_headers'):
                    self._update_rate_limits(response._headers)
                
                # Get records
                records = response.get('_embedded', {}).get('records', [])
                
                if not records:
                    logger.info(f"No more {asset_code} holders found")
                    break
                
                # Process each account
                for account_data in records:
                    try:
                        # Store account
                        await self._store_account(account_data)
                        
                        # Store balances (only UBEC tokens will be stored)
                        balances = account_data.get('balances', [])
                        await self._store_balances(account_data['id'], balances)
                        
                        discovered += 1
                        
                        if discovered % 50 == 0:
                            logger.info(f"  Discovered {discovered} {asset_code} holders...")
                        
                    except Exception as e:
                        logger.error(f"Error processing account {account_data.get('id')}: {e}")
                        continue
                
                # Check if there are more pages
                next_link = response.get('_links', {}).get('next', {}).get('href')
                if not next_link or discovered >= max_accounts:
                    break
                
                # Extract cursor for next page
                if 'cursor=' in next_link:
                    cursor = next_link.split('cursor=')[1].split('&')[0]
                else:
                    break
                
                # Small delay between pages
                await asyncio.sleep(0.5)
            
            logger.info(f"✓ Discovered {discovered} holders of {asset_code}")
            return discovered
            
        except Exception as e:
            logger.error(f"Error discovering {asset_code} holders: {e}")
            return 0
    
    async def discover_all_ubec_holders(self, max_per_asset: int = 1000) -> Dict[str, int]:
        """
        Discover all holders of all 4 UBEC tokens.
        
        Args:
            max_per_asset: Maximum accounts to discover per asset
            
        Returns:
            dict: Discovery results per asset
        """
        logger.info("="*70)
        logger.info("Discovering All UBEC Token Holders")
        logger.info("="*70)
        
        results = {}
        assets = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']
        
        for asset_code in assets:
            logger.info(f"\nSearching for {asset_code} holders...")
            count = await self.discover_asset_holders(
                asset_code=asset_code,
                limit=200,
                max_accounts=max_per_asset
            )
            results[asset_code] = count
        
        total = sum(results.values())
        logger.info("="*70)
        logger.info(f"Discovery Complete: {total} total account records")
        for asset, count in results.items():
            logger.info(f"  {asset}: {count} holders")
        logger.info("="*70)
        
        return results

    # ========================================================================
    # BULK SYNCHRONIZATION METHODS
    # ========================================================================
    
    async def sync_account_data(
        self,
        asset_code: str = 'UBEC',
        limit: Optional[int] = 5000
    ) -> Dict[str, Any]:
        """
        Synchronize account data for all holders of a specific asset.
        
        Args:
            asset_code: Asset code to sync (UBEC, UBECrc, UBECgpi, UBECtt)
            limit: Maximum accounts to sync (default: 5000)
                   Set to None for unlimited sync (use cautiously with rate limits)
            
        Returns:
            dict: Sync results with counts
            
        Note:
            This syncs full account details from Stellar (sequence, subentry_count, etc.)
            If you only need balance updates, use sync_balance_data() instead.
            
        Examples:
            # Sync up to 1000 accounts
            result = await sync.sync_account_data('UBEC', limit=1000)
            
            # Sync ALL accounts (no limit)
            result = await sync.sync_account_data('UBEC', limit=None)
        """
        logger.info(f"Syncing account data for {asset_code} holders (limit: {limit})...")
        
        try:
            # Get all accounts that hold this token from database
            if limit is None:
                # Unlimited - fetch all accounts
                query = """
                    SELECT DISTINCT account_id
                    FROM ubec_balances
                    WHERE token_code = $1
                """
                rows = await self.db.fetch_all(query, (asset_code,))
            else:
                # Limited - fetch up to limit
                query = """
                    SELECT DISTINCT account_id
                    FROM ubec_balances
                    WHERE token_code = $1
                    LIMIT $2
                """
                rows = await self.db.fetch_all(query, (asset_code, limit))
            
            if not rows:
                logger.warning(f"No accounts found holding {asset_code}")
                return {
                    'success': True,
                    'asset_code': asset_code,
                    'accounts_synced': 0,
                    'message': f'No accounts found holding {asset_code}'
                }
            
            synced = 0
            failed = 0
            
            for row in rows:
                account_id = row['account_id']
                success = await self.sync_account(account_id)
                
                if success:
                    synced += 1
                else:
                    failed += 1
                
                # Progress logging
                if (synced + failed) % 50 == 0:
                    logger.info(f"  Progress: {synced + failed}/{len(rows)} accounts processed")
            
            logger.info(f"✓ Account sync complete: {synced} synced, {failed} failed")
            
            return {
                'success': True,
                'asset_code': asset_code,
                'accounts_synced': synced,
                'accounts_failed': failed,
                'total_accounts': len(rows)
            }
            
        except Exception as e:
            logger.error(f"Error syncing account data for {asset_code}: {e}")
            return {
                'success': False,
                'asset_code': asset_code,
                'error': str(e)
            }
    
    async def sync_balance_data(
        self,
        asset_code: str = 'UBEC'
    ) -> Dict[str, Any]:
        """
        Synchronize balance data for all holders of a specific asset.
        
        This updates the balance information for all accounts holding the asset.
        Note: sync_account() already syncs balances, so this is complementary.
        
        Args:
            asset_code: Asset code to sync (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            dict: Sync results with counts
        """
        logger.info(f"Syncing balance data for {asset_code}...")
        
        try:
            # Get all accounts that hold this token
            query = """
                SELECT DISTINCT account_id
                FROM ubec_balances
                WHERE token_code = $1
            """
            
            rows = await self.db.fetch_all(query, (asset_code,))
            
            if not rows:
                logger.warning(f"No balances found for {asset_code}")
                return {
                    'success': True,
                    'asset_code': asset_code,
                    'balances_synced': 0,
                    'message': f'No balances found for {asset_code}'
                }
            
            synced = 0
            failed = 0
            
            # Sync each account (which includes balance updates)
            for row in rows:
                account_id = row['account_id']
                
                try:
                    # Fetch fresh account data from Stellar
                    if not self.server:
                        logger.error("Stellar server not initialized")
                        failed += 1
                        continue
                    
                    await self._check_rate_limit()
                    account = await self.server.accounts().account_id(account_id).call()
                    
                    # Update balances
                    await self._store_balances(account_id, account.get('balances', []))
                    synced += 1
                    
                    if synced % 50 == 0:
                        logger.info(f"  Progress: {synced}/{len(rows)} balances synced")
                    
                except Exception as e:
                    logger.error(f"Error syncing balance for {account_id}: {e}")
                    failed += 1
                    continue
            
            logger.info(f"✓ Balance sync complete: {synced} synced, {failed} failed")
            
            return {
                'success': True,
                'asset_code': asset_code,
                'balances_synced': synced,
                'balances_failed': failed,
                'total_balances': len(rows)
            }
            
        except Exception as e:
            logger.error(f"Error syncing balance data for {asset_code}: {e}")
            return {
                'success': False,
                'asset_code': asset_code,
                'error': str(e)
            }
    
    async def sync_transaction_data(
        self,
        asset_code: str = 'UBEC',
        days_back: int = 7,
        limit_per_account: int = 100
    ) -> Dict[str, Any]:
        """
        Synchronize recent transactions for all holders of a specific asset.
        
        Args:
            asset_code: Asset code to sync (UBEC, UBECrc, UBECgpi, UBECtt)
            days_back: Number of days of transaction history to sync
            limit_per_account: Maximum transactions per account
            
        Returns:
            dict: Sync results with counts
        """
        logger.info(f"Syncing transaction data for {asset_code} holders (last {days_back} days)...")
        
        try:
            # Get all accounts that hold this token
            query = """
                SELECT DISTINCT account_id
                FROM ubec_balances
                WHERE token_code = $1
            """
            
            rows = await self.db.fetch_all(query, (asset_code,))
            
            if not rows:
                logger.warning(f"No accounts found holding {asset_code}")
                return {
                    'success': True,
                    'asset_code': asset_code,
                    'transactions_synced': 0,
                    'message': f'No accounts found holding {asset_code}'
                }
            
            total_transactions = 0
            accounts_processed = 0
            accounts_failed = 0
            
            # Sync transactions for each account
            for row in rows:
                account_id = row['account_id']
                
                try:
                    tx_count = await self.sync_transactions(
                        account_id=account_id,
                        limit=limit_per_account
                    )
                    
                    total_transactions += tx_count
                    accounts_processed += 1
                    
                    if accounts_processed % 20 == 0:
                        logger.info(
                            f"  Progress: {accounts_processed}/{len(rows)} accounts, "
                            f"{total_transactions} transactions synced"
                        )
                    
                except Exception as e:
                    logger.error(f"Error syncing transactions for {account_id}: {e}")
                    accounts_failed += 1
                    continue
            
            logger.info(
                f"✓ Transaction sync complete: {total_transactions} transactions from "
                f"{accounts_processed} accounts ({accounts_failed} failed)"
            )
            
            return {
                'success': True,
                'asset_code': asset_code,
                'transactions_synced': total_transactions,
                'accounts_processed': accounts_processed,
                'accounts_failed': accounts_failed,
                'total_accounts': len(rows)
            }
            
        except Exception as e:
            logger.error(f"Error syncing transaction data for {asset_code}: {e}")
            return {
                'success': False,
                'asset_code': asset_code,
                'error': str(e)
            }

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current synchronization status.
        
        Returns:
            dict: Synchronization statistics
        """
        try:
            stats = {}
            
            # Count accounts
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM stellar_accounts")
            stats['total_accounts'] = result['count'] if result else 0
            
            # Count balances
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM ubec_balances")
            stats['total_balances'] = result['count'] if result else 0
            
            # Count transactions
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM stellar_transactions")
            stats['total_transactions'] = result['count'] if result else 0
            
            # Get last activity time
            result = await self.db.fetch_one(
                "SELECT MAX(last_activity_at) as last_activity FROM stellar_accounts"
            )
            stats['last_sync_time'] = result['last_activity'] if result and result['last_activity'] else 'Never'
            
            # Rate limit info
            stats['rate_limit'] = {
                'remaining': self.rate_limit_remaining,
                'limit': self.rate_limit_limit,
                'reset_time': self.rate_limit_reset
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            dict: Health status information
        """
        health = {
            'status': 'unknown',
            'database': False,
            'stellar': False,
            'settings_loaded': bool(self.settings),
            'accounts_loaded': len(self.accounts)
        }
        
        try:
            # Check database
            result = await self.db.fetch_one("SELECT 1 as test")
            health['database'] = result is not None
            
            # Check Stellar connection
            if self.server:
                try:
                    # Simple ledger query to test connection
                    await self.server.ledgers().limit(1).call()
                    health['stellar'] = True
                except:
                    health['stellar'] = False
            
            # Determine overall status
            if health['database'] and health['stellar'] and health['settings_loaded']:
                health['status'] = 'healthy'
            elif health['database']:
                health['status'] = 'degraded'
            else:
                health['status'] = 'unhealthy'
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
        
        return health


# ==================== MODULE EXPORTS ====================

__all__ = [
    'UBECDataSynchronizer',
    'SyncException',
    'RateLimitException'
]
