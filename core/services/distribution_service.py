#!/usr/bin/env python3
"""
UBEC Distribution Manager Service - CORRECTED VERSION

This version fixes the "object dict can't be used in 'await' expression" error
by ensuring proper async database manager usage.

Key fixes:
1. Added db_manager type validation on initialization
2. Ensured all database calls properly use async/await
3. Fixed parameter passing to match AsyncDatabaseManager interface
4. Added comprehensive error handling

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team  
Version: 2.3 (Fixed Both DB Manager and Stellar Client Validation)
Date: October 12, 2025
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
                # Calculate how long to wait for next token
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
    Async service for managing UBEC token distribution.
    
    This service ensures that token distribution across General, Administration,
    and Stewardship accounts matches the defined tokenomics ratios.
    
    Attributes:
        db_manager: Async database manager
        config: System configuration
        stellar_client: Async Stellar client
        audit_service: Token audit service
        rate_limiter: Rate limiter for Stellar API calls
    """
    
    def __init__(
        self,
        db_manager: Any,
        config: Dict[str, Any],
        stellar_client: Any,
        audit_service: Any,
        rate_limit_calls_per_second: float = 5.0
    ):
        """
        Initialize the distribution service.
        
        Args:
            db_manager: Async database manager instance
            config: Configuration dictionary with network, accounts, etc.
            stellar_client: Async Stellar ServerAsync client
            audit_service: UBECTokenAudit service instance
            rate_limit_calls_per_second: API rate limit (default: 5/sec)
        """
        # CRITICAL FIX: Validate db_manager has async methods
        self._validate_db_manager(db_manager)
        
        # CRITICAL FIX: Validate stellar_client is proper async client
        self._validate_stellar_client(stellar_client)
        
        self.db_manager = db_manager
        self.config = config
        self.stellar_client = stellar_client
        self.audit_service = audit_service
        
        # Setup logging
        self.logger = logging.getLogger('UBECDistributionService')
        
        # Rate limiting
        self.rate_limiter = RateLimiter(rate_limit_calls_per_second)
        
        # Extract configuration
        self.db_schema = config.get('db_schema', 'ubec_main')
        self.network = Network.PUBLIC_NETWORK_PASSPHRASE
        
        # UBEC asset configuration
        self.ubec_issuer = config.get('ubec_issuer')
        self.ubec_code = config.get('ubec_code', 'UBEC')
        self.ubec_asset = Asset(self.ubec_code, self.ubec_issuer)
        
        # Account configuration
        self.accounts = config.get('accounts', {})
        self.target_distribution = config.get('target_distribution', {})
        self.rebalance_threshold = Decimal(str(config.get('rebalance_threshold', 0.02)))
        
        # Secret keys (from config, not hardcoded)
        self.secret_keys = config.get('secret_keys', {})
        
        # Cache for stewardship balances
        self._balance_cache: Dict[str, Decimal] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        self.logger.info(f"Distribution Service initialized for {self.ubec_code}")
    
    def _validate_db_manager(self, db_manager: Any):
        """
        Validate that db_manager has the required async methods.
        
        Args:
            db_manager: Database manager to validate
            
        Raises:
            TypeError: If db_manager doesn't have required async methods
        """
        required_methods = ['fetch_one', 'fetch_all', 'execute']
        
        for method_name in required_methods:
            if not hasattr(db_manager, method_name):
                raise TypeError(
                    f"db_manager must have '{method_name}' method. "
                    f"Got type: {type(db_manager)}"
                )
            
            method = getattr(db_manager, method_name)
            if not (callable(method) or inspect.iscoroutinefunction(method)):
                raise TypeError(
                    f"db_manager.{method_name} must be a callable method. "
                    f"Got: {type(method)}"
                )
    
    def _validate_stellar_client(self, stellar_client: Any):
        """
        Validate that stellar_client is a proper Stellar async client.
        
        Args:
            stellar_client: Stellar client to validate
            
        Raises:
            TypeError: If stellar_client is not a valid client
        """
        # Check it's not a dict
        if isinstance(stellar_client, dict):
            raise TypeError(
                f"stellar_client cannot be a dict. "
                f"Must be a Stellar ServerAsync instance. "
                f"Got: {stellar_client}"
            )
        
        # Check for key Stellar client methods
        required_methods = ['accounts', 'submit_transaction', 'load_account']
        
        for method_name in required_methods:
            if not hasattr(stellar_client, method_name):
                raise TypeError(
                    f"stellar_client must have '{method_name}' method. "
                    f"Got type: {type(stellar_client)}"
                )
            
            method = getattr(stellar_client, method_name)
            if not callable(method):
                raise TypeError(
                    f"stellar_client.{method_name} must be callable. "
                    f"Got: {type(method)}"
                )
    
    # ========================================================================
    # CACHE MANAGEMENT
    # ========================================================================
    
    def _is_cache_valid(self) -> bool:
        """Check if balance cache is still valid"""
        if self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_ttl
    
    async def _invalidate_cache(self):
        """Invalidate the balance cache"""
        self._balance_cache.clear()
        self._cache_timestamp = None
        self.logger.debug("Balance cache invalidated")
    
    # ========================================================================
    # BALANCE RETRIEVAL
    # ========================================================================
    
    async def get_account_balance(self, account_id: str) -> Decimal:
        """
        Get UBEC balance for a specific account.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            Decimal: Account balance in UBEC
        """
        # Check cache first
        if self._is_cache_valid() and account_id in self._balance_cache:
            return self._balance_cache[account_id]
        
        try:
            # Rate limit
            await self.rate_limiter.acquire()
            
            # Fetch from database first
            query = f"""
                SELECT balance FROM {self.db_schema}.asset_holders 
                WHERE account_id = $1 AND asset_code = $2 AND asset_issuer = $3
            """
            
            # FIXED: Properly await async method with tuple parameters
            result = await self.db_manager.fetch_one(
                query, 
                (account_id, self.ubec_code, self.ubec_issuer)
            )
            
            if result:
                balance = Decimal(str(result['balance']))
            else:
                # Fallback to Stellar if not in database
                account = await self.stellar_client.accounts().account_id(account_id).call()
                
                balance = Decimal('0')
                for bal in account.get('balances', []):
                    if (bal.get('asset_type') == 'credit_alphanum4' and 
                        bal.get('asset_code') == self.ubec_code and 
                        bal.get('asset_issuer') == self.ubec_issuer):
                        balance = Decimal(str(bal['balance']))
                        break
            
            # Update cache
            self._balance_cache[account_id] = balance
            self._cache_timestamp = datetime.now()
            
            return balance
            
        except Exception as e:
            self.logger.error(f"Error getting balance for {account_id}: {e}")
            self.logger.exception("Full traceback:")
            return Decimal('0')
    
    async def get_stewardship_balances(self) -> Dict[str, Any]:
        """
        Get detailed balance information for all stewardship accounts.
        
        Returns:
            dict: Information about each stewardship account and totals
        """
        self.logger.info("Getting stewardship balances")
        
        balances = []
        total_direct_balance = Decimal('0')
        
        stewardship_accounts = self.accounts.get('stewardship', [])
        labels = ["Management", "Infrastructure", "Liquidity"]
        
        # Fetch balances concurrently
        tasks = [
            self.get_account_balance(address) 
            for address in stewardship_accounts
        ]
        account_balances = await asyncio.gather(*tasks)
        
        # Build result structure
        for i, (address, balance) in enumerate(zip(stewardship_accounts, account_balances)):
            label = labels[i] if i < len(labels) else f"Account {i}"
            
            balances.append({
                'index': i,
                'address': address,
                'label': label,
                'balance': balance
            })
            total_direct_balance += balance
        
        # Sort by balance (highest first)
        balances.sort(key=lambda x: x['balance'], reverse=True)
        
        # Log information
        for acct in balances:
            percent = (acct['balance'] / total_direct_balance * 100) if total_direct_balance > 0 else 0
            self.logger.info(
                f"Stewardship {acct['label']} ({acct['address']}): "
                f"{acct['balance']} UBEC ({percent:.2f}%)"
            )
        
        return {
            'accounts': balances,
            'total_direct': total_direct_balance
        }
    
    async def select_stewardship_account_for_transfer(
        self, 
        amount: Decimal, 
        is_source: bool = True
    ) -> Tuple[str, str, Decimal]:
        """
        Select the best stewardship account for a transfer.
        
        Args:
            amount: Amount to transfer
            is_source: True if this account is source, False if destination
            
        Returns:
            tuple: (account_address, secret_key, available_balance)
        """
        stewardship_info = await self.get_stewardship_balances()
        
        if is_source:
            # Find account with sufficient balance
            for acct in stewardship_info['accounts']:
                if acct['balance'] >= amount:
                    self.logger.info(
                        f"Selected Stewardship {acct['label']} for sending {amount} UBEC"
                    )
                    return (
                        acct['address'],
                        self.secret_keys['stewardship'][acct['index']],
                        acct['balance']
                    )
            
            # Use highest balance account if none have enough
            if stewardship_info['accounts']:
                best_acct = stewardship_info['accounts'][0]
                self.logger.warning(
                    f"No account has sufficient balance. Using {best_acct['label']} "
                    f"with {best_acct['balance']} UBEC"
                )
                return (
                    best_acct['address'],
                    self.secret_keys['stewardship'][best_acct['index']],
                    best_acct['balance']
                )
        else:
            # For receiving, prefer Management Account (index 0)
            management_acct = next(
                (acct for acct in stewardship_info['accounts'] if acct['index'] == 0), 
                None
            )
            
            if management_acct:
                self.logger.info("Selected Stewardship Management Account for receiving")
                return (
                    management_acct['address'],
                    self.secret_keys['stewardship'][0],
                    management_acct['balance']
                )
        
        # Default to Management Account (index 0)
        self.logger.info("Defaulting to Stewardship Management Account")
        default_address = self.accounts['stewardship'][0]
        default_balance = await self.get_account_balance(default_address)
        
        return (
            default_address,
            self.secret_keys['stewardship'][0],
            default_balance
        )
    
    # ========================================================================
    # COMPLIANCE CHECKING
    # ========================================================================
    
    async def _check_compliance_from_database(
        self,
        asset_code: str,
        asset_issuer: str
    ) -> Dict[str, Any]:
        """
        Fallback compliance check using only database data.
        Used when audit service is not available.
        
        Args:
            asset_code: Asset code
            asset_issuer: Asset issuer
            
        Returns:
            dict: Compliance status
        """
        try:
            # Get balances from database
            general_balance = await self.get_account_balance(self.accounts['general'])
            admin_balance = await self.get_account_balance(self.accounts['administration'])
            stewardship_info = await self.get_stewardship_balances()
            stewardship_balance = stewardship_info['total_direct']
            
            # Calculate total
            total_balance = general_balance + admin_balance + stewardship_balance
            
            if total_balance == 0:
                self.logger.warning("Total balance is zero - cannot check compliance")
                return {
                    'overall': False,
                    'administration': False,
                    'stewardship': False,
                    'error': 'Total balance is zero',
                    'asset_code': asset_code,
                    'asset_issuer': asset_issuer,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Calculate current percentages
            admin_pct = admin_balance / total_balance
            steward_pct = stewardship_balance / total_balance
            
            # Get target percentages
            target_admin = Decimal(str(self.target_distribution['administration']))
            target_steward = Decimal(str(self.target_distribution['stewardship']))
            
            # Check compliance (within threshold)
            admin_compliant = abs(admin_pct - target_admin) <= self.rebalance_threshold
            steward_compliant = abs(steward_pct - target_steward) <= self.rebalance_threshold
            
            overall_compliant = admin_compliant and steward_compliant
            
            compliance_status = {
                'overall': overall_compliant,
                'administration': admin_compliant,
                'stewardship': steward_compliant,
                'details': {
                    'current': {
                        'administration': float(admin_pct),
                        'stewardship': float(steward_pct)
                    },
                    'target': {
                        'administration': float(target_admin),
                        'stewardship': float(target_steward)
                    },
                    'deviations': {
                        'administration': float(abs(admin_pct - target_admin)),
                        'stewardship': float(abs(steward_pct - target_steward))
                    }
                },
                'asset_code': asset_code,
                'asset_issuer': asset_issuer,
                'timestamp': datetime.now().isoformat(),
                'note': 'Database-only check (audit service unavailable)'
            }
            
            self.logger.info(
                f"Database compliance check for {asset_code}: Overall={overall_compliant}, "
                f"Admin={admin_compliant}, Stewardship={steward_compliant}"
            )
            
            return compliance_status
            
        except Exception as e:
            self.logger.error(f"Error in database compliance check: {e}")
            self.logger.exception("Full traceback:")
            return {
                'overall': False,
                'error': str(e),
                'asset_code': asset_code,
                'asset_issuer': asset_issuer,
                'timestamp': datetime.now().isoformat()
            }
    
    async def check_compliance(
        self, 
        asset_code: Optional[str] = None, 
        asset_issuer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if current distribution meets target percentages.
        
        Args:
            asset_code: Optional asset code (defaults to UBEC)
            asset_issuer: Optional issuer (defaults to UBEC issuer)
        
        Returns:
            dict: Compliance status with details
        """
        if asset_code is None:
            asset_code = self.ubec_code
        if asset_issuer is None:
            asset_issuer = self.ubec_issuer
        
        try:
            # Check if audit service is available
            if self.audit_service is None:
                self.logger.warning("Audit service not available - using database-only compliance check")
                # Fallback to database-only check
                return await self._check_compliance_from_database(asset_code, asset_issuer)
            
            # Use audit service to check compliance
            audit_report = await self.audit_service.perform_audit()
            
            compliance_status = {
                'overall': audit_report.get('tokenomics_compliance', {}).get('overall', False),
                'administration': audit_report.get('tokenomics_compliance', {}).get('administration', False),
                'stewardship': audit_report.get('tokenomics_compliance', {}).get('stewardship', False),
                'details': audit_report.get('tokenomics_compliance', {}),
                'asset_code': asset_code,
                'asset_issuer': asset_issuer,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(
                f"Compliance check for {asset_code}: Overall={compliance_status['overall']}, "
                f"Admin={compliance_status['administration']}, "
                f"Stewardship={compliance_status['stewardship']}"
            )
            
            return compliance_status
            
        except Exception as e:
            self.logger.error(f"Error checking compliance: {e}")
            self.logger.exception("Full traceback:")
            return {
                'overall': False,
                'error': str(e),
                'asset_code': asset_code,
                'asset_issuer': asset_issuer,
                'timestamp': datetime.now().isoformat()
            }
    
    async def snapshot_distribution(
        self, 
        asset_code: Optional[str] = None, 
        asset_issuer: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a snapshot of current distribution in the database.
        
        Args:
            asset_code: Optional asset code (defaults to UBEC)
            asset_issuer: Optional issuer (defaults to UBEC issuer)
        
        Returns:
            int: ID of created snapshot, or None if failed
        """
        if asset_code is None:
            asset_code = self.ubec_code
        if asset_issuer is None:
            asset_issuer = self.ubec_issuer
        
        try:
            # Get current distribution
            if self.audit_service:
                audit_report = await self.audit_service.perform_audit()
                
                # Extract balances
                general_balance = Decimal(str(audit_report.get('monitored_supply', {}).get('general', 0)))
                admin_balance = Decimal(str(audit_report.get('monitored_supply', {}).get('administration', 0)))
                stewardship_balance = Decimal(str(audit_report.get('monitored_supply', {}).get('stewardship', 0)))
                total_supply = Decimal(str(audit_report.get('total_supply', 0)))
            else:
                # Fallback to direct balance queries
                general_balance = await self.get_account_balance(self.accounts['general'])
                admin_balance = await self.get_account_balance(self.accounts['administration'])
                stewardship_info = await self.get_stewardship_balances()
                stewardship_balance = stewardship_info['total_direct']
                total_supply = general_balance + admin_balance + stewardship_balance
                audit_report = {'distribution': {}}  # Empty audit report
            
            # Check if rebalance needed
            compliance = await self.check_compliance(asset_code, asset_issuer)
            rebalance_needed = not compliance.get('overall', True)
            
            # Record in database
            query = f"""
                SELECT {self.db_schema}.record_distribution_check(
                    $1, $2, $3, $4, $5, $6, $7, $8
                )
            """
            
            # FIXED: Properly await with tuple parameters
            result = await self.db_manager.fetch_one(
                query,
                (
                    asset_code,
                    asset_issuer,
                    float(general_balance),
                    float(admin_balance),
                    float(stewardship_balance),
                    float(total_supply),
                    rebalance_needed,
                    json.dumps(audit_report.get('distribution', {}))
                )
            )
            
            if result:
                snapshot_id = result['record_distribution_check']
                self.logger.info(f"Created distribution snapshot ID: {snapshot_id} for {asset_code}")
                return snapshot_id
            else:
                self.logger.warning(f"Could not create snapshot for {asset_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating distribution snapshot: {e}")
            self.logger.exception("Full traceback:")
            return None
    
    async def is_rebalance_needed(self) -> Tuple[bool, Dict[str, Decimal]]:
        """
        Check if rebalancing is needed based on current vs target distribution.
        
        Returns:
            tuple: (bool: True if rebalance needed, dict: current distribution)
        """
        # Check for pending transfers in database
        try:
            query = f"""
                SELECT COUNT(*) as count FROM {self.db_schema}.transfer_recommendations
                WHERE status = 'pending' AND asset_code = $1 AND asset_issuer = $2
            """
            # FIXED: Properly await with tuple parameters
            result = await self.db_manager.fetch_one(
                query, 
                (self.ubec_code, self.ubec_issuer)
            )
            
            if result and result['count'] > 0:
                self.logger.info(f"Found {result['count']} pending transfers, rebalance needed")
                
                # Get current distribution for reference
                if self.audit_service:
                    audit_report = await self.audit_service.perform_audit()
                    current_distribution = {
                        'general': Decimal(str(audit_report['distribution']['current']['general'])),
                        'administration': Decimal(str(audit_report['distribution']['current']['administration'])),
                        'stewardship': Decimal(str(audit_report['distribution']['current']['stewardship']))
                    }
                else:
                    # Use database balances
                    general_balance = await self.get_account_balance(self.accounts['general'])
                    admin_balance = await self.get_account_balance(self.accounts['administration'])
                    stewardship_info = await self.get_stewardship_balances()
                    total = general_balance + admin_balance + stewardship_info['total_direct']
                    
                    current_distribution = {
                        'general': general_balance / total if total > 0 else Decimal('0'),
                        'administration': admin_balance / total if total > 0 else Decimal('0'),
                        'stewardship': stewardship_info['total_direct'] / total if total > 0 else Decimal('0')
                    }
                
                return True, current_distribution
                
        except Exception as e:
            self.logger.error(f"Error checking pending transfers: {e}")
            self.logger.exception("Full traceback:")
        
        # Check if audit service is available
        if self.audit_service is None:
            self.logger.warning("Audit service not available - using database-only check")
            # Use database balances to check compliance
            compliance = await self._check_compliance_from_database(
                self.ubec_code, 
                self.ubec_issuer
            )
            
            # Extract distribution from compliance check
            current_dist = compliance.get('details', {}).get('current', {})
            current_distribution = {
                'general': Decimal('1.0') - Decimal(str(current_dist.get('administration', 0))) - Decimal(str(current_dist.get('stewardship', 0))),
                'administration': Decimal(str(current_dist.get('administration', 0))),
                'stewardship': Decimal(str(current_dist.get('stewardship', 0)))
            }
            
            # Return based on compliance check
            needs_rebalance = not compliance.get('overall', True)
            return needs_rebalance, current_distribution
        
        # Perform full audit check
        audit_report = await self.audit_service.perform_audit()
        
        current_distribution = {
            'general': Decimal(str(audit_report['distribution']['current']['general'])),
            'administration': Decimal(str(audit_report['distribution']['current']['administration'])),
            'stewardship': Decimal(str(audit_report['distribution']['current']['stewardship']))
        }
        
        supply_distribution = {
            'administration': Decimal(str(audit_report['distribution']['of_total_supply']['administration'])),
            'stewardship': Decimal(str(audit_report['distribution']['of_total_supply']['stewardship']))
        }
        
        # Log current state
        self.logger.info(
            f"Current distribution (of monitored): General={current_distribution['general']:.2%}, "
            f"Stewardship={current_distribution['stewardship']:.2%}, "
            f"Admin={current_distribution['administration']:.2%}"
        )
        
        self.logger.info(
            f"Current distribution (of total): "
            f"Stewardship={supply_distribution['stewardship']:.2%}, "
            f"Admin={supply_distribution['administration']:.2%}"
        )
        
        # Check deviations
        for category in ['administration', 'stewardship']:
            target = Decimal(str(self.target_distribution[category]))
            deviation = abs(supply_distribution[category] - target)
            
            if deviation > self.rebalance_threshold:
                self.logger.info(f"Rebalance needed: {category} deviation is {deviation:.2%}")
                return True, current_distribution
        
        self.logger.info("No rebalance needed, distribution within thresholds")
        return False, current_distribution
    
    # ========================================================================
    # TRANSFER EXECUTION METHODS
    # ========================================================================
    
    async def perform_rebalance(self) -> Dict[str, Any]:
        """
        Execute transactions to rebalance UBEC token distribution.
        
        Returns:
            dict: Rebalance operation results
        """
        self.logger.info("Starting rebalance operation")
        
        results = {
            'transfers_attempted': 0,
            'transfers_completed': 0,
            'transfers_failed': 0,
            'transactions': [],
            'errors': []
        }
        
        # Get pending transfers from database
        transfers = []
        try:
            query = f"""
                SELECT id, from_account_type as "from", to_account_type as "to", 
                       amount, priority, created_at
                FROM {self.db_schema}.transfer_recommendations
                WHERE status = 'pending' AND asset_code = $1 AND asset_issuer = $2
                ORDER BY priority DESC, created_at ASC
            """
            # FIXED: Properly await with tuple parameters
            db_transfers = await self.db_manager.fetch_all(
                query, 
                (self.ubec_code, self.ubec_issuer)
            )
            
            if db_transfers:
                self.logger.info(f"Found {len(db_transfers)} pending transfers in database")
                
                for transfer in db_transfers:
                    transfers.append({
                        "id": transfer['id'],
                        "from": transfer['from'],
                        "to": transfer['to'],
                        "amount": Decimal(str(transfer['amount'])),
                        "source": "database"
                    })
                    
        except Exception as e:
            self.logger.error(f"Error getting pending transfers: {e}")
            self.logger.exception("Full traceback:")
            results['errors'].append(str(e))
        
        # If no database transfers, get from auditor
        if not transfers and self.audit_service:
            audit_report = await self.audit_service.perform_audit()
            
            if audit_report.get("tokenomics_compliance", {}).get("overall", False):
                self.logger.info("Distribution already compliant, no transfers needed")
                return results
            
            # Get recommendations from audit service
            await self.audit_service.add_transfer_recommendations()
            auditor_transfers = audit_report.get("transfer_recommendations", {}).get("transfers", [])
            
            if not auditor_transfers:
                self.logger.info("No transfers recommended by auditor")
                return results
            
            for transfer in auditor_transfers:
                transfers.append({
                    "from": transfer['from'],
                    "to": transfer['to'],
                    "amount": Decimal(str(transfer['amount'])),
                    "source": "auditor"
                })
        elif not transfers:
            self.logger.warning("No pending transfers and audit service unavailable - cannot generate recommendations")
            return results
        
        # Log planned transfers
        for transfer in transfers:
            self.logger.info(
                f"Planning transfer: {transfer['amount']} UBEC from "
                f"{transfer['from']} to {transfer['to']}"
            )
        
        # Execute transfers
        for transfer in transfers:
            results['transfers_attempted'] += 1
            
            try:
                tx_result = await self._execute_transfer(transfer)
                
                if tx_result['success']:
                    results['transfers_completed'] += 1
                    results['transactions'].append(tx_result)
                else:
                    results['transfers_failed'] += 1
                    results['errors'].append(tx_result.get('error', 'Unknown error'))
                    
            except Exception as e:
                self.logger.error(f"Error executing transfer: {e}")
                self.logger.exception("Full traceback:")
                results['transfers_failed'] += 1
                results['errors'].append(str(e))
        
        # Invalidate cache after transfers
        await self._invalidate_cache()
        
        # Run post-transfer audit
        self.logger.info("Running post-transfer audit")
        
        if self.audit_service:
            post_audit = await self.audit_service.perform_audit()
            
            new_distribution = {
                'general': Decimal(str(post_audit['distribution']['current']['general'])),
                'administration': Decimal(str(post_audit['distribution']['current']['administration'])),
                'stewardship': Decimal(str(post_audit['distribution']['current']['stewardship']))
            }
        else:
            # Calculate distribution from balances
            general_balance = await self.get_account_balance(self.accounts['general'])
            admin_balance = await self.get_account_balance(self.accounts['administration'])
            stewardship_info = await self.get_stewardship_balances()
            total = general_balance + admin_balance + stewardship_info['total_direct']
            
            new_distribution = {
                'general': general_balance / total if total > 0 else Decimal('0'),
                'administration': admin_balance / total if total > 0 else Decimal('0'),
                'stewardship': stewardship_info['total_direct'] / total if total > 0 else Decimal('0')
            }
        
        self.logger.info(
            f"Distribution after rebalancing: General={new_distribution['general']:.2%}, "
            f"Stewardship={new_distribution['stewardship']:.2%}, "
            f"Admin={new_distribution['administration']:.2%}"
        )
        
        results['final_distribution'] = {
            'general': float(new_distribution['general']),
            'administration': float(new_distribution['administration']),
            'stewardship': float(new_distribution['stewardship'])
        }
        
        return results
    
    async def _execute_transfer(self, transfer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single transfer operation.
        
        Args:
            transfer: Transfer details dictionary
            
        Returns:
            dict: Transfer execution result
        """
        result = {
            'success': False,
            'transfer': transfer,
            'tx_hash': None,
            'error': None
        }
        
        try:
            from_category = transfer['from']
            to_category = transfer['to']
            amount = transfer['amount']
            
            # Determine source account
            if from_category == 'general':
                source_account = self.accounts['general']
                source_secret = self.secret_keys['general']
                available_balance = await self.get_account_balance(source_account)
                source_label = "General Distribution"
            elif from_category == 'administration':
                source_account = self.accounts['administration']
                source_secret = self.secret_keys['administration']
                available_balance = await self.get_account_balance(source_account)
                source_label = "Administration"
            else:  # stewardship
                source_account, source_secret, available_balance = \
                    await self.select_stewardship_account_for_transfer(amount, is_source=True)
                source_label = f"Stewardship ({source_account})"
            
            # Check sufficient balance
            buffer = Decimal('0.1')
            if available_balance < (amount + buffer):
                error_msg = f"Insufficient balance in {source_label}. Needed: {amount}, Available: {available_balance}"
                self.logger.warning(error_msg)
                
                if available_balance > buffer:
                    amount = available_balance - buffer
                    self.logger.info(f"Adjusting transfer amount to {amount}")
                else:
                    result['error'] = error_msg
                    
                    if "id" in transfer and transfer["source"] == "database":
                        await self._update_transfer_status(transfer["id"], 'failed', error_msg)
                    
                    return result
            
            # Validate positive amount
            if amount <= 0:
                error_msg = f"Transfer amount {amount} is not positive"
                self.logger.warning(error_msg)
                result['error'] = error_msg
                
                if "id" in transfer and transfer["source"] == "database":
                    await self._update_transfer_status(transfer["id"], 'failed', error_msg)
                
                return result
            
            # Determine destination account
            if to_category == 'general':
                destination_account = self.accounts['general']
                destination_label = "General Distribution"
            elif to_category == 'administration':
                destination_account = self.accounts['administration']
                destination_label = "Administration"
            else:  # stewardship
                destination_account, _, _ = \
                    await self.select_stewardship_account_for_transfer(amount, is_source=False)
                destination_label = f"Stewardship ({destination_account})"
            
            self.logger.info(
                f"Executing transfer: {amount} UBEC from {source_label} to {destination_label}"
            )
            
            # Execute Stellar transfer
            tx_hash = await self._execute_stellar_transfer(
                source_account,
                source_secret,
                destination_account,
                amount,
                source_label,
                destination_label
            )
            
            result['success'] = True
            result['tx_hash'] = tx_hash
            
            # Update database if this was a database transfer
            if "id" in transfer and transfer["source"] == "database":
                await self._update_transfer_status(
                    transfer["id"],
                    'completed',
                    f"Transaction completed: {tx_hash}"
                )
                
                # Update additional fields
                try:
                    update_query = f"""
                        UPDATE {self.db_schema}.transfer_recommendations
                        SET transaction_hash = $1,
                            actual_amount = $2,
                            completed_at = NOW()
                        WHERE id = $3
                    """
                    # FIXED: Properly await with tuple parameters
                    await self.db_manager.execute(
                        update_query, 
                        (tx_hash, float(amount), transfer["id"])
                    )
                except Exception as e:
                    self.logger.error(f"Error updating transaction details: {e}")
                    self.logger.exception("Full traceback:")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error executing transfer: {error_msg}")
            self.logger.exception("Full traceback:")
            result['error'] = error_msg
            
            if "id" in transfer and transfer["source"] == "database":
                await self._update_transfer_status(transfer["id"], 'failed', error_msg[:255])
        
        return result
    
    async def _execute_stellar_transfer(
        self,
        source_account: str,
        source_secret: str,
        destination_account: str,
        amount: Decimal,
        source_label: str,
        destination_label: str
    ) -> str:
        """
        Execute a transfer on the Stellar blockchain.
        
        Args:
            source_account: Source account address
            source_secret: Secret key for source
            destination_account: Destination address
            amount: Amount to transfer
            source_label: Label for logging
            destination_label: Label for logging
            
        Returns:
            str: Transaction hash
        """
        # Rate limit
        await self.rate_limiter.acquire()
        
        source_keypair = Keypair.from_secret(source_secret)
        
        try:
            # Load source account
            source_account_obj = await self.stellar_client.load_account(source_keypair.public_key)
            
            # Build transaction
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
            
            # Sign transaction
            transaction.sign(source_keypair)
            
            # Submit transaction
            response = await self.stellar_client.submit_transaction(transaction)
            
            tx_hash = response['hash']
            
            # Record in database
            await self._record_transfer_in_database(
                source_account,
                destination_account,
                amount,
                tx_hash,
                source_label,
                destination_label
            )
            
            self.logger.info(
                f"Transfer completed: {amount} UBEC from {source_label} "
                f"to {destination_label}, hash: {tx_hash}"
            )
            
            return tx_hash
            
        except BadRequestError as e:
            error_data = getattr(e, 'extras', {}).get('result_codes', {})
            op_errors = error_data.get('operations', [])
            
            if 'op_underfunded' in op_errors:
                self.logger.error(f"Underfunded error, retrying with reduced amount")
                
                # Retry with 80% of amount
                reduced_amount = amount * Decimal('0.8')
                self.logger.info(f"Retrying with {reduced_amount}")
                
                # Reload account
                source_account_obj = await self.stellar_client.load_account(source_keypair.public_key)
                
                # Build new transaction
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
                response = await self.stellar_client.submit_transaction(transaction)
                
                tx_hash = response['hash']
                
                await self._record_transfer_in_database(
                    source_account,
                    destination_account,
                    reduced_amount,
                    tx_hash,
                    source_label,
                    destination_label
                )
                
                self.logger.info(f"Reduced transfer completed: {reduced_amount} UBEC")
                return tx_hash
            else:
                raise
                
        except Exception as e:
            self.logger.error(f"Error executing Stellar transfer: {e}")
            self.logger.exception("Full traceback:")
            raise
    
    async def _record_transfer_in_database(
        self,
        source: str,
        destination: str,
        amount: Decimal,
        tx_hash: str,
        source_label: str,
        destination_label: str
    ) -> bool:
        """
        Record transfer in database for tracking.
        
        Args:
            source: Source account address
            destination: Destination address
            amount: Amount transferred
            tx_hash: Transaction hash
            source_label: Source label
            destination_label: Destination label
            
        Returns:
            bool: True if successful
        """
        try:
            # Update asset holder balances
            source_balance = await self.get_account_balance(source)
            dest_balance = await self.get_account_balance(destination)
            
            update_query = f"""
                SELECT {self.db_schema}.update_asset_holder_balance($1, $2, $3, $4)
            """
            
            # FIXED: Properly await with tuple parameters
            await self.db_manager.execute(
                update_query, 
                (source, self.ubec_code, self.ubec_issuer, float(source_balance))
            )
            
            await self.db_manager.execute(
                update_query, 
                (destination, self.ubec_code, self.ubec_issuer, float(dest_balance))
            )
            
            self.logger.info(f"Transfer recorded in database: {tx_hash}")
            
            # Record reciprocity impact
            if "Stewardship" in source_label or "Stewardship" in destination_label:
                await self._record_reciprocity_transaction(source, destination, amount, tx_hash)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording transfer in database: {e}")
            self.logger.exception("Full traceback:")
            return False
    
    async def _record_reciprocity_transaction(
        self,
        source: str,
        destination: str,
        amount: Decimal,
        tx_hash: str
    ) -> bool:
        """
        Record transfer impact on reciprocity scores.
        
        Args:
            source: Source account
            destination: Destination account
            amount: Amount transferred
            tx_hash: Transaction hash
            
        Returns:
            bool: True if successful
        """
        try:
            query = f"""
                INSERT INTO {self.db_schema}.reciprocity_transactions 
                (account_id, transaction_type, amount, reason, source, context, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """
            
            # FIXED: Properly await with tuple parameters - Source (debit)
            await self.db_manager.execute(
                query,
                (
                    source,
                    'debit',
                    float(amount),
                    'UBEC tokenomics rebalance',
                    'distribution_manager',
                    json.dumps({'tx_hash': tx_hash, 'destination': destination})
                )
            )
            
            # FIXED: Properly await with tuple parameters - Destination (credit)
            await self.db_manager.execute(
                query,
                (
                    destination,
                    'credit',
                    float(amount),
                    'UBEC tokenomics rebalance',
                    'distribution_manager',
                    json.dumps({'tx_hash': tx_hash, 'source': source})
                )
            )
            
            self.logger.info(f"Recorded reciprocity impact for {tx_hash}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording reciprocity: {e}")
            self.logger.exception("Full traceback:")
            return False
    
    async def _update_transfer_status(
        self,
        transfer_id: int,
        status: str,
        message: Optional[str] = None
    ) -> bool:
        """
        Update transfer recommendation status in database.
        
        Args:
            transfer_id: Transfer ID
            status: New status
            message: Optional message
            
        Returns:
            bool: True if successful
        """
        try:
            query = f"""
                UPDATE {self.db_schema}.transfer_recommendations
                SET status = $1, 
                    status_message = $2,
                    updated_at = NOW()
                WHERE id = $3
            """
            # FIXED: Properly await with tuple parameters
            await self.db_manager.execute(
                query, 
                (status, message, transfer_id)
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating transfer status: {e}")
            self.logger.exception("Full traceback:")
            return False
    
    # ========================================================================
    # STATUS AND MONITORING
    # ========================================================================
    
    async def get_distribution_status(self) -> Dict[str, Any]:
        """
        Get current distribution status and compliance information.
        
        Returns:
            dict: Comprehensive distribution status
        """
        try:
            # Get compliance
            compliance = await self.check_compliance()
            
            # Get balances
            general_balance = await self.get_account_balance(self.accounts['general'])
            admin_balance = await self.get_account_balance(self.accounts['administration'])
            stewardship_info = await self.get_stewardship_balances()
            
            # Check if rebalance needed
            needs_rebalance, current_dist = await self.is_rebalance_needed()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'asset_code': self.ubec_code,
                'asset_issuer': self.ubec_issuer,
                'compliance': compliance,
                'needs_rebalance': needs_rebalance,
                'balances': {
                    'general': float(general_balance),
                    'administration': float(admin_balance),
                    'stewardship': float(stewardship_info['total_direct']),
                    'stewardship_accounts': [
                        {
                            'label': acct['label'],
                            'address': acct['address'],
                            'balance': float(acct['balance'])
                        }
                        for acct in stewardship_info['accounts']
                    ]
                },
                'distribution_percentages': {
                    'general': float(current_dist['general']),
                    'administration': float(current_dist['administration']),
                    'stewardship': float(current_dist['stewardship'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting distribution status: {e}")
            self.logger.exception("Full traceback:")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def schedule_next_check(
        self, 
        interval_seconds: Optional[int] = None
    ) -> bool:
        """
        Schedule next distribution check in database scheduler.
        
        Args:
            interval_seconds: Check interval (uses config default if None)
            
        Returns:
            bool: True if successful
        """
        try:
            interval = interval_seconds or self.config.get('check_interval', 3600)
            next_run = datetime.now() + timedelta(seconds=interval)
            
            params = json.dumps({
                "parameters": [self.ubec_code, self.ubec_issuer]
            })
            
            query = f"""
                INSERT INTO {self.db_schema}.scheduler_jobs (
                    job_name, schedule_interval, next_run, job_function, parameters, enabled
                ) VALUES (
                    $1, $2, $3, $4, $5, $6
                )
                ON CONFLICT (job_name) DO UPDATE SET
                    schedule_interval = EXCLUDED.schedule_interval,
                    next_run = EXCLUDED.next_run,
                    job_function = EXCLUDED.job_function,
                    parameters = EXCLUDED.parameters,
                    enabled = EXCLUDED.enabled
            """
            
            # FIXED: Properly await with tuple parameters
            await self.db_manager.execute(
                query,
                (
                    'ubec_distribution_rebalance',
                    f'{interval} seconds',
                    next_run,
                    'SELECT check_distribution_balance($1, $2)',
                    params,
                    True
                )
            )
            
            self.logger.info(f"Scheduled next check for {next_run}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling next check: {e}")
            self.logger.exception("Full traceback:")
            return False
    
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
    
    This follows the service pattern - the ONLY way to create
    a distribution service instance.
    
    Args:
        db_manager: Async database manager
        config: System configuration
        stellar_client: Async Stellar client
        audit_service: Token audit service
        rate_limit_calls_per_second: API rate limit
        
    Returns:
        UBECDistributionService: Initialized service instance
    
    Example:
        service = create_distribution_service(
            db_manager=registry.get('database'),
            config=system_config.get_distribution_config(),
            stellar_client=registry.get('stellar'),
            audit_service=registry.get('audit')
        )
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
    'create_distribution_service'
]
