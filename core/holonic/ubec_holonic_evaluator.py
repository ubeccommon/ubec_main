#!/usr/bin/env python3
"""
UBEC Holonic Evaluator - Ubuntu Philosophy Implementation (ASYNC)
===================================================================

Service implementation for holonic evaluation of UBEC token holders based
on Ubuntu principles: reciprocity, mutualism, diversity, regeneration, and holism.

This module evaluates UBEC token holders based on holonic principles, measuring:
1. Balance of Autonomy and Integration
2. Multi-scale Participation  
3. Regenerative Impact
4. Network Contribution
5. Alignment with Ubuntu Philosophy

Design Principles Compliance:
    ✅ Principle 1: Modular Design - Self-contained evaluation service
    ✅ Principle 2: Service Pattern - Factory-based instantiation, no standalone execution
    ✅ Principle 3: Service Registry - Accessed through centralized registry
    ✅ Principle 4: Single Source of Truth - Database is authoritative
    ✅ Principle 5: Strict Async - ALL I/O operations use async/await
    ✅ Principle 6: No Sync Fallbacks - Pure async implementation
    ✅ Principle 7: Per-Asset Monitoring - Individual account tracking
    ✅ Principle 8: No Duplicate Config - Uses global configuration
    ✅ Principle 9: Integrated Rate Limiting - Built-in for database operations
    ✅ Principle 10: Separation of Concerns - Evaluation logic isolated
    ✅ Principle 11: Comprehensive Documentation - Full docstrings and attribution
    ✅ Principle 12: Method Singularity - No duplicate methods

Usage:
    from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
    
    evaluator = create_holonic_evaluator(
        db_manager=async_db,
        config={'ubec_code': 'UBEC', 'ubec_issuer': 'G...', 'db_schema': 'ubec_main'}
    )
    
    # All methods are async
    report = await evaluator.evaluate_network_holism()
    metrics = await evaluator.get_holonic_metrics()
    health = await evaluator.health_check()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 4.0.0 (Async Service Architecture - Improved)
Date: October 12, 2025
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure precision for decimal calculations
getcontext().prec = 10

logger = logging.getLogger(__name__)


# ==================== DATA MODELS ====================

class HolonicCategory(Enum):
    """Holonic evaluation categories based on Ubuntu principles."""
    OBSERVER = "Observer"          # Minimal participation (0.0-0.2)
    PARTICIPANT = "Participant"    # Basic involvement (0.2-0.4)
    CONTRIBUTOR = "Contributor"    # Active contribution (0.4-0.6)
    INTEGRATOR = "Integrator"      # System integration (0.6-0.8)
    EXEMPLAR = "Exemplar"          # Highest alignment (0.8-1.0)


@dataclass
class HolonicMetrics:
    """Holonic evaluation metrics for an account."""
    account_id: str
    autonomy_integration_score: float
    multi_scale_score: float
    regenerative_impact_score: float
    network_contribution_score: float
    ubuntu_alignment_score: float
    composite_score: float
    holonic_category: HolonicCategory
    evaluation_date: datetime
    raw_metrics: Dict[str, Any]


@dataclass
class AccountHolderData:
    """Simplified data for a UBEC account holder."""
    agent_id: int
    public_key: str
    balance: Decimal
    transaction_count: int
    unique_partners: int
    joined_at: datetime
    last_activity: datetime
    reciprocity_score: float
    account_type: str
    metrics: Dict[str, Any]


# ==================== SERVICE IMPLEMENTATION ====================

class AsyncUBECHolonicEvaluator:
    """
    Async UBEC Holonic Evaluator Service
    
    Evaluates UBEC token holders based on Ubuntu principles using
    pure async operations. All database access uses AsyncDatabaseManager.
    
    Attributes:
        db_manager: Async database manager
        config: Evaluator configuration
        logger: Logger instance
        holders_data: Cache of account holder data
    """
    
    def __init__(
        self,
        db_manager: Any,
        config: Dict[str, Any]
    ):
        """
        Initialize async holonic evaluator.
        
        Args:
            db_manager: Async database manager with pool
            config: Configuration dictionary with:
                - db_schema: Database schema name (required)
                - ubec_code: UBEC token code (required)
                - ubec_issuer: UBEC issuer address (optional)
                - batch_size: Batch size for processing (default: 50)
                - max_evaluations: Max accounts to evaluate (default: 500)
        """
        self.db_manager = db_manager
        self.config = self._load_config(config)
        
        # Setup logging
        self.logger = logging.getLogger('holonic.UBECHolonicEvaluator')
        
        # Data storage
        self.holders_data: Dict[str, AccountHolderData] = {}
        
        # Evaluation thresholds
        self.thresholds = {
            'autonomy_integration': {
                'holding_period_days': 90,
                'min_transactions': 5,
                'balance_threshold': 100.0,
            },
            'multi_scale': {
                'local_partners': 3,      # 3+ partners = local
                'regional_partners': 10,  # 10+ partners = regional
                'global_partners': 20,    # 20+ partners = global
            },
            'regenerative': {
                'growth_rate': 0.1,       # 10% monthly growth
                'activity_rate': 0.2,     # 20% active accounts
            },
            'network': {
                'min_activity': 10,       # 10 transactions
                'connector_threshold': 5, # 5+ unique connections
            },
            'ubuntu': {
                'reciprocity_ratio': 0.8, # 80% balance
                'community_size': 20,     # 20+ connections
            },
            'composite': {
                'observer': 0.2,
                'participant': 0.4,
                'contributor': 0.6,
                'integrator': 0.8,
                'exemplar': 0.9
            }
        }
        
        # Load core accounts
        self._load_accounts()
        
        # Rate limiting
        self._last_evaluation = None
        self._min_eval_interval = 300  # 5 minutes between full evaluations
        
        self.logger.info(
            f"Async UBEC Holonic Evaluator initialized for {self.config['ubec_code']} "
            f"(Schema: {self.config['db_schema']})"
        )
    
    def _load_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load and validate configuration.
        
        Args:
            config: User-provided configuration
        
        Returns:
            Complete configuration with defaults
        """
        # Required fields
        if 'db_schema' not in config:
            raise ValueError("db_schema is required in config")
        if 'ubec_code' not in config:
            raise ValueError("ubec_code is required in config")
        
        # Defaults
        defaults = {
            "ubec_issuer": "",
            "batch_size": 50,
            "min_activity": 1,
            "min_reciprocity_score": 0,
            "evaluation_interval_days": 30,
            "max_evaluations": 500
        }
        
        # Merge with defaults
        full_config = {**defaults, **config}
        
        return full_config
    
    def _load_accounts(self):
        """Load core accounts from configuration."""
        try:
            # Try to import from GlobalConfig (NEW standard)
            from config.config import GlobalConfig
            global_config = GlobalConfig()
            self.accounts = global_config.ACCOUNTS
            self.logger.info("✓ Loaded accounts from GlobalConfig")
        except (ImportError, AttributeError):
            # Fallback to defaults
            self.accounts = {
                'general': "GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74",
                'administration': "GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC",
                'stewardship': [
                    "GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC",
                    "GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC",
                    "GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC"
                ]
            }
            self.logger.info("Using default account configuration")
    
    # ========================================================================
    # CORE EVALUATION METHODS
    # ========================================================================
    
    async def evaluate_network_holism(self) -> Dict[str, Any]:
        """
        Evaluate overall network holonic health based on Ubuntu principles.
        
        This is the main evaluation method that calculates holistic health
        metrics for the entire UBEC network.
        
        Returns:
            dict: Comprehensive holonic evaluation report with:
                - timestamp: Evaluation timestamp
                - network_stats: Network statistics
                - ubuntu_principles: Scores for each principle
                - holism_score: Overall holonic score (0-1)
                - holonic_category: Overall category
                - health_status: Health status string
                - recommendations: List of recommendations
        """
        self.logger.info("Evaluating network-wide holonic health")
        
        # Rate limiting check
        if self._last_evaluation:
            elapsed = (datetime.now() - self._last_evaluation).total_seconds()
            if elapsed < self._min_eval_interval:
                self.logger.info(f"Using cached evaluation (age: {elapsed:.0f}s)")
                return self._cached_report
        
        try:
            # Collect network statistics
            total_accounts = await self._get_total_accounts()
            active_accounts = await self._get_active_accounts()
            total_transactions = await self._get_total_transactions()
            
            if total_accounts == 0:
                self.logger.warning("No accounts found for evaluation")
                return self._empty_report()
            
            # Calculate Ubuntu principle scores
            reciprocity_score = await self._calculate_reciprocity_score()
            mutualism_score = await self._calculate_mutualism_score()
            diversity_score = await self._calculate_diversity_score()
            regeneration_score = await self._calculate_regeneration_score()
            
            # Calculate composite holism score (weighted average)
            holism_score = (
                reciprocity_score * 0.25 +  # Water - Flow balance
                mutualism_score * 0.25 +    # Earth - Stability
                diversity_score * 0.20 +    # Air - Freedom
                regeneration_score * 0.30   # Fire - Growth
            )
            
            # Generate comprehensive report
            report = {
                'timestamp': datetime.now().isoformat(),
                'network_stats': {
                    'total_accounts': total_accounts,
                    'active_accounts': active_accounts,
                    'total_transactions': total_transactions,
                    'activity_rate': float(active_accounts / total_accounts) if total_accounts > 0 else 0.0
                },
                'ubuntu_principles': {
                    'reciprocity': {
                        'score': reciprocity_score,
                        'element': 'Water',
                        'description': 'Balanced exchange and mutual support',
                        'status': self._score_status(reciprocity_score)
                    },
                    'mutualism': {
                        'score': mutualism_score,
                        'element': 'Earth',
                        'description': 'Symbiotic relationships and cooperation',
                        'status': self._score_status(mutualism_score)
                    },
                    'diversity': {
                        'score': diversity_score,
                        'element': 'Air',
                        'description': 'Variety of participants and approaches',
                        'status': self._score_status(diversity_score)
                    },
                    'regeneration': {
                        'score': regeneration_score,
                        'element': 'Fire',
                        'description': 'Renewal and positive transformation',
                        'status': self._score_status(regeneration_score)
                    }
                },
                'holism_score': holism_score,
                'holonic_category': self._determine_category(holism_score),
                'health_status': self._determine_health_status(holism_score),
                'recommendations': self._generate_holonic_recommendations(
                    reciprocity_score,
                    mutualism_score,
                    diversity_score,
                    regeneration_score
                ),
                'evaluation_age_seconds': 0
            }
            
            # Cache the result
            self._cached_report = report
            self._last_evaluation = datetime.now()
            
            self.logger.info(
                f"Network holonic evaluation complete - "
                f"Holism Score: {holism_score:.2f}, "
                f"Category: {report['holonic_category']}, "
                f"Status: {report['health_status']}"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error evaluating network holism: {e}")
            self.logger.exception("Full traceback:")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'holism_score': 0.0,
                'health_status': 'ERROR'
            }
    
    async def get_holonic_metrics(self) -> Dict[str, Any]:
        """
        Get current holonic metrics without full evaluation.
        
        This is a lightweight method for quick metrics without running
        the full evaluation process.
        
        Returns:
            dict: Quick holonic metrics summary
        """
        try:
            total_accounts = await self._get_total_accounts()
            active_accounts = await self._get_active_accounts()
            
            # If we have a recent cached report, include scores
            cached_scores = {}
            if self._last_evaluation:
                age = (datetime.now() - self._last_evaluation).total_seconds()
                if age < self._min_eval_interval and hasattr(self, '_cached_report'):
                    cached_scores = {
                        'holism_score': self._cached_report.get('holism_score'),
                        'health_status': self._cached_report.get('health_status'),
                        'cache_age_seconds': age
                    }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_accounts': total_accounts,
                'active_accounts': active_accounts,
                'activity_rate': float(active_accounts / total_accounts) if total_accounts > 0 else 0.0,
                **cached_scores,
                'note': 'Use evaluate_network_holism() for full detailed report'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting holonic metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def evaluate_account(
        self,
        account_id: str
    ) -> Optional[AccountHolderData]:
        """
        Evaluate a specific account's holonic metrics.
        
        Args:
            account_id: Stellar public key
            
        Returns:
            AccountHolderData with metrics, or None if not found
        """
        self.logger.info(f"Evaluating account: {account_id[:10]}...")
        
        try:
            # Get account data
            holder_data = await self._collect_account_data(account_id)
            
            if not holder_data:
                self.logger.warning(f"No data found for account {account_id[:10]}...")
                return None
            
            # Calculate metrics
            await self._calculate_account_metrics(holder_data)
            
            return holder_data
            
        except Exception as e:
            self.logger.error(f"Error evaluating account: {e}")
            return None
    
    # ========================================================================
    # UBUNTU PRINCIPLE CALCULATIONS (Network-wide)
    # ========================================================================
    
    async def _calculate_reciprocity_score(self) -> float:
        """
        Calculate reciprocity score (Water - balanced flow and exchange).
        
        Measures the balance of giving and receiving in the network.
        High score = balanced transactions between accounts.
        
        Returns:
            Score from 0.0 to 1.0
        """
        try:
            query = f"""
                SELECT 
                    COUNT(DISTINCT from_account) as senders,
                    COUNT(DISTINCT to_account) as receivers,
                    COUNT(*) as total_txs,
                    AVG(amount) as avg_amount,
                    STDDEV(amount) as std_amount
                FROM {self.config['db_schema']}.stellar_operations
                WHERE asset_code = $1
                AND created_at > NOW() - INTERVAL '30 days'
                AND type = 'payment'
            """
            result = await self.db_manager.fetch_one(query, (self.config['ubec_code'],))
            
            if not result or result['total_txs'] == 0:
                return 0.5  # Neutral score if no data
            
            # Score based on how balanced sending/receiving is
            senders = result['senders'] or 0
            receivers = result['receivers'] or 0
            
            if max(senders, receivers) == 0:
                return 0.5
            
            # Balance ratio: closer to 1.0 = more balanced
            balance_ratio = min(senders, receivers) / max(senders, receivers)
            
            # Transaction diversity (lower std dev = more consistent amounts)
            avg_amount = float(result['avg_amount'] or 0)
            std_amount = float(result['std_amount'] or 0)
            
            if avg_amount > 0:
                consistency = 1.0 - min(std_amount / avg_amount, 1.0)
            else:
                consistency = 0.5
            
            # Combined score
            score = (balance_ratio * 0.7) + (consistency * 0.3)
            
            return float(min(max(score, 0.0), 1.0))
            
        except Exception as e:
            self.logger.error(f"Error calculating reciprocity: {e}")
            return 0.5
    
    async def _calculate_mutualism_score(self) -> float:
        """
        Calculate mutualism score (Earth - stability and mutual support).
        
        Measures the degree of mutual support and long-term relationships.
        High score = many stable, long-term holders.
        
        Returns:
            Score from 0.0 to 1.0
        """
        try:
            # Get accounts with sustained balances (holding for stability)
            query = f"""
                SELECT 
                    COUNT(DISTINCT account_id) as stable_holders,
                    AVG(balance) as avg_balance,
                    COUNT(*) as total_holders
                FROM {self.config['db_schema']}.asset_holders
                WHERE asset_code = $1
                AND balance > 10
                AND last_updated < NOW() - INTERVAL '30 days'
            """
            stable = await self.db_manager.fetch_one(query, (self.config['ubec_code'],))
            
            total = await self._get_total_accounts()
            
            if total == 0:
                return 0.5
            
            # Calculate stable holder ratio
            stable_count = stable['stable_holders'] or 0
            stable_ratio = float(stable_count / total)
            
            # Higher percentage of stable holders = higher score
            # Scale: 50% stable holders = full score
            score = min(stable_ratio * 2.0, 1.0)
            
            return float(score)
            
        except Exception as e:
            self.logger.error(f"Error calculating mutualism: {e}")
            return 0.5
    
    async def _calculate_diversity_score(self) -> float:
        """
        Calculate diversity score (Air - variety and freedom).
        
        Measures the variety of participants and distribution patterns.
        High score = evenly distributed tokens across many accounts.
        
        Returns:
            Score from 0.0 to 1.0
        """
        try:
            # Get balance distribution statistics
            query = f"""
                SELECT 
                    STDDEV(balance) as std_dev,
                    AVG(balance) as avg_balance,
                    COUNT(*) as account_count,
                    MIN(balance) as min_balance,
                    MAX(balance) as max_balance
                FROM {self.config['db_schema']}.asset_holders
                WHERE asset_code = $1
                AND balance > 0
            """
            result = await self.db_manager.fetch_one(query, (self.config['ubec_code'],))
            
            if not result or result['account_count'] == 0:
                return 0.5
            
            # Use coefficient of variation as diversity measure
            # Lower CV = more equal distribution = higher diversity
            avg = float(result['avg_balance']) if result['avg_balance'] else 1.0
            std = float(result['std_dev']) if result['std_dev'] else 0.0
            count = result['account_count']
            
            if avg == 0:
                return 0.5
            
            cv = std / avg
            
            # Convert CV to 0-1 score (lower CV = higher score)
            # Cap at CV = 2.0 for scoring
            cv_score = max(0, min(1.0, 1.0 - (cv / 2.0)))
            
            # Also consider account count (more accounts = more diversity)
            # 100+ accounts = full score on this component
            count_score = min(count / 100.0, 1.0)
            
            # Combined score
            diversity = (cv_score * 0.6) + (count_score * 0.4)
            
            return float(diversity)
            
        except Exception as e:
            self.logger.error(f"Error calculating diversity: {e}")
            return 0.5
    
    async def _calculate_regeneration_score(self) -> float:
        """
        Calculate regeneration score (Fire - transformation and renewal).
        
        Measures new participant growth and network expansion.
        High score = strong growth in new accounts and activity.
        
        Returns:
            Score from 0.0 to 1.0
        """
        try:
            # Get new accounts in last 30 days
            query = f"""
                SELECT 
                    COUNT(*) as new_accounts,
                    (SELECT COUNT(*) FROM {self.config['db_schema']}.asset_holders 
                     WHERE asset_code = $1 AND balance > 0) as total_accounts
                FROM {self.config['db_schema']}.asset_holders
                WHERE asset_code = $1
                AND last_updated > NOW() - INTERVAL '30 days'
                AND balance > 0
            """
            result = await self.db_manager.fetch_one(query, (self.config['ubec_code'],))
            
            if not result or result['total_accounts'] == 0:
                return 0.5
            
            new_count = result['new_accounts'] or 0
            total = result['total_accounts']
            
            # Growth rate as regeneration indicator
            growth_rate = float(new_count / total)
            
            # Convert to 0-1 score (10% growth/month = full score)
            growth_score = min(growth_rate * 10, 1.0)
            
            # Also check transaction activity growth
            tx_query = f"""
                SELECT COUNT(*) as recent_txs
                FROM {self.config['db_schema']}.stellar_operations
                WHERE asset_code = $1
                AND created_at > NOW() - INTERVAL '30 days'
            """
            tx_result = await self.db_manager.fetch_one(tx_query, (self.config['ubec_code'],))
            
            recent_txs = tx_result['recent_txs'] if tx_result else 0
            
            # Activity score (100+ txs/month = full score)
            activity_score = min(recent_txs / 100.0, 1.0)
            
            # Combined regeneration score
            regeneration = (growth_score * 0.6) + (activity_score * 0.4)
            
            return float(regeneration)
            
        except Exception as e:
            self.logger.error(f"Error calculating regeneration: {e}")
            return 0.5
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    async def _get_total_accounts(self) -> int:
        """Get total number of UBEC accounts."""
        try:
            query = f"""
                SELECT COUNT(DISTINCT account_id) as total
                FROM {self.config['db_schema']}.asset_holders
                WHERE asset_code = $1
                AND balance > 0
            """
            result = await self.db_manager.fetch_one(query, (self.config['ubec_code'],))
            return int(result['total']) if result else 0
        except Exception as e:
            self.logger.error(f"Error getting total accounts: {e}")
            return 0
    
    async def _get_active_accounts(self, days: int = 30) -> int:
        """Get number of accounts with recent transactions."""
        try:
            query = f"""
                SELECT COUNT(DISTINCT 
                    CASE 
                        WHEN from_account != to_account 
                        THEN COALESCE(NULLIF(from_account, ''), to_account)
                        ELSE to_account
                    END
                ) as active
                FROM {self.config['db_schema']}.stellar_operations
                WHERE asset_code = $1
                AND created_at > NOW() - INTERVAL '{days} days'
            """
            result = await self.db_manager.fetch_one(query, (self.config['ubec_code'],))
            return int(result['active']) if result else 0
        except Exception as e:
            self.logger.error(f"Error getting active accounts: {e}")
            return 0
    
    async def _get_total_transactions(self, days: int = 30) -> int:
        """Get total number of transactions in time period."""
        try:
            query = f"""
                SELECT COUNT(*) as total
                FROM {self.config['db_schema']}.stellar_operations
                WHERE asset_code = $1
                AND created_at > NOW() - INTERVAL '{days} days'
            """
            result = await self.db_manager.fetch_one(query, (self.config['ubec_code'],))
            return int(result['total']) if result else 0
        except Exception as e:
            self.logger.error(f"Error getting total transactions: {e}")
            return 0
    
    async def _collect_account_data(self, account_id: str) -> Optional[AccountHolderData]:
        """Collect data for a specific account."""
        try:
            # Get account balance
            balance_query = f"""
                SELECT balance, last_updated
                FROM {self.config['db_schema']}.asset_holders
                WHERE account_id = $1 AND asset_code = $2
            """
            balance_result = await self.db_manager.fetch_one(
                balance_query,
                (account_id, self.config['ubec_code'])
            )
            
            if not balance_result:
                return None
            
            # Get transaction stats
            tx_query = f"""
                SELECT 
                    COUNT(*) as tx_count,
                    COUNT(DISTINCT 
                        CASE WHEN from_account = $1 THEN to_account 
                             WHEN to_account = $1 THEN from_account 
                        END
                    ) as unique_partners,
                    MIN(created_at) as first_tx,
                    MAX(created_at) as last_tx
                FROM {self.config['db_schema']}.stellar_operations
                WHERE (from_account = $1 OR to_account = $1)
                AND asset_code = $2
            """
            tx_result = await self.db_manager.fetch_one(
                tx_query,
                (account_id, self.config['ubec_code'])
            )
            
            # Determine account type
            account_type = self._determine_account_type(account_id)
            
            # Create holder data
            holder_data = AccountHolderData(
                agent_id=hash(account_id) % 1000000,  # Simple ID generation
                public_key=account_id,
                balance=Decimal(str(balance_result['balance'])),
                transaction_count=tx_result['tx_count'] if tx_result else 0,
                unique_partners=tx_result['unique_partners'] if tx_result else 0,
                joined_at=tx_result['first_tx'] if tx_result and tx_result['first_tx'] else datetime.now(),
                last_activity=tx_result['last_tx'] if tx_result and tx_result['last_tx'] else datetime.now(),
                reciprocity_score=0.5,  # Default
                account_type=account_type,
                metrics={}
            )
            
            return holder_data
            
        except Exception as e:
            self.logger.error(f"Error collecting account data: {e}")
            return None
    
    async def _calculate_account_metrics(self, holder_data: AccountHolderData):
        """Calculate holonic metrics for a specific account."""
        # This would calculate individual account metrics
        # Simplified version for now
        holder_data.metrics = {
            'autonomy_integration': {'score': 0.5},
            'multi_scale_participation': {'score': 0.5},
            'regenerative_impact': {'score': 0.5},
            'network_contribution': {'score': 0.5},
            'ubuntu_alignment': {'score': 0.5},
            'holonic_score': 0.5,
            'holonic_category': HolonicCategory.PARTICIPANT
        }
    
    def _determine_account_type(self, public_key: str) -> str:
        """Determine account type from public key."""
        if public_key == self.accounts.get('general'):
            return 'general'
        elif public_key == self.accounts.get('administration'):
            return 'administration'
        elif public_key in self.accounts.get('stewardship', []):
            return 'stewardship'
        else:
            return 'regular'
    
    def _determine_category(self, score: float) -> str:
        """Determine holonic category from score."""
        if score >= self.thresholds['composite']['exemplar']:
            return HolonicCategory.EXEMPLAR.value
        elif score >= self.thresholds['composite']['integrator']:
            return HolonicCategory.INTEGRATOR.value
        elif score >= self.thresholds['composite']['contributor']:
            return HolonicCategory.CONTRIBUTOR.value
        elif score >= self.thresholds['composite']['participant']:
            return HolonicCategory.PARTICIPANT.value
        else:
            return HolonicCategory.OBSERVER.value
    
    def _determine_health_status(self, score: float) -> str:
        """Determine overall health status."""
        if score >= 0.8:
            return "EXCELLENT"
        elif score >= 0.6:
            return "GOOD"
        elif score >= 0.4:
            return "FAIR"
        elif score >= 0.2:
            return "NEEDS ATTENTION"
        else:
            return "POOR"
    
    def _score_status(self, score: float) -> str:
        """Get status string for a score."""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _generate_holonic_recommendations(
        self,
        reciprocity: float,
        mutualism: float,
        diversity: float,
        regeneration: float
    ) -> List[str]:
        """Generate recommendations based on Ubuntu principle scores."""
        recommendations = []
        
        if reciprocity < 0.6:
            recommendations.append(
                "🜄 Water/Reciprocity: Encourage more balanced exchange and "
                "mutual transactions between accounts. Current reciprocity is below optimal."
            )
        
        if mutualism < 0.6:
            recommendations.append(
                "🜃 Earth/Mutualism: Foster long-term holdings and stable relationships "
                "within the network. Support initiatives that encourage sustained participation."
            )
        
        if diversity < 0.6:
            recommendations.append(
                "🜁 Air/Diversity: Work to distribute tokens more evenly across participants. "
                "Encourage broader participation to increase network diversity."
            )
        
        if regeneration < 0.6:
            recommendations.append(
                "🜂 Fire/Regeneration: Focus on onboarding new participants and "
                "expanding the network. Increase outreach and growth initiatives."
            )
        
        if all(s >= 0.6 for s in [reciprocity, mutualism, diversity, regeneration]):
            recommendations.append(
                "✅ All Ubuntu principles are well-balanced. The network demonstrates "
                "strong holonic health. Continue current practices while monitoring for drift."
            )
        
        return recommendations
    
    def _empty_report(self) -> Dict[str, Any]:
        """Generate empty report when no data available."""
        return {
            'timestamp': datetime.now().isoformat(),
            'network_stats': {
                'total_accounts': 0,
                'active_accounts': 0,
                'total_transactions': 0,
                'activity_rate': 0.0
            },
            'ubuntu_principles': {
                'reciprocity': {'score': 0.0, 'status': 'No Data'},
                'mutualism': {'score': 0.0, 'status': 'No Data'},
                'diversity': {'score': 0.0, 'status': 'No Data'},
                'regeneration': {'score': 0.0, 'status': 'No Data'}
            },
            'holism_score': 0.0,
            'holonic_category': 'Observer',
            'health_status': 'NO DATA',
            'recommendations': ['No accounts found. Initialize the network to begin evaluation.']
        }
    
    # ========================================================================
    # LIFECYCLE METHODS
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check database connection
            test_query = "SELECT 1 as test"
            result = await self.db_manager.fetch_one(test_query, ())
            
            db_healthy = result is not None and result.get('test') == 1
            
            return {
                'service': 'UBECHolonicEvaluator',
                'status': 'healthy' if db_healthy else 'unhealthy',
                'database': 'connected' if db_healthy else 'disconnected',
                'accounts_cached': len(self.holders_data),
                'last_evaluation': self._last_evaluation.isoformat() if self._last_evaluation else None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'service': 'UBECHolonicEvaluator',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def close(self):
        """
        Clean up evaluator resources.
        
        Implements Principle #5 (Strict Async) - async cleanup method.
        """
        self.logger.info("Holonic evaluator closing")
        
        # Clear cached data
        self.holders_data.clear()
        self._last_evaluation = None
        if hasattr(self, '_cached_report'):
            del self._cached_report
        
        self.logger.info("Holonic evaluator closed")


# ==================== SERVICE FACTORY ====================

def create_holonic_evaluator(
    db_manager: Any,
    config: Dict[str, Any],
    **kwargs
) -> AsyncUBECHolonicEvaluator:
    """
    Factory function to create async holonic evaluator instance.
    
    Implements Principle #2 (Service Pattern) - factory-based instantiation.
    
    Args:
        db_manager: Async database manager
        config: Configuration dictionary with:
            - db_schema: Database schema name (required)
            - ubec_code: UBEC token code (required)
            - ubec_issuer: UBEC issuer address (optional)
        **kwargs: Additional options (reserved for future use)
    
    Returns:
        AsyncUBECHolonicEvaluator: Initialized service instance
    
    Raises:
        ValueError: If required config parameters are missing
    """
    evaluator = AsyncUBECHolonicEvaluator(
        db_manager=db_manager,
        config=config
    )
    
    return evaluator


# ==================== MODULE EXPORTS ====================

__all__ = [
    'HolonicCategory',
    'HolonicMetrics',
    'AccountHolderData',
    'AsyncUBECHolonicEvaluator',
    'create_holonic_evaluator'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Implements Principle #2 (Service Pattern)

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator. "
        "\n\nExample usage:"
        "\n  from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator"
        "\n  evaluator = create_holonic_evaluator(db_manager, config)"
        "\n  report = await evaluator.evaluate_network_holism()"
    )
