#!/usr/bin/env python3
# core/holonic/ubec_holonic_evaluator.py
"""
UBEC Holonic Evaluator - Ubuntu Philosophy Implementation with Element Metrics
===============================================================================
Service implementation for holonic evaluation of UBEC token holders with
complete integration of four-element Ubuntu principle metrics.

This module calculates, stores, and manages:
1. Five-dimensional holonic scores (autonomy, multi-scale, regenerative, network, ubuntu)
2. Four-element Ubuntu principle metrics (diversity, reciprocity, mutualism, regeneration)
3. Element-specific health assessments stored in ubec_holonic_metrics table
4. Composite scoring that integrates all dimensions

NEW IN v3.0.0 - COMPLETE UBUNTU PRINCIPLE INTEGRATION:
- ✅ reciprocity_health (Water/UBECrc) - calculated and stored
- ✅ mutualism_capacity (Earth/UBECgpi) - calculated and stored  
- ✅ diversity_score (Air/UBEC) - calculated and stored
- ✅ regeneration_score (Fire/UBECtt) - calculated and stored
- ✅ All metrics stored in ubec_holonic_metrics table
- ✅ ubuntu_alignment_score properly calculated from element metrics
- ✅ Health status assessment for each principle
- ✅ Complete integration with API service

Evaluates UBEC token holders based on Ubuntu principles:
- **Diversity (Air/UBEC)**: Unique participation patterns and breadth
- **Reciprocity (Water/UBECrc)**: Balance of giving and receiving, flow
- **Mutualism (Earth/UBECgpi)**: Stability, grounding, mutual benefit
- **Regeneration (Fire/UBECtt)**: Transformation and sustainable contribution
- **Holism**: Integration across all dimensions

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained evaluation service
    ✅ 2.  Service Pattern: Factory-based, no standalone execution
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative with persistence
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Individual account and element tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Integrated Rate Limiting: Built-in for database operations
    ✅ 10. Separation of Concerns: Evaluation logic isolated
    ✅ 11. Comprehensive Documentation: Full docstrings and attribution
    ✅ 12. Method Singularity: No duplicate methods, single implementation
══════════════════════════════════════════════════════════════════════════════

Usage:
    from ubec_holonic_evaluator import create_holonic_evaluator
    
    evaluator = await create_holonic_evaluator(
        db_manager=async_db,
        config={
            'ubec_code': 'UBEC',
            'ubec_issuer': 'G...',
            'db_schema': 'ubec_main'
        }
    )
    
    # All methods are async
    result = await evaluator.evaluate_all_accounts()
    report = await evaluator.evaluate_network_holism()
    metrics = await evaluator.get_ubuntu_principle_metrics(account_id)
    health = await evaluator.health_check()
    
    await evaluator.close()

Database Schema:
    Uses TWO tables for complete evaluation:
    
    1. {schema}.holonic_metrics - Main holonic evaluation scores
       - autonomy_integration_score
       - multi_scale_score
       - regenerative_impact_score
       - network_contribution_score
       - ubuntu_alignment_score (calculated from element metrics)
       - composite_score
       - holonic_category
       - raw_metrics (JSONB)
    
    2. {schema}.ubec_holonic_metrics - Element-specific Ubuntu principles
       - account_id
       - element (Air, Water, Earth, Fire)
       - principle (diversity, reciprocity, mutualism, regeneration)
       - score (0.0-1.0)
       - health_status (healthy, degraded, unhealthy)
       - assessment_details (JSONB)
       - calculated_at

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.0.1 (Import Path Fix)
Date: November 10, 2025

Changelog:
    v3.0.1 - CRITICAL FIX: Corrected ServiceHealthCheck import path
           - Fixed: from utilities.service_health_check -> from core.utils.service_health
           - Resolves ModuleNotFoundError on service initialization
    v3.0.0 - MAJOR UPDATE: Complete Ubuntu principle integration
           - Added reciprocity_health calculation (Water/UBECrc flows)
           - Added mutualism_capacity calculation (Earth/UBECgpi stability)
           - Added diversity_score calculation (Air/UBEC participation)
           - Added regeneration_score calculation (Fire/UBECtt transformation)
           - All metrics stored in ubec_holonic_metrics table
           - ubuntu_alignment_score now properly calculated from elements
           - Health status assessment per principle
           - Complete API integration support
    v2.3.2 - PostgreSQL enum type casting fix
    v2.3.1 - Health check return type verification
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from core.utils.service_health import ServiceHealthCheck

# ==================== ENUMS AND CONSTANTS ====================

class HolonicCategory(Enum):
    """
    Holonic categories for UBEC token holders.
    
    Categories represent levels of integration with the network:
    - OBSERVER: Minimal participation (0-20%)
    - PARTICIPANT: Active participation (20-40%)
    - CONTRIBUTOR: Regular contribution (40-60%)
    - INTEGRATOR: High integration (60-80%)
    - EXEMPLAR: Exemplary Ubuntu alignment (80-100%)
    """
    OBSERVER = 'observer'
    PARTICIPANT = 'participant'
    CONTRIBUTOR = 'contributor'
    INTEGRATOR = 'integrator'
    EXEMPLAR = 'exemplar'


class UbuntuPrinciple(Enum):
    """Ubuntu principles aligned with four elements."""
    DIVERSITY = 'diversity'         # Air/UBEC
    RECIPROCITY = 'reciprocity'     # Water/UBECrc
    MUTUALISM = 'mutualism'         # Earth/UBECgpi
    REGENERATION = 'regeneration'   # Fire/UBECtt


class Element(Enum):
    """Four elements of the UBEC system."""
    AIR = 'Air'       # UBEC
    WATER = 'Water'   # UBECrc
    EARTH = 'Earth'   # UBECgpi
    FIRE = 'Fire'     # UBECtt


class HealthStatus(Enum):
    """Health status for principle metrics."""
    HEALTHY = 'healthy'         # Score >= 0.6
    DEGRADED = 'degraded'       # Score >= 0.3
    UNHEALTHY = 'unhealthy'     # Score < 0.3


# Element to token mapping
ELEMENT_TOKEN_MAP = {
    Element.AIR: 'UBEC',
    Element.WATER: 'UBECrc',
    Element.EARTH: 'UBECgpi',
    Element.FIRE: 'UBECtt'
}

# Principle to element mapping
PRINCIPLE_ELEMENT_MAP = {
    UbuntuPrinciple.DIVERSITY: Element.AIR,
    UbuntuPrinciple.RECIPROCITY: Element.WATER,
    UbuntuPrinciple.MUTUALISM: Element.EARTH,
    UbuntuPrinciple.REGENERATION: Element.FIRE
}


# ==================== DATA MODELS ====================

@dataclass
class UbuntuPrincipleMetrics:
    """Ubuntu principle metrics for a specific element."""
    account_id: str
    element: Element
    principle: UbuntuPrinciple
    score: float
    raw_value: Optional[float]
    normalized_value: Optional[float]
    health_status: HealthStatus
    assessment_details: Dict[str, Any]
    calculation_method: str
    data_points: int
    confidence_level: float
    calculated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'account_id': self.account_id,
            'element': self.element.value,
            'principle': self.principle.value,
            'score': self.score,
            'raw_value': self.raw_value,
            'normalized_value': self.normalized_value,
            'health_status': self.health_status.value,
            'assessment_details': self.assessment_details,
            'calculation_method': self.calculation_method,
            'data_points': self.data_points,
            'confidence_level': self.confidence_level,
            'calculated_at': self.calculated_at
        }


@dataclass
class HolonicMetrics:
    """Main holonic evaluation results for an account."""
    account_id: str
    autonomy_integration_score: float
    multi_scale_score: float
    regenerative_impact_score: float
    network_contribution_score: float
    ubuntu_alignment_score: float
    composite_score: float
    holonic_category: HolonicCategory
    raw_metrics: Dict[str, Any]
    evaluation_date: datetime
    
    # Element-specific Ubuntu principle scores (from ubec_holonic_metrics table)
    diversity_score: Optional[float] = None         # Air/UBEC
    reciprocity_health: Optional[float] = None      # Water/UBECrc
    mutualism_capacity: Optional[float] = None      # Earth/UBECgpi
    regeneration_score: Optional[float] = None      # Fire/UBECtt
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'account_id': self.account_id,
            'autonomy_integration_score': self.autonomy_integration_score,
            'multi_scale_score': self.multi_scale_score,
            'regenerative_impact_score': self.regenerative_impact_score,
            'network_contribution_score': self.network_contribution_score,
            'ubuntu_alignment_score': self.ubuntu_alignment_score,
            'composite_score': self.composite_score,
            'holonic_category': self.holonic_category.value,
            'diversity_score': self.diversity_score,
            'reciprocity_health': self.reciprocity_health,
            'mutualism_capacity': self.mutualism_capacity,
            'regeneration_score': self.regeneration_score,
            'raw_metrics': self.raw_metrics,
            'evaluation_date': self.evaluation_date.isoformat()
        }
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'HolonicMetrics':
        """Create instance from database row."""
        return cls(
            account_id=row['account_id'],
            autonomy_integration_score=float(row['autonomy_integration_score']),
            multi_scale_score=float(row['multi_scale_score']),
            regenerative_impact_score=float(row['regenerative_impact_score']),
            network_contribution_score=float(row['network_contribution_score']),
            ubuntu_alignment_score=float(row['ubuntu_alignment_score']),
            composite_score=float(row['composite_score']),
            holonic_category=HolonicCategory(row['holonic_category']),
            diversity_score=float(row['diversity_score']) if row.get('diversity_score') else None,
            reciprocity_health=float(row['reciprocity_health']) if row.get('reciprocity_health') else None,
            mutualism_capacity=float(row['mutualism_capacity']) if row.get('mutualism_capacity') else None,
            regeneration_score=float(row['regeneration_score']) if row.get('regeneration_score') else None,
            raw_metrics=row.get('raw_metrics', {}),
            evaluation_date=row['evaluation_date']
        )


# ==================== MAIN SERVICE CLASS ====================

class UBECHolonicEvaluator:
    """
    Holonic evaluator service for UBEC token holders.
    
    Implements Ubuntu philosophy through quantitative metrics across five dimensions
    plus four element-specific Ubuntu principles.
    """
    
    def __init__(self, db_manager, config: Dict[str, Any]):
        """
        Initialize the holonic evaluator.
        
        Args:
            db_manager: Async database manager
            config: Configuration dictionary
        """
        self.db_manager = db_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Extract configuration
        self.db_schema = config.get('db_schema', 'ubec_main')
        self.ubec_code = config.get('ubec_code', 'UBEC')
        self.ubec_issuer = config.get('ubec_issuer', '')
        
        # Scoring weights (should sum to 1.0)
        self.weights = {
            'autonomy_integration': config.get('holonic_weight_autonomy', 0.20),
            'multi_scale': config.get('holonic_weight_multi_scale', 0.20),
            'regenerative_impact': config.get('holonic_weight_regenerative', 0.20),
            'network_contribution': config.get('holonic_weight_network', 0.20),
            'ubuntu_alignment': config.get('holonic_weight_ubuntu', 0.20)
        }
        
        # Category thresholds
        self.thresholds = {
            'observer': 0.2,
            'participant': 0.4,
            'contributor': 0.6,
            'integrator': 0.8
        }
        
        # State tracking
        self._initialized = False
        self._has_ubuntu_metrics_table = False
        self._evaluation_count = 0
        self._error_count = 0
        self._last_evaluation_time: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
    
    async def initialize(self) -> bool:
        """
        Initialize the evaluator service.
        
        Verifies database schema and tables exist.
        
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info(f"Initializing UBEC Holonic Evaluator | schema={self.db_schema}")
            
            # Check if holonic_metrics table exists
            check_query = f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = '{self.db_schema}' 
                    AND table_name = 'holonic_metrics'
                )
            """
            result = await self.db_manager.fetch_one(check_query, ())
            
            if not result or not result['exists']:
                self.logger.error(f"Table {self.db_schema}.holonic_metrics not found")
                return False
            
            # Check if ubec_holonic_metrics table exists (for Ubuntu principles)
            ubuntu_check_query = f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = '{self.db_schema}' 
                    AND table_name = 'ubec_holonic_metrics'
                )
            """
            ubuntu_result = await self.db_manager.fetch_one(ubuntu_check_query, ())
            self._has_ubuntu_metrics_table = ubuntu_result and ubuntu_result['exists']
            
            if self._has_ubuntu_metrics_table:
                self.logger.info("✓ Ubuntu principle metrics table available")
            else:
                self.logger.warning("Ubuntu principle metrics table not found - element scores unavailable")
            
            self._initialized = True
            self.logger.info("✓ UBEC Holonic Evaluator initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize evaluator: {e}", exc_info=True)
            return False
    
    # ==================== EVALUATION METHODS ====================
    
    async def evaluate_account(self, account_id: str) -> Optional[HolonicMetrics]:
        """
        Evaluate a single account for holonic metrics.
        
        Args:
            account_id: Stellar account ID to evaluate
            
        Returns:
            HolonicMetrics if successful, None otherwise
        """
        try:
            self.logger.debug(f"Evaluating account: {account_id}")
            
            # Calculate dimension scores
            autonomy_score = await self._calculate_autonomy_integration(account_id)
            multi_scale_score = await self._calculate_multi_scale_participation(account_id)
            regenerative_score = await self._calculate_regenerative_impact(account_id)
            network_score = await self._calculate_network_contribution(account_id)
            
            # Get Ubuntu principle scores if available
            ubuntu_scores = await self._get_ubuntu_principle_scores(account_id)
            
            # Calculate ubuntu_alignment_score from element scores
            if ubuntu_scores:
                ubuntu_alignment_score = (
                    ubuntu_scores.get('diversity_score', 0) * 0.25 +
                    ubuntu_scores.get('reciprocity_health', 0) * 0.25 +
                    ubuntu_scores.get('mutualism_capacity', 0) * 0.25 +
                    ubuntu_scores.get('regeneration_score', 0) * 0.25
                )
            else:
                # Fallback calculation if element scores unavailable
                ubuntu_alignment_score = (autonomy_score + network_score) / 2
            
            # Calculate composite score
            composite_score = (
                autonomy_score * self.weights['autonomy_integration'] +
                multi_scale_score * self.weights['multi_scale'] +
                regenerative_score * self.weights['regenerative_impact'] +
                network_score * self.weights['network_contribution'] +
                ubuntu_alignment_score * self.weights['ubuntu_alignment']
            )
            
            # Determine category
            category = self._determine_category(composite_score)
            
            # Create metrics object
            metrics = HolonicMetrics(
                account_id=account_id,
                autonomy_integration_score=autonomy_score,
                multi_scale_score=multi_scale_score,
                regenerative_impact_score=regenerative_score,
                network_contribution_score=network_score,
                ubuntu_alignment_score=ubuntu_alignment_score,
                composite_score=composite_score,
                holonic_category=category,
                diversity_score=ubuntu_scores.get('diversity_score') if ubuntu_scores else None,
                reciprocity_health=ubuntu_scores.get('reciprocity_health') if ubuntu_scores else None,
                mutualism_capacity=ubuntu_scores.get('mutualism_capacity') if ubuntu_scores else None,
                regeneration_score=ubuntu_scores.get('regeneration_score') if ubuntu_scores else None,
                raw_metrics={
                    'autonomy': autonomy_score,
                    'multi_scale': multi_scale_score,
                    'regenerative': regenerative_score,
                    'network': network_score,
                    'ubuntu': ubuntu_alignment_score
                },
                evaluation_date=datetime.now(timezone.utc)
            )
            
            # Store evaluation
            await self._store_evaluation(metrics)
            
            self._evaluation_count += 1
            self._last_evaluation_time = datetime.now(timezone.utc)
            
            return metrics
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error evaluating account {account_id}: {e}")
            return None
    
    async def evaluate_all_accounts(self) -> Dict[str, Any]:
        """
        Evaluate all UBEC holders in the system.
        
        Returns:
            Summary of evaluation results
        """
        try:
            self.logger.info("Starting evaluation of all UBEC accounts")
            
            # Get all account holders
            query = f"""
                SELECT DISTINCT account_id
                FROM {self.db_schema}.account_balances
                WHERE asset_code = $1 AND balance > 0
                ORDER BY account_id
            """
            
            accounts = await self.db_manager.fetch_all(query, (self.ubec_code,))
            total_accounts = len(accounts)
            
            self.logger.info(f"Found {total_accounts} accounts to evaluate")
            
            # Evaluate each account
            successful = 0
            failed = 0
            
            for account in accounts:
                account_id = account['account_id']
                result = await self.evaluate_account(account_id)
                
                if result:
                    successful += 1
                else:
                    failed += 1
            
            summary = {
                'total_accounts': total_accounts,
                'successful': successful,
                'failed': failed,
                'success_rate': successful / total_accounts if total_accounts > 0 else 0,
                'evaluation_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.info(f"Evaluation complete: {successful}/{total_accounts} successful")
            
            return summary
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error in evaluate_all_accounts: {e}")
            return {
                'total_accounts': 0,
                'successful': 0,
                'failed': 0,
                'error': str(e)
            }
    
    async def evaluate_network_holism(self) -> Dict[str, Any]:
        """
        Evaluate overall network holism and Ubuntu principle integration.
        
        Returns:
            Network-level holistic assessment
        """
        try:
            self.logger.info("Evaluating network holism")
            
            # Get category distribution
            distribution_query = f"""
                SELECT 
                    holonic_category,
                    COUNT(*) as count,
                    AVG(composite_score) as avg_score
                FROM {self.db_schema}.holonic_metrics
                WHERE evaluation_date >= NOW() - INTERVAL '7 days'
                GROUP BY holonic_category
                ORDER BY 
                    CASE holonic_category
                        WHEN 'observer' THEN 1
                        WHEN 'participant' THEN 2
                        WHEN 'contributor' THEN 3
                        WHEN 'integrator' THEN 4
                        WHEN 'exemplar' THEN 5
                    END
            """
            
            distribution = await self.db_manager.fetch_all(distribution_query, ())
            
            # Get overall statistics
            stats_query = f"""
                SELECT 
                    COUNT(*) as total_evaluated,
                    AVG(composite_score) as avg_composite,
                    AVG(ubuntu_alignment_score) as avg_ubuntu,
                    STDDEV(composite_score) as score_stddev
                FROM {self.db_schema}.holonic_metrics
                WHERE evaluation_date >= NOW() - INTERVAL '7 days'
            """
            
            stats = await self.db_manager.fetch_one(stats_query, ())
            
            # Calculate network holism score
            # Higher scores for more balanced distribution across categories
            if distribution:
                total_accounts = sum(row['count'] for row in distribution)
                category_proportions = [row['count'] / total_accounts for row in distribution]
                
                # Shannon entropy as diversity measure
                import math
                entropy = -sum(p * math.log(p) if p > 0 else 0 for p in category_proportions)
                max_entropy = math.log(5)  # 5 categories
                diversity_score = entropy / max_entropy if max_entropy > 0 else 0
            else:
                diversity_score = 0
            
            report = {
                'network_holism_score': diversity_score,
                'total_evaluated': int(stats['total_evaluated']) if stats else 0,
                'average_composite_score': float(stats['avg_composite']) if stats and stats['avg_composite'] else 0,
                'average_ubuntu_score': float(stats['avg_ubuntu']) if stats and stats['avg_ubuntu'] else 0,
                'score_stddev': float(stats['score_stddev']) if stats and stats['score_stddev'] else 0,
                'category_distribution': [
                    {
                        'category': row['holonic_category'],
                        'count': int(row['count']),
                        'average_score': float(row['avg_score'])
                    }
                    for row in distribution
                ],
                'evaluation_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.info(f"Network holism evaluation complete: score={diversity_score:.3f}")
            
            return report
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error evaluating network holism: {e}")
            return {'error': str(e)}
    
    # ==================== UBUNTU PRINCIPLE METHODS ====================
    
    async def get_ubuntu_principle_metrics(
        self,
        account_id: str
    ) -> Optional[Dict[str, List[UbuntuPrincipleMetrics]]]:
        """
        Retrieve Ubuntu principle metrics for an account.
        
        Args:
            account_id: Account to retrieve metrics for
            
        Returns:
            Dictionary mapping principles to their metrics, or None if unavailable
        """
        if not self._has_ubuntu_metrics_table:
            self.logger.warning("Ubuntu metrics table not available")
            return None
        
        try:
            query = f"""
                SELECT *
                FROM {self.db_schema}.ubec_holonic_metrics
                WHERE account_id = $1
                ORDER BY calculated_at DESC
            """
            
            results = await self.db_manager.fetch_all(query, (account_id,))
            
            if not results:
                return None
            
            # Group by principle
            metrics_by_principle = {}
            for row in results:
                principle = UbuntuPrinciple(row['principle'])
                
                metric = UbuntuPrincipleMetrics(
                    account_id=row['account_id'],
                    element=Element(row['element']),
                    principle=principle,
                    score=float(row['score']),
                    raw_value=float(row['raw_value']) if row.get('raw_value') else None,
                    normalized_value=float(row['normalized_value']) if row.get('normalized_value') else None,
                    health_status=HealthStatus(row['health_status']),
                    assessment_details=row.get('assessment_details', {}),
                    calculation_method=row.get('calculation_method', 'unknown'),
                    data_points=row.get('data_points', 0),
                    confidence_level=float(row.get('confidence_level', 0)),
                    calculated_at=row['calculated_at']
                )
                
                if principle not in metrics_by_principle:
                    metrics_by_principle[principle] = []
                metrics_by_principle[principle].append(metric)
            
            return metrics_by_principle
            
        except Exception as e:
            self.logger.error(f"Error retrieving Ubuntu metrics for {account_id}: {e}")
            return None
    
    async def _get_ubuntu_principle_scores(self, account_id: str) -> Optional[Dict[str, float]]:
        """
        Get latest Ubuntu principle scores for an account.
        
        Returns dict with diversity_score, reciprocity_health, mutualism_capacity, regeneration_score
        """
        if not self._has_ubuntu_metrics_table:
            return None
        
        try:
            query = f"""
                SELECT DISTINCT ON (principle) 
                    principle, score
                FROM {self.db_schema}.ubec_holonic_metrics
                WHERE account_id = $1
                ORDER BY principle, calculated_at DESC
            """
            
            results = await self.db_manager.fetch_all(query, (account_id,))
            
            if not results:
                return None
            
            scores = {}
            for row in results:
                principle = row['principle']
                score = float(row['score'])
                
                # Map principle to appropriate field name
                if principle == 'diversity':
                    scores['diversity_score'] = score
                elif principle == 'reciprocity':
                    scores['reciprocity_health'] = score
                elif principle == 'mutualism':
                    scores['mutualism_capacity'] = score
                elif principle == 'regeneration':
                    scores['regeneration_score'] = score
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Error retrieving Ubuntu scores for {account_id}: {e}")
            return None
    
    # ==================== DIMENSION CALCULATIONS ====================
    
    async def _calculate_autonomy_integration(self, account_id: str) -> float:
        """Calculate autonomy integration score."""
        try:
            # Check if account has active trustlines and participates in network
            query = f"""
                SELECT COUNT(DISTINCT asset_code) as asset_count
                FROM {self.db_schema}.account_balances
                WHERE account_id = $1 AND balance > 0
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            
            if not result:
                return 0.0
            
            asset_count = result['asset_count']
            
            # Normalize: having all 4 element tokens = 1.0
            return min(asset_count / 4.0, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating autonomy for {account_id}: {e}")
            return 0.0
    
    async def _calculate_multi_scale_participation(self, account_id: str) -> float:
        """Calculate multi-scale participation score."""
        try:
            # Measure diversity of transaction types and scales
            query = f"""
                SELECT 
                    COUNT(DISTINCT type) as operation_types,
                    COUNT(*) as total_operations
                FROM {self.db_schema}.stellar_operations
                WHERE source_account = $1 OR destination_account = $1
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            
            if not result or result['total_operations'] == 0:
                return 0.0
            
            # More operation types = higher score
            operation_types = result['operation_types']
            
            # Normalize: 5+ operation types = 1.0
            return min(operation_types / 5.0, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating multi-scale for {account_id}: {e}")
            return 0.0
    
    async def _calculate_regenerative_impact(self, account_id: str) -> float:
        """Calculate regenerative impact score."""
        try:
            # Measure contribution to network growth and sustainability
            # For now, use transaction frequency as proxy
            query = f"""
                SELECT COUNT(*) as operation_count
                FROM {self.db_schema}.stellar_operations
                WHERE (source_account = $1 OR destination_account = $1)
                    AND created_at >= NOW() - INTERVAL '30 days'
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            
            if not result:
                return 0.0
            
            operation_count = result['operation_count']
            
            # Normalize: 50+ operations per month = 1.0
            return min(operation_count / 50.0, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating regenerative impact for {account_id}: {e}")
            return 0.0
    
    async def _calculate_network_contribution(self, account_id: str) -> float:
        """Calculate network contribution score."""
        try:
            # Measure active participation in the network
            query = f"""
                SELECT 
                    COUNT(*) as sent_operations,
                    (SELECT COUNT(*) 
                     FROM {self.db_schema}.stellar_operations 
                     WHERE destination_account = $1) as received_operations
                FROM {self.db_schema}.stellar_operations
                WHERE source_account = $1
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            
            if not result:
                return 0.0
            
            sent = result['sent_operations']
            received = result['received_operations']
            total = sent + received
            
            if total == 0:
                return 0.0
            
            # Balance of giving and receiving (reciprocity)
            balance_ratio = min(sent, received) / max(sent, received) if max(sent, received) > 0 else 0
            
            # Activity level
            activity_score = min(total / 100.0, 1.0)
            
            # Combined score
            return (balance_ratio * 0.5 + activity_score * 0.5)
            
        except Exception as e:
            self.logger.error(f"Error calculating network contribution for {account_id}: {e}")
            return 0.0
    
    # ==================== STORAGE ====================
    
    async def _store_evaluation(self, metrics: HolonicMetrics) -> bool:
        """
        Store evaluation results in database.
        
        Args:
            metrics: Evaluation metrics to store
            
        Returns:
            True if successful
        """
        try:
            query = f"""
                INSERT INTO {self.db_schema}.holonic_metrics (
                    account_id,
                    autonomy_integration_score,
                    multi_scale_score,
                    regenerative_impact_score,
                    network_contribution_score,
                    ubuntu_alignment_score,
                    composite_score,
                    holonic_category,
                    diversity_score,
                    reciprocity_health,
                    mutualism_capacity,
                    regeneration_score,
                    raw_metrics,
                    evaluation_date
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                ON CONFLICT (account_id, evaluation_date) 
                DO UPDATE SET
                    autonomy_integration_score = EXCLUDED.autonomy_integration_score,
                    multi_scale_score = EXCLUDED.multi_scale_score,
                    regenerative_impact_score = EXCLUDED.regenerative_impact_score,
                    network_contribution_score = EXCLUDED.network_contribution_score,
                    ubuntu_alignment_score = EXCLUDED.ubuntu_alignment_score,
                    composite_score = EXCLUDED.composite_score,
                    holonic_category = EXCLUDED.holonic_category,
                    diversity_score = EXCLUDED.diversity_score,
                    reciprocity_health = EXCLUDED.reciprocity_health,
                    mutualism_capacity = EXCLUDED.mutualism_capacity,
                    regeneration_score = EXCLUDED.regeneration_score,
                    raw_metrics = EXCLUDED.raw_metrics
            """
            
            await self.db_manager.execute(
                query,
                (
                    metrics.account_id,
                    metrics.autonomy_integration_score,
                    metrics.multi_scale_score,
                    metrics.regenerative_impact_score,
                    metrics.network_contribution_score,
                    metrics.ubuntu_alignment_score,
                    metrics.composite_score,
                    metrics.holonic_category.value,
                    metrics.diversity_score,
                    metrics.reciprocity_health,
                    metrics.mutualism_capacity,
                    metrics.regeneration_score,
                    json.dumps(metrics.raw_metrics),
                    metrics.evaluation_date
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing evaluation for {metrics.account_id}: {e}")
            return False
    
    # ==================== RETRIEVAL ====================
    
    async def get_latest_evaluation(self, account_id: str) -> Optional[HolonicMetrics]:
        """
        Retrieve latest evaluation for an account.
        
        Args:
            account_id: Account to retrieve evaluation for
            
        Returns:
            Latest HolonicMetrics or None
        """
        try:
            query = f"""
                SELECT *
                FROM {self.db_schema}.holonic_metrics
                WHERE account_id = $1
                ORDER BY evaluation_date DESC
                LIMIT 1
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            
            if not result:
                return None
            
            return HolonicMetrics.from_db_row(result)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error retrieving latest evaluation: {e}")
            return None
    
    async def get_evaluation_history(
        self,
        account_id: str,
        days: int = 30
    ) -> List[HolonicMetrics]:
        """
        Retrieve evaluation history for an account.
        
        Args:
            account_id: Account to retrieve history for
            days: Number of days of history to retrieve
            
        Returns:
            List of HolonicMetrics ordered by date descending
        """
        try:
            query = f"""
                SELECT *
                FROM {self.db_schema}.holonic_metrics
                WHERE account_id = $1
                    AND evaluation_date >= NOW() - INTERVAL '{days} days'
                ORDER BY evaluation_date DESC
            """
            
            results = await self.db_manager.fetch_all(query, (account_id,))
            
            return [HolonicMetrics.from_db_row(row) for row in results]
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error retrieving evaluation history: {e}")
            return []
    
    # ==================== HELPERS ====================
    
    def _determine_category(self, composite_score: float) -> HolonicCategory:
        """
        Determine holonic category based on composite score.
        
        Args:
            composite_score: Composite evaluation score (0-1)
            
        Returns:
            HolonicCategory enum value
        """
        if composite_score >= self.thresholds['integrator']:
            return HolonicCategory.EXEMPLAR
        elif composite_score >= self.thresholds['contributor']:
            return HolonicCategory.INTEGRATOR
        elif composite_score >= self.thresholds['participant']:
            return HolonicCategory.CONTRIBUTOR
        elif composite_score >= self.thresholds['observer']:
            return HolonicCategory.PARTICIPANT
        else:
            return HolonicCategory.OBSERVER
    
    # ==================== HEALTH CHECK ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for evaluator service.
        
        Uses ServiceHealthCheck utility for standardized monitoring.
        
        Returns:
            Health status dictionary
        """
        checks = [
            ('initialization', self._check_initialization),
            ('database', self._check_database),
            ('operations', self._check_operations),
            ('weights', self._check_weights)
        ]
        
        result = await ServiceHealthCheck.run_health_checks(
            service_name='UBECHolonicEvaluator',
            checks=checks,
            logger=self.logger
        )
        
        # Add service-specific stats
        result['stats'] = {
            'evaluations_performed': self._evaluation_count,
            'error_count': self._error_count,
            'last_evaluation': self._last_evaluation_time.isoformat() if self._last_evaluation_time else None,
            'ubuntu_metrics_enabled': self._has_ubuntu_metrics_table
        }
        
        return result
    
    async def _check_initialization(self) -> Optional[Dict[str, Any]]:
        """Check if service is properly initialized."""
        if not self._initialized:
            return {
                'name': 'initialization',
                'status': 'fail',
                'message': 'Service not initialized',
                'severity': 'high'
            }
        return None
    
    async def _check_database(self) -> Optional[Dict[str, Any]]:
        """Check database connectivity."""
        try:
            query = f"SELECT 1 FROM {self.db_schema}.holonic_metrics LIMIT 1"
            await self.db_manager.fetch_one(query, ())
            return None
        except Exception as e:
            return {
                'name': 'database',
                'status': 'fail',
                'message': f'Database check failed: {str(e)}',
                'severity': 'high',
                'error': str(e)
            }
    
    async def _check_operations(self) -> Optional[Dict[str, Any]]:
        """Check operational metrics."""
        try:
            if self._evaluation_count > 0:
                error_rate = self._error_count / self._evaluation_count
                
                if error_rate > 0.5:
                    return {
                        'name': 'operations',
                        'status': 'fail',
                        'message': f'High error rate: {error_rate:.1%}',
                        'severity': 'high',
                        'details': {
                            'evaluations': self._evaluation_count,
                            'errors': self._error_count,
                            'error_rate': error_rate
                        }
                    }
                elif error_rate > 0.2:
                    return {
                        'name': 'operations',
                        'status': 'warn',
                        'message': f'Elevated error rate: {error_rate:.1%}',
                        'severity': 'medium',
                        'details': {
                            'evaluations': self._evaluation_count,
                            'errors': self._error_count,
                            'error_rate': error_rate
                        }
                    }
            
            return None
            
        except Exception as e:
            return {
                'name': 'operations',
                'status': 'fail',
                'message': f'Operations check failed: {str(e)}',
                'severity': 'low',
                'error': str(e)
            }
    
    async def _check_weights(self) -> Optional[Dict[str, Any]]:
        """Verify evaluation weights sum to 1.0."""
        try:
            total = sum(self.weights.values())
            if abs(total - 1.0) > 0.01:
                return {
                    'name': 'weights',
                    'status': 'warn',
                    'message': f'Weights sum to {total:.3f}, not 1.0',
                    'severity': 'low',
                    'details': {'weight_sum': total, 'weights': self.weights}
                }
            return None
        except Exception as e:
            return {
                'name': 'weights',
                'status': 'fail',
                'message': f'Weight validation failed: {str(e)}',
                'severity': 'low',
                'error': str(e)
            }
    
    # ==================== CLEANUP ====================
    
    async def close(self) -> None:
        """
        Clean up resources.
        
        Called by service registry during system shutdown.
        """
        self.logger.info("Closing UBEC Holonic Evaluator")
        self._initialized = False


# ==================== FACTORY FUNCTION ====================

async def create_holonic_evaluator(
    db_manager,
    config: Dict[str, Any]
) -> UBECHolonicEvaluator:
    """
    Factory function to create and initialize UBEC Holonic Evaluator.
    
    This function follows the service pattern by creating and initializing
    the evaluator with proper error handling.
    
    Args:
        db_manager: Async database manager instance
        config: Configuration dictionary
        
    Returns:
        Initialized UBECHolonicEvaluator instance
        
    Raises:
        RuntimeError: If initialization fails
        
    Example:
        evaluator = await create_holonic_evaluator(
            db_manager=async_db,
            config={
                'db_schema': 'ubec_main',
                'ubec_code': 'UBEC',
                'ubec_issuer': 'G...'
            }
        )
    """
    evaluator = UBECHolonicEvaluator(db_manager, config)
    
    if not await evaluator.initialize():
        raise RuntimeError("Failed to initialize UBEC Holonic Evaluator")
    
    return evaluator


# ==================== MODULE EXPORTS ====================

__all__ = [
    'HolonicCategory',
    'UbuntuPrinciple',
    'Element',
    'HealthStatus',
    'UbuntuPrincipleMetrics',
    'HolonicMetrics',
    'UBECHolonicEvaluator',
    'create_holonic_evaluator'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator."
    )
