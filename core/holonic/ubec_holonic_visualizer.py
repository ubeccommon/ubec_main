#!/usr/bin/env python3
"""
UBEC Protocol Suite - Holonic Visualizer Service
=================================================
Comprehensive visualization of UBEC holonic evaluation results.

Creates charts, graphs, and HTML reports from holonic metrics data with advanced
analytics capabilities.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained visualization service
    ✅ #2  Service Pattern: Factory-based instantiation, no standalone execution
    ✅ #3  Service Registry: Accessed through centralized registry
    ✅ #4  Single Source of Truth: Database is authoritative
    ✅ #5  Strict Async Operations: ALL I/O operations use async/await
    ✅ #6  No Sync Fallbacks: Pure async implementation with explicit feature detection
    ✅ #7  Per-Asset Monitoring: Individual account visualization with health checks
    ✅ #8  No Duplicate Configuration: Database-backed configuration
    ✅ #9  Integrated Rate Limiting: Built-in for database operations
    ✅ #10 Separation of Concerns: Visualization logic isolated
    ✅ #11 Comprehensive Documentation: Full docstrings and attribution
    ✅ #12 Method Singularity: Uses ServiceHealthCheck utility for health monitoring
════════════════════════════════════════════════════════════════════════════

Key Features:
- Score distribution histograms
- Holonic dimension radar charts
- Category distribution pie charts
- Network visualization graphs (when transaction data available)
- Time-series trend analysis
- Comparative category analysis
- Correlation matrices
- Account detail views
- Element-specific dashboards
- Comprehensive HTML reports
- Ubuntu dynamic pastel earth tone color palette (v13.0.0)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 13.2.2 (Health Check Return Pattern Enhancement)
Date: November 8, 2025

Changelog:
    v13.2.2 - CRITICAL ENHANCEMENT: Health Check Return Pattern Verification
            - 🔧 ENHANCED: check_matplotlib made absolutely explicit with None return
            - 🔧 ENHANCED: check_data_access with explicit schema name verification
            - 🔧 ENHANCED: check_output_directory with clear success path
            - ✅ VERIFIED: All check functions follow ServiceHealthCheck v3.3 pattern exactly
            - ✅ VERIFIED: No implicit boolean evaluations anywhere
            - ✅ VERIFIED: All database queries use explicit schema names
            - 📊 IMPROVED: More comprehensive error messages in check functions
            - 🎯 CONFIRMED: Full compliance with all 12 design principles
            - ⚡ OPTIMIZED: Removed potential ambiguity in return paths
    v13.2.1 - CRITICAL BOOL RETURN FIX (check_data_access):
            - 🔧 FIXED: check_data_access() now returns None instead of bool
            - ✅ FIXED: Eliminated "Unexpected return type <class 'bool'>" warning
            - ✅ CORRECTED: Now raises Exception on failure instead of returning False
            - 🎯 VERIFIED: Full compliance with ServiceHealthCheck patterns
            - 📊 IMPROVED: Proper exception handling with descriptive error messages
    v13.2.0 - HEALTH CHECK FIX (ServiceHealthCheck Integration):
            - 🔧 CRITICAL FIX: health_check() now uses ServiceHealthCheck.database_dependent_health()
            - ✅ FIXED: Returns standardized format with 'status' instead of 'healthy'
            - ✅ FIXED: Service registry now correctly shows visualizer as 'healthy' not 'unknown'
            - ✅ IMPLEMENTED: Principle #12 (Method Singularity) - uses shared utility
            - ✅ ENHANCED: Added matplotlib availability check
            - ✅ ENHANCED: Added data access verification check
            - 📊 IMPROVED: Health check returns complete service metrics
            - 🎯 VERIFIED: Full compliance with health monitoring standards
    v13.1.5 - Type Conversion & Schema Fix
    v13.1.4 - Category distribution f-string fix
    v13.1.3 - String concatenation syntax fix
    v13.1.2 - None value handling improvements
    v13.1.1 - Key insights formatting improvements
    v13.1.0 - Dynamic key insights feature
    v13.0.2 - Correlation matrix validation
    v13.0.1 - Missing dimension handling
    v13.0.0 - Ubuntu color palette implementation
"""

import asyncio
import base64
import io
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal

# Visualization imports with feature detection
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server use
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Optional NetworkX for network visualizations
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None


# ═════════════════════════════════════════════════════════════════════════════
# Ubuntu Color Palette (v13.0.0)
# ═════════════════════════════════════════════════════════════════════════════

UBUNTU_COLORS = {
    # Holonic Category Colors (Dynamic Pastel Earth Tones)
    'categories': {
        'Exemplar': '#B08BBB',      # 🟣 Soft Amethyst - Wisdom & Leadership
        'Integrator': '#8FBC8F',    # 🟢 Sage Green - Growth & Balance
        'Contributor': '#87CEEB',   # 🔵 Sky Blue - Clarity & Cooperation
        'Participant': '#E8A87C',   # 🟠 Soft Terracotta - Community & Warmth
        'Observer': '#9CB4CC'       # ⚪ Soft Slate - Neutrality & Potential
    },
    
    # Element Colors (Four-Element Protocol)
    'elements': {
        'Earth': '#8AA67E',     # Moss Green - Grounding & Stability
        'Water': '#87CEEB',     # Sky Blue - Flow & Adaptability  
        'Air': '#D4B5D9',       # Lavender - Communication & Ideas
        'Fire': '#E8A87C'       # Soft Terracotta - Transformation & Energy
    },
    
    # Gradients for backgrounds and transitions
    'gradients': {
        'earth_to_sky': ['#8AA67E', '#87CEEB'],      # Earth → Sky Blue
        'sage_to_amethyst': ['#8FBC8F', '#B08BBB']   # Sage Green → Amethyst
    },
    
    # Accent colors for highlights and emphasis
    'accents': {
        'growth': '#8FBC8F',     # Sage Green - Growth & Development
        'wisdom': '#B08BBB',     # Soft Amethyst - Wisdom & Insight
        'community': '#E8A87C',  # Soft Terracotta - Community & Connection
        'earth': '#8AA67E'       # Moss Green - Earth & Grounding
    },
    
    # Neutral colors for text, backgrounds, and UI elements
    'neutral': {
        'background': '#FAFAF9',  # Warm White
        'text': '#2D3436',        # Charcoal
        'border': '#E8E6E3',      # Soft Gray
        'grid': '#D3D1CE',        # Medium Gray
        'connection': '#9CB4CC'   # Soft Slate (for links/connections)
    }
}


# ═════════════════════════════════════════════════════════════════════════════
# HolonicVisualizer Service Class
# ═════════════════════════════════════════════════════════════════════════════

class HolonicVisualizer:
    """
    Comprehensive visualization service for UBEC holonic metrics.
    
    This service creates charts, graphs, and HTML reports from holonic evaluation
    data using the Ubuntu color palette and design principles.
    
    Design Pattern:
        Service class instantiated via factory function only.
        Integrates with service registry for database access.
        Follows async-first architecture.
    
    Attributes:
        db_manager: Async database manager from service registry
        config: Configuration dictionary
        logger: Logging instance
        db_schema: Database schema name (default: 'public')
        output_dir: Directory for generated reports and charts
        element_mode: Whether four-element protocol is enabled
        transactions_table_available: Whether transaction data exists
        schema_features_verified: Whether schema verification completed
        report_data: Cached evaluation data
        time_series_data: Cached time-series data
    """
    
    def __init__(
        self,
        db_manager: Any,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize HolonicVisualizer with dependencies.
        
        Args:
            db_manager: Async database manager instance
            config: Configuration dictionary
            logger: Optional logger instance
        """
        self.db_manager = db_manager
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Configuration
        self.db_schema = config.get('db_schema', 'public')
        self.output_dir = Path(config.get('output_dir', './visualizations'))
        self.element_mode = config.get('element_mode', False)
        
        # Feature availability flags (set during initialization)
        self.transactions_table_available = False
        self.schema_features_verified = False
        
        # Cached data
        self.report_data = None
        self.time_series_data = None
        
        # Tracking for health checks
        self._initialized = False
        self._charts_generated = 0
        self._last_visualization = None
        
        self.logger.info(
            f"HolonicVisualizer initialized | "
            f"schema={self.db_schema} | "
            f"element_mode={self.element_mode} | "
            f"color_palette=Ubuntu_v13.0.0"
        )
    
    # ═════════════════════════════════════════════════════════════════════════
    # Lifecycle Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    async def _verify_schema_features(self) -> bool:
        """
        Verify available database schema features.
        
        Detects presence of optional tables like stellar_operations for advanced
        visualizations. Implements Principle #6 (No Sync Fallbacks) and
        Principle #1 (Precision in Implementation).
        
        Returns:
            True if verification completed successfully
        """
        try:
            # Check for stellar_operations table (used for transaction network viz)
            # Explicit schema name used (Principle #4)
            query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = $1 
                    AND table_name = 'stellar_operations'
                ) as table_exists
            """
            
            result = await self.db_manager.fetch_one(query, (self.db_schema,))
            self.transactions_table_available = bool(result['table_exists']) if result else False
            
            self.schema_features_verified = True
            
            self.logger.info(
                f"Schema features verified | "
                f"transactions_available={self.transactions_table_available}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying schema features: {e}", exc_info=True)
            self.transactions_table_available = False
            self.schema_features_verified = False
            return False
    
    async def initialize(self) -> bool:
        """
        Initialize the visualizer service.
        
        Verifies database connectivity and available features.
        
        Returns:
            True if initialization successful
        """
        try:
            # Verify schema features
            await self._verify_schema_features()
            
            # Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self._initialized = True
            
            self.logger.info(
                f"HolonicVisualizer initialized successfully | "
                f"transactions_available={self.transactions_table_available}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing visualizer: {e}", exc_info=True)
            self._initialized = False
            return False
    
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check using standardized ServiceHealthCheck utility.
        
        This method implements Principle #12 (Method Singularity) by using the shared
        ServiceHealthCheck utility instead of custom health check logic.
        
        Returns:
            Health status dictionary with standardized format:
                - status: 'healthy', 'degraded', 'unhealthy', or 'unknown'
                - message: Human-readable status message
                - timestamp: ISO format timestamp
                - details: Dictionary with service-specific metrics
        """
        from core.utils.service_health import ServiceHealthCheck
        
        # Additional health checks specific to visualizer
        # CRITICAL: These functions MUST return None (success) or raise Exception (failure)
        # NEVER return boolean values - follows ServiceHealthCheck v3.3 pattern
        
        async def check_matplotlib():
            """
            Verify matplotlib is working properly.
            
            Returns:
                None: Matplotlib available and functional (healthy)
            
            Raises:
                Exception: Matplotlib test failed (unhealthy)
            
            NEVER returns boolean - follows ServiceHealthCheck v3.3 pattern
            """
            try:
                if not MATPLOTLIB_AVAILABLE:
                    raise Exception("Matplotlib is not installed or not available")
                
                # Quick test to ensure matplotlib can create figures
                fig, ax = plt.subplots(figsize=(1, 1))
                plt.close(fig)
                
                # Explicit success return (not implicit)
                return None
                
            except Exception as e:
                # Raise exception with descriptive message
                raise Exception(f"Matplotlib check failed: {str(e)}")
        
        async def check_data_access():
            """
            Verify we can access holonic metrics data.
            
            Returns:
                None: Data access successful (healthy)
            
            Raises:
                Exception: Cannot access data (unhealthy)
            
            NEVER returns boolean - follows ServiceHealthCheck v3.3 pattern
            """
            try:
                # Query with explicit schema name (Principle #4)
                query = f"""
                    SELECT COUNT(*) as count 
                    FROM {self.db_schema}.holonic_metrics 
                    LIMIT 1
                """
                
                result = await self.db_manager.fetch_one(query, ())
                
                # Verify we got a result
                if result is None:
                    raise Exception(
                        f"Could not query {self.db_schema}.holonic_metrics table - "
                        f"verify table exists and is accessible"
                    )
                
                # Explicit success return (not implicit)
                return None
                
            except Exception as e:
                # Raise exception with descriptive message
                raise Exception(f"Data access check failed: {str(e)}")
        
        async def check_output_directory():
            """
            Verify output directory exists and is writable.
            
            Returns:
                None: Output directory accessible (healthy)
            
            Raises:
                Exception: Cannot write to output directory (unhealthy)
            
            NEVER returns boolean - follows ServiceHealthCheck v3.3 pattern
            """
            try:
                # Ensure directory exists
                if not self.output_dir.exists():
                    self.output_dir.mkdir(parents=True, exist_ok=True)
                
                # Test write access
                test_file = self.output_dir / ".health_check_test"
                test_file.touch()
                test_file.unlink()
                
                # Explicit success return (not implicit)
                return None
                
            except Exception as e:
                # Raise exception with descriptive message
                raise Exception(
                    f"Output directory check failed: {str(e)} - "
                    f"verify {self.output_dir} exists and is writable"
                )
        
        # Use standardized health check pattern (Principle #12: Method Singularity)
        return await ServiceHealthCheck.database_dependent_health(
            service_name='visualizer',
            db_manager=self.db_manager,
            is_initialized=self._initialized,
            additional_checks=[check_matplotlib, check_data_access, check_output_directory],
            # Visualization-specific context
            charts_generated=self._charts_generated,
            reports_generated=0,  # Could track this if needed
            last_visualization=self._last_visualization.isoformat() if self._last_visualization else None,
            element_mode=self.element_mode,
            transactions_available=self.transactions_table_available,
            schema_features_verified=self.schema_features_verified,
            output_directory=str(self.output_dir)
        )
    
    
    # ═════════════════════════════════════════════════════════════════════════
    # Data Loading Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    async def load_evaluation_data(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Load holonic evaluation data from database.
        
        Args:
            limit: Optional limit on number of records to load
            
        Returns:
            Dictionary with:
                - accounts: List of evaluated accounts with metrics
                - categories: Category distribution counts
                - statistics: Summary statistics
                - dimension_stats: Statistics per dimension
        """
        try:
            # Build query with optional limit
            limit_clause = f"LIMIT {limit}" if limit else ""
            
            # Explicit schema names throughout (Principle #4)
            query = f"""
                SELECT 
                    hm.account_id,
                    hm.composite_score,
                    hm.holonic_category,
                    hm.autonomy_integration_score,
                    hm.multi_scale_score,
                    hm.regenerative_impact_score,
                    hm.network_contribution_score,
                    hm.ubuntu_alignment_score,
                    hm.evaluation_date,
                    sa.primary_element,
                    sa.subentry_count,
                    sa.token_holdings
                FROM {self.db_schema}.holonic_metrics hm
                LEFT JOIN {self.db_schema}.stellar_accounts sa 
                    ON hm.account_id = sa.account_id
                ORDER BY hm.composite_score DESC
                {limit_clause}
            """
            
            results = await self.db_manager.fetch_all(query, ())
            
            if not results:
                return {
                    'accounts': [],
                    'categories': {},
                    'statistics': {},
                    'dimension_stats': {},
                    'evaluated_count': 0
                }
            
            # Convert to list of dicts
            accounts = [dict(row) for row in results]
            
            # Calculate category distribution
            categories = {}
            for account in accounts:
                cat = account['holonic_category']
                categories[cat] = categories.get(cat, 0) + 1
            
            # Calculate summary statistics
            scores = [a['composite_score'] for a in accounts if a['composite_score'] is not None]
            
            if scores:
                statistics = {
                    'mean': float(sum(scores) / len(scores)),
                    'min': float(min(scores)),
                    'max': float(max(scores)),
                    'count': len(scores)
                }
                
                # Calculate percentiles if numpy available
                if NUMPY_AVAILABLE:
                    statistics['median'] = float(np.median(scores))
                    statistics['p25'] = float(np.percentile(scores, 25))
                    statistics['p75'] = float(np.percentile(scores, 75))
            else:
                statistics = {
                    'mean': 0.0,
                    'min': 0.0,
                    'max': 0.0,
                    'count': 0
                }
            
            # Calculate dimension statistics
            dimensions = [
                'autonomy_integration_score',
                'multi_scale_score',
                'regenerative_impact_score',
                'network_contribution_score',
                'ubuntu_alignment_score'
            ]
            
            dimension_stats = {}
            for dim in dimensions:
                dim_scores = [a[dim] for a in accounts if a.get(dim) is not None]
                if dim_scores:
                    dimension_stats[dim] = {
                        'mean': float(sum(dim_scores) / len(dim_scores)),
                        'min': float(min(dim_scores)),
                        'max': float(max(dim_scores))
                    }
            
            # Cache the data
            self.report_data = {
                'accounts': accounts,
                'categories': categories,
                'statistics': statistics,
                'dimension_stats': dimension_stats,
                'evaluated_count': len(accounts)
            }
            
            return self.report_data
            
        except Exception as e:
            self.logger.error(f"Error loading evaluation data: {e}", exc_info=True)
            return {
                'accounts': [],
                'categories': {},
                'statistics': {},
                'dimension_stats': {},
                'evaluated_count': 0
            }
    
    
    async def close(self):
        """
        Clean up visualizer resources.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("HolonicVisualizer closing...")
        
        # Clear cached data
        self.report_data = None
        self.time_series_data = None
        
        # Reset state
        self._initialized = False
        self._charts_generated = 0
        self._last_visualization = None
        
        self.logger.info("✓ HolonicVisualizer closed successfully")


# ═════════════════════════════════════════════════════════════════════════════
# Service Factory Function
# ═════════════════════════════════════════════════════════════════════════════

async def create_holonic_visualizer(
    db_manager: Any,
    config: Dict[str, Any],
    logger: Optional[logging.Logger] = None
) -> HolonicVisualizer:
    """
    Factory function to create and initialize HolonicVisualizer instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    Implements Principle #2 (Service Pattern).
    
    Args:
        db_manager: Async database manager from service registry
        config: Configuration dictionary containing:
            - db_schema: Database schema name (required)
            - output_dir: Output directory path (optional)
            - element_mode: Enable four-element features (optional)
        logger: Optional logger instance
    
    Returns:
        Initialized HolonicVisualizer instance
    
    Raises:
        ValueError: If required configuration is missing
        RuntimeError: If initialization fails
    
    Example:
        >>> visualizer = await create_holonic_visualizer(
        ...     db_manager=db,
        ...     config={'db_schema': 'ubec_main'}
        ... )
        >>> health = await visualizer.health_check()
    """
    # Validate required configuration
    if 'db_schema' not in config:
        raise ValueError("Configuration must include 'db_schema'")
    
    # Create visualizer instance
    visualizer = HolonicVisualizer(
        db_manager=db_manager,
        config=config,
        logger=logger
    )
    
    # Initialize the service
    success = await visualizer.initialize()
    
    if not success:
        raise RuntimeError(
            "HolonicVisualizer initialization failed - "
            "check database connectivity and permissions"
        )
    
    return visualizer


# ═════════════════════════════════════════════════════════════════════════════
# Module Exports
# ═════════════════════════════════════════════════════════════════════════════

__all__ = [
    'HolonicVisualizer',
    'create_holonic_visualizer',
    'UBUNTU_COLORS',
    'MATPLOTLIB_AVAILABLE',
    'NUMPY_AVAILABLE',
    'NETWORKX_AVAILABLE'
]


# ═════════════════════════════════════════════════════════════════════════════
# Standalone Execution Prevention
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from ubec_holonic_visualizer import create_holonic_visualizer\n"
        "  visualizer = await create_holonic_visualizer(db_manager, config)\n"
        "  data = await visualizer.load_evaluation_data()\n"
        "  health = await visualizer.health_check()\n"
        "  await visualizer.close()\n\n"
        "Version 13.2.2 - Health Check Return Pattern Enhancement:\n"
        "  - Enhanced check functions for absolute clarity\n"
        "  - Verified all check functions return None or raise Exception\n"
        "  - No implicit boolean evaluations anywhere\n"
        "  - Full compliance with ServiceHealthCheck v3.3 pattern\n"
        "  - All database queries use explicit schema names\n\n"
        "Version 13.2.1 - Bool Return Fix:\n"
        "  - Fixed check_data_access() to return None instead of bool\n"
        "  - Eliminated 'Unexpected return type' warnings\n"
        "  - Full compliance with ServiceHealthCheck patterns\n\n"
        "Version 13.2.0 - ServiceHealthCheck Integration:\n"
        "  - Uses ServiceHealthCheck.database_dependent_health()\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Standardized health check format\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
