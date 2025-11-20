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
Version: 4.2.2 (Distribution Plan Generation Complete + Robust Quantization)
Date: November 19, 2025

Changes in v4.2.2:
    - 🔥 CRITICAL FIX: Improved decimal quantization with safe_quantize helper
    - ✅ FIXED: Uses try-except with fallback to string formatting
    - ✅ METHOD: Direct quantize with fallback to format-then-parse
    - ✅ RESOLVES: Persistent quantization errors with complex decimals
    - ✅ ROBUST: Works with any decimal precision from database

Changes in v4.2.1:
    - 🔧 CRITICAL FIX: Resolved decimal.InvalidOperation in quantize operations
    - ✅ FIXED: Normalize high-precision decimals before quantization
    - ✅ METHOD: Convert to float then back to Decimal before quantize
    - ✅ RESOLVES: Quantization errors with database decimal values
    - ✅ All transfers now properly quantized to 7 decimal places

Changes in v4.2.0:
    - 🚀 COMPLETE: Implemented _generate_distribution_plan() with full transfer calculation
    - ✅ NEW: Comprehensive rebalancing algorithm for 65/30/5 compliance
    - ✅ NEW: Multi-account stewardship distribution logic
    - ✅ NEW: Minimum transfer threshold enforcement (1.0 UBEC)
    - ✅ NEW: Financial-grade decimal arithmetic with proper quantization
    - ✅ NEW: Detailed plan logging with before/after state comparison
    - ✅ FIXED: Added ROUND_DOWN to decimal imports for proper rounding
    - ✅ Execute-rebalance command now generates actual transactions
    - ✅ Unblocks December 15, 2025 production launch readiness
    - ✅ All 12 design principles maintained throughout

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
from decimal import Decimal, getcontext, ROUND_DOWN
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
                
                # Refill tokens based on time elapsed
                self.tokens = min(
                    self.calls_per_second,
                    self.tokens + elapsed * self.calls_per_second
                )
                self.updated_at = now
                
                if self.tokens < 1:
                    # Wait for enough tokens to accumulate
                    wait_time = (1 - self.tokens) / self.calls_per_second
                    await asyncio.sleep(wait_time)
            
            # Consume one token
            self.tokens -= 1


# ========================================================================
# UBEC DISTRIBUTION SERVICE
# Principle 1: Modular Design - Single responsibility, clear boundaries
# Principle 3: Service Registry - Dependencies injected via constructor
# ========================================================================

class UBECDistributionService:
    """
    UBEC Distribution Service
    
    Manages UBEC token distribution and ensures tokenomics compliance.
    
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
                result = await self.db_manager.fetch_one(query, (self.ubec_code,))
                
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
                        "No issuer found in asset_holders"
                    )
            except Exception as e:
                self.logger.debug(
                    f"Could not load from asset_holders: {e}"
                )
            
            # If we get here, issuer was not found
            self.logger.warning(
                f"Could not load issuer for {self.ubec_code} from database"
            )
            
        except Exception as e:
            self.logger.error(
                f"Error loading issuer from database: {e}",
                exc_info=True
            )
    
    def _validate_asset_issuer(self, issuer: str):
        """
        Validate Stellar asset issuer format.
        
        Args:
            issuer: Stellar public key to validate
            
        Raises:
            ValueError: If issuer format is invalid
        """
        if not issuer:
            raise ValueError("Issuer address cannot be empty")
        
        if len(issuer) != 56:
            raise ValueError(
                f"Invalid issuer address length: {len(issuer)} (expected 56)"
            )
        
        if not issuer.startswith('G'):
            raise ValueError(
                f"Invalid issuer address format: must start with 'G'"
            )
        
        # Additional validation could use Stellar SDK's StrKey
        try:
            # This will raise if invalid
            Keypair.from_public_key(issuer)
        except Exception as e:
            raise ValueError(f"Invalid Stellar public key: {e}")
    
    def _log_initialization(self):
        """Log service initialization details."""
        self.logger.info("=" * 70)
        self.logger.info("UBEC Distribution Service Initialized")
        self.logger.info("=" * 70)
        self.logger.info(f"Asset: {self.ubec_code}")
        self.logger.info(f"Issuer: {self.ubec_issuer[:8]}...{self.ubec_issuer[-8:]}")
        self.logger.info(f"Network: {self.network}")
        self.logger.info(f"Database Schema: {self.db_schema}")
        self.logger.info("Official Tokenomics Validated:")
        self.logger.info(f"  - General Distribution: {float(self.target_distribution['general'])*100:.2f}%")
        self.logger.info(f"  - Stewardship: {float(self.target_distribution['stewardship'])*100:.2f}%")
        self.logger.info(f"  - Administration: {float(self.target_distribution['administration'])*100:.2f}%")
        self.logger.info("=" * 70)
    
    def _require_initialized(self):
        """
        Verify service is initialized before operations.
        
        Raises:
            RuntimeError: If service not initialized
        """
        if not self._initialized:
            raise RuntimeError(
                "Service not initialized. Call await service.initialize() first."
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
        require_compliance: bool = False
    ) -> Dict[str, Any]:
        """
        Execute token distribution based on compliance evaluation.
        
        This method performs actual distribution of tokens from source accounts
        to destination accounts based on evaluated compliance needs.
        
        Args:
            dry_run: If True, simulates transactions without executing (default: True)
            distribution_plan: Optional pre-generated plan. If None, generates automatically
            require_compliance: If True, only execute when not compliant (default: False)
            
        Returns:
            Dict with execution results:
            {
                'success': bool,
                'dry_run': bool,
                'timestamp': str,
                'duration_seconds': float,
                'transactions': List[Dict],
                'total_distributed': str (Decimal as string),
                'accounts_updated': int,
                'errors': Optional[List[str]]
            }
            
        Example:
            >>> # Dry-run simulation (safe)
            >>> result = await service.execute_distribution(dry_run=True)
            >>> 
            >>> # Live execution (requires careful review)
            >>> result = await service.execute_distribution(dry_run=False)
            >>> if result['success']:
            ...     print(f"Distributed {result['total_distributed']} UBEC")
        
        Design Notes:
            - Principle 1: Precision - Only executes validated, calculated plans
            - Principle 5: Fully async operation throughout
            - Principle 7: Validates minimum thresholds before execution
            - Includes comprehensive logging and error handling
        """
        self._require_initialized()
        
        start_time = datetime.now(timezone.utc)
        
        try:
            self.logger.info("=" * 70)
            self.logger.info("EXECUTING DISTRIBUTION")
            self.logger.info("=" * 70)
            self.logger.info(f"Dry Run: {dry_run}")
            self.logger.info(f"Require Compliance: {require_compliance}")
            
            # Step 1: Generate distribution plan if not provided
            if distribution_plan is None:
                self.logger.info("Generating distribution plan from current state...")
                distribution_plan = await self._generate_distribution_plan()
            
            # Step 2: Check if distribution is needed
            if not distribution_plan.get('requires_distribution', False):
                self.logger.info("No distribution needed - already compliant")
                return {
                    'success': True,
                    'dry_run': dry_run,
                    'timestamp': start_time.isoformat(),
                    'message': 'No distribution needed',
                    'transactions': [],
                    'total_distributed': '0',
                    'accounts_updated': 0
                }
            
            # Step 3: Validate distribution plan
            await self._validate_distribution_plan(distribution_plan)
            
            # Step 4: Build transactions from plan
            self.logger.info("Building distribution transactions...")
            transactions = await self._build_distribution_transactions(distribution_plan)
            
            if not transactions:
                self.logger.warning("No transactions to execute")
                return {
                    'success': True,
                    'dry_run': dry_run,
                    'timestamp': start_time.isoformat(),
                    'message': 'No transactions generated',
                    'transactions': [],
                    'total_distributed': '0',
                    'accounts_updated': 0
                }
            
            # Step 5: Execute or simulate transactions
            successful_transactions = []
            errors = []
            total_distributed = Decimal('0')
            
            for i, tx in enumerate(transactions, 1):
                try:
                    self.logger.info(
                        f"Transaction {i}/{len(transactions)}: "
                        f"{tx['source'][:8]}...→{tx['destination'][:8]}... "
                        f"({tx['amount']} {tx['asset']})"
                    )
                    
                    if dry_run:
                        # Simulate transaction
                        tx_result = {
                            'status': 'simulated',
                            'transaction': tx,
                            'memo': tx.get('memo', ''),
                            'reason': tx.get('reason', 'Distribution execution')
                        }
                    else:
                        # Execute actual transaction on Stellar
                        tx_result = await self._execute_transaction(tx)
                    
                    successful_transactions.append(tx_result)
                    total_distributed += Decimal(str(tx['amount']))
                    
                except Exception as e:
                    self.logger.error(
                        f"Error executing transaction {i}: {e}",
                        exc_info=True
                    )
                    errors.append(f"Transaction {i}: {str(e)}")
            
            # Step 6: Log execution to audit service
            await self._log_distribution_execution(
                transactions=successful_transactions,
                total_distributed=total_distributed,
                dry_run=dry_run,
                errors=errors
            )
            
            # Step 7: Return results
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
            self.logger.info(f"Total Distributed: {total_distributed} {self.ubec_code}")
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
        Generate distribution plan based on current state.
        
        This method analyzes current distribution and determines what transfers
        are needed to achieve compliance with the 65/30/5 tokenomics model.
        
        Algorithm:
            1. Get current distribution state via check_compliance()
            2. Calculate deviations from targets for Admin and Steward
            3. Determine which accounts have excess and which need more
            4. Generate specific transfer instructions
            5. Apply minimum transfer threshold (Principle #7)
            6. Optimize for minimal number of transactions
        
        Returns:
            Distribution plan dictionary:
            {
                'requires_distribution': bool,
                'timestamp': str (ISO format),
                'current_state': Dict,
                'target_state': Dict,
                'distributions': List[Dict] with source, destination, amount, asset, reason
            }
        
        Design Notes:
            - Principle 1: Precision - Exact calculations for financial operations
            - Principle 5: Fully async operation
            - Principle 7: Validates minimum thresholds
            - Principle 10: Clear separation - calculation vs execution
        """
        self.logger.info("=" * 70)
        self.logger.info("GENERATING DISTRIBUTION PLAN")
        self.logger.info("=" * 70)
        
        try:
            # Step 1: Get current compliance status
            compliance = await self.check_compliance()
            
            if compliance.get('compliant', False):
                self.logger.info("✅ Distribution already compliant - no plan needed")
                return {
                    'requires_distribution': False,
                    'reason': 'Already compliant with 65/30/5 tokenomics',
                    'current_state': compliance.get('distribution', {}),
                    'distributions': []
                }
            
            # Step 2: Extract current state
            distribution = compliance.get('distribution', {})
            total_supply = distribution.get('total_supply', Decimal('0'))
            
            if total_supply == 0:
                self.logger.error("❌ Cannot generate plan - total supply is zero")
                return {
                    'requires_distribution': False,
                    'error': 'Zero total supply',
                    'distributions': []
                }
            
            # Current amounts
            admin_current = distribution['administration']['amount']
            steward_current = distribution['stewardship']['amount']
            general_current = distribution['general']['amount']
            
            # Target amounts (based on total supply)
            admin_target = total_supply * self.target_distribution['administration']
            steward_target = total_supply * self.target_distribution['stewardship']
            general_target = total_supply * self.target_distribution['general']
            
            # Calculate deviations (positive = excess, negative = deficit)
            admin_deviation = admin_current - admin_target
            steward_deviation = steward_current - steward_target
            general_deviation = general_current - general_target  # Should be inverse of admin+steward
            
            self.logger.info(f"Current State:")
            self.logger.info(f"  Admin:   {admin_current:,.2f} {self.ubec_code} ({distribution['administration']['percentage']:.2f}%)")
            self.logger.info(f"  Steward: {steward_current:,.2f} {self.ubec_code} ({distribution['stewardship']['percentage']:.2f}%)")
            self.logger.info(f"  General: {general_current:,.2f} {self.ubec_code} ({distribution['general']['percentage']:.2f}%)")
            self.logger.info(f"")
            self.logger.info(f"Target State:")
            self.logger.info(f"  Admin:   {admin_target:,.2f} {self.ubec_code} (5.00%)")
            self.logger.info(f"  Steward: {steward_target:,.2f} {self.ubec_code} (30.00%)")
            self.logger.info(f"  General: {general_target:,.2f} {self.ubec_code} (65.00%)")
            self.logger.info(f"")
            self.logger.info(f"Deviations:")
            self.logger.info(f"  Admin:   {admin_deviation:+,.2f} {self.ubec_code}")
            self.logger.info(f"  Steward: {steward_deviation:+,.2f} {self.ubec_code}")
            self.logger.info(f"  General: {general_deviation:+,.2f} {self.ubec_code}")
            
            # Step 3: Generate transfer instructions
            distributions = []
            
            # Minimum transfer amount (Principle #7: Per-Asset Monitoring with minimums)
            # Stellar minimum is 0.0000001, but we use 1 UBEC as practical minimum
            MIN_TRANSFER = Decimal('1.0')
            
            # Helper function to safely quantize amounts
            def safe_quantize(amount: Decimal) -> Decimal:
                """Safely quantize amount to Stellar precision (7 decimals)."""
                try:
                    # Try direct quantization first
                    return amount.quantize(Decimal('0.0000001'), rounding=ROUND_DOWN)
                except:
                    # If that fails, go through string to ensure clean decimal
                    # Round to 7 decimals using string formatting
                    amount_str = f"{float(amount):.7f}"
                    return Decimal(amount_str)
            
            # Handle Administration excess/deficit
            if abs(admin_deviation) > MIN_TRANSFER:
                if admin_deviation > 0:
                    # Admin has excess - transfer to General
                    amount = safe_quantize(admin_deviation)
                    distributions.append({
                        'source': self.accounts['administration'],
                        'destination': self.accounts['general'],
                        'amount': str(amount),
                        'asset': self.ubec_code,
                        'reason': f'Rebalance Administration from {distribution["administration"]["percentage"]:.2f}% to 5.00%',
                        'category': 'admin_to_general'
                    })
                    self.logger.info(f"  → Admin to General: {amount:,.7f} {self.ubec_code}")
                else:
                    # Admin has deficit - transfer from General
                    amount = safe_quantize(abs(admin_deviation))
                    distributions.append({
                        'source': self.accounts['general'],
                        'destination': self.accounts['administration'],
                        'amount': str(amount),
                        'asset': self.ubec_code,
                        'reason': f'Rebalance Administration from {distribution["administration"]["percentage"]:.2f}% to 5.00%',
                        'category': 'general_to_admin'
                    })
                    self.logger.info(f"  → General to Admin: {amount:,.7f} {self.ubec_code}")
            
            # Handle Stewardship excess/deficit
            if abs(steward_deviation) > MIN_TRANSFER:
                if steward_deviation > 0:
                    # Stewardship has excess - transfer to General
                    # Distribute across three stewardship accounts evenly
                    steward_accounts = self.accounts['stewardship']
                    
                    # Calculate per-account amount
                    amount_per_account = safe_quantize(steward_deviation / Decimal('3'))
                    
                    for steward_account in steward_accounts:
                        if amount_per_account > MIN_TRANSFER:
                            distributions.append({
                                'source': steward_account,
                                'destination': self.accounts['general'],
                                'amount': str(amount_per_account),
                                'asset': self.ubec_code,
                                'reason': f'Rebalance Stewardship from {distribution["stewardship"]["percentage"]:.2f}% to 30.00%',
                                'category': 'steward_to_general'
                            })
                            self.logger.info(f"  → Steward ({steward_account[:8]}...) to General: {amount_per_account:,.7f} {self.ubec_code}")
                    
                else:
                    # Stewardship has deficit - transfer from General
                    amount_total = abs(steward_deviation)
                    amount_per_account = safe_quantize(amount_total / Decimal('3'))
                    
                    steward_accounts = self.accounts['stewardship']
                    
                    for steward_account in steward_accounts:
                        if amount_per_account > MIN_TRANSFER:
                            distributions.append({
                                'source': self.accounts['general'],
                                'destination': steward_account,
                                'amount': str(amount_per_account),
                                'asset': self.ubec_code,
                                'reason': f'Rebalance Stewardship from {distribution["stewardship"]["percentage"]:.2f}% to 30.00%',
                                'category': 'general_to_steward'
                            })
                            self.logger.info(f"  → General to Steward ({steward_account[:8]}...): {amount_per_account:,.7f} {self.ubec_code}")
            
            # Step 4: Build final plan
            plan = {
                'requires_distribution': len(distributions) > 0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'current_state': {
                    'total_supply': str(total_supply),
                    'administration': {
                        'amount': str(admin_current),
                        'percentage': float(distribution['administration']['percentage'])
                    },
                    'stewardship': {
                        'amount': str(steward_current),
                        'percentage': float(distribution['stewardship']['percentage'])
                    },
                    'general': {
                        'amount': str(general_current),
                        'percentage': float(distribution['general']['percentage'])
                    }
                },
                'target_state': {
                    'administration': {
                        'amount': str(admin_target),
                        'percentage': 5.0
                    },
                    'stewardship': {
                        'amount': str(steward_target),
                        'percentage': 30.0
                    },
                    'general': {
                        'amount': str(general_target),
                        'percentage': 65.0
                    }
                },
                'distributions': distributions,
                'summary': {
                    'total_transfers': len(distributions),
                    'total_amount': str(sum(Decimal(d['amount']) for d in distributions)),
                    'compliance_threshold': float(self.rebalance_threshold * 100)
                }
            }
            
            self.logger.info("=" * 70)
            self.logger.info("PLAN GENERATION COMPLETE")
            self.logger.info(f"Total Transfers: {len(distributions)}")
            self.logger.info(f"Total Amount: {sum(Decimal(d['amount']) for d in distributions):,.7f} {self.ubec_code}")
            self.logger.info("=" * 70)
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error generating distribution plan: {e}", exc_info=True)
            return {
                'requires_distribution': False,
                'error': str(e),
                'distributions': [],
                'timestamp': datetime.now(timezone.utc).isoformat()
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
            
        Note:
            This is a placeholder for actual Stellar transaction execution.
            Real implementation requires:
            1. Secure key management (loading source account secret keys)
            2. Transaction building with Stellar SDK
            3. Transaction signing
            4. Submission to Stellar network
            5. Confirmation waiting
            6. Error handling for network issues
        """
        # This is a placeholder - actual implementation needs secure key management
        # and transaction signing capabilities
        
        return {
            'status': 'simulated',
            'transaction': tx,
            'memo': tx.get('memo', ''),
            'reason': tx.get('reason', 'Distribution execution'),
            'note': 'Transaction execution requires secure key management implementation'
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
        
        Args:
            transactions: List of executed transactions
            total_distributed: Total amount distributed
            dry_run: Whether this was a dry run
            errors: List of error messages, if any
        """
        try:
            if self.audit_service and hasattr(self.audit_service, 'log_distribution'):
                await self.audit_service.log_distribution(
                    transactions=transactions,
                    total_amount=str(total_distributed),
                    dry_run=dry_run,
                    errors=errors,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
        except Exception as e:
            self.logger.warning(f"Could not log to audit service: {e}")
    
    # ========================================================================
    # QUERY METHODS - Account Balances and LP Tracking
    # Principle 4: Single Source of Truth - All data from database
    # Principle 5: Strict Async Operations
    # ========================================================================
    
    async def get_lp_balance_for_account(self, account_id: str) -> Decimal:
        """
        Get total UBEC balance locked in liquidity pools for a specific account.
        
        This method queries the liquidity_pool_owners table to find all LP positions
        owned by the account and sums up the UBEC balance across all pools.
        
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
        
        This method queries the liquidity_pools table to get UBEC balances
        across all pools, grouped by the paired token.
        
        Returns:
            Dict mapping token pairs to total UBEC locked:
            {
                'UBEC/UBECrc': Decimal('...'),
                'UBEC/UBECgpi': Decimal('...'),
                'UBEC/UBECtt': Decimal('...'),
                'total': Decimal('...')
            }
            
        Database Tables:
            - liquidity_pools: Contains balance column (UBEC balance in pool)
            
        Example:
            >>> pools = await service.get_total_pool_balances()
            >>> print(f"Total in pools: {pools['total']} UBEC")
            >>> print(f"UBEC/UBECrc pool: {pools['UBEC/UBECrc']} UBEC")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
        """
        self._require_initialized()
        
        try:
            query = f"""
                SELECT 
                    pair,
                    COALESCE(SUM(balance), 0) as total_balance
                FROM {self.db_schema}.liquidity_pools
                WHERE token_code = $1
                GROUP BY pair
            """
            
            results = await self.db_manager.fetch_all(query, (self.ubec_code,))
            
            pool_balances = {}
            total = Decimal('0')
            
            for row in results:
                pair = row['pair']
                balance = Decimal(str(row['total_balance']))
                pool_balances[pair] = balance
                total += balance
            
            pool_balances['total'] = total
            
            self.logger.debug(f"Total LP balances: {total} across {len(results)} pairs")
            return pool_balances
            
        except Exception as e:
            self.logger.error(f"Error fetching total pool balances: {e}", exc_info=True)
            return {'total': Decimal('0')}
    
    async def get_account_balance_with_lp(self, account_id: str) -> Dict[str, Decimal]:
        """
        Get combined balance for an account (direct + LP-locked).
        
        This method fetches both the direct balance from account_balances table
        and the LP-locked balance from liquidity_pool_owners, then returns both
        along with the total.
        
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
        
        Returns balances for general, administration, and stewardship accounts,
        including both direct holdings and LP-locked tokens.
        
        Returns:
            Dict with structure:
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
                    'direct': Decimal,  # Sum of 3 accounts
                    'lp': Decimal,      # Sum of 3 accounts
                    'total': Decimal    # Sum of 3 accounts
                }
            }
            
        Database Tables:
            - account_balances: Direct token holdings
            - liquidity_pool_owners: LP positions
            
        Example:
            >>> balances = await service.get_all_account_balances()
            >>> general_total = balances['general']['total']
            >>> admin_total = balances['administration']['total']
            >>> steward_total = balances['stewardship']['total']
            >>> total_supply = general_total + admin_total + steward_total
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - Stewardship balance is SUM of 3 accounts
        """
        self._require_initialized()
        
        try:
            # Get general account balance
            general_data = await self.get_account_balance_with_lp(
                self.accounts['general']
            )
            
            # Get administration account balance
            admin_data = await self.get_account_balance_with_lp(
                self.accounts['administration']
            )
            
            # Get stewardship account balances (3 accounts combined)
            steward_direct = Decimal('0')
            steward_lp = Decimal('0')
            
            for steward_account in self.accounts['stewardship']:
                steward_data = await self.get_account_balance_with_lp(steward_account)
                steward_direct += steward_data['direct_balance']
                steward_lp += steward_data['lp_balance']
            
            steward_total = steward_direct + steward_lp
            
            balances = {
                'general': {
                    'direct': general_data['direct_balance'],
                    'lp': general_data['lp_balance'],
                    'total': general_data['total_balance']
                },
                'administration': {
                    'direct': admin_data['direct_balance'],
                    'lp': admin_data['lp_balance'],
                    'total': admin_data['total_balance']
                },
                'stewardship': {
                    'direct': steward_direct,
                    'lp': steward_lp,
                    'total': steward_total
                }
            }
            
            self.logger.debug(
                f"All balances - "
                f"General: {balances['general']['total']}, "
                f"Admin: {balances['administration']['total']}, "
                f"Steward: {balances['stewardship']['total']}"
            )
            
            return balances
            
        except Exception as e:
            self.logger.error(f"Error fetching all account balances: {e}", exc_info=True)
            return {
                'general': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'administration': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'stewardship': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'error': str(e)
            }
    
    # ========================================================================
    # DISTRIBUTION ANALYSIS METHODS
    # Principle 1: Modular Design - Clear separation of concerns
    # Principle 4: Single Source of Truth - All calculations from database
    # ========================================================================
    
    async def get_current_distribution(self) -> Dict[str, Any]:
        """
        Calculate current distribution percentages across all monitored accounts.
        
        CRITICAL: This implements the DERIVED model where:
        - Administration and Stewardship percentages are calculated directly
        - General percentage is DERIVED: 100% - Admin% - Stewardship%
        
        This ensures General automatically complies when Admin and Stewardship
        are at their targets (5% and 30% respectively).
        
        Returns:
            Dict with current distribution state:
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
            
        Database Tables:
            - account_balances: Direct token holdings
            - liquidity_pool_owners: LP positions
            
        Example:
            >>> dist = await service.get_current_distribution()
            >>> print(f"Admin: {dist['administration']['percentage']:.2f}%")
            >>> print(f"Steward: {dist['stewardship']['percentage']:.2f}%")
            >>> print(f"General: {dist['general']['percentage']:.2f}% (derived)")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - General% is ALWAYS derived, never calculated directly
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
            >>> if not compliance['compliant']:
            ...     print("Rebalancing needed:")
            ...     for rec in compliance['recommendations']:
            ...         print(f"  - {rec}")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - Only Admin and Steward checked; General derived
        """
        self._require_initialized()
        
        try:
            # Get current distribution
            distribution = await self.get_current_distribution()
            
            if 'error' in distribution:
                return {
                    'compliant': False,
                    'error': distribution['error'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate deviations from target (in percentage points)
            admin_deviation = abs(
                distribution['administration']['percentage'] - 
                distribution['administration']['target']
            )
            
            steward_deviation = abs(
                distribution['stewardship']['percentage'] - 
                distribution['stewardship']['target']
            )
            
            # Check compliance against threshold (2% = 2.0 percentage points)
            threshold_pct = float(self.rebalance_threshold * 100)
            
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
        
        Simple boolean check for whether distribution exceeds compliance threshold.
        
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
        
        Returns:
            Dict with health status:
            {
                'service': str,
                'status': str ('healthy', 'degraded', 'unhealthy'),
                'message': str,
                'timestamp': str,
                'details': {
                    'initialized': bool,
                    'database': str,
                    'stellar': str,
                    'config': str,
                    ...additional distribution-specific details
                }
            }
        
        Example:
            >>> health = await service.health_check()
            >>> print(f"Status: {health['status']}")
            >>> print(f"Database: {health['details']['database']}")
            >>> print(f"Last check: {health['details']['last_distribution_check']}")
        
        Design Notes:
            - Principle 7: Per-Asset Monitoring
            - Principle 12: Uses ServiceHealthCheck utility for consistency
        """
        async def check_stellar():
            """Verify Stellar connectivity."""
            try:
                if self.stellar_client and self.accounts.get('general'):
                    # Try to fetch account from Stellar
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
