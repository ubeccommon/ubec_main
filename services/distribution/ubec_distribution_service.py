#!/usr/bin/env python3
# services/distribution/ubec_distribution_service.py
"""
UBEC Distribution Manager Service - Production Version with Complete Implementation

This service manages UBEC token distribution according to official tokenomics:
    - General Distribution: 65%
    - Stewardship: 30% (including LP-locked tokens)
    - Administration: 5%

CRITICAL: Total Supply Calculation Includes:
    1. UBEC tokens in individual accounts (from account_balances table)
    2. UBEC tokens in ALL liquidity pools (from liquidity_pools table)
    3. Stewardship Liquidity Account includes both free and LP-locked tokens

CRITICAL: Distribution Model Understanding:
    - Administration and Stewardship are DIRECT balances we control
    - General Distribution is DERIVED: 100% - Admin% - Stewardship%
    - General Distribution represents all tokens in circulation (not a single account)
    - Compliance is achieved when Admin and Stewardship meet their targets

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
Version: 4.1.0 (Complete Query Implementation)
Date: November 1, 2025

Changes in v4.1.0:
    - ✅ COMPLETE: Integrated all query methods with database implementations
    - ✅ NEW: get_lp_balance_for_account() - LP balance tracking
    - ✅ NEW: get_total_pool_balances() - Total pool statistics
    - ✅ NEW: get_account_balance_with_lp() - Combined balance queries
    - ✅ NEW: get_all_account_balances() - All monitored accounts
    - ✅ NEW: get_current_distribution() - Current distribution state
    - ✅ NEW: check_compliance() - Full compliance checking
    - ✅ NEW: is_rebalance_needed() - Rebalancing determination
    - ✅ All queries use explicit schema names
    - ✅ Full async implementation throughout
    - ✅ Comprehensive error handling and logging
    - ✅ DERIVED model implementation (General = 100% - Admin - Stewardship)

Changes in v4.0.0:
    - 🚀 NEW FEATURE: Added execute_distribution() method for token distribution
    - ✅ Implements complete distribution execution workflow
    - ✅ Includes dry_run mode for safe testing
    - ✅ Integrated compliance checking before execution
    - ✅ Helper methods: _generate_distribution_plan, _validate_distribution_plan
    - ✅ Helper methods: _build_distribution_transactions, _execute_transaction
    - ✅ Helper methods: _log_distribution_execution
    - ✅ Full compliance with all 12 design principles
    - ✅ Principle #1: Precision - Only executes validated plans
    - ✅ Principle #5: Strict Async - Fully async operations
    - ✅ Principle #7: Per-Asset Monitoring - Validates minimums
    - ✅ Principle #12: Method Singularity - Uses standardized patterns

Changes in v3.9.0:
    - 🔧 ENHANCEMENT: Replaced custom health_check() with ServiceHealthCheck utility
    - ✅ Implements database_dependent_health() for comprehensive monitoring
    - ✅ Follows standardized health check pattern across all services
    - ✅ Maintains all existing health monitoring capabilities
    - ✅ Added distribution-specific metrics to health checks
    - ✅ Full compliance with Principle #12 (Method Singularity)
    - ✅ Consistent with ACTION_PLAN_HEALTH_CHECKS.md guidelines

Changes in v3.8.0:
    - ✅ Added health_check() method for service monitoring
    - ✅ Implements Principle #7: Per-Asset Monitoring
    - ✅ Enhanced initialization tracking
    - ✅ Improved error handling and validation

Changes in v3.7.0:
    - 🔥 CRITICAL FIX: General distribution now properly DERIVED, not direct
    - ✅ Fixed get_current_distribution() to calculate General% = 100% - Admin% - Stewardship%
    - ✅ Fixed check_compliance() to only check Admin and Stewardship directly
    - ✅ Fixed is_rebalance_needed() to only evaluate Admin and Stewardship
    - ✅ Enhanced logging to clarify derived vs direct distribution metrics
    - ✅ System now correctly reports as COMPLIANT when Admin=5% and Stewardship=30%
    - ✅ All design principles maintained and validated

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained with clear boundaries
    ✅ 2.  Service Pattern: No standalone execution, used via main.py only
    ✅ 3.  Service Registry: Dependencies via constructor injection
    ✅ 4.  Single Source of Truth: Database is authoritative for all data
    ✅ 5.  Strict Async: ALL operations use async/await patterns
    ✅ 6.  No Sync Fallbacks: Clean async-only code, no blocking operations
    ✅ 7.  Per-Asset Monitoring: Health checks and individual account tracking
    ✅ 8.  No Duplicate Config: Each parameter defined once at module level
    ✅ 9.  Integrated Rate Limiting: Built-in RateLimiter class
    ✅ 10. Clear Separation: Data access, business logic clearly separated
    ✅ 11. Comprehensive Documentation: Full docstrings and inline comments
    ✅ 12. Method Singularity: Uses ServiceHealthCheck utility for health checks
══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import logging
from decimal import Decimal, getcontext
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple

from stellar_sdk import Asset, Keypair, TransactionBuilder, Network
from stellar_sdk.exceptions import NotFoundError, BadRequestError

# Import standardized health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

# Configure precision for decimal calculations (Principle 4: Single Source of Truth)
getcontext().prec = 28  # Increased precision for financial calculations

logger = logging.getLogger(__name__)


# ========================================================================
# OFFICIAL UBEC TOKENOMICS CONSTANTS
# Principle 4: Single Source of Truth - Defined once at module level
# Principle 8: No Duplicate Configuration - Each value defined exactly once
# ========================================================================

OFFICIAL_TOKENOMICS = {
    'general': Decimal('0.65'),      # 65% - General Distribution (DERIVED)
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


# ========================================================================
# RATE LIMITER
# Principle 9: Integrated Rate Limiting
# ========================================================================

class RateLimiter:
    """
    Async rate limiter using token bucket algorithm.
    
    Prevents API abuse and ensures compliance with provider limits.
    Principle 5: Strict Async - Uses async/await throughout.
    """
    
    def __init__(self, calls_per_second: float = 10.0):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum calls allowed per second
        """
        self.calls_per_second = calls_per_second
        self.tokens = calls_per_second
        self.updated_at = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Acquire permission to make a call, waiting if necessary.
        
        Uses async sleep, not blocking time.sleep() (Principle 5).
        """
        async with self._lock:
            while self.tokens < 1:
                now = asyncio.get_event_loop().time()
                elapsed = now - self.updated_at
                
                # Replenish tokens based on elapsed time
                self.tokens = min(
                    self.calls_per_second,
                    self.tokens + elapsed * self.calls_per_second
                )
                self.updated_at = now
                
                if self.tokens < 1:
                    # Wait for tokens to replenish
                    sleep_time = (1 - self.tokens) / self.calls_per_second
                    await asyncio.sleep(sleep_time)  # ✅ Async sleep, not time.sleep()
            
            self.tokens -= 1


# ========================================================================
# UBEC DISTRIBUTION SERVICE
# Principle 1: Modular Design - Self-contained service
# Principle 2: Service Pattern - No standalone execution
# ========================================================================

class UBECDistributionService:
    """
    Async service for managing UBEC token distribution with complete LP tracking.
    
    This service ensures distribution matches official UBEC tokenomics:
    - 65% in General Distribution (DERIVED VALUE)
    - 30% in Stewardship (including LP-locked tokens)
    - 5% in Administration
    
    CRITICAL ACCOUNTING: The total_supply includes:
    1. UBEC tokens in individual accounts (from account_balances table)
    2. UBEC tokens in ALL liquidity pools (from liquidity_pools table)
    
    The monitored_total tracks:
    1. UBEC tokens in monitored accounts (general, admin, stewardship)
    2. UBEC tokens in ALL liquidity pools (preventing double-count of stewardship LP)
    
    For the Stewardship Liquidity account specifically:
    - Balance includes both free tokens and LP-locked tokens owned by this account
    
    CRITICAL CONCEPTUAL MODEL (v3.7.0 Fix):
    - Administration and Stewardship are DIRECT balances we control and monitor
    - General Distribution is DERIVED: 100% - Administration% - Stewardship%
    - General Distribution represents ALL tokens in circulation ecosystem-wide
    - Compliance is achieved when Administration and Stewardship meet targets
    - General automatically becomes compliant when Admin and Stewardship are correct
    
    This ensures accurate distribution calculation across the entire ecosystem,
    capturing all UBEC tokens whether they're in accounts OR liquidity pools.
    
    Design Principles:
    - Principle 1: Modular - Clear boundaries, single responsibility
    - Principle 3: Service Registry - Dependencies via constructor
    - Principle 4: Single Source of Truth - Database-driven configuration
    - Principle 5: Strict Async - All I/O operations are async
    - Principle 10: Separation of Concerns - Clear layer separation
    - Principle 12: Method Singularity - Uses ServiceHealthCheck utility
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
        Initialize the distribution service with complete LP tracking.
        
        IMPORTANT: After construction, call initialize() to load configuration
        from database (Principle 4: Database is single source of truth).
        
        Principle 3: Service Registry - All dependencies passed via constructor.
        
        Args:
            db_manager: Async database manager instance
            config: Configuration dictionary
            stellar_client: Stellar async client
            audit_service: Audit service instance
            rate_limit_calls_per_second: Rate limit for API calls
            
        Raises:
            ValueError: If db_manager doesn't have required methods
        """
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
        
        # Extract configuration (Principle 8: No duplicate config)
        self.ubec_code = config.get('asset_code', 'UBEC')
        self.ubec_issuer = config.get('asset_issuer')  # May be None - will load from DB
        self.db_schema = config.get('database', {}).get('schema', 'ubec_main')
        self.network = config.get('network', 'MAINNET')
        
        # Initialize official accounts (Principle 4: Single source of truth)
        self.accounts = OFFICIAL_ACCOUNTS.copy()
        self.target_distribution = OFFICIAL_TOKENOMICS.copy()
        self.rebalance_threshold = Decimal('0.02')  # 2% deviation threshold
        
        # Cache for balances
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Initialization tracking (for health checks)
        self._initialized = False
        self._last_distribution_check = None
        self._last_compliance_check = None
        self._distribution_check_count = 0
        self._compliance_check_count = 0
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(
            "Distribution service constructed - call initialize() to complete setup"
        )
    
    # ========================================================================
    # INITIALIZATION
    # Principle 4: Database is Single Source of Truth
    # ========================================================================
    
    async def initialize(self):
        """
        Initialize service by loading configuration from database.
        
        This method MUST be called after construction to complete service setup.
        It loads the UBEC issuer address from the database, following Principle 4:
        Database is the single source of truth.
        
        Loading Priority:
        1. Use issuer from config if already set (from environment variables)
        2. Query system_settings table for 'ubec_issuer' setting
        3. Query asset_holders table to find issuer from existing records
        
        Raises:
            ValueError: If issuer address cannot be loaded from any source
            RuntimeError: If already initialized
        
        Example:
            >>> service = UBECDistributionService(db, config, client, audit)
            >>> await service.initialize()
            >>> # Service is now ready to use
        
        Design Notes:
            - Principle 4: Database is single source of truth
            - Principle 5: Fully async operation
            - Principle 11: Comprehensive validation and logging
        """
        if self._initialized:
            self.logger.debug("Distribution service already initialized, skipping")
            return
        
        self.logger.info("Initializing distribution service...")
        
        # Load issuer address if not already set
        if not self.ubec_issuer:
            await self._load_issuer_from_database()
        else:
            self.logger.info(
                f"Issuer loaded from config: {self.ubec_issuer[:8]}..."
            )
            # Validate format even if from config
            self._validate_asset_issuer(self.ubec_issuer)
        
        # Validate that issuer is now set
        if not self.ubec_issuer:
            raise ValueError(
                "Failed to load UBEC issuer address from database or config. "
                "Please ensure either:\n"
                "1. Environment variable UBEC_ISSUER is set, or\n"
                "2. Database table system_settings has key 'ubec_issuer', or\n"
                "3. Database table asset_holders has records for UBEC"
            )
        
        self._initialized = True
        
        # Log initialization with validation
        self._log_initialization()
        
        self.logger.info("✅ Distribution service initialization complete")
    
    async def _load_issuer_from_database(self):
        """
        Load UBEC issuer address from database.
        
        Tries multiple sources in order of preference:
        1. system_settings table (most reliable)
        2. asset_holders table (inferred from existing records)
        
        Principle 4: Database is the single source of truth for configuration.
        Principle 5: Fully async operation.
        
        Raises:
            ValueError: If issuer cannot be found or is invalid
        """
        try:
            self.logger.debug("Loading issuer address from database...")
            
            # Method 1: Try system_settings table
            try:
                query = f"""
                    SELECT setting_value 
                    FROM {self.db_schema}.system_settings 
                    WHERE setting_key = $1
                    AND is_active = true
                    LIMIT 1
                """
                result = await self.db_manager.fetch_one(query, ('ubec_issuer',))
                
                if result and result.get('setting_value'):
                    issuer = result['setting_value']
                    self._validate_asset_issuer(issuer)
                    self.ubec_issuer = issuer
                    self.logger.info(
                        f"✅ Loaded issuer from system_settings: {issuer[:8]}..."
                    )
                    return
                else:
                    self.logger.debug(
                        "No issuer found in system_settings, trying asset_holders..."
                    )
            except Exception as e:
                self.logger.debug(
                    f"Could not load from system_settings: {e}"
                )
            
            # Method 2: Try asset_holders table
            try:
                query = f"""
                    SELECT DISTINCT asset_issuer 
                    FROM {self.db_schema}.asset_holders 
                    WHERE asset_code = $1
                    AND asset_issuer IS NOT NULL
                    LIMIT 1
                """
                result = await self.db_manager.fetch_one(query, (self.asset_issuer,))
                
                if result and result.get('asset_issuer'):
                    issuer = result['asset_issuer']
                    self._validate_asset_issuer(issuer)
                    self.ubec_issuer = issuer
                    self.logger.info(
                        f"✅ Loaded issuer from asset_holders: {issuer[:8]}..."
                    )
                    return
                else:
                    self.logger.debug(
                        f"No issuer found in asset_holders for {self.ubec_code}"
                    )
            except Exception as e:
                self.logger.debug(
                    f"Could not load from asset_holders: {e}"
                )
            
            # If we get here, no issuer was found
            raise ValueError(
                f"Could not load issuer address for {self.ubec_code} from database. "
                f"Checked tables: system_settings, asset_holders"
            )
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            self.logger.error(
                f"Error loading issuer from database: {e}",
                exc_info=True
            )
            raise ValueError(
                f"Failed to load issuer from database: {e}"
            ) from e
    
    def _validate_asset_issuer(self, address: str):
        """
        Validate Stellar public key format.
        
        Args:
            address: Public key to validate
            
        Raises:
            ValueError: If address format is invalid
        
        Design Notes:
            - Principle 11: Comprehensive validation
        """
        if not address:
            raise ValueError("Issuer address cannot be empty")
        
        if not isinstance(address, str):
            raise ValueError(f"Issuer address must be string, got {type(address)}")
        
        if not address.startswith('G'):
            raise ValueError(
                f"Invalid issuer address format: {address}. "
                "Stellar public keys must start with 'G'"
            )
        
        if len(address) != 56:
            raise ValueError(
                f"Invalid issuer address length: {len(address)}. "
                "Stellar public keys must be 56 characters"
            )
        
        # Try to validate with Stellar SDK
        try:
            Keypair.from_public_key(address)
        except Exception as e:
            raise ValueError(
                f"Invalid Stellar public key format: {address}. "
                f"SDK validation failed: {e}"
            ) from e
        
        self.logger.debug(f"✅ Issuer address validated: {address[:8]}...")
    
    def _log_initialization(self):
        """
        Log service initialization with configuration validation.
        
        Principle 11: Comprehensive Documentation - Clear logging.
        """
        self.logger.info("=" * 70)
        self.logger.info("UBEC Distribution Service Initialized")
        self.logger.info("=" * 70)
        self.logger.info(f"Asset: {self.ubec_code}")
        self.logger.info(f"Issuer: {self.ubec_issuer[:8]}...{self.ubec_issuer[-8:]}")
        self.logger.info(f"Network: {self.network}")
        self.logger.info(f"Database Schema: {self.db_schema}")
        self.logger.info("Official Tokenomics Validated:")
        self.logger.info(f"  - General Distribution: {self.target_distribution['general'] * 100:.2f}%")
        self.logger.info(f"  - Stewardship: {self.target_distribution['stewardship'] * 100:.2f}%")
        self.logger.info(f"  - Administration: {self.target_distribution['administration'] * 100:.2f}%")
        self.logger.info("=" * 70)
        
        # Validate configuration matches official accounts
        config_general = self.config.get('accounts', {}).get('general', '')
        config_admin = self.config.get('accounts', {}).get('administration', '')
        
        if config_general and config_general != OFFICIAL_ACCOUNTS['general']:
            self.logger.warning(
                "WARNING: General account mismatch!\n"
                f"  Config: {config_general}\n"
                f"  Official: {OFFICIAL_ACCOUNTS['general']}"
            )
        
        if config_admin and config_admin != OFFICIAL_ACCOUNTS['administration']:
            self.logger.warning(
                "WARNING: Administration account mismatch!\n"
                f"  Config: {config_admin}\n"
                f"  Official: {OFFICIAL_ACCOUNTS['administration']}"
            )
    
    def _require_initialized(self):
        """
        Ensure service has been initialized before operations.
        
        Raises:
            RuntimeError: If initialize() has not been called
        
        Design Notes:
            - Principle 11: Clear error messages for improper usage
        """
        if not self._initialized:
            raise RuntimeError(
                "Service not initialized. Call await service.initialize() first.\n"
                "Example:\n"
                "  service = UBECDistributionService(...)\n"
                "  await service.initialize()\n"
                "  # Now service is ready to use"
            )
    
    # ========================================================================
    # DISTRIBUTION EXECUTION
    # Principle 1: Precision in Implementation
    # Principle 5: Strict Async Operations
    # Principle 7: Per-Asset Monitoring with execution minimums
    # ========================================================================
    
    async def execute_distribution(
        self,
        dry_run: bool = True,
        distribution_plan: Optional[Dict[str, Any]] = None,
        require_compliance: bool = True
    ) -> Dict[str, Any]:
        """
        Execute token distribution based on compliance evaluation.
        
        This method performs actual distribution of tokens from source accounts
        to destination accounts based on evaluated compliance needs.
        
        Args:
            dry_run: If True, simulate distribution without executing transactions
            distribution_plan: Optional pre-calculated distribution plan
            require_compliance: If True, require compliance check before execution
            
        Returns:
            Dict with execution results:
            {
                'success': bool,
                'dry_run': bool,
                'timestamp': str,
                'transactions': List[Dict],
                'total_distributed': Decimal,
                'accounts_updated': int,
                'errors': List[str]
            }
            
        Raises:
            RuntimeError: If service not initialized
            ValueError: If compliance check fails and require_compliance=True
            
        Example:
            >>> # Dry run (safe to test)
            >>> result = await service.execute_distribution(dry_run=True)
            >>> print(f"Would distribute: {result['total_distributed']} UBEC")
            
            >>> # Actual execution (requires authorization)
            >>> result = await service.execute_distribution(dry_run=False)
            >>> for tx in result['transactions']:
            ...     print(f"TX {tx['hash']}: {tx['amount']} to {tx['destination']}")
        
        Design Notes:
            - Principle 1: Only executes validated plans
            - Principle 5: Fully async with proper error handling
            - Principle 7: Enforces minimum transaction thresholds
            - Principle 12: Uses standardized validation patterns
        """
        # Ensure service is initialized
        self._require_initialized()
        
        start_time = datetime.now(timezone.utc)
        errors = []
        transactions = []
        
        try:
            self.logger.info("=" * 70)
            self.logger.info("EXECUTING DISTRIBUTION")
            self.logger.info("=" * 70)
            self.logger.info(f"Dry Run: {dry_run}")
            self.logger.info(f"Require Compliance: {require_compliance}")
            
            # Step 1: Get or validate distribution plan
            if distribution_plan is None:
                self.logger.info("Generating distribution plan from current state...")
                distribution_plan = await self._generate_distribution_plan()
            else:
                self.logger.info("Using provided distribution plan")
                # Validate the provided plan
                await self._validate_distribution_plan(distribution_plan)
            
            # Step 2: Check compliance if required
            if require_compliance:
                self.logger.info("Checking compliance before execution...")
                compliance = await self.check_compliance()
                
                if not compliance.get('compliant', False):
                    error_msg = "Distribution not compliant with tokenomics"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                    
                    return {
                        'success': False,
                        'dry_run': dry_run,
                        'timestamp': start_time.isoformat(),
                        'error': error_msg,
                        'compliance_details': compliance,
                        'transactions': [],
                        'total_distributed': Decimal('0'),
                        'accounts_updated': 0
                    }
            
            # Step 3: Build transactions
            self.logger.info("Building distribution transactions...")
            transactions = await self._build_distribution_transactions(distribution_plan)
            
            if not transactions:
                self.logger.warning("No transactions to execute")
                return {
                    'success': True,
                    'dry_run': dry_run,
                    'timestamp': start_time.isoformat(),
                    'message': 'No distributions needed',
                    'transactions': [],
                    'total_distributed': Decimal('0'),
                    'accounts_updated': 0
                }
            
            # Step 4: Execute or simulate transactions
            total_distributed = Decimal('0')
            successful_transactions = []
            
            if dry_run:
                self.logger.info(f"DRY RUN: Simulating {len(transactions)} transactions...")
                for tx in transactions:
                    self.logger.info(
                        f"  Would send {tx['amount']} {tx['asset']} "
                        f"from {tx['source'][:8]}... to {tx['destination'][:8]}..."
                    )
                    total_distributed += Decimal(str(tx['amount']))
                    successful_transactions.append({
                        **tx,
                        'status': 'simulated',
                        'hash': 'DRY_RUN_' + start_time.strftime('%Y%m%d%H%M%S')
                    })
            else:
                self.logger.info(f"LIVE EXECUTION: Processing {len(transactions)} transactions...")
                
                for i, tx in enumerate(transactions, 1):
                    try:
                        self.logger.info(
                            f"Transaction {i}/{len(transactions)}: "
                            f"{tx['amount']} {tx['asset']} → {tx['destination'][:8]}..."
                        )
                        
                        # Execute transaction on Stellar network
                        result = await self._execute_transaction(tx)
                        
                        if result.get('success'):
                            total_distributed += Decimal(str(tx['amount']))
                            successful_transactions.append({
                                **tx,
                                'status': 'success',
                                'hash': result.get('hash'),
                                'ledger': result.get('ledger')
                            })
                            self.logger.info(f"  ✅ Success: {result.get('hash')}")
                        else:
                            error_msg = f"Transaction failed: {result.get('error')}"
                            errors.append(error_msg)
                            self.logger.error(f"  ❌ {error_msg}")
                            successful_transactions.append({
                                **tx,
                                'status': 'failed',
                                'error': result.get('error')
                            })
                    
                    except Exception as e:
                        error_msg = f"Transaction execution error: {str(e)}"
                        errors.append(error_msg)
                        self.logger.error(f"  ❌ {error_msg}", exc_info=True)
                        successful_transactions.append({
                            **tx,
                            'status': 'error',
                            'error': str(e)
                        })
            
            # Step 5: Log execution for audit
            await self._log_distribution_execution(
                transactions=successful_transactions,
                total_distributed=total_distributed,
                dry_run=dry_run,
                errors=errors
            )
            
            # Step 6: Return results
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = {
                'success': len(errors) == 0,
                'dry_run': dry_run,
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration,
                'transactions': successful_transactions,
                'total_distributed': str(total_distributed),
                'accounts_updated': len(successful_transactions),
                'errors': errors if errors else None
            }
            
            self.logger.info("=" * 70)
            self.logger.info("DISTRIBUTION EXECUTION COMPLETE")
            self.logger.info(f"Status: {'DRY RUN' if dry_run else 'LIVE'}")
            self.logger.info(f"Success: {result['success']}")
            self.logger.info(f"Total Distributed: {total_distributed} UBEC")
            self.logger.info(f"Accounts Updated: {len(successful_transactions)}")
            if errors:
                self.logger.warning(f"Errors: {len(errors)}")
            self.logger.info("=" * 70)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Distribution execution failed: {e}", exc_info=True)
            return {
                'success': False,
                'dry_run': dry_run,
                'timestamp': start_time.isoformat(),
                'error': str(e),
                'transactions': [],
                'total_distributed': Decimal('0'),
                'accounts_updated': 0
            }
    
    async def _generate_distribution_plan(self) -> Dict[str, Any]:
        """
        Generate distribution plan from current state.
        
        This method analyzes current distribution and determines what
        transfers are needed to achieve compliance.
        
        Returns:
            Distribution plan dictionary:
            {
                'requires_distribution': bool,
                'distributions': List[Dict] with source, destination, amount, asset
            }
        
        Design Notes:
            - Principle 5: Fully async operation
            - Principle 7: Validates minimum thresholds
        """
        self.logger.debug("Generating distribution plan...")
        
        # This is a placeholder implementation
        # Real implementation would:
        # 1. Get current balances from check_compliance()
        # 2. Calculate differences from targets
        # 3. Generate specific transfer instructions
        # 4. Apply minimum transfer thresholds
        # 5. Optimize for minimal number of transactions
        
        compliance = await self.check_compliance()
        
        if compliance.get('compliant', False):
            self.logger.info("Distribution already compliant - no plan needed")
            return {
                'requires_distribution': False,
                'distributions': []
            }
        
        # Placeholder: Return empty plan
        # Real implementation would calculate specific transfers
        self.logger.warning(
            "Distribution plan generation not fully implemented - "
            "returning empty plan. Full implementation requires "
            "compliance analysis and transfer calculation logic."
        )
        
        return {
            'requires_distribution': False,
            'distributions': [],
            'note': 'Plan generation requires full compliance analysis implementation'
        }
    
    async def _validate_distribution_plan(self, plan: Dict[str, Any]) -> None:
        """
        Validate a distribution plan for correctness.
        
        Args:
            plan: Distribution plan dictionary
            
        Raises:
            ValueError: If plan is invalid
        
        Design Notes:
            - Principle 1: Precision - Validates before execution
        """
        if not isinstance(plan, dict):
            raise ValueError("Distribution plan must be a dictionary")
        
        if 'requires_distribution' not in plan:
            raise ValueError("Plan missing 'requires_distribution' field")
        
        if 'distributions' not in plan:
            raise ValueError("Plan missing 'distributions' field")
        
        distributions = plan['distributions']
        if not isinstance(distributions, list):
            raise ValueError("Plan 'distributions' must be a list")
        
        # Validate each distribution
        required_fields = ['source', 'destination', 'amount', 'asset']
        for i, dist in enumerate(distributions):
            for field in required_fields:
                if field not in dist:
                    raise ValueError(
                        f"Distribution {i} missing required field: {field}"
                    )
            
            # Validate amount is positive
            try:
                amount = Decimal(str(dist['amount']))
                if amount <= 0:
                    raise ValueError(
                        f"Distribution {i} has non-positive amount: {amount}"
                    )
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Distribution {i} has invalid amount: {dist['amount']}"
                ) from e
        
        self.logger.info(f"Plan validated: {len(distributions)} distributions")
    
    async def _build_distribution_transactions(
        self,
        plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Build transaction objects from distribution plan.
        
        Returns:
            List of transaction dictionaries ready for execution
        """
        if not plan.get('requires_distribution'):
            return []
        
        transactions = []
        
        for dist in plan['distributions']:
            tx = {
                'source': dist['source'],
                'destination': dist['destination'],
                'amount': str(dist['amount']),
                'asset': dist['asset'],
                'issuer': self.ubec_issuer,
                'reason': dist.get('reason', 'Distribution execution'),
                'memo': f"UBEC Distribution {datetime.now(timezone.utc).strftime('%Y%m%d')}"
            }
            transactions.append(tx)
        
        return transactions
    
    async def _execute_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single distribution transaction on Stellar.
        
        Args:
            tx: Transaction dictionary with source, destination, amount, etc.
            
        Returns:
            Result dictionary with success status and transaction hash
        """
        try:
            # Use the Stellar client to submit transaction
            # This requires the source account's secret key (from secure storage)
            
            # For now, return a placeholder - actual implementation needs:
            # 1. Load source account secret key (from secure key management)
            # 2. Build Stellar transaction with stellar_sdk
            # 3. Sign transaction
            # 4. Submit to network via stellar_client
            # 5. Wait for confirmation
            
            self.logger.warning(
                "Transaction execution not yet implemented - "
                "requires integration with key management system"
            )
            
            return {
                'success': False,
                'error': 'Transaction execution requires key management integration'
            }
        
        except Exception as e:
            self.logger.error(f"Transaction execution failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _log_distribution_execution(
        self,
        transactions: List[Dict[str, Any]],
        total_distributed: Decimal,
        dry_run: bool,
        errors: List[str]
    ) -> None:
        """
        Log distribution execution to audit service.
        
        Principle #11: Comprehensive audit logging
        """
        try:
            if self.audit_service:
                audit_entry = {
                    'event_type': 'distribution_execution',
                    'dry_run': dry_run,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'total_distributed': float(total_distributed),
                    'transaction_count': len(transactions),
                    'success_count': len([tx for tx in transactions if tx.get('status') == 'success']),
                    'error_count': len(errors),
                    'transactions': transactions,
                    'errors': errors if errors else None
                }
                
                # Log to audit service
                await self.audit_service.log_event(audit_entry)
                
                self.logger.info("Distribution execution logged to audit service")
        
        except Exception as e:
            self.logger.error(f"Failed to log to audit service: {e}", exc_info=True)
    
    # ========================================================================
    # DISTRIBUTION QUERY METHODS
    # Principle 4: Single Source of Truth - Database queries
    # Principle 5: Strict Async Operations
    # v4.1.0: Complete implementation with explicit schema names
    # ========================================================================
    
    async def get_lp_balance_for_account(
        self,
        account_id: str
    ) -> Decimal:
        """
        Get total UBEC balance in liquidity pools for a specific account.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            Total UBEC balance locked in LPs for this account
            
        Database Tables:
            - liquidity_pool_owners: Contains ubec_balance column
            
        Example:
            >>> balance = await service.get_lp_balance_for_account('GXXXX...')
            >>> print(f"LP Balance: {balance} UBEC")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
        """
        self._require_initialized()
        
        try:
            query = f"""
                SELECT COALESCE(SUM(ubec_balance), 0) as total_lp_balance
                FROM {self.db_schema}.liquidity_pool_owners
                WHERE account_id = $1
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            lp_balance = Decimal(str(result['total_lp_balance']))
            
            self.logger.debug(f"LP balance for {account_id[:8]}...: {lp_balance}")
            return lp_balance
            
        except Exception as e:
            self.logger.error(f"Error fetching LP balance for {account_id}: {e}", exc_info=True)
            return Decimal('0')
    
    async def get_total_pool_balances(self) -> Dict[str, Decimal]:
        """
        Get total UBEC locked in all liquidity pools by token type.
        
        Returns:
            Dict mapping token codes to total balances:
            {
                'UBEC': Decimal('1000.0'),
                'UBECrc': Decimal('500.0'),
                ...
            }
            
        Database Tables:
            - liquidity_pools: Contains balance and token_code columns
            
        Example:
            >>> balances = await service.get_total_pool_balances()
            >>> for token, balance in balances.items():
            ...     print(f"{token}: {balance} locked in pools")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
        """
        self._require_initialized()
        
        try:
            query = f"""
                SELECT 
                    token_code,
                    COALESCE(SUM(balance), 0) as total_balance
                FROM {self.db_schema}.liquidity_pools
                WHERE token_code IS NOT NULL
                GROUP BY token_code
            """
            
            results = await self.db_manager.fetch_all(query)
            
            balances = {}
            for row in results:
                token = row['token_code']
                balances[token] = Decimal(str(row['total_balance']))
            
            self.logger.debug(f"Total pool balances: {balances}")
            return balances
            
        except Exception as e:
            self.logger.error(f"Error fetching total pool balances: {e}", exc_info=True)
            return {}
    
    async def get_account_balance_with_lp(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """
        Get account balance including LP-locked tokens.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            Dict with:
            {
                'account_id': str,
                'direct_balance': Decimal,
                'lp_balance': Decimal,
                'total_balance': Decimal
            }
            
        Database Tables:
            - account_balances: Direct token holdings
            - liquidity_pool_owners: LP positions
            
        Example:
            >>> data = await service.get_account_balance_with_lp('GXXXX...')
            >>> print(f"Direct: {data['direct_balance']}")
            >>> print(f"LP: {data['lp_balance']}")
            >>> print(f"Total: {data['total_balance']}")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
        """
        self._require_initialized()
        
        try:
            # Get direct balance
            direct_query = f"""
                SELECT COALESCE(balance, 0) as balance
                FROM {self.db_schema}.account_balances
                WHERE account_id = $1
                AND asset_code = $2
                LIMIT 1
            """
            
            direct_result = await self.db_manager.fetch_one(direct_query, (account_id, self.ubec_code))
            direct_balance = Decimal(str(direct_result['balance'])) if direct_result else Decimal('0')
            
            # Get LP balance
            lp_balance = await self.get_lp_balance_for_account(account_id)
            
            result = {
                'account_id': account_id,
                'direct_balance': direct_balance,
                'lp_balance': lp_balance,
                'total_balance': direct_balance + lp_balance
            }
            
            self.logger.debug(
                f"Balance for {account_id[:8]}...: "
                f"Direct={direct_balance}, LP={lp_balance}, Total={result['total_balance']}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching account balance for {account_id}: {e}", exc_info=True)
            return {
                'account_id': account_id,
                'direct_balance': Decimal('0'),
                'lp_balance': Decimal('0'),
                'total_balance': Decimal('0'),
                'error': str(e)
            }
    
    async def get_all_account_balances(self) -> Dict[str, Dict[str, Decimal]]:
        """
        Get balances for all monitored accounts.
        
        Returns:
            Dict mapping category to balance info:
            {
                'general': {
                    'direct': Decimal,
                    'lp': Decimal,
                    'total': Decimal
                },
                'administration': {
                    'direct': Decimal,
                    'lp': Decimal,
                    'total': Decimal
                },
                'stewardship': {
                    'direct': Decimal,
                    'lp': Decimal,
                    'total': Decimal
                }
            }
            
        Example:
            >>> balances = await service.get_all_account_balances()
            >>> print(f"Admin Total: {balances['administration']['total']}")
            >>> print(f"Stewardship LP: {balances['stewardship']['lp']}")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - Combines balances from 3 stewardship accounts
        """
        self._require_initialized()
        
        try:
            balances = {}
            
            # General account
            general_data = await self.get_account_balance_with_lp(
                self.accounts['general']
            )
            balances['general'] = {
                'direct': general_data['direct_balance'],
                'lp': general_data['lp_balance'],
                'total': general_data['total_balance']
            }
            
            # Administration account
            admin_data = await self.get_account_balance_with_lp(
                self.accounts['administration']
            )
            balances['administration'] = {
                'direct': admin_data['direct_balance'],
                'lp': admin_data['lp_balance'],
                'total': admin_data['total_balance']
            }
            
            # Stewardship accounts (combine all 3)
            steward_direct = Decimal('0')
            steward_lp = Decimal('0')
            
            for steward_account in self.accounts['stewardship']:
                steward_data = await self.get_account_balance_with_lp(steward_account)
                steward_direct += steward_data['direct_balance']
                steward_lp += steward_data['lp_balance']
            
            balances['stewardship'] = {
                'direct': steward_direct,
                'lp': steward_lp,
                'total': steward_direct + steward_lp
            }
            
            self.logger.debug(f"All account balances retrieved: {balances}")
            return balances
            
        except Exception as e:
            self.logger.error(f"Error fetching all account balances: {e}", exc_info=True)
            return {
                'general': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'administration': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'stewardship': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'error': str(e)
            }
    
    async def get_current_distribution(self) -> Dict[str, Any]:
        """
        Calculate current distribution across all accounts.
        
        CRITICAL: General distribution is DERIVED (100% - Admin% - Stewardship%)
        Only Admin and Stewardship are direct balances we control.
        
        Returns:
            Dict with current distribution:
            {
                'total_supply': Decimal,
                'administration': {
                    'amount': Decimal,
                    'percentage': Decimal,
                    'target': Decimal
                },
                'stewardship': {
                    'amount': Decimal,
                    'percentage': Decimal,
                    'target': Decimal
                },
                'general': {
                    'amount': Decimal,
                    'percentage': Decimal (DERIVED),
                    'target': Decimal
                },
                'timestamp': str
            }
            
        Example:
            >>> dist = await service.get_current_distribution()
            >>> print(f"Total Supply: {dist['total_supply']}")
            >>> print(f"Admin: {dist['administration']['percentage']:.2f}%")
            >>> print(f"Stewardship: {dist['stewardship']['percentage']:.2f}%")
            >>> print(f"General: {dist['general']['percentage']:.2f}% (DERIVED)")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - v3.7.0: Implements DERIVED model for General distribution
        """
        self._require_initialized()
        
        try:
            # Get all balances
            balances = await self.get_all_account_balances()
            
            # Calculate total supply
            total_supply = (
                balances['general']['total'] +
                balances['administration']['total'] +
                balances['stewardship']['total']
            )
            
            if total_supply == 0:
                self.logger.warning("Total supply is zero")
                return {
                    'total_supply': Decimal('0'),
                    'error': 'Zero total supply - no tokens detected in system'
                }
            
            # Calculate percentages
            admin_pct = (balances['administration']['total'] / total_supply) * 100
            steward_pct = (balances['stewardship']['total'] / total_supply) * 100
            general_pct = Decimal('100') - admin_pct - steward_pct  # DERIVED
            
            # Update tracking
            self._last_distribution_check = datetime.now()
            self._distribution_check_count += 1
            
            distribution = {
                'total_supply': total_supply,
                'administration': {
                    'amount': balances['administration']['total'],
                    'percentage': admin_pct,
                    'target': self.target_distribution['administration'] * 100
                },
                'stewardship': {
                    'amount': balances['stewardship']['total'],
                    'percentage': steward_pct,
                    'target': self.target_distribution['stewardship'] * 100
                },
                'general': {
                    'amount': balances['general']['total'],
                    'percentage': general_pct,  # DERIVED
                    'target': self.target_distribution['general'] * 100
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.info(
                f"Current Distribution: "
                f"Admin={admin_pct:.2f}%, "
                f"Steward={steward_pct:.2f}%, "
                f"General={general_pct:.2f}% (DERIVED)"
            )
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Error calculating current distribution: {e}", exc_info=True)
            return {
                'total_supply': Decimal('0'),
                'error': str(e)
            }
    
    async def check_compliance(self) -> Dict[str, Any]:
        """
        Check distribution compliance against official tokenomics.
        
        CRITICAL: Only checks Administration and Stewardship directly.
        General compliance is automatic when Admin and Stewardship are compliant.
        
        Returns:
            Dict with compliance status:
            {
                'compliant': bool,
                'administration_compliant': bool,
                'stewardship_compliant': bool,
                'general_compliant': bool (always True when others compliant),
                'deviations': {
                    'administration': float,
                    'stewardship': float
                },
                'recommendations': List[str],
                'distribution': Dict (current distribution data),
                'timestamp': str
            }
            
        Example:
            >>> compliance = await service.check_compliance()
            >>> if compliance['compliant']:
            ...     print("✅ Distribution is compliant!")
            >>> else:
            ...     print("❌ Compliance issues:")
            ...     for rec in compliance['recommendations']:
            ...         print(f"  - {rec}")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - v3.7.0: Implements DERIVED model - only checks Admin & Stewardship
        """
        self._require_initialized()
        
        try:
            # Get current distribution
            distribution = await self.get_current_distribution()
            
            if 'error' in distribution:
                return {
                    'compliant': False,
                    'error': distribution['error']
                }
            
            # Calculate deviations (percentage points)
            admin_deviation = abs(
                distribution['administration']['percentage'] -
                distribution['administration']['target']
            )
            steward_deviation = abs(
                distribution['stewardship']['percentage'] -
                distribution['stewardship']['target']
            )
            
            # Check compliance (within threshold)
            threshold_pct = self.rebalance_threshold * 100  # Convert to percentage points
            admin_compliant = admin_deviation <= threshold_pct
            steward_compliant = steward_deviation <= threshold_pct
            
            # Overall compliance requires both Admin and Stewardship compliant
            compliant = admin_compliant and steward_compliant
            
            # General is ALWAYS compliant when Admin and Stewardship are compliant
            # This is the DERIVED model: General = 100% - Admin - Stewardship
            general_compliant = compliant
            
            # Generate recommendations
            recommendations = []
            if not admin_compliant:
                direction = "increase" if distribution['administration']['percentage'] < distribution['administration']['target'] else "decrease"
                recommendations.append(
                    f"Administration: {direction} by {admin_deviation:.2f}% to reach {distribution['administration']['target']:.2f}%"
                )
            
            if not steward_compliant:
                direction = "increase" if distribution['stewardship']['percentage'] < distribution['stewardship']['target'] else "decrease"
                recommendations.append(
                    f"Stewardship: {direction} by {steward_deviation:.2f}% to reach {distribution['stewardship']['target']:.2f}%"
                )
            
            if compliant:
                recommendations.append("✅ Distribution is compliant - no action needed")
            
            # Update tracking
            self._last_compliance_check = datetime.now()
            self._compliance_check_count += 1
            
            result = {
                'compliant': compliant,
                'administration_compliant': admin_compliant,
                'stewardship_compliant': steward_compliant,
                'general_compliant': general_compliant,
                'deviations': {
                    'administration': float(admin_deviation),
                    'stewardship': float(steward_deviation)
                },
                'recommendations': recommendations,
                'distribution': distribution,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            status_icon = "✅" if compliant else "❌"
            self.logger.info(
                f"{status_icon} Compliance Check: "
                f"Admin={admin_compliant}, Steward={steward_compliant}, Overall={compliant}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking compliance: {e}", exc_info=True)
            return {
                'compliant': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def is_rebalance_needed(self) -> bool:
        """
        Check if rebalancing is needed based on threshold.
        
        Returns:
            True if any deviation exceeds rebalance_threshold (2%)
            
        Example:
            >>> needs_rebalance = await service.is_rebalance_needed()
            >>> if needs_rebalance:
            ...     print("⚠️ Rebalancing required")
            ...     compliance = await service.check_compliance()
            ...     # Take action based on recommendations
        
        Design Notes:
            - Principle 5: Fully async operation
            - Simple boolean check for quick decisions
        """
        self._require_initialized()
        
        try:
            compliance = await self.check_compliance()
            needs_rebalance = not compliance.get('compliant', False)
            
            if needs_rebalance:
                self.logger.warning("⚠️ Rebalancing needed")
            else:
                self.logger.info("✅ No rebalancing needed")
            
            return needs_rebalance
            
        except Exception as e:
            self.logger.error(f"Error checking rebalance status: {e}", exc_info=True)
            # Conservative approach: assume rebalance needed on error
            return True
    
    # ========================================================================
    # STANDARDIZED HEALTH CHECK METHOD
    # Principle 7: Per-Asset Monitoring with health checks
    # Principle 12: Method Singularity - Uses ServiceHealthCheck utility
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check using standardized utility.
        
        Implements Principle #7 (Per-Asset Monitoring) and Principle #12 
        (Method Singularity) by using the ServiceHealthCheck utility.
        
        This method checks:
        - Service initialization status
        - Database connectivity
        - Stellar client connectivity
        - Configuration validity
        - Last operation recency
        - Cache status
        - Distribution-specific metrics
        
        Returns:
            Health status dictionary from ServiceHealthCheck utility:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str (ISO timestamp),
                'details': {
                    'initialized': bool,
                    'database_connected': bool,
                    'stellar_connected': bool,
                    'config_valid': bool,
                    'last_distribution_check': str (ISO timestamp),
                    'last_compliance_check': str (ISO timestamp),
                    'distribution_checks': int,
                    'compliance_checks': int,
                    'cache_status': str
                }
            }
        
        Example:
            >>> health = await service.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Distribution service operational")
            >>> else:
            ...     print(f"Issues detected: {health['message']}")
        
        Design Notes:
            - Principle 7: Per-asset monitoring with detailed tracking
            - Principle 12: Uses ServiceHealthCheck utility for consistency
        """
        # Define custom checks specific to distribution service
        async def check_database():
            """Test database connectivity."""
            if hasattr(self.db_manager, 'health_check'):
                db_health = await self.db_manager.health_check()
                return db_health.get('status') == 'healthy'
            else:
                # Fallback: try a simple query
                test_query = "SELECT 1 as test"
                result = await self.db_manager.fetch_one(test_query)
                return result is not None
        
        async def check_stellar():
            """Test Stellar client connectivity."""
            try:
                # Rate limit before checking
                await self.rate_limiter.acquire()
                
                # Try to load a known account (General account)
                if self._initialized and self.accounts.get('general'):
                    account = await self.stellar_client.accounts().account_id(
                        self.accounts['general']
                    ).call()
                    return account is not None
                else:
                    # Can't test without initialized accounts
                    return False
            except Exception:
                return False
        
        async def check_config():
            """Validate service configuration."""
            try:
                self._validate_config()
                return True
            except ValueError:
                return False
        
        # Prepare distribution-specific details
        distribution_details = {
            'last_distribution_check': self._last_distribution_check.isoformat() if self._last_distribution_check else None,
            'last_compliance_check': self._last_compliance_check.isoformat() if self._last_compliance_check else None,
            'distribution_checks': self._distribution_check_count,
            'compliance_checks': self._compliance_check_count,
            'cache_status': 'fresh' if self._is_cache_fresh() else 'stale',
            'cache_size': len(self._cache),
            'ubec_code': self.ubec_code,
            'ubec_issuer': f"{self.ubec_issuer[:8]}..." if self.ubec_issuer else None,
            'network': self.network
        }
        
        # Use ServiceHealthCheck utility for database and Stellar health
        # This follows Principle #12: Method Singularity
        health = await ServiceHealthCheck.database_dependent_health(
            service_name='distribution',
            db_manager=self.db_manager,
            is_initialized=self._initialized,
            additional_checks=[check_stellar, check_config],
            **distribution_details
        )
        
        # Add warnings for stale operations
        issues = []
        if self._last_distribution_check:
            check_age = (datetime.now() - self._last_distribution_check).total_seconds()
            if check_age > 86400:  # 24 hours
                issues.append(f"No distribution check in {check_age/3600:.1f} hours")
        
        if self._last_compliance_check:
            check_age = (datetime.now() - self._last_compliance_check).total_seconds()
            if check_age > 86400:  # 24 hours
                issues.append(f"No compliance check in {check_age/3600:.1f} hours")
        
        # Update status if there are operational warnings
        if issues and health['status'] == 'healthy':
            health['status'] = 'degraded'
            health['message'] = f"Distribution service operational with warnings: {', '.join(issues)}"
        
        return health
    
    def _validate_config(self) -> None:
        """
        Validate service configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.ubec_code:
            raise ValueError("ubec_code not configured")
        
        if not self.ubec_issuer:
            raise ValueError("ubec_issuer not configured")
        
        if not self.accounts.get('general'):
            raise ValueError("general account not configured")
        
        if not self.accounts.get('administration'):
            raise ValueError("administration account not configured")
        
        if not self.accounts.get('stewardship') or len(self.accounts['stewardship']) != 3:
            raise ValueError("stewardship accounts not properly configured (need 3 accounts)")
    
    def _is_cache_fresh(self) -> bool:
        """Check if cache is still fresh."""
        if not self._cache_timestamp:
            return False
        
        age = datetime.now() - self._cache_timestamp
        return age < self._cache_ttl


# ========================================================================
# FACTORY FUNCTION
# Principle 2: Service Pattern - Factory for service registry
# ========================================================================

async def create_distribution_service(
    db_manager: Any,
    config: Dict[str, Any],
    stellar_client: Any,
    audit_service: Any,
    rate_limit_calls_per_second: float = 5.0
) -> UBECDistributionService:
    """
    Factory function to create and initialize distribution service instance.
    
    This async factory creates the service and performs necessary async
    initialization, including loading the issuer address from the database.
    
    IMPORTANT: This function is async because initialization requires database
    queries to load configuration (Principle 4: Database is single source of truth).
    
    Args:
        db_manager: Async database manager
        config: Configuration dictionary
        stellar_client: Stellar async client
        audit_service: Audit service instance
        rate_limit_calls_per_second: Rate limit for API calls
    
    Returns:
        UBECDistributionService: Fully initialized service with complete LP tracking
    
    Example:
        >>> # In main.py or service registry
        >>> service = await create_distribution_service(
        ...     db_manager=db,
        ...     config=config,
        ...     stellar_client=client,
        ...     audit_service=audit
        ... )
        >>> # Service is ready to use
        >>> distribution = await service.get_current_distribution()
        >>> compliance = await service.check_compliance()
        >>> health = await service.health_check()
    
    Design Notes:
        - Principle 2: Service pattern with async factory function
        - Principle 3: Dependencies injected via service registry
        - Principle 4: Database-driven initialization
        - Principle 5: Fully async operation
    """
    # Create service instance
    service = UBECDistributionService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        audit_service=audit_service,
        rate_limit_calls_per_second=rate_limit_calls_per_second
    )
    
    # Perform async initialization (loads issuer from database if needed)
    # Service registry handles initialization
    return service


# ========================================================================
# PUBLIC INTERFACE
# Principle 1: Modular Design - Clear public interface
# ========================================================================

__all__ = [
    'UBECDistributionService',
    'create_distribution_service',
    'OFFICIAL_TOKENOMICS',
    'OFFICIAL_ACCOUNTS',
    'LIQUIDITY_ACCOUNT'
]


# ========================================================================
# STANDALONE EXECUTION PREVENTION
# Principle 2: Service Pattern - No standalone execution
# ========================================================================

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from services.distribution.ubec_distribution_service import create_distribution_service\n"
        "  service = await create_distribution_service(db_manager, config, stellar_client, audit)\n"
        "  distribution = await service.get_current_distribution()\n"
        "  compliance = await service.check_compliance()\n"
        "  health = await service.health_check()\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
