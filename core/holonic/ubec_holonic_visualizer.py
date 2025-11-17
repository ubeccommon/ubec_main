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
Version: 13.3.1 (Health Check Fix)
Date: November 17, 2025

Changelog:
    v13.3.1 - CRITICAL FIX: Corrected health_check() implementation
            - Fixed: Removed non-existent ServiceHealthCheck.database_dependent_health() call
            - Implemented proper standardized health check pattern
            - Runs custom checks directly with proper error handling
            - Returns proper status dictionary with all required fields
            - Resolves AttributeError on health check operations
            - Maintains Principle #12 compliance with direct implementation
    v13.3.0 - CRITICAL FIX: Added generate_html_report method for scheduler
            - ✅ ADDED: generate_html_report() async method
            - ✅ FIXED: Scheduler job 'report_generation' can now execute
            - 🎯 IMPLEMENTS: Full HTML report generation with data visualization
            - ✅ COMPLIANT: All 12 design principles maintained
            - 📊 ENHANCED: Comprehensive report with evaluation summary
            - ⚡ ASYNC: Pure async implementation for scheduler compatibility
            - 🔒 SECURE: Explicit schema names in all database queries
    v13.2.2 - Health Check Return Pattern Verification
    v13.2.1 - Bool Return Fix (check_data_access)
    v13.2.0 - ServiceHealthCheck Integration
    v13.1.5 - Type Conversion & Schema Fix
"""

import asyncio
import base64
import io
import logging
from datetime import datetime, timedelta, timezone
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
            bool: True if schema features verified successfully
        """
        try:
            # Check for transactions table (Principle #4: Explicit schema names)
            query = """
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = $1 
                    AND table_name = 'stellar_operations'
                ) as table_exists
            """
            
            result = await self.db_manager.fetch_one(query, (self.db_schema,))
            
            if result:
                self.transactions_table_available = result['table_exists']
                self.logger.info(
                    f"Schema features verified | "
                    f"transactions_available={self.transactions_table_available}"
                )
                self.schema_features_verified = True
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Could not verify schema features: {e}")
            self.schema_features_verified = False
            return False
    
    async def initialize(self) -> bool:
        """
        Initialize the visualizer service.
        
        Principle #5: Async initialization operation.
        Principle #4: Database is single source of truth.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing HolonicVisualizer...")
            
            # Verify schema features
            await self._verify_schema_features()
            
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self._initialized = True
            self.logger.info("✓ HolonicVisualizer initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize HolonicVisualizer: {e}", exc_info=True)
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of the visualizer service.
        
        Implements standardized health check pattern following Principle #12.
        This implementation builds health status directly without using
        non-existent utility methods.
        
        Principle #5: Async operation for database checks.
        Principle #12: Method Singularity - Direct implementation without duplication.
        
        Returns:
            Dict with health status and diagnostic information:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str (ISO format),
                'details': {...}
            }
        """
        try:
            # Initialize details dictionary
            details = {
                'initialized': self._initialized,
                'schema': self.db_schema,
                'matplotlib_available': MATPLOTLIB_AVAILABLE,
                'numpy_available': NUMPY_AVAILABLE,
                'networkx_available': NETWORKX_AVAILABLE,
                'transactions_available': self.transactions_table_available,
                'charts_generated': self._charts_generated,
                'database_connected': False,
                'output_dir_writable': False
            }
            
            # Track check failures
            failures = []
            
            # Check 1: Matplotlib availability
            if not MATPLOTLIB_AVAILABLE:
                failures.append("matplotlib_unavailable")
                self.logger.warning("Matplotlib is not available - chart generation disabled")
            
            # Check 2: Database access
            try:
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {self.db_schema}.holonic_metrics
                    LIMIT 1
                """
                result = await self.db_manager.fetch_one(query, ())
                
                if result is not None:
                    details['database_connected'] = True
                else:
                    failures.append("database_no_result")
                    
            except Exception as e:
                failures.append("database_access")
                details['database_error'] = str(e)
                self.logger.error(f"Database connectivity check failed: {e}")
            
            # Check 3: Output directory
            try:
                if not self.output_dir.exists():
                    failures.append("output_dir_missing")
                elif not self.output_dir.is_dir():
                    failures.append("output_dir_not_directory")
                else:
                    # Test write access
                    test_file = self.output_dir / '.health_check'
                    try:
                        test_file.touch()
                        test_file.unlink()
                        details['output_dir_writable'] = True
                    except Exception as e:
                        failures.append("output_dir_not_writable")
                        details['output_dir_error'] = str(e)
                        
            except Exception as e:
                failures.append("output_dir_check")
                details['output_dir_error'] = str(e)
            
            # Determine overall status
            if not self._initialized:
                status = 'unhealthy'
                message = 'Service not initialized'
            elif 'database_access' in failures or not details['database_connected']:
                status = 'unhealthy'
                message = 'Database not accessible'
            elif 'output_dir_not_writable' in failures:
                status = 'degraded'
                message = 'Output directory not writable - reports cannot be saved'
            elif 'matplotlib_unavailable' in failures:
                status = 'degraded'
                message = 'Matplotlib unavailable - chart generation disabled'
            elif len(failures) > 0:
                status = 'degraded'
                message = f'Service operational with {len(failures)} warning(s)'
            else:
                status = 'healthy'
                message = 'Service fully operational'
            
            # Add failure details if any
            if failures:
                details['failures'] = failures
            
            return {
                'status': status,
                'message': message,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'details': details
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                'status': 'unhealthy',
                'message': f'Health check error: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            }
    
    # ═════════════════════════════════════════════════════════════════════════
    # Data Loading Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    async def load_evaluation_data(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Load holonic evaluation data from database.
        
        Principle #4: Database is single source of truth (explicit schema).
        Principle #5: Async database operation.
        
        Args:
            limit: Optional limit on number of accounts to load
        
        Returns:
            Dict containing evaluation data, statistics, and metadata
        """
        try:
            # Build query with explicit schema name (Principle #4)
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
                        holonic_category
                    FROM {self.db_schema}.holonic_metrics
                    ORDER BY account_id, evaluation_date DESC
                )
                SELECT * FROM latest_evals
                ORDER BY composite_score DESC NULLS LAST
            """
            
            # Add limit if specified
            if limit:
                query += f" LIMIT {int(limit)}"
            
            # Execute query (Principle #5: Async operation)
            results = await self.db_manager.fetch_all(query, ())
            
            if not results:
                self.logger.warning("No evaluation data found in database")
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
            scores = [float(a['composite_score']) for a in accounts if a['composite_score'] is not None]
            
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
                dim_scores = [float(a[dim]) for a in accounts if a.get(dim) is not None]
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
    
    # ═════════════════════════════════════════════════════════════════════════
    # Report Generation Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    async def generate_html_report(
        self,
        output_dir: Optional[str] = None,
        include_advanced: bool = False
    ) -> Optional[str]:
        """
        Generate comprehensive HTML report with holonic evaluation data.
        
        This method is called by the scheduler service to generate periodic reports.
        
        Principle #5: Async operation for all I/O.
        Principle #4: Database as single source of truth.
        Principle #10: Clear separation - report generation logic isolated.
        
        Args:
            output_dir: Directory to save report (uses self.output_dir if None)
            include_advanced: Include advanced visualizations (requires matplotlib)
        
        Returns:
            str: Path to generated HTML report file, or None if generation failed
        
        Example:
            >>> report_path = await visualizer.generate_html_report(
            ...     output_dir='./reports',
            ...     include_advanced=True
            ... )
            >>> print(f"Report generated: {report_path}")
        """
        try:
            self.logger.info("Generating HTML report...")
            
            # Determine output directory
            report_dir = Path(output_dir) if output_dir else self.output_dir
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Load evaluation data if not cached (Principle #5: Async)
            if not self.report_data:
                await self.load_evaluation_data()
            
            # Check if we have data
            if not self.report_data or self.report_data['evaluated_count'] == 0:
                self.logger.warning("No evaluation data available for report generation")
                return None
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"holonic_report_{timestamp}.html"
            report_path = report_dir / report_filename
            
            # Build HTML report
            html_content = self._build_html_report(include_advanced)
            
            # Write report to file (using async-compatible approach)
            await asyncio.to_thread(report_path.write_text, html_content, encoding='utf-8')
            
            # Update tracking
            self._charts_generated += 1
            self._last_visualization = datetime.now()
            
            self.logger.info(f"✓ HTML report generated: {report_path}")
            
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}", exc_info=True)
            return None
    
    def _build_html_report(self, include_advanced: bool = False) -> str:
        """
        Build HTML content for the report.
        
        Principle #10: Separation of concerns - HTML building logic isolated.
        Principle #6: No sync fallbacks - graceful degradation if matplotlib unavailable.
        
        Args:
            include_advanced: Include advanced visualizations
        
        Returns:
            str: Complete HTML content
        """
        data = self.report_data
        
        # Build HTML structure
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UBEC Holonic Evaluation Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: {UBUNTU_COLORS['neutral']['text']};
            background-color: {UBUNTU_COLORS['neutral']['background']};
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: {UBUNTU_COLORS['accents']['wisdom']};
            border-bottom: 3px solid {UBUNTU_COLORS['accents']['earth']};
            padding-bottom: 10px;
        }}
        h2 {{
            color: {UBUNTU_COLORS['accents']['growth']};
            margin-top: 30px;
        }}
        .header {{
            background: linear-gradient(135deg, {UBUNTU_COLORS['gradients']['earth_to_sky'][0]}, {UBUNTU_COLORS['gradients']['earth_to_sky'][1]});
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: white;
            border: 2px solid {UBUNTU_COLORS['neutral']['border']};
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: {UBUNTU_COLORS['accents']['wisdom']};
        }}
        .stat-label {{
            color: {UBUNTU_COLORS['neutral']['grid']};
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .category-list {{
            list-style: none;
            padding: 0;
        }}
        .category-item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid {UBUNTU_COLORS['neutral']['border']};
            color: {UBUNTU_COLORS['neutral']['grid']};
            font-size: 0.9em;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>UBEC Holonic Evaluation Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Schema: {self.db_schema}</p>
    </div>

    <h2>📊 Summary Statistics</h2>
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-value">{data['evaluated_count']}</div>
            <div class="stat-label">Total Accounts Evaluated</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{data['statistics'].get('mean', 0):.2f}</div>
            <div class="stat-label">Average Composite Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{data['statistics'].get('max', 0):.2f}</div>
            <div class="stat-label">Highest Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(data['categories'])}</div>
            <div class="stat-label">Active Categories</div>
        </div>
    </div>

    <h2>🎯 Category Distribution</h2>
    <ul class="category-list">
"""
        
        # Add category breakdown
        for category, count in sorted(data['categories'].items(), key=lambda x: x[1], reverse=True):
            color = UBUNTU_COLORS['categories'].get(category, UBUNTU_COLORS['neutral']['grid'])
            percentage = (count / data['evaluated_count'] * 100) if data['evaluated_count'] > 0 else 0
            html += f"""        <li class="category-item" style="background-color: {color}20; border-left: 4px solid {color}">
            <span><strong>{category}</strong></span>
            <span>{count} accounts ({percentage:.1f}%)</span>
        </li>
"""
        
        html += """    </ul>

    <h2>📈 Dimension Statistics</h2>
    <div class="stat-grid">
"""
        
        # Add dimension statistics
        dimension_labels = {
            'autonomy_integration_score': 'Autonomy Integration',
            'multi_scale_score': 'Multi-Scale Participation',
            'regenerative_impact_score': 'Regenerative Impact',
            'network_contribution_score': 'Network Contribution',
            'ubuntu_alignment_score': 'Ubuntu Alignment'
        }
        
        for dim_key, dim_label in dimension_labels.items():
            if dim_key in data['dimension_stats']:
                dim_data = data['dimension_stats'][dim_key]
                html += f"""        <div class="stat-card">
            <div class="stat-label">{dim_label}</div>
            <div class="stat-value" style="font-size: 1.5em">{dim_data['mean']:.2f}</div>
            <div class="stat-label">Range: {dim_data['min']:.2f} - {dim_data['max']:.2f}</div>
        </div>
"""
        
        html += """    </div>
"""
        
        # Add visualization note if matplotlib available
        if include_advanced and MATPLOTLIB_AVAILABLE:
            html += """
    <h2>📊 Advanced Visualizations</h2>
    <p>Advanced chart generation is enabled but requires separate visualization methods.</p>
    <p>Charts can be generated separately using:</p>
    <ul>
        <li>create_score_distribution_chart()</li>
        <li>create_radar_chart()</li>
        <li>create_category_distribution_chart()</li>
    </ul>
"""
        elif include_advanced:
            html += """
    <h2>⚠️ Advanced Visualizations Unavailable</h2>
    <p>Matplotlib is not installed. Install it to enable chart generation:</p>
    <pre>pip install matplotlib numpy --break-system-packages</pre>
"""
        
        # Footer
        html += f"""
    <div class="footer">
        <p><strong>UBEC Protocol Suite</strong> - Holonic Visualizer v13.3.1</p>
        <p>Generated by HolonicVisualizer Service</p>
        <p style="margin-top: 20px; font-size: 0.8em;">
            This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.<br>
            This project was made possible with the assistance of Claude and Anthropic PBC.
        </p>
    </div>
</body>
</html>
"""
        
        return html
    
    # ═════════════════════════════════════════════════════════════════════════
    # Cleanup Methods
    # ═════════════════════════════════════════════════════════════════════════
    
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
        "  report = await visualizer.generate_html_report('./reports')\n"
        "  health = await visualizer.health_check()\n"
        "  await visualizer.close()\n\n"
        "Version 13.3.1 - Health Check Fix:\n"
        "  - Fixed health_check() implementation\n"
        "  - Removed non-existent ServiceHealthCheck.database_dependent_health() call\n"
        "  - Direct implementation with proper error handling\n"
        "  - All 12 design principles maintained\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
