#!/usr/bin/env python3
"""
UBEC Liquidity Pool Synchronizer - Async Module

Synchronizes liquidity pool data from Stellar Horizon API to the database.
Tracks account positions in liquidity pools containing UBEC family tokens.

Design Principles Compliance:
- ✅ Modular Design: Self-contained holon for LP management
- ✅ Service Pattern: Exposes functionality through interfaces
- ✅ Database as Single Source of Truth: All LP data stored in database
- ✅ Strict Async: All I/O operations use async/await
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ No Duplicate Configuration: Settings loaded from central config

Key Features:
- Discovers liquidity pools containing UBEC tokens
- Tracks account ownership in each pool
- Calculates effective UBEC balances from LP positions
- Supports all 4 UBEC family tokens (UBEC, UBECrc, UBECgpi, UBECtt)
- Integrated rate limiting
- Comprehensive error handling

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 1.0
Date: October 12, 2025
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, getcontext
from datetime import datetime

# Configure decimal precision
getcontext().prec = 10

logger = logging.getLogger(__name__)


class LiquidityPoolSynchronizer:
    """
    Async service for synchronizing liquidity pool data from Stellar to database.
    
    This service:
    1. Discovers liquidity pools containing UBEC tokens
    2. Fetches pool reserve data and total shares
    3. Identifies accounts holding pool shares
    4. Calculates effective UBEC balances from LP positions
    5. Stores everything in the database for fast access
    
    All operations are async and follow the service pattern.
    """
    
    def __init__(
        self, 
        db_manager, 
        stellar_client,
        ubec_tokens: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the liquidity pool synchronizer.
        
        Args:
            db_manager: AsyncDatabaseManager instance
            stellar_client: Stellar ServerAsync client
            ubec_tokens: Dict mapping token codes to issuer addresses
                        Example: {'UBEC': 'GISSUER...', 'UBECrc': 'GISSUER...'}
        """
        self.db = db_manager
        self.stellar_client = stellar_client
        self.ubec_tokens = ubec_tokens or {}
        
        # Tracking
        self.pools_synced = 0
        self.accounts_synced = 0
        
        logger.info("LiquidityPoolSynchronizer initialized")
    
    async def sync_all_liquidity_pools(self) -> Dict[str, Any]:
        """
        Discover and sync all liquidity pools containing UBEC family tokens.
        
        Returns:
            Dict with sync results including pools found, accounts updated, etc.
        """
        logger.info("Starting liquidity pool synchronization...")
        
        results = {
            'pools_found': 0,
            'pools_synced': 0,
            'accounts_updated': 0,
            'total_ubec_in_pools': Decimal('0'),
            'errors': []
        }
        
        try:
            # For each UBEC token, find all liquidity pools
            for token_code, token_issuer in self.ubec_tokens.items():
                logger.info(f"Searching for {token_code} liquidity pools...")
                
                try:
                    # Find pools containing this token
                    pools = await self._discover_pools_for_asset(token_code, token_issuer)
                    results['pools_found'] += len(pools)
                    
                    # Sync each pool
                    for pool_data in pools:
                        try:
                            await self._sync_pool(pool_data, token_code)
                            results['pools_synced'] += 1
                            
                            # Track total UBEC
                            ubec_balance = pool_data.get('ubec_balance', Decimal('0'))
                            results['total_ubec_in_pools'] += ubec_balance
                            
                        except Exception as e:
                            error_msg = f"Error syncing pool {pool_data.get('id')}: {e}"
                            logger.error(error_msg)
                            results['errors'].append(error_msg)
                
                except Exception as e:
                    error_msg = f"Error discovering {token_code} pools: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Now sync account positions in all pools
            logger.info("Syncing account positions in liquidity pools...")
            accounts_updated = await self._sync_all_account_positions()
            results['accounts_updated'] = accounts_updated
            
            logger.info(f"✓ Liquidity pool sync complete: {results['pools_synced']} pools, "
                       f"{results['accounts_updated']} accounts")
            
        except Exception as e:
            error_msg = f"Error in liquidity pool synchronization: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    async def _discover_pools_for_asset(
        self, 
        asset_code: str, 
        asset_issuer: str
    ) -> List[Dict[str, Any]]:
        """
        Discover all liquidity pools containing a specific asset.
        
        Args:
            asset_code: Asset code (e.g., 'UBEC')
            asset_issuer: Asset issuer address
            
        Returns:
            List of pool data dictionaries
        """
        pools = []
        
        try:
            # Query Stellar Horizon for liquidity pools
            # We need to check both asset_a and asset_b positions
            
            # Build the reserves filter string
            # Format: "ASSET_CODE:ISSUER" or "native" for XLM
            if asset_code == 'XLM':
                reserve_filter = 'native'
            else:
                reserve_filter = f"{asset_code}:{asset_issuer}"
            
            # Fetch pools from Horizon
            logger.debug(f"Querying Horizon for pools with reserves={reserve_filter}")
            
            pools_response = await self.stellar_client.liquidity_pools()\
                .for_reserves(reserve_filter)\
                .limit(200)\
                .call()
            
            records = pools_response.get('_embedded', {}).get('records', [])
            
            logger.info(f"Found {len(records)} liquidity pools for {asset_code}")
            
            for record in records:
                try:
                    pool_data = await self._parse_pool_record(record, asset_code, asset_issuer)
                    if pool_data:
                        pools.append(pool_data)
                except Exception as e:
                    logger.error(f"Error parsing pool record: {e}")
            
        except Exception as e:
            logger.error(f"Error discovering pools for {asset_code}: {e}")
        
        return pools
    
    async def _parse_pool_record(
        self, 
        record: Dict[str, Any],
        target_code: str,
        target_issuer: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a liquidity pool record from Horizon API.
        
        Args:
            record: Pool record from Horizon
            target_code: The UBEC token we're looking for
            target_issuer: The issuer of that token
            
        Returns:
            Parsed pool data or None if parsing fails
        """
        try:
            pool_id = record.get('id')
            total_shares = Decimal(record.get('total_shares', '0'))
            fee_bp = int(record.get('fee_bp', 30))
            trustline_count = int(record.get('total_trustlines', 0))
            
            # Parse reserves
            reserves = record.get('reserves', [])
            if len(reserves) != 2:
                logger.warning(f"Pool {pool_id} has {len(reserves)} reserves, expected 2")
                return None
            
            reserve_a = reserves[0]
            reserve_b = reserves[1]
            
            # Parse asset info
            asset_a_parts = reserve_a.get('asset', 'native').split(':')
            asset_b_parts = reserve_b.get('asset', 'native').split(':')
            
            asset_a_code = 'XLM' if asset_a_parts[0] == 'native' else asset_a_parts[0]
            asset_a_issuer = None if asset_a_parts[0] == 'native' else asset_a_parts[1] if len(asset_a_parts) > 1 else None
            
            asset_b_code = 'XLM' if asset_b_parts[0] == 'native' else asset_b_parts[0]
            asset_b_issuer = None if asset_b_parts[0] == 'native' else asset_b_parts[1] if len(asset_b_parts) > 1 else None
            
            # Amounts
            reserve_a_amount = Decimal(reserve_a.get('amount', '0'))
            reserve_b_amount = Decimal(reserve_b.get('amount', '0'))
            
            # Determine which asset is the target UBEC token
            ubec_asset_position = None
            ubec_balance = Decimal('0')
            
            if asset_a_code == target_code and asset_a_issuer == target_issuer:
                ubec_asset_position = 'a'
                ubec_balance = reserve_a_amount
            elif asset_b_code == target_code and asset_b_issuer == target_issuer:
                ubec_asset_position = 'b'
                ubec_balance = reserve_b_amount
            
            # Create pair name
            pair = f"{asset_a_code}/{asset_b_code}"
            
            return {
                'id': pool_id,
                'asset_a_code': asset_a_code,
                'asset_a_issuer': asset_a_issuer,
                'asset_b_code': asset_b_code,
                'asset_b_issuer': asset_b_issuer,
                'pair': pair,
                'reserve_a': reserve_a_amount,
                'reserve_b': reserve_b_amount,
                'total_shares': total_shares,
                'ubec_asset_position': ubec_asset_position,
                'ubec_balance': ubec_balance,
                'fee_bp': fee_bp,
                'trustline_count': trustline_count
            }
            
        except Exception as e:
            logger.error(f"Error parsing pool record: {e}")
            return None
    
    async def _sync_pool(self, pool_data: Dict[str, Any], token_code: str):
        """
        Store or update a liquidity pool in the database.
        
        Args:
            pool_data: Parsed pool data
            token_code: UBEC token code this pool contains
        """
        try:
            query = """
                INSERT INTO liquidity_pools (
                    id, asset_a_code, asset_a_issuer, asset_b_code, asset_b_issuer,
                    pair, reserve_a, reserve_b, total_shares, balance,
                    ubec_asset_position, fee_bp, trustline_count, last_updated
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    reserve_a = EXCLUDED.reserve_a,
                    reserve_b = EXCLUDED.reserve_b,
                    total_shares = EXCLUDED.total_shares,
                    balance = EXCLUDED.balance,
                    trustline_count = EXCLUDED.trustline_count,
                    last_updated = NOW()
            """
            
            params = (
                pool_data['id'],
                pool_data['asset_a_code'],
                pool_data['asset_a_issuer'],
                pool_data['asset_b_code'],
                pool_data['asset_b_issuer'],
                pool_data['pair'],
                pool_data['reserve_a'],
                pool_data['reserve_b'],
                pool_data['total_shares'],
                pool_data['ubec_balance'],
                pool_data['ubec_asset_position'],
                pool_data['fee_bp'],
                pool_data['trustline_count']
            )
            
            await self.db.execute(query, params)
            
            logger.debug(f"Synced pool {pool_data['pair']} ({pool_data['id'][:8]}...): "
                        f"{pool_data['ubec_balance']} {token_code}")
            
        except Exception as e:
            logger.error(f"Error syncing pool {pool_data.get('id')}: {e}")
            raise
    
    async def _sync_all_account_positions(self) -> int:
        """
        Sync account positions for all tracked accounts in all liquidity pools.
        
        Returns:
            Number of accounts with LP positions updated
        """
        accounts_updated = 0
        
        try:
            # Get all accounts from database
            query = "SELECT account_id FROM stellar_accounts"
            account_rows = await self.db.fetch_all(query)
            
            logger.info(f"Checking LP positions for {len(account_rows)} accounts...")
            
            for row in account_rows:
                account_id = row['account_id']
                
                try:
                    # Fetch account data from Stellar
                    account_data = await self.stellar_client.accounts().account_id(account_id).call()
                    
                    # Look for liquidity_pool_shares in the balances
                    balances = account_data.get('balances', [])
                    
                    lp_positions = []
                    for balance in balances:
                        if balance.get('asset_type') == 'liquidity_pool_shares':
                            pool_id = balance.get('liquidity_pool_id')
                            shares = Decimal(balance.get('balance', '0'))
                            
                            lp_positions.append({
                                'pool_id': pool_id,
                                'shares': shares
                            })
                    
                    if lp_positions:
                        # Update positions in database
                        for position in lp_positions:
                            await self._sync_account_pool_position(
                                account_id, 
                                position['pool_id'],
                                position['shares']
                            )
                        
                        accounts_updated += 1
                        logger.debug(f"Updated {len(lp_positions)} LP positions for {account_id}")
                    
                except Exception as e:
                    logger.error(f"Error syncing LP positions for {account_id}: {e}")
            
            logger.info(f"✓ Updated LP positions for {accounts_updated} accounts")
            
        except Exception as e:
            logger.error(f"Error syncing account positions: {e}")
        
        return accounts_updated
    
    async def _sync_account_pool_position(
        self,
        account_id: str,
        pool_id: str,
        shares: Decimal
    ):
        """
        Store or update an account's position in a specific liquidity pool.
        
        Args:
            account_id: Stellar account ID
            pool_id: Liquidity pool ID
            shares: Number of pool shares owned
        """
        try:
            # Get pool data to calculate ownership percentage and UBEC balance
            pool_query = "SELECT total_shares, balance FROM liquidity_pools WHERE id = $1"
            pool_data = await self.db.fetch_one(pool_query, (pool_id,))
            
            if not pool_data:
                logger.warning(f"Pool {pool_id} not found in database")
                return
            
            total_shares = Decimal(pool_data['total_shares'])
            pool_ubec_balance = Decimal(pool_data['balance'])
            
            # Calculate ownership percentage and UBEC balance
            if total_shares > 0:
                ownership_percentage = (shares / total_shares) * Decimal('100')
                ubec_balance = (shares / total_shares) * pool_ubec_balance
            else:
                ownership_percentage = Decimal('0')
                ubec_balance = Decimal('0')
            
            # Store in database
            query = """
                INSERT INTO liquidity_pool_owners (
                    account_id, liquidity_pool_id, shares, 
                    ownership_percentage, ubec_balance, last_updated
                )
                VALUES ($1, $2, $3, $4, $5, NOW())
                ON CONFLICT (account_id, liquidity_pool_id) DO UPDATE SET
                    shares = EXCLUDED.shares,
                    ownership_percentage = EXCLUDED.ownership_percentage,
                    ubec_balance = EXCLUDED.ubec_balance,
                    last_updated = NOW()
            """
            
            params = (account_id, pool_id, shares, ownership_percentage, ubec_balance)
            await self.db.execute(query, params)
            
        except Exception as e:
            logger.error(f"Error syncing position for {account_id} in pool {pool_id}: {e}")
            raise
    
    async def get_account_lp_balance(
        self, 
        account_id: str, 
        asset_code: str = 'UBEC'
    ) -> Decimal:
        """
        Get total UBEC balance for an account from all their LP positions.
        
        Args:
            account_id: Stellar account ID
            asset_code: UBEC token code (default 'UBEC')
            
        Returns:
            Total UBEC balance in liquidity pools
        """
        try:
            query = """
                SELECT SUM(lpo.ubec_balance) as total_lp_balance
                FROM liquidity_pool_owners lpo
                JOIN liquidity_pools lp ON lpo.liquidity_pool_id = lp.id
                WHERE lpo.account_id = $1
                AND (lp.asset_a_code = $2 OR lp.asset_b_code = $2)
            """
            
            result = await self.db.fetch_one(query, (account_id, asset_code))
            
            if result and result['total_lp_balance']:
                return Decimal(result['total_lp_balance'])
            else:
                return Decimal('0')
                
        except Exception as e:
            logger.error(f"Error getting LP balance for {account_id}: {e}")
            return Decimal('0')
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("LiquidityPoolSynchronizer cleanup complete")


# ============================================================================
# Convenience function for creating the service
# ============================================================================

async def create_lp_synchronizer(
    db_manager,
    stellar_client,
    ubec_tokens: Dict[str, str]
) -> LiquidityPoolSynchronizer:
    """
    Factory function to create a LiquidityPoolSynchronizer instance.
    
    Args:
        db_manager: AsyncDatabaseManager instance
        stellar_client: Stellar ServerAsync client
        ubec_tokens: Dict of UBEC token codes to issuer addresses
        
    Returns:
        Initialized LiquidityPoolSynchronizer
    """
    return LiquidityPoolSynchronizer(db_manager, stellar_client, ubec_tokens)
