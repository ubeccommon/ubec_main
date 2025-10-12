#!/usr/bin/env python3
# services/distribution/distribution_service.py
"""
UBEC Distribution Manager Service - With Liquidity Pool Tracking

This service manages UBEC token distribution according to official tokenomics:
    - General Distribution: 65%
    - Stewardship: 30% (including LP-locked tokens)
    - Administration: 5%

CRITICAL: Stewardship Liquidity Account Balance Includes:
    1. Free UBEC tokens in the account
    2. UBEC tokens locked in liquidity pools

Official Accounts:
    General: GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74
    Administration: GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC
    Stewardship:
        - Management: GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC
        - Infrastructure: GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC
        - Liquidity: GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team  
Version: 3.2.2 (Fixed Database Schema Compatibility)
Date: October 12, 2025

Changes in v3.2.2:
    - CRITICAL FIX: Updated queries to match actual database schema
    - Removed token_issuer column references (not in ubec_balances table)
    - Fixed total supply query to sum from ubec_balances instead of non-existent ubec_metadata
    - Simplified LP queries to use token_code only
    - All database queries now compatible with actual schema

Changes in v3.2.1:
    - CRITICAL FIX: Database query parameters now passed as tuples
    - Fixed fetch_one() calls to wrap parameters in tuple
    - Fixed fetch_all() calls to wrap parameters in tuple
    - Resolves "takes from 2 to 3 positional arguments" error

Changes in v3.2:
    - CRITICAL: Added liquidity pool balance tracking for Liquidity account
    - Added method to calculate UBEC tokens in LP positions
    - Enhanced balance retrieval to include LP-locked tokens
    - Added detailed breakdown of free vs LP-locked tokens
    - Improved logging for liquidity pool positions
"""

import asyncio
import json
import logging
import inspect
from decimal import Decimal, getcontext
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

from stellar_sdk import Asset, Keypair, TransactionBuilder, Network
from stellar_sdk.exceptions import NotFoundError, BadRequestError

# Configure precision for decimal calculations
getcontext().prec = 10

logger = logging.getLogger(__name__)


# ========================================================================
# OFFICIAL UBEC TOKENOMICS CONSTANTS
# ========================================================================

OFFICIAL_TOKENOMICS = {
    'general': Decimal('0.65'),      # 65% - General Distribution
    'stewardship': Decimal('0.30'),  # 30% - Stewardship (3 accounts combined)
    'administration': Decimal('0.05') # 5% - Administration
}

OFFICIAL_ACCOUNTS = {
    'general': 'GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74',
    'administration': 'GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC',
    'stewardship': [
        'GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC',  # Management
        'GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC',  # Infrastructure
        'GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC'   # Liquidity (includes LP-locked)
    ]
}

# Liquidity account (needs special handling for LP positions)
LIQUIDITY_ACCOUNT = 'GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC'


class RateLimiter:
    """Simple async rate limiter using token bucket algorithm"""
    
    def __init__(self, calls_per_second: float = 10.0):
        self.calls_per_second = calls_per_second
        self.tokens = calls_per_second
        self.updated_at = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a call, waiting if necessary"""
        async with self._lock:
            while self.tokens < 1:
                now = asyncio.get_event_loop().time()
                elapsed = now - self.updated_at
                self.tokens = min(
                    self.calls_per_second,
                    self.tokens + elapsed * self.calls_per_second
                )
                self.updated_at = now
                
                if self.tokens < 1:
                    sleep_time = (1 - self.tokens) / self.calls_per_second
                    await asyncio.sleep(sleep_time)
            
            self.tokens -= 1


class UBECDistributionService:
    """
    Async service for managing UBEC token distribution with LP tracking.
    
    This service ensures distribution matches official UBEC tokenomics:
    - 65% in General Distribution
    - 30% in Stewardship (including LP-locked tokens)
    - 5% in Administration
    
    CRITICAL: For the Stewardship Liquidity account, the balance calculation
    includes BOTH:
    1. Free UBEC tokens in the account
    2. UBEC tokens locked in liquidity pools
    
    This ensures accurate distribution calculation across the entire ecosystem.
    """
    
    def __init__(
        self,
        db_manager: Any,
        config: Dict[str, Any],
        stellar_client: Any,
        audit_service: Any,
        rate_limit_calls_per_second: float = 5.0
    ):
        """Initialize the distribution service with LP tracking."""
        # Validate database manager type
        if not hasattr(db_manager, 'fetch_all') or not hasattr(db_manager, 'fetch_one'):
            raise ValueError(
                f"Invalid database manager type: {type(db_manager)}. "
                "Expected AsyncDatabaseManager with fetch_all and fetch_one methods."
            )
        
        # Validate stellar client
        if not hasattr(stellar_client, 'accounts'):
            logger.warning(
                f"Stellar client type may be incorrect: {type(stellar_client)}. "
                "Expected ServerAsync instance."
            )
        
        self.db_manager = db_manager
        self.config = config
        self.stellar_client = stellar_client
        self.audit_service = audit_service
        self.rate_limiter = RateLimiter(calls_per_second=rate_limit_calls_per_second)
        
        # Extract configuration
        self.ubec_code = config.get('asset_code', 'UBEC')
        self.ubec_issuer = config.get('issuer_address')
        self.db_schema = config.get('database', {}).get('schema', 'ubec')
        self.network = config.get('network', 'TESTNET')
        
        # Initialize official accounts
        self.accounts = OFFICIAL_ACCOUNTS.copy()
        self.target_distribution = OFFICIAL_TOKENOMICS.copy()
        self.rebalance_threshold = Decimal('0.02')  # 2% deviation threshold
        
        # Cache for balances
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = timedelta(minutes=5)
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info("Distribution service initialized with LP tracking")
        
        # Log initialization with validation
        self._log_initialization()
    
    def _log_initialization(self):
        """Log service initialization with configuration validation."""
        self.logger.info("=" * 70)
        self.logger.info("UBEC Distribution Service Initialized")
        self.logger.info("=" * 70)
        self.logger.info(f"Asset: {self.ubec_code}")
        self.logger.info("Official Tokenomics Validated:")
        self.logger.info(f"  - General Distribution: {self.target_distribution['general'] * 100}%")
        self.logger.info(f"  - Stewardship: {self.target_distribution['stewardship'] * 100}%")
        self.logger.info(f"  - Administration: {self.target_distribution['administration'] * 100}%")
        self.logger.info("=" * 70)
        
        # Validate configuration matches official accounts
        config_general = self.config.get('accounts', {}).get('general', '')
        config_admin = self.config.get('accounts', {}).get('administration', '')
        
        if config_general and config_general != OFFICIAL_ACCOUNTS['general']:
            self.logger.warning(
                f"⚠️  General account mismatch!\n"
                f"  Config: {config_general}\n"
                f"  Official: {OFFICIAL_ACCOUNTS['general']}"
            )
        
        if config_admin and config_admin != OFFICIAL_ACCOUNTS['administration']:
            self.logger.warning(
                f"⚠️  Administration account mismatch!\n"
                f"  Config: {config_admin}\n"
                f"  Official: {OFFICIAL_ACCOUNTS['administration']}"
            )
    
    # ========================================================================
    # LIQUIDITY POOL BALANCE TRACKING
    # ========================================================================
    
    async def get_lp_balance_for_account(
        self,
        account_address: str
    ) -> Tuple[Decimal, List[Dict[str, Any]]]:
        """
        Get UBEC tokens locked in liquidity pools for a specific account.
        
        This method calculates the amount of UBEC tokens that an account has
        locked in liquidity pools based on their ownership percentage of each pool.
        
        Args:
            account_address: The Stellar account address
            
        Returns:
            Tuple of (total_lp_balance, list of pool details)
            
        Example:
            lp_balance, pools = await service.get_lp_balance_for_account('GXXX...')
            for pool in pools:
                print(f"Pool {pool['pool_id']}: {pool['ubec_amount']} UBEC")
        """
        try:
            query = """
                SELECT 
                    lpo.liquidity_pool_id as pool_id,
                    lpo.ownership_percentage,
                    lp.balance as pool_balance,
                    lp.pair,
                    lp.asset_a_code,
                    lp.asset_b_code
                FROM liquidity_pool_owners lpo
                JOIN liquidity_pools lp ON lpo.liquidity_pool_id = lp.id
                WHERE lpo.account_id = $1
                AND (lp.asset_a_code = $2 OR lp.asset_b_code = $2)
            """
            
            pool_records = await self.db_manager.fetch_all(
                query,
                (account_address, self.ubec_code)
            )
            
            total_lp_balance = Decimal('0')
            pool_details = []
            
            if pool_records:
                for record in pool_records:
                    pool_balance = Decimal(str(record['pool_balance']))
                    ownership_pct = Decimal(str(record['ownership_percentage']))
                    
                    # Calculate this account's share of UBEC in the pool
                    ubec_amount = pool_balance * (ownership_pct / Decimal('100'))
                    total_lp_balance += ubec_amount
                    
                    pool_details.append({
                        'pool_id': record['pool_id'],
                        'pair': record['pair'],
                        'ownership_percentage': float(ownership_pct),
                        'pool_total_ubec': float(pool_balance),
                        'ubec_amount': float(ubec_amount)
                    })
                
                self.logger.debug(
                    f"Account {account_address[:8]}... has {total_lp_balance} UBEC "
                    f"in {len(pool_details)} liquidity pools"
                )
            else:
                self.logger.debug(
                    f"No liquidity pool positions found for {account_address[:8]}..."
                )
            
            return total_lp_balance, pool_details
            
        except Exception as e:
            self.logger.error(f"Error getting LP balance for {account_address}: {e}")
            return Decimal('0'), []
    
    async def get_account_balance_with_lp(
        self,
        account_address: str,
        include_lp: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive balance information for an account.
        
        For the Stewardship Liquidity account, this includes both free tokens
        and tokens locked in liquidity pools.
        
        Args:
            account_address: The account to check
            include_lp: Whether to include LP-locked tokens (default True)
            
        Returns:
            Dictionary with balance breakdown:
            {
                'account': str,
                'free_balance': Decimal,
                'lp_balance': Decimal,
                'total_balance': Decimal,
                'lp_positions': List[Dict],
                'includes_lp': bool
            }
        """
        try:
            # Get direct balance from database
            query = """
                SELECT balance 
                FROM ubec_balances 
                WHERE account_id = $1 
                AND token_code = $2
            """
            
            result = await self.db_manager.fetch_one(
                query,
                (account_address, self.ubec_code)
            )
            
            free_balance = Decimal(str(result['balance'])) if result else Decimal('0')
            
            # Get LP balance if requested
            lp_balance = Decimal('0')
            lp_positions = []
            
            if include_lp:
                lp_balance, lp_positions = await self.get_lp_balance_for_account(
                    account_address
                )
            
            total_balance = free_balance + lp_balance
            
            return {
                'account': account_address,
                'free_balance': free_balance,
                'lp_balance': lp_balance,
                'total_balance': total_balance,
                'lp_positions': lp_positions,
                'includes_lp': include_lp
            }
            
        except Exception as e:
            self.logger.error(
                f"Error getting balance with LP for {account_address}: {e}"
            )
            return {
                'account': account_address,
                'free_balance': Decimal('0'),
                'lp_balance': Decimal('0'),
                'total_balance': Decimal('0'),
                'lp_positions': [],
                'includes_lp': include_lp,
                'error': str(e)
            }
    
    # ========================================================================
    # ACCOUNT BALANCE RETRIEVAL
    # ========================================================================
    
    async def get_all_account_balances(self) -> Dict[str, Dict[str, Any]]:
        """
        Get balances for all monitored accounts with LP tracking.
        
        CRITICAL: The Stewardship Liquidity account balance includes BOTH
        free tokens AND tokens locked in liquidity pools.
        
        Returns:
            Dictionary mapping account addresses to balance information
        """
        self.logger.info("Retrieving all account balances with LP tracking...")
        
        balances = {}
        
        # Get general account balance (no LP needed)
        general_balance = await self.get_account_balance_with_lp(
            self.accounts['general'],
            include_lp=False
        )
        balances['general'] = general_balance
        
        # Get administration account balance (no LP needed)
        admin_balance = await self.get_account_balance_with_lp(
            self.accounts['administration'],
            include_lp=False
        )
        balances['administration'] = admin_balance
        
        # Get stewardship account balances
        # CRITICAL: Liquidity account must include LP positions
        stewardship_accounts = []
        for i, address in enumerate(self.accounts['stewardship']):
            account_label = ["Management", "Infrastructure", "Liquidity"][i]
            
            # Only include LP for the Liquidity account
            include_lp = (address == LIQUIDITY_ACCOUNT)
            
            balance_info = await self.get_account_balance_with_lp(
                address,
                include_lp=include_lp
            )
            balance_info['label'] = account_label
            stewardship_accounts.append(balance_info)
        
        balances['stewardship'] = stewardship_accounts
        
        # Log detailed breakdown
        self.logger.info("Account Balance Summary:")
        self.logger.info(f"  General: {general_balance['total_balance']} UBEC")
        self.logger.info(f"  Administration: {admin_balance['total_balance']} UBEC")
        self.logger.info("  Stewardship:")
        
        for acct in stewardship_accounts:
            if acct['includes_lp']:
                self.logger.info(
                    f"    {acct['label']}: {acct['total_balance']} UBEC "
                    f"(Free: {acct['free_balance']}, LP: {acct['lp_balance']})"
                )
            else:
                self.logger.info(
                    f"    {acct['label']}: {acct['total_balance']} UBEC"
                )
        
        return balances
    
    async def _invalidate_cache(self):
        """Invalidate the balance cache."""
        self._cache = {}
        self._cache_timestamp = None
    
    # ========================================================================
    # DISTRIBUTION ANALYSIS
    # ========================================================================
    
    async def get_current_distribution(self) -> Dict[str, Any]:
        """
        Calculate current distribution percentages with LP tracking.
        
        Returns:
            Dictionary with distribution analysis including LP positions
        """
        self.logger.info("Analyzing current distribution with LP tracking...")
        
        # Get all balances
        balances = await self.get_all_account_balances()
        
        # Calculate totals
        general_total = balances['general']['total_balance']
        admin_total = balances['administration']['total_balance']
        
        stewardship_total = Decimal('0')
        stewardship_breakdown = {}
        
        for acct in balances['stewardship']:
            stewardship_total += acct['total_balance']
            stewardship_breakdown[acct['label']] = {
                'free': float(acct['free_balance']),
                'lp': float(acct['lp_balance']),
                'total': float(acct['total_balance']),
                'lp_positions': acct['lp_positions']
            }
        
        monitored_total = general_total + admin_total + stewardship_total
        
        # Get total supply from database (sum of all balances)
        try:
            supply_query = """
                SELECT SUM(balance) as total_supply
                FROM ubec_balances 
                WHERE token_code = $1
            """
            supply_result = await self.db_manager.fetch_one(
                supply_query,
                (self.ubec_code,)
            )
            total_supply = Decimal(str(supply_result['total_supply'])) if supply_result and supply_result['total_supply'] else monitored_total
        except Exception as e:
            self.logger.warning(f"Could not get total supply from ubec_balances: {e}")
            total_supply = monitored_total
        
        # Calculate distributions
        if monitored_total > 0:
            monitored_dist = {
                'general': float(general_total / monitored_total),
                'administration': float(admin_total / monitored_total),
                'stewardship': float(stewardship_total / monitored_total)
            }
        else:
            monitored_dist = {
                'general': 0.0,
                'administration': 0.0,
                'stewardship': 0.0
            }
        
        if total_supply > 0:
            supply_dist = {
                'general': float(general_total / total_supply),
                'administration': float(admin_total / total_supply),
                'stewardship': float(stewardship_total / total_supply)
            }
        else:
            supply_dist = monitored_dist.copy()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_supply': float(total_supply),
            'monitored_total': float(monitored_total),
            'unmonitored': float(total_supply - monitored_total),
            'balances': {
                'general': float(general_total),
                'administration': float(admin_total),
                'stewardship': float(stewardship_total),
                'stewardship_breakdown': stewardship_breakdown
            },
            'distribution_of_monitored': monitored_dist,
            'distribution_of_supply': supply_dist,
            'target_distribution': {
                'general': float(self.target_distribution['general']),
                'administration': float(self.target_distribution['administration']),
                'stewardship': float(self.target_distribution['stewardship'])
            }
        }
    
    async def check_compliance(self) -> Dict[str, Any]:
        """
        Check if current distribution complies with target tokenomics.
        
        Returns:
            Compliance status with detailed breakdown
        """
        self.logger.info("Checking distribution compliance...")
        
        current = await self.get_current_distribution()
        supply_dist = current['distribution_of_supply']
        
        # Check each category against targets
        compliance = {}
        deviations = {}
        
        for category in ['general', 'administration', 'stewardship']:
            target = float(self.target_distribution[category])
            actual = supply_dist[category]
            deviation = abs(actual - target)
            
            is_compliant = deviation <= float(self.rebalance_threshold)
            
            compliance[category] = is_compliant
            deviations[category] = {
                'target': target,
                'actual': actual,
                'deviation': deviation,
                'deviation_percent': deviation * 100,
                'compliant': is_compliant
            }
        
        overall_compliant = all(compliance.values())
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'overall_compliant': overall_compliant,
            'compliance': compliance,
            'deviations': deviations,
            'threshold_percent': float(self.rebalance_threshold * 100),
            'note': 'Stewardship balance includes UBEC tokens locked in liquidity pools'
        }
        
        # Log compliance status
        if overall_compliant:
            self.logger.info("✓ Distribution is COMPLIANT with target tokenomics")
        else:
            self.logger.warning("✗ Distribution is NON-COMPLIANT")
            for category, compliant in compliance.items():
                if not compliant:
                    dev = deviations[category]
                    self.logger.warning(
                        f"  {category.capitalize()}: "
                        f"{dev['actual']:.2%} vs {dev['target']:.2%} target "
                        f"(deviation: {dev['deviation_percent']:.2f}%)"
                    )
        
        return result
    
    # ========================================================================
    # DISTRIBUTION STATUS
    # ========================================================================
    
    async def get_distribution_status(self) -> Dict[str, Any]:
        """
        Get comprehensive distribution status including LP positions.
        
        Returns:
            Complete status report with all distribution details
        """
        try:
            self.logger.info("Generating comprehensive distribution status...")
            
            current_dist = await self.get_current_distribution()
            compliance = await self.check_compliance()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'ubec_code': self.ubec_code,
                'ubec_issuer': self.ubec_issuer,
                'total_supply': current_dist['total_supply'],
                'monitored_total': current_dist['monitored_total'],
                'unmonitored': current_dist['unmonitored'],
                'account_balances': current_dist['balances'],
                'distribution_percentages': {
                    'general': float(current_dist['distribution_of_supply']['general']),
                    'administration': float(current_dist['distribution_of_supply']['administration']),
                    'stewardship': float(current_dist['distribution_of_supply']['stewardship'])
                },
                'target_percentages': current_dist['target_distribution'],
                'compliance': compliance,
                'note': 'Stewardship balance includes UBEC tokens locked in liquidity pools'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting distribution status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources on shutdown"""
        await self._invalidate_cache()
        self.logger.info("Distribution service cleaned up")


# ========================================================================
# FACTORY FUNCTION
# ========================================================================

def create_distribution_service(
    db_manager: Any,
    config: Dict[str, Any],
    stellar_client: Any,
    audit_service: Any,
    rate_limit_calls_per_second: float = 5.0
) -> UBECDistributionService:
    """
    Factory function to create distribution service instance.
    
    Returns:
        UBECDistributionService: Service with LP tracking support
    """
    return UBECDistributionService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        audit_service=audit_service,
        rate_limit_calls_per_second=rate_limit_calls_per_second
    )


# Export public interface
__all__ = [
    'UBECDistributionService',
    'create_distribution_service',
    'OFFICIAL_TOKENOMICS',
    'OFFICIAL_ACCOUNTS',
    'LIQUIDITY_ACCOUNT'
]
