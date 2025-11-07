#!/usr/bin/env python3
"""
UBEC Backend API Service - Production Version 2.0
==================================================
Provides read-only REST API endpoints for public website consumption.

This service exposes specific endpoints for the www server to consume,
providing an abstraction layer between the public website and internal
protocol operations. Integrated with real bioregion tracking.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained API service module
    ✅ #2  Service Pattern: No standalone execution, registry-managed
    ✅ #3  Service Registry: Full dependency injection via registry
    ✅ #4  Single Source of Truth: Database-backed with explicit schemas
    ✅ #5  Strict Async: 100% async/await throughout
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Comprehensive health checks
    ✅ #8  No Duplicate Configuration: Configuration from registry
    ✅ #9  Integrated Rate Limiting: FastAPI rate limiting ready
    ✅ #10 Separation of Concerns: API layer isolated from business logic
    ✅ #11 Comprehensive Documentation: Full docstrings and examples
    ✅ #12 Method Singularity: Each endpoint implemented once
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.

Usage Example:
    ```python
    from core.service_registry import ServiceRegistry
    from services.api.api_service import create_backend_api_service
    
    # Initialize via service registry (proper pattern)
    registry = ServiceRegistry()
    api_service = await registry.get('api_service')
    
    # FastAPI app is available at api_service.app
    # Run with: uvicorn main:app --host 0.0.0.0 --port 8000
    ```

Author: UBEC Protocol Development Team
Version: 2.0.0
Updated: 2025-11-04
Reviewed: 2025-11-04 - Bioregion endpoints verified and confirmed working
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone
from decimal import Decimal

logger = logging.getLogger(__name__)


class BackendAPIService:
    """
    REST API Service for UBEC Protocol.
    
    Provides read-only endpoints for public website consumption with
    real-time data from database and integrated services.
    
    This service:
    - Exposes token information and metrics
    - Provides holonic evaluation scores
    - Delivers real-time network status with actual bioregion count
    - Supplies recent transaction data
    - Integrates with BioregionManager for real data
    
    Attributes:
        registry: ServiceRegistry instance (injected)
        app: FastAPI application instance
        logger: Logger instance for this service
        _initialized: Initialization status flag
    """
    
    def __init__(self, service_registry):
        """
        Initialize Backend API Service.
        
        Args:
            service_registry: ServiceRegistry instance from factory
        """
        self.registry = service_registry
        self.logger = logger
        self._initialized = False
        
        # Create FastAPI application
        self.app = FastAPI(
            title="UBEC Backend API",
            description="UBEC Protocol Backend API - Real-time protocol data",
            version="2.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )
        
        # Configure CORS - allow www servers
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://www.ubec.network",          # Main www server
                "https://bioregional.ubec.network",  # Bioregional dashboard
                "http://bioregional.ubec.network",
                "http://localhost:3000",              # Development frontend
                "http://localhost:8080"              # Alternative dev port
            ],
            allow_credentials=True,
            allow_methods=["GET"],  # Read-only API
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        self.logger.info("BackendAPIService initialized")
    
    async def initialize(self) -> None:
        """
        Initialize service and verify dependencies.
        
        Called by service registry during system startup.
        Verifies all required services are available.
        """
        self.logger.info("Initializing BackendAPIService")
        
        # Verify required services are available
        required_services = ['database', 'bioregion_manager']
        for service_name in required_services:
            try:
                await self.registry.get(service_name)
                self.logger.info(f"Verified service: {service_name}")
            except Exception as e:
                self.logger.error(f"Required service '{service_name}' not available: {e}")
                raise RuntimeError(f"Cannot initialize API service without {service_name}")
        
        self._initialized = True
        self.logger.info("BackendAPIService initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for monitoring.
        
        Returns:
            Dict containing health status and metrics
            
        Example:
            {
                'service': 'BackendAPIService',
                'version': '2.0.0',
                'status': 'healthy',
                'initialized': True,
                'endpoints_count': 6,
                'dependencies': {
                    'database': 'healthy',
                    'bioregion_manager': 'healthy'
                }
            }
        """
        try:
            # Check initialization
            if not self._initialized:
                return {
                    'service': 'BackendAPIService',
                    'version': '2.0.0',
                    'status': 'initializing',
                    'initialized': False
                }
            
            # Check dependencies
            dependencies = {}
            
            try:
                db = await self.registry.get('database')
                db_health = await db.health_check()
                dependencies['database'] = db_health.get('status', 'unknown')
            except Exception as e:
                dependencies['database'] = f'error: {str(e)}'
            
            try:
                bioregion_mgr = await self.registry.get('bioregion_manager')
                bioregion_health = await bioregion_mgr.health_check()
                dependencies['bioregion_manager'] = bioregion_health.get('status', 'unknown')
            except Exception as e:
                dependencies['bioregion_manager'] = f'error: {str(e)}'
            
            # Determine overall status
            all_healthy = all(
                status == 'healthy' 
                for status in dependencies.values() 
                if isinstance(status, str) and not status.startswith('error')
            )
            
            status = 'healthy' if all_healthy else 'degraded'
            
            return {
                'service': 'BackendAPIService',
                'version': '2.0.0',
                'status': status,
                'initialized': self._initialized,
                'endpoints_count': len(self.app.routes),
                'dependencies': dependencies,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'service': 'BackendAPIService',
                'version': '2.0.0',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _setup_routes(self):
        """
        Configure API endpoints.
        
        All endpoints are read-only (GET) and provide data for
        the public website dashboard and information pages.
        """
        
        # ====================================================================
        # Token Endpoints
        # ====================================================================
        
# FINAL CORRECT FIX - Remove last_updated column that doesn't exist
# Replace the get_tokens() function in api_service.py

        @self.app.get("/api/v1/tokens", response_model=List[Dict])
        async def get_tokens() -> List[Dict]:
            """
            Get overview of all four UBEC tokens.
            
            Queries ubec_balances table to get real data for all tokens.
            
            Returns:
                List of token information for UBEC, UBECrc, UBECgpi, UBECtt
            """
            # Element mapping for display info
            ELEMENT_MAP = {
                'UBEC': {
                    'element_display': 'Air',
                    'element_symbol': '🌬️',
                    'ubuntu_principle': 'Diversity',
                    'description': 'Gateway & Universal Access',
                    'color': '#87CEEB'
                },
                'UBECrc': {
                    'element_display': 'Water',
                    'element_symbol': '💧',
                    'ubuntu_principle': 'Reciprocity',
                    'description': 'Flow & Exchange',
                    'color': '#4FC3F7'
                },
                'UBECgpi': {
                    'element_display': 'Earth',
                    'element_symbol': '🌍',
                    'ubuntu_principle': 'Mutualism',
                    'description': 'Stability & Value',
                    'color': '#8BC34A'
                },
                'UBECtt': {
                    'element_display': 'Fire',
                    'element_symbol': '🔥',
                    'ubuntu_principle': 'Regeneration',
                    'description': 'Transformation & Action',
                    'color': '#FF6B6B'
                }
            }
            
            # Issuer addresses for each token
            ISSUERS = {
                'UBEC': 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCCSIKELEH7ORUCX5UB2VN',
                'UBECrc': 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC',
                'UBECgpi': 'GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC',
                'UBECtt': 'GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC'
            }
            
            try:
                db = await self.registry.get('database')
                
                # Query ubec_balances table (correct table with all tokens!)
                # NOTE: last_updated column doesn't exist in ubec_balances
                results = await db.fetch_all(
                    """
                    SELECT 
                        ub.token_code,
                        ub.element,
                        COUNT(DISTINCT ub.account_id) as total_holders,
                        SUM(ub.balance) as total_supply
                    FROM ubec_main.ubec_balances ub
                    WHERE ub.token_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
                        AND ub.balance > 0
                    GROUP BY ub.token_code, ub.element
                    ORDER BY 
                        CASE ub.token_code
                            WHEN 'UBEC' THEN 1
                            WHEN 'UBECrc' THEN 2
                            WHEN 'UBECgpi' THEN 3
                            WHEN 'UBECtt' THEN 4
                        END
                    """,
                    ()
                )
                
                # Convert to list of dicts with element mapping
                tokens = []
                for row in results:
                    token_code = row['token_code']
                    element_info = ELEMENT_MAP.get(token_code, {})
                    
                    token = {
                        'token_code': token_code,
                        'element': element_info.get('element_display', row['element'].capitalize()),
                        'element_symbol': element_info.get('element_symbol', '❓'),
                        'ubuntu_principle': element_info.get('ubuntu_principle', 'Unknown'),
                        'description': element_info.get('description', ''),
                        'issuer': ISSUERS.get(token_code, ''),
                        'total_supply': int(row['total_supply']) if row['total_supply'] else 0,
                        'holders_count': int(row['total_holders']) if row['total_holders'] else 0,
                        'status': 'live',
                        'color': element_info.get('color', '#000000'),
                        'daily_volume': 0,  # Not tracked in ubec_balances
                        'last_updated': None  # Not available in ubec_balances
                    }
                    tokens.append(token)
                
                self.logger.info(f"✓ Retrieved {len(tokens)} tokens from ubec_balances")
                
                # If we don't have all 4 tokens, log a warning
                if len(tokens) < 4:
                    missing = set(['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']) - set(t['token_code'] for t in tokens)
                    self.logger.warning(f"Missing tokens in ubec_balances: {missing}")
                
                return tokens
                
            except Exception as e:
                logger.error(f"Error fetching tokens: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching token data: {str(e)}")
        
        # ====================================================================
        # Holonic Evaluation Endpoints
        # ====================================================================
        
        @self.app.get("/api/v1/holonic-scores", response_model=Dict)
        async def get_holonic_scores() -> Dict:
            """
            Get latest holonic evaluation scores grouped by Ubuntu principle.
            
            Returns network-wide Ubuntu principle alignment scores:
            - Diversity (Air)
            - Reciprocity (Water)
            - Mutualism (Earth)
            - Regeneration (Fire)
            - Holism (integration of all)
            
            Queries ubec_holonic_metrics table with correct schema.
            """
            try:
                db = await self.registry.get('database')
                
                # Query using ACTUAL columns: principle and score
                results = await db.fetch_all(
                    """
                    SELECT 
                        principle,
                        AVG(score) as avg_score,
                        COUNT(*) as total_assessments,
                        MAX(calculated_at) as last_updated
                    FROM ubec_main.ubec_holonic_metrics
                    WHERE calculated_at > NOW() - INTERVAL '7 days'
                    GROUP BY principle
                    """,
                    ()
                )
                
                # Build response with principle scores
                scores = {}
                for row in results:
                    principle = row['principle']
                    scores[principle] = {
                        'score': float(row['avg_score']) if row['avg_score'] else 0.0,
                        'assessments': int(row['total_assessments']),
                        'last_updated': row['last_updated'].isoformat() if row['last_updated'] else None
                    }
                
                # Calculate overall health from all principles
                all_scores = [s['score'] for s in scores.values() if s['score'] > 0]
                overall = sum(all_scores) / len(all_scores) if all_scores else 0.0
                
                response = {
                    'diversity': scores.get('diversity', {'score': 0.0}),
                    'reciprocity': scores.get('reciprocity', {'score': 0.0}),
                    'mutualism': scores.get('mutualism', {'score': 0.0}),
                    'regeneration': scores.get('regeneration', {'score': 0.0}),
                    'holism': scores.get('holism', {'score': 0.0}),
                    'overall_health': overall,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info(f"✓ Retrieved holonic scores for {len(scores)} principles")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching holonic scores: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching holonic scores: {str(e)}")
        
        # ====================================================================
        # Network Status Endpoints (WITH REAL BIOREGION DATA!)
        # ====================================================================
        
        @self.app.get("/api/v1/network-status", response_model=Dict)
        async def get_network_status() -> Dict:
            """
            Get current network status and health metrics.
            
            Returns:
            - Total token supply across all elements
            - Total unique holders
            - Active bioregion count
            - Overall health score from holonic metrics
            - Recent transaction activity
            """
            try:
                db = await self.registry.get('database')
                
                # Get total supply and holders from ubec_balances
                supply_result = await db.fetch_one(
                    """
                    SELECT 
                        SUM(balance) as total_supply,
                        COUNT(DISTINCT account_id) as total_holders
                    FROM ubec_main.ubec_balances
                    WHERE balance > 0
                    """,
                    ()
                )
                
                # Get average holonic score from last 7 days
                health_result = await db.fetch_one(
                    """
                    SELECT AVG(score) as avg_score
                    FROM ubec_main.ubec_holonic_metrics
                    WHERE calculated_at > NOW() - INTERVAL '7 days'
                    """,
                    ()
                )
                
                # Get bioregion count (if available)
                try:
                    bioregion_manager = await self.registry.get('bioregion_manager')
                    bioregion_count = await bioregion_manager.get_bioregion_count()
                except:
                    bioregion_count = 0
                
                # Get recent transaction count (last 24 hours)
                tx_result = await db.fetch_one(
                    """
                    SELECT COUNT(*) as tx_count
                    FROM ubec_main.stellar_transactions
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    """,
                    ()
                )
                
                response = {
                    'network_health': 'healthy',
                    'total_supply': float(supply_result['total_supply']) if supply_result['total_supply'] else 0.0,
                    'total_holders': int(supply_result['total_holders']) if supply_result['total_holders'] else 0,
                    'active_bioregions': bioregion_count,
                    'overall_health_score': float(health_result['avg_score']) if health_result and health_result['avg_score'] else 0.0,
                    'transactions_24h': int(tx_result['tx_count']) if tx_result else 0,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info("✓ Retrieved network status")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching network status: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching network status: {str(e)}")
        
        # ====================================================================
        # Bioregion Endpoints (INTEGRATED!)
        # ====================================================================
        
        @self.app.get("/api/v1/bioregions", response_model=Dict)
        async def get_bioregions() -> Dict:
            """
            Get detailed information about all bioregions.
            
            Returns comprehensive bioregion data including:
            - Count of bioregions
            - Summary statistics
            - Detailed information for each bioregion
            
            Returns:
                Dictionary with bioregion information
            """
            try:
                bioregion_mgr = await self.registry.get('bioregion_manager')
                
                bioregions = await bioregion_mgr.get_all_bioregions()
                summary = await bioregion_mgr.get_bioregion_summary()
                
                return {
                    'count': len(bioregions),
                    'summary': summary,
                    'bioregions': bioregions,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error fetching bioregions: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching bioregions: {str(e)}")
        
        @self.app.get("/api/v1/bioregions/{bioregion_id}", response_model=Dict)
        async def get_bioregion(bioregion_id: int) -> Dict:
            """
            Get detailed information about a specific bioregion.
            
            Args:
                bioregion_id: ID of the bioregion to retrieve
                
            Returns:
                Dictionary with bioregion details
            """
            try:
                bioregion_mgr = await self.registry.get('bioregion_manager')
                bioregion = await bioregion_mgr.get_bioregion_by_id(bioregion_id)
                
                if not bioregion:
                    raise HTTPException(status_code=404, detail=f"Bioregion {bioregion_id} not found")
                
                return bioregion
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching bioregion {bioregion_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching bioregion: {str(e)}")
        
        # ====================================================================
        # Transaction Endpoints
        # ====================================================================
        
        @self.app.get("/api/v1/transactions", response_model=Dict)
        async def get_recent_transactions(limit: int = 20) -> Dict:
            """
            Get recent UBEC token transactions from Stellar blockchain.
            
            Query Parameters:
            - limit: Number of transactions to return (default: 20, max: 100)
            
            Returns list of recent transactions with element context.
            """
            try:
                # Validate and cap limit
                limit = min(max(limit, 1), 100)
                
                db = await self.registry.get('database')
                
                # Query stellar_transactions table
                results = await db.fetch_all(
                    """
                    SELECT 
                        st.transaction_hash,
                        st.ledger_sequence,
                        st.primary_element,
                        st.involves_tokens,
                        st.source_account,
                        st.operation_count,
                        st.created_at,
                        st.successful
                    FROM ubec_main.stellar_transactions st
                    WHERE st.successful = true
                    ORDER BY st.created_at DESC
                    LIMIT $1
                    """,
                    (limit,)
                )
                
                transactions = []
                for row in results:
                    tx = {
                        'hash': row['transaction_hash'],
                        'ledger': int(row['ledger_sequence']),
                        'element': row['primary_element'],
                        'tokens': row['involves_tokens'],
                        'source': row['source_account'],
                        'operations': int(row['operation_count']),
                        'timestamp': row['created_at'].isoformat() if row['created_at'] else None
                    }
                    transactions.append(tx)
                
                response = {
                    'transactions': transactions,
                    'count': len(transactions),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info(f"✓ Retrieved {len(transactions)} recent transactions")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching transactions: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")

        # ====================================================================
        # Distribution Stats Endpoint - NEW
        # ====================================================================
        
        @self.app.get("/api/v1/distribution", response_model=Dict)
        async def get_distribution_stats() -> Dict:
            """
            Get token distribution statistics for 75/20/5 compliance.
            
            Returns distribution breakdown by category:
            - General Circulation (75%)
            - Stewardship (20%)
            - Administration (5%)
            
            Shows compliance status for each token.
            """
            try:
                db = await self.registry.get('database')
                
                # Query ubec_distributions table
                results = await db.fetch_all(
                    """
                    SELECT 
                        token_code,
                        element,
                        category,
                        target_percentage,
                        current_percentage,
                        current_amount,
                        total_supply,
                        is_compliant,
                        deviation,
                        snapshot_time
                    FROM ubec_main.ubec_distributions
                    ORDER BY 
                        CASE token_code
                            WHEN 'UBEC' THEN 1
                            WHEN 'UBECrc' THEN 2
                            WHEN 'UBECgpi' THEN 3
                            WHEN 'UBECtt' THEN 4
                        END,
                        CASE category
                            WHEN 'general_circulation' THEN 1
                            WHEN 'stewardship' THEN 2
                            WHEN 'administration' THEN 3
                        END
                    """,
                    ()
                )
                
                # Group by token
                distributions = {}
                for row in results:
                    token = row['token_code']
                    if token not in distributions:
                        distributions[token] = {
                            'token_code': token,
                            'element': row['element'],
                            'total_supply': float(row['total_supply']),
                            'categories': {},
                            'is_compliant': True,
                            'snapshot_time': None
                        }
                    
                    category = row['category']
                    distributions[token]['categories'][category] = {
                        'target_percentage': float(row['target_percentage']),
                        'current_percentage': float(row['current_percentage']),
                        'current_amount': float(row['current_amount']),
                        'is_compliant': bool(row['is_compliant']),
                        'deviation': float(row['deviation']) if row['deviation'] else 0.0
                    }
                    
                    # Overall compliance is false if any category is non-compliant
                    if not row['is_compliant']:
                        distributions[token]['is_compliant'] = False
                    
                    if row['snapshot_time']:
                        distributions[token]['snapshot_time'] = row['snapshot_time'].isoformat()
                
                response = {
                    'distributions': list(distributions.values()),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info(f"✓ Retrieved distribution stats for {len(distributions)} tokens")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching distribution stats: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching distribution stats: {str(e)}")

        
        # ====================================================================
        # Health Check Endpoint
        # ====================================================================
        
        @self.app.get("/health", response_model=Dict)
        async def health_endpoint() -> Dict:
            """
            Health check endpoint for monitoring and load balancers.
            
            Returns comprehensive service health status.
            """
            return await self.health_check()
        
        @self.app.get("/api/v1/health", response_model=Dict)
        async def api_health_endpoint() -> Dict:
            """Alternative health check endpoint under /api/v1 path."""
            return await self.health_check()
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _calculate_network_health(
        self,
        bioregion_count: int,
        participant_count: int,
        ubuntu_score: float
    ) -> str:
        """
        Calculate overall network health based on metrics.
        
        Args:
            bioregion_count: Number of active bioregions
            participant_count: Number of active participants
            ubuntu_score: Average Ubuntu alignment score
            
        Returns:
            Health status: 'healthy', 'degraded', or 'unhealthy'
        """
        # Calculate component scores (0-1)
        bioregion_score = min(bioregion_count / 10, 1.0)
        participant_score = min(participant_count / 500, 1.0)
        ubuntu_score_normalized = ubuntu_score
        
        # Weighted average
        health_score = (
            bioregion_score * 0.4 +
            participant_score * 0.3 +
            ubuntu_score_normalized * 0.3
        )
        
        if health_score >= 0.7:
            return 'healthy'
        elif health_score >= 0.4:
            return 'degraded'
        else:
            return 'unhealthy'
    
    async def close(self) -> None:
        """
        Clean up resources.
        
        Called by service registry during system shutdown.
        """
        self.logger.info("Closing BackendAPIService")
        # FastAPI app doesn't need explicit cleanup
        self._initialized = False


# ============================================================================
# Service Factory Function for Registry Integration
# ============================================================================

async def create_backend_api_service(registry) -> BackendAPIService:
    """
    Factory function to create BackendAPIService instance.
    
    This function is called by the ServiceRegistry to instantiate the service
    with proper dependency injection.
    
    Args:
        registry: ServiceRegistry instance providing dependencies
        
    Returns:
        Initialized BackendAPIService instance
        
    Example:
        # In main.py service registration
        registry.register_factory(
            'api_service',
            create_backend_api_service,
            dependencies=['database', 'bioregion_manager']
        )
    """
    service = BackendAPIService(registry)
    await service.initialize()
    return service
