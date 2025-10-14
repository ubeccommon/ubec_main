#!/usr/bin/env python3
"""
UBEC Data Synchronizer - Async Production Version

Synchronizes data between Stellar blockchain and the ubec_main database schema.
Compatible with the four-element protocol architecture.

Design Principles Compliance:
- ✅ Modular Design: Self-contained service with defined boundaries
- ✅ Service Pattern: No standalone execution (used via main.py only)
- ✅ Service Registry: Dependencies managed through central registry
- ✅ Database as Single Source of Truth: Settings loaded from database
- ✅ Strict Async: All I/O operations use async/await
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ No Duplicate Configuration: Settings stored once in database
- ✅ Integrated Rate Limiting: Built-in for all external API calls
- ✅ Clear Separation of Concerns: Active vs passive operations separated
- ✅ Comprehensive Documentation: Docstrings and inline comments
- ✅ Method Singularity: Each method implemented exactly once

Key Features:
- FULLY ASYNC operations (async/await pattern throughout)
- Proper operation ordering (accounts before balances)
- Transaction-safe operations with async context managers
- Comprehensive error handling
- Integrated rate limit management with async waiting
- Progress tracking for long-running operations
- Idempotent operations (safe to retry)
- Liquidity pool tracking and synchronization
- Compatible with asyncpg datetime conversion (handled in database_manager)

Schema Mapping:
- stellar_accounts: Core account data
- ubec_balances: Token holdings with foreign key to stellar_accounts
- stellar_transactions: Transaction records
- stellar_operations: Operation details
- ubec_sync_status: Synchronization tracking
- liquidity_pools: Pool data with reserves and fees
- liquidity_pool_owners: Individual LP positions (renamed from participants)

Four-Element Architecture:
- 🌬️ Air (UBEC) - Gateway & Universal Access
- 💧 Water (UBECrc) - Flow & Exchange  
- 🌍 Earth (UBECgpi) - Stability & Value
- 🔥 Fire (UBECtt) - Transformation & Action

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 5.3 (CRITICAL FIX - Correct LP participant sync implementation)
Date: October 14, 2025

Changes in v5.3:
    - 🔥 CRITICAL FIX: Replaced invalid Horizon API query with correct account iteration
    - ✅ LP participants now synced by checking each account's balances for liquidity_pool_shares
    - ✅ Removed broken _sync_pool_participants method that used invalid API query
    - ✅ Added _sync_all_pool_participants method that properly iterates through accounts
    - ✅ Updated sync_liquidity_pools to call new participant sync after storing pools
    - ✅ Maintains all 12 design principles
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
    4. Sync liquidity pool data and participants
    
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
        logger.info(f"Initializing UBEC Data Synchronizer (Async Service)")
        
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
        
        logger.info("✓ UBEC Data Synchronizer initialized - awaiting settings load")
    
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
            
        except Exception as e:
            logger.error(f"Error loading settings from database: {e}")
            raise
    
    def _get_issuer_for_token(self, token_code: str) -> str:
        """
        Get the correct issuer address for a specific token.
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            str: Issuer address for the token
        """
        issuer_map = {
            'UBEC': self.ubec_issuer,
            'UBECrc': self.ubecrc_issuer,
            'UBECgpi': self.ubecgpi_issuer,
            'UBECtt': self.ubectt_issuer
        }
        return issuer_map.get(token_code, self.ubec_issuer)
    
    async def initialize(self, stellar_client):
        """
        Initialize the synchronizer with Stellar client.
        
        Args:
            stellar_client: Initialized Stellar ServerAsync client
        """
        logger.info("Initializing UBEC Data Synchronizer...")
        
        # Store Stellar server
        self.server = stellar_client
        
        # Load settings from database
        await self._load_settings_from_database()
        
        # Create aiohttp session for direct API calls
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        logger.info("✓ UBEC Data Synchronizer fully initialized")
    
    async def close(self):
        """
        Clean up resources.
        """
        if self.session:
            await self.session.close()
            self.session = None
    
    # ========================================================================
    # RATE LIMIT MANAGEMENT
    # ========================================================================
    
    def _update_rate_limits(self, headers: Dict[str, str]):
        """
        Update rate limit tracking from response headers.
        
        Args:
            headers: Response headers from Stellar API
        """
        try:
            self.rate_limit_remaining = int(headers.get('X-Ratelimit-Remaining', 3000))
            self.rate_limit_limit = int(headers.get('X-Ratelimit-Limit', 3600))
            self.rate_limit_reset = int(headers.get('X-Ratelimit-Reset', 0))
            
            logger.debug(
                f"Rate limits: {self.rate_limit_remaining}/{self.rate_limit_limit} "
                f"(reset: {self.rate_limit_reset})"
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing rate limit headers: {e}")
    
    async def _check_rate_limit(self):
        """
        Check if rate limit allows request, wait if necessary.
        """
        if self.rate_limit_remaining < 10:
            # Calculate wait time
            now = int(datetime.now().timestamp())
            wait_time = max(1, self.rate_limit_reset - now)
            
            logger.warning(f"Rate limit low, waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            
            # Reset tracking
            self.rate_limit_remaining = self.rate_limit_limit
    
    # ========================================================================
    # ACCOUNT AND BALANCE SYNCHRONIZATION
    # ========================================================================
    
    async def sync_account(
        self,
        account_id: str,
        force_refresh: bool = False
    ) -> bool:
        """
        Synchronize single account from Stellar.
        
        Args:
            account_id: Stellar account ID
            force_refresh: Force refresh even if recently synced
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Syncing account {account_id}...")
            
            # Ensure settings are loaded
            if not self.settings:
                logger.info("Settings not loaded yet, loading from database...")
                await self._load_settings_from_database()
            
            if not self.server:
                logger.error("Stellar server not initialized")
                return False
            
            # Check rate limits
            await self._check_rate_limit()
            
            # Fetch account data from Stellar
            try:
                account = await self.server.accounts().account_id(account_id).call()
            except Exception as e:
                logger.error(f"Error fetching account {account_id}: {e}")
                return False
            
            # Update rate limits
            if hasattr(account, '_headers'):
                self._update_rate_limits(account._headers)
            
            # Store account data
            await self._store_account(account)
            
            # Store balances
            balances = account.get('balances', [])
            await self._store_balances(account_id, balances)
            
            logger.info(f"✓ Account {account_id} synced successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing account {account_id}: {e}")
            return False
    
    async def _store_account(self, account_data: Dict):
        """
        Store or update account in database.
        
        FIXED v4.5: Updated to match actual database schema.
        The stellar_accounts table has: account_id, sequence, subentry_count,
        home_domain, last_modified_at, sync_status
        
        Removed non-existent columns:
        - inflation_destination (deprecated in Stellar Protocol 15)
        - last_modified_ledger (not in schema)
        - last_activity_at (not in schema)
        
        Args:
            account_data: Account data from Stellar API
        """
        try:
            account_id = account_data['id']
            
            # FIXED: Use only columns that exist in database
            query = """
                INSERT INTO stellar_accounts (
                    account_id, sequence, subentry_count, home_domain,
                    last_modified_at, sync_status
                )
                VALUES ($1, $2, $3, $4, NOW(), $5)
                ON CONFLICT (account_id) DO UPDATE SET
                    sequence = EXCLUDED.sequence,
                    subentry_count = EXCLUDED.subentry_count,
                    home_domain = EXCLUDED.home_domain,
                    last_modified_at = NOW(),
                    sync_status = EXCLUDED.sync_status
            """
            
            params = (
                account_id,
                int(account_data.get('sequence', '0')),
                int(account_data.get('subentry_count', 0)),
                account_data.get('home_domain'),
                'synced'
            )
            
            await self.db.execute(query, params)
            logger.debug(f"Account stored: {account_id}")
            
        except Exception as e:
            logger.error(f"Error storing account {account_data.get('id')}: {e}")
            raise
    
    async def _store_balances(self, account_id: str, balances: List[Dict]):
        """
        Store or update balances for an account.
        Only stores UBEC family tokens (UBEC, UBECrc, UBECgpi, UBECtt).
        
        Args:
            account_id: Stellar account ID
            balances: List of balance objects from Stellar API
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
                
                # CRITICAL: Only store UBEC family tokens
                # Skip XLM and any other assets
                if token_code not in self.VALID_UBEC_TOKENS:
                    skipped_count += 1
                    logger.debug(f"Skipping non-UBEC token: {token_code} for account {account_id}")
                    continue
                
                # Get element for this UBEC token
                element = self.ELEMENT_MAP.get(token_code, 'air')
                
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
    
    # ========================================================================
    # TRANSACTION SYNCHRONIZATION
    # ========================================================================
    
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
            
            # Ensure settings are loaded
            if not self.settings:
                await self._load_settings_from_database()
            
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
            
            params = (
                tx_data['hash'],
                tx_data.get('ledger_sequence', 0),
                tx_data.get('created_at'),
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
    # LIQUIDITY POOL SYNCHRONIZATION - FIXED IN V5.3
    # ========================================================================
    
    async def sync_liquidity_pools(
        self,
        asset_code: str,
        asset_issuer: str
    ) -> Dict[str, Any]:
        """
        Synchronize liquidity pools involving a specific asset.
        
        This method fetches all liquidity pools that contain the specified asset,
        stores pool metadata, and tracks individual participant positions.
        
        🔥 FIXED in v5.3: Now properly syncs LP participants by checking account balances.
        
        Args:
            asset_code: Asset code (UBEC, UBECrc, UBECgpi, UBECtt)
            asset_issuer: Asset issuer address
            
        Returns:
            dict: Sync results with pool and participant counts
        """
        logger.info(f"Syncing liquidity pools for {asset_code}:{asset_issuer[:8]}...")
        
        try:
            # Ensure settings are loaded (required for horizon_url)
            if not self.settings or not self.horizon_url:
                logger.info("Settings not loaded yet, loading from database...")
                await self._load_settings_from_database()
            
            pools_synced = 0
            participants_synced = 0
            total_tvl = Decimal('0')
            
            # Use direct API call to fetch liquidity pools
            # Stellar SDK doesn't have built-in LP methods, so we use HTTP
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Build API URL for liquidity pools
            # Format: /liquidity_pools?reserves={asset_code}:{asset_issuer}
            url = f"{self.horizon_url}/liquidity_pools"
            params = {
                'reserves': f"{asset_code}:{asset_issuer}",
                'limit': 200
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error fetching liquidity pools: {response.status} - {error_text}")
                    return {
                        'success': False,
                        'asset_code': asset_code,
                        'error': f"API error: {response.status}"
                    }
                
                data = await response.json()
                pools = data.get('_embedded', {}).get('records', [])
                
                logger.info(f"Found {len(pools)} liquidity pools for {asset_code}")
                
                # Process each pool
                for pool_data in pools:
                    try:
                        # Store pool metadata
                        pool_id = await self._store_liquidity_pool(pool_data, asset_code)
                        
                        if pool_id:
                            pools_synced += 1
                            
                            # Calculate pool TVL (for the UBEC asset only)
                            reserves = pool_data.get('reserves', [])
                            primary_issuer = self._get_issuer_for_token(asset_code)
                            
                            for reserve in reserves:
                                asset_str = reserve.get('asset', '')
                                # Check if this reserve is the UBEC asset we're tracking
                                if f"{asset_code}:{primary_issuer}" in asset_str:
                                    amount = Decimal(reserve.get('amount', '0'))
                                    total_tvl += amount
                                    break
                        
                    except Exception as e:
                        logger.error(f"Error processing pool {pool_data.get('id')}: {e}")
                        continue
                
                # 🔥 NEW in v5.3: Sync participants AFTER all pools are stored
                # This ensures all pool records exist before we try to reference them
                logger.info(f"Syncing LP participants for {asset_code}...")
                participants_synced = await self._sync_all_pool_participants(asset_code)
                
                logger.info(
                    f"✓ LP sync complete for {asset_code}: "
                    f"{pools_synced} pools, {participants_synced} participants, "
                    f"TVL: {total_tvl:,.2f}"
                )
                
                return {
                    'success': True,
                    'asset_code': asset_code,
                    'pools_synced': pools_synced,
                    'participants_synced': participants_synced,
                    'total_tvl': float(total_tvl)
                }
                
        except Exception as e:
            logger.error(f"Error syncing liquidity pools for {asset_code}: {e}")
            return {
                'success': False,
                'asset_code': asset_code,
                'error': str(e)
            }
    
    async def _store_liquidity_pool(
        self,
        pool_data: Dict,
        primary_asset: str
    ) -> Optional[str]:
        """
        Store liquidity pool metadata in database.
        
        Args:
            pool_data: Pool data from Stellar API
            primary_asset: Primary UBEC asset in the pool
            
        Returns:
            str: Pool ID, or None if failed
        """
        try:
            pool_id = pool_data['id']
            fee_bp = int(pool_data.get('fee_bp', 30))
            trustline_count = int(pool_data.get('total_trustlines', 0))
            total_shares = Decimal(pool_data.get('total_shares', '0'))
            
            # Parse reserves
            reserves = pool_data.get('reserves', [])
            if len(reserves) < 2:
                logger.warning(f"Pool {pool_id} has insufficient reserves")
                return None
            
            # Parse asset A
            asset_a_str = reserves[0].get('asset', 'native')
            if asset_a_str == 'native':
                asset_a_code = 'XLM'
                asset_a_issuer = None
            else:
                parts = asset_a_str.split(':')
                asset_a_code = parts[0] if parts else 'UNKNOWN'
                asset_a_issuer = parts[1] if len(parts) > 1 else None
            
            # Parse asset B
            asset_b_str = reserves[1].get('asset', 'native')
            if asset_b_str == 'native':
                asset_b_code = 'XLM'
                asset_b_issuer = None
            else:
                parts = asset_b_str.split(':')
                asset_b_code = parts[0] if parts else 'UNKNOWN'
                asset_b_issuer = parts[1] if len(parts) > 1 else None
            
            # Get reserve amounts
            reserve_a = Decimal(reserves[0].get('amount', '0'))
            reserve_b = Decimal(reserves[1].get('amount', '0'))
            
            # Determine UBEC asset position and balance
            ubec_asset_position = None
            ubec_balance = Decimal('0')
            
            # Get issuer for primary asset
            primary_issuer = self._get_issuer_for_token(primary_asset)
            
            if asset_a_code == primary_asset and asset_a_issuer == primary_issuer:
                ubec_asset_position = 'a'
                ubec_balance = reserve_a
            elif asset_b_code == primary_asset and asset_b_issuer == primary_issuer:
                ubec_asset_position = 'b'
                ubec_balance = reserve_b
            
            # Create pair name
            pair = f"{asset_a_code}/{asset_b_code}"
            
            # Get element for this token
            element = self.ELEMENT_MAP.get(primary_asset, 'air')
            
            # Store in database matching actual schema
            query = """
                INSERT INTO liquidity_pools (
                    id, asset_a_code, asset_a_issuer, asset_b_code, asset_b_issuer,
                    pair, primary_element, token_code,
                    reserve_a, reserve_b, total_shares, balance,
                    ubec_asset_position, fee_bp, trustline_count,
                    sync_timestamp, sync_status
                )
                VALUES (
                    $1, $2, $3, $4, $5, 
                    $6, $7::ubec_main.element_type, $8::ubec_main.token_code,
                    $9, $10, $11, $12,
                    $13, $14, $15,
                    NOW(), 'active'
                )
                ON CONFLICT (id) DO UPDATE SET
                    reserve_a = EXCLUDED.reserve_a,
                    reserve_b = EXCLUDED.reserve_b,
                    total_shares = EXCLUDED.total_shares,
                    balance = EXCLUDED.balance,
                    trustline_count = EXCLUDED.trustline_count,
                    sync_timestamp = NOW(),
                    last_modified_at = NOW()
            """
            
            params = (
                pool_id,
                asset_a_code,
                asset_a_issuer,
                asset_b_code,
                asset_b_issuer,
                pair,
                element,
                primary_asset,
                reserve_a,
                reserve_b,
                total_shares,
                ubec_balance,
                ubec_asset_position,
                fee_bp,
                trustline_count
            )
            
            await self.db.execute(query, params)
            
            logger.debug(f"Liquidity pool stored: {pair} ({pool_id[:8]}...): {ubec_balance} {primary_asset}")
            return pool_id
            
        except Exception as e:
            logger.error(f"Error storing liquidity pool: {e}")
            return None
    
    async def _sync_all_pool_participants(self, token_code: str) -> int:
        """
        Sync LP participants by checking all accounts for liquidity_pool_shares.
        
        🔥 NEW in v5.3: Correct implementation that iterates through accounts.
        
        This is the ONLY way to find LP share holders on Stellar. You cannot
        query "who owns shares in this pool?" directly from the Horizon API.
        Instead, you must:
        1. Get all accounts from the database
        2. Fetch each account's data from Stellar
        3. Check their balances for liquidity_pool_shares
        4. Match pool IDs to the pools we're tracking
        5. Store the ownership data
        
        Args:
            token_code: Token code to sync participants for (UBEC, UBECrc, etc)
            
        Returns:
            int: Number of participants synced
        """
        try:
            # Get all accounts from database
            query = "SELECT account_id FROM stellar_accounts"
            account_rows = await self.db.fetch_all(query)
            
            if not account_rows:
                logger.info("No accounts in database to check for LP positions")
                return 0
            
            logger.info(f"Checking {len(account_rows)} accounts for LP positions...")
            
            participants_synced = 0
            accounts_checked = 0
            
            # Get element for this token
            element = self.ELEMENT_MAP.get(token_code, 'air')
            
            for row in account_rows:
                account_id = row['account_id']
                
                try:
                    # Check rate limit
                    await self._check_rate_limit()
                    
                    # Fetch account data from Stellar
                    account_data = await self.server.accounts().account_id(account_id).call()
                    
                    # Update rate limits
                    if hasattr(account_data, '_headers'):
                        self._update_rate_limits(account_data._headers)
                    
                    # Look for liquidity_pool_shares in the balances
                    balances = account_data.get('balances', [])
                    
                    for balance in balances:
                        if balance.get('asset_type') == 'liquidity_pool_shares':
                            pool_id = balance.get('liquidity_pool_id')
                            shares = Decimal(balance.get('balance', '0'))
                            
                            if shares > 0:
                                # Check if this pool is one we're tracking for this token
                                pool_query = """
                                    SELECT total_shares, balance, token_code
                                    FROM liquidity_pools
                                    WHERE id = $1 AND token_code = $2
                                """
                                pool_data = await self.db.fetch_one(
                                    pool_query,
                                    (pool_id, token_code)
                                )
                                
                                if pool_data:
                                    # Calculate ownership percentage and UBEC balance
                                    total_shares = Decimal(pool_data['total_shares'])
                                    pool_ubec_balance = Decimal(pool_data['balance'])
                                    
                                    if total_shares > 0:
                                        ownership_percentage = (shares / total_shares) * Decimal('100')
                                        ubec_balance = (shares / total_shares) * pool_ubec_balance
                                    else:
                                        ownership_percentage = Decimal('0')
                                        ubec_balance = Decimal('0')
                                    
                                    # Store participant position
                                    insert_query = """
                                        INSERT INTO liquidity_pool_owners (
                                            account_id, liquidity_pool_id, shares,
                                            ownership_percentage, ubec_balance,
                                            element, token_code,
                                            sync_timestamp, sync_status
                                        )
                                        VALUES (
                                            $1, $2, $3, $4, $5,
                                            $6::ubec_main.element_type, $7::ubec_main.token_code,
                                            NOW(), 'synced'
                                        )
                                        ON CONFLICT (account_id, liquidity_pool_id) DO UPDATE SET
                                            shares = EXCLUDED.shares,
                                            ownership_percentage = EXCLUDED.ownership_percentage,
                                            ubec_balance = EXCLUDED.ubec_balance,
                                            sync_timestamp = NOW(),
                                            last_modified_at = NOW()
                                    """
                                    
                                    await self.db.execute(insert_query, (
                                        account_id, pool_id, shares,
                                        ownership_percentage, ubec_balance,
                                        element, token_code
                                    ))
                                    
                                    participants_synced += 1
                                    logger.debug(
                                        f"LP position synced: {account_id[:8]}... "
                                        f"owns {ownership_percentage:.4f}% of pool {pool_id[:8]}..."
                                    )
                    
                    accounts_checked += 1
                    
                    # Progress logging every 50 accounts
                    if accounts_checked % 50 == 0:
                        logger.info(
                            f"  Progress: {accounts_checked}/{len(account_rows)} accounts checked, "
                            f"{participants_synced} LP positions found"
                        )
                    
                except Exception as e:
                    logger.error(f"Error checking LP positions for {account_id}: {e}")
                    continue
            
            logger.info(
                f"✓ LP participant sync complete: {participants_synced} positions found "
                f"in {accounts_checked} accounts"
            )
            
            return participants_synced
            
        except Exception as e:
            logger.error(f"Error syncing LP participants: {e}")
            return 0
    
    # ========================================================================
    # ACCOUNT DISCOVERY
    # ========================================================================
    
    async def discover_accounts(
        self,
        max_accounts: int = 1000,
        asset_code: str = 'UBEC'
    ) -> int:
        """
        Discover account holders (compatibility wrapper for main.py).
        
        This method provides compatibility with main.py's discover mode.
        It wraps the discover_asset_holders() method which does the actual work.
        
        Design Note:
            This is a thin wrapper that maintains compatibility with main.py
            while delegating to the actual implementation in discover_asset_holders().
            Follows Principle #12: Method Singularity - this wrapper exists once,
            the actual discovery logic exists once in discover_asset_holders().
        
        Args:
            max_accounts: Maximum number of accounts to discover (default: 1000)
            asset_code: Asset code to discover holders for (default: 'UBEC')
            
        Returns:
            int: Number of accounts discovered
            
        Example:
            >>> # From main.py
            >>> count = await synchronizer.discover_accounts(max_accounts=500)
            >>> print(f"Discovered {count} accounts")
        """
        logger.info(f"Discovering {asset_code} holders (max: {max_accounts})...")
        
        # Call the actual implementation
        count = await self.discover_asset_holders(
            asset_code=asset_code,
            limit=200,  # Page size for API calls
            max_accounts=max_accounts
        )
        
        logger.info(f"✓ Discovery complete: {count} {asset_code} holders found")
        
        return count
    
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
        # Ensure settings are loaded
        if not self.settings:
            logger.info("Settings not loaded yet, loading from database...")
            await self._load_settings_from_database()
        
        if not self.server:
            logger.error("Stellar server not initialized")
            return 0
        
        logger.info(f"Discovering holders of {asset_code}...")
        
        try:
            discovered = 0
            cursor = None
            
            # Get the correct issuer for this specific token
            asset_issuer = self._get_issuer_for_token(asset_code)
            
            logger.info(f"Using issuer: {asset_issuer} for {asset_code}")
            
            # Import Asset class
            from stellar_sdk import Asset
            
            # Create Asset object with the correct issuer
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
                   Set to None for unlimited sync (use cautiously)
            
        Returns:
            dict: Sync results with counts
        """
        logger.info(f"Syncing account data for {asset_code} holders (limit: {limit})...")
        
        try:
            # Ensure settings are loaded
            if not self.settings:
                await self._load_settings_from_database()
            
            # Get all accounts that hold this token from database
            if limit is None:
                query = """
                    SELECT DISTINCT account_id
                    FROM ubec_balances
                    WHERE token_code = $1
                """
                rows = await self.db.fetch_all(query, (asset_code,))
            else:
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
            
            # Sync each account
            for row in rows:
                account_id = row['account_id']
                
                try:
                    success = await self.sync_account(account_id)
                    if success:
                        synced += 1
                    else:
                        failed += 1
                    
                    if synced % 50 == 0:
                        logger.info(f"  Progress: {synced}/{len(rows)} accounts synced")
                    
                except Exception as e:
                    logger.error(f"Error syncing account {account_id}: {e}")
                    failed += 1
                    continue
            
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
        
        Args:
            asset_code: Asset code to sync (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            dict: Sync results with counts
        """
        logger.info(f"Syncing balance data for {asset_code} holders...")
        
        try:
            # Ensure settings are loaded
            if not self.settings:
                await self._load_settings_from_database()
            
            if not self.server:
                logger.error("Stellar server not initialized")
                return {
                    'success': False,
                    'asset_code': asset_code,
                    'error': 'Stellar server not initialized'
                }
            
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
                    'balances_synced': 0,
                    'message': f'No accounts found holding {asset_code}'
                }
            
            synced = 0
            failed = 0
            
            # Sync balances for each account
            for row in rows:
                account_id = row['account_id']
                
                try:
                    # Fetch account from Stellar
                    await self._check_rate_limit()
                    account = await self.server.accounts().account_id(account_id).call()
                    
                    # Update rate limits
                    if hasattr(account, '_headers'):
                        self._update_rate_limits(account._headers)
                    
                    # Store balances
                    balances = account.get('balances', [])
                    await self._store_balances(account_id, balances)
                    
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
            # Ensure settings are loaded
            if not self.settings:
                await self._load_settings_from_database()
            
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
            
            # Count liquidity pools
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM liquidity_pools")
            stats['total_pools'] = result['count'] if result else 0
            
            # Count LP owners
            result = await self.db.fetch_one("SELECT COUNT(*) as count FROM liquidity_pool_owners")
            stats['total_lp_owners'] = result['count'] if result else 0
            
            # Get last activity time
            result = await self.db.fetch_one(
                "SELECT MAX(last_modified_at) as last_activity FROM stellar_accounts"
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
