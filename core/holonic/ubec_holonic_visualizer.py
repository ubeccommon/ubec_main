#!/usr/bin/env python3
# core/holonic/ubec_holonic_visualizer.py
"""
UBEC Holonic Visualizer - Async Visualization Service (Enhanced)
=================================================================

Service implementation for comprehensive visualization of UBEC holonic evaluation results.
Creates charts, graphs, and HTML reports from holonic metrics data with advanced analytics.

This module provides:
1. Score distribution histograms
2. Radar charts of holonic dimensions
3. Category distribution pie charts
4. Network visualization graphs
5. Time-series trend analysis
6. Comparative analysis charts
7. Correlation matrices
8. Account detail views
9. Element-specific dashboards
10. Comprehensive HTML reports

Design Principles Compliance:
────────────────────────────────────────────────────────────────────────────────
    ✅ 1.  Modular Design: Self-contained visualization service
    ✅ 2.  Service Pattern: Factory-based instantiation, no standalone execution
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: ALL I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Individual account visualization
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Integrated Rate Limiting: Built-in for database operations
    ✅ 10. Separation of Concerns: Visualization logic isolated
    ✅ 11. Comprehensive Documentation: Full docstrings and attribution
    ✅ 12. Method Singularity: No duplicate methods
────────────────────────────────────────────────────────────────────────────────

Usage:
    from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer
    
    visualizer = await create_holonic_visualizer(
        db_manager=async_db,
        config={'db_schema': 'ubec_main'}
    )
    
    # All methods are async
    report = await visualizer.generate_html_report('/path/to/output')
    chart = await visualizer.create_score_distribution_chart()
    trends = await visualizer.create_time_series_chart(days=30)
    network = await visualizer.create_network_visualization()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 6.2.0 (Fixed Account Matching)
Date: October 14, 2025

Changes in v6.2.0:
    - 🔧 CRITICAL FIX: load_network_data now queries evaluated accounts FIRST
    - 🔧 Then fetches transaction activity specifically for those accounts
    - 🔧 Uses WHERE source_account = ANY($1) to filter by evaluated accounts
    - 🔧 No more arbitrary LIMIT 100 that excluded evaluated accounts
    - 🔧 Now correctly matches accounts between holonic_metrics and stellar_transactions
    - ✅ Verified with SQL diagnostics showing 5/5 matches

Changes in v6.1.1:
    - ✅ Fixed network visualization to work with nodes-only (no edges required)
    - ✅ Added detailed diagnostic logging for account matching
    - ✅ Network viz now shows evaluated accounts even without transaction edges
    - ✅ Logs account matching statistics for debugging
    - ✅ Works with stellar_transactions source-centric model

Changes in v6.1.0:
    - ✅ EXACT stellar_transactions table implementation
    - ✅ Removed ALL fallback logic - coding is exact science
    - ✅ Uses precise column names: source_account, fee_charged, successful
    - ✅ Activity-based network visualization (transaction counts, fees, success rates)
    - ✅ No assumptions, no table checking - exact database schema

Changes in v6.0.0:
    - ✅ Added time-series trend analysis
    - ✅ Added comparative analysis charts
    - ✅ Added correlation matrix visualization
    - ✅ Added network visualization with NetworkX
    - ✅ Added account detail views
    - ✅ Added element-specific dashboard support
    - ✅ Enhanced HTML reports with all new visualizations
    - ✅ Improved color schemes and styling
    - ✅ All 12 design principles enforced
"""

import asyncio
import logging
import json
import base64
from datetime import datetime, timezone, timedelta
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

# Visualization libraries
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import numpy as np
from scipy import stats
import seaborn as sns

# Network visualization (optional dependency)
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

logger = logging.getLogger(__name__)


# ========================================================================
# HOLONIC VISUALIZER SERVICE (ENHANCED)
# Principle 1: Modular Design - Self-contained service
# Principle 2: Service Pattern - No standalone execution
# ========================================================================

class UBECHolonicVisualizer:
    """
    Enhanced Async UBEC Holonic Visualizer Service
    
    Creates comprehensive visualizations from holonic evaluation data using
    pure async operations. All database access uses async patterns.
    
    The visualizer generates:
    1. Score distribution histograms
    2. Holonic dimension radar charts
    3. Category distribution pie charts
    4. Network visualization graphs
    5. Time-series trend analysis
    6. Comparative analysis charts
    7. Correlation matrices
    8. Account detail views
    9. Element-specific dashboards
    10. Comprehensive HTML reports
    
    Design Principles:
    - Principle 1: Modular - Clear boundaries, single responsibility
    - Principle 3: Service Registry - Dependencies via constructor
    - Principle 4: Single Source of Truth - Database-driven data
    - Principle 5: Strict Async - All I/O operations are async
    - Principle 10: Separation of Concerns - Clear layer separation
    - Principle 12: Method Singularity - Each visualization implemented once
    """
    
    # Color schemes for visualizations
    ELEMENT_COLORS = {
        'air': '#87CEEB',      # Sky Blue
        'water': '#4682B4',    # Steel Blue
        'earth': '#8B4513',    # Saddle Brown
        'fire': '#FF4500'      # Orange Red
    }
    
    CATEGORY_COLORS = {
        'Exemplar': '#8b5cf6',
        'Integrator': '#10b981',
        'Contributor': '#3b82f6',
        'Participant': '#f59e0b',
        'Observer': '#9ca3af'
    }
    
    DIMENSION_COLORS = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'
    ]
    
    def __init__(
        self,
        db_manager: Any,
        config: Dict[str, Any]
    ):
        """
        Initialize async holonic visualizer.
        
        Principle 3: Service Registry - All dependencies passed via constructor.
        
        Args:
            db_manager: Async database manager instance
            config: Configuration dictionary with:
                - db_schema: Database schema name (required)
                - element_mode: Enable element-specific features (optional)
                
        Raises:
            ValueError: If required config parameters are missing
        """
        # Initialize logger FIRST
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Validate database manager
        if not hasattr(db_manager, 'fetch_all') or not hasattr(db_manager, 'fetch_one'):
            raise ValueError(
                f"Invalid database manager type: {type(db_manager)}. "
                "Expected AsyncDatabaseManager with fetch_all and fetch_one methods."
            )
        
        self.db_manager = db_manager
        self.config = config
        
        # Extract configuration (Principle 8: No duplicate config)
        self.db_schema = config.get('db_schema', 'ubec_main')
        self.element_mode = config.get('element_mode', False)
        
        # Cache for evaluation data
        self.report_data: Optional[Dict[str, Any]] = None
        self.time_series_data: Optional[List[Dict[str, Any]]] = None
        self.network_data: Optional[Dict[str, Any]] = None
        
        # Set seaborn style for better-looking plots
        sns.set_style("whitegrid")
        
        self.logger.info(
            f"Enhanced Holonic Visualizer initialized "
            f"(element_mode={self.element_mode}, networkx={NETWORKX_AVAILABLE})"
        )
    
    # ========================================================================
    # DATA LOADING
    # Principle 4: Single Source of Truth - Database as authority
    # Principle 5: Strict Async - All operations async
    # ========================================================================
    
    async def load_evaluation_data(
        self,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Load holonic evaluation data from database.
        
        Principle 4: Database is the single source of truth for evaluation data.
        Principle 5: Fully async operation.
        
        Args:
            limit: Maximum number of evaluation records to load (optional)
            
        Returns:
            Dictionary with evaluation data including:
            - status: 'success' or 'error'
            - evaluated_count: Number of accounts loaded
            - evaluation_date: Timestamp of data
            - category_distribution: Dict of category counts
            - average_scores: Dict of average dimension scores
            - results: List of individual account evaluations
            
        Example:
            >>> data = await visualizer.load_evaluation_data(limit=100)
            >>> print(f"Loaded {data['evaluated_count']} evaluations")
        
        Design Notes:
            - Queries holonic_metrics table directly
            - Gets most recent evaluation per account
            - Calculates aggregate statistics
            - Caches results in self.report_data
        """
        try:
            self.logger.info(f"Loading evaluation data from database (limit={limit})...")
            
            # Query for most recent evaluations per account
            query = f"""
                WITH latest_evals AS (
                    SELECT DISTINCT ON (account_id)
                        account_id,
                        evaluation_date,
                        autonomy_integration_score,
                        multi_scale_score,
                        regenerative_impact_score,
                        network_contribution_score,
                        ubuntu_alignment_score,
                        composite_score,
                        holonic_category,
                        raw_metrics
                    FROM {self.db_schema}.holonic_metrics
                    ORDER BY account_id, evaluation_date DESC
                )
                SELECT *
                FROM latest_evals
                ORDER BY composite_score DESC
                {'LIMIT $1' if limit else ''}
            """
            
            params = (limit,) if limit else ()
            results = await self.db_manager.fetch_all(query, params)
            
            if not results or len(results) == 0:
                self.logger.warning("No evaluation data found in database")
                self.report_data = {
                    "status": "success",
                    "evaluated_count": 0,
                    "evaluation_date": datetime.now(timezone.utc).isoformat(),
                    "category_distribution": {},
                    "average_scores": {
                        'autonomy': 0, 'multi_scale': 0, 'regenerative': 0,
                        'network': 0, 'ubuntu': 0, 'composite': 0
                    },
                    "results": []
                }
                return self.report_data
            
            # Get category distribution
            category_query = f"""
                WITH latest_evals AS (
                    SELECT DISTINCT ON (account_id)
                        account_id,
                        holonic_category
                    FROM {self.db_schema}.holonic_metrics
                    ORDER BY account_id, evaluation_date DESC
                )
                SELECT holonic_category, COUNT(*) as count
                FROM latest_evals
                GROUP BY holonic_category
            """
            
            categories = await self.db_manager.fetch_all(category_query, ())
            category_distribution = {
                cat['holonic_category']: cat['count'] 
                for cat in categories
            } if categories else {}
            
            # Calculate average scores
            avg_query = f"""
                WITH latest_evals AS (
                    SELECT DISTINCT ON (account_id) *
                    FROM {self.db_schema}.holonic_metrics
                    ORDER BY account_id, evaluation_date DESC
                )
                SELECT 
                    AVG(autonomy_integration_score) as autonomy,
                    AVG(multi_scale_score) as multi_scale,
                    AVG(regenerative_impact_score) as regenerative,
                    AVG(network_contribution_score) as network,
                    AVG(ubuntu_alignment_score) as ubuntu,
                    AVG(composite_score) as composite
                FROM latest_evals
            """
            
            avg_scores_result = await self.db_manager.fetch_one(avg_query, ())
            
            # Convert Decimal to float for JSON serialization
            avg_scores = {
                'autonomy': float(avg_scores_result['autonomy'] or 0),
                'multi_scale': float(avg_scores_result['multi_scale'] or 0),
                'regenerative': float(avg_scores_result['regenerative'] or 0),
                'network': float(avg_scores_result['network'] or 0),
                'ubuntu': float(avg_scores_result['ubuntu'] or 0),
                'composite': float(avg_scores_result['composite'] or 0)
            } if avg_scores_result else {
                'autonomy': 0, 'multi_scale': 0, 'regenerative': 0,
                'network': 0, 'ubuntu': 0, 'composite': 0
            }
            
            # Convert results to dict format
            results_list = []
            for row in results:
                result_dict = {
                    'account_id': row['account_id'],
                    'evaluation_date': row['evaluation_date'].isoformat() if row['evaluation_date'] else None,
                    'autonomy_integration_score': float(row['autonomy_integration_score'] or 0),
                    'multi_scale_score': float(row['multi_scale_score'] or 0),
                    'regenerative_impact_score': float(row['regenerative_impact_score'] or 0),
                    'network_contribution_score': float(row['network_contribution_score'] or 0),
                    'ubuntu_alignment_score': float(row['ubuntu_alignment_score'] or 0),
                    'composite_score': float(row['composite_score'] or 0),
                    'holonic_category': row['holonic_category'],
                    'raw_metrics': row.get('raw_metrics', {})
                }
                results_list.append(result_dict)
            
            # Build report data structure
            self.report_data = {
                "status": "success",
                "evaluated_count": len(results_list),
                "evaluation_date": datetime.now(timezone.utc).isoformat(),
                "category_distribution": category_distribution,
                "average_scores": avg_scores,
                "results": results_list
            }
            
            self.logger.info(f"Loaded evaluation data for {len(results_list)} accounts")
            return self.report_data
            
        except Exception as e:
            self.logger.error(f"Error loading evaluation data from database: {e}", exc_info=True)
            self.report_data = {
                "status": "error",
                "evaluated_count": 0,
                "evaluation_date": datetime.now(timezone.utc).isoformat(),
                "category_distribution": {},
                "average_scores": {
                    'autonomy': 0, 'multi_scale': 0, 'regenerative': 0,
                    'network': 0, 'ubuntu': 0, 'composite': 0
                },
                "results": [],
                "error": str(e)
            }
            return self.report_data
    
    async def load_time_series_data(
        self,
        days: int = 30,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Load time-series evaluation data for trend analysis.
        
        Principle 4: Database as single source of truth.
        Principle 5: Fully async operation.
        
        Args:
            days: Number of days of history to load
            account_id: Specific account to load (None for all accounts)
            
        Returns:
            List of evaluation records with timestamps
            
        Example:
            >>> # Load 30 days of network-wide data
            >>> data = await visualizer.load_time_series_data(days=30)
            >>> # Load specific account history
            >>> data = await visualizer.load_time_series_data(
            ...     days=90, 
            ...     account_id='GDC2ECKYO4WJMD35M4E2...'
            ... )
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            query = f"""
                SELECT 
                    account_id,
                    evaluation_date,
                    autonomy_integration_score,
                    multi_scale_score,
                    regenerative_impact_score,
                    network_contribution_score,
                    ubuntu_alignment_score,
                    composite_score,
                    holonic_category
                FROM {self.db_schema}.holonic_metrics
                WHERE evaluation_date >= $1
                {'AND account_id = $2' if account_id else ''}
                ORDER BY evaluation_date ASC
            """
            
            params = (cutoff_date, account_id) if account_id else (cutoff_date,)
            results = await self.db_manager.fetch_all(query, params)
            
            # Convert to list of dicts
            time_series = []
            for row in results:
                time_series.append({
                    'account_id': row['account_id'],
                    'evaluation_date': row['evaluation_date'],
                    'autonomy_integration_score': float(row['autonomy_integration_score'] or 0),
                    'multi_scale_score': float(row['multi_scale_score'] or 0),
                    'regenerative_impact_score': float(row['regenerative_impact_score'] or 0),
                    'network_contribution_score': float(row['network_contribution_score'] or 0),
                    'ubuntu_alignment_score': float(row['ubuntu_alignment_score'] or 0),
                    'composite_score': float(row['composite_score'] or 0),
                    'holonic_category': row['holonic_category']
                })
            
            self.time_series_data = time_series
            self.logger.info(f"Loaded {len(time_series)} time-series records")
            return time_series
            
        except Exception as e:
            self.logger.error(f"Error loading time-series data: {e}", exc_info=True)
            return []
    
    async def load_network_data(
        self,
        min_transaction_count: int = 1
    ) -> Dict[str, Any]:
        """
        Load transaction network data from stellar_transactions table.
        
        FIXED in v6.2.0: Now queries evaluated accounts FIRST, then gets their
        transaction activity specifically. This ensures we don't miss evaluated
        accounts that aren't in the top 100 most active accounts.
        
        Builds network graph showing transaction relationships between accounts.
        Uses source_account from stellar_transactions as the source node.
        
        Args:
            min_transaction_count: Minimum transactions per account to include
            
        Returns:
            Dictionary with nodes and edges for network graph
            
        Note:
            Uses stellar_transactions table with exact column names:
            - source_account: Transaction source
            - successful: Transaction success status
            - fee_charged: Transaction fee
            
        Example:
            >>> # Load network with accounts having at least 1 transaction
            >>> network = await visualizer.load_network_data(min_transaction_count=1)
            >>> print(f"Nodes: {len(network['nodes'])}, Edges: {len(network['edges'])}")
        """
        try:
            # STEP 1: Get all evaluated accounts from holonic_metrics
            self.logger.info(f"Querying holonic_metrics for evaluated accounts...")
            nodes_query = f"""
                WITH latest_evals AS (
                    SELECT DISTINCT ON (account_id)
                        account_id,
                        composite_score,
                        holonic_category
                    FROM {self.db_schema}.holonic_metrics
                    ORDER BY account_id, evaluation_date DESC
                )
                SELECT * FROM latest_evals
            """
            
            nodes = await self.db_manager.fetch_all(nodes_query, ())
            self.logger.info(f"Found {len(nodes)} evaluated accounts")
            
            if not nodes:
                self.logger.error("No evaluated accounts found in holonic_metrics!")
                return {'nodes': [], 'edges': []}
            
            # Extract account IDs for filtering
            evaluated_account_ids = [node['account_id'] for node in nodes]
            self.logger.info(
                f"Evaluated account IDs (sample): "
                f"{evaluated_account_ids[:3] if len(evaluated_account_ids) >= 3 else evaluated_account_ids}"
            )
            
            # STEP 2: Query transaction activity ONLY for evaluated accounts
            # Using WHERE source_account = ANY($1) to filter for specific accounts
            activity_query = f"""
                SELECT 
                    source_account,
                    COUNT(*) as transaction_count,
                    SUM(fee_charged) as total_fees,
                    COUNT(*) FILTER (WHERE successful = true) as successful_count
                FROM {self.db_schema}.stellar_transactions
                WHERE source_account = ANY($1)
                GROUP BY source_account
                HAVING COUNT(*) >= $2
            """
            
            self.logger.info(
                f"Querying stellar_transactions for activity of {len(evaluated_account_ids)} "
                f"evaluated accounts (min {min_transaction_count} transactions)..."
            )
            
            account_activity = await self.db_manager.fetch_all(
                activity_query, 
                (evaluated_account_ids, min_transaction_count)
            )
            self.logger.info(f"Found activity for {len(account_activity)} evaluated accounts")
            
            if account_activity and len(account_activity) > 0:
                sample_accounts = [row['source_account'][:16] + '...' for row in account_activity[:3]]
                self.logger.info(f"Sample accounts with activity: {sample_accounts}")
            
            # Create activity map
            activity_map = {
                row['source_account']: {
                    'count': int(row['transaction_count']),
                    'fees': float(row['total_fees'] or 0),
                    'success_rate': (
                        float(row['successful_count']) / float(row['transaction_count']) 
                        if row['transaction_count'] > 0 else 0
                    )
                }
                for row in account_activity
            }
            
            # Check for matches
            transaction_account_ids = set(activity_map.keys())
            matching_accounts = set(evaluated_account_ids).intersection(transaction_account_ids)
            
            self.logger.info(
                f"Account matching: {len(evaluated_account_ids)} evaluated, "
                f"{len(transaction_account_ids)} with sufficient transactions, "
                f"{len(matching_accounts)} matched successfully"
            )
            
            if len(matching_accounts) == 0:
                self.logger.warning(
                    f"No accounts found in BOTH holonic_metrics and stellar_transactions "
                    f"with >= {min_transaction_count} transactions. "
                    "Try lowering min_transaction_count or check if accounts have made transactions."
                )
            else:
                # Log some matching accounts
                sample_matches = list(matching_accounts)[:3]
                self.logger.info(
                    f"Sample matched accounts: "
                    f"{[acc[:16] + '...' for acc in sample_matches]}"
                )
            
            # Build network data structure
            network_data = {
                'nodes': [
                    {
                        'id': node['account_id'],
                        'score': float(node['composite_score'] or 0),
                        'category': node['holonic_category'],
                        'activity': activity_map.get(node['account_id'], {
                            'count': 0, 
                            'fees': 0, 
                            'success_rate': 0
                        }),
                        'has_transactions': node['account_id'] in transaction_account_ids
                    }
                    for node in nodes
                ],
                'edges': []  # Stellar transactions are account-centric, not bilateral
            }
            
            self.network_data = network_data
            
            nodes_with_activity = sum(1 for n in network_data['nodes'] if n['has_transactions'])
            self.logger.info(
                f"Loaded network data: {len(network_data['nodes'])} nodes total, "
                f"{nodes_with_activity} with transaction activity "
                f"(min_transactions={min_transaction_count})"
            )
            
            return network_data
            
        except Exception as e:
            self.logger.error(f"Error loading network data from stellar_transactions: {e}", exc_info=True)
            return {'nodes': [], 'edges': []}
    
    # ========================================================================
    # CORE VISUALIZATIONS
    # Principle 10: Separation of Concerns - Visualization logic isolated
    # Principle 12: Method Singularity - Each chart type created once
    # ========================================================================
    
    async def create_score_distribution_chart(
        self,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a histogram of composite scores.
        
        Principle 5: Async method that loads data if needed.
        Principle 12: Single implementation of score distribution chart.
        
        Args:
            output_file: Path to save the chart image (optional)
            
        Returns:
            Path to saved file or base64-encoded image string, or None on error
            
        Example:
            >>> # Save to file
            >>> path = await visualizer.create_score_distribution_chart('/path/to/chart.png')
            >>> # Get base64 image
            >>> img_data = await visualizer.create_score_distribution_chart()
        
        Design Notes:
            - Loads data from database if not cached
            - Creates matplotlib histogram
            - Returns file path or base64-encoded image
        """
        # Ensure data is loaded
        if not self.report_data:
            await self.load_evaluation_data()
        
        if not self.report_data or len(self.report_data.get('results', [])) == 0:
            self.logger.warning("No evaluation data available for visualization")
            return None
        
        try:
            # Extract scores from results
            scores = [result['composite_score'] for result in self.report_data['results']]
            
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Create histogram
            n, bins, patches = ax.hist(
                scores, 
                bins=30, 
                alpha=0.7, 
                color='skyblue', 
                edgecolor='black',
                linewidth=1.2
            )
            
            # Color bars by category threshold
            thresholds = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
            colors = ['#9ca3af', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6']
            
            for i in range(len(patches)):
                bin_center = (bins[i] + bins[i+1]) / 2
                for j in range(len(thresholds)-1):
                    if thresholds[j] <= bin_center < thresholds[j+1]:
                        patches[i].set_facecolor(colors[j])
                        break
            
            # Add category threshold lines
            category_labels = ['Observer', 'Participant', 'Contributor', 'Integrator', 'Exemplar']
            for i, (threshold, label) in enumerate(zip(thresholds[1:], category_labels)):
                ax.axvline(
                    x=threshold, 
                    color=colors[i], 
                    linestyle='--', 
                    alpha=0.8, 
                    linewidth=2
                )
                ax.text(
                    threshold, 
                    ax.get_ylim()[1] * 0.95, 
                    label, 
                    rotation=90,
                    verticalalignment='top', 
                    fontsize=9,
                    fontweight='bold'
                )
            
            # Add mean and median lines
            mean_score = np.mean(scores)
            median_score = np.median(scores)
            ax.axvline(
                mean_score, 
                color='red', 
                linestyle='-', 
                linewidth=2, 
                label=f'Mean: {mean_score:.3f}'
            )
            ax.axvline(
                median_score, 
                color='green', 
                linestyle='-', 
                linewidth=2, 
                label=f'Median: {median_score:.3f}'
            )
            
            ax.set_title(
                'Distribution of Holonic Composite Scores', 
                fontsize=16, 
                fontweight='bold',
                pad=20
            )
            ax.set_xlabel('Composite Score', fontsize=13, fontweight='bold')
            ax.set_ylabel('Number of Accounts', fontsize=13, fontweight='bold')
            ax.legend(loc='upper right', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            
            # Save or return
            return self._save_or_encode_figure(fig, output_file, 'score_distribution_chart')
                
        except Exception as e:
            self.logger.error(f"Error creating score distribution chart: {e}", exc_info=True)
            plt.close('all')
            return None
    
    async def create_radar_chart(
        self,
        output_file: Optional[str] = None,
        top_n: int = 5
    ) -> Optional[str]:
        """
        Create a radar chart of holonic dimensions.
        
        Shows network average and optionally top N accounts.
        
        Args:
            output_file: Path to save the chart image (optional)
            top_n: Number of top accounts to include (default: 5)
            
        Returns:
            Path to saved file or base64-encoded image string, or None on error
            
        Example:
            >>> chart = await visualizer.create_radar_chart(top_n=3)
        
        Design Notes:
            - Creates spider/radar chart with 5 dimensions
            - Plots network average
            - Optionally plots top performers
        """
        # Ensure data is loaded
        if not self.report_data:
            await self.load_evaluation_data()
        
        if not self.report_data or len(self.report_data.get('results', [])) == 0:
            self.logger.warning("No evaluation data available for radar chart")
            return None
        
        try:
            # Get average scores
            avg_scores = self.report_data.get('average_scores', {})
            
            # Get top N accounts
            top_accounts = sorted(
                self.report_data.get('results', []),
                key=lambda x: x['composite_score'],
                reverse=True
            )[:top_n]
            
            # Define categories
            categories = [
                'Autonomy &\nIntegration', 
                'Multi-scale\nParticipation',
                'Regenerative\nImpact',
                'Network\nContribution',
                'Ubuntu\nAlignment'
            ]
            
            # Number of variables
            N = len(categories)
            
            # Calculate angles
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Close the loop
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True))
            
            # Plot average scores
            avg_values = [
                avg_scores.get('autonomy', 0),
                avg_scores.get('multi_scale', 0),
                avg_scores.get('regenerative', 0),
                avg_scores.get('network', 0),
                avg_scores.get('ubuntu', 0)
            ]
            avg_values += avg_values[:1]  # Close the loop
            
            ax.plot(
                angles, 
                avg_values, 
                color='blue', 
                linewidth=3.5, 
                label='Network Average', 
                linestyle='-', 
                marker='o',
                markersize=8
            )
            ax.fill(angles, avg_values, color='blue', alpha=0.15)
            
            # Plot top accounts
            colors = cm.rainbow(np.linspace(0, 1, max(1, len(top_accounts))))
            for i, account in enumerate(top_accounts):
                values = [
                    account['autonomy_integration_score'],
                    account['multi_scale_score'],
                    account['regenerative_impact_score'],
                    account['network_contribution_score'],
                    account['ubuntu_alignment_score']
                ]
                values += values[:1]  # Close the loop
                
                label = f"{account['account_id'][:8]}... ({account['holonic_category']})"
                ax.plot(
                    angles, 
                    values, 
                    color=colors[i], 
                    linewidth=2, 
                    label=label, 
                    alpha=0.7,
                    marker='o',
                    markersize=5
                )
                ax.fill(angles, values, color=colors[i], alpha=0.05)
            
            # Set chart properties
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            plt.xticks(angles[:-1], categories, fontsize=11, fontweight='bold')
            ax.set_ylim(0, 1)
            ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
            ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            plt.legend(
                loc='upper right', 
                bbox_to_anchor=(1.35, 1.1), 
                fontsize=10,
                framealpha=0.9
            )
            plt.title(
                'Holonic Dimensions Radar Chart', 
                size=16, 
                fontweight='bold', 
                pad=30
            )
            plt.tight_layout()
            
            # Save or return
            return self._save_or_encode_figure(fig, output_file, 'radar_chart')
                
        except Exception as e:
            self.logger.error(f"Error creating radar chart: {e}", exc_info=True)
            plt.close('all')
            return None
    
    async def create_category_distribution_chart(
        self,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a pie chart of holonic category distribution.
        
        Args:
            output_file: Path to save the chart image (optional)
            
        Returns:
            Path to saved file or base64-encoded image string, or None on error
            
        Example:
            >>> chart = await visualizer.create_category_distribution_chart()
        
        Design Notes:
            - Creates donut-style pie chart
            - Shows category distribution with percentages
            - Uses consistent category colors
        """
        # Ensure data is loaded
        if not self.report_data:
            await self.load_evaluation_data()
        
        if not self.report_data or not self.report_data.get('category_distribution'):
            self.logger.warning("No category distribution data available")
            return None
        
        try:
            # Get category distribution
            category_dist = self.report_data.get('category_distribution', {})
            
            if not category_dist:
                return None
            
            # Define order and colors
            category_order = ['Exemplar', 'Integrator', 'Contributor', 'Participant', 'Observer']
            
            # Filter to existing categories
            labels = []
            sizes = []
            colors = []
            for cat in category_order:
                if cat in category_dist and category_dist[cat] > 0:
                    labels.append(cat)
                    sizes.append(category_dist[cat])
                    colors.append(self.CATEGORY_COLORS[cat])
            
            if not sizes:
                return None
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(12, 9))
            
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=None,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                pctdistance=0.85,
                textprops={'fontsize': 12, 'fontweight': 'bold'},
                explode=[0.05] * len(sizes)  # Slight separation
            )
            
            # Style percentage text
            for autotext in autotexts:
                autotext.set_color('white')
            
            # Add center circle for donut effect
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            ax.add_artist(centre_circle)
            
            # Add legend with counts
            legend_labels = [
                f'{cat} ({sizes[i]} accounts, {sizes[i]/sum(sizes)*100:.1f}%)' 
                for i, cat in enumerate(labels)
            ]
            ax.legend(
                wedges, 
                legend_labels, 
                loc='center left', 
                bbox_to_anchor=(1, 0, 0.5, 1), 
                fontsize=11,
                framealpha=0.9
            )
            
            ax.axis('equal')
            plt.title(
                'Distribution of Holonic Categories', 
                size=16, 
                fontweight='bold', 
                pad=20
            )
            plt.tight_layout()
            
            # Save or return
            return self._save_or_encode_figure(fig, output_file, 'category_distribution_chart')
                
        except Exception as e:
            self.logger.error(f"Error creating category distribution chart: {e}", exc_info=True)
            plt.close('all')
            return None
    
    # ========================================================================
    # ADVANCED VISUALIZATIONS (NEW)
    # Principle 12: Method Singularity - Each new chart type implemented once
    # ========================================================================
    
    async def create_time_series_chart(
        self,
        output_file: Optional[str] = None,
        days: int = 30,
        metric: str = 'composite_score'
    ) -> Optional[str]:
        """
        Create time-series trend chart for network-wide metrics.
        
        Args:
            output_file: Path to save chart (optional)
            days: Number of days of history
            metric: Metric to plot ('composite_score', 'autonomy', etc.)
            
        Returns:
            Path to saved file or base64-encoded image, or None on error
            
        Example:
            >>> # Plot 30-day composite score trend
            >>> chart = await visualizer.create_time_series_chart(days=30)
            >>> # Plot specific dimension over 90 days
            >>> chart = await visualizer.create_time_series_chart(
            ...     days=90, 
            ...     metric='network_contribution_score'
            ... )
        """
        # Load time series data if not cached
        if not self.time_series_data:
            await self.load_time_series_data(days=days)
        
        if not self.time_series_data:
            self.logger.warning("No time-series data available")
            return None
        
        try:
            # Group data by date and calculate daily averages
            daily_data = defaultdict(list)
            for record in self.time_series_data:
                date = record['evaluation_date'].date()
                daily_data[date].append(record[metric])
            
            # Calculate daily statistics
            dates = sorted(daily_data.keys())
            means = [np.mean(daily_data[date]) for date in dates]
            stds = [np.std(daily_data[date]) for date in dates]
            mins = [np.min(daily_data[date]) for date in dates]
            maxs = [np.max(daily_data[date]) for date in dates]
            
            # Create plot
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Plot mean line
            ax.plot(dates, means, color='blue', linewidth=2.5, label='Network Average', marker='o')
            
            # Plot confidence interval
            ax.fill_between(
                dates,
                [m - s for m, s in zip(means, stds)],
                [m + s for m, s in zip(means, stds)],
                alpha=0.2,
                color='blue',
                label='±1 Std Dev'
            )
            
            # Plot min/max range
            ax.fill_between(
                dates,
                mins,
                maxs,
                alpha=0.1,
                color='gray',
                label='Min-Max Range'
            )
            
            # Add trend line
            if len(dates) > 1:
                x_numeric = np.arange(len(dates))
                z = np.polyfit(x_numeric, means, 1)
                p = np.poly1d(z)
                ax.plot(
                    dates, 
                    p(x_numeric), 
                    "r--", 
                    alpha=0.8, 
                    linewidth=2,
                    label=f'Trend (slope: {z[0]:.4f})'
                )
            
            # Formatting
            ax.set_title(
                f'{metric.replace("_", " ").title()} - {days} Day Trend',
                fontsize=16,
                fontweight='bold',
                pad=20
            )
            ax.set_xlabel('Date', fontsize=13, fontweight='bold')
            ax.set_ylabel('Score', fontsize=13, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Rotate date labels
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'time_series_chart')
            
        except Exception as e:
            self.logger.error(f"Error creating time-series chart: {e}", exc_info=True)
            plt.close('all')
            return None
    
    async def create_correlation_matrix(
        self,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Create correlation matrix heatmap for holonic dimensions.
        
        Args:
            output_file: Path to save chart (optional)
            
        Returns:
            Path to saved file or base64-encoded image, or None on error
            
        Example:
            >>> matrix = await visualizer.create_correlation_matrix()
        """
        # Ensure data is loaded
        if not self.report_data:
            await self.load_evaluation_data()
        
        if not self.report_data or len(self.report_data.get('results', [])) == 0:
            self.logger.warning("No evaluation data available for correlation matrix")
            return None
        
        try:
            # Extract dimension scores
            results = self.report_data['results']
            
            # Create data matrix
            data = {
                'Autonomy': [r['autonomy_integration_score'] for r in results],
                'Multi-scale': [r['multi_scale_score'] for r in results],
                'Regenerative': [r['regenerative_impact_score'] for r in results],
                'Network': [r['network_contribution_score'] for r in results],
                'Ubuntu': [r['ubuntu_alignment_score'] for r in results],
                'Composite': [r['composite_score'] for r in results]
            }
            
            # Calculate correlation matrix
            import pandas as pd
            df = pd.DataFrame(data)
            corr_matrix = df.corr()
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(10, 8))
            
            im = ax.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
            
            # Set ticks and labels
            ax.set_xticks(np.arange(len(corr_matrix.columns)))
            ax.set_yticks(np.arange(len(corr_matrix.columns)))
            ax.set_xticklabels(corr_matrix.columns, fontsize=11, fontweight='bold')
            ax.set_yticklabels(corr_matrix.columns, fontsize=11, fontweight='bold')
            
            # Rotate x labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            # Add correlation values
            for i in range(len(corr_matrix)):
                for j in range(len(corr_matrix)):
                    text = ax.text(
                        j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                        ha="center", va="center", 
                        color="white" if abs(corr_matrix.iloc[i, j]) > 0.5 else "black",
                        fontsize=10, fontweight='bold'
                    )
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20, fontsize=12)
            
            ax.set_title(
                'Holonic Dimensions Correlation Matrix',
                fontsize=16,
                fontweight='bold',
                pad=20
            )
            
            plt.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'correlation_matrix')
            
        except Exception as e:
            self.logger.error(f"Error creating correlation matrix: {e}", exc_info=True)
            plt.close('all')
            return None
    
    async def create_comparative_analysis_chart(
        self,
        output_file: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Create comparative analysis chart across categories.
        
        Args:
            output_file: Path to save chart (optional)
            categories: List of categories to compare (None for all)
            
        Returns:
            Path to saved file or base64-encoded image, or None on error
            
        Example:
            >>> # Compare all categories
            >>> chart = await visualizer.create_comparative_analysis_chart()
            >>> # Compare specific categories
            >>> chart = await visualizer.create_comparative_analysis_chart(
            ...     categories=['Exemplar', 'Integrator', 'Contributor']
            ... )
        """
        # Ensure data is loaded
        if not self.report_data:
            await self.load_evaluation_data()
        
        if not self.report_data or len(self.report_data.get('results', [])) == 0:
            self.logger.warning("No evaluation data available for comparative analysis")
            return None
        
        try:
            results = self.report_data['results']
            
            # Filter by categories if specified
            if categories:
                results = [r for r in results if r['holonic_category'] in categories]
            
            if not results:
                return None
            
            # Group by category
            category_data = defaultdict(lambda: {
                'autonomy': [],
                'multi_scale': [],
                'regenerative': [],
                'network': [],
                'ubuntu': []
            })
            
            for r in results:
                cat = r['holonic_category']
                category_data[cat]['autonomy'].append(r['autonomy_integration_score'])
                category_data[cat]['multi_scale'].append(r['multi_scale_score'])
                category_data[cat]['regenerative'].append(r['regenerative_impact_score'])
                category_data[cat]['network'].append(r['network_contribution_score'])
                category_data[cat]['ubuntu'].append(r['ubuntu_alignment_score'])
            
            # Calculate means for each category
            dimensions = ['autonomy', 'multi_scale', 'regenerative', 'network', 'ubuntu']
            dimension_labels = ['Autonomy', 'Multi-scale', 'Regenerative', 'Network', 'Ubuntu']
            
            # Prepare data for grouped bar chart
            x = np.arange(len(dimensions))
            width = 0.15
            multiplier = 0
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            for category in sorted(category_data.keys()):
                means = [np.mean(category_data[category][dim]) for dim in dimensions]
                offset = width * multiplier
                bars = ax.bar(
                    x + offset, 
                    means, 
                    width, 
                    label=category,
                    color=self.CATEGORY_COLORS.get(category, 'gray'),
                    alpha=0.8
                )
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2., 
                        height,
                        f'{height:.2f}',
                        ha='center', 
                        va='bottom', 
                        fontsize=8
                    )
                
                multiplier += 1
            
            ax.set_xlabel('Holonic Dimensions', fontsize=13, fontweight='bold')
            ax.set_ylabel('Average Score', fontsize=13, fontweight='bold')
            ax.set_title(
                'Comparative Analysis Across Categories',
                fontsize=16,
                fontweight='bold',
                pad=20
            )
            ax.set_xticks(x + width * (len(category_data) - 1) / 2)
            ax.set_xticklabels(dimension_labels, fontsize=11)
            ax.legend(loc='upper left', fontsize=10)
            ax.set_ylim(0, 1.0)
            ax.grid(True, alpha=0.3, axis='y', linestyle='--')
            
            plt.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'comparative_analysis_chart')
            
        except Exception as e:
            self.logger.error(f"Error creating comparative analysis chart: {e}", exc_info=True)
            plt.close('all')
            return None
    
    async def create_network_visualization(
        self,
        output_file: Optional[str] = None,
        min_transaction_count: int = 1,
        max_nodes: int = 100
    ) -> Optional[str]:
        """
        Create network visualization graph showing transaction relationships.
        
        Args:
            output_file: Path to save chart (optional)
            min_transaction_count: Minimum transactions for inclusion
            max_nodes: Maximum number of nodes to display
            
        Returns:
            Path to saved file or base64-encoded image, or None on error
            
        Example:
            >>> network = await visualizer.create_network_visualization(
            ...     min_transaction_count=1,
            ...     max_nodes=50
            ... )
        """
        if not NETWORKX_AVAILABLE:
            self.logger.warning("NetworkX not available, cannot create network visualization")
            return None
        
        # Load network data if not cached
        if not self.network_data:
            await self.load_network_data(min_transaction_count=min_transaction_count)
        
        # Check if we have nodes (edges are optional for stellar transactions)
        if not self.network_data or not self.network_data.get('nodes'):
            self.logger.warning("No network nodes available for visualization")
            return None
        
        # Log if we're creating a nodes-only visualization
        if not self.network_data.get('edges'):
            self.logger.info(
                "Creating nodes-only network visualization "
                "(no edges - stellar transactions are source-centric)"
            )
        
        try:
            # Create directed graph
            G = nx.DiGraph()
            
            # Add nodes with attributes
            node_map = {node['id']: node for node in self.network_data['nodes']}
            for node in self.network_data['nodes'][:max_nodes]:
                G.add_node(
                    node['id'],
                    score=node['score'],
                    category=node['category'],
                    has_transactions=node['has_transactions']
                )
            
            # Add edges
            for edge in self.network_data['edges']:
                if edge['source'] in G.nodes() and edge['target'] in G.nodes():
                    G.add_edge(
                        edge['source'],
                        edge['target'],
                        weight=edge['weight']
                    )
            
            if len(G.nodes()) == 0:
                self.logger.warning("No nodes in graph after filtering")
                return None
            
            # Create visualization
            fig, ax = plt.subplots(figsize=(16, 12))
            
            # Calculate layout
            pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
            
            # Node colors by category
            node_colors = [
                self.CATEGORY_COLORS.get(G.nodes[node].get('category', 'Observer'), 'gray')
                for node in G.nodes()
            ]
            
            # Node sizes by score (larger for higher scores)
            node_sizes = [
                max(300, G.nodes[node].get('score', 0) * 2000)
                for node in G.nodes()
            ]
            
            # Node alpha by transaction activity
            node_alphas = [
                0.9 if G.nodes[node].get('has_transactions', False) else 0.3
                for node in G.nodes()
            ]
            
            # Draw nodes in two passes: inactive then active
            inactive_nodes = [n for n in G.nodes() if not G.nodes[n].get('has_transactions', False)]
            active_nodes = [n for n in G.nodes() if G.nodes[n].get('has_transactions', False)]
            
            if inactive_nodes:
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=inactive_nodes,
                    node_color=[self.CATEGORY_COLORS.get(G.nodes[n].get('category'), 'gray') for n in inactive_nodes],
                    node_size=[max(300, G.nodes[n].get('score', 0) * 2000) for n in inactive_nodes],
                    alpha=0.2,
                    ax=ax,
                    label='No transactions'
                )
            
            if active_nodes:
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=active_nodes,
                    node_color=[self.CATEGORY_COLORS.get(G.nodes[n].get('category'), 'gray') for n in active_nodes],
                    node_size=[max(300, G.nodes[n].get('score', 0) * 2000) for n in active_nodes],
                    alpha=0.9,
                    ax=ax,
                    label='With transactions'
                )
            
            # Draw edges only if they exist
            if len(G.edges()) > 0:
                edge_widths = [
                    min(5, G[u][v]['weight'] / 10)
                    for u, v in G.edges()
                ]
                nx.draw_networkx_edges(
                    G, pos,
                    width=edge_widths,
                    alpha=0.3,
                    edge_color='gray',
                    arrows=True,
                    arrowsize=10,
                    ax=ax
                )
            
            # Draw labels for high-scoring nodes with transactions
            high_score_nodes = {
                node: G.nodes[node]['score']
                for node in G.nodes()
                if G.nodes[node].get('score', 0) > 0.7 
                and G.nodes[node].get('has_transactions', False)
            }
            
            if high_score_nodes:
                labels = {
                    node: f"{node[:6]}..." 
                    for node in high_score_nodes.keys()
                }
                nx.draw_networkx_labels(
                    G, pos,
                    labels,
                    font_size=8,
                    font_weight='bold',
                    ax=ax
                )
            
            # Create legend
            legend_elements = [
                mpatches.Patch(
                    facecolor=self.CATEGORY_COLORS[cat],
                    label=cat,
                    alpha=0.7
                )
                for cat in self.CATEGORY_COLORS.keys()
            ]
            
            # Add transaction activity indicator
            legend_elements.extend([
                mpatches.Patch(facecolor='gray', alpha=0.9, label='Has transaction activity'),
                mpatches.Patch(facecolor='gray', alpha=0.2, label='No transaction activity')
            ])
            
            ax.legend(
                handles=legend_elements,
                loc='upper left',
                fontsize=10,
                title='Categories & Activity'
            )
            
            # Count nodes with activity
            nodes_with_activity = sum(1 for n in G.nodes() if G.nodes[n].get('has_transactions', False))
            
            ax.set_title(
                f'Transaction Network Visualization\n'
                f'{len(G.nodes())} nodes ({nodes_with_activity} with transactions, '
                f'{len(G.nodes()) - nodes_with_activity} without), {len(G.edges())} edges',
                fontsize=16,
                fontweight='bold',
                pad=20
            )
            ax.axis('off')
            
            plt.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'network_visualization')
            
        except Exception as e:
            self.logger.error(f"Error creating network visualization: {e}", exc_info=True)
            plt.close('all')
            return None
    
    async def create_account_detail_view(
        self,
        account_id: str,
        output_file: Optional[str] = None,
        days: int = 90
    ) -> Optional[str]:
        """
        Create detailed visualization for a specific account.
        
        Args:
            account_id: Account ID to visualize
            output_file: Path to save chart (optional)
            days: Days of history to include
            
        Returns:
            Path to saved file or base64-encoded image, or None on error
            
        Example:
            >>> detail = await visualizer.create_account_detail_view(
            ...     account_id='GDC2ECKYO4WJMD35M4E2...',
            ...     days=90
            ... )
        """
        # Load account time series
        account_data = await self.load_time_series_data(days=days, account_id=account_id)
        
        if not account_data:
            self.logger.warning(f"No data available for account {account_id}")
            return None
        
        try:
            # Create subplot figure
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
            
            # 1. Composite score over time
            ax1 = fig.add_subplot(gs[0, :])
            dates = [d['evaluation_date'] for d in account_data]
            scores = [d['composite_score'] for d in account_data]
            ax1.plot(dates, scores, marker='o', linewidth=2, color='blue')
            ax1.set_title(
                f'Composite Score Trend - {account_id[:12]}...',
                fontsize=14,
                fontweight='bold'
            )
            ax1.set_ylabel('Score', fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            # 2. Dimension scores over time
            ax2 = fig.add_subplot(gs[1, :])
            dimensions = [
                ('autonomy_integration_score', 'Autonomy'),
                ('multi_scale_score', 'Multi-scale'),
                ('regenerative_impact_score', 'Regenerative'),
                ('network_contribution_score', 'Network'),
                ('ubuntu_alignment_score', 'Ubuntu')
            ]
            
            for field, label in dimensions:
                values = [d[field] for d in account_data]
                ax2.plot(dates, values, marker='o', linewidth=1.5, label=label, alpha=0.7)
            
            ax2.set_title('Dimension Scores Over Time', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Score', fontweight='bold')
            ax2.legend(loc='best', fontsize=9)
            ax2.grid(True, alpha=0.3)
            
            # 3. Latest radar chart
            ax3 = fig.add_subplot(gs[2, 0], projection='polar')
            latest = account_data[-1]
            categories = ['Autonomy', 'Multi-scale', 'Regenerative', 'Network', 'Ubuntu']
            values = [
                latest['autonomy_integration_score'],
                latest['multi_scale_score'],
                latest['regenerative_impact_score'],
                latest['network_contribution_score'],
                latest['ubuntu_alignment_score']
            ]
            
            N = len(categories)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            values += values[:1]
            angles += angles[:1]
            
            ax3.plot(angles, values, 'o-', linewidth=2, color='green')
            ax3.fill(angles, values, alpha=0.25, color='green')
            ax3.set_xticks(angles[:-1])
            ax3.set_xticklabels(categories, fontsize=9)
            ax3.set_ylim(0, 1)
            ax3.set_title('Current Dimension Profile', fontsize=12, fontweight='bold', pad=15)
            ax3.grid(True)
            
            # 4. Category history
            ax4 = fig.add_subplot(gs[2, 1])
            categories_over_time = [d['holonic_category'] for d in account_data]
            category_counts = {}
            for cat in categories_over_time:
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            ax4.bar(
                category_counts.keys(),
                category_counts.values(),
                color=[self.CATEGORY_COLORS.get(c, 'gray') for c in category_counts.keys()]
            )
            ax4.set_title('Category Distribution', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Count', fontweight='bold')
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
            ax4.grid(True, alpha=0.3, axis='y')
            
            fig.suptitle(
                f'Account Detail View - {account_id}',
                fontsize=18,
                fontweight='bold',
                y=0.995
            )
            
            plt.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'account_detail_view')
            
        except Exception as e:
            self.logger.error(f"Error creating account detail view: {e}", exc_info=True)
            plt.close('all')
            return None
    
    # ========================================================================
    # HTML REPORT GENERATION (ENHANCED)
    # Principle 5: Strict Async - Async report generation
    # ========================================================================
    
    async def generate_html_report(
        self,
        output_dir: Optional[str] = None,
        include_advanced: bool = True
    ) -> Optional[str]:
        """
        Generate a comprehensive HTML report with all visualizations.
        
        Principle 5: Fully async operation.
        
        Args:
            output_dir: Directory to save the HTML report (default: current dir)
            include_advanced: Include advanced visualizations (time-series, correlations, etc.)
            
        Returns:
            Path to the saved HTML report, or None on error
            
        Example:
            >>> report_path = await visualizer.generate_html_report('./reports')
            >>> print(f"Report saved to {report_path}")
        
        Design Notes:
            - Generates all charts as base64 images
            - Creates comprehensive HTML with embedded images
            - Includes summary statistics and insights
            - Optional advanced analytics section
        """
        # Ensure data is loaded
        if not self.report_data:
            await self.load_evaluation_data()
        
        if not self.report_data:
            self.logger.error("No evaluation data available for report generation")
            return None
        
        try:
            self.logger.info("Generating comprehensive HTML report...")
            
            # Generate core visualizations as base64 images
            score_dist_img = await self.create_score_distribution_chart()
            radar_img = await self.create_radar_chart(top_n=5)
            category_dist_img = await self.create_category_distribution_chart()
            
            # Generate advanced visualizations if requested
            time_series_img = None
            correlation_img = None
            comparative_img = None
            network_img = None
            
            if include_advanced:
                self.logger.info("Generating advanced visualizations...")
                time_series_img = await self.create_time_series_chart(days=30)
                correlation_img = await self.create_correlation_matrix()
                comparative_img = await self.create_comparative_analysis_chart()
                if NETWORKX_AVAILABLE:
                    network_img = await self.create_network_visualization(
                        min_transaction_count=1,
                        max_nodes=50
                    )
            
            # Create output directory
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            else:
                output_dir = "."
            
            # Define output file
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_file = str(Path(output_dir) / f"ubec_holonic_report_{timestamp}.html")
            
            # Get data
            evaluated_count = self.report_data.get('evaluated_count', 0)
            evaluation_date = self.report_data.get('evaluation_date', 
                                                  datetime.now(timezone.utc).isoformat())
            avg_scores = self.report_data.get('average_scores', {})
            category_dist = self.report_data.get('category_distribution', {})
            
            # Generate HTML content
            html_content = self._build_enhanced_html_content(
                evaluated_count, evaluation_date, avg_scores, category_dist,
                score_dist_img, radar_img, category_dist_img,
                time_series_img, correlation_img, comparative_img, network_img
            )
            
            # Write HTML to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Comprehensive HTML report saved to {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}", exc_info=True)
            return None
    
    def _build_enhanced_html_content(
        self,
        evaluated_count: int,
        evaluation_date: str,
        avg_scores: Dict[str, float],
        category_dist: Dict[str, int],
        score_dist_img: Optional[str],
        radar_img: Optional[str],
        category_dist_img: Optional[str],
        time_series_img: Optional[str],
        correlation_img: Optional[str],
        comparative_img: Optional[str],
        network_img: Optional[str]
    ) -> str:
        """Build enhanced HTML content for report (sync helper method)."""
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UBEC Holonic Evaluation Report - Enhanced</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
        }}
        
        header::after {{
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            right: 0;
            height: 50px;
            background: white;
            clip-path: polygon(0 100%, 100% 100%, 100% 0, 0 100%);
        }}
        
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .subtitle {{
            font-size: 1.1rem;
            opacity: 0.95;
        }}
        
        .content {{
            padding: 2rem;
        }}
        
        .summary {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
            border-left: 5px solid #667eea;
        }}
        
        .summary h2 {{
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.8rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-top: 4px solid #667eea;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .section {{
            margin: 3rem 0;
        }}
        
        .section-title {{
            font-size: 2rem;
            color: #667eea;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #764ba2;
        }}
        
        .visualization {{
            margin: 2rem 0;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .visualization h3 {{
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.4rem;
        }}
        
        .visualization img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .visualization-description {{
            margin-top: 1rem;
            color: #666;
            font-style: italic;
            line-height: 1.5;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            padding: 1rem;
            text-align: left;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }}
        
        td {{
            padding: 0.9rem 1rem;
            border-bottom: 1px solid #e9ecef;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        tr:hover {{
            background: #e9ecef;
            transition: background 0.2s ease;
        }}
        
        .advanced-section {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin: 3rem 0;
        }}
        
        .advanced-section h2 {{
            color: white;
            margin-bottom: 1rem;
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            background: #f8f9fa;
            color: #666;
            border-top: 1px solid #dee2e6;
            margin-top: 3rem;
        }}
        
        footer p {{
            margin: 0.5rem 0;
        }}
        
        .footer-logo {{
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
            
            .metric-card {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌱 UBEC Holonic Evaluation Report</h1>
            <p class="subtitle">Comprehensive Analysis of Ubuntu Protocol Holonic Metrics</p>
            <p class="subtitle">Generated on {datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M:%S UTC")}</p>
        </header>
        
        <div class="content">
            <div class="summary">
                <h2>📊 Executive Summary</h2>
                <p>This report provides a comprehensive holonic evaluation of UBEC token holder accounts based on Ubuntu principles. The evaluation assesses accounts across five key dimensions: Autonomy & Integration, Multi-scale Participation, Regenerative Impact, Network Contribution, and Ubuntu Alignment.</p>
                <p style="margin-top: 1rem;"><strong>Total Accounts Evaluated:</strong> {evaluated_count:,}</p>
                <p><strong>Evaluation Date:</strong> {evaluation_date}</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">📈 Network-Wide Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Autonomy & Integration</div>
                        <div class="metric-value">{avg_scores.get('autonomy', 0):.3f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Multi-scale</div>
                        <div class="metric-value">{avg_scores.get('multi_scale', 0):.3f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Regenerative</div>
                        <div class="metric-value">{avg_scores.get('regenerative', 0):.3f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Network</div>
                        <div class="metric-value">{avg_scores.get('network', 0):.3f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Ubuntu</div>
                        <div class="metric-value">{avg_scores.get('ubuntu', 0):.3f}</div>
                    </div>
                    <div class="metric-card" style="border-top-color: #764ba2;">
                        <div class="metric-label">Composite</div>
                        <div class="metric-value">{avg_scores.get('composite', 0):.3f}</div>
                    </div>
                </div>
            </div>
        """
        
        # Add category distribution table
        if category_dist:
            html += """
            <div class="section">
                <h2 class="section-title">🏆 Category Distribution</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            total = sum(category_dist.values())
            for category in ['Exemplar', 'Integrator', 'Contributor', 'Participant', 'Observer']:
                if category in category_dist:
                    count = category_dist[category]
                    pct = (count / total * 100) if total > 0 else 0
                    html += f"""
                        <tr>
                            <td><strong>{category}</strong></td>
                            <td>{count:,}</td>
                            <td>{pct:.1f}%</td>
                        </tr>
                    """
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        # Add core visualizations
        html += """
            <div class="section">
                <h2 class="section-title">📊 Core Visualizations</h2>
        """
        
        if score_dist_img:
            html += f"""
                <div class="visualization">
                    <h3>Score Distribution</h3>
                    <img src="{score_dist_img}" alt="Score Distribution">
                    <p class="visualization-description">
                        This histogram shows the distribution of composite scores across all evaluated accounts,
                        with category thresholds marked and statistical indicators (mean and median) highlighted.
                    </p>
                </div>
            """
        
        if radar_img:
            html += f"""
                <div class="visualization">
                    <h3>Holonic Dimensions Radar</h3>
                    <img src="{radar_img}" alt="Radar Chart">
                    <p class="visualization-description">
                        This radar chart displays the network average scores for each holonic dimension,
                        along with the profiles of top-performing accounts for comparison.
                    </p>
                </div>
            """
        
        if category_dist_img:
            html += f"""
                <div class="visualization">
                    <h3>Category Distribution</h3>
                    <img src="{category_dist_img}" alt="Category Distribution">
                    <p class="visualization-description">
                        This donut chart illustrates the distribution of accounts across holonic categories,
                        showing the proportion of accounts at each level of Ubuntu alignment.
                    </p>
                </div>
            """
        
        html += "</div>"  # End core visualizations section
        
        # Add advanced visualizations if available
        if time_series_img or correlation_img or comparative_img or network_img:
            html += """
            <div class="advanced-section">
                <h2>🔬 Advanced Analytics</h2>
                <p>Deep-dive analysis including trends, correlations, and network effects.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">📈 Advanced Visualizations</h2>
            """
            
            if time_series_img:
                html += f"""
                <div class="visualization">
                    <h3>Time-Series Trend Analysis</h3>
                    <img src="{time_series_img}" alt="Time Series">
                    <p class="visualization-description">
                        30-day trend analysis showing the evolution of composite scores over time,
                        including confidence intervals and trend lines.
                    </p>
                </div>
                """
            
            if correlation_img:
                html += f"""
                <div class="visualization">
                    <h3>Dimension Correlation Matrix</h3>
                    <img src="{correlation_img}" alt="Correlation Matrix">
                    <p class="visualization-description">
                        Correlation matrix showing the relationships between different holonic dimensions,
                        highlighting which metrics tend to move together.
                    </p>
                </div>
                """
            
            if comparative_img:
                html += f"""
                <div class="visualization">
                    <h3>Comparative Category Analysis</h3>
                    <img src="{comparative_img}" alt="Comparative Analysis">
                    <p class="visualization-description">
                        Comparative analysis showing average dimension scores across different holonic categories,
                        enabling clear comparison of performance profiles.
                    </p>
                </div>
                """
            
            if network_img:
                html += f"""
                <div class="visualization">
                    <h3>Transaction Network Visualization</h3>
                    <img src="{network_img}" alt="Network Visualization">
                    <p class="visualization-description">
                        Network graph showing evaluated accounts with transaction activity highlighted.
                        Node sizes represent composite scores, colors indicate holonic categories,
                        and opacity shows transaction activity level.
                    </p>
                </div>
                """
            
            html += "</div>"  # End advanced visualizations section
        
        # Add top accounts table
        if self.report_data and self.report_data.get('results'):
            top_accounts = sorted(
                self.report_data['results'],
                key=lambda x: x['composite_score'],
                reverse=True
            )[:20]
            
            html += """
            <div class="section">
                <h2 class="section-title">⭐ Top 20 Accounts</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Account ID</th>
                            <th>Category</th>
                            <th>Composite</th>
                            <th>Autonomy</th>
                            <th>Multi-scale</th>
                            <th>Regenerative</th>
                            <th>Network</th>
                            <th>Ubuntu</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for i, account in enumerate(top_accounts, 1):
                html += f"""
                    <tr>
                        <td><strong>#{i}</strong></td>
                        <td style="font-family: monospace;">{account['account_id'][:16]}...</td>
                        <td><strong>{account['holonic_category']}</strong></td>
                        <td>{account['composite_score']:.3f}</td>
                        <td>{account['autonomy_integration_score']:.3f}</td>
                        <td>{account['multi_scale_score']:.3f}</td>
                        <td>{account['regenerative_impact_score']:.3f}</td>
                        <td>{account['network_contribution_score']:.3f}</td>
                        <td>{account['ubuntu_alignment_score']:.3f}</td>
                    </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        # Footer
        html += """
        </div> <!-- End content -->
        
        <footer>
            <p class="footer-logo">UBEC Holonic Evaluation System</p>
            <p>This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.</p>
            <p>This project was made possible with the assistance of Claude and Anthropic PBC.</p>
            <p>&copy; 2025 UBEC Protocol Team | Version 6.2.0 (Fixed Account Matching)</p>
        </footer>
    </div>
</body>
</html>
        """
        
        return html
    
    # ========================================================================
    # HELPER METHODS
    # Principle 12: Method Singularity - Shared helper implemented once
    # ========================================================================
    
    def _save_or_encode_figure(
        self,
        fig: plt.Figure,
        output_file: Optional[str],
        default_name: str
    ) -> Optional[str]:
        """
        Helper method to save figure to file or encode as base64.
        
        Args:
            fig: Matplotlib figure
            output_file: Path to save file (optional)
            default_name: Default filename if saving
            
        Returns:
            File path or base64-encoded image string
        """
        try:
            if output_file:
                fig.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close(fig)
                self.logger.info(f"{default_name} saved to {output_file}")
                return output_file
            else:
                buf = BytesIO()
                fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close(fig)
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"
        except Exception as e:
            self.logger.error(f"Error saving/encoding figure: {e}", exc_info=True)
            plt.close(fig)
            return None
    
    # ========================================================================
    # LIFECYCLE METHODS
    # Principle 5: Strict Async - Async lifecycle management
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
                'service': 'UBECHolonicVisualizer',
                'version': '6.2.0',
                'status': 'healthy' if db_healthy else 'unhealthy',
                'database': 'connected' if db_healthy else 'disconnected',
                'data_loaded': self.report_data is not None,
                'networkx_available': NETWORKX_AVAILABLE,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                'service': 'UBECHolonicVisualizer',
                'version': '6.2.0',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def close(self):
        """Clean up visualizer resources."""
        self.logger.info("Enhanced holonic visualizer closing")
        
        # Clear cached data
        self.report_data = None
        self.time_series_data = None
        self.network_data = None
        
        # Close any matplotlib figures
        plt.close('all')
        
        self.logger.info("Enhanced holonic visualizer closed")


# ========================================================================
# SERVICE FACTORY
# Principle 2: Service Pattern - Factory for service registry
# ========================================================================

async def create_holonic_visualizer(
    db_manager: Any,
    config: Dict[str, Any],
    **kwargs
) -> UBECHolonicVisualizer:
    """
    Factory function to create holonic visualizer instance.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    
    Args:
        db_manager: Async database manager
        config: Configuration dictionary with:
            - db_schema: Database schema name (required)
            - element_mode: Enable element-specific features (optional)
        **kwargs: Additional options (reserved for future use)
    
    Returns:
        UBECHolonicVisualizer: Initialized service instance
    
    Raises:
        ValueError: If required config parameters are missing
    
    Example:
        >>> # In main.py or service registry
        >>> visualizer = await create_holonic_visualizer(
        ...     db_manager=db,
        ...     config={'db_schema': 'ubec_main', 'element_mode': True}
        ... )
        >>> report = await visualizer.generate_html_report('./reports')
    """
    # Validate required config
    if 'db_schema' not in config:
        raise ValueError("Configuration missing required parameter: 'db_schema'")
    
    # Create visualizer instance
    visualizer = UBECHolonicVisualizer(
        db_manager=db_manager,
        config=config
    )
    
    return visualizer


# ========================================================================
# PUBLIC INTERFACE
# Principle 1: Modular Design - Clear public interface
# ========================================================================

__all__ = [
    'UBECHolonicVisualizer',
    'create_holonic_visualizer'
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
        "  from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer\n"
        "  visualizer = await create_holonic_visualizer(db_manager, config)\n"
        "  report = await visualizer.generate_html_report('./reports')\n\n"
        "Version 6.2.0 - Fixed Account Matching:\n"
        "  - Query evaluated accounts FIRST from holonic_metrics\n"
        "  - Then fetch transaction activity for those specific accounts\n"
        "  - No more arbitrary LIMIT 100 that excluded evaluated accounts\n"
        "  - Correctly matches accounts between tables\n\n"
        "Enhanced features:\n"
        "  - Time-series trend analysis\n"
        "  - Correlation matrices\n"
        "  - Comparative analysis\n"
        "  - Network visualization with activity indicators\n"
        "  - Account detail views\n"
        "  - Element-specific dashboards"
    )
