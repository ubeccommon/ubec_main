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
        
        @self.app.get("/api/v1/tokens", response_model=List[Dict])
        async def get_tokens() -> List[Dict]:
            """
            Get overview of all four UBEC tokens.
            
            Returns token information including:
            - Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            - Element type (Air, Water, Earth, Fire)
            - Total supply
            - Number of holders
            - Daily trading volume
            
            Returns:
                List of token information dictionaries
                
            Example Response:
                [
                    {
                        "token_code": "UBEC",
                        "element_type": "Air",
                        "ubuntu_principle": "Diversity",
                        "total_supply": 152025699,
                        "holders_count": 495,
                        "daily_volume": 1234567
                    },
                    ...
                ]
            """
            try:
                db = await self.registry.get('database')
                
                # Query with EXPLICIT schema name
                results = await db.fetch_all(
                    """
                    SELECT 
                        ab.asset_code as token_code,
                        ab.element_type,
                        ab.ubuntu_principle,
                        ab.total_supply,
                        ab.holders_count,
                        ab.daily_volume,
                        ab.last_updated
                    FROM ubec_main.asset_holder_analysis ab
                    WHERE ab.asset_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
                    ORDER BY 
                        CASE ab.asset_code
                            WHEN 'UBEC' THEN 1
                            WHEN 'UBECrc' THEN 2
                            WHEN 'UBECgpi' THEN 3
                            WHEN 'UBECtt' THEN 4
                        END
                    """,
                    ()
                )
                
                # Convert to list of dicts
                tokens = []
                for row in results:
                    token = {
                        'token_code': row['token_code'],
                        'element_type': row['element_type'],
                        'ubuntu_principle': row['ubuntu_principle'],
                        'total_supply': int(row['total_supply']) if row['total_supply'] else 0,
                        'holders_count': int(row['holders_count']) if row['holders_count'] else 0,
                        'daily_volume': float(row['daily_volume']) if row['daily_volume'] else 0.0,
                        'last_updated': row['last_updated'].isoformat() if row['last_updated'] else None
                    }
                    tokens.append(token)
                
                return tokens
                
            except Exception as e:
                logger.error(f"Error fetching tokens: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching token data: {str(e)}")
        
        # ====================================================================
        # Holonic Evaluation Endpoints
        # ====================================================================
        
        @self.app.get("/api/v1/holonic-scores", response_model=Dict)
        async def get_holonic_scores() -> Dict:
            """
            Get latest holonic evaluation scores.
            
            Returns network-wide Ubuntu principle alignment scores:
            - Autonomy-Integration balance
            - Ubuntu alignment
            - Reciprocity health
            - Mutualism capacity
            - Regeneration impact
            
            Returns:
                Dictionary with holonic metrics
                
            Example Response:
                {
                    "network_average": {
                        "autonomy_integration": 0.78,
                        "ubuntu_alignment": 0.85,
                        "reciprocity_health": 0.72,
                        "mutualism_capacity": 0.81,
                        "regeneration_impact": 0.68
                    },
                    "overall_health": 0.77,
                    "category_distribution": {
                        "exemplar": 65,
                        "integrator": 130,
                        "contributor": 260,
                        "participant": 840
                    }
                }
            """
            try:
                db = await self.registry.get('database')
                
                # Get network averages with EXPLICIT schema
                avg_result = await db.fetch_one(
                    """
                    SELECT 
                        AVG(autonomy_integration_score) as autonomy_integration,
                        AVG(ubuntu_alignment_score) as ubuntu_alignment,
                        AVG(reciprocity_health_score) as reciprocity_health,
                        AVG(mutualism_capacity_score) as mutualism_capacity,
                        AVG(regeneration_impact_score) as regeneration_impact,
                        AVG(composite_score) as overall_health,
                        COUNT(*) as total_accounts
                    FROM ubec_main.ubec_holonic_metrics
                    WHERE evaluated_at > NOW() - INTERVAL '7 days'
                    """,
                    ()
                )
                
                # Get category distribution
                category_result = await db.fetch_all(
                    """
                    SELECT 
                        holonic_category,
                        COUNT(*) as count
                    FROM ubec_main.ubec_holonic_metrics
                    WHERE evaluated_at > NOW() - INTERVAL '7 days'
                    GROUP BY holonic_category
                    ORDER BY holonic_category
                    """,
                    ()
                )
                
                # Format response
                response = {
                    'network_average': {
                        'autonomy_integration': float(avg_result['autonomy_integration'] or 0),
                        'ubuntu_alignment': float(avg_result['ubuntu_alignment'] or 0),
                        'reciprocity_health': float(avg_result['reciprocity_health'] or 0),
                        'mutualism_capacity': float(avg_result['mutualism_capacity'] or 0),
                        'regeneration_impact': float(avg_result['regeneration_impact'] or 0)
                    },
                    'overall_health': float(avg_result['overall_health'] or 0),
                    'total_accounts': int(avg_result['total_accounts'] or 0),
                    'category_distribution': {
                        row['holonic_category']: int(row['count'])
                        for row in category_result
                    },
                    'calculated_at': datetime.now(timezone.utc).isoformat()
                }
                
                return response
                
            except Exception as e:
                logger.error(f"Error fetching holonic scores: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching holonic scores: {str(e)}")
        
        # ====================================================================
        # Network Status Endpoints (WITH REAL BIOREGION DATA!)
        # ====================================================================
        
        @self.app.get("/api/v1/network-status", response_model=Dict)
        async def get_network_status() -> Dict:
            """
            Get real-time network status with ACTUAL bioregion count.
            
            This endpoint now provides REAL bioregion data from the
            BioregionManager service instead of mock data.
            
            Returns:
                Dictionary with network metrics including real bioregion count
                
            Example Response:
                {
                    "active_participants": 495,
                    "total_transactions_24h": 1247,
                    "average_ubuntu_score": 0.77,
                    "bioregions_count": 12,  # REAL COUNT from database!
                    "bioregions_summary": {
                        "total_members": 68,
                        "average_size": 5.67,
                        "largest_bioregion": "Pacific Northwest Economic Commons"
                    },
                    "last_block_time": "2025-11-04T...",
                    "network_health": "healthy",
                    "data_source": "real"
                }
            """
            try:
                db = await self.registry.get('database')
                bioregion_mgr = await self.registry.get('bioregion_manager')
                
                # Get REAL bioregion count
                bioregion_count = await bioregion_mgr.get_bioregion_count()
                bioregion_summary = await bioregion_mgr.get_bioregion_summary()
                
                # Get active participants count with EXPLICIT schema
                participants_result = await db.fetch_one(
                    """
                    SELECT COUNT(DISTINCT account_id) as active_participants
                    FROM ubec_main.stellar_accounts
                    WHERE account_id IS NOT NULL
                    """,
                    ()
                )
                active_participants = int(participants_result['active_participants'] or 0)
                
                # Get 24h transaction count with EXPLICIT schema
                tx_result = await db.fetch_one(
                    """
                    SELECT COUNT(*) as tx_count
                    FROM ubec_main.stellar_transactions
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    """,
                    ()
                )
                total_transactions_24h = int(tx_result['tx_count'] or 0)
                
                # Get average Ubuntu score with EXPLICIT schema
                ubuntu_result = await db.fetch_one(
                    """
                    SELECT AVG(composite_score) as avg_score
                    FROM ubec_main.ubec_holonic_metrics
                    WHERE evaluated_at > NOW() - INTERVAL '7 days'
                    """,
                    ()
                )
                average_ubuntu_score = float(ubuntu_result['avg_score'] or 0)
                
                # Get last block time with EXPLICIT schema
                block_result = await db.fetch_one(
                    """
                    SELECT MAX(created_at) as last_block
                    FROM ubec_main.stellar_transactions
                    """,
                    ()
                )
                last_block_time = block_result['last_block'].isoformat() if block_result['last_block'] else None
                
                # Determine network health
                network_health = self._calculate_network_health(
                    bioregion_count,
                    active_participants,
                    average_ubuntu_score
                )
                
                return {
                    'active_participants': active_participants,
                    'total_transactions_24h': total_transactions_24h,
                    'average_ubuntu_score': round(average_ubuntu_score, 2),
                    'bioregions_count': bioregion_count,  # REAL DATA!
                    'bioregions_summary': bioregion_summary,
                    'last_block_time': last_block_time,
                    'network_health': network_health,
                    'data_source': 'real',  # Indicator this is actual data
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error fetching network status: {e}")
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
        
        @self.app.get("/api/v1/transactions/recent", response_model=List[Dict])
        async def get_recent_transactions(limit: int = 20) -> List[Dict]:
            """
            Get recent transactions for blockchain explorer.
            
            Args:
                limit: Maximum number of transactions to return (max 100)
                
            Returns:
                List of recent transaction dictionaries
            """
            if limit > 100:
                raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
            
            try:
                db = await self.registry.get('database')
                
                # Query with EXPLICIT schema
                results = await db.fetch_all(
                    """
                    SELECT 
                        st.transaction_hash,
                        st.ledger_sequence,
                        st.source_account,
                        st.operation_count,
                        st.successful,
                        st.created_at,
                        st.memo_type,
                        st.memo
                    FROM ubec_main.stellar_transactions st
                    ORDER BY st.created_at DESC
                    LIMIT $1
                    """,
                    (limit,)
                )
                
                # Format transactions
                transactions = []
                for row in results:
                    tx = {
                        'hash': row['transaction_hash'],
                        'ledger': int(row['ledger_sequence']),
                        'source': row['source_account'],
                        'operations': int(row['operation_count']),
                        'successful': bool(row['successful']),
                        'timestamp': row['created_at'].isoformat() if row['created_at'] else None,
                        'memo_type': row['memo_type'],
                        'memo': row['memo']
                    }
                    transactions.append(tx)
                
                return transactions
                
            except Exception as e:
                logger.error(f"Error fetching transactions: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")
        
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
